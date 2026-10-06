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
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from .. import config, db, dream, pick, reconcile, research
from ..hunt import config as hunt_config
from ..hunt import doctor as hunt_doctor
from ..hunt import harness as hunt_harness
from ..hunt import ledger as hunt_ledger
from . import commands, settings
from .presets import ALL, COLD, DREAM, HOT, PRESETS, Sort

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
    """Hot statuses in `db.STATUSES` order (zeros included), then `all` = the discovered count,
    then `dream` = the listed rows (hot or discovered) at a company on the dream list."""
    listed = (*HOT, *COLD)
    with _conn() as conn:
        got = dict(conn.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status").fetchall())
        by_company = conn.execute(
            f"SELECT company, COUNT(*) FROM jobs WHERE status IN ({','.join('?' for _ in listed)}) "
            "GROUP BY company", listed).fetchall() if dream.dream_companies() else []
    out = {s: got.get(s, 0) for s in HOT}
    out[ALL] = sum(got.get(s, 0) for s in COLD)
    out[DREAM] = sum(n for company, n in by_company if dream.is_dream(company))
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
    if status is not None and status not in (ALL, DREAM) and status not in HOT:
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
        if status == DREAM:
            return _dream_rows(conn, order_by, match, match_args)
        return select(conn, (status,) if status else p.statuses, None)


def _dream_rows(conn: sqlite3.Connection, order_by: str, match: str, match_args: list[object]) -> list[JobRow]:
    """The Dream tab: every listed row (hot or discovered) at a dream company, in one order.
    SQL narrows by a LIKE per alias (a superset: no word boundaries there), then `is_dream`
    keeps the rows the alias rules really match."""
    aliases = [a for d in dream.dream_companies() for a in d["match"]]
    if not aliases:
        return []
    listed = (*HOT, *COLD)
    where = (f"status IN ({','.join('?' for _ in listed)}) AND ("
             + " OR ".join("company LIKE ? ESCAPE '\\'" for _ in aliases) + ")"
             + (f" AND {match}" if match else ""))
    sql = f"SELECT {_ROW_COLS} FROM jobs WHERE {where} ORDER BY {order_by}"
    found = (_job_row(r) for r in conn.execute(sql, [*listed, *(_like(a) for a in aliases), *match_args]))
    return [r for r in found if r.dream]


@dataclass(frozen=True)
class DreamCompany:
    name: str
    match: tuple[str, ...]
    careers_url: str
    note: str


def dream_companies() -> list[DreamCompany]:
    """The dream list as the table holds it, by name."""
    with _conn() as conn:
        return [DreamCompany(d["name"], tuple(d["match"]), d["careers_url"], d["note"])
                for d in db.list_dream(conn)]


def dream_name(company: str) -> str:
    """The dream list's name for a company string ("" when it is not on the list)."""
    return dream.dream_name(company) or ""


def parse_dream(text: str) -> str:
    """The `a` prompt's line, `Name, alias, alias`, checked: a name is required. Returns it as typed."""
    if not text.split(",", 1)[0].strip():
        raise ValueError("type a company name, then any aliases after commas")
    return text.strip()


def add_dream(text: str) -> str:
    """Add `Name, alias, alias` to the dream list (db.add_dream) and drop src.dream's cache so
    the next load flags the rows. Raises ValueError for an empty or duplicate name."""
    name, *aliases = [part.strip() for part in parse_dream(text).split(",")]
    with _conn() as conn:
        row = db.add_dream(conn, name, [a for a in aliases if a])
        conn.commit()
    dream.reset_cache()
    return f"{row['name']} is on the dream list (matches {', '.join(row['match'])})"


def remove_dream(name: str) -> str:
    with _conn() as conn:
        gone = db.remove_dream(conn, name)
        conn.commit()
    dream.reset_cache()
    if not gone:
        raise ValueError(f"{name} is not on the dream list")
    return f"{name} is off the dream list"


def rows_by_id(ids: set[int] | frozenset[int]) -> list[JobRow]:
    """The marked rows that are still ones the TUI lists, whatever view is on screen: the app's
    selection outlives a filter, and a row that went `irrelevant` or `expired` leaves it."""
    if not ids:
        return []
    listed = (*HOT, *COLD)
    with _conn() as conn:
        sql = (f"SELECT {_ROW_COLS} FROM jobs WHERE id IN ({','.join('?' for _ in ids)}) "
               f"AND status IN ({','.join('?' for _ in listed)})")
        return [_job_row(r) for r in conn.execute(sql, [*sorted(ids), *listed])]


def picks() -> list[int]:
    """The rows `src.pick` would choose right now, in the order a hunt would take them (spec
    decision 11): computed on every load, never stored, so a pick is gone the moment its row
    leaves `shortlisted` or its company goes into play. Same connection rules and the same
    applications tree as everything here. The table shows them as a pre-selection."""
    with _conn() as conn:
        chosen, _skipped, _spares = pick.pick(conn=conn, apps_dir=reconcile.APPS_DIR)
    return [p["id"] for p in chosen]


def picks_first(found: list[JobRow], picked: set[int]) -> list[JobRow]:
    """The hunt's picks on top, each half in the order it came in."""
    return [r for r in found if r.id in picked] + [r for r in found if r.id not in picked]


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


# Applications (the apps section): every folder under applications/{pending,applied,other} joined to
# its DB row by the `-<id>` suffix.

APP_FILES = ("resume", "pdf", "letter", "answers")   # the order the files column lists them in


@dataclass(frozen=True)
class AppRow:
    bucket: str
    folder: Path
    job_id: int | None          # None: the folder name carries no -<id>
    company: str                # from the DB row; the folder name when there is none
    title: str
    status: str                 # "" when no DB row matches
    url: str
    files: tuple[str, ...]      # which of APP_FILES are there
    resume_pdf: Path | None
    build: str                  # "ok", "fail N" (N failures), "unreadable", or "" with no build.json
    drift: str                  # "" when folder and DB agree, else what `reconcile` would say


def _app_files(folder: Path, stem: str) -> tuple[tuple[str, ...], Path | None]:
    names = {p.name for p in folder.iterdir() if p.is_file()}
    # An earlier profile name leaves another stem behind (`reconcile` lists those): still a resume.
    yamls = sorted(n for n in names if n.endswith("Resume.yaml"))
    pdfs = sorted(n for n in names if n.endswith("Resume.pdf"))
    pdf = f"{stem}.pdf" if f"{stem}.pdf" in names else (pdfs[0] if pdfs else None)
    have = {"resume": bool(yamls), "pdf": pdf is not None,
            "letter": bool(names & {"CoverLetter.pdf", "CoverLetter.docx", "CoverLetter.md"}),
            "answers": "answers.md" in names}
    return tuple(k for k in APP_FILES if have[k]), folder / pdf if pdf else None


def _build_verdict(folder: Path) -> str:
    try:
        d = json.loads((folder / "build.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ""
    except (OSError, ValueError):
        return "unreadable"
    if not isinstance(d, dict):
        return "unreadable"
    failures = d.get("failures")
    return "ok" if d.get("ok") else f"fail {len(failures) if isinstance(failures, list) else '?'}"


def _drift(bucket: str, status: str) -> str:
    """The three rules of `reconcile.plan`, as one short line for the row they apply to."""
    if bucket == "applied" and status in reconcile.PRE_SUBMISSION:
        return f"DB still {status}: reconcile flips it to applied"
    expected = reconcile.STATUS_BUCKET.get(status)
    if not expected or expected == bucket:
        return ""
    if reconcile.BUCKET_ORDER[expected] > reconcile.BUCKET_ORDER[bucket]:
        return f"DB says {status}: reconcile moves it to {expected}/"
    return f"filed in {bucket}/ but DB says {status}: record the outcome"


def apps() -> list[AppRow]:
    """Pending first (those wait on a human click), then applied, then other; inside a
    bucket the folder touched last leads."""
    folders = reconcile.scan(reconcile.APPS_DIR)
    ids = [reconcile.folder_job_id(p.name) for _b, p in folders]
    seen: dict[int, list[str]] = {}
    for (bucket, _p), job_id in zip(folders, ids, strict=True):
        if job_id is not None:
            seen.setdefault(job_id, []).append(bucket)
    found: dict[int, sqlite3.Row] = {}
    if seen:
        with _conn() as conn:
            marks = ",".join("?" for _ in seen)
            found = {r["id"]: r for r in conn.execute(
                f"SELECT id, company, title, status, url FROM jobs WHERE id IN ({marks})", list(seen))}

    # Once per load, not once per folder: `resume_basename` parses profile.yaml each time it is
    # asked, and 155 folders made that 2 s of a 2 s load (measured 2026-09-20, PRA-119).
    stem = config.resume_basename()
    out: list[tuple[tuple[int, float, str], AppRow]] = []
    for (bucket, path), job_id in zip(folders, ids, strict=True):
        r = found.get(job_id) if job_id is not None else None
        if job_id is None:
            drift = "no -<id> suffix: map it by hand"
        elif r is None:
            drift = f"no DB row with id {job_id}"
        elif len(seen[job_id]) > 1:
            drift = "also in " + ", ".join(f"{b}/" for b in seen[job_id] if b != bucket) + ": resolve by hand"
        else:
            drift = _drift(bucket, r["status"] or "")
        try:
            files, pdf = _app_files(path, stem)
            build, mtime = _build_verdict(path), path.stat().st_mtime
        except OSError:
            continue    # moved between the scan and here (a status change, a hunt): the next load has it
        row = AppRow(bucket=bucket, folder=path, job_id=job_id,
                     company=(r["company"] or "") if r else path.name,
                     title=(r["title"] or "") if r else "", status=(r["status"] or "") if r else "",
                     url=(r["url"] or "") if r else "", files=files, resume_pdf=pdf,
                     build=build, drift=drift)
        out.append(((reconcile.BUCKET_ORDER[bucket], -mtime, path.name), row))
    return [row for _key, row in sorted(out, key=lambda pair: pair[0])]


@dataclass(frozen=True)
class ReconcilePlan:
    db_updates: int
    folder_moves: int
    unmatched: tuple[str, ...]      # what only a human can settle

    @property
    def fixes(self) -> int:
        return self.db_updates + self.folder_moves

    @property
    def line(self) -> str:
        if not self.fixes and not self.unmatched:
            return "reconcile: no drift, folders and DB statuses agree"
        parts = [f"{self.db_updates} DB update{'' if self.db_updates == 1 else 's'}",
                 f"{self.folder_moves} folder move{'' if self.folder_moves == 1 else 's'}"]
        if self.unmatched:
            parts.append(f"{len(self.unmatched)} by hand")
        return "reconcile: " + ", ".join(parts)


def _plan(conn: sqlite3.Connection) -> tuple[dict, ReconcilePlan]:
    p = reconcile.plan(conn, reconcile.APPS_DIR)
    return p, ReconcilePlan(len(p["db_updates"]), len(p["folder_moves"]), tuple(p["unmatched"]))


def reconcile_plan() -> ReconcilePlan:
    """`python -m src.reconcile` as a dry run."""
    with _conn() as conn:
        return _plan(conn)[1]


def reconcile_apply() -> str:
    """`python -m src.reconcile --apply`. The plan is computed again here, so what runs is
    the tree as it is now, not as it was when the question was asked."""
    with _conn() as conn:
        p, summary = _plan(conn)
        notes = reconcile.apply(conn, p, reconcile.APPS_DIR)
    bad = [n for n in notes if n.startswith(("CONFLICT", "ERROR"))]
    return " · ".join([summary.line.replace("reconcile:", "reconciled:"), *bad, *summary.unmatched])


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


# How a hunt runs: `config/hunt.toml` through `src.hunt.config` (spec decision 13). The settings
# modal's harness tab reads and writes here; what counts as a fit is never touched.

@dataclass(frozen=True)
class StageModel:
    stage: str
    harness: str               # the stage's own override, else the default
    model: str | None          # None: the harness default
    concurrency: int = 1       # the most harness processes the orchestrator runs at once for it


@dataclass(frozen=True)
class HarnessView:
    default: str = ""
    harnesses: tuple[str, ...] = ()        # shipped adapters plus the file's [harness.<name>] templates
    stages: tuple[StageModel, ...] = ()    # fanned stages only: a Python stage runs no model
    error: str = ""                        # hunt.toml does not load; nothing else is set
    global_concurrency: int = 8            # the cap over every stage's own number


def harness_view() -> HarnessView:
    try:
        cfg = hunt_config.load()
    except ValueError as e:
        return HarnessView(error=str(e))
    names = tuple(dict.fromkeys([*hunt_harness.SHIPPED, *sorted(cfg.harness_templates), cfg.harness]))
    stages = tuple(StageModel(s, cfg.harness_for(s), cfg.stage(s).model, cfg.stage(s).concurrency)
                   for s in hunt_config.STAGES if cfg.stage(s).fanned)
    return HarnessView(cfg.harness, names, stages, global_concurrency=cfg.global_concurrency)


@dataclass(frozen=True)
class ModelChoices:
    harness: str
    ids: tuple[str, ...]
    note: str                  # where the list came from, or why there is none
    open_ended: bool           # no live catalog: any full model id may be typed


def harness_models(harness: str) -> ModelChoices:
    """The harness's LIVE catalog, the list `hunt models` prints. Runs the harness CLI, so
    call it from a worker. A harness with no catalog (claude) gives its `--help` aliases."""
    try:
        h = hunt_harness.get(harness)
    except ValueError as e:
        return ModelChoices(harness, (), str(e), True)
    models, reason = hunt_doctor.catalog(h)
    if models is not None:
        return ModelChoices(harness, tuple(m.id for m in models), f"{len(models)} models in the {harness} catalog", False)
    aliases = tuple(h.aliases()) if hasattr(h, "aliases") else ()
    why = reason or f"{harness} has no model catalog"
    return ModelChoices(harness, aliases, f"{why}: aliases from --help, or type a full model id", True)


def set_harness(name: str) -> str:
    hunt_config.set_default_harness(name)
    return f"hunt.toml: harness.default = {name}"


def set_stage_model(stage: str, model: str | None) -> str:
    hunt_config.set_stage_model(stage, model)
    return f"hunt.toml: {stage} runs on {model or 'the harness default'}"


# The runner (spec decision 12): what can be run, what has run. The stage list is the `src.hunt`
# registry plus the full hunt and the two Python extras; a run is a ledger folder under
# `data/hunt/`. Nothing here starts a process: a stage carries its argv, the screen runs it.

def set_stage_concurrency(stage: str, n: int) -> str:
    hunt_config.set_stage_concurrency(stage, n)
    return f"{stage}: {n} parallel (config/hunt.toml)"


def set_global_concurrency(n: int) -> str:
    hunt_config.set_global_concurrency(n)
    return f"at most {n} harness processes at once, over every stage (config/hunt.toml)"


HUNT = "hunt"                                   # the whole loop, `python -m src.hunt run`
ON_SELECTION = ("research", "tailor")           # `--only` these needs picks: the selection is them
SLASH = {HUNT: "/jh-hunt", "discover": "/jh-discover", "triage": "/jh-triage", "match": "/jh-match",
         "inbox": "/jh-gmail-sync", "report": "/jh-report"}   # research and tailor need an id: `c` on a job


@dataclass(frozen=True)
class RunStage:
    name: str
    kind: str                      # hunt | python | fanned | extra
    argv: tuple[str, ...]
    note: str                      # what it is, or the model it runs on
    slash: str = ""                # the slash command that does the same inside an agent session

    @property
    def copy_text(self) -> str:
        """What `c` puts on the clipboard: the slash command, else the shell line."""
        return self.slash or commands.shell_line(self.argv)

    @property
    def takes_selection(self) -> bool:
        """Runs on the rows marked in the jobs sections (`hunt run --ids`), never on its own."""
        return self.name in ON_SELECTION

    def argv_for(self, job_ids: Sequence[int]) -> tuple[str, ...]:
        return (*self.argv, "--ids", ",".join(str(int(i)) for i in job_ids)) if self.takes_selection else self.argv


def stages() -> list[RunStage]:
    from ..hunt.stages import REGISTRY    # imports every stage module: only when the runner opens

    try:
        cfg = hunt_config.load()
    except ValueError:
        cfg = hunt_config.defaults()      # the harness tab names the error; the list still draws
    out = [RunStage(HUNT, "hunt", tuple(commands.hunt_argv("run")),
                    f"every stage, on {cfg.harness} · cap {cfg.global_concurrency} parallel", SLASH[HUNT])]
    for name, stage in REGISTRY.items():
        sc = cfg.stage(name)
        # `N parallel` is `concurrency` in hunt.toml, a setting (the harness tab edits it), not a
        # limit of the runner: the most harness processes the orchestrator fans out at once.
        note = f"{sc.model or 'harness default'} on {cfg.harness_for(name)} · {sc.concurrency} parallel" \
            if sc.fanned else "python, in process"
        out.append(RunStage(name, stage.kind, tuple(commands.hunt_argv("run", "--only", name)),
                            note, SLASH.get(name, "")))
    out.append(RunStage("reconcile", "extra", tuple(commands.module_argv("src.reconcile")),
                        "folders vs statuses, dry run"))
    out.append(RunStage("stats", "extra", tuple(commands.module_argv("src.stats", "funnel")),
                        "the conversion funnel"))
    return out


@dataclass(frozen=True)
class HuntRun:
    run_id: str
    state: str                     # pending | running | done | failed | unreadable
    started: str
    harness: str
    path: Path


def hunt_runs() -> list[HuntRun]:
    """Every ledger under data/hunt/, newest first; an unreadable one is listed, not hidden."""
    return [HuntRun(r.run_id, r.state, r.started or "", r.harness or "", r.path)
            for r in hunt_ledger.list_runs(hunt_ledger.HUNT_DIR)]


@dataclass(frozen=True)
class HuntUnit:
    stage: str
    id: str
    state: str
    attempts: int
    verdict: str
    log: Path | None               # logs/<stage>/<unit>.log, whether or not it exists yet


@dataclass(frozen=True)
class HuntStage:
    name: str
    state: str
    note: str
    summary: str                   # the scalar fields of the stage's summary, `k=v k=v`
    units: tuple[HuntUnit, ...]

    @property
    def progress(self) -> str:
        if not self.units:
            return ""
        done = sum(1 for u in self.units if u.state == "done")
        failed = sum(1 for u in self.units if u.state == "failed")
        return f"{done}/{len(self.units)}" + (f", {failed} failed" if failed else "")


@dataclass(frozen=True)
class HuntStatus:
    run_id: str
    state: str
    started: str = ""
    ended: str = ""
    harness: str = ""
    stages: tuple[HuntStage, ...] = ()
    tree: str = ""                 # what `hunt status` prints
    report_html: Path | None = None
    error: str = ""

    def units(self) -> list[HuntUnit]:
        return [u for s in self.stages for u in s.units]


def _scalars(summary: object) -> str:
    if not isinstance(summary, dict):
        return ""
    return " ".join(f"{k}={v}" for k, v in summary.items()
                    if isinstance(v, (int, float, str)) and not isinstance(v, bool))


def hunt_status(run: str = "latest") -> HuntStatus | None:
    """One run's ledger as the runner draws it. None when there is no such run."""
    path = hunt_ledger.resolve(run, hunt_ledger.HUNT_DIR)
    if path is None:
        return None
    try:
        state = hunt_ledger.load_state(path)
    except (FileNotFoundError, ValueError) as e:
        return HuntStatus(path.name, "unreadable", error=str(e))
    found = []
    for st in state.get("stages", []):
        name = str(st.get("name"))
        units = tuple(HuntUnit(name, str(u.get("id")), str(u.get("state", "pending")), int(u.get("attempts") or 0),
                               str(u.get("verdict") or ""), path / str(u["log"]) if u.get("log") else None)
                      for u in st.get("units") or [])
        found.append(HuntStage(name, str(st.get("state", "pending")), str(st.get("note") or ""),
                               _scalars(st.get("summary")), units))
    html_path = report_path()
    return HuntStatus(path.name, hunt_ledger.run_state(state), str(state.get("started") or ""),
                      str(state.get("ended") or ""), str(state.get("harness") or ""), tuple(found),
                      hunt_ledger.render_status(state, path), html_path if html_path.exists() else None)


def report_path() -> Path:
    """Where the report stage writes the dashboard. Asked at the moment of use: a status loaded
    before a run cannot know about the file that run wrote."""
    return db.DB_PATH.parent / "report.html"


TAIL_BYTES = 64_000


def tail(path: Path, max_bytes: int = TAIL_BYTES) -> str:
    """The end of a log file, cut at a line start. A log that is not there yet is empty."""
    try:
        with path.open("rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - max_bytes))
            blob = f.read()
    except OSError:
        return ""
    text = blob.decode("utf-8", errors="replace")
    return text.split("\n", 1)[-1] if size > max_bytes and "\n" in text else text


@dataclass(frozen=True)
class SourceRun:
    source: str
    ts: str
    pulled: int
    new: int
    seen: int
    ok: bool
    error: str


def source_runs() -> list[SourceRun]:
    """The last discover run of every source from the `runs` table, failures first, then by name."""
    with _conn() as conn:
        found = conn.execute(
            "SELECT source, ts, pulled, new, seen, ok, error FROM runs "
            "WHERE id IN (SELECT MAX(id) FROM runs GROUP BY source)").fetchall()
    out = [SourceRun(r["source"], r["ts"] or "", r["pulled"] or 0, r["new"] or 0, r["seen"] or 0,
                     bool(r["ok"]), r["error"] or "") for r in found]
    return sorted(out, key=lambda r: (r.ok, r.source))


# The config view (spec decision 13): read-only, with open-in-editor. No forms over YAML.

@dataclass(frozen=True)
class ConfigFile:
    name: str
    path: Path
    lexer: str                     # yaml | toml
    role: str                      # one line: what the file decides


def config_files() -> list[ConfigFile]:
    """Resolved on every call: the profile and the local sources are user files that tests
    (and one day a second profile) point somewhere else."""
    return [
        ConfigFile("profile.yaml", Path(config.USER_FILES["profile"]), "yaml", "what counts as a fit"),
        ConfigFile("sources.yaml", config.CONFIG_DIR / "sources.yaml", "yaml", "adapter mechanics, tracked"),
        ConfigFile("sources.local.yaml", Path(config.USER_FILES["sources_local"]), "yaml", "your targeting, git-ignored"),
        ConfigFile("hunt.toml", hunt_config.HUNT_TOML, "toml", "how a hunt runs (the harness tab edits it)"),
        ConfigFile("tui.toml", settings.TUI_TOML, "toml", "how this TUI looks (the settings modal edits it)"),
    ]


def read_config(f: ConfigFile) -> str:
    try:
        return f.path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except (OSError, UnicodeDecodeError) as e:
        raise ValueError(f"{f.name}: {e}") from e
