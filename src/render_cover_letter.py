"""Render a CoverLetter.md into a clean, house-styled .docx.

Matches the resume package look (Arial, navy #1F3864 accent) but with letter-appropriate
margins and spacing. The first blank-line-separated block is treated as the letterhead
(line 1 = name, remaining lines = contact info merged into one line); every following
block is a body paragraph.

Usage:
    python -m src.render_cover_letter applications/pending/<slug>/CoverLetter.md [--no-pdf]

Produces a .docx AND a .pdf next to the source with the same basename (the app convention
is CoverLetter.md -> CoverLetter.docx/.pdf). The PDF is the file that gets attached to an
application, so it is regenerated every run; passing --no-pdf, or a missing LibreOffice,
warns loudly that any existing PDF is now stale.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from src.render_docx import to_pdf

NAVY = "1F3864"
GREY = "444444"
FONT = "Arial"

# CoverLetter.md is supposed to be plain text (see .claude/agents/resume-tailor.md), but a
# tailor run can slip Markdown syntax in anyway. Rather than copy it verbatim into the docx
# (which shows up as literal "#"/"**" in the PDF), normalize the common Markdown markers so
# the rendered letter always looks like plain text, and warn loudly when we had to.
_HEADING_RE = re.compile(r"^#{1,6}\s+")
_INLINE_MD_RE = re.compile(
    r"(\*\*.+?\*\*|__.+?__|\*[^\s*].*?\*|_[^\s_].*?_|`[^`]+`)"
)


def _parse_inline(text: str) -> list[tuple[str, bool, bool]]:
    """Split text on Markdown bold/italic/code markers into (text, bold, italic) runs."""
    runs: list[tuple[str, bool, bool]] = []
    pos = 0
    for m in _INLINE_MD_RE.finditer(text):
        if m.start() > pos:
            runs.append((text[pos:m.start()], False, False))
        token = m.group(0)
        if token.startswith("**") and token.endswith("**"):
            runs.append((token[2:-2], True, False))
        elif token.startswith("__") and token.endswith("__"):
            runs.append((token[2:-2], True, False))
        elif token.startswith("`") and token.endswith("`"):
            runs.append((token[1:-1], False, False))
        elif token.startswith("*") and token.endswith("*"):
            runs.append((token[1:-1], False, True))
        elif token.startswith("_") and token.endswith("_"):
            runs.append((token[1:-1], False, True))
        pos = m.end()
    if pos < len(text):
        runs.append((text[pos:], False, False))
    if not runs:
        runs.append(("", False, False))
    return runs


def _strip_heading(line: str) -> tuple[str, bool]:
    """Strip a leading '#'..'######' Markdown heading marker. Returns (text, was_heading)."""
    stripped = _HEADING_RE.sub("", line, count=1)
    return stripped, stripped != line


def _has_markdown(text: str) -> bool:
    return bool(_INLINE_MD_RE.search(text)) or bool(_HEADING_RE.match(text))


def _run(p, text, size, color="000000", bold=False, italic=False):
    r = p.add_run(text)
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = RGBColor.from_string(color)
    # ensure the east-asian/complex-script font is Arial too, so nothing falls back
    rpr = r._element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.append(fonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        fonts.set(qn(attr), FONT)
    return r


def _run_markdown(p, text, size, color="000000", base_bold=False, base_italic=False):
    """Render text into paragraph p, splitting inline Markdown emphasis into separate runs."""
    for chunk, bold, italic in _parse_inline(text):
        if not chunk:
            continue
        _run(p, chunk, size, color, bold=base_bold or bold, italic=base_italic or italic)


def _bottom_border(p, color=NAVY, size=6):
    """Draw a thin bottom rule under paragraph p (size in eighths of a point)."""
    ppr = p._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), color)
    borders.append(bottom)
    ppr.append(borders)


def render(md_path: Path) -> Path:
    raw = md_path.read_text(encoding="utf-8")
    if "—" in raw:
        print("WARNING: em-dash (U+2014) found in source; house rule forbids it.", file=sys.stderr)

    # Split into blank-line-separated blocks; join wrapped lines within a block. A block that
    # is only a "---" horizontal rule is a Markdown separator, not content, so drop it.
    blocks: list[list[str]] = []
    for chunk in raw.replace("\r\n", "\n").split("\n\n"):
        lines = [ln.strip() for ln in chunk.split("\n") if ln.strip()]
        if lines and not all(re.fullmatch(r"-{3,}", ln) for ln in lines):
            blocks.append(lines)

    if not blocks:
        raise SystemExit(f"empty cover letter: {md_path}")

    found_markdown = any(_has_markdown(ln) for block in blocks for ln in block)

    doc = Document()
    sect = doc.sections[0]
    sect.top_margin = sect.bottom_margin = Inches(0.9)
    sect.left_margin = sect.right_margin = Inches(0.9)

    # --- letterhead ---
    head = blocks[0]
    name, _ = _strip_heading(head[0])
    contact = "  |  ".join(head[1:]) if len(head) > 1 else ""

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(1)
    _run_markdown(p, name, 16, NAVY, base_bold=True)

    if contact:
        pc = doc.add_paragraph()
        pc.paragraph_format.space_after = Pt(6)
        _run_markdown(pc, contact, 9.5, GREY)
        _bottom_border(pc)
    else:
        _bottom_border(p)

    # small gap after the rule
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # --- body ---
    for block in blocks[1:]:
        text = " ".join(_strip_heading(ln)[0] for ln in block)
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(9)
        pf.line_spacing = 1.15
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        _run_markdown(p, text, 10.5, "000000")

    if found_markdown:
        print(
            f"WARNING: Markdown syntax found in {md_path} and normalized for rendering "
            "(headings/**bold**/*italic*/`code` stripped or converted). CoverLetter.md must "
            "be plain text; fix the source so this cannot recur.",
            file=sys.stderr,
        )

    out = md_path.with_suffix(".docx")
    doc.save(str(out))
    return out


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if len(args) != 1 or flags - {"--no-pdf"}:
        print(__doc__)
        return 2
    md_path = Path(args[0])
    if not md_path.is_file():
        print(f"not found: {md_path}", file=sys.stderr)
        return 1
    out = render(md_path)
    print(f"wrote {out}")

    # The PDF is what actually gets attached to an application, so it must never be
    # left older than the .docx. Silently skipping the conversion once shipped a
    # placeholder line to the edge of a real submission.
    pdf = out.with_suffix(".pdf")
    if "--no-pdf" in flags:
        if pdf.exists():
            print(f"WARNING: {pdf} is now STALE (--no-pdf). Do not send it.", file=sys.stderr)
        return 0
    made = to_pdf(out)
    if made:
        print(f"wrote {made}")
        return 0
    msg = "PDF skipped: LibreOffice (soffice) not found"
    if pdf.exists():
        msg += f"\nWARNING: {pdf} is STALE and no longer matches the .docx. Do not send it."
    print(msg, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
