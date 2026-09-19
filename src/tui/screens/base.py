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

    def compose(self) -> ComposeResult:
        yield SectionBar(self.mode)
        yield from self.body()
        yield SectionFooter()

    def body(self) -> ComposeResult:
        yield Static(self.placeholder, id="placeholder")

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
