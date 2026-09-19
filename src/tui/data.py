"""The ONLY TUI module that opens SQLite (spec decision 1): pure functions returning dataclasses.

All synchronous, called from Textual workers. Each call opens its own connection, because a
sqlite3 connection belongs to the thread that made it and workers run on a pool.
"""
from __future__ import annotations

import html
import json
import re
import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from .. import config, db, dream, pick, reconcile, research
from .presets import ALL, COLD, HOT, PRESETS, Sort

ALL_CAP = 500        # discovered rows shown under `all` (~15k exist); search narrows, never scroll
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


_READY: set[Path] = set()
_READY_LOCK = threading.Lock()


def _ensure_schema(path: Path) -> None:
    """`db.connect` creates the schema, runs migrations and switches the file to WAL. Those are
    writes, and the screen starts several workers at once: on a fresh DB they raced each other
    into "database is locked" (the WAL switch does not wait on busy_timeout). Once per process
    and path, under a lock; every later connection is a plain one."""
    with _READY_LOCK:
        if path not in _READY:
            db.connect(path).close()
            _READY.add(path)


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    # db.DB_PATH is read at call time so a test (or a future --db flag) can point it elsewhere.
    path = db.DB_PATH
    _ensure_schema(path)
    conn = sqlite3.connect(path, timeout=5.0)
    conn.row_factory = sqlite3.Row
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


def rows(preset: str = "board", status: str | None = None, query: str = "",
         sort: Sort | None = None) -> list[JobRow]:
    """Rows for the jobs table. `status` is the left-pane pick: a hot status, `all`, or None
    for the preset's own statuses. Never `irrelevant`/`expired`. `query` matches title,
    company and notes inside that filter. `sort` replaces the preset's own order.

    `all` is how `discovered` is reached, and its left-pane number is the discovered count,
    so the cold rows come FIRST and ALL_CAP limits only them; the hot rows follow, uncapped
    (there are hundreds, not thousands). One score-sorted list under one cap would be 500
    scored hot rows and not a single discovered one. A `sort` orders each half on its own."""
    p = PRESETS[preset]
    order_by = sort.order_by if sort else p.order_by
    if status is not None and status != ALL and status not in HOT:
        raise ValueError(f"{status!r} is not a status the TUI shows")

    q = query.strip()
    fields = ["title", "company", "notes"]
    if status == ALL and q.lower().startswith(DESC_PREFIX):
        q = q[len(DESC_PREFIX):].strip()
        fields.append("description")
    match = "(" + " OR ".join(f"{f} LIKE ? ESCAPE '\\'" for f in fields) + ")" if q else ""
    match_args: list[object] = [_like(q)] * len(fields) if q else []

    def select(conn: sqlite3.Connection, statuses: tuple[str, ...], cap: int | None) -> list[JobRow]:
        where = f"status IN ({','.join('?' for _ in statuses)})" + (f" AND {match}" if match else "")
        sql = f"SELECT {_ROW_COLS} FROM jobs WHERE {where} ORDER BY {order_by}"
        if cap is not None:
            sql += f" LIMIT {int(cap)}"
        return [_job_row(r) for r in conn.execute(sql, [*statuses, *match_args])]

    with _conn() as conn:
        if status == ALL:
            return select(conn, COLD, ALL_CAP) + select(conn, HOT, None)
        return select(conn, (status,) if status else p.statuses, None)


def stars() -> set[int]:
    """The rows `src.pick` would choose right now (spec decision 11): computed on every load,
    never stored, so a star is gone the moment its row leaves `shortlisted` or its company
    goes into play. Same connection rules and the same applications tree as everything here."""
    with _conn() as conn:
        picks, _skipped, _spares = pick.pick(conn=conn, apps_dir=reconcile.APPS_DIR)
    return {p["id"] for p in picks}


def stars_first(found: list[JobRow], starred: set[int]) -> list[JobRow]:
    """Starred rows on top, each half in the order it came in."""
    return [r for r in found if r.id in starred] + [r for r in found if r.id not in starred]


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


_LI = re.compile(r"<li\b[^>]*>", re.IGNORECASE)
_BLOCK = re.compile(r"</?(p|div|br|li|ul|ol|h[1-6]|tr|section)\b[^>]*>", re.IGNORECASE)
_TAG = re.compile(r"<[^>]+>")


def plain_description(s: str | None) -> str:
    """A posting body as readable text: some sources store HTML, a few store it escaped
    (`&lt;p&gt;`), so unescape first, then turn block tags into line breaks and list items
    into `- ` lines. Unlike `models.strip_html` this keeps the paragraphs."""
    if not s:
        return ""
    if "&lt;" in s:
        s = html.unescape(s)
    s = _LI.sub("\n- ", s)
    s = _TAG.sub("", _BLOCK.sub("\n", s))
    lines = [" ".join(line.split()) for line in html.unescape(s).splitlines()]
    out: list[str] = []
    for line in lines:
        if line in ("", "-") and (not out or out[-1] == ""):
            continue
        out.append("" if line == "-" else line)
    # </li> and <li> each left a break; a list reads better without a gap between its items.
    tight = [line for i, line in enumerate(out)
             if line or not (0 < i < len(out) - 1
                             and out[i - 1].startswith("- ") and out[i + 1].startswith("- "))]
    return "\n".join(tight).strip()


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
        notes=r["notes"] or "", description=plain_description(r["description"]),
        verdict=parse_verdict(r["match_verdict"]), events=events,
        dossier=dossier if dossier and dossier.exists() else None,
        bucket=found[0] if found else None, folder=found[1] if found else None,
    )


