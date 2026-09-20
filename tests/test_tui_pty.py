"""The editor round trip on a real pseudo-terminal (PRA-116). `e` in the config view suspends
the TUI for the editor; an editor like nvim asks the terminal questions, and answers that come
back after it is gone used to be read as keys by the resumed TUI (the cursor-style answer ends
in ` q`, and `q` quits). The pilot tests cannot see this: headless, `suspend` is not supported.

Needs a pty, so it is skipped where there is none (`-m "not pty"` skips it by hand)."""
import os
import select
import sys
import time
from pathlib import Path

import pytest

pty = pytest.importorskip("pty")
pytestmark = [pytest.mark.pty, pytest.mark.skipif(sys.platform == "win32", reason="no pty")]

CHILD = Path(__file__).with_name("tui_pty_child.py")
# A terminal editor as the TUI sees one: it takes the terminal, says it is up, reads nothing
# (so whatever the terminal sends meanwhile stays queued, as a late reply does) and leaves.
EDITOR = "import sys, time; print('EDITOR-UP', sys.argv[1], flush=True); time.sleep(1.0)"
LATE_REPLY = b"\x1bP1$r2 q\x1b\\" + b"q"        # DECRQSS cursor-style answer, then a bare q for good measure


class Term:
    def __init__(self, argv: list[str]) -> None:
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

    def wait_for(self, text: bytes, seconds: float = 20.0, since: int = 0) -> int:
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            at = self.seen.find(text, since)
            if at >= 0:
                return at
            self.read(0.1)
        raise AssertionError(f"never saw {text!r}; the tail was {self.seen[-600:]!r}")

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
        t = Term([sys.executable, str(CHILD), str(tmp_path), editor])
    except OSError as e:
        pytest.skip(f"no pty here: {e}")
    yield t
    t.close()


def test_a_terminal_editor_round_trip_survives_a_late_terminal_reply(term):
    term.wait_for(b"follow-ups")                                 # the section bar: the TUI is up
    term.send(b"6")
    term.wait_for(b"e edits")                                    # the config view
    term.send(b"e")
    up = term.wait_for(b"EDITOR-UP")
    term.send(LATE_REPLY)                                        # lands while the editor holds the terminal, unread
    back = term.wait_for(b"e edits", since=up)                   # the editor left, the TUI drew itself again
    term.read(1.0)
    assert term.alive(), "the late reply was read as `q` and quit the TUI"
    assert b"CHILD-EXITED-CLEAN" not in term.seen[back:]

    term.send(b"q")                                              # a moment later a human q still quits
    term.wait_for(b"CHILD-EXITED-CLEAN", since=back)
    term.read(0.5)
    for _ in range(50):
        if not term.alive():
            break
        time.sleep(0.1)
    assert term.status is not None and os.waitstatus_to_exitcode(term.status) == 0
