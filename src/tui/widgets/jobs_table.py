"""Middle pane: one line per job, in the order the preset's sort returned them."""
from __future__ import annotations

from datetime import date

from rich.text import Text
from textual.binding import Binding
from textual.message import Message
from textual.widgets import DataTable

from ..data import JobRow
from ..presets import LIVE, OVERDUE_STYLE, Sort

NONE = "·"
MARK = "●"
PICK_STYLE = "yellow"   # a mark the hunt made (`src.pick` would choose the row), not the reader
# (key, label, width). The first column carries the selection mark.
COLUMNS: tuple[tuple[str, str, int], ...] = (
    ("mark", " ", 1),
    ("score", "score", 7),
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
        Binding("space", "toggle_mark", "select"),
        Binding("v", "mark_all", "select every row listed", show=False),
        Binding("C", "repick", "select the hunt's picks again", show=False),
    ]

    class SelectionChanged(Message):
        def __init__(self, selected: int, picked: int) -> None:
            super().__init__()
            self.selected = selected      # marked by hand
            self.picked = picked          # pre-selected and listed

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id, cursor_type="row", zebra_stripes=False, cell_padding=1)
        self.job_ids: list[int] = []
        self.rows_by_id: dict[int, JobRow] = {}
        self.picks: set[int] | frozenset[int] = frozenset()   # what `src.pick` would choose
        self.dismissed: set[int] = set()                       # picks the reader took the mark off
        self.selected: set[int] = set()                        # marked by hand
        self.overdue_style = OVERDUE_STYLE                     # the screen sets it from the settings

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
            self.mark_cell(r.id),
            Text(NONE if r.score is None else str(r.score), justify="right"),
            Text(clip(r.company, widths["company"])),
            Text(clip(r.title, widths["title"])),
            Text(loc or NONE),
            self.followup_cell(r, today, self.overdue_style),
        )

    def mark_cell(self, job_id: int) -> Text:
        if job_id in self.selected:
            return Text(MARK)
        return Text(MARK, style=PICK_STYLE) if job_id in self.preselected else Text("")

    @staticmethod
    def followup_cell(r: JobRow, today: date | None, overdue_style: str = OVERDUE_STYLE) -> Text:
        """Red (or the style `config/tui.toml` names) once the date has passed, and only while the application is live: a stale date
        on a rejected row is history, not something to chase."""
        if not r.followup:
            return Text(NONE)
        overdue = today is not None and r.status in LIVE and r.followup < today.isoformat()
        return Text(r.followup, style=overdue_style if overdue else "")

    def load(self, rows: list[JobRow], today: date | None = None, keep: bool = False,
             picks: set[int] | frozenset[int] = frozenset()) -> None:
        """Replace the rows. With `keep` (a reload of the same view) the cursor stays on the same
        job when it is still listed, else on the same line, where the row below slid up; a
        status change must not throw the reader back to the top. A new filter starts at the top.
        The marks follow the same rule: kept for the rows still listed, while a new filter drops
        the hand-made ones and brings the hunt's picks back."""
        was_id, was_line, before = self.current_id, self.cursor_row, self._counts()
        self.clear()
        self.job_ids = [r.id for r in rows]
        self.rows_by_id = {r.id: r for r in rows}
        self.picks = picks
        self.selected = self.selected & set(self.job_ids) if keep else set()
        self.dismissed = self.dismissed & set(picks) if keep else set()
        for r in rows:
            self.add_row(*self.cells(r, today), key=str(r.id))
        if keep and rows and was_id is not None:
            line = self.job_ids.index(was_id) if was_id in self.rows_by_id else min(was_line, len(rows) - 1)
            self.move_cursor(row=line)
        self._announce(before)

    # Marks. Two kinds share one `●`: the hunt's picks arrive pre-selected (yellow) and feed
    # `c` only; a hand-made mark also feeds the bulk verbs. `space` works on the row under the
    # cursor and steps down, so a run of rows is a run of spaces: it takes a pick's mark off,
    # else toggles a hand-made one. `v` marks every row listed, `C` brings the picks back, the
    # screen's `esc` clears both kinds.

    @property
    def preselected(self) -> set[int]:
        return set(self.picks) - self.dismissed - self.selected

    def _counts(self) -> tuple[int, int]:
        return len(self.selected), len(self.preselected & self.rows_by_id.keys())

    def set_marks(self, selected: set[int], dismissed: set[int]) -> None:
        was = {i: self.mark_cell(i) for i in (self.selected | set(self.picks)) & self.rows_by_id.keys()}
        before = self._counts()
        self.selected, self.dismissed = set(selected), set(dismissed)
        for job_id in (was.keys() | self.selected) & self.rows_by_id.keys():
            cell = self.mark_cell(job_id)
            if was.get(job_id) != cell:
                self.update_cell(str(job_id), "mark", cell)
        self._announce(before)

    def _announce(self, before: tuple[int, int]) -> None:
        if self._counts() != before:
            self.post_message(self.SelectionChanged(*self._counts()))

    def clear_marks(self) -> None:
        self.set_marks(set(), set(self.picks))

    @property
    def selected_rows(self) -> list[JobRow]:
        """Marked by hand, in table order, so a bulk verb reads top to bottom."""
        return [self.rows_by_id[i] for i in self.job_ids if i in self.selected]

    @property
    def marked_rows(self) -> list[JobRow]:
        """Every marked row listed, the hunt's picks included: what `c` copies."""
        marked = self.selected | self.preselected
        return [self.rows_by_id[i] for i in self.job_ids if i in marked]

    def action_toggle_mark(self) -> None:
        job_id = self.current_id
        if job_id is None:
            return
        if job_id in self.preselected:
            self.set_marks(self.selected, self.dismissed | {job_id})
        else:
            self.set_marks(self.selected ^ {job_id}, self.dismissed)
        self.action_cursor_down()

    def action_mark_all(self) -> None:
        self.set_marks(set(self.job_ids), self.dismissed)

    def action_repick(self) -> None:
        self.set_marks(self.selected, set())

    def mark_sort(self, sort: Sort) -> None:
        """`▲` or `▼` on the header the rows are ordered by (the preset's own lead included)."""
        for key, label, _width in COLUMNS:
            arrow = (" ▼" if sort.desc else " ▲") if key == sort.column else ""
            self.columns[key].label = Text(label + arrow)      # type: ignore[index]
        self.refresh()

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
