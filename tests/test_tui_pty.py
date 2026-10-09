"""The editor round trip on a real pseudo-terminal (PRA-116). `e` in the config view suspends
the TUI for the editor; an editor like nvim asks the terminal questions, and answers that come
back after it is gone used to be read as keys by the resumed TUI (the cursor-style answer ends
in ` q`, and `q` quits). The pilot tests cannot see this: headless, `suspend` is not supported.

Needs a pty, so it is skipped where there is none (`-m "not pty"` skips it by hand)."""
import os
import select
import signal
import sys
import time
from pathlib import Path

import pytest

from src.tui.app import DEAF_SECONDS

pty = pytest.importorskip("pty")
pytestmark = [pytest.mark.pty, pytest.mark.skipif(sys.platform == "win32", reason="no pty")]

CHILD = Path(__file__).with_name("tui_pty_child.py")
# A terminal editor as the TUI sees one: it takes the terminal, says it is up, reads nothing
# (so whatever the terminal sends meanwhile stays queued, as a late reply does) and leaves.
EDITOR = "import sys, time; print('EDITOR-UP', sys.argv[1], flush=True); time.sleep(0.2)"
LATE_REPLY = b"\x1bP1$r2 q\x1b\\" + b"q"        # DECRQSS cursor-style answer, then a bare q for good measure
# The config view is up when its footer shows the `e` key: a key label ends in a style reset.
# Not the header's "e edits": that line starts with the fixture's absolute path, and a long
# checkout pushes the words past column 140.
CONFIG_UP = b"edit \x1b"


class Term:
    def __init__(self, argv: list[str], tmp: Path) -> None:
        import fcntl
        import struct
        import termios
        self.pid, self.fd = pty.fork()
        if self.pid == 0:                                        # the child: becomes the TUI
            os.environ.update(TERM="xterm-256color", COLUMNS="140", LINES="40")
            os.execv(argv[0], argv)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack("HHHH", 40, 140, 0, 0))
        self.seen = b""
        self.status: int | None = None
        self.stacks_file = tmp / "stacks.txt"                   # tui_pty_child.py writes it on SIGUSR1

    def read(self, seconds: float) -> None:
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            ready, _, _ = select.select([self.fd], [], [], 0.05)
            if ready:
                try:
                    chunk = os.read(self.fd, 65536)
                except OSError:                                  # the child is gone
                    return
                if not chunk:
                    return
                self.seen += chunk

    def find(self, text: bytes, seconds: float, since: int = 0) -> int:
        """Where `text` shows up within `seconds`, or -1."""
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            at = self.seen.find(text, since)
            if at >= 0:
                return at
            self.read(0.1)
        return -1

    def wait_for(self, text: bytes, seconds: float = 20.0, since: int = 0) -> int:
        at = self.find(text, seconds, since)
        if at < 0:
            raise AssertionError(f"never saw {text!r}; the tail was {self.seen[-600:]!r}\n{self.stacks()}")
        return at

    def stacks(self) -> str:
        """Every thread's stack in the child, for a failure message: a TUI that stopped drawing
        says where it is stuck."""
        if not self.alive():
            return "the child is gone"
        os.kill(self.pid, signal.SIGUSR1)
        end = time.monotonic() + 2.0
        while time.monotonic() < end:
            if self.stacks_file.exists() and self.stacks_file.stat().st_size:
                time.sleep(0.1)                                  # let the dump finish
                return "the child's threads:\n" + self.stacks_file.read_text()
            self.read(0.05)
        return "the child wrote no stacks"

    def send(self, data: bytes) -> None:
        os.write(self.fd, data)

    def alive(self) -> bool:
        if self.status is None:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
            if pid:
                self.status = status
        return self.status is None

    def close(self) -> None:
        if self.alive():
            os.kill(self.pid, 9)
            os.waitpid(self.pid, 0)
        os.close(self.fd)


@pytest.fixture
def term(tmp_path):
    editor = f'{sys.executable} -c "{EDITOR}"'
    try:
        t = Term([sys.executable, str(CHILD), str(tmp_path), editor], tmp_path)
    except OSError as e:
        pytest.skip(f"no pty here: {e}")
    yield t
    t.close()


def open_config(term: Term) -> None:
    """`6` until the config view is up. A key sent while the app is still settling can be lost on
    a slow runner, and `6` on the config view does nothing, so pressing it again is safe."""
    for _ in range(5):
        term.send(b"6")
        if term.find(CONFIG_UP, 4.0) >= 0:
            return
    term.wait_for(CONFIG_UP, 0.1)                                # fails with the tail and the child's stacks


def test_a_terminal_editor_round_trip_survives_a_late_terminal_reply(term):
    term.wait_for(b"follow-ups")                                 # the section bar: the TUI is up
    open_config(term)
    term.send(b"e")
    up = term.wait_for(b"EDITOR-UP")
    term.send(LATE_REPLY)                                        # lands while the editor holds the terminal, unread
    back = term.wait_for(CONFIG_UP, since=up)                    # the editor left, the TUI drew itself again
    term.read(DEAF_SECONDS + 0.1)                                # the whole deaf window, then the human q
    assert term.alive(), "the late reply was read as `q` and quit the TUI"
    assert b"CHILD-EXITED-CLEAN" not in term.seen[back:]

    term.send(b"q")                                              # a moment later a human q still quits
    term.wait_for(b"CHILD-EXITED-CLEAN", since=back)
    end = time.monotonic() + 5.0                                 # drain the pty until the child is reaped
    while term.alive() and time.monotonic() < end:
        term.read(0.05)
    assert term.status is not None and os.waitstatus_to_exitcode(term.status) == 0
