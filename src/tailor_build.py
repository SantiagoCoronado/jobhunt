"""One command after the tailor writes: split, check, render, audit, export, verdict.
(spec: docs/spec-tailor-lean.md, A2)

    python -m src.tailor_build <folder> [--json] [--no-pdf] [--keep-draft] [--strict-review]

Steps, stopping at the first hard failure:
  1. split <folder>/draft.md on `=== FILE: <name> ===` lines into the deliverables
  2. text checks: em-dashes, TAILOR marker left in answers.md, CoverLetter.md shape and
     body word count (220-280), resume YAML parses
  3. dream checks: relocation line in the letter <-> the relocation header (profile
     `work_authorization.relocation_header`) in the resume header
  4. resume render with fit auto (over one page at level 3 is a failure)
  5. line-fill audit (more than 3 findings is a failure, 1-3 are warnings)
  6. PDF export + page count (pypdf); two pages is a failure
  7. cover letter render + PDF
  8. verdict (at most 12 lines), <folder>/build.json, <folder>/state.json

Exit 0: green or warnings only. Exit 1: the agent must fix what the FAIL lines name.
Exit 2: environment (LibreOffice missing when a PDF was requested).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path

import yaml

from . import geo
from . import render_docx as rd
from .db import connect
from .config import profile, resume_basename
from .dream import is_dream, relocation_line
from .reconcile import folder_job_id
from .render_cover_letter import render as render_letter
from .tailor_state import update_state



def resume_file() -> str:
    """`<NameParts>Resume.yaml`, from profile.name (config.resume_basename)."""
    return f"{resume_basename()}.yaml"


def legacy_deliverables(folder: Path) -> list[str]:
    """Deliverables in the folder left under an earlier `profile.name` stem. The build writes
    and renders under the current one, so these stay behind holding older content, and
    scripts/export_pdf.sh regenerates their PDFs too: a human picking a file out of the
    folder can attach the stale resume. Named, never deleted (the tailor owns the folder)."""
    stem = resume_basename()
    return sorted(
        p.name
        for p in folder.glob("*Resume.*")
        if p.is_file() and p.suffix.lower() in (".yaml", ".yml", ".docx", ".pdf") and p.stem != stem
    )


def allowed_files() -> tuple[str, ...]:
    return (resume_file(), "CoverLetter.md", "match_report.md", "answers.md", "review_response.md")


def required_files() -> tuple[str, ...]:
    return (resume_file(), "CoverLetter.md", "match_report.md")


SPLIT_RE = re.compile(r"^=== FILE: ([A-Za-z0-9_.-]+) ===\s*$")
EMDASH = "\u2014"  # the em-dash, written as an escape so this file itself stays free of it
LETTER_MIN, LETTER_MAX = 220, 280
AUDIT_FAIL_AT = 4
# Deliberately above the honest target: the estimator runs conservative (the author's read of
# the 2026-09-02 drafts showed visible white space at an estimated 92%), so 95 here prints as a
# full page. Do not "fix" it back to 90.
FILL_WARN_BELOW = 95


class BuildError(Exception):
    """A hard failure that stops the build (exit 1)."""


class EnvError(Exception):
    """Missing tooling (exit 2)."""


@dataclass
class Verdict:
    folder: str
    job_id: int | None = None
    stage: str = "tailor"
    ok: bool = False
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    files: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    at: str = ""

    def to_dict(self) -> dict:
        return {"stage": self.stage, "job_id": self.job_id, "ok": self.ok, "failures": self.failures,
                "warnings": self.warnings, "metrics": self.metrics, "files": self.files,
                "verdict": self.lines, "at": self.at, "folder": self.folder}


# ------------------------------------------------------------------ steps

def split_draft(folder: Path, keep: bool = False) -> list[str]:
    """Explode draft.md into the named deliverables. Returns the names written."""
    draft = folder / "draft.md"
    if not draft.exists():
        return []
    current: str | None = None
    parts: dict[str, list[str]] = {}
    for line in draft.read_text(encoding="utf-8").splitlines():
        m = SPLIT_RE.match(line)
        if m:
            current = m.group(1)
            if current not in allowed_files():
                raise BuildError(f"draft.md names an unknown file {current!r}; allowed: {', '.join(allowed_files())}")
            parts.setdefault(current, [])
            continue
        if current is not None:
            parts[current].append(line)
    if not parts:
        raise BuildError("draft.md has no `=== FILE: <name> ===` sections")
    for name, body in parts.items():
        lines = [ln for ln in body]
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if lines and lines[0].lstrip().startswith("```"):        # a fenced section is the likeliest model slip
            lines.pop(0)
        if lines and lines[-1].strip().startswith("```"):
            lines.pop()
        text = "\n".join(lines).strip("\n") + "\n"
        (folder / name).write_text(text, encoding="utf-8")
    if not keep:
        draft.unlink()
    return list(parts)


def _tailor_blocks_left(text: str) -> list[str]:
    """The `## ...` heading above every `<!-- TAILOR` marker still in answers.md (answers_export
    can emit one per template id, so the failure names each block, not "the" block)."""
    heading, out = "(no heading)", []
    for line in text.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
        elif "<!-- TAILOR" in line:
            out.append(heading)
    return out


def letter_stats(text: str) -> dict:
    """Shape of CoverLetter.md: name line, contact line, Re: line, body words, markdown."""
    lines = [ln.rstrip() for ln in text.splitlines()]
    nonblank = [ln for ln in lines if ln.strip()]
    re_idx = next((i for i, ln in enumerate(nonblank) if ln.strip().lower().startswith("re:")), None)
    body_lines = nonblank[re_idx + 1:] if re_idx is not None else nonblank[2:]
    words = sum(len(ln.split()) for ln in body_lines)
    markdown = [ln for ln in nonblank if ln.lstrip().startswith("#") or "**" in ln or "`" in ln]
    return {"name": nonblank[0] if nonblank else "", "contact": nonblank[1] if len(nonblank) > 1 else "",
            "has_re": re_idx is not None, "body_words": words, "markdown_lines": markdown,
            "text": text}


def _emdash_hits(folder: Path) -> list[str]:
    hits = []
    for p in sorted(folder.glob("*")):
        if p.suffix not in (".md", ".yaml"):
            continue
        for n, ln in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if EMDASH in ln:
                hits.append(f"{p.name}:{n}")
    return hits


def _norm(s: str) -> str:
    return " ".join(s.split()).lower()


# Where is a posting located, relative to the candidate's relocation regions
# (profile `work_authorization.relocation_regions`, resolved through config/geo.yaml)? A dream
# row outside them must NOT carry the relocation line; the letter needs a visa note instead.


def relocation_scope(prof: dict | None = None) -> set[str]:
    """The regions a dream row may sit in without a visa note: the profile's
    `work_authorization.relocation_regions` plus the home region (a dream row at home needs
    no relocation). `relocation_regions: []` therefore means home only. Empty only when no
    home resolves either, and then nothing is ever outside."""
    if prof is None:
        try:
            prof = profile()
        except FileNotFoundError:
            return set()
    regions = set((prof.get("work_authorization") or {}).get("relocation_regions") or [])
    return regions | geo.home(prof)


def outside_relocation_regions(location: str | None, scope: set[str] | None = None) -> bool:
    """True when the posting sits somewhere the relocation line does not cover. Pass the
    scope from `relocation_scope()` when calling per row; None reads the profile once."""
    return geo.outside(location, relocation_scope() if scope is None else scope)


def resolve_job(folder: Path, job: dict | None) -> dict:
    """{id, company, dream, location}. Explicit `job` wins (tests); else the folder's -<id> + DB."""
    if job:
        return {"id": job.get("id"), "company": job.get("company"), "dream": bool(job.get("dream")),
                "location": job.get("location")}
    jid = folder_job_id(folder.name)
    if jid is None:
        return {"id": None, "company": None, "dream": False, "location": None}
    row = connect().execute("SELECT company, location FROM jobs WHERE id=?", (jid,)).fetchone()
    company = row["company"] if row else None
    return {"id": jid, "company": company, "dream": is_dream(company), "location": row["location"] if row else None}


