"""App shell: seven sections as Textual modes, a section bar, the footer, global keys."""
from __future__ import annotations

from datetime import date

from textual.app import App
from textual.binding import Binding
from textual.screen import Screen

from .presets import PRESETS
from .screens.base import SectionScreen
from .screens.jobs import JobsScreen
from .widgets.detail import DetailPane
from .widgets.jobs_table import JobsTable
from .widgets.modals import HelpGroup, HelpOverlay, NotesEditor, StatusPicker
from .widgets.status_list import StatusList

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


def _screen(mode: str, label: str):
    def make() -> Screen:
        if mode in PRESETS:
            return JobsScreen(mode)
        return SectionScreen(mode, f"{label}: coming in a later story (docs/spec-tui.md)")
    return make


class JobhuntApp(App):
    TITLE = "jobhunt"
    MODES = {mode: _screen(mode, label) for mode, label in SECTIONS}
    DEFAULT_MODE = "board"
    BINDINGS = [
        *(Binding(str(i), f"section('{mode}')", label, show=False)
          for i, (mode, label) in enumerate(SECTIONS, start=1)),
        Binding("question_mark", "help", "help"),
        Binding("escape", "home", "home: back to the table, search cleared, modal closed", show=False),
        Binding("q", "quit", "quit"),
    ]

    def __init__(self, today: date | None = None) -> None:
        super().__init__()
        self.today = today or date.today()

    def action_section(self, mode: str) -> None:
        if mode != self.current_mode:
            self.switch_mode(mode)

    def action_home(self) -> None:
        """`esc` on a section with nothing to go home to. JobsScreen and every modal bind their
        own `escape`, which wins over this one."""

    @staticmethod
    def help_groups() -> list[HelpGroup]:
        owners = (
            ("everywhere", JobhuntApp), ("sections 1 to 3", JobsScreen), ("jobs table", JobsTable),
            ("status list", StatusList), ("detail pane", DetailPane),
            ("status picker", StatusPicker), ("notes editor", NotesEditor),
        )
        # Textual also accepts bare tuples in BINDINGS; this app only writes Binding objects.
        return [(title, [b for b in cls.BINDINGS if isinstance(b, Binding)]) for title, cls in owners]

    def action_help(self) -> None:
        if not isinstance(self.screen, HelpOverlay):
            self.push_screen(HelpOverlay(self.help_groups()))
