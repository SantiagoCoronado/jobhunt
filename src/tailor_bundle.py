"""Bundle every input the resume-tailor agent needs into ONE file (spec: docs/spec-tailor-lean.md, A1).

    python -m src.tailor_bundle <job_id> [--company NAME] [--dossier PATH] [--out DIR] [--stdout]

Writes `data/tailor/<id>/inputs.md` with, in this fixed order:
  1. voice rules (docs/writing-voice.md, verbatim)
  2. profile (config/profile.yaml, verbatim: dream_rule, relocation_line, location_rule, comp ...)
  3. master resume (resume/master_resume.yaml, verbatim, the single source of truth)
  4. page geometry (generated from src/render_docx constants, so it can never go stale)
  5. the job (DB row, dream flag, the dream sheet's Curated block, full description)
  6. the company dossier (or one line saying there is none)
  7. answers.md pre-rendered (src.answers_export, why-company left as a TAILOR block)
  8. the existing tailored resume when the application folder already has one
  9. open review comments from <folder>/review.json when a reviewer left any

The agent reads this once, writes draft.md once, runs `python -m src.tailor_build` once.
Nothing under data/mail_* or interviews/ can end up here.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, UTC
from pathlib import Path

import yaml

from . import render_docx as rd
from .answers_export import _slug, answers_path
from .answers_export import render as render_answers
from .config import ROOT, user_file
from .db import connect
from .dream import is_dream
from .reconcile import APPS_DIR, find_folder
from .research import dossier_info
from .tailor_state import update_state

TAILOR_DIR = ROOT / "data" / "tailor"
VOICE = ROOT / "docs" / "writing-voice.md"

SECTION_PURPOSE = {
    1: "Voice rules. Every sentence you write obeys these.",
    2: "Profile. dream_rule, relocation_line, location_rule and comp are quoted here verbatim; apply them as written.",
    3: "Master resume. The single source of truth: reorder, reframe, rephrase; never add a fact that is not here.",
    4: "Page geometry. Write to this grid on the FIRST draft so the build passes without a fit loop.",
    5: "The job.",
    6: "Company dossier. Use one or two of its facts for the letter hook; never invent a company fact.",
    7: "answers.md, pre-rendered. Copy it into draft.md unchanged except the TAILOR blocks (one per template question): replace each with a real answer written to the hint inside its marker.",
    8: "Existing tailored resume for this job. Edit it instead of starting over.",
    9: "Open review comments. Address each by number; list what you changed in review_response.md.",
}


def folder_name(company: str, job_id: int) -> str:
    return f"{_slug(company)}-{job_id}"


def application_folder(job_id: int, company: str, apps_dir: Path = APPS_DIR) -> Path:
    """The job's application folder: the existing one in any bucket, else pending/<slug>-<id>."""
    hit = find_folder(job_id, apps_dir)
    return hit[1] if hit else apps_dir / "pending" / folder_name(company, job_id)


# ------------------------------------------------------------------ geometry

def chars_per_line(size: float, width_pts: float, samples: list[str]) -> int:
    """Characters that fit on one full line at `size`, measured on real bullet text."""
    tot = n = 0
    for t in samples:
        lines, fill = rd._wrap_info(t, size, width_pts)
        if lines >= 2:
            tot += len(t) / (lines - 1 + fill)
            n += 1
    if n:
        return round(tot / n)
    probe = "Built and shipped a production service for three teams, cutting review time and cost."
    return round(width_pts / (rd._text_width_pts(probe, size) / len(probe)))


