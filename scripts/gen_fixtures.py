"""Regenerate tests/fixtures/ from the tracked *.example.* files.

The example files are the one source for the invented candidate ("Alex Example"); the
fixtures are copies of them so tests never read a real user's profile, resume or answers.
`tests/test_fixtures_sync.py` fails when the two drift, so after editing an example run:

    python scripts/gen_fixtures.py

Usage: python scripts/gen_fixtures.py [--check]   (--check exits 1 on drift, writes nothing)

It also renders Alex Example's master resume as the documents a new user brings to `/jh-setup`
(docs/spec-pre-release.md PR 5 story 1): `tests/fixtures/onboard/alex-example-resume.pdf`, a
plain text PDF built by hand so the same resume gives the same bytes, and `.docx` (python-docx,
whose zip carries a timestamp, so drift compares its paragraphs, not its bytes). Both say only
what the example resume says.
"""
from __future__ import annotations

import io
import shutil
import sys
import textwrap
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"

# example (tracked) -> fixture name under tests/fixtures/
PAIRS: dict[str, str] = {
    "config/profile.example.yaml": "profile.yaml",
    "config/sources.local.example.yaml": "sources.local.yaml",
    "resume/master_resume.example.yaml": "master_resume.yaml",
    "resume/answers.example.yaml": "answers.yaml",
}
MASTER_EXAMPLE = ROOT / "resume" / "master_resume.example.yaml"
RESUME_PDF = "onboard/alex-example-resume.pdf"
RESUME_DOCX = "onboard/alex-example-resume.docx"
WRAP = 96                      # characters per line at 10pt Helvetica inside the margins
PAGE_LINES = 56


def resume_lines(master: dict) -> list[str]:
    """The master resume as the plain lines a one-column resume document shows."""
    cv = master["cv"]
    sec = cv.get("sections") or {}
    links = [f"linkedin.com/in/{s['username']}" for s in cv.get("social_networks") or []
             if str(s.get("network", "")).lower() == "linkedin"]
    out = [cv["name"], " | ".join([cv["location"], cv["email"], str(cv["phone"]), *links]), ""]
    if sec.get("summary"):
        out += ["SUMMARY", *sec["summary"], ""]
    if sec.get("experience"):
        out.append("EXPERIENCE")
        for job in sec["experience"]:
            out.append(f"{job['position']}, {job['company']}, {job.get('location', '')} "
                       f"({job['start_date']} to {job['end_date']})")
            out += [f"- {h}" for h in job.get("highlights") or []]
        out.append("")
    if sec.get("projects"):
        out.append("PROJECTS")
        for proj in sec["projects"]:
            out.append(f"{proj['name']} ({proj.get('date', '')})")
            out += [f"- {h}" for h in proj.get("highlights") or []]
        out.append("")
    if sec.get("skills"):
        out += ["SKILLS", *(f"{s['label']}: {s['details']}" for s in sec["skills"]), ""]
    if sec.get("education"):
        out.append("EDUCATION")
        out += [f"{e['degree']} {e['area']}, {e['institution']} ({e['start_date']} to {e['end_date']})"
                for e in sec["education"]]
        out.append("")
    if sec.get("additional"):
        out += ["ADDITIONAL", *(f"{a['label']}: {a['details']}" for a in sec["additional"])]
    return out


def _pdf_escape(line: str) -> str:
    return line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def resume_pdf(lines: list[str]) -> bytes:
    """A minimal text PDF (Helvetica 10pt, US Letter): no dates, no ids, so the same lines give
    the same bytes."""
    wrapped: list[str] = []
    for line in lines:
        wrapped += textwrap.wrap(line, WRAP, subsequent_indent="  ") or [""]
    pages = [wrapped[i:i + PAGE_LINES] for i in range(0, len(wrapped), PAGE_LINES)]
    objs: list[bytes] = [b"<< /Type /Catalog /Pages 2 0 R >>", b"",
                         b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"]
    kids = []
    for page in pages:
        body = ["BT", "/F1 10 Tf", "13 TL", "54 738 Td"]
        body += [f"({_pdf_escape(ln)}) Tj T*" for ln in page]
        body.append("ET")
        stream = "\n".join(body).encode("latin-1", errors="replace")
        objs.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        content = len(objs)
        objs.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    b"/Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>" % content)
        kids.append(len(objs))
    objs[1] = (b"<< /Type /Pages /Kids [" + b" ".join(b"%d 0 R" % k for k in kids)
               + b"] /Count %d >>" % len(kids))
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objs, 1):
        offsets.append(out.tell())
        out.write(b"%d 0 obj\n" % i + obj + b"\nendobj\n")
    xref = out.tell()
    out.write(b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1))
    for off in offsets:
        out.write(b"%010d 00000 n \n" % off)
    out.write(b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref))
    return out.getvalue()


def resume_docx(lines: list[str], path: Path) -> None:
    from docx import Document

    doc = Document()
    for line in lines:
        doc.add_paragraph(line)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))


def docx_lines(path: Path) -> list[str]:
    from docx import Document

    return [p.text for p in Document(str(path)).paragraphs]


def _example_lines() -> list[str]:
    return resume_lines(yaml.safe_load(MASTER_EXAMPLE.read_text(encoding="utf-8")))


def documents_drift() -> list[str]:
    """The generated documents that no longer say what the example resume says."""
    lines = _example_lines()
    out = []
    pdf = FIXTURES / RESUME_PDF
    if not pdf.exists() or pdf.read_bytes() != resume_pdf(lines):
        out.append(RESUME_PDF)
    docx = FIXTURES / RESUME_DOCX
    if not docx.exists() or docx_lines(docx) != lines:
        out.append(RESUME_DOCX)
    return out


def drift() -> list[str]:
    """Fixture names whose content differs from (or is missing against) their example."""
    out = []
    for src, dst in PAIRS.items():
        a, b = ROOT / src, FIXTURES / dst
        if not a.exists():
            out.append(f"missing example: {src}")
        elif not b.exists() or a.read_bytes() != b.read_bytes():
            out.append(dst)
    return out + documents_drift()


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--check" in argv:
        bad = drift()
        for name in bad:
            print(f"  ! {name}")
        print("fixtures in sync" if not bad else "fixtures drifted: run python scripts/gen_fixtures.py")
        return 1 if bad else 0
    FIXTURES.mkdir(parents=True, exist_ok=True)
    for src, dst in PAIRS.items():
        shutil.copyfile(ROOT / src, FIXTURES / dst)
        print(f"  {src} -> tests/fixtures/{dst}")
    stale = documents_drift()
    lines = _example_lines()
    for name in stale:                   # the docx changes bytes on every save: rewrite only on drift
        (FIXTURES / name).parent.mkdir(parents=True, exist_ok=True)
        if name == RESUME_PDF:
            (FIXTURES / name).write_bytes(resume_pdf(lines))
        else:
            resume_docx(lines, FIXTURES / name)
        print(f"  {MASTER_EXAMPLE.relative_to(ROOT)} -> tests/fixtures/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
