"""Sections 1 to 3: one three-pane screen (status list, jobs table, detail) under a preset."""
from __future__ import annotations

from textual import events, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.worker import get_current_worker

from .. import data
from ..presets import PRESETS
from ..widgets.detail import DetailPane
from ..widgets.jobs_table import JobsTable
from ..widgets.modals import Confirm, DetailOverlay, StatusPicker
from ..widgets.status_list import StatusList
from .base import SectionScreen


WIDE = 120   # under this many columns the detail pane collapses and `enter` opens it as an overlay


class JobsScreen(SectionScreen):
    DEFAULT_CSS = """
    JobsScreen #panes { height: 1fr; }
    """

    BINDINGS = [
        Binding("s", "status", "status"),
        Binding("b", "backlog", "backlog"),
    ]

    def __init__(self, preset: str) -> None:
        super().__init__(preset)
        self.preset = preset
        self.status_filter: str | None = None
        self.query_text = ""

    def body(self) -> ComposeResult:
        with Horizontal(id="panes"):
            yield StatusList(PRESETS[self.preset].entries, id="status-list")
            yield JobsTable(id="jobs-table")
            yield DetailPane(id="detail")

    def on_mount(self) -> None:
        self.query_one(JobsTable).focus()
        self.load_counts()

    @property
    def wide(self) -> bool:
        return self.size.width >= WIDE

    def on_resize(self, event: events.Resize) -> None:
        self.query_one("#detail", DetailPane).display = event.size.width >= WIDE

    @work(thread=True, group="counts", exclusive=True)
    def load_counts(self) -> None:
        counts = data.counts()
        preset = PRESETS[self.preset]
        counts[self.preset] = sum(counts.get(s, 0) for s in preset.statuses)   # the head entry
        self.app.call_from_thread(self.query_one(StatusList).set_counts, counts)

    @work(thread=True, group="rows", exclusive=True)
    def load_rows(self, keep: bool = False) -> None:
        """SQLite off the UI thread. A thread cannot be interrupted, so a load that was
        superseded (the cursor moved on in the status list) drops its result instead."""
        worker = get_current_worker()
        rows = data.rows(self.preset, self.status_filter, self.query_text)
        if not worker.is_cancelled:
            today = self.app.today  # type: ignore[attr-defined]
            self.app.call_from_thread(self.query_one(JobsTable).load, rows, today, keep)

    def on_status_list_picked(self, event: StatusList.Picked) -> None:
        # The head entry carries the preset's name and means "no pick": the preset's statuses.
        self.status_filter = None if event.status == self.preset else event.status
        self.load_rows()

    def on_data_table_row_highlighted(self, event: JobsTable.RowHighlighted) -> None:
        self.load_detail(self.query_one(JobsTable).current_id, overlay=False)

    def on_data_table_row_selected(self, event: JobsTable.RowSelected) -> None:
        """`enter`: focus the pane when it is on screen, open it as an overlay when it is not."""
        if self.wide:
            self.query_one("#detail", DetailPane).focus()
        else:
            self.load_detail(self.query_one(JobsTable).current_id, overlay=True)

    @work(thread=True, group="detail", exclusive=True)
    def load_detail(self, job_id: int | None, overlay: bool) -> None:
        worker = get_current_worker()
        detail = data.detail(job_id) if job_id is not None else None
        if worker.is_cancelled:
            return
        if overlay:
            if detail is not None:
                self.app.call_from_thread(self.app.push_screen, DetailOverlay(detail))
        else:
            self.app.call_from_thread(self.query_one("#detail", DetailPane).show, detail)

    # Status changes. One row: the table cursor. (Bulk verbs over a selection arrive in PR 4.)

    def current_row(self) -> data.JobRow | None:
        return self.query_one(JobsTable).current_row

    def action_status(self) -> None:
        row = self.current_row()
        if row is None:
            return

        def picked(status: str | None) -> None:
            if status:
                self.request_status(row, status)

        self.app.push_screen(StatusPicker(f"#{row.id} {row.company}", row.status), picked)

    def action_backlog(self) -> None:
        row = self.current_row()
        if row is not None:
            self.request_status(row, "backlog")

    def request_status(self, row: data.JobRow, status: str) -> None:
        if status == row.status:
            return
        if not data.needs_confirm(row.status, status):
            self.write_status(row.id, status)
            return

        def answered(yes: bool | None) -> None:
            if yes:
                self.write_status(row.id, status)

        self.app.push_screen(Confirm(f"#{row.id} {row.company}: leave {row.status} for {status}?"), answered)

    @work(thread=True, group="write")
    def write_status(self, job_id: int, status: str) -> None:
        try:
            line = data.set_status(job_id, status)
        except ValueError as e:
            self.app.call_from_thread(self.app.notify, str(e), severity="error")
            return
        bad = "CONFLICT" in line or "ERROR" in line
        self.app.call_from_thread(self.app.notify, line, severity="warning" if bad else "information")
        self.app.call_from_thread(self.reload)

    def reload(self) -> None:
        self.load_counts()
        self.load_rows(keep=True)
