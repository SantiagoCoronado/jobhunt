"""Company-dossier path plumbing (thin: the AI/web research itself lives in Claude).

Python only guarantees a consistent slug + path so the writer (company-researcher
agent) and the reader (/jh-tailor -> resume-tailor) never disagree on where a company's
dossier lives.

  python -m src.research path "<company>"   # print the dossier path for a company name
  python -m src.research get  <job_id>       # resolve company from the DB, print path + exists
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

from .db import connect

ROOT = Path(__file__).resolve().parent.parent
COMPANIES_DIR = ROOT / "research" / "companies"


def company_slug(name: str) -> str:
    """Stable slug from a company name: lowercase, de-accented, hyphenated.

    "BC Tecnología" -> "bc-tecnologia";  "ClickUp" -> "clickup".
    """
    decomposed = unicodedata.normalize("NFKD", name or "")
    ascii_only = "".join(c for c in decomposed if not unicodedata.combining(c))
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    return slug


def dossier_path(name: str) -> Path:
    """Absolute path to a company's dossier .md (may or may not exist yet)."""
    return COMPANIES_DIR / f"{company_slug(name)}.md"


def _path(name: str) -> None:
    if not company_slug(name):
        sys.exit(f"Cannot derive a slug from company name: {name!r}")
    print(dossier_path(name))


def _get(job_id: str) -> None:
    row = connect().execute("SELECT company FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        sys.exit(f"No job with id {job_id}")
    company = row["company"]
    if not company:
        sys.exit(f"Job {job_id} has no company name recorded")
    p = dossier_path(company)
    print(f"company: {company}")
    print(f"dossier: {p}")
    print(f"exists:  {p.exists()}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Company dossier path helper")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("path", help="print dossier path for a company name")
    p.add_argument("company")
    g = sub.add_parser("get", help="resolve company from a job id, print path + exists")
    g.add_argument("job_id")
    a = ap.parse_args()
    if a.cmd == "path":
        _path(a.company)
    else:
        _get(a.job_id)
