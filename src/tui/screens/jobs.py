"""Sections 1 to 3: one three-pane screen (status list, jobs table, detail) under a preset."""
from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.worker import get_current_worker

from .. import data
from ..presets import PRESETS
from ..widgets.jobs_table import JobsTable
from ..widgets.status_list import StatusList
from .base import SectionScreen


class JobsScreen(SectionScreen):
    DEFAULT_CSS = """
    JobsScreen #panes { height: 1fr; }
    """

    def __init__(self, preset: str) -> None:
        super().__init__(preset)
        self.preset = preset
        self.status_filter: str | None = None
        self.query_text = ""

    def body(self) -> ComposeResult:
        with Horizontal(id="panes"):
            yield StatusList(PRESETS[self.preset].entries, id="status-list")
            yield JobsTable(id="jobs-table")

    def on_mount(self) -> None:
        self.query_one(JobsTable).focus()
        self.load_counts()

    @work(thread=True, group="counts", exclusive=True)
    def load_counts(self) -> None:
        counts = data.counts()
        self.app.call_from_thread(self.query_one(StatusList).set_counts, counts)

    @work(thread=True, group="rows", exclusive=True)
    def load_rows(self) -> None:
        """SQLite off the UI thread. A thread cannot be interrupted, so a load that was
        superseded (the cursor moved on in the status list) drops its result instead."""
        worker = get_current_worker()
        rows = data.rows(self.preset, self.status_filter, self.query_text)
        if not worker.is_cancelled:
            self.app.call_from_thread(self.query_one(JobsTable).load, rows)

    def on_status_list_picked(self, event: StatusList.Picked) -> None:
        self.status_filter = event.status
        self.load_rows()
