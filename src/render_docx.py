"""Render a resume YAML (master or tailored, RenderCV-like schema) to a styled .docx.

Design is an exact replica of the reference CVs ("Tech AI job CV" design):
Arial base, navy #1F3864 accents, underlined CAPS section headers, compact
spacing, 0.38in top/bottom and 0.7in side margins, right-tab dates.

Usage:
    python -m src.render_docx <resume.yaml> [-o out.docx] [--fit auto|0|1|2|3] [--pdf]

Fit levels (auto picks the loosest level whose estimated height fits one page):
    0  reference spacing (the design as-is)
    1  paragraph spacing tightened ~30%
    2  spacing tightened ~50%
    3  level 2 + body font one step smaller (9.5/9 -> 9/8.5)

No em-dashes (U+2014) are ever emitted; dates use an en dash.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from docx import Document
from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Twips

# ---------------------------------------------------------------- design spec

NAVY = "1F3864"
BLACK = "000000"
DARK = "262626"
GRAY = "404040"
LIGHT = "808080"

PAGE_W = 12240          # US Letter, twips
PAGE_H = 15840
MARGIN_TB = 547         # 0.38 in
MARGIN_LR = 1008        # 0.70 in
RIGHT_TAB = 10080       # right-aligned tab stop for dates (7.0 in)
BULLET_LEFT = 720       # bullet text indent
BULLET_HANG = 360

# spacing in points, per fit level: (level0, level1, level2, level3)
SP = {
    "name_after":     (1.5, 1.2, 1.0, 1.0),
    "contact_after":  (1.5, 1.2, 1.0, 1.0),
    "sect_before":    (5.0, 4.0, 3.0, 3.0),
    "sect_after":     (1.5, 1.2, 1.0, 1.0),
    "body_after":     (1.5, 1.0, 0.7, 0.7),
    "comp_before":    (4.0, 3.0, 2.0, 2.0),
    "proj_before":    (3.5, 2.5, 1.8, 1.8),
    "proj_after":     (0.5, 0.4, 0.3, 0.3),
}

# font sizes in points, per fit level
FS = {
    "name":    (18.0, 18.0, 18.0, 17.0),
    "contact": (8.0, 8.0, 8.0, 8.0),
    "section": (10.0, 10.0, 10.0, 9.5),
    "company": (9.5, 9.5, 9.5, 9.0),
    "summary": (9.5, 9.5, 9.5, 9.0),
    "body":    (9.0, 9.0, 9.0, 8.5),
    "projdate": (8.5, 8.5, 8.5, 8.0),
}

LINE = 1.16  # measured single-spacing factor for Arial (1.154) + cushion

DEGREE_NAMES = {
    "BEng": "Bachelor of Engineering",
    "BS": "Bachelor of Science", "BSc": "Bachelor of Science",
    "BA": "Bachelor of Arts",
    "MEng": "Master of Engineering",
    "MS": "Master of Science", "MSc": "Master of Science",
    "MBA": "Master of Business Administration",
    "PhD": "Doctor of Philosophy",
}

SECTION_TITLES = {
    "en": {
        "summary": "Summary",
        "experience": "Experience",
        "projects": "Projects & Consulting",
        "skills": "Skills",
        "education": "Education",
    },
    "es": {
        "summary": "Resumen",
        "experience": "Experiencia",
        "projects": "Proyectos y Consultoría",
        "skills": "Habilidades",
        "education": "Educación",
    },
}

# --------------------------------------------------- Helvetica width metrics
# Arial/Helvetica advance widths per 1000 units of font size (AFM values).
_W = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667,
    "'": 191, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, "0": 556, "1": 556, "2": 556, "3": 556, "4": 556,
    "5": 556, "6": 556, "7": 556, "8": 556, "9": 556, ":": 278, ";": 278,
    "<": 584, "=": 584, ">": 584, "?": 556, "@": 1015, "A": 667, "B": 667,
    "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722, "I": 278,
    "J": 500, "K": 667, "L": 556, "M": 833, "N": 722, "O": 778, "P": 667,
    "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944,
    "X": 667, "Y": 667, "Z": 611, "[": 278, "\\": 278, "]": 278, "^": 469,
    "_": 556, "`": 333, "a": 556, "b": 556, "c": 500, "d": 556, "e": 556,
    "f": 278, "g": 556, "h": 556, "i": 222, "j": 222, "k": 500, "l": 222,
    "m": 833, "n": 556, "o": 556, "p": 556, "q": 556, "r": 333, "s": 500,
    "t": 278, "u": 556, "v": 500, "w": 722, "x": 500, "y": 500, "z": 500,
    "{": 334, "|": 260, "}": 334, "~": 584,
}
_W_BOLD_DELTA = 1.08  # bold runs ~8% wider on average


def _text_width_pts(text: str, size: float, bold: bool = False) -> float:
    total = 0
    for ch in text:
        total += _W.get(ch, 556)
    w = total / 1000.0 * size
    return w * (_W_BOLD_DELTA if bold else 1.0) * 1.03  # 3% safety margin


def _wrap_info(text: str, size: float, avail_pts: float, bold: bool = False):
    """Greedy word-wrap: returns (line_count, last_line_fill_ratio)."""
    if not text:
        return 1, 0.0
    space_w = _text_width_pts(" ", size, bold)
    lines, cur = 1, 0.0
    for word in text.split():
        w = _text_width_pts(word, size, bold)
        if cur == 0.0:
            cur = w
        elif cur + space_w + w <= avail_pts:
            cur += space_w + w
        else:
            lines += 1
            cur = w
    return lines, cur / avail_pts


def _wrapped_lines(text: str, size: float, avail_pts: float, bold: bool = False) -> int:
    return _wrap_info(text, size, avail_pts, bold)[0]


# ------------------------------------------------------------- docx plumbing

def _run(p, text, size, color, bold=False, italic=False, caps=False):
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor.from_string(color)
    r.bold = bold
    r.italic = italic
    if caps:
        rpr = r._element.get_or_add_rPr()
        rpr.append(OxmlElement("w:caps"))
    return r


def _hyperlink(p, text, url, size, color=NAVY):
    part = p.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), r_id)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    fonts = OxmlElement("w:rFonts")
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(a), "Arial")
    rpr.append(fonts)
    c = OxmlElement("w:color")
    c.set(qn("w:val"), color)
    rpr.append(c)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(int(size * 2)))
    rpr.append(sz)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)
    h.append(r)
    p._p.append(h)


def _spacing(p, before=None, after=None):
    pf = p.paragraph_format
    pf.line_spacing = 1.0  # single, as in the reference (kills template's 1.08)
    if before is not None:
        pf.space_before = Pt(before)
    if after is not None:
        pf.space_after = Pt(after)


def _right_tab(p):
    tabs = p.paragraph_format.tab_stops
    from docx.enum.text import WD_TAB_ALIGNMENT
    tabs.add_tab_stop(Twips(RIGHT_TAB), WD_TAB_ALIGNMENT.RIGHT)


def _keep_next(p):
    ppr = p._p.get_or_add_pPr()
    ppr.insert(0, OxmlElement("w:keepNext"))


def _bottom_border(p):
    ppr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single")
    b.set(qn("w:color"), NAVY)
    b.set(qn("w:sz"), "6")
    b.set(qn("w:space"), "2")
    pbdr.append(b)
    ppr.append(pbdr)


def _bullet(p):
    pf = p.paragraph_format
    pf.left_indent = Twips(BULLET_LEFT)
    pf.first_line_indent = Twips(-BULLET_HANG)
    from docx.enum.text import WD_TAB_ALIGNMENT
    pf.tab_stops.add_tab_stop(Twips(BULLET_LEFT), WD_TAB_ALIGNMENT.LEFT)


# ---------------------------------------------------------------- data model

MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _fmt_date(v) -> str:
    if v is None or v == "":
        return "Present"
    s = str(v)
    m = re.match(r"^(\d{4})-(\d{2})", s)
    if m:
        return f"{MONTHS[int(m.group(2))]} {m.group(1)}"
    return s


def _no_emdash(s: str) -> str:
    return s.replace("—", ", ")


def _degree(entry) -> str:
    deg = entry.get("degree", "")
    area = entry.get("area", "")
    full = DEGREE_NAMES.get(deg, deg)
    if full and area:
        return f"{full} in {area}"
    return full or area


def _project_title(name: str):
    """'Pragma AI (Co-Founder)' -> ('Pragma AI', 'Co-Founder')."""
    m = re.match(r"^(.*?)\s*\((.*)\)\s*$", name)
    if m:
        return m.group(1), m.group(2)
    return name, None


def _contact_items(cv):
    items = []  # (text, kind) kind: text|email|linkedin
    if cv.get("phone"):
        items.append((str(cv["phone"]).replace("-", " "), "text"))
    if cv.get("email"):
        items.append((cv["email"], "email"))
    for sn in cv.get("social_networks", []) or []:
        if sn.get("network", "").lower() == "linkedin":
            items.append((f"linkedin.com/in/{sn['username']}", "linkedin"))
    if cv.get("location"):
        items.append((cv["location"], "text"))
    for extra in cv.get("contact_extras", []) or []:
        items.append((extra, "text"))
    # surface TN Visa eligibility in the header if declared in additional
    for a in (cv.get("sections", {}).get("additional") or []):
        if "work" in a.get("label", "").lower() and "tn visa" in a.get("details", "").lower():
            if not any("tn " in t.lower() or "tn-" in t.lower() for t, _ in items):   # header may already say "TN eligible"
                items.append(("TN Visa Eligible", "text"))
    return items


# ------------------------------------------------------------------ renderer

def build(data: dict, level: int, lang: str = "en") -> DocumentType:
    cv = data["cv"]
    sections = cv.get("sections", {})
    titles = SECTION_TITLES.get(lang, SECTION_TITLES["en"])
    L = level

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Arial"
    st.font.size = Pt(FS["summary"][L])
    sect = doc.sections[0]
    sect.page_width = Twips(PAGE_W)
    sect.page_height = Twips(PAGE_H)
    sect.top_margin = sect.bottom_margin = Twips(MARGIN_TB)
    sect.left_margin = sect.right_margin = Twips(MARGIN_LR)

    def para(align=None):
        p = doc.add_paragraph()
        if align is not None:
            p.alignment = align
        return p

    def section_header(title):
        p = para()
        _spacing(p, before=SP["sect_before"][L], after=SP["sect_after"][L])
        _bottom_border(p)
        _keep_next(p)
        _run(p, title, FS["section"][L], NAVY, bold=True, caps=True)

    # name
    p = para(WD_ALIGN_PARAGRAPH.CENTER)
    _spacing(p, after=SP["name_after"][L])
    _run(p, cv["name"], FS["name"][L], NAVY, bold=True, caps=True)

    # contact line
    p = para(WD_ALIGN_PARAGRAPH.CENTER)
    _spacing(p, after=SP["contact_after"][L])
    items = _contact_items(cv)
    for i, (text, kind) in enumerate(items):
        if i:
            _run(p, "  |  ", FS["contact"][L], LIGHT)
        if kind == "email":
            _hyperlink(p, text, f"mailto:{text}", FS["contact"][L])
        elif kind == "linkedin":
            _hyperlink(p, text, f"https://www.{text}", FS["contact"][L])
        else:
            _run(p, text, FS["contact"][L], GRAY)

    # summary
    if sections.get("summary"):
        section_header(titles["summary"])
        for s in sections["summary"]:
            p = para(WD_ALIGN_PARAGRAPH.JUSTIFY)
            _spacing(p, after=SP["body_after"][L])
            _run(p, _no_emdash(s), FS["summary"][L], DARK)

    # experience
    if sections.get("experience"):
        section_header(titles["experience"])
        for job in sections["experience"]:
            p = para()
            _spacing(p, before=SP["comp_before"][L], after=0)
            _keep_next(p)
            _right_tab(p)
            _run(p, job["company"], FS["company"][L], BLACK, bold=True)
            dates = f"{_fmt_date(job.get('start_date'))} – {_fmt_date(job.get('end_date'))}"
            _run(p, "\t" + dates, FS["body"][L], GRAY)

            p = para()
            _spacing(p, before=0, after=SP["body_after"][L])
            _keep_next(p)
            _right_tab(p)
            _run(p, job.get("position", ""), FS["body"][L], NAVY, italic=True)
            if job.get("location"):
                _run(p, "\t" + job["location"], FS["body"][L], GRAY, italic=True)

            for h in job.get("highlights", []) or []:
                p = para()
                _spacing(p, after=SP["body_after"][L])
                _bullet(p)
                _run(p, "•\t" + _no_emdash(h), FS["body"][L], DARK)

    # projects
    if sections.get("projects"):
        section_header(titles["projects"])
        for proj in sections["projects"]:
            name, role = _project_title(proj["name"])
            p = para()
            _spacing(p, before=SP["proj_before"][L], after=SP["proj_after"][L])
            _keep_next(p)
            _right_tab(p)
            _run(p, name, FS["company"][L], BLACK, bold=True)
            date = str(proj.get("date", "")).replace(" - ", " – ").replace("--", "–")
            tag = f"{role} · {date}" if role else date
            if tag.strip():
                _run(p, "\t" + tag, FS["projdate"][L], GRAY, italic=True)
            for h in proj.get("highlights", []) or []:
                p = para(WD_ALIGN_PARAGRAPH.JUSTIFY)
                _spacing(p, after=SP["body_after"][L])
                _run(p, _no_emdash(h), FS["body"][L], DARK)

    # skills
    if sections.get("skills"):
        section_header(titles["skills"])
        for sk in sections["skills"]:
            p = para()
            _spacing(p, after=SP["body_after"][L])
            _run(p, f"{sk['label']}: ", FS["body"][L], NAVY, bold=True)
            _run(p, _no_emdash(sk["details"]), FS["body"][L], DARK)

    # education (+ additional merged in, reference style)
    edu = sections.get("education") or []
    extra = sections.get("additional") or []
    if edu or extra:
        section_header(titles["education"])
        for e in edu:
            p = para()
            _spacing(p, after=SP["body_after"][L])
            _run(p, f"{e['institution']}: ", FS["body"][L], NAVY, bold=True)
            details = _degree(e)
            if e.get("start_date") or e.get("end_date"):
                details += f" ({_fmt_date(e.get('start_date'))} – {_fmt_date(e.get('end_date'))})"
            _run(p, details, FS["body"][L], DARK)
        for a in extra:
            if "work" in a.get("label", "").lower() and "tn visa" in a.get("details", "").lower():
                continue  # already surfaced in the contact line
            p = para()
            _spacing(p, after=SP["body_after"][L])
            _run(p, f"{a['label']}: ", FS["body"][L], NAVY, bold=True)
            _run(p, _no_emdash(a["details"]), FS["body"][L], DARK)

    return doc


# ------------------------------------------------------------ height estimate

def estimate_height_pts(data: dict, level: int) -> float:
    """Estimated content height in points (page allows PAGE_H - 2*MARGIN_TB)."""
    cv = data["cv"]
    sections = cv.get("sections", {})
    L = level
    avail = (PAGE_W - 2 * MARGIN_LR) / 20.0          # content width, points
    avail_bullet = avail - BULLET_LEFT / 20.0
    h = 0.0

    def block(lines, size, before=0.0, after=0.0):
        nonlocal h
        h += before + lines * size * LINE + after

    block(1, FS["name"][L], after=SP["name_after"][L])
    contact = "  |  ".join(t for t, _ in _contact_items(cv))
    block(_wrapped_lines(contact, FS["contact"][L], avail), FS["contact"][L],
          after=SP["contact_after"][L])

    def header():
        block(1, FS["section"][L], before=SP["sect_before"][L],
              after=SP["sect_after"][L] + 1.0)  # +1pt for border offset

    if sections.get("summary"):
        header()
        for s in sections["summary"]:
            block(_wrapped_lines(s, FS["summary"][L], avail), FS["summary"][L],
                  after=SP["body_after"][L])
    if sections.get("experience"):
        header()
        for job in sections["experience"]:
            block(1, FS["company"][L], before=SP["comp_before"][L])
            block(1, FS["body"][L], after=SP["body_after"][L])
            for hl in job.get("highlights", []) or []:
                block(_wrapped_lines(hl, FS["body"][L], avail_bullet),
                      FS["body"][L], after=SP["body_after"][L])
    if sections.get("projects"):
        header()
        for proj in sections["projects"]:
            block(1, FS["company"][L], before=SP["proj_before"][L],
                  after=SP["proj_after"][L])
            for hl in proj.get("highlights", []) or []:
                block(_wrapped_lines(hl, FS["body"][L], avail), FS["body"][L],
                      after=SP["body_after"][L])
    if sections.get("skills"):
        header()
        for sk in sections["skills"]:
            txt = f"{sk['label']}: {sk['details']}"
            block(_wrapped_lines(txt, FS["body"][L], avail), FS["body"][L],
                  after=SP["body_after"][L])
    edu = sections.get("education") or []
    extra = [a for a in (sections.get("additional") or [])
             if not ("work" in a.get("label", "").lower()
                     and "tn visa" in a.get("details", "").lower())]
    if edu or extra:
        header()
        for _ in edu:
            block(1, FS["body"][L], after=SP["body_after"][L])
        for a in extra:
            txt = f"{a['label']}: {a['details']}"
            block(_wrapped_lines(txt, FS["body"][L], avail), FS["body"][L],
                  after=SP["body_after"][L])
    return h


PAGE_AVAIL_PTS = (PAGE_H - 2 * MARGIN_TB) / 20.0

# line-fill audit thresholds
MIN_LAST_LINE_FILL = 0.70   # wrapped paragraphs: last line should be at least this full
MIN_SINGLE_LINE_FILL = 0.55  # one-line bullets shorter than this suggest merging


def audit_line_fill(data: dict, level: int) -> list[str]:
    """Report paragraphs whose last line leaves too much trailing white space.

    For each flagged block, estimates how many characters to CUT to drop the
    dangling line entirely, and how many could be ADDED (of real content only)
    to fill the line. The goal is full-width lines, not padded prose.
    """
    cv = data["cv"]
    sections = cv.get("sections", {})
    L = level
    avail = (PAGE_W - 2 * MARGIN_LR) / 20.0
    avail_bullet = avail - BULLET_LEFT / 20.0
    findings: list[str] = []

    def check(where, text, size, width_pts):
        lines, fill = _wrap_info(text, size, width_pts)
        avg_char = _text_width_pts("n", size)
        if lines == 1:
            if fill < MIN_SINGLE_LINE_FILL:
                findings.append(
                    f"[{where}] 1 line only {fill:.0%} full: merge into a sibling bullet "
                    f"or expand with ~{int((width_pts * 0.95 - fill * width_pts) / avg_char)} chars of real content")
        elif fill < MIN_LAST_LINE_FILL:
            cut = int(fill * width_pts / avg_char)
            add = int((width_pts * 0.95 - fill * width_pts) / avg_char)
            findings.append(
                f"[{where}] {lines} lines, last line {fill:.0%} full: "
                f"cut ~{cut} chars to save a line, or add ~{add} chars of real content "
                f"| ...{text[-60:]!r}")

    for s in sections.get("summary", []) or []:
        check("summary", s, FS["summary"][L], avail)
    for job in sections.get("experience", []) or []:
        for i, h in enumerate(job.get("highlights", []) or [], 1):
            check(f"{job['company']} b{i}", h, FS["body"][L], avail_bullet)
    for proj in sections.get("projects", []) or []:
        for i, h in enumerate(proj.get("highlights", []) or [], 1):
            check(f"{proj['name']} p{i}", h, FS["body"][L], avail)
    for sk in sections.get("skills", []) or []:
        check(f"skills:{sk['label']}", f"{sk['label']}: {sk['details']}",
              FS["body"][L], avail)
    return findings


def pick_fit_level(data: dict) -> int:
    for lvl in range(4):
        if estimate_height_pts(data, lvl) <= PAGE_AVAIL_PTS:
            return lvl
    return 3


# ------------------------------------------------------------------- pdf/cli

def to_pdf(docx_path: Path) -> Path | None:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return None
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf",
         "--outdir", str(docx_path.parent), str(docx_path)],
        check=True, capture_output=True, timeout=120,
    )
    pdf = docx_path.with_suffix(".pdf")
    return pdf if pdf.exists() else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("yaml_path")
    ap.add_argument("-o", "--output", help="output .docx (default: alongside yaml)")
    ap.add_argument("--fit", default="auto", choices=["auto", "0", "1", "2", "3"])
    ap.add_argument("--lang", default=None, choices=["en", "es"],
                    help="section-title language (default: cv.language in the yaml, else en)")
    ap.add_argument("--pdf", action="store_true",
                    help="also convert to PDF via LibreOffice if installed")
    ap.add_argument("--audit", action="store_true",
                    help="report paragraphs whose last line leaves trailing white space")
    args = ap.parse_args(argv)

    src = Path(args.yaml_path)
    data = yaml.safe_load(src.read_text())
    if "cv" not in data:
        sys.exit("error: yaml has no top-level 'cv' key")

    lang = args.lang or data["cv"].get("language", "en")
    level = pick_fit_level(data) if args.fit == "auto" else int(args.fit)
    est = estimate_height_pts(data, level)
    doc = build(data, level, lang)

    out = Path(args.output) if args.output else src.with_suffix(".docx")
    doc.save(str(out))
    pct = est / PAGE_AVAIL_PTS * 100
    print(f"wrote {out}  (fit level {level}, est. height {est:.0f}/{PAGE_AVAIL_PTS:.0f}pt = {pct:.0f}% of page)")
    if pct > 102:
        print("WARNING: content likely exceeds one page even at max compression; trim bullets.")
    elif pct > 100:
        print("NOTE: estimate is borderline (estimator runs ~2% conservative); verify page count.")

    if args.audit:
        findings = audit_line_fill(data, level)
        if findings:
            print(f"\nline-fill audit ({len(findings)} block(s) with trailing white space):")
            for f in findings:
                print("  " + f)
            print("fix by tightening or extending REAL content only; never pad with filler.")
        else:
            print("line-fill audit: clean, all paragraphs end near full width.")

    if args.pdf:
        pdf = to_pdf(out)
        print(f"wrote {pdf}" if pdf else "PDF skipped: LibreOffice (soffice) not found")


if __name__ == "__main__":
    main()
