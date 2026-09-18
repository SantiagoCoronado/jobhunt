"""Sections 1 to 3: one three-pane screen (status list, jobs table, detail) under a preset."""
from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from .. import data
from ..widgets.status_list import StatusList
from .base import SectionScreen


class JobsScreen(SectionScreen):
    DEFAULT_CSS = """
    JobsScreen #panes { height: 1fr; }
    JobsScreen #jobs-table { width: 1fr; padding: 0 1; }
    """

    def __init__(self, preset: str) -> None:
        super().__init__(preset)
        self.preset = preset
        self.status_filter: str | None = None

    def body(self) -> ComposeResult:
        with Horizontal(id="panes"):
            yield StatusList(id="status-list")
            yield Static("", id="jobs-table")

    def on_mount(self) -> None:
        self.load_counts()

    @work(thread=True, group="counts", exclusive=True)
    def load_counts(self) -> None:
        counts = data.counts()
        self.app.call_from_thread(self.query_one(StatusList).set_counts, counts)

    def on_status_list_picked(self, event: StatusList.Picked) -> None:
        self.status_filter = event.status
        self.query_one("#jobs-table", Static).update(f"{event.status}: the table lands in story 5")
