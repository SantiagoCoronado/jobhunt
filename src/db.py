"""SQLite = single source of truth for jobs + application status (the CRM backend).

One table, keyed by (source, external_id) so re-runs upsert instead of duplicating.
`status` turns the jobs table into a lightweight applicant tracker.
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "jobs.db"

STATUSES = [
    "discovered", "shortlisted", "applied", "screen",
    "interview", "offer", "rejected", "ghosted", "withdrawn",
    "irrelevant",   # coarse Haiku triage drop (off-field / dealbreaker); excluded from match
    "backlog",      # deliberately deferred (e.g. apply later); skipped by shortlist/star/tailor
    "expired",      # dropped out of its source's feed while still 'discovered'; posting likely gone
]

# Direct ATS boards carry the authoritative posting (full JD, working apply URL);
# aggregators re-syndicate. The canonical_jobs view prefers ATS rows for a role.
ATS_SOURCES = (
    "greenhouse", "lever", "ashby", "workable", "recruitee",
    "smartrecruiters", "personio", "bamboohr", "workday", "softserve",
    "teamtailor",   # added 2026-09-01 (migration 4 rebuilt the view for it)
    "pinpoint", "rippling", "secretlab",   # added 2026-09-01 (migration 5)
)

# The canonical_jobs view body. Migration 2 created it; any later migration that
# changes ATS_SOURCES or ALTERs the jobs table must DROP and re-CREATE it with
# this same string (SQLite expands `SELECT *` at CREATE VIEW time).
_CANONICAL_VIEW = f"""
    CREATE VIEW IF NOT EXISTS canonical_jobs AS
    SELECT * FROM (
        SELECT jobs.*, ROW_NUMBER() OVER (
            PARTITION BY canonical_key
            ORDER BY CASE WHEN source IN ({", ".join(f"'{s}'" for s in ATS_SOURCES)})
                     THEN 0 ELSE 1 END, id
        ) AS canonical_rank
        FROM jobs
    ) WHERE canonical_rank = 1;
"""

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    source         TEXT NOT NULL,
    external_id    TEXT NOT NULL,
    canonical_key  TEXT NOT NULL,
    url            TEXT,
    company        TEXT,
    title          TEXT,
    location       TEXT,
    remote         INTEGER DEFAULT 0,
    description    TEXT,
    salary_min     INTEGER,
    salary_max     INTEGER,
    currency       TEXT,
    posted_at      TEXT,
    tags           TEXT,
    -- pipeline / matching
    match_score    INTEGER,            -- 0-100, set by matcher
    match_verdict  TEXT,               -- JSON blob from the LLM judge
    -- application tracking (the CRM columns)
    status         TEXT DEFAULT 'discovered',
    applied_at     TEXT,
    last_contact_at TEXT,
    next_followup_at TEXT,
    notes          TEXT,
    -- bookkeeping
    first_seen     TEXT,
    last_seen      TEXT,
    notified       INTEGER DEFAULT 0,
    UNIQUE(source, external_id)
);
CREATE INDEX IF NOT EXISTS idx_canonical ON jobs(canonical_key);
CREATE INDEX IF NOT EXISTS idx_status    ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_score     ON jobs(match_score);
"""

