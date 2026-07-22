"""Pull the Notion "Job Hunt" mirror back into the local DB.

This is the reverse half of /jh-notion-sync: statuses, applied dates, and
follow-up dates edited in Notion (usually from the phone) flow back into
SQLite. Claude exports the Notion rows to JSON via MCP; this script does the
deterministic matching and diffing, so no LLM judgment touches the CRM.

  python -m src.notion_pull <rows.json>                    # diff only
  python -m src.notion_pull <rows.json> --apply            # execute
  python -m src.notion_pull <rows.json> --apply --create-missing
                                                           # also insert Notion rows
                                                           # with no DB match (source='manual')

Input: JSON array, one object per Notion row:
  {"company": ..., "role": ..., "status": ..., "applied": "YYYY-MM-DD"|null,
   "followup": "YYYY-MM-DD"|null, "notes": ...|null, "link": ...|null}

Rules:
- A row matches a DB job by URL first (scheme/query-insensitive), then by
  normalized company+title.
- Notion statuses map to the DB vocabulary: declined -> withdrawn (chose not
  to / could not apply), "Not Found" -> withdrawn (posting gone).
- A Notion status applies only if it advances the pipeline or is terminal.
  Downgrades (Notion 'shortlisted' vs DB 'applied') are reported, never
  applied; DB 'backlog' is a deliberate hold that Notion 'shortlisted' can't
  overwrite.
- Notion's explicit Applied date corrects the DB applied_at (local backfills
  are folder-mtime guesses; the human-entered date wins).
- Notion's Follow-up date wins over the DB next_followup_at.
- Notion Notes are copied (prefixed '[notion]') only when DB notes are empty.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

from .config import followup_days
from .db import connect, log_event, set_status, upsert_job
from .models import Job, normalize_text, now_iso
from .reconcile import sync_folder

NOTION_TO_DB = {
    "discovered": "discovered", "shortlisted": "shortlisted", "applied": "applied",
    "screen": "screen", "interview": "interview", "offer": "offer",
    "rejected": "rejected", "ghosted": "ghosted",
    "declined": "withdrawn",   # user declined / could not apply
    "Not Found": "withdrawn",  # posting no longer available
}
RANK = {"discovered": 0, "shortlisted": 1, "applied": 2, "screen": 3,
        "interview": 4, "offer": 5}
TERMINAL = {"rejected", "ghosted", "withdrawn"}

_URL_NOISE = re.compile(r"^https?://(www\.)?")
_TRACKING_PARAMS = ("utm", "se=", "v=", "ref=", "source=", "gh_src=")


def url_key(url: str | None) -> str | None:
    """Scheme-, www-, tracking-param-, and trailing-slash-insensitive URL identity.

    Identifying query params are KEPT: for Hacker News every posting shares the
    /item path and only ?id= distinguishes them, so stripping the whole query
    would collapse all HN jobs into one key."""
    if not url:
        return None
    u = _URL_NOISE.sub("", url).lower()
    path, _, query = u.partition("?")
    keep = sorted(p for p in query.split("&")
                  if p and not p.startswith(_TRACKING_PARAMS))
    path = path.rstrip("/")
    return f"{path}?{'&'.join(keep)}" if keep else path


def ct_key(company: str | None, title: str | None) -> str:
    return f"{normalize_text(company)}|{normalize_text(title)}"


def match_job(row: dict, by_url: dict, by_ct: dict) -> sqlite3.Row | None:
    return by_url.get(url_key(row.get("link"))) or by_ct.get(ct_key(row.get("company"), row.get("role")))


def plan(conn: sqlite3.Connection, rows: list[dict]) -> dict:
    jobs = conn.execute(
        "SELECT id,url,company,title,status,applied_at,next_followup_at,notes FROM jobs"
    ).fetchall()
    by_url = {k: j for j in jobs if (k := url_key(j["url"]))}
    by_ct = {ct_key(j["company"], j["title"]): j for j in jobs}

    changes: list[dict] = []
    skipped: list[str] = []
    unmatched: list[dict] = []

    for row in rows:
        if not row.get("company") and not row.get("link"):
            continue  # empty Notion row
        notion_status = row.get("status")
        target = NOTION_TO_DB.get(notion_status) if notion_status else None
        job = match_job(row, by_url, by_ct)
        if job is None:
            unmatched.append(row)
            continue

        c: dict = {"id": job["id"], "company": job["company"], "title": job["title"]}
        db_status = job["status"]
        if target and target != db_status:
            advances = target in TERMINAL or RANK.get(target, -1) > RANK.get(db_status, 99)
            if db_status == "backlog" and target not in TERMINAL:
                skipped.append(f"#{job['id']} {job['company']}: kept 'backlog' (deliberate hold) over Notion '{notion_status}'")
            elif advances:
                c["status"] = target
                if notion_status != target:
                    c["status_note"] = f"[notion] status was '{notion_status}'"
            else:
                skipped.append(f"#{job['id']} {job['company']}: Notion '{notion_status}' would downgrade DB '{db_status}', kept DB")

        applied = row.get("applied")
        if applied and applied != job["applied_at"]:
            c["applied_at"] = applied
        followup = row.get("followup")
        if followup and followup != job["next_followup_at"]:
            c["next_followup_at"] = followup
        notes = row.get("notes")
        if notes and not job["notes"]:
            c["notes"] = f"[notion] {notes}"

        if len(c) > 3:
            changes.append(c)

    return {"changes": changes, "skipped": skipped, "unmatched": unmatched}


def apply_changes(conn: sqlite3.Connection, p: dict, create_missing: bool = False) -> list[str]:
    log: list[str] = []
    days = followup_days()

    for c in p["changes"]:
        if "status" in c:
            set_status(conn, c["id"], c["status"],
                       note=c.get("status_note"),
                       next_followup=c.get("next_followup_at"),
                       followup_days=days)
        elif "next_followup_at" in c:
            conn.execute("UPDATE jobs SET next_followup_at=? WHERE id=?",
                         (c["next_followup_at"], c["id"]))
        if "applied_at" in c:
            conn.execute("UPDATE jobs SET applied_at=? WHERE id=?",
                         (c["applied_at"], c["id"]))
            # keep the event log aware of the correction; latency() reads events
            log_event(conn, c["id"], "note",
                      {"applied_at_corrected": c["applied_at"], "source": "notion"})
        if "notes" in c and "status" not in c:
            conn.execute("UPDATE jobs SET notes=COALESCE(notes,?) WHERE id=?",
                         (c["notes"], c["id"]))
    conn.commit()

    for c in p["changes"]:
        if "status" in c:
            moved = sync_folder(c["id"], c["status"])
            if moved:
                log.append(moved)

    if create_missing:
        for row in p["unmatched"]:
            if not row.get("company"):
                continue
            job = Job(source="manual",
                      external_id=normalize_text(f"{row.get('company')} {row.get('role')}").replace(" ", "-"),
                      url=row.get("link") or "", company=row["company"], title=row.get("role") or "")
            upsert_job(conn, job.to_row(), now_iso())
            new_id = conn.execute("SELECT id FROM jobs WHERE source='manual' AND external_id=?",
                                  (job.external_id,)).fetchone()["id"]
            target = NOTION_TO_DB.get(row.get("status") or "", "shortlisted")
            set_status(conn, new_id, target,
                       note=f"[notion] {row['notes']}" if row.get("notes") else None,
                       next_followup=row.get("followup"), followup_days=days)
            if row.get("applied"):
                conn.execute("UPDATE jobs SET applied_at=? WHERE id=?", (row["applied"], new_id))
            log.append(f"created #{new_id} {row['company']} - {row.get('role')} ({target})")
        conn.commit()
    return log


def main() -> None:
    ap = argparse.ArgumentParser(description="Pull Notion statuses back into the local DB")
    ap.add_argument("rows_json", help="JSON array exported from the Notion data source")
    ap.add_argument("--apply", action="store_true", help="execute the proposed changes")
    ap.add_argument("--create-missing", action="store_true",
                    help="insert Notion rows that have no DB match (source='manual')")
    args = ap.parse_args()

    rows = json.loads(Path(args.rows_json).read_text())
    conn = connect()
    p = plan(conn, rows)

    if p["changes"]:
        print(f"Changes ({len(p['changes'])}):")
        for c in p["changes"]:
            fields = {k: v for k, v in c.items() if k not in ("id", "company", "title", "status_note")}
            print(f"  #{c['id']} {c['company']} - {c['title']}: {fields}")
    if p["skipped"]:
        print(f"Kept DB state ({len(p['skipped'])}):")
        for s in p["skipped"]:
            print(f"  {s}")
    if p["unmatched"]:
        print(f"No DB match ({len(p['unmatched'])}){'' if args.create_missing else ' (use --create-missing to insert)'}:")
        for r in p["unmatched"]:
            print(f"  {r.get('company')} - {r.get('role')} [{r.get('status')}]")
    if not p["changes"] and not p["unmatched"]:
        print("Notion and DB agree.")

    if not args.apply:
        print("\nDry run. Re-run with --apply to execute.")
        return

    for line in apply_changes(conn, p, create_missing=args.create_missing):
        print(line)
    print(f"\nApplied {len(p['changes'])} changes.")


if __name__ == "__main__":
    main()
