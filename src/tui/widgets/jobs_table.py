"""Middle pane: one line per job, in the order the preset's sort returned them."""
from __future__ import annotations

from rich.text import Text
from textual.binding import Binding
from textual.widgets import DataTable

from ..data import JobRow

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
    ]

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id, cursor_type="row", zebra_stripes=False, cell_padding=1)
        self.job_ids: list[int] = []

    def on_mount(self) -> None:
        for key, label, width in COLUMNS:
            self.add_column(label, key=key, width=width)

    def cells(self, r: JobRow) -> tuple[Text | str, ...]:
        widths = {key: w for key, _label, w in COLUMNS}
        loc = (clip(r.location, widths["loc"] - len(DREAM_TAG)) + DREAM_TAG if r.dream
               else clip(r.location, widths["loc"]))
        return (
            "",
            Text(NONE if r.score is None else str(r.score), justify="right"),
            clip(r.company, widths["company"]),
            clip(r.title, widths["title"]),
            loc or NONE,
            r.followup or NONE,
        )

    def load(self, rows: list[JobRow]) -> None:
        self.clear()
        self.job_ids = [r.id for r in rows]
        for r in rows:
            self.add_row(*self.cells(r), key=str(r.id))

    @property
    def current_id(self) -> int | None:
        if not self.job_ids or not 0 <= self.cursor_row < len(self.job_ids):
            return None
        return self.job_ids[self.cursor_row]

    def action_top(self) -> None:
        if self.row_count:
            self.move_cursor(row=0)

    def action_bottom(self) -> None:
        if self.row_count:
            self.move_cursor(row=self.row_count - 1)