def geometry_block(master: dict) -> str:
    """The grid the agent writes to, computed from the renderer's own constants."""
    avail = (rd.PAGE_W - 2 * rd.MARGIN_LR) / 20.0
    avail_bullet = avail - rd.BULLET_LEFT / 20.0
    cv = master["cv"]
    secs = cv.get("sections", {}) or {}
    samples = [h for k in ("experience", "projects") for e in (secs.get(k) or [])
               for h in (e.get("highlights") or [])]
    body, summ = rd.FS["body"], rd.FS["summary"]
    b_norm = chars_per_line(body[1], avail_bullet, samples)
    b_tight = chars_per_line(body[3], avail_bullet, samples)
    s_norm = chars_per_line(summ[1], avail, samples)
    s_tight = chars_per_line(summ[3], avail, samples)
    fixed = {k: v for k, v in secs.items() if k in ("summary", "skills", "education", "additional")}
    fixed_pts = rd.estimate_height_pts({"cv": {**cv, "sections": fixed}}, 0)
    body_line = body[0] * rd.LINE + rd.SP["body_after"][0]
    budget = int((rd.PAGE_AVAIL_PTS - fixed_pts) / body_line)
    n_exp = len(secs.get("experience") or [])
    n_proj = len(secs.get("projects") or [])
    return "\n".join([
        f"Page: US letter, {rd.MARGIN_LR / 1440:.2f}in side margins, content width {avail:.0f}pt "
        f"(bullets indent to {avail_bullet:.0f}pt), {rd.PAGE_AVAIL_PTS:.0f}pt of usable height.",
        f"Body text {body[1]}pt Arial at fit levels 0-2; {body[3]}pt at level 3 (the last resort).",
        f"A full bullet line holds about {b_norm} characters ({b_tight} at level 3); a full summary or "
        f"skills line about {s_norm} ({s_tight} at level 3).",
        f"Write to the grid: every bullet is either ONE full line ({b_norm - 15} to {b_norm} chars) or TWO "
        f"full lines ({2 * b_norm - 15} to {2 * b_norm} chars). Never 1.3 lines. Summary: two full lines "
        f"({2 * s_norm - 12} to {2 * s_norm} chars). Skills: each label line {s_norm - 10} to {s_norm} chars. "
        "Merge a short bullet into a sibling rather than leave it dangling.",
        f"Budget: with this master resume's header, summary, skills, education and additional lines, about "
        f"{budget} body lines remain at fit level 0 (the loosest spacing) for experience + projects, and each "
        f"entry costs 2 lines of company/title overhead before its bullets. The master has {n_exp} experience "
        f"and {n_proj} project entries; keep every entry and spend the WHOLE budget on full-width bullets. "
        "Overshooting by one or two lines is fine: the renderer tightens spacing on its own (levels 1 to 3). "
        "Undershooting leaves white space at the bottom of the page and the build flags anything under 95%. "
        "The estimator runs a little conservative, so a draft that estimates 97-100% prints with a small margin.",
    ])


# ------------------------------------------------------------------ sections

def _job_block(conn, job_id: int, company_override: str | None) -> tuple[str, dict]:
    r = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not r:
        raise SystemExit(f"no job {job_id}")
    job = dict(r)
    job["dream"] = is_dream(job.get("company"))
    display = company_override or job["company"]
    curated = None
    if job.get("source") == "dreamsheet":
        curated = job.get("description")
    elif job.get("canonical_key"):
        hit = conn.execute(
            "SELECT description FROM jobs WHERE canonical_key=? AND source='dreamsheet' "
            "AND description IS NOT NULL LIMIT 1", (job["canonical_key"],)).fetchone()
        curated = hit["description"] if hit else None
    verdict = {}
    try:
        verdict = json.loads(job.get("match_verdict") or "{}")
        if not isinstance(verdict, dict):
            verdict = {}
    except ValueError:
        verdict = {}
    if job.get("salary_min") is not None or job.get("salary_max") is not None:
        salary = f"{job.get('salary_min')}-{job.get('salary_max')} {job.get('currency') or ''} (as posted; annualize before judging)"
    else:
        salary = "not posted"
    lines = [
        f"id: {job['id']}",
        f"company: {display}" + (f"  (DB row says {job['company']!r}; use {display!r} everywhere)" if company_override else ""),
        f"title: {job.get('title')}",
        f"location: {job.get('location')}",
        f"remote flag: {job.get('remote')}",
        f"url: {job.get('url')}",
        f"source: {job.get('source')}",
        f"salary: {salary}",
        f"status: {job.get('status')}, match {job.get('match_score')}",
        f"dream: {'true (profile dream_rule applies)' if job['dream'] else 'false'}",
    ]
    for k in ("recommendation", "location_ok", "visa_path", "missing_skills", "reasons"):
        if verdict.get(k) not in (None, "", []):
            lines.append(f"matcher {k}: {verdict[k]}")
    if curated:
        lines += ["", "Curated (dream sheet), Santiago's own judgment; quote its priority, never recompute it:", curated.strip()]
    desc = (job.get("description") or "").strip()
    if desc and job.get("source") != "dreamsheet":
        lines += ["", "Description:", desc]
    else:
        lines += ["", "Description: EMPTY in the DB for this row. Use the dossier's Target role section as the JD; "
                  "if that is missing too, say so in match_report.md and tailor on the title alone."]
    return "\n".join(lines), {**job, "display_company": display, "curated": bool(curated)}


def _dossier_block(company: str, override: Path | None) -> tuple[str, dict]:
    if override:
        p = Path(override)
        if not p.exists():
            raise SystemExit(f"dossier not found: {p}")
        return p.read_text(encoding="utf-8"), {"dossier": p.name, "stale": None}
    info = dossier_info(company)
    if not info["exists"]:
        return ("No dossier for this company. Do not invent company facts; write the hook from the JD "
                "and say in match_report.md that no dossier was available."), {"dossier": None, "stale": None}
    head = ""
    if info["stale"]:
        head = (f"NOTE: dossier researched {info['researched']} ({info['age_days']} days ago, stale): "
                "do not cite its time-sensitive facts (funding, news) as current.\n\n")
    return head + Path(info["path"]).read_text(encoding="utf-8"), {"dossier": Path(info["path"]).name, "stale": info["stale"]}


