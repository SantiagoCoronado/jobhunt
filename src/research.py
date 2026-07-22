"""Company-dossier path plumbing (thin: the AI/web research itself lives in Claude).

Python only guarantees a consistent slug + path so the writer (company-researcher
agent) and the reader (/jh-tailor -> resume-tailor) never disagree on where a company's
dossier lives, and a deterministic staleness verdict so "still looks fresh" is not
eyeballed differently every session.

  python -m src.research path "<company>"    # print the dossier path for a company name
  python -m src.research get  <job_id>       # resolve company from the DB, print path + exists + stale
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path

from .db import connect

ROOT = Path(__file__).resolve().parent.parent
COMPANIES_DIR = ROOT / "research" / "companies"
ALIASES_FILE = ROOT / "research" / "aliases.yaml"

STALE_DAYS = 30
# "99minutos.com" and "99minutos" are one company; the TLD only survives when
# the name is written as a domain, so strip it before slugging.
_DOMAIN_SUFFIX = re.compile(r"\.(com|io|ai|co|net|org|dev|app|mx)$", re.IGNORECASE)
# Corporate boilerplate that produces duplicate slugs ("EasyAudit AI, Inc.").
_CORP_TOKENS = {"inc", "llc", "ltd", "gmbh", "corp", "plc"}
_RESEARCHED = re.compile(r"researched:\s*(\d{4}-\d{2}-\d{2})")


@lru_cache(maxsize=1)
def _aliases() -> dict:
    """Optional manual slug overrides: research/aliases.yaml {alias: canonical}.
    Cached per process; CLI invocations are one-shot so edits are always seen."""
    if not ALIASES_FILE.exists():
        return {}
    import yaml
    return yaml.safe_load(ALIASES_FILE.read_text()) or {}


def company_slug(name: str) -> str:
    """Stable slug from a company name: lowercase, de-accented, hyphenated,
    domain TLDs and corporate suffixes stripped, aliases applied.

    "BC Tecnología" -> "bc-tecnologia";  "99minutos.com" -> "99minutos";
    "EasyAudit AI, Inc." -> "easyaudit-ai"  (but "Sira AI" keeps its "ai").
    """
    name = _DOMAIN_SUFFIX.sub("", (name or "").strip())
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_only = "".join(c for c in decomposed if not unicodedata.combining(c))
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    parts = slug.split("-")
    while len(parts) > 1 and parts[-1] in _CORP_TOKENS:
        parts.pop()
    slug = "-".join(parts)
    return _aliases().get(slug, slug)


def dossier_path(name: str) -> Path:
    """Absolute path to a company's dossier .md (may or may not exist yet)."""
    return COMPANIES_DIR / f"{company_slug(name)}.md"


def dossier_info(name: str, ttl_days: int = STALE_DAYS) -> dict:
    """Deterministic freshness: parse the dossier's `researched: YYYY-MM-DD`
    line (file mtime as fallback) and compare against the TTL. Commands branch
    on `stale` instead of eyeballing."""
    p = dossier_path(name)
    info: dict = {"path": p, "exists": p.exists(), "researched": None,
                  "age_days": None, "stale": None}
    if not p.exists():
        return info
    m = _RESEARCHED.search(p.read_text(errors="ignore"))
    researched = (date.fromisoformat(m.group(1)) if m
                  else datetime.fromtimestamp(p.stat().st_mtime).date())
    info["researched"] = researched.isoformat()
    info["age_days"] = (date.today() - researched).days
    info["stale"] = info["age_days"] > ttl_days
    return info


def _print_info(company: str, ttl: int) -> None:
    info = dossier_info(company, ttl)
    print(f"company: {company}")
    print(f"dossier: {info['path']}")
    print(f"exists:  {info['exists']}")
    if info["exists"]:
        print(f"researched: {info['researched']} ({info['age_days']} days ago)")
        print(f"stale:   {info['stale']} (ttl {ttl} days)")


def _path(name: str) -> None:
    if not company_slug(name):
        sys.exit(f"Cannot derive a slug from company name: {name!r}")
    print(dossier_path(name))


def _get(job_id: str, ttl: int) -> None:
    row = connect().execute("SELECT company FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        sys.exit(f"No job with id {job_id}")
    company = row["company"]
    if not company:
        sys.exit(f"Job {job_id} has no company name recorded")
    _print_info(company, ttl)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Company dossier path helper")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("path", help="print dossier path for a company name")
    p.add_argument("company")
    g = sub.add_parser("get", help="resolve company from a job id, print path + exists + stale")
    g.add_argument("job_id")
    g.add_argument("--ttl", type=int, default=STALE_DAYS, help="freshness window in days")
    a = ap.parse_args()
    if a.cmd == "path":
        _path(a.company)
    else:
        _get(a.job_id, a.ttl)