# Writes. Each one goes through the same db function `python -m src.query` uses, so the events
# table and the folder moves cannot drift between the two front ends.

PIPELINE = ("applied", "screen", "interview", "offer")   # leaving one of these asks for a `y`


def needs_confirm(old: str, new: str) -> bool:
    return old in PIPELINE and new != old


def set_status(job_id: int, status: str, note: str | None = None,
               followup: str | None = None) -> str:
    """Status change + folder move, as `query set-status` does them. Returns one line for the
    toast; raises ValueError on a bad status, date or id."""
    if status not in HOT:
        raise ValueError(f"{status!r} is not a status the TUI sets")
    with _conn() as conn:
        changed = db.set_status(conn, job_id, status, note=note, next_followup=followup,
                                followup_days=config.followup_days())
        conn.commit()
    moved = reconcile.sync_folder(job_id, status, reconcile.APPS_DIR)
    line = f"#{job_id} {changed['company']}: {changed['old_status']} -> {status}"
    return f"{line} · {moved}" if moved else line


def set_status_many(job_ids: list[int], status: str) -> str:
    """The bulk verb: one `set_status` per row, so every row gets its own event and folder
    move. A row that fails does not stop the rest; the line counts both. CONFLICT (a folder
    move that found the destination taken) is carried up for the toast."""
    done, failed, conflicts = 0, [], 0
    for job_id in job_ids:
        try:
            conflicts += "CONFLICT" in set_status(job_id, status)
            done += 1
        except ValueError as e:
            failed.append(f"#{job_id}: {e}")
    line = f"{done} job{'' if done == 1 else 's'} -> {status}"
    if conflicts:
        line += f" · {conflicts} folder CONFLICT, run reconcile"
    return f"{line} · ERROR {'; '.join(failed)}" if failed else line


def _current_status(conn: sqlite3.Connection, job_id: int) -> str:
    r = conn.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
    if r is None:
        raise ValueError(f"No job with id {job_id}")
    return r["status"]


def notes(job_id: int) -> str:
    """The whole notes field, for the editor (the table rows do not carry it)."""
    with _conn() as conn:
        r = conn.execute("SELECT notes FROM jobs WHERE id=?", (job_id,)).fetchone()
    return (r["notes"] or "") if r else ""


NOTE_EVENT_CHARS = 200


def set_notes(job_id: int, text: str) -> str:
    """Replace the notes field (`db.set_status(notes=...)`, the status untouched). The field
    keeps only the latest text, so the edit also lands in the events log."""
    text = text.strip()
    with _conn() as conn:
        db.set_status(conn, job_id, _current_status(conn, job_id), notes=text)
        shown = text if len(text) <= NOTE_EVENT_CHARS else text[:NOTE_EVENT_CHARS - 1] + "…"
        db.log_event(conn, job_id, "note", {"note": shown or "notes cleared", "edit": True})
        conn.commit()
    return f"#{job_id} notes saved" if text else f"#{job_id} notes cleared"


def parse_followup(text: str, today: date) -> str:
    """`YYYY-MM-DD`, `+N` (days from today), `t` (today); empty or `-` clears (returns "")."""
    text = text.strip().lower()
    if text in ("", "-"):
        return ""
    if text == "t":
        return today.isoformat()
    if text.startswith("+"):
        if not text[1:].isdigit():
            raise ValueError(f"+N needs a whole number of days, got {text!r}")
        return (today + timedelta(days=int(text[1:]))).isoformat()
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise ValueError(f"use YYYY-MM-DD, +N or t, got {text!r}") from None


def set_followup(job_id: int, when: str) -> str:
    """`when` is an ISO date, or "" to clear (what `parse_followup` returns)."""
    with _conn() as conn:
        db.set_status(conn, job_id, _current_status(conn, job_id), next_followup=when)
        conn.commit()
    return f"#{job_id} follow-up {when}" if when else f"#{job_id} follow-up cleared"


def touch(job_id: int, bump: bool = False) -> str:
    """Contact today; with `bump` the follow-up moves `config.followup_days()` out, as
    `query touch --bump` does."""
    with _conn() as conn:
        changed = db.touch_contact(conn, job_id,
                                   bump_days=config.followup_days() if bump else None)
        conn.commit()
    line = f"#{job_id} {changed['company']}: contact {changed['last_contact_at']}"
    return f"{line} · follow-up {changed['next_followup_at']}" if bump else line