def _review_block(folder: Path) -> tuple[str | None, int]:
    p = folder / "review.json"
    if not p.exists():
        return None, 0
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return "review.json is not valid JSON; ignore it and mention that in match_report.md.", 0
    items = [i for i in (doc.get("items") or []) if not i.get("resolved")]
    if not items:
        return None, 0
    lines = [f"Reviewer: {doc.get('reviewer', '?')} at {doc.get('at', '?')}. Open items:"]
    for i in items:
        lines.append(f"{i.get('id')}. [{i.get('severity', 'should')}] {i.get('file')} @ {i.get('anchor', '')}: {i.get('comment', '')}")
    return "\n".join(lines), len(items)


def build_bundle(conn, job_id: int, company: str | None = None, dossier: str | None = None,
                 apps_dir: Path = APPS_DIR) -> tuple[str, dict]:
    """Return (bundle text, meta). Pure apart from reading the repo files and the DB."""
    job_text, job = _job_block(conn, job_id, company)
    master = yaml.safe_load(user_file("master_resume").read_text(encoding="utf-8"))
    entries = (yaml.safe_load(answers_path().read_text(encoding="utf-8")) or {}).get("answers") or []
    answers_text, drafts = render_answers(
        {"id": job["id"], "company": job["display_company"], "title": job.get("title")}, entries)
    dossier_text, dmeta = _dossier_block(job["display_company"], Path(dossier) if dossier else None)
    folder = application_folder(job_id, job["display_company"], apps_dir)
    existing = folder / "SantiagoCoronadoResume.yaml"
    review_text, n_review = _review_block(folder)

    parts: list[tuple[int, str]] = [
        (1, VOICE.read_text(encoding="utf-8")),
        (2, user_file("profile").read_text(encoding="utf-8")),
        (3, user_file("master_resume").read_text(encoding="utf-8")),
        (4, geometry_block(master)),
        (5, job_text),
        (6, dossier_text),
        (7, answers_text),
    ]
    if existing.exists():
        parts.append((8, existing.read_text(encoding="utf-8")))
    if review_text:
        parts.append((9, review_text))

    out = [f"<!-- tailor bundle for job {job_id}, generated {datetime.now(UTC).isoformat(timespec='seconds')} -->",
           f"Application folder: {folder}", ""]
    for n, body in parts:
        out.append(f"# {n}. {SECTION_PURPOSE[n].split('.')[0]}")
        out.append(SECTION_PURPOSE[n])
        out.append("")
        out.append(body.rstrip())
        out.append("")
    text = "\n".join(out)
    meta = {
        "job_id": job_id, "company": job["display_company"], "dream": job["dream"], "curated": job["curated"],
        "dossier": dmeta["dossier"], "dossier_stale": dmeta["stale"],
        "answers_approved": sum(1 for e in entries if not e.get("draft", True)),
        "answers_drafts": len(drafts), "existing_draft": existing.exists(), "review_open": n_review,
        "folder": str(folder), "sections": [n for n, _ in parts], "bytes": len(text.encode("utf-8")),
    }
    return text, meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("job_id", type=int)
    ap.add_argument("--company", help="display name override (aggregator rows: HN, Jobgether)")
    ap.add_argument("--dossier", help="dossier path override (e.g. research/companies/quill.md)")
    ap.add_argument("--out", help="directory for inputs.md (default data/tailor/<id>)")
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args(argv)
    text, meta = build_bundle(connect(), a.job_id, a.company, a.dossier)
    if a.stdout:
        print(text)
        return 0
    out_dir = Path(a.out) if a.out else TAILOR_DIR / str(a.job_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "inputs.md"
    path.write_text(text, encoding="utf-8")
    folder = Path(meta["folder"])
    folder.mkdir(parents=True, exist_ok=True)
    update_state(folder, "bundled", job_id=a.job_id)
    extras = []
    if meta["existing_draft"]:
        extras.append("existing draft included")
    if meta["review_open"]:
        extras.append(f"{meta['review_open']} review items open")
    print(f"wrote {path} ({meta['bytes'] / 1024:.1f} kB, ~{meta['bytes'] // 4 / 1000:.1f}k tokens): "
          f"dream={str(meta['dream']).lower()} dossier={meta['dossier'] or 'none'}"
          f"{' (stale)' if meta['dossier_stale'] else ''} answers={meta['answers_approved']} approved"
          f"{'; ' + ', '.join(extras) if extras else ''}")
    print(f"folder: {folder}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
