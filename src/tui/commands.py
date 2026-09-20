"""What the TUI hands to the outside world: things to open, slash commands for the clipboard
(later: hunt argv)."""
from __future__ import annotations

import os
import signal
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from urllib.parse import urlsplit

from ..config import ROOT

OPENER = "open" if sys.platform == "darwin" else "xdg-open"


def launch(target: str) -> None:
    """Hand a URL or a path to the desktop. Detached and silent: the TUI owns the terminal."""
    subprocess.Popen([OPENER, target], stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def open_posting(url: str) -> str:
    """A posting URL comes from a scraped feed, so only http(s) reaches `open`: anything else
    (`file:`, an app scheme, a bare path) would be the feed choosing what runs here."""
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError(f"no posting URL to open ({url!r})" if url else "this row has no posting URL")
    launch(url.strip())
    return f"opened {parts.netloc}"


def open_path(path: Path) -> str:
    if not path.exists():
        raise ValueError(f"{path} is gone")
    launch(str(path))
    return f"opened {path.name}"


# Slash commands. The TUI runs no model (spec decision 5): it puts the command on the clipboard
# and the reader pastes it into the agent's prompt, where several lines run in order.

def tailor_command(job_id: int) -> str:
    return f"/jh-tailor {int(job_id)}"


def tailor_commands(job_ids: Sequence[int]) -> str:
    """One per line, in the order given."""
    return "\n".join(tailor_command(i) for i in job_ids)


# The hunt orchestrator as a subprocess (spec decision 5): the TUI runs no model itself.

def hunt_argv(*args: str) -> list[str]:
    return [sys.executable, "-m", "src.hunt", *args]


def module_argv(module: str, *args: str) -> list[str]:
    return [sys.executable, "-m", module, *args]


def shell_line(argv: Sequence[str]) -> str:
    """An argv the way a human would type it: `python` for this interpreter."""
    import shlex
    return shlex.join(["python" if a == sys.executable else a for a in argv])


def capture(argv: Sequence[str], timeout: int = 600) -> tuple[int, str]:
    """(exit code, stdout then stderr) of a command that prints a report and exits."""
    try:
        cp = subprocess.run(list(argv), cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=timeout, stdin=subprocess.DEVNULL, check=False)
    except subprocess.TimeoutExpired:
        return -1, f"no answer after {timeout}s"
    except OSError as e:
        return -1, str(e)
    return cp.returncode, "\n".join(part.rstrip() for part in (cp.stdout, cp.stderr) if part.strip())


# A GUI editor's command line tool lives inside its app bundle on macOS and reaches PATH only if
# the reader once ran the editor's "install shell command" action. Most never do, so `code -w`
# found nothing and the file never opened. Glob patterns, because a second install is
# "Visual Studio Code 2.app".
APP_DIRS = (Path("/Applications"), Path.home() / "Applications")
BUNDLED_CLI: dict[str, tuple[str, ...]] = {
    "code": ("Visual Studio Code*.app/Contents/Resources/app/bin/code",),
    "code-insiders": ("Visual Studio Code*Insiders*.app/Contents/Resources/app/bin/code",),
    "cursor": ("Cursor*.app/Contents/Resources/app/bin/cursor",),
    "zed": ("Zed*.app/Contents/MacOS/cli",),
    "subl": ("Sublime Text*.app/Contents/SharedSupport/bin/subl",),
}


def find_program(name: str) -> str | None:
    """Where `name` is: PATH first, then (macOS) the CLI inside the editor's app bundle. A path
    is taken as given. None when it is nowhere."""
    import shutil
    if os.sep in name:
        return name if os.access(name, os.X_OK) else None
    found = shutil.which(name)
    if found or sys.platform != "darwin":
        return found
    for pattern in BUNDLED_CLI.get(name, ()):
        for apps in APP_DIRS:
            for hit in sorted(apps.glob(pattern)):
                if os.access(hit, os.X_OK):
                    return str(hit)
    return None


def resolve_editor(argv: Sequence[str]) -> list[str]:
    """`argv` with its program located. Raises ValueError, with what to do about it, when the
    editor is not installed where anything can find it."""
    if not argv:
        raise ValueError("the editor command is empty")
    program = find_program(argv[0])
    if program is None:
        hint = (f": install its shell command (in the editor, \"Shell Command: Install '{argv[0]}' command in PATH\") "
                "or pick another editor in the settings") if argv[0] in BUNDLED_CLI else "; pick another editor in the settings (,)"
        raise ValueError(f"{argv[0]} is not on PATH and no app bundle carries it{hint}")
    return [program, *argv[1:]]


def is_window_editor(argv: Sequence[str]) -> bool:
    """An editor that opens its own window (VS Code, Cursor, Zed, Sublime) needs nothing from the
    terminal, so the TUI stays up beside it. Anything else is taken for a terminal editor, which
    must have the terminal: guessing wrong that way only costs a suspend.

    Two ways to be one, because `resolve_editor` may already have swapped the name for the file
    inside the bundle, and that file is not always called what the command is (Zed's is `cli`):
    the command's name as typed, or a program that is one of the bundle files looked up here."""
    if not argv:
        return False
    program = Path(argv[0])
    if program.name in BUNDLED_CLI:
        return True
    return any(program.match(pattern) for patterns in BUNDLED_CLI.values() for pattern in patterns)


def launch_editor(argv: Sequence[str]) -> subprocess.Popen[bytes]:
    """A window editor, detached and silent: the TUI keeps the terminal and keeps running. With
    `-w` the process lives until the file's tab closes; the caller may wait on it in a worker."""
    return subprocess.Popen(list(argv), cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, start_new_session=True)


def run_editor(argv: Sequence[str]) -> int:
    """The editor in the foreground, on the real terminal (the caller suspended the TUI).
    Returns its exit code, -1 when it could not start."""
    try:
        return subprocess.run(list(argv), cwd=ROOT, check=False).returncode
    except OSError:
        return -1


def flush_terminal_input() -> None:
    """Drop what is waiting on the terminal's input. An editor like nvim asks the terminal
    questions on its way in and out (cursor style, colours, keyboard protocol) and the answers
    that come back after it is gone sit in the queue the TUI reads next; the cursor-style
    answer ends in ` q`, and `q` quits. Called after the editor exits and BEFORE the TUI takes
    the terminal back. A no-op where there is no terminal (tests, a pipe, Windows)."""
    stdin = sys.__stdin__                                # the stream Textual's driver reads
    if stdin is None:
        return
    try:
        import termios
        termios.tcflush(stdin.fileno(), termios.TCIFLUSH)
    except (ImportError, OSError, ValueError):
        pass


def spawn(argv: Sequence[str]) -> subprocess.Popen[str]:
    """A stage as a child process, stdout and stderr on one pipe, line buffered so the log pane
    moves while it runs. Its own session: a hard stop can take the harness children with it."""
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    return subprocess.Popen(list(argv), cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                            bufsize=1, start_new_session=True)


def stop(proc: subprocess.Popen[str], hard: bool = False) -> None:
    """SIGTERM first: the orchestrator closes its ledger on it (running units end failed, so
    `--resume` picks them up). `hard` is the second ask: SIGKILL to the whole process group."""
    if proc.poll() is not None:
        return
    try:
        if hard:
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.terminate()
    except (ProcessLookupError, PermissionError):
        pass


def pbcopy(text: str) -> None:
    subprocess.run(["pbcopy"], input=text.encode(), check=True, timeout=5,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def copy(text: str, fallback: Callable[[str], None]) -> None:
    """`pbcopy` where there is one: it reaches the system clipboard whatever the terminal is.
    `fallback` is Textual's clipboard (an OSC 52 escape, which some terminals ignore)."""
    try:
        pbcopy(text)
    except (OSError, subprocess.SubprocessError):
        fallback(text)


def copied_line(job_ids: Sequence[int]) -> str:
    """The toast: what is on the clipboard now."""
    if len(job_ids) == 1:
        return f"copied {tailor_command(job_ids[0])}"
    return f"copied {len(job_ids)} commands: /jh-tailor {', '.join(str(i) for i in job_ids)}"
