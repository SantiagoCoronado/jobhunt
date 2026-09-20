"""The marked rows, held once for the whole app (spec decisions 11, 15): every jobs table draws
from it and the runner runs it, so a section switch or another filter never drops a mark.

Two kinds share one `●`. A hand-made mark (`space`, `v`) feeds every verb. The hunt's picks
arrive pre-selected and feed `c` and the runner only; `dismissed` is the picks the reader took
the mark off. A mark goes when its row leaves the statuses the TUI lists (the loader passes
the rows it still found), a pick the moment `src.pick` stops choosing it.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable

from .data import JobRow


class Selection:
    def __init__(self) -> None:
        self.selected: set[int] = set()          # marked by hand
        self.dismissed: set[int] = set()         # picks the reader took the mark off
        self.picks: list[int] = []               # what `src.pick` would choose, in its order
        self.rows: dict[int, JobRow] = {}        # what is known about every marked row
        self.order: list[int] = []               # table order, as the last table listed them
        self.on_change: Callable[[], None] | None = None

    @property
    def preselected(self) -> set[int]:
        return set(self.picks) - self.dismissed - self.selected

    @property
    def marked(self) -> set[int]:
        return self.selected | self.preselected

    def kind(self, job_id: int) -> str:
        """"hand", "pick" or "": what the mark column draws."""
        if job_id in self.selected:
            return "hand"
        return "pick" if job_id in self.preselected else ""

    def _in_order(self, ids: set[int]) -> list[JobRow]:
        return [self.rows[i] for i in self.order if i in ids and i in self.rows]

    @property
    def selected_rows(self) -> list[JobRow]:
        """Marked by hand, in table order, so a bulk verb reads top to bottom."""
        return self._in_order(self.selected)

    @property
    def marked_rows(self) -> list[JobRow]:
        """Every marked row, the hunt's picks included: what `c` copies and the runner runs."""
        return self._in_order(self.marked)

    def counts(self) -> tuple[int, int]:
        return len(self.selected), len(self.preselected)

    def note(self) -> str:
        """The footer's state line, the same on every section."""
        selected, picked = self.counts()
        parts = [f"{selected} selected" if selected else "",
                 f"{picked} hunt pick{'' if picked == 1 else 's'}" if picked else ""]
        return " · ".join(p for p in parts if p)

    def _reorder(self, listed: Iterable[int] = ()) -> None:
        marked = self.marked
        head = [i for i in listed if i in marked]
        seen = set(head)
        self.order = head + [i for i in self.order if i in marked and i not in seen]
        self.order += sorted(marked - set(self.order))          # a pick no table has listed yet

    def _changed(self, before: tuple[set[int], set[int]]) -> None:
        if (self.selected, self.preselected) != before and self.on_change is not None:
            self.on_change()

    def set(self, selected: set[int], dismissed: set[int], listed: Iterable[int] = (),
            known: dict[int, JobRow] | None = None) -> None:
        """`known` is the rows of the table the marks were made in: a new mark brings its row."""
        before = (set(self.selected), self.preselected)
        self.selected, self.dismissed = set(selected), set(dismissed)
        marked = self.marked
        self.rows = {i: r for i, r in {**(known or {}), **self.rows}.items() if i in marked}
        self._reorder(listed)
        self._changed(before)

    def loaded(self, picks: list[int], found: Iterable[JobRow], listed: Iterable[int],
               asked: Iterable[int] | None = None) -> None:
        """A table read the DB again: the picks as they are now, and every marked row it still
        found. A hand-made mark on a row that was not found (it left the listed statuses) goes.
        `asked` is the marks the loader looked up when it started: a mark made while it was
        reading (in this table or the other jobs section) was never looked up, so not finding
        it says nothing, and it stays."""
        before = (set(self.selected), self.preselected)
        self.picks = list(picks)
        fresh = {r.id: r for r in found}
        checked = set(self.selected) if asked is None else set(asked) & self.selected
        self.selected -= checked - fresh.keys()
        rows = {**self.rows, **fresh}                # a mark that was not looked up keeps its row
        self.dismissed &= set(picks)
        self.rows = {i: r for i, r in rows.items() if i in self.marked}
        self._reorder(listed)
        self._changed(before)

    def drop(self, job_id: int) -> None:
        """Take one row off, whichever kind its mark is."""
        if job_id in self.selected:
            self.set(self.selected - {job_id}, self.dismissed, ())
        elif job_id in self.preselected:
            self.set(self.selected, self.dismissed | {job_id}, ())

    def toggle(self, row: JobRow, pick: bool) -> None:
        """The runner's checklist: take a row's mark off, or put back the one it had. `pick`
        says which kind it was, since an unmarked row no longer tells."""
        if row.id in self.marked:
            self.drop(row.id)
        elif pick and row.id in self.picks:
            self.set(self.selected, self.dismissed - {row.id}, (), {row.id: row})
        else:
            self.set(self.selected | {row.id}, self.dismissed, (), {row.id: row})

    def spend(self, ids: Iterable[int]) -> None:
        """A verb ran on these rows: their marks go, a pick among them stays off."""
        ids = set(ids)
        self.set(self.selected - ids, self.dismissed | (ids & set(self.picks)), ())
