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


@dataclass(frozen=True)
class Preset:
    name: str
    statuses: tuple[str, ...]   # what the preset shows when no status is picked in the left pane
    order_by: str
    listed: tuple[str, ...] = ()   # the left pane's entries; empty = the same as `statuses`

    @property
    def entries(self) -> tuple[str, ...]:
        return self.listed or self.statuses


PRESETS: dict[str, Preset] = {
    "board": Preset("board", HOT, BY_SCORE, listed=(*HOT, ALL)),
    "shortlist": Preset("shortlist", ("shortlisted",), BY_SCORE),
    # The head entry (the preset's own name) is every live application at once, soonest
    # follow-up first: that is the view the section exists for.
    "followups": Preset("followups", LIVE, BY_FOLLOWUP, listed=("followups", *LIVE)),
}
LABELS = {"followups": "follow-ups"}   # left-pane wording for a head entry
