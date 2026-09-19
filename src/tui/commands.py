"""What the TUI hands to the outside world: things to open (later: slash commands, hunt argv)."""
from __future__ import annotations

import subprocess
import sys
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
