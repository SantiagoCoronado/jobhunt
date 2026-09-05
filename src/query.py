"""DB queries + status transitions used by the Claude Code commands.

  python -m src.query job <id>          # one job as JSON (for /jh-tailor)
  python -m src.query crm               # all trackable jobs as JSON (gmail-sync MCP fallback)
  python -m src.query followups         # jobs due for follow-up (for /jh-followups)
  python -m src.query set-status <id> <status> [--note "..."] [--followup YYYY-MM-DD]
                                        # record a transition; flipping to applied stamps
                                        # applied_at + schedules the follow-up, and the
                                        # application folder moves to its right bucket
  python -m src.query touch <id> [--date YYYY-MM-DD] [--bump]
                                        # record contact (reply seen / nudge sent);
                                        # --bump pushes next_followup_at out again
  python -m src.query add --company C --title T [--url U] [--status shortlisted] [--note ...]
                                        # hand-enter a role no board carries (outreach,
                                        # referral); source='manual', idempotent on
                                        # company+title, the only non-discovery insert path
"""
from __future__ import annotations

import argparse
import json
import sys

from .config import followup_days
from .db import STATUSES, connect, set_status as _set_status, touch_contact, upsert_job
from .dream import is_dream
from .models import Job, normalize_text, now_iso


def _with_dream(r) -> dict:
    """Row -> dict plus `dream` (profile.yaml dream_companies; computed, never stored)."""
    d = dict(r)
    d["dream"] = is_dream(d.get("company"))
    return d


def _dump(rows):
    print(json.dumps([_with_dream(r) for r in rows], indent=2, default=str))


def job(job_id: str) -> None:
    r = connect().execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not r:
        sys.exit(f"No job with id {job_id}")
    print(json.dumps(_with_dream(r), indent=2, default=str))


def crm() -> None:
    rows = connect().execute(
        "SELECT id,company,title,location,url,match_score,status,applied_at,"
        "next_followup_at,notes FROM jobs "
        "WHERE status NOT IN ('discovered','irrelevant','expired') "
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


def cmd_set_status(job_id: str, status: str, note: str | None, followup: str | None) -> None:
    from .reconcile import sync_folder  # local import: keeps read-only paths light

    conn = connect()
    try:
        changed = _set_status(conn, job_id, status, note=note,
                              next_followup=followup, followup_days=followup_days())
    except ValueError as e:
        sys.exit(str(e))
    conn.commit()
    moved = sync_folder(int(changed["id"]), status)
    if moved:
        changed["folder"] = moved
    print(json.dumps(changed, indent=2, default=str))


def cmd_event(job_id: str, kind: str, note: str | None) -> None:
    from .db import log_event

    conn = connect()
    if not conn.execute("SELECT 1 FROM jobs WHERE id=?", (job_id,)).fetchone():
        sys.exit(f"No job with id {job_id}")
    log_event(conn, job_id, kind, {"note": note} if note else None)
    conn.commit()
    print(json.dumps({"id": job_id, "event": kind, "note": note}))


def cmd_add(company: str, title: str, url: str | None, status: str, note: str | None) -> None:
    """Insert one hand-entered role (source='manual') and set its status.

    Same external_id scheme the Notion pull used, so re-adding the same company+title
    is a no-op ('seen') instead of a duplicate. Status goes through set_status so the
    events row, applied_at and the folder bucket behave like any other row.
    """
    conn = connect()
    job = Job(source="manual",
              external_id=normalize_text(f"{company} {title}").replace(" ", "-"),
              url=url or "", company=company, title=title)
    outcome = upsert_job(conn, job.to_row(), now_iso())
    job_id = conn.execute("SELECT id FROM jobs WHERE source='manual' AND external_id=?",
                          (job.external_id,)).fetchone()["id"]
    if outcome == "new":
        _set_status(conn, job_id, status, note=note, followup_days=followup_days())
    conn.commit()
    print(json.dumps({"id": job_id, "outcome": outcome, "company": company, "title": title,
                      "status": status if outcome == "new" else "unchanged"}, indent=2))


def cmd_touch(job_id: str, date: str | None, bump: bool) -> None:
    conn = connect()
    try:
        changed = touch_contact(conn, job_id, contact_date=date,
                                bump_days=followup_days() if bump else None)
    except ValueError as e:
        sys.exit(str(e))
    conn.commit()
    print(json.dumps(changed, indent=2, default=str))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("job")
    j.add_argument("id")
    sub.add_parser("crm")
    sub.add_parser("followups")
    s = sub.add_parser("set-status", help="record a status transition")
    s.add_argument("id")
    s.add_argument("status", choices=STATUSES)
    s.add_argument("--note", help="appended to the job's notes")
    s.add_argument("--followup", help="explicit next follow-up date YYYY-MM-DD")
    t = sub.add_parser("touch", help="record contact with the company")
    t.add_argument("id")
    t.add_argument("--date", help="contact date YYYY-MM-DD (default today)")
    t.add_argument("--bump", action="store_true",
                   help="push next_followup_at out another followup_days")
    e = sub.add_parser("event", help="log an event (debrief, note) for a job")
    e.add_argument("id")
    e.add_argument("kind")
    e.add_argument("--note", help="short free-text payload")
    ad = sub.add_parser("add", help="hand-enter a role that no board carries")
    ad.add_argument("--company", required=True)
    ad.add_argument("--title", required=True)
    ad.add_argument("--url", help="posting or company page, if any")
    ad.add_argument("--status", default="shortlisted", choices=STATUSES)
    ad.add_argument("--note", help="appended to the job's notes")
    a = ap.parse_args()
    if a.cmd == "job":
        job(a.id)
    elif a.cmd == "crm":
        crm()
    elif a.cmd == "followups":
        followups()
    elif a.cmd == "set-status":
        cmd_set_status(a.id, a.status, a.note, a.followup)
    elif a.cmd == "event":
        cmd_event(a.id, a.kind, a.note)
    elif a.cmd == "add":
        cmd_add(a.company, a.title, a.url, a.status, a.note)
    else:
        cmd_touch(a.id, a.date, a.bump)
