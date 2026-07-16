"""Keep applications/ folders and DB statuses agreeing (both directions).

  python -m src.reconcile           # show the drift, change nothing
  python -m src.reconcile --apply   # execute the proposed fixes

Filing convention (CLAUDE.md): applications/{pending,applied,other}/<company>-<id>/

Rules, in order:
1. A folder moved into applied/ is a human act recording a submission, so it wins
   over a pre-submission DB status: the row flips to 'applied' (applied_at = the
   folder's mtime date) and a follow-up comes due followup_days later.
2. When the DB status is AHEAD of the folder (pending < applied < other), the DB
   is canonical and the folder moves forward to match it.
3. When the FOLDER is ahead (e.g. filed in other/ but the DB still says
   shortlisted), a human recorded an outcome the DB never got. We can't guess
   WHICH outcome (rejected? ghosted? withdrawn?), so it's flagged for a manual
   `python -m src.query set-status`, never moved back.
4. Folders with no -<id> suffix, ids with no DB row, and ids appearing in more
   than one bucket are reported and never touched.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sqlite3
from datetime import date, datetime
from pathlib import Path

from .config import ROOT, followup_days
from .db import connect, set_status

APPS_DIR = ROOT / "applications"
BUCKETS = ("pending", "applied", "other")
BUCKET_ORDER = {"pending": 0, "applied": 1, "other": 2}

# Which bucket a job's folder belongs in, per DB status.
STATUS_BUCKET = {
    "discovered": "pending", "shortlisted": "pending", "backlog": "pending",
    "applied": "applied", "screen": "applied", "interview": "applied", "offer": "applied",
    "rejected": "other", "ghosted": "other", "withdrawn": "other", "irrelevant": "other",
}
# Statuses a folder-in-applied/ is allowed to override (rule 1).
PRE_SUBMISSION = {"discovered", "shortlisted", "backlog"}

_ID_RE = re.compile(r"-(\d+)$")


def folder_job_id(name: str) -> int | None:
    m = _ID_RE.search(name)
    return int(m.group(1)) if m else None


def scan(apps_dir: Path = APPS_DIR) -> list[tuple[str, Path]]:
    """All application folders as (bucket, path)."""
    out = []
    for bucket in BUCKETS:
        d = apps_dir / bucket
        if d.is_dir():
            out.extend((bucket, p) for p in sorted(d.iterdir()) if p.is_dir())
    return out


def find_folder(job_id: int, apps_dir: Path = APPS_DIR) -> tuple[str, Path] | None:
    for bucket, path in scan(apps_dir):
        if folder_job_id(path.name) == job_id:
            return bucket, path
    return None


def sync_folder(job_id: int, status: str, apps_dir: Path = APPS_DIR) -> str | None:
    """Move a job's folder to the bucket its status expects. Returns a
    description of the move, or None if there was nothing to do."""
    expected = STATUS_BUCKET.get(status)
    found = find_folder(job_id, apps_dir)
    if not expected or not found or found[0] == expected:
        return None
    bucket, path = found
    dest = apps_dir / expected / path.name
    if dest.exists():
        return f"CONFLICT: {dest} already exists, left {path} in {bucket}/"
    # Callers invoke this after the DB commit, so a filesystem hiccup must not
    # blow up the transition; the next `reconcile --apply` will retry the move.
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(dest))
    except OSError as e:
        return f"ERROR: could not move {path.name} to {expected}/ ({e}); run reconcile --apply to retry"
    return f"moved {path.name}: {bucket}/ -> {expected}/"


def plan(conn: sqlite3.Connection, apps_dir: Path = APPS_DIR) -> dict:
    """Compute the drift diff without changing anything."""
    folders = scan(apps_dir)
    by_id: dict[int, list[tuple[str, Path]]] = {}
    unmatched: list[str] = []
    for bucket, path in folders:
        jid = folder_job_id(path.name)
        if jid is None:
            unmatched.append(f"{bucket}/{path.name}: no -<id> suffix, map manually")
        else:
            by_id.setdefault(jid, []).append((bucket, path))

    db_updates: list[dict] = []
    folder_moves: list[dict] = []

    for jid, entries in sorted(by_id.items()):
        if len(entries) > 1:
            spots = ", ".join(f"{b}/{p.name}" for b, p in entries)
            unmatched.append(f"id {jid} in multiple buckets ({spots}): resolve manually")
            continue
        bucket, path = entries[0]
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone()
        if not row:
            unmatched.append(f"{bucket}/{path.name}: no DB row with id {jid}")
            continue

        status = row["status"]
        # Rule 1: folder in applied/ + pre-submission DB status -> flip the row.
        if bucket == "applied" and status in PRE_SUBMISSION:
            # mtime is a best-guess submission date: it moves if a file is added
            # to the folder later. Good enough for a one-shot backfill; live
            # transitions should go through `query set-status`, which uses today.
            applied_at = datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()
            db_updates.append({
                "id": jid, "company": row["company"], "title": row["title"],
                "old_status": status, "new_status": "applied", "applied_at": applied_at,
            })
            status = "applied"  # simulate for rule 2 below

        # Rule 2: DB ahead of the folder -> the folder moves forward to match.
        # Rule 3: folder ahead of the DB -> a human recorded an outcome the DB
        # never got; we can't guess which, so flag it instead of moving back.
        expected = STATUS_BUCKET.get(status)
        if expected and bucket != expected:
            if BUCKET_ORDER[expected] > BUCKET_ORDER[bucket]:
                folder_moves.append({
                    "id": jid, "name": path.name, "from": bucket, "to": expected,
                    "status": status,
                })
            else:
                unmatched.append(
                    f"{bucket}/{path.name}: filed in {bucket}/ but DB status is "
                    f"'{status}'. Record the outcome: python -m src.query "
                    f"set-status {jid} rejected|ghosted|withdrawn"
                )

    return {"db_updates": db_updates, "folder_moves": folder_moves, "unmatched": unmatched}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="execute the proposed fixes")
    args = ap.parse_args()

    conn = connect()
    p = plan(conn, APPS_DIR)

    if not any(p.values()):
        print("No drift: folders and DB statuses agree.")
        return

    if p["db_updates"]:
        print(f"DB updates ({len(p['db_updates'])}), folder in applied/ wins over pre-submission status:")
        for u in p["db_updates"]:
            print(f"  #{u['id']} {u['company']} - {u['title']}: "
                  f"{u['old_status']} -> applied (applied_at={u['applied_at']})")
    if p["folder_moves"]:
        print(f"Folder moves ({len(p['folder_moves'])}), DB status is canonical:")
        for m in p["folder_moves"]:
            print(f"  {m['name']}: {m['from']}/ -> {m['to']}/ (status={m['status']})")
    if p["unmatched"]:
        print(f"Needs manual attention ({len(p['unmatched'])}):")
        for u in p["unmatched"]:
            print(f"  {u}")

    if not args.apply:
        print("\nDry run. Re-run with --apply to execute.")
        return

    days = followup_days()
    for u in p["db_updates"]:
        set_status(conn, u["id"], "applied", applied_at=u["applied_at"], followup_days=days)
    conn.commit()
    for m in p["folder_moves"]:
        note = sync_folder(m["id"], m["status"], APPS_DIR)
        if note:
            print(note)
    print(f"\nApplied: {len(p['db_updates'])} DB updates, {len(p['folder_moves'])} folder moves.")


if __name__ == "__main__":
    main()
