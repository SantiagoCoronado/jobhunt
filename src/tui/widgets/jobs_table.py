"""Middle pane: one line per job, in the order the preset's sort returned them."""
from __future__ import annotations

from datetime import date

from rich.text import Text
from textual import events
from textual.binding import Binding
from textual.widgets import DataTable

from ..data import JobRow
from ..presets import LIVE, OVERDUE_STYLE, Sort
from ..selection import Selection

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
TITLE_MIN = 16          # the title column takes the table's slack and never gets narrower than this


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

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id, cursor_type="row", zebra_stripes=False, cell_padding=1)
        self.job_ids: list[int] = []
        self.rows_by_id: dict[int, JobRow] = {}
        self.marks = Selection()                               # the screen hands it the app's one
        self.drawn: dict[int, str] = {}                        # the kind of mark each row shows now
        self.overdue_style = OVERDUE_STYLE                     # the screen sets it from the settings
        self.widths = {key: w for key, _label, w in COLUMNS}   # `title` follows the table's width

    def on_mount(self) -> None:
        for key, label, width in COLUMNS:
            self.add_column(label, key=key, width=width)

    def on_resize(self, event: events.Resize) -> None:
        """The columns are fixed except the title, which takes what is left: the table fits its
        pane, so no horizontal scrollbar, until the pane is too narrow even for TITLE_MIN."""
        fixed = sum(w for key, w in self.widths.items() if key != "title") + 2 * self.cell_padding * len(COLUMNS)
        width = max(TITLE_MIN, event.size.width - fixed - 1)             # 1: the vertical scrollbar
        if width != self.widths["title"] and any(k.value == "title" for k in self.columns):
            self.widths["title"] = width
            self.columns["title"].width = width                          # type: ignore[index]
            for r in self.rows_by_id.values():
                self.update_cell(str(r.id), "title", Text(clip(r.title, width)))
            # DataTable measures its virtual size when a cell or a row changes, not when a
            # column's width is set by hand; without this the old width keeps the scrollbar.
            self._require_update_dimensions = True
            self.refresh(layout=True)

    def cells(self, r: JobRow, today: date | None = None) -> tuple[Text, ...]:
        """Every cell is a `Text`. DataTable runs `Text.from_markup` on a `str` cell, and these
        strings come from scraped postings: `[on-site]` would vanish, `[/bold]` would raise
        MarkupError and kill the table, `[link=file:///...]` would plant a link that never
        passed the http(s) check in `commands.open_posting`."""
        widths = self.widths
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
        kind = self.marks.kind(job_id)
        return Text(MARK, style=PICK_STYLE if kind == "pick" else "") if kind else Text("")

    @staticmethod
    def followup_cell(r: JobRow, today: date | None, overdue_style: str = OVERDUE_STYLE) -> Text:
        """Red (or the style `config/tui.toml` names) once the date has passed, and only while the application is live: a stale date
        on a rejected row is history, not something to chase."""
        if not r.followup:
            return Text(NONE)
        overdue = today is not None and r.status in LIVE and r.followup < today.isoformat()
        return Text(r.followup, style=overdue_style if overdue else "")

    def load(self, rows: list[JobRow], today: date | None = None, keep: bool = False,
             picks: list[int] | None = None, held: list[JobRow] | None = None,
             asked: frozenset[int] | None = None) -> None:
        """Replace the rows. With `keep` (a reload of the same view) the cursor stays on the same
        job when it is still listed, else on the same line, where the row below slid up; a
        status change must not throw the reader back to the top. A new filter starts at the top.
        The marks are the app's and outlive the view: `held` is the marked rows the loader still
        found outside it, so a mark goes only when its row left the statuses the TUI lists."""
        was_id, was_line = self.current_id, self.cursor_row
        # First, while the old rows are still here: a change redraws the marks of what is listed.
        self.marks.loaded(picks or [], [*(held or []), *rows], [r.id for r in rows], asked)
        self.clear()
        self.job_ids = [r.id for r in rows]
        self.rows_by_id = {r.id: r for r in rows}
        for r in rows:
            self.add_row(*self.cells(r, today), key=str(r.id))
        self.drawn = {r.id: self.marks.kind(r.id) for r in rows}
        if keep and rows and was_id is not None:
            line = self.job_ids.index(was_id) if was_id in self.rows_by_id else min(was_line, len(rows) - 1)
            self.move_cursor(row=line)

    # Marks. Two kinds share one `●`: the hunt's picks arrive pre-selected (yellow) and feed
    # `c` and the runner only; a hand-made mark also feeds the bulk verbs. `space` works on the
    # row under the cursor and steps down, so a run of rows is a run of spaces: it takes a pick's
    # mark off, else toggles a hand-made one. `v` marks every row listed, `C` brings the picks
    # back, the screen's `esc` clears both kinds. The marks themselves live in `self.marks`.

    @property
    def selected(self) -> set[int]:
        return self.marks.selected

    @property
    def dismissed(self) -> set[int]:
        return self.marks.dismissed

    @property
    def preselected(self) -> set[int]:
        return self.marks.preselected

    def set_marks(self, selected: set[int], dismissed: set[int]) -> None:
        self.marks.set(selected, dismissed, self.job_ids, self.rows_by_id)
        self.redraw_marks()

    def redraw_marks(self) -> None:
        """Only the cells whose mark changed, wherever the change was made."""
        for job_id in self.job_ids:
            kind = self.marks.kind(job_id)
            if self.drawn.get(job_id, "") != kind:
                self.drawn[job_id] = kind
                self.update_cell(str(job_id), "mark", self.mark_cell(job_id))

    def clear_marks(self) -> None:
        self.set_marks(set(), set(self.marks.picks))

    @property
    def selected_rows(self) -> list[JobRow]:
        return self.marks.selected_rows

    @property
    def marked_rows(self) -> list[JobRow]:
        return self.marks.marked_rows

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
        self.set_marks(self.selected | set(self.job_ids), self.dismissed)

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