def _pdf_pages(pdf: Path) -> int | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        return len(PdfReader(str(pdf)).pages)
    except Exception:  # noqa: BLE001  (a corrupt PDF is reported, not raised)
        return None


def _review(folder: Path, verdict: Verdict, strict: bool) -> None:
    p = folder / "review.json"
    if not p.exists():
        return
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        verdict.warnings.append("review.json is not valid JSON")
        verdict.lines.append("REVIEW  review.json unreadable                        WARN")
        return
    response = (folder / "review_response.md")
    answered: set[int] = set()
    if response.exists():
        answered = {int(x) for x in re.findall(r"(?:#|item\s+)(\d+)\b", response.read_text(encoding="utf-8"), re.I)}
    changed = False
    for item in doc.get("items") or []:
        if not item.get("resolved") and item.get("id") in answered:
            item["resolved"] = True
            changed = True
    if changed:
        p.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    open_items = [i for i in (doc.get("items") or []) if not i.get("resolved")]
    verdict.metrics["review_open"] = len(open_items)
    if not open_items:
        verdict.lines.append("REVIEW  0 open                                        OK")
        return
    musts = [i for i in open_items if i.get("severity") == "must"]
    desc = "; ".join(f"#{i.get('id')} {i.get('file')} {str(i.get('comment', ''))[:80]}" for i in open_items[:3])
    if strict and musts:
        verdict.failures.append(f"{len(musts)} unresolved must-fix review item(s): {desc}")
        verdict.lines.append(f"REVIEW  {len(open_items)} open ({len(musts)} must): {desc}   FAIL")
    else:
        verdict.warnings.append(f"{len(open_items)} open review item(s): {desc}")
        verdict.lines.append(f"REVIEW  {len(open_items)} open: {desc}   WARN")


