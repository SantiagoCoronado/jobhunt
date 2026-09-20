"""The sections, in key order: `1` is the first entry. Its own module so the bar, the help
overlay and any text that names a section by number read one table (and nothing imports app)."""
from __future__ import annotations

# (mode, label)
SECTIONS: tuple[tuple[str, str], ...] = (
    ("board", "board"),
    ("followups", "follow-ups"),
    ("apps", "apps"),
    ("stats", "stats"),
    ("run", "run"),
    ("settings", "settings"),
)
MODES: tuple[str, ...] = tuple(mode for mode, _label in SECTIONS)


def number(mode: str) -> int:
    """The key that opens `mode`, so on-screen wording follows the table when it changes."""
    return MODES.index(mode) + 1
