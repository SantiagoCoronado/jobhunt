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
  python -m src.query add --company C --title T [--url U] [--status S] [--note ...]
                          [--applied-at YYYY-MM-DD] [--description ...]
                                        # hand-enter a role no board carries (outreach,
                                        # referral): reuses the row with the same
                                        # company+title if one exists (manual, then live
                                        # ATS, then aggregator; junk rows revive), else
                                        # inserts source='manual' as discovered;
                                        # status/note/applied-at apply on every call
"""
from __future__ import annotations

import argparse
import json
import sys

from .config import followup_days
from .db import ATS_SOURCES, STATUSES, _valid_date, connect, set_status as _set_status, touch_contact, upsert_job
from .dream import is_dream
from .models import Job, now_iso


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


JUNK = ("irrelevant", "expired")   # terminal triage/feed drops; a hand-added role revives them


def cmd_add(company: str, title: str, url: str | None = None, status: str | None = None,
            note: str | None = None, applied_at: str | None = None,
            description: str | None = None) -> None:
    """Hand-enter a role no board carries, or update the one already on file.

    Resolution: an existing row with the same canonical_key (company+title), in
    the order manual row, then live rows before irrelevant/expired ones, then
    ATS sources before aggregators (the canonical_jobs precedence), then lowest
    id. Otherwise inserts source='manual' as `discovered` so the matcher scores
    it. A matched irrelevant/expired row with no --status is revived to
    `discovered`. --status and --note apply on every call through set_status;
    --applied-at is stamped on the first flip to applied and, on a row that
    already carries a date, corrects it (the human-entered date wins). The
    application folder follows the status; the printed `status` is the row's
    real current status. On a manual row --url and --description overwrite;
    a board row's own url and description are never touched.
    """
    from .reconcile import sync_folder  # local import: keeps read-only paths light

    conn = connect()
    job = Job(source="manual", external_id="", url=url or "", company=company, title=title,
              description=description or "")
    row = job.to_row()
    # external_id = the canonical key itself: unique per role, so two company/title
    # splits that slug alike ("Arga Labs"/"Engineer" vs "Arga"/"Labs Engineer") can't collide.
    row["external_id"] = job.external_id = row["canonical_key"]
    ats = ", ".join("?" * len(ATS_SOURCES))
    existing = conn.execute(
        "SELECT id, source, status, url, description FROM jobs WHERE canonical_key=? "
        "ORDER BY CASE WHEN source='manual' THEN 0 ELSE 1 END, "
        f"CASE WHEN status IN (?, ?) THEN 1 ELSE 0 END, "
        f"CASE WHEN source IN ({ats}) THEN 0 ELSE 1 END, id",
        (row["canonical_key"], *JUNK, *ATS_SOURCES)).fetchone()
    if existing:
        job_id, source, current = existing["id"], existing["source"], existing["status"]
        outcome = "seen" if source == "manual" else "matched"
        if source == "manual":
            if url and url != existing["url"]:
                conn.execute("UPDATE jobs SET url=? WHERE id=?", (url, job_id))
            if description and description != existing["description"]:
                conn.execute("UPDATE jobs SET description=? WHERE id=?", (description, job_id))
        if current in JUNK and not status:
            status, outcome = "discovered", "revived"
    else:
        if upsert_job(conn, row, now_iso()) != "new":
            sys.exit(f"Refusing: a manual row with key {row['canonical_key']} already exists "
                     "but the canonical lookup missed it; inspect the DB.")
        job_id = conn.execute("SELECT id FROM jobs WHERE source='manual' AND external_id=?",
                              (job.external_id,)).fetchone()["id"]
        source, outcome, current = "manual", "new", "discovered"
        status = status or "discovered"

    try:
        if status or note:
            target = status or current
            _set_status(conn, job_id, target, note=note, applied_at=applied_at,
                        followup_days=followup_days())
            current = target
        if applied_at:
            # set_status only stamps an EMPTY applied_at; a human-entered date corrects
            # a row that already has one (folder-mtime backfills are guesses).
            conn.execute("UPDATE jobs SET applied_at=? WHERE id=? AND applied_at IS NOT NULL "
                         "AND applied_at!=?", (_valid_date(applied_at, "applied_at"), job_id, applied_at))
    except ValueError as e:
        conn.rollback()
        sys.exit(str(e))
    conn.commit()
    moved = sync_folder(int(job_id), current)
    out = {"id": job_id, "outcome": outcome, "source": source, "company": company,
           "title": title, "status": current}
    if moved:
        out["folder"] = moved
    print(json.dumps(out, indent=2))


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
    ad.add_argument("--status", choices=STATUSES,
                    help="apply this status (new rows default to discovered)")
    ad.add_argument("--note", help="appended to the job's notes")
    ad.add_argument("--applied-at", help="real application date YYYY-MM-DD (first flip to applied)")
    ad.add_argument("--description", help="role text for the matcher, since no board provides one")
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
        cmd_add(a.company, a.title, a.url, a.status, a.note, a.applied_at, a.description)
    else:
        cmd_touch(a.id, a.date, a.bump)
