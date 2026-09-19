"""Sections 1 to 3: one three-pane screen (status list, jobs table, detail) under a preset."""
from __future__ import annotations

from textual import events, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Input
from textual.worker import get_current_worker

from .. import commands, data
from ..presets import PRESETS, SORT_COLUMNS, Sort
from ..widgets.detail import DetailPane
from ..widgets.footer import SectionFooter
from ..widgets.jobs_table import JobsTable
from ..widgets.modals import Confirm, DetailOverlay, NotesEditor, Prompt, StatusPicker
from ..widgets.status_list import StatusList
from .base import SectionScreen


WIDE = 120   # under this many columns the detail pane collapses and `enter` opens it as an overlay


class JobsScreen(SectionScreen):
    POLL_SECONDS = 2.0   # how often the DB's mtime is checked for a hunt writing in another pane

    DEFAULT_CSS = """
    JobsScreen #panes { height: 1fr; }
    JobsScreen #middle { width: 1fr; height: 1fr; }
    JobsScreen #search { display: none; height: 1; border: none; padding: 0 1; background: $boost; }
    JobsScreen #search.open { display: block; }
    """

    BINDINGS = [
        Binding("r", "refresh", "refresh"),
        Binding("slash", "search", "search"),
        Binding("greater_than_sign", "sort_move(1)", "sort by next column", key_display=">"),
        Binding("less_than_sign", "sort_move(-1)", "sort by previous column", key_display="<", show=False),
        Binding("minus", "sort_flip", "ascending / descending", key_display="-"),
        Binding("equals_sign", "sort_reset", "back to the section's own sort", key_display="=", show=False),
        Binding("escape", "home", "home: back to the table, search and selection cleared", show=False),
        Binding("tab", "app.focus_next", "next pane: status list, table, detail", show=False),
        Binding("s", "status", "status"),
        Binding("b", "backlog", "backlog"),
        Binding("o", "open(False)", "open posting"),
        Binding("O", "open(True)", "open folder"),
        Binding("c", "copy", "copy /jh-tailor"),
        Binding("n", "notes", "note"),
        Binding("f", "followup", "follow-up"),
        Binding("t", "touch(False)", "touch"),
        Binding("T", "touch(True)", "touch and bump the follow-up", show=False),
    ]

    def __init__(self, preset: str) -> None:
        super().__init__(preset)
        self.preset = preset
        self.status_filter: str | None = None
        self.query_text = ""
        self.sort: Sort | None = None      # None = the preset's own order
        self.seen_mtime = 0.0

    def body(self) -> ComposeResult:
        with Horizontal(id="panes"):
            yield StatusList(PRESETS[self.preset].entries, id="status-list")
            with Vertical(id="middle"):
                yield Input(placeholder="search title, company, notes (d: adds descriptions in all)",
                            id="search")
                yield JobsTable(id="jobs-table")
            yield DetailPane(id="detail")

    def on_mount(self) -> None:
        self.query_one(JobsTable).focus()
        self.query_one(JobsTable).overdue_style = self.app.settings.overdue_style  # type: ignore[attr-defined]
        self.call_after_refresh(self.set_sort, None)      # the arrow on the preset's lead column
        self.seen_mtime = data.db_mtime()
        self.load_counts()
        self.set_interval(self.POLL_SECONDS, self.poll)

    def poll(self) -> None:
        """One stat per tick, a reload only when the file moved. Skipped while this screen is
        not the one on top (another section, or a modal over it): the change is not marked
        seen, so the first tick after coming back picks it up."""
        if self.app.screen is self and data.db_mtime() != self.seen_mtime:
            self.reload()

    def on_screen_resume(self) -> None:
        """Back from a modal or another section: the settings may have changed meanwhile."""
        self.apply_settings()
        self.poll()

    def apply_settings(self) -> None:
        s = self.app.settings  # type: ignore[attr-defined]
        self.query_one("#detail", DetailPane).display = self.wide
        table = self.query_one(JobsTable)
        if table.overdue_style != s.overdue_style:
            table.overdue_style = s.overdue_style
            self.reload()

    def action_refresh(self) -> None:
        self.reload()

    @property
    def wide(self) -> bool:
        """The detail pane sits beside the table: a wide terminal, and the setting allows it."""
        return self.size.width >= WIDE and self.app.settings.detail_pane  # type: ignore[attr-defined]

    def on_resize(self, event: events.Resize) -> None:
        self.query_one("#detail", DetailPane).display = (
            event.size.width >= WIDE and self.app.settings.detail_pane)  # type: ignore[attr-defined]

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
        rows = data.rows(self.preset, self.status_filter, self.query_text, self.sort)
        picks = set(data.picks())
        if PRESETS[self.preset].picks_first and self.sort is None:    # a chosen sort is obeyed as is
            rows = data.picks_first(rows, picks)
        if not worker.is_cancelled:
            today = self.app.today  # type: ignore[attr-defined]
            self.app.call_from_thread(self.query_one(JobsTable).load, rows, today, keep, picks)

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

    # Status changes. The hand-made selection when there is one, else the row under the cursor;
    # never the hunt's pre-selection, so a stray `b` cannot backlog five rows.

    def current_row(self) -> data.JobRow | None:
        return self.query_one(JobsTable).current_row

    def targets(self) -> list[data.JobRow]:
        table = self.query_one(JobsTable)
        return table.selected_rows or ([table.current_row] if table.current_row else [])

    @staticmethod
    def named(rows: list[data.JobRow]) -> str:
        return f"#{rows[0].id} {rows[0].company}" if len(rows) == 1 else f"{len(rows)} selected"

    def action_status(self) -> None:
        rows = self.targets()
        if not rows:
            return

        def picked(status: str | None) -> None:
            if status:
                self.request_status(rows, status)

        current = rows[0].status if len({r.status for r in rows}) == 1 else ""
        self.app.push_screen(StatusPicker(self.named(rows), current), picked)

    def action_backlog(self) -> None:
        rows = self.targets()
        if rows:
            self.request_status(rows, "backlog")

    def request_status(self, rows: list[data.JobRow], status: str) -> None:
        """One confirm for the whole batch, asked when any row in it leaves applied or later."""
        moving = [r for r in rows if r.status != status]
        leaving = [r for r in moving if data.needs_confirm(r.status, status)]
        if not moving:
            return
        if not leaving:
            self.write_status(moving, status)
            return

        def answered(yes: bool | None) -> None:
            if yes:
                self.write_status(moving, status)

        if len(moving) == 1:
            question = f"{self.named(moving)}: leave {moving[0].status} for {status}?"
        else:
            question = (f"{len(moving)} jobs to {status}: {len(leaving)} of them leave "
                        f"{' / '.join(sorted({r.status for r in leaving}, key=data.PIPELINE.index))}?")
        self.app.push_screen(Confirm(question), answered)

    def write_status(self, rows: list[data.JobRow], status: str) -> None:
        if len(rows) == 1:
            self.write(lambda: data.set_status(rows[0].id, status))
        else:
            table = self.query_one(JobsTable)
            table.set_marks(set(), table.dismissed)            # a bulk verb spends its selection
            self.write(lambda: data.set_status_many([r.id for r in rows], status))

    def reload(self) -> None:
        self.seen_mtime = data.db_mtime()
        self.load_counts()
        self.load_rows(keep=True)
        self.load_detail(self.query_one(JobsTable).current_id, overlay=False)

    # Notes and dates.

    def action_notes(self) -> None:
        row = self.current_row()
        if row is not None:
            self.open_notes(row)

    @work(thread=True, group="notes", exclusive=True)
    def open_notes(self, row: data.JobRow) -> None:
        before = data.notes(row.id)      # the table rows do not carry the field

        def saved(text: str | None) -> None:
            if text is not None and text.strip() != before.strip():
                self.write(lambda: data.set_notes(row.id, text))

        self.app.call_from_thread(
            self.app.push_screen, NotesEditor(f"#{row.id} {row.company} notes", before), saved)

    def action_followup(self) -> None:
        row = self.current_row()
        if row is None:
            return
        today = self.app.today  # type: ignore[attr-defined]

        def entered(when: str | None) -> None:
            if when is not None and when != (row.followup or ""):
                self.write(lambda: data.set_followup(row.id, when))

        days = self.app.settings.followup_days  # type: ignore[attr-defined]
        self.app.push_screen(Prompt(f"#{row.id} {row.company} follow-up",
                                    f"YYYY-MM-DD, +N (+{days}), t; empty clears",
                                    lambda text: data.parse_followup(text, today),
                                    row.followup or ""), entered)

    def action_touch(self, bump: bool) -> None:
        row = self.current_row()
        if row is not None:
            self.write(lambda: data.touch(row.id, bump))

    # Open: `o` the posting, `O` the application folder, or the dossier when there is no folder.

    def action_open(self, folder: bool) -> None:
        row = self.current_row()
        if row is not None:
            self.open_job(row.id, folder)

    @work(thread=True, group="open")
    def open_job(self, job_id: int, folder: bool) -> None:
        d = data.detail(job_id)
        try:
            if d is None:
                raise ValueError(f"#{job_id} is gone")
            target = d.folder or d.dossier
            if not folder:
                line = commands.open_posting(d.url)
            elif target is not None:
                line = commands.open_path(target)
            else:
                raise ValueError(f"#{job_id} has no application folder and no dossier yet")
        except (ValueError, OSError) as e:
            self.app.call_from_thread(self.toast, str(e), "warning")
            return
        self.app.call_from_thread(self.toast, line)

    # Copy: `c` every marked row listed (the hunt's picks arrive marked, so on a fresh shortlist
    # that is what a hunt would tailor), else the row under the cursor. One `/jh-tailor <id>`
    # per line, in table order; a multi-line paste runs in order.

    def action_copy(self) -> None:
        table = self.query_one(JobsTable)
        rows = table.marked_rows or ([table.current_row] if table.current_row else [])
        self.copy_commands([r.id for r in rows])

    @work(thread=True, group="copy")
    def copy_commands(self, ids: list[int]) -> None:
        if not ids:
            self.app.call_from_thread(self.toast, "no row to copy", "warning")
            return
        commands.copy(commands.tailor_commands(ids),
                      lambda text: self.app.call_from_thread(self.app.copy_to_clipboard, text))
        self.app.call_from_thread(self.toast, commands.copied_line(ids))

    # Search: live, inside the current filter. `enter` keeps the query and goes back to the
    # table; `esc` clears it from wherever the focus is.

    def action_search(self) -> None:
        box = self.query_one("#search", Input)
        box.add_class("open")
        box.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search" and event.value != self.query_text:
            self.query_text = event.value
            self.load_rows()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search":
            self.query_one(JobsTable).focus()

    def action_home(self) -> None:
        box = self.query_one("#search", Input)
        box.remove_class("open")
        if box.value:
            box.value = ""          # fires Changed, which reloads the unfiltered rows
        table = self.query_one(JobsTable)
        table.clear_marks()
        table.focus()

    def on_jobs_table_selection_changed(self, event: JobsTable.SelectionChanged) -> None:
        parts = [f"{event.selected} selected" if event.selected else "",
                 f"{event.picked} hunt pick{'' if event.picked == 1 else 's'}" if event.picked else ""]
        self.query_one(SectionFooter).note = " · ".join(p for p in parts if p)

    # Sort. `>` `<` pick the column, `-` flips, `=` returns to the preset; a header click does
    # both (first click sorts by that column, the next one flips). The order is made in SQL.

    def set_sort(self, sort: Sort | None) -> None:
        changed = sort != self.sort
        self.sort = sort
        self.query_one(JobsTable).mark_sort(sort or PRESETS[self.preset].leads)
        if changed:
            self.load_rows(keep=True)

    def action_sort_move(self, step: int) -> None:
        keys = list(SORT_COLUMNS)
        at = keys.index((self.sort or PRESETS[self.preset].leads).column)
        self.set_sort(Sort.first(keys[(at + step) % len(keys)]))

    def action_sort_flip(self) -> None:
        self.set_sort((self.sort or PRESETS[self.preset].leads).flipped())

    def action_sort_reset(self) -> None:
        self.set_sort(None)

    def on_data_table_header_selected(self, event: JobsTable.HeaderSelected) -> None:
        column = event.column_key.value or ""
        if column not in SORT_COLUMNS:
            return                                  # the star column
        now = self.sort or PRESETS[self.preset].leads
        self.set_sort(now.flipped() if now.column == column else Sort.first(column))
