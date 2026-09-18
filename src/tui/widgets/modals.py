"""Modal screens. Every one closes on `esc` (spec: esc is home)."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen

from ..data import JobDetail
from .detail import DetailPane


class DetailOverlay(ModalScreen[None]):
    """The detail pane full-width, for a terminal too narrow to keep it beside the table."""

    DEFAULT_CSS = """
    DetailOverlay { align: center middle; }
    DetailOverlay DetailPane { width: 90%; height: 90%; border: round $primary; background: $surface; }
    """
    BINDINGS = [
        Binding("escape", "dismiss", "close"),
        Binding("enter", "dismiss", "close", show=False),
        Binding("q", "dismiss", "close", show=False),
    ]

    def __init__(self, detail: JobDetail) -> None:
        super().__init__()
        self.detail = detail

    def compose(self) -> ComposeResult:
        yield DetailPane(id="detail-overlay", classes="overlay")

    def on_mount(self) -> None:
        pane = self.query_one(DetailPane)
        pane.show(self.detail)
        pane.focus()
