"""Dream companies: the constraints are waived, the honesty is not.

`config/profile.yaml` carries a `dream_companies:` list (set 2026-09-01). For a
role at one of them the pipeline waives the location rule and the comp floors:
the title gate lets every posting through, triage never drops for pay, the
matcher scores on fit without the location cap, and ingest shortlists at
`dream_shortlist_threshold` instead of `shortlist_threshold`. What stays hard
is `dream_rule` (ITAR / US-person / citizens-only / clearance) and the fit
score itself. Nothing here is stored in the DB: a company is a dream company
whenever the profile says so, so editing the list never leaves stale flags.
"""
from __future__ import annotations

import re

from .config import load_yaml, shortlist_threshold

_CACHE: dict | None = None


def _profile() -> dict:
    global _CACHE
    if _CACHE is None:
        try:
            _CACHE = load_yaml("profile.yaml")
        except FileNotFoundError:
            _CACHE = {}
    return _CACHE


def reset_cache() -> None:
    """Tests swap profiles; production never needs this."""
    global _CACHE
    _CACHE = None


def dream_companies() -> list[dict]:
    """[{name, match: [..], note}] with `match` always a non-empty lowercase list."""
    out = []
    for entry in _profile().get("dream_companies") or []:
        if isinstance(entry, str):
            entry = {"name": entry}
        name = str(entry.get("name") or "").strip()
        if not name:
            continue
        match = [str(m).lower().strip() for m in (entry.get("match") or []) if str(m).strip()]
        if name.lower() not in match:
            match.append(name.lower())
        out.append({"name": name, "match": match, "note": entry.get("note") or ""})
    return out


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
    """Canonical display name (so a sheet row and an ATS row share a canonical_key)."""
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
