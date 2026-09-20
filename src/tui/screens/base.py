"""SectionScreen: the frame every section shares (section bar on top, footer below)."""
from __future__ import annotations

from collections.abc import Callable

from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from ..widgets.footer import SectionFooter
from ..widgets.section_bar import SectionBar


class SectionScreen(Screen):
    """A section with a placeholder body. Real sections subclass and override `body`."""

    def __init__(self, mode: str, placeholder: str = "") -> None:
        super().__init__()
        self.mode = mode
        self.placeholder = placeholder
        self.state_note = ""           # what the section itself is doing ("running tailor")

    def compose(self) -> ComposeResult:
        yield SectionBar(self.mode)
        yield from self.body()
        yield SectionFooter()

    def body(self) -> ComposeResult:
        yield Static(self.placeholder, id="placeholder")

    def on_mount(self) -> None:
        self.draw_note()

    def on_screen_resume(self) -> None:
        self.draw_note()

    def sync_selection(self) -> None:
        """The app's selection changed (any section may have changed it)."""
        self.draw_note()

    def draw_note(self) -> None:
        """The footer's state line: the section's own state, then the selection, which reads the
        same on every section so the reader never loses sight of what is marked."""
        parts = (self.state_note, self.app.selection.note())  # type: ignore[attr-defined]
        self.query_one(SectionFooter).note = " · ".join(p for p in parts if p)

    def toast(self, line: str, severity: str = "information") -> None:
        """A toast line carries a company name or a typed value: never parse it as markup."""
        self.app.notify(line, severity=severity, markup=False)  # type: ignore[arg-type]

    def reload(self) -> None:
        """Read the section's data again. Called after every write."""

    @work(thread=True, group="write")
    def write(self, op: Callable[[], str]) -> None:
        """Every write: run it off the UI thread, toast its one line, reload the view."""
        try:
            line = op()
        except ValueError as e:
            self.app.call_from_thread(self.toast, str(e), "error")
            return
        bad = "CONFLICT" in line or "ERROR" in line
        self.app.call_from_thread(self.toast, line, "warning" if bad else "information")
        self.app.call_from_thread(self.reload)
