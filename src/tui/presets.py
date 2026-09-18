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

# ORDER BY fragments. Literals only: they are spliced into SQL, never built from input.
BY_SCORE = "match_score IS NULL, match_score DESC, id DESC"
BY_FOLLOWUP = "next_followup_at IS NULL, next_followup_at ASC, match_score DESC, id DESC"


@dataclass(frozen=True)
class Preset:
    name: str
    statuses: tuple[str, ...]   # what the preset shows when no status is picked in the left pane
    order_by: str


PRESETS: dict[str, Preset] = {
    "board": Preset("board", HOT, BY_SCORE),
    "shortlist": Preset("shortlist", ("shortlisted",), BY_SCORE),
    "followups": Preset("followups", ("applied", "screen", "interview"), BY_FOLLOWUP),
}