# Numbered, append-only migrations applied via PRAGMA user_version. Each entry
# runs at most once per database; keep them idempotent anyway (IF NOT EXISTS)
# so a half-applied dev DB can't wedge. NEVER reorder or edit shipped entries.
MIGRATIONS: list[str] = [
    # 1: per-source fetch health, written by discover, read by the digest.
    #    A source whose recent runs all pulled 0 (or failed) is silently dead.
    """
    CREATE TABLE IF NOT EXISTS runs (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        ts      TEXT NOT NULL,
        source  TEXT NOT NULL,
        pulled  INTEGER NOT NULL DEFAULT 0,
        new     INTEGER NOT NULL DEFAULT 0,
        seen    INTEGER NOT NULL DEFAULT 0,
        ok      INTEGER NOT NULL DEFAULT 1,
        error   TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_runs_source ON runs(source, id);
    """,
    # 2: deterministic cross-source dedup. One representative row per
    #    canonical_key: ATS source beats aggregator, then lowest id. Replaces
    #    the non-deterministic bare `GROUP BY canonical_key` in match/triage.
    #    NOTE: SQLite expands `SELECT *` at CREATE VIEW time, so any future
    #    migration that ALTERs the jobs table MUST also DROP and recreate this view.
    _CANONICAL_VIEW,
    # 3: event log, the memory the intelligence layer runs on. `status` alone
    #    loses history (you can't compute applied -> first-reply latency from
    #    one column). set_status/touch_contact write events automatically.
    #    The INSERT backfills a synthetic applied event from applied_at so
    #    funnel stats start with the existing pipeline.
    """
    CREATE TABLE IF NOT EXISTS events (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id  INTEGER NOT NULL,
        ts      TEXT NOT NULL,
        kind    TEXT NOT NULL,   -- status_change | contact | debrief | note
        payload TEXT             -- JSON detail
    );
    CREATE INDEX IF NOT EXISTS idx_events_job ON events(job_id, id);
    -- The NOT IN guard makes the backfill idempotent: executescript commits
    -- before the user_version bump, so a crash between the two would re-run
    -- this migration on the next connect and, unguarded, duplicate history.
    INSERT INTO events (job_id, ts, kind, payload)
        SELECT id, applied_at, 'status_change',
               '{"to": "applied", "backfill": true}'
        FROM jobs WHERE applied_at IS NOT NULL
        AND id NOT IN (SELECT job_id FROM events WHERE kind='status_change');
    """,
    # 4: rebuild canonical_jobs so the 2026-09-01 ATS addition (teamtailor) ranks
    #    ahead of aggregators. DROP + CREATE is idempotent.
    "DROP VIEW IF EXISTS canonical_jobs;" + _CANONICAL_VIEW,
    # 5: same rebuild for pinpoint / rippling / secretlab (dream-company boards).
    "DROP VIEW IF EXISTS canonical_jobs;" + _CANONICAL_VIEW,
]


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # One writer (a hunt in another pane) plus readers (the TUI polling every 2 s):
    # WAL lets reads proceed during a write, busy_timeout waits instead of raising
    # "database is locked" when two writers do collide. WAL is persistent per file.
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    for n, migration in enumerate(MIGRATIONS[version:], start=version + 1):
        conn.executescript(migration)
        conn.execute(f"PRAGMA user_version = {n}")
    return conn


def upsert_job(conn: sqlite3.Connection, row: dict, now: str) -> str:
    """Insert new job or refresh last_seen on an existing one.

    Returns 'new' or 'seen' so the caller can count fresh discoveries.
    """
    cur = conn.execute(
        "SELECT id FROM jobs WHERE source=? AND external_id=?",
        (row["source"], row["external_id"]),
    )
    existing = cur.fetchone()
    if existing:
        conn.execute("UPDATE jobs SET last_seen=? WHERE id=?", (now, existing["id"]))
        return "seen"

    cols = [
        "source", "external_id", "canonical_key", "url", "company", "title",
        "location", "remote", "description", "salary_min", "salary_max",
        "currency", "posted_at", "tags",
    ]
    placeholders = ",".join("?" for _ in cols) + ",?,?"
    conn.execute(
        f"INSERT INTO jobs ({','.join(cols)},first_seen,last_seen) VALUES ({placeholders})",
        [row.get(c) for c in cols] + [now, now],
    )
    return "new"


def _valid_date(s: str, field: str) -> str:
    try:
        return date.fromisoformat(s).isoformat()
    except ValueError:
        raise ValueError(f"{field} must be YYYY-MM-DD, got {s!r}") from None


def log_event(conn: sqlite3.Connection, job_id: int | str, kind: str,
              payload: dict | None = None) -> None:
    """Append to the event log (the history `status` alone can't hold).
    Caller commits, same contract as set_status."""
    import json
    from datetime import datetime, UTC
    conn.execute(
        "INSERT INTO events (job_id, ts, kind, payload) VALUES (?,?,?,?)",
        (job_id, datetime.now(UTC).isoformat(),
         kind, json.dumps(payload) if payload else None),
    )


