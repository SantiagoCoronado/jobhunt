"""Consider VC talent boards (e.g. Sequoia). Pattern: consider.com/boards/vc/{board}/jobs.
The board is fully client-rendered and its runtime JSON endpoint is undocumented; a
static fetch returns no job data. Left DISABLED until the network JSON call is captured
(open a board, inspect DevTools -> Network) and wired here. cfg.boards: firm slugs.
"""
from __future__ import annotations

from ..models import Job  # noqa: F401  (kept for the annotation / when wired)


def fetch(cfg: dict) -> list[Job]:
    if cfg.get("boards"):
        print("  ! consider: JSON endpoint not yet wired (client-rendered board); capture the "
              "network call at consider.com/boards/vc/<firm>/jobs to enable")
    return []
