"""Y Combinator Work at a Startup. Listings are readable in-browser, but the job-search
JSON API returns HTTP 406 without a browser session (needs session/CSRF headers). Left
DISABLED until that session flow is reproduced. Rich source of "Founding Engineer /
Applied AI" roles once wired.
"""
from __future__ import annotations

from ..models import Job  # noqa: F401  (kept for the annotation / when wired)


def fetch(cfg: dict) -> list[Job]:
    print("  ! workatastartup: job API needs a browser session (406 otherwise); not yet wired")
    return []