# ------------------------------------------------------------------ build

def build(folder: Path, job: dict | None = None, no_pdf: bool = False, keep_draft: bool = False,
          strict_review: bool = False) -> Verdict:
    folder = Path(folder)
    v = Verdict(folder=str(folder), at=datetime.now(UTC).isoformat(timespec="seconds"))
    if not folder.is_dir():
        v.failures.append(f"not a folder: {folder} (has the application moved to another bucket?)")
        v.lines = [f"FAIL    {v.failures[0]}", "RESULT  FAIL (1) (exit 1)"]
        return v
    info = resolve_job(folder, job)
    v.job_id = info["id"]
    try:
        _build(folder, info, v, no_pdf, keep_draft, strict_review)
    except BuildError as e:
        v.failures.append(str(e))
        v.lines.append(f"FAIL    {e}")
    v.ok = not v.failures
    tail = "OK" if v.ok else f"FAIL ({len(v.failures)})"
    if v.warnings and v.ok:
        tail += f" with {len(v.warnings)} warning(s)"
    v.lines.append(f"RESULT  {tail} (exit {0 if v.ok else 1})")
    v.lines = _cap(v.lines, 12)
    (folder / "build.json").write_text(json.dumps(v.to_dict(), indent=1), encoding="utf-8")
    update_state(folder, "built", job_id=v.job_id, ok=v.ok)
    return v


def _cap(lines: list[str], n: int) -> list[str]:
    """Keep the verdict under n lines: FAIL and RESULT lines are never dropped."""
    if len(lines) <= n:
        return lines
    for prefix in ("FILES", "WARN", "AUDIT"):
        while len(lines) > n and any(ln.startswith(prefix) for ln in lines):
            idx = max(i for i, ln in enumerate(lines) if ln.startswith(prefix))
            lines.pop(idx)
    return lines


