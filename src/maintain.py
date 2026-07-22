"""Nightly DB maintenance: expire vanished postings, prune dead descriptions.

Runs automatically at the end of `python -m src.discover`; run standalone with

  python -m src.maintain [--vacuum]

Expiry: a job still at `status='discovered'` whose source has had a successful
run SINCE the job was last seen, and that hasn't been seen for EXPIRE_DAYS, has
dropped out of its feed: the posting is likely closed. It becomes `expired`
(terminal junk, excluded from triage/match/CRM). Jobs from sources that simply
stopped running are NOT expired: absence of evidence only counts when the
source was actually checked.

Description pruning (the DB-bloat fix; descriptions are ~80% of the file):
- `irrelevant` rows keep only the first 300 chars, exactly the excerpt the
  Haiku triage judged them on, so drop audits keep their evidence.
- `expired` rows unseen for PRUNE_DAYS lose the description entirely.
VACUUM only reclaims file space when something was pruned (or --vacuum).
"""
from __future__ import annotations

import argparse
import sqlite3

from .db import connect

EXPIRE_DAYS = 14
PRUNE_DAYS = 30
TRIAGE_EXCERPT = 300  # keep what triage saw (triage.py truncates to 300)
VACUUM_MIN_PRUNED = 200


def expire_stale(conn: sqlite3.Connection, days: int = EXPIRE_DAYS) -> int:
    cur = conn.execute(
        f"""
        UPDATE jobs SET status='expired'
        WHERE status='discovered'
          -- datetime() normalizes last_seen's ISO form ('T' separator, +00:00
          -- offset, microseconds) to SQLite's format; comparing the raw string
          -- against datetime('now',...) is off by a day ('T' sorts after ' ').
          AND datetime(last_seen) < datetime('now', '-{int(days)} days')
          AND EXISTS (
              SELECT 1 FROM runs
              WHERE runs.source = jobs.source AND runs.ok = 1
                AND runs.pulled > 0 AND runs.ts > jobs.last_seen
          )
        """
    )
    return cur.rowcount


def prune_descriptions(conn: sqlite3.Connection, days: int = PRUNE_DAYS) -> int:
    truncated = conn.execute(
        "UPDATE jobs SET description = substr(description, 1, ?) "
        "WHERE status='irrelevant' AND length(description) > ?",
        (TRIAGE_EXCERPT, TRIAGE_EXCERPT),
    ).rowcount
    cleared = conn.execute(
        f"UPDATE jobs SET description = NULL "
        f"WHERE status='expired' AND description IS NOT NULL "
        f"AND datetime(last_seen) < datetime('now', '-{int(days)} days')"
    ).rowcount
    return truncated + cleared


def run(conn: sqlite3.Connection | None = None, force_vacuum: bool = False) -> dict:
    conn = conn or connect()
    expired = expire_stale(conn)
    pruned = prune_descriptions(conn)
    conn.commit()
    did_vacuum = False
    if force_vacuum or pruned >= VACUUM_MIN_PRUNED:
        conn.execute("VACUUM")  # no open transaction after the commit above
        did_vacuum = True
    return {"expired": expired, "pruned": pruned, "vacuumed": did_vacuum}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vacuum", action="store_true", help="force VACUUM even if little was pruned")
    args = ap.parse_args()
    r = run(force_vacuum=args.vacuum)
    print(f"Expired {r['expired']} vanished postings; pruned {r['pruned']} descriptions"
          f"{'; VACUUMed' if r['vacuumed'] else ''}.")


if __name__ == "__main__":
    main()
