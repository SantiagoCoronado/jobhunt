"""What the TUI hands to the outside world: things to open, slash commands for the clipboard
(later: hunt argv)."""
from __future__ import annotations

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