def _build(folder: Path, info: dict, v: Verdict, no_pdf: bool, keep_draft: bool, strict_review: bool) -> None:
    if not folder.is_dir():
        raise BuildError(f"not a folder: {folder}")
    v.lines.append(f"BUILD   {folder}" + ("  (dream row)" if info["dream"] else ""))

    written = split_draft(folder, keep_draft)
    if written:
        v.metrics["split"] = written
    missing = [f for f in required_files() if not (folder / f).exists()]
    if missing:
        raise BuildError(f"missing {', '.join(missing)}")
    legacy = legacy_deliverables(folder)
    if legacy:
        v.metrics["legacy_deliverables"] = legacy
        v.warnings.append(f"{len(legacy)} deliverable(s) under an earlier name stem, not rebuilt "
                          f"and not the ones to send: {', '.join(legacy)}. Delete them or keep "
                          f"only {resume_file()}")

    # ---- text checks
    hits = _emdash_hits(folder)
    if hits:
        v.failures.append(f"em-dash (U+2014) at {', '.join(hits[:6])}")
    v.metrics["emdash"] = len(hits)
    answers = folder / "answers.md"
    answers_ok = None
    if answers.exists():
        atext = answers.read_text(encoding="utf-8")
        left = _tailor_blocks_left(atext)
        answers_ok = not left
        if not answers_ok:
            v.failures.append(f"answers.md still carries {len(left)} TAILOR block(s) under: "
                              + "; ".join(left) + ". Replace each with a real answer written to the hint in its marker")
    letter = letter_stats((folder / "CoverLetter.md").read_text(encoding="utf-8"))
    v.metrics["letter_words"] = letter["body_words"]
    if not letter["has_re"]:
        v.failures.append("CoverLetter.md has no `Re:` line (line 1 name, line 2 contact, then Re:)")
    if letter["markdown_lines"]:
        v.failures.append(f"CoverLetter.md contains Markdown ({len(letter['markdown_lines'])} line(s) with #, ** or `)")
    if not (LETTER_MIN <= letter["body_words"] <= LETTER_MAX):
        v.failures.append(f"CoverLetter.md body is {letter['body_words']} words; must be {LETTER_MIN}-{LETTER_MAX}")

    ypath = folder / resume_file()
    try:
        data = yaml.safe_load(ypath.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise BuildError(f"{ypath.name} does not parse: {str(e).splitlines()[0]}") from e
    if not isinstance(data, dict) or "cv" not in data or not isinstance(data["cv"].get("sections"), dict):
        raise BuildError(f"{ypath.name} needs a top-level `cv:` with `sections:`")

    # ---- dream checks
    try:
        prof = profile()
    except FileNotFoundError:
        prof = {}
    wa = prof.get("work_authorization") or {}
    scope = relocation_scope(prof)
    reloc_header = str(wa.get("relocation_header") or "").lower()
    header_loc = str(data["cv"].get("location") or "")
    header_reloc = bool(reloc_header) and reloc_header in header_loc.lower()
    reloc = relocation_line()
    letter_reloc = bool(reloc) and _norm(reloc) in _norm(letter["text"])
    v.metrics["relocation_line"] = letter_reloc
    where = ", ".join(sorted(scope)) or "none declared"
    if info["dream"] and geo.outside(info.get("location"), scope):
        if letter_reloc or header_reloc:
            v.failures.append(f"dream row located outside the relocation regions ({where}): {info.get('location')}: "
                              "drop the relocation line and the relocation header; the letter needs a plain "
                              "visa note instead")
        elif "visa" not in letter["text"].lower():
            v.warnings.append(f"dream row located outside the relocation regions ({where}): {info.get('location')}: "
                              "the letter has no visa note")
    elif info["dream"]:
        if header_reloc and not letter_reloc:
            v.failures.append(f"header says {reloc_header!r} but the letter lacks relocation_line verbatim: {reloc!r}")
        elif letter_reloc and not header_reloc and reloc_header:
            expected = f"{prof.get('header_location') or header_loc.split('(')[0].strip()} ({wa.get('relocation_header')})"
            v.failures.append(f"letter carries relocation_line but the header is not {expected!r}")
    elif letter_reloc:
        v.warnings.append("relocation line present on a non-dream row; profile waives location only for dream companies")

    # ---- resume render + audit
    level = rd.pick_fit_level(data)
    est = rd.estimate_height_pts(data, level)
    pct = est / rd.PAGE_AVAIL_PTS * 100
    lang = data["cv"].get("language", "en")
    doc = rd.build(data, level, lang)
    docx = ypath.with_suffix(".docx")
    doc.save(str(docx))
    v.metrics.update({"fit_level": level, "fill_pct": round(pct)})
    if pct > 100 and level >= 3:
        v.failures.append(f"resume is {pct:.0f}% of the page at fit level 3: cut a bullet (trim real content)")
    elif pct > 100:
        v.warnings.append(f"estimate {pct:.0f}% at level {level}; verify the page count")
    elif pct < FILL_WARN_BELOW and level == 0:
        # Only at level 0 is "add content" the right instruction: a higher level was picked
        # because the content already overflowed the looser spacing, so a 94% there is a full page.
        # A failure, not a warning: exit 1 is what makes the agent's fix round happen.
        body_line = rd.FS["body"][level] * rd.LINE + rd.SP["body_after"][level]
        free_lines = int((rd.PAGE_AVAIL_PTS - est) / body_line)
        v.metrics["free_lines"] = free_lines
        v.failures.append(f"resume fills only {pct:.0f}% at fit level {level}: about {free_lines} body lines free; "
                          "add real master-resume content (full-width bullets) until it reads 95-100%")
    findings = rd.audit_line_fill(data, level)
    v.metrics["audit_findings"] = len(findings)
    if len(findings) >= AUDIT_FAIL_AT:
        v.failures.append(f"{len(findings)} blocks end with trailing white space (max {AUDIT_FAIL_AT - 1})")
    for f in findings[:3]:
        v.warnings.append(f)

    # ---- pdf + page count
    pages: int | None = None
    page_note = ", pdf skipped" if no_pdf else ""
    if not no_pdf:
        pdf = rd.to_pdf(docx)
        if not pdf:
            raise EnvError("LibreOffice (soffice) not found; rerun with --no-pdf or install it")
        pages = _pdf_pages(pdf)
        v.metrics["pages"] = pages
        if pages is None:
            page_note = ", page count skipped: pypdf missing or PDF unreadable"
            v.warnings.append("page count skipped: pypdf missing or PDF unreadable (pip install -r requirements.txt)")
        elif pages > 1:
            v.failures.append(f"rendered PDF has {pages} pages; cut real content until it is one")

    # ---- cover letter
    letter_docx = render_letter(folder / "CoverLetter.md")
    if not no_pdf:
        if not rd.to_pdf(letter_docx):
            raise EnvError("LibreOffice (soffice) not found for the cover letter PDF")

    # ---- verdict lines
    page_txt = f", {pages} page{'s' if pages != 1 else ''} (pdf)" if pages is not None else page_note
    v.lines.append(f"RESUME  fit level {level}, {pct:.0f}% fill{page_txt}"
                   f"        {'FAIL' if any('page' in f or 'resume' in f for f in v.failures) else 'OK'}")
    if findings:
        shown = [f.split(" | ...")[0] for f in findings[:3]]   # drop the quoted tail, keep the numbers
        more = f" (+{len(findings) - 3} more)" if len(findings) > 3 else ""
        v.lines.append(f"AUDIT   {len(findings)} block(s): " + " | ".join(shown) + more
                       + ("   FAIL" if len(findings) >= AUDIT_FAIL_AT else "   WARN"))
    else:
        v.lines.append("AUDIT   clean                                         OK")
    lstate = "OK" if not any("letter" in f.lower() for f in v.failures) else "FAIL"
    v.lines.append(f"LETTER  {letter['body_words']} words, {'plain text' if not letter['markdown_lines'] else 'MARKDOWN'}, "
                   f"relocation line {'present' if letter_reloc else 'absent'}   {lstate}")
    if answers_ok is None:
        v.lines.append("ANSWERS missing (run src.answers_export)               WARN")
        v.warnings.append("answers.md missing")
    else:
        v.lines.append(f"ANSWERS why-company {'filled' if answers_ok else 'NOT filled'}                       {'OK' if answers_ok else 'FAIL'}")
    v.lines.append(f"EMDASH  {len(hits)}                                            {'OK' if not hits else 'FAIL'}")
    _review(folder, v, strict_review)
    audit_set = set(findings)
    for f in v.failures:
        if not any(ln.startswith("FAIL") and f in ln for ln in v.lines):
            v.lines.append(f"FAIL    {f}")
    for w in v.warnings:
        if w not in audit_set and not any(w in ln for ln in v.lines):
            v.lines.append(f"WARN    {w}")
    v.files = sorted(p.name for p in folder.iterdir() if p.is_file() and p.name not in ("build.json", "state.json"))
    v.lines.append("FILES   " + " ".join(v.files))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folder")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--keep-draft", action="store_true")
    ap.add_argument("--strict-review", action="store_true")
    a = ap.parse_args(argv)
    try:
        v = build(Path(a.folder), no_pdf=a.no_pdf, keep_draft=a.keep_draft, strict_review=a.strict_review)
    except EnvError as e:
        print(f"ENV     {e}")
        return 2
    if a.json:
        print(json.dumps(v.to_dict(), indent=1))
    else:
        print("\n".join(v.lines))
    return 0 if v.ok else 1


if __name__ == "__main__":
    sys.exit(main())
