"""The ONLY TUI module that opens SQLite (spec decision 1): pure functions returning dataclasses.

All synchronous, called from Textual workers. Each call opens its own connection, because a
sqlite3 connection belongs to the thread that made it and workers run on a pool.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from .. import db, dream, reconcile, research
from .presets import ALL, COLD, HOT, NEVER, PRESETS

ALL_CAP = 500        # the `all` view holds ~15k discovered rows; search narrows it, never scroll
EVENTS_SHOWN = 5
DESC_PREFIX = "d:"   # in the `all` view, `d:kafka` also searches descriptions (spec decision 18)

_ROW_COLS = ("id, company, title, location, source, status, match_score, "
             "applied_at, next_followup_at")


@dataclass(frozen=True)
class JobRow:
    id: int
    company: str
    title: str
    location: str
    source: str
    status: str
    score: int | None
    applied_at: str | None
    followup: str | None
    dream: bool


@dataclass(frozen=True)
class Verdict:
    """`match_verdict` parsed. A triage keeper holds {"triage", "reason", "bucket"} there until
    real scoring overwrites it, so every field is optional."""
    recommendation: str = ""
    reasons: str = ""
    strengths: tuple[str, ...] = ()
    missing_skills: tuple[str, ...] = ()
    bucket: int | None = None      # triage fit bucket 0-3, only before the matcher has run
    raw: str = ""                  # set only when the blob is not the JSON we expect

    @property
    def empty(self) -> bool:
        return self == Verdict()


@dataclass(frozen=True)
class Event:
    ts: str
    kind: str
    payload: dict


@dataclass(frozen=True)
class JobDetail:
    row: JobRow
    url: str
    remote: bool
    salary_min: int | None
    salary_max: int | None
    currency: str
    posted_at: str | None
    first_seen: str | None
    last_contact_at: str | None
    notes: str
    description: str
    verdict: Verdict
    events: list[Event] = field(default_factory=list)   # newest first, at most EVENTS_SHOWN
    dossier: Path | None = None                          # only when the file exists
    bucket: str | None = None                            # pending | applied | other
    folder: Path | None = None


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    # db.DB_PATH is read at call time so a test (or a future --db flag) can point it elsewhere.
    conn = db.connect(db.DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def db_mtime() -> float:
    """Newest mtime of the DB and its WAL. Under journal_mode=WAL a commit lands in
    `jobs.db-wal` and the main file only moves at a checkpoint, so polling the main file
    alone would miss a hunt writing in another pane. 0.0 when there is no DB yet."""
    newest = 0.0
    for p in (db.DB_PATH, db.DB_PATH.with_name(db.DB_PATH.name + "-wal")):
        try:
            newest = max(newest, p.stat().st_mtime)
        except OSError:
            pass
    return newest


def counts() -> dict[str, int]:
    """Hot statuses in `db.STATUSES` order (zeros included), then `all` = the discovered count."""
    with _conn() as conn:
        got = dict(conn.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status").fetchall())
    out = {s: got.get(s, 0) for s in HOT}
    out[ALL] = sum(got.get(s, 0) for s in COLD)
    return out


def _job_row(r: sqlite3.Row) -> JobRow:
    return JobRow(
        id=r["id"], company=r["company"] or "", title=r["title"] or "",
        location=r["location"] or "", source=r["source"] or "", status=r["status"] or "",
        score=r["match_score"], applied_at=r["applied_at"], followup=r["next_followup_at"],
        dream=dream.is_dream(r["company"]),
    )


def _like(term: str) -> str:
    esc = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{esc}%"


def rows(preset: str = "board", status: str | None = None, query: str = "") -> list[JobRow]:
    """Rows for the jobs table. `status` is the left-pane pick: a hot status, `all`, or None
    for the preset's own statuses. Never `irrelevant`/`expired`; `discovered` only under `all`,
    which is capped at ALL_CAP. `query` matches title, company and notes inside that filter."""
    p = PRESETS[preset]
    where: list[str] = []
    args: list[object] = []
    if status == ALL:
        where.append(f"status NOT IN ({','.join('?' for _ in NEVER)})")
        args += NEVER
    else:
        if status is not None and status not in HOT:
            raise ValueError(f"{status!r} is not a status the TUI shows")
        wanted = (status,) if status else p.statuses
        where.append(f"status IN ({','.join('?' for _ in wanted)})")
        args += wanted

    q = query.strip()
    fields = ["title", "company", "notes"]
    if status == ALL and q.lower().startswith(DESC_PREFIX):
        q = q[len(DESC_PREFIX):].strip()
        fields.append("description")
    if q:
        where.append("(" + " OR ".join(f"{f} LIKE ? ESCAPE '\\'" for f in fields) + ")")
        args += [_like(q)] * len(fields)

    sql = f"SELECT {_ROW_COLS} FROM jobs WHERE {' AND '.join(where)} ORDER BY {p.order_by}"
    if status == ALL:
        sql += f" LIMIT {ALL_CAP}"
    with _conn() as conn:
        return [_job_row(r) for r in conn.execute(sql, args)]


def _strs(v: object) -> tuple[str, ...]:
    if isinstance(v, str):
        return (v,) if v else ()
    if isinstance(v, list):
        return tuple(str(x) for x in v if x)
    return ()


def parse_verdict(blob: str | None) -> Verdict:
    if not blob:
        return Verdict()
    try:
        d = json.loads(blob)
    except ValueError:
        return Verdict(raw=blob)
    if not isinstance(d, dict):
        return Verdict(raw=blob)
    if "triage" in d:
        bucket = d.get("bucket")
        return Verdict(recommendation=f"triage {d['triage']}", reasons=str(d.get("reason") or ""),
                       bucket=bucket if isinstance(bucket, int) else None)
    return Verdict(
        recommendation=str(d.get("recommendation") or ""),
        reasons=str(d.get("reasons") or ""),
        strengths=_strs(d.get("strengths")),
        missing_skills=_strs(d.get("missing_skills")),
    )


def _payload(blob: str | None) -> dict:
    try:
        d = json.loads(blob) if blob else {}
    except ValueError:
        return {"raw": blob}
    return d if isinstance(d, dict) else {"raw": blob}


def detail(job_id: int) -> JobDetail | None:
    """Everything the detail pane draws. None when the id is gone (expired mid-session)."""
    with _conn() as conn:
        r = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if r is None:
            return None
        events = [Event(e["ts"], e["kind"], _payload(e["payload"])) for e in conn.execute(
            "SELECT ts, kind, payload FROM events WHERE job_id=? ORDER BY id DESC LIMIT ?",
            (job_id, EVENTS_SHOWN))]
    dossier = research.dossier_path(r["company"]) if r["company"] else None
    # reconcile.APPS_DIR is passed at call time for the same reason db.DB_PATH is.
    found = reconcile.find_folder(job_id, reconcile.APPS_DIR)
    return JobDetail(
        row=_job_row(r), url=r["url"] or "", remote=bool(r["remote"]),
        salary_min=r["salary_min"], salary_max=r["salary_max"], currency=r["currency"] or "",
        posted_at=r["posted_at"], first_seen=r["first_seen"], last_contact_at=r["last_contact_at"],
        notes=r["notes"] or "", description=r["description"] or "",
        verdict=parse_verdict(r["match_verdict"]), events=events,
        dossier=dossier if dossier and dossier.exists() else None,
        bucket=found[0] if found else None, folder=found[1] if found else None,
    )
