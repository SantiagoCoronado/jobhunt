"""Render `applications/<bucket>/<company>-<id>/answers.md` from the answer bank.

Deterministic half of /jh-tailor step 2b. Only `draft: false` entries leave the bank;
`{company}` placeholders are filled from the job row. The `why-company` entry is a
TEMPLATE in the bank, so it is emitted as a clearly marked block for the resume-tailor
agent to replace from the company dossier. Draft ids are listed under "needs your input".

Usage:
    python -m src.answers_export <job_id> [--out <dir>]     # default dir: the job's folder
    python -m src.answers_export <job_id> --stdout

Why a script: the bank is 50 kB and only ~7 entries are approved. Having every tailor
sub-agent read the whole file cost roughly 13k tokens per agent call it stayed in
context for (token audit, 2026-09-02).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from .config import ROOT
from .db import connect

ANSWERS = ROOT / "resume" / "answers.yaml"
# Entries whose stored body is an instruction to the tailor, not an answer: rendered under a
# TAILOR marker so the build's marker check refuses a folder that still carries it verbatim.
TEMPLATE_IDS = {
    "why-company": ("replace this block with a 3-sentence answer grounded in the company "
                    "dossier (one concrete company fact, one line tying it to the founder / "
                    "AI-deployment background, one line on what to ship first)."),
    "what-do-you-know-about-us": ("replace this block with three specific dossier facts said "
                                  "flat (at least one not on the homepage) and one line on what "
                                  "maps to Santiago's own work; never mention how much was "
                                  "prepared."),
}


def _slug(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def render(job: dict, entries: list[dict]) -> tuple[str, list[str]]:
    company = job["company"]
    lines = [
        f"# Application answers: {company}, {job['title']} (job {job['id']})",
        "",
        f"Approved answers only (draft: false in resume/answers.yaml), personalized for {company}.",
        "",
    ]
    drafts: list[str] = []
    for e in entries:
        if e.get("draft", True):
            drafts.append(e["id"])
            continue
        answer = str(e.get("answer") or "").strip()
        if not answer:
            drafts.append(e["id"])
            continue
        lines.append(f"## {e['question'].replace('{company}', company)}")
        if e["id"] in TEMPLATE_IDS:
            lines.append(f"<!-- TAILOR: {TEMPLATE_IDS[e['id']]} -->")
            lines.append(answer.replace("{company}", company))
        else:
            lines.append(answer.replace("{company}", company))
        lines.append("")
    if drafts:
        lines.append("## Needs your input (draft entries, not emitted)")
        lines.append(", ".join(drafts))
        lines.append("")
    return "\n".join(lines), drafts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("job_id", type=int)
    ap.add_argument("--out", help="folder to write answers.md into (default: the job's application folder)")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--company", help="display name override (aggregator rows such as HN: Who is Hiring)")
    a = ap.parse_args(argv)
    conn = connect()
    row = conn.execute("SELECT id, company, title FROM jobs WHERE id=?", (a.job_id,)).fetchone()
    if not row:
        sys.exit(f"no job {a.job_id}")
    job = dict(row)
    if a.company:
        job["company"] = a.company
    entries = (yaml.safe_load(ANSWERS.read_text()) or {}).get("answers") or []
    text, drafts = render(job, entries)
    if a.stdout:
        print(text)
        return 0
    if a.out:
        out = Path(a.out)
    else:
        hits = sorted(p for p in (ROOT / "applications").glob(f"*/*-{job['id']}") if p.is_dir())
        out = hits[0] if hits else ROOT / "applications" / "pending" / f"{_slug(job['company'])}-{job['id']}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "answers.md").write_text(text)
    n = sum(1 for e in entries if not e.get("draft", True))
    print(f"wrote {out / 'answers.md'}: {n} approved answers, {len(drafts)} drafts listed, "
          f"why-company left as TAILOR block")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
