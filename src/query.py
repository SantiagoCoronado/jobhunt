"""Read-only DB queries used by the Claude Code commands.

  python -m src.query job <id>     # one job as JSON (for /jh-tailor)
  python -m src.query crm          # all trackable jobs as JSON (for /jh-notion-sync)
  python -m src.query followups    # jobs due for follow-up (for /jh-followups)
"""
from __future__ import annotations

import argparse
import json
import sys

from .db import connect


def _dump(rows):
    print(json.dumps([dict(r) for r in rows], indent=2, default=str))


def job(job_id: str) -> None:
    r = connect().execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not r:
        sys.exit(f"No job with id {job_id}")
    print(json.dumps(dict(r), indent=2, default=str))


def crm() -> None:
    rows = connect().execute(
        "SELECT id,company,title,location,url,match_score,status,applied_at,"
        "next_followup_at,notes FROM jobs WHERE status!='discovered' "
        "ORDER BY COALESCE(match_score,0) DESC"
    ).fetchall()
    _dump(rows)


def followups() -> None:
    rows = connect().execute(
        "SELECT id,company,title,url,status,applied_at,last_contact_at,"
        "next_followup_at,notes FROM jobs "
        "WHERE status IN ('applied','screen','interview') "
        "ORDER BY next_followup_at IS NULL, next_followup_at"
    ).fetchall()
    _dump(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("job"); j.add_argument("id")
    sub.add_parser("crm")
    sub.add_parser("followups")
    a = ap.parse_args()
    if a.cmd == "job":
        job(a.id)
    elif a.cmd == "crm":
        crm()
    else:
        followups()
