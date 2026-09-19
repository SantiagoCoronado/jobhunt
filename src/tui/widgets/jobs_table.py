"""Middle pane: one line per job, in the order the preset's sort returned them."""
from __future__ import annotations

from datetime import date

from rich.text import Text
from textual.binding import Binding
from textual.widgets import DataTable

from ..data import JobRow
from ..presets import LIVE, OVERDUE_STYLE

NONE = "·"
# (key, label, width). The star column stays empty until PR 4 computes stars from src.pick.
COLUMNS: tuple[tuple[str, str, int], ...] = (
    ("star", " ", 1),
    ("score", "score", 5),
    ("company", "company", 20),
    ("title", "title", 38),
    ("loc", "loc", 18),
    ("fup", "fup", 10),
)
DREAM_TAG = " (dream)"


def clip(s: str, width: int) -> str:
    s = " ".join(s.split())
    return s if len(s) <= width else s[: width - 1] + "…"


class JobsTable(DataTable):
    DEFAULT_CSS = """
    JobsTable { width: 1fr; height: 1fr; }
    """
    BINDINGS = [
        Binding("j", "cursor_down", "down", show=False),
        Binding("k", "cursor_up", "up", show=False),
        Binding("g", "top", "top", show=False),
        Binding("G", "bottom", "bottom", show=False),
        Binding("enter", "select_cursor", "detail: focus the pane, or the overlay when narrow", show=False),
    ]

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id, cursor_type="row", zebra_stripes=False, cell_padding=1)
        self.job_ids: list[int] = []
        self.rows_by_id: dict[int, JobRow] = {}

    def on_mount(self) -> None:
        for key, label, width in COLUMNS:
            self.add_column(label, key=key, width=width)

    def cells(self, r: JobRow, today: date | None = None) -> tuple[Text, ...]:
        """Every cell is a `Text`. DataTable runs `Text.from_markup` on a `str` cell, and these
        strings come from scraped postings: `[on-site]` would vanish, `[/bold]` would raise
        MarkupError and kill the table, `[link=file:///...]` would plant a link that never
        passed the http(s) check in `commands.open_posting`."""
        widths = {key: w for key, _label, w in COLUMNS}
        loc = (clip(r.location, widths["loc"] - len(DREAM_TAG)) + DREAM_TAG if r.dream
               else clip(r.location, widths["loc"]))
        return (
            Text(""),
            Text(NONE if r.score is None else str(r.score), justify="right"),
            Text(clip(r.company, widths["company"])),
            Text(clip(r.title, widths["title"])),
            Text(loc or NONE),
            self.followup_cell(r, today),
        )

    @staticmethod
    def followup_cell(r: JobRow, today: date | None) -> Text:
        """Red once the date has passed, and only while the application is live: a stale date
        on a rejected row is history, not something to chase."""
        if not r.followup:
            return Text(NONE)
        overdue = today is not None and r.status in LIVE and r.followup < today.isoformat()
        return Text(r.followup, style=OVERDUE_STYLE if overdue else "")

    def load(self, rows: list[JobRow], today: date | None = None, keep: bool = False) -> None:
        """Replace the rows. With `keep` (a reload of the same view) the cursor stays on the same
        job when it is still listed, else on the same line, where the row below slid up; a
        status change must not throw the reader back to the top. A new filter starts at the top."""
        was_id, was_line = self.current_id, self.cursor_row
        self.clear()
        self.job_ids = [r.id for r in rows]
        self.rows_by_id = {r.id: r for r in rows}
        for r in rows:
            self.add_row(*self.cells(r, today), key=str(r.id))
        if keep and rows and was_id is not None:
            line = self.job_ids.index(was_id) if was_id in self.rows_by_id else min(was_line, len(rows) - 1)
            self.move_cursor(row=line)

    @property
    def current_id(self) -> int | None:
        if not self.job_ids or not 0 <= self.cursor_row < len(self.job_ids):
            return None
        return self.job_ids[self.cursor_row]

    @property
    def current_row(self) -> JobRow | None:
        return self.rows_by_id.get(self.current_id) if self.current_id is not None else None

    def action_top(self) -> None:
        if self.row_count:
            self.move_cursor(row=0)

    def action_bottom(self) -> None:
        if self.row_count:
            self.move_cursor(row=self.row_count - 1)
