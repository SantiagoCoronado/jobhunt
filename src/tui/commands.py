"""What the TUI hands to the outside world: things to open, slash commands for the clipboard
(later: hunt argv)."""
from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from urllib.parse import urlsplit

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
