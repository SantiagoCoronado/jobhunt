"""Board, shortlist and follow-ups: the same rows under three filters and sorts (spec decision 9)."""
from __future__ import annotations

from dataclasses import dataclass

from ..db import STATUSES

# Never shown anywhere in the TUI; `stats drops` audits them (spec decision 14).
NEVER = ("irrelevant", "expired")
# `discovered` is cold: it only appears behind the dimmed `all` entry.
COLD = ("discovered",)
HOT: tuple[str, ...] = tuple(s for s in STATUSES if s not in NEVER + COLD)
ALL = "all"
LIVE = ("applied", "screen", "interview")   # a follow-up date means something only here
OVERDUE_STYLE = "red"

# ORDER BY fragments. Literals only: they are spliced into SQL, never built from input.
BY_SCORE = "match_score IS NULL, match_score DESC, id DESC"
BY_FOLLOWUP = "next_followup_at IS NULL, next_followup_at ASC, match_score DESC, id DESC"


# The columns the table can be sorted by (its own keys) and the SQL each one orders on.
SORT_COLUMNS: dict[str, str] = {
    "score": "match_score",
    "company": "company COLLATE NOCASE",
    "title": "title COLLATE NOCASE",
    "loc": "location COLLATE NOCASE",
    "fup": "next_followup_at",
}
FIRST_DESC = ("score",)   # a first sort on these starts high to low; text and dates start A to Z, soonest


@dataclass(frozen=True)
class Sort:
    column: str
    desc: bool

    @classmethod
    def first(cls, column: str) -> Sort:
        return cls(column, column in FIRST_DESC)

    def flipped(self) -> Sort:
        return Sort(self.column, not self.desc)

    @property
    def order_by(self) -> str:
        """Empty values last in BOTH directions: a missing score or date is not the smallest
        value, it is no value. Built from the whitelist above, never from input."""
        if self.column not in SORT_COLUMNS:
            raise ValueError(f"{self.column!r} is not a sortable column")
        expr = SORT_COLUMNS[self.column]
        col = expr.split()[0]
        return f"({col} IS NULL OR {col} = ''), {expr} {'DESC' if self.desc else 'ASC'}, id DESC"


@dataclass(frozen=True)
class Preset:
    name: str
    statuses: tuple[str, ...]   # what the preset shows when no status is picked in the left pane
    order_by: str
    listed: tuple[str, ...] = ()   # the left pane's entries; empty = the same as `statuses`
    leads: Sort = Sort("score", True)   # the column and direction `order_by` leads with

    @property
    def entries(self) -> tuple[str, ...]:
        return self.listed or self.statuses


PRESETS: dict[str, Preset] = {
    "board": Preset("board", HOT, BY_SCORE, listed=(*HOT, ALL)),
    "shortlist": Preset("shortlist", ("shortlisted",), BY_SCORE),
    # The head entry (the preset's own name) is every live application at once, soonest
    # follow-up first: that is the view the section exists for.
    "followups": Preset("followups", LIVE, BY_FOLLOWUP, listed=("followups", *LIVE),
                        leads=Sort("fup", False)),
}
LABELS = {"followups": "follow-ups"}   # left-pane wording for a head entry
