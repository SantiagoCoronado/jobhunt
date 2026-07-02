"""SQLite = single source of truth for jobs + application status (the CRM backend).

One table, keyed by (source, external_id) so re-runs upsert instead of duplicating.
`status` turns the jobs table into a lightweight applicant tracker.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "jobs.db"

STATUSES = [
    "discovered", "shortlisted", "applied", "screen",
    "interview", "offer", "rejected", "ghosted", "withdrawn",
]

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


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
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