def set_status(
    conn: sqlite3.Connection,
    job_id: int | str,
    status: str,
    *,
    note: str | None = None,
    notes: str | None = None,
    next_followup: str | None = None,
    applied_at: str | None = None,
    followup_days: int = 7,
) -> dict:
    """Single write path for status transitions (CLI + viewer both route here).

    - Validates status against STATUSES and dates against YYYY-MM-DD.
    - First flip to 'applied' stamps applied_at (today unless given) and, when no
      explicit follow-up is supplied, schedules next_followup_at = applied_at + followup_days.
    - `note` appends to existing notes; `notes` replaces them (viewer semantics).
    - Terminal statuses clear next_followup_at so closed roles drop out of /jh-followups.

    Returns a summary dict of what changed. Raises ValueError on bad input;
    caller commits.
    """
    if status not in STATUSES:
        raise ValueError(f"Unknown status {status!r}. Valid: {', '.join(STATUSES)}")
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        raise ValueError(f"No job with id {job_id}")

    sets: dict[str, object] = {"status": status}

    # next_followup: None = not provided, "" = clear, "YYYY-MM-DD" = set.
    # A terminal status clears it unless an explicit date is passed (an
    # intentional reminder, e.g. "rejected, reapply eligible in October").
    if status == "applied":
        if not row["applied_at"]:
            base = _valid_date(applied_at, "applied_at") if applied_at else date.today().isoformat()
            sets["applied_at"] = base
        else:
            # Re-apply (e.g. after rejected/ghosted): keep the original
            # applied_at but schedule the new follow-up from today.
            base = date.today().isoformat()
        if not next_followup and not row["next_followup_at"]:
            due = date.fromisoformat(base) + timedelta(days=followup_days)
            sets["next_followup_at"] = due.isoformat()

    if next_followup is not None and "next_followup_at" not in sets:
        sets["next_followup_at"] = _valid_date(next_followup, "next_followup") if next_followup else None
    elif status in ("rejected", "ghosted", "withdrawn", "irrelevant"):
        sets["next_followup_at"] = None

    if notes is not None:
        sets["notes"] = notes or None
    elif note:
        sets["notes"] = f"{row['notes']}\n{note}" if row["notes"] else note

    # Keys in `sets` MUST always be hardcoded column-name literals, never
    # derived from caller input; only the values are bound via placeholders.
    assign = ", ".join(f"{c}=?" for c in sets)
    conn.execute(f"UPDATE jobs SET {assign} WHERE id=?", [*sets.values(), row["id"]])
    if status != row["status"]:
        log_event(conn, row["id"], "status_change",
                  {"from": row["status"], "to": status})
    return {"id": row["id"], "company": row["company"], "title": row["title"],
            "old_status": row["status"], **sets}


def touch_contact(
    conn: sqlite3.Connection,
    job_id: int | str,
    *,
    contact_date: str | None = None,
    bump_days: int | None = None,
) -> dict:
    """Record contact with the company (reply seen / follow-up sent).

    Sets last_contact_at; with bump_days, pushes next_followup_at that many days out.
    """
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        raise ValueError(f"No job with id {job_id}")
    stamp = _valid_date(contact_date, "contact_date") if contact_date else date.today().isoformat()
    sets: dict[str, object] = {"last_contact_at": stamp}
    if bump_days is not None:
        sets["next_followup_at"] = (date.fromisoformat(stamp) + timedelta(days=bump_days)).isoformat()
    assign = ", ".join(f"{c}=?" for c in sets)
    conn.execute(f"UPDATE jobs SET {assign} WHERE id=?", [*sets.values(), row["id"]])
    log_event(conn, row["id"], "contact",
              {"date": stamp, "bumped": bump_days is not None})
    return {"id": row["id"], "company": row["company"], "old_status": row["status"], **sets}
