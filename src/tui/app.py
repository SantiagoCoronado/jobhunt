"""App shell: seven sections as Textual modes, a section bar, the footer, global keys."""
from __future__ import annotations

from datetime import date

from textual.app import App
from textual.binding import Binding
from textual.screen import Screen

from .screens.base import SectionScreen

# (mode, label). Order is the key order: `1` is the first entry.
SECTIONS: tuple[tuple[str, str], ...] = (
    ("board", "board"),
    ("shortlist", "shortlist"),
    ("followups", "follow-ups"),
    ("apps", "apps"),
    ("stats", "stats"),
    ("run", "run"),
    ("settings", "settings"),
)


def _placeholder(mode: str, label: str):
    def make() -> Screen:
        return SectionScreen(mode, f"{label}: coming in a later story (docs/spec-tui.md)")
    return make


class JobhuntApp(App):
    TITLE = "jobhunt"
    MODES = {mode: _placeholder(mode, label) for mode, label in SECTIONS}
    DEFAULT_MODE = "board"
    BINDINGS = [
        *(Binding(str(i), f"section('{mode}')", label, show=False)
          for i, (mode, label) in enumerate(SECTIONS, start=1)),
        Binding("q", "quit", "quit"),
    ]

    def __init__(self, today: date | None = None) -> None:
        super().__init__()
        self.today = today or date.today()

    def action_section(self, mode: str) -> None:
        if mode != self.current_mode:
            self.switch_mode(mode)
