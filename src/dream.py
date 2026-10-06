"""Dream companies: the constraints are waived, the honesty is not.

The list lives in the `dream_companies` table of `data/jobs.db` (name, match aliases, careers
URL, note, added_at; docs/spec-pre-release.md decision 9), edited with `python -m src.query
dream {list|add|rm}` or the TUI's Dream tab. The RULES stay in `config/profile.yaml`:
`dream_rule`, `relocation_line`, `dream_shortlist_threshold`. For a role at one of them the
pipeline waives the location rule and the comp floors: the title gate lets every posting
through, triage never drops for pay, the matcher scores on fit without the location cap, and
ingest shortlists at `dream_shortlist_threshold` instead of `shortlist_threshold`. What stays
hard is `dream_rule` (ITAR / US-person / citizens-only / clearance) and the fit score itself.
Nothing is stored on a job row: a company is a dream company whenever the table says so, so
editing the list never leaves stale flags.

A profile written before the table still carries a `dream_companies:` list; until
`python -m src.init` moves it into the table, that list counts too, so pulling this change
never silently drops a waiver.
"""
from __future__ import annotations

import re

from . import db
from .config import load_profile, shortlist_threshold

_CACHE: dict | None = None               # the profile (the rules)
_COMPANIES: list[dict] | None = None     # the table, read once per process


def _profile() -> dict:
    global _CACHE
    if _CACHE is None:
        try:
            _CACHE = load_profile()
        except FileNotFoundError:
            _CACHE = {}
    return _CACHE


def reset_cache() -> None:
    """Drop both caches: tests swap profiles, and a write to the table (the TUI's Dream tab,
    `query dream add|rm` in the same process) must be seen by the next read."""
    global _CACHE, _COMPANIES
    _CACHE = None
    _COMPANIES = None


def normalize(entry) -> dict | None:
    """A profile-style entry (a bare name or {name, match, note, careers_url}) -> the table's
    shape with `match` a non-empty lowercase list; None when it has no name."""
    if isinstance(entry, str):
        entry = {"name": entry}
    if not isinstance(entry, dict):
        return None
    name = str(entry.get("name") or "").strip()
    if not name:
        return None
    match = entry.get("match") or []
    if isinstance(match, str):
        match = [match]
    return {"name": name, "match": db._aliases(name, match), "note": str(entry.get("note") or "").strip(),
            "careers_url": str(entry.get("careers_url") or "").strip()}


def _table() -> list[dict]:
    """The table at `db.DB_PATH` (resolved at call time, so a test's temp DB is the one read);
    [] when there is no database yet. Never creates one just to read it."""
    path = db.DB_PATH
    if not path.exists():
        return []
    conn = db.connect(path)
    try:
        return db.list_dream(conn)
    finally:
        conn.close()


def legacy_profile_list() -> list[dict]:
    """The `dream_companies:` list a not-yet-migrated profile still carries ([] once moved)."""
    out = []
    for entry in _profile().get("dream_companies") or []:
        d = normalize(entry)
        if d:
            out.append(d)
    return out


def dream_companies() -> list[dict]:
    """[{name, match: [..], note, careers_url}] with `match` always a non-empty lowercase list:
    the table, plus any entry an unmigrated profile still lists under a name the table lacks."""
    global _COMPANIES
    if _COMPANIES is None:
        rows = [d for d in (normalize(r) for r in _table()) if d]
        have = {d["name"].lower() for d in rows}
        rows += [d for d in legacy_profile_list() if d["name"].lower() not in have]
        _COMPANIES = rows
    return _COMPANIES


def _compile() -> list[tuple[re.Pattern[str], dict]]:
    rules = []
    for d in dream_companies():
        # Word boundaries so "riot" never matches "Chariot"; dots and slashes in
        # aliases like "steven.com" are escaped, not wildcards.
        alt = "|".join(re.escape(m) for m in sorted(d["match"], key=len, reverse=True))
        rules.append((re.compile(rf"(?<![a-z0-9])(?:{alt})(?![a-z0-9])", re.I), d))
    return rules


def dream_entry(company: str | None) -> dict | None:
    """The dream_companies entry a company string belongs to, else None."""
    if not company:
        return None
    for rx, d in _compile():
        if rx.search(company):
            return d
    return None


def is_dream(company: str | None) -> bool:
    return dream_entry(company) is not None


def dream_name(company: str | None) -> str | None:
    """Canonical display name (so a hand-entered row and an ATS row share a canonical_key)."""
    d = dream_entry(company)
    return d["name"] if d else None


def dream_rule() -> str:
    return str(_profile().get("dream_rule") or "").strip()


def relocation_line() -> str:
    return str(_profile().get("relocation_line") or "").strip()


def dream_shortlist_threshold() -> int:
    """Shortlist cutoff for dream-company rows; falls back to the normal one."""
    raw = _profile().get("dream_shortlist_threshold")
    if raw is None:
        return shortlist_threshold()
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise ValueError(
            f"config/profile.yaml: dream_shortlist_threshold must be an integer, got {raw!r}"
        ) from None
