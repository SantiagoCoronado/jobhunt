"""The deterministic half of `/jh-setup` (docs/spec-pre-release.md decisions 6, 7, 14).

    python -m src.onboard extract <files...>     text of each document into data/onboard/, one line of sizes each
    python -m src.onboard check resume [--file P]   validate a master resume (schema, dates, the renderer)
    python -m src.onboard check profile [--file P]  validate a profile (the prompt keys, the keys the pipeline reads)

The agent runs the interview; this module does everything that has a right answer. `extract`
reads PDF (pypdf), docx (python-docx), md, txt, csv and LinkedIn's data-export zip (only the
csv files a resume is made of, never messages or connections) and writes one text file per
document under `data/onboard/`, plus `manifest.json`, the list of documents the provenance of
every resume entry points at. Each document's line carries its size in characters and an
estimated token count (characters / 4) so the agent can refuse a 40-page PDF and ask for the
relevant pages before reading it (decision 14).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import ROOT, user_file

ONBOARD_DIR = ROOT / "data" / "onboard"      # resolved at call time; tests point it at a temp dir
MANIFEST = "manifest.json"
KINDS = {".pdf": "pdf", ".docx": "docx", ".md": "md", ".markdown": "md", ".txt": "txt", ".csv": "csv",
         ".zip": "linkedin-export"}
LARGE_TOKENS = 15_000          # a document above this is refused until the user points at the pages
INTERVIEW = "interview"        # the provenance of a fact the user typed in the chat

# The csv files of LinkedIn's data export that a resume is made of. Everything else in the zip
# (messages, connections, invitations, ad targeting) is never read.
LINKEDIN_CSVS: tuple[str, ...] = (
    "Profile", "Positions", "Education", "Skills", "Projects", "Certifications", "Languages",
    "Honors", "Courses", "Publications", "Volunteering",
)


def tokens(chars: int) -> int:
    """The estimate every size line uses: four characters a token, rounded up."""
    return (chars + 3) // 4


# ---- extract ------------------------------------------------------------------------------

@dataclass
class Document:
    id: str              # the name provenance cites: the file's own name
    source: str          # where it was read from
    kind: str
    text: str            # the extracted text file, relative to the repo root when inside it
    chars: int
    tokens: int
    pages: int | None = None
    note: str = ""

    @property
    def large(self) -> bool:
        return self.tokens > LARGE_TOKENS


def _pdf_text(path: Path) -> tuple[str, int]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as e:  # noqa: BLE001, pypdf raises several types for a locked file
            raise ValueError(f"{path.name}: the PDF is password protected ({e})") from None
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n\n".join(f"[page {i}]\n{t}" for i, t in enumerate(pages, 1) if t)
    return text, len(reader.pages)


def _docx_text(path: Path) -> str:
    from docx import Document as Docx

    doc = Docx(str(path))
    lines = [p.text for p in doc.paragraphs]
    for table in doc.tables:                       # a two-column resume template is often a table
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells]
            lines.append(" | ".join(dict.fromkeys(c for c in cells if c)))
    return "\n".join(ln.rstrip() for ln in lines).strip()


def _csv_rows(text: str) -> str:
    """A csv as `key: value` lines, one blank line between rows, empty cells left out."""
    rows = list(csv.DictReader(io.StringIO(text)))
    out: list[str] = []
    for row in rows:
        lines = [f"{k.strip()}: {' '.join(str(v).split())}" for k, v in row.items() if k and v and str(v).strip()]
        if lines:
            out.append("\n".join(lines))
    return "\n\n".join(out)


def _linkedin_zip_text(path: Path) -> tuple[str, str]:
    """The resume csv files of a LinkedIn data export, one `## <name>` section each. Returns
    (text, note naming what was read)."""
    with zipfile.ZipFile(path) as z:
        members = {Path(n).stem: n for n in z.namelist() if n.lower().endswith(".csv")}
        found = [name for name in LINKEDIN_CSVS if name in members]
        if not found:
            raise ValueError(f"{path.name}: no LinkedIn profile csv in the zip (expected {', '.join(LINKEDIN_CSVS[:3])}, ...)")
        parts = []
        for name in found:
            body = _csv_rows(z.read(members[name]).decode("utf-8-sig", errors="replace"))
            if body:
                parts.append(f"## {name}\n{body}")
    return "\n\n".join(parts), f"read {', '.join(found)}; skipped {len(members) - len(found)} other csv files"


def read_document(path: Path) -> tuple[str, str, int | None, str]:
    """(kind, text, pages, note) of one document. Raises ValueError for a kind it cannot read."""
    kind = KINDS.get(path.suffix.lower())
    if kind is None:
        raise ValueError(f"{path.name}: unsupported type {path.suffix or '(none)'} "
                         f"(reads {', '.join(sorted(set(KINDS)))}; save a .doc as .docx or PDF)")
    if kind == "pdf":
        text, pages = _pdf_text(path)
        note = "" if text else "no text layer (a scanned PDF?); export it as a text PDF or paste the text"
        return kind, text, pages, note
    if kind == "docx":
        return kind, _docx_text(path), None, ""
    if kind == "linkedin-export":
        text, note = _linkedin_zip_text(path)
        return kind, text, None, note
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    return kind, (_csv_rows(raw) if kind == "csv" else raw.strip()), None, ""


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "document"


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_manifest() -> list[Document]:
    path = ONBOARD_DIR / MANIFEST
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Document(**d) for d in raw.get("documents") or []]


def save_manifest(docs: list[Document]) -> None:
    ONBOARD_DIR.mkdir(parents=True, exist_ok=True)
    (ONBOARD_DIR / MANIFEST).write_text(json.dumps({"documents": [asdict(d) for d in docs]}, indent=2) + "\n",
                                        encoding="utf-8")


def document_ids() -> list[str]:
    return [d.id for d in load_manifest()]


def _unique_id(name: str, source: str, docs: list[Document]) -> str:
    """The file's own name, unless another file of that name was read already."""
    taken = {d.id: d.source for d in docs}
    if taken.get(name, source) == source:
        return name
    stem, suffix = Path(name).stem, Path(name).suffix
    n = 2
    while f"{stem}-{n}{suffix}" in taken and taken[f"{stem}-{n}{suffix}"] != source:
        n += 1
    return f"{stem}-{n}{suffix}"


def record(doc_id: str, source: str, kind: str, text: str, pages: int | None = None, note: str = "") -> Document:
    """Write one document's text under data/onboard/ and put it in the manifest (replacing an
    earlier read of the same document)."""
    docs = load_manifest()
    out = ONBOARD_DIR / f"{_slug(doc_id)}.txt"
    ONBOARD_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    doc = Document(doc_id, source, kind, _rel(out), len(text), tokens(len(text)), pages, note)
    docs = [d for d in docs if d.id != doc_id] + [doc]
    save_manifest(docs)
    return doc


def extract(paths: list[Path]) -> tuple[list[Document], list[str]]:
    """Read every document; returns (the documents written, one error line per file that failed)."""
    done: list[Document] = []
    errors: list[str] = []
    for path in paths:
        if not path.is_file():
            errors.append(f"{path}: no such file")
            continue
        try:
            kind, text, pages, note = read_document(path)
        except (ValueError, zipfile.BadZipFile, OSError) as e:
            errors.append(str(e) if path.name in str(e) else f"{path.name}: {e}")
            continue
        except Exception as e:  # noqa: BLE001, a malformed PDF or docx raises the library's own types
            errors.append(f"{path.name}: could not be read ({type(e).__name__}: {e})")
            continue
        source = str(path.resolve())
        doc_id = _unique_id(path.name, source, load_manifest())
        done.append(record(doc_id, source, kind, text, pages, note))
    return done, errors


def size_line(doc: Document) -> str:
    pages = f", {doc.pages} page{'s' if doc.pages != 1 else ''}" if doc.pages is not None else ""
    line = f"  {doc.id:32s} {doc.kind:15s} {doc.chars:>7,} chars  ~{doc.tokens:,} tokens{pages}  -> {doc.text}"
    if doc.large:
        line += (f"\n    ! large: over {LARGE_TOKENS:,} tokens; ask for the pages that matter "
                 "(the resume part, the last roles) before reading it")
    if doc.note:
        line += f"\n    {doc.note}"
    return line


# ---- check --------------------------------------------------------------------------------

EM_DASH = "—"
RESUME_SECTIONS = ("summary", "experience", "projects", "skills", "education", "additional")
_DATE = re.compile(r"^\d{4}(-\d{2})?$")
_PRESENT = ("present", "current", "now", "")


def _strings(value, where: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(s, str) and s.strip() for s in value):
        errors.append(f"{where} must be a list of non-empty strings")
        return []
    return value


def _date_ok(value, end: bool) -> bool:
    if value is None:
        return end
    s = str(value).strip()
    return bool(_DATE.match(s)) or (end and s.lower() in _PRESENT)


def _entries(sections: dict, name: str, required: tuple[str, ...], errors: list[str]) -> list[dict]:
    raw = sections.get(name)
    if raw is None:
        return []
    if not isinstance(raw, list):
        errors.append(f"cv.sections.{name} must be a list")
        return []
    out = []
    for i, e in enumerate(raw):
        where = f"cv.sections.{name}[{i}]"
        if not isinstance(e, dict):
            errors.append(f"{where} must be a mapping")
            continue
        for key in required:
            if not str(e.get(key) or "").strip():
                errors.append(f"{where} needs `{key}`")
        out.append(e)
    return out


def _emdash_paths(value, where: str = "") -> list[str]:
    if isinstance(value, str):
        return [where or "(top)"] if EM_DASH in value else []
    if isinstance(value, dict):
        return [p for k, v in value.items() for p in _emdash_paths(v, f"{where}.{k}" if where else str(k))]
    if isinstance(value, list):
        return [p for i, v in enumerate(value) for p in _emdash_paths(v, f"{where}[{i}]")]
    return []


def resume_errors(data) -> list[str]:
    """Every way `data` is not a master resume `src.render_docx` and the tailor can use; [] = ok."""
    if not isinstance(data, dict) or not isinstance(data.get("cv"), dict):
        return ["the file needs a top-level `cv:` mapping"]
    cv = data["cv"]
    errors: list[str] = []
    for key in ("name", "location"):
        if not isinstance(cv.get(key), str) or not cv[key].strip():
            errors.append(f"cv.{key} is required")
    for key in ("email", "phone"):
        if cv.get(key) is not None and not isinstance(cv[key], str):
            errors.append(f"cv.{key} must be a string (quote a phone number)")
    for i, sn in enumerate(cv.get("social_networks") or []):
        if not isinstance(sn, dict) or not sn.get("network") or not sn.get("username"):
            errors.append(f"cv.social_networks[{i}] needs `network` and `username`")
    sections = cv.get("sections")
    if not isinstance(sections, dict):
        return errors + ["cv.sections is required (summary, experience, projects, skills, education, additional)"]
    unknown = sorted(set(sections) - set(RESUME_SECTIONS))
    if unknown:
        errors.append(f"cv.sections has unknown section(s) {', '.join(unknown)} "
                      f"(known: {', '.join(RESUME_SECTIONS)})")
    if sections.get("summary") is not None:
        _strings(sections["summary"], "cv.sections.summary", errors)
    if not sections.get("experience") and not sections.get("projects"):
        errors.append("cv.sections needs at least one experience or project entry")
    for kind, required in (("experience", ("company", "position")), ("projects", ("name",))):
        for i, e in enumerate(_entries(sections, kind, required, errors)):
            where = f"cv.sections.{kind}[{i}]"
            if e.get("highlights") is not None:
                _strings(e["highlights"], f"{where}.highlights", errors)
            if kind == "experience":
                if not _date_ok(e.get("start_date"), end=False):
                    errors.append(f"{where}.start_date must be YYYY-MM or YYYY, got {e.get('start_date')!r}")
                if not _date_ok(e.get("end_date"), end=True):
                    errors.append(f"{where}.end_date must be YYYY-MM, YYYY or present, got {e.get('end_date')!r}")
    for i, e in enumerate(_entries(sections, "education", ("institution",), errors)):
        for key in ("start_date", "end_date"):
            if e.get(key) is not None and not _date_ok(e.get(key), end=key == "end_date"):
                errors.append(f"cv.sections.education[{i}].{key} must be YYYY-MM or YYYY, got {e.get(key)!r}")
    for kind in ("skills", "additional"):
        _entries(sections, kind, ("label", "details"), errors)
    errors += [f"{p} contains an em-dash (U+2014); use a comma, colon or period" for p in _emdash_paths(data)]
    if not errors:                     # the renderer is the loader the tailor relies on: it must build
        from . import render_docx

        try:
            render_docx.build(data, 0)
        except Exception as e:  # noqa: BLE001, any failure here is a resume the tailor cannot render
            errors.append(f"src.render_docx could not build it: {type(e).__name__}: {e}")
    return errors


def resume_counts(data: dict) -> dict[str, int]:
    sections = (data.get("cv") or {}).get("sections") or {}
    skills = 0
    for group in sections.get("skills") or []:
        skills += len([s for s in re.split(r"[,;]", str(group.get("details") or "")) if s.strip()])
    return {"roles": len(sections.get("experience") or []), "projects": len(sections.get("projects") or []),
            "skills": skills, "education": len(sections.get("education") or [])}


# The keys the pipeline reads from a profile beyond the four prompt keys `config.profile`
# validates: (key, the type it must be).
PROFILE_REQUIRED: tuple[tuple[str, type], ...] = (
    ("name", str), ("target_titles", list), ("locations", list), ("location_rule", str),
    ("dealbreakers", list), ("comp", dict), ("shortlist_threshold", int),
)
_KIND = {str: "a string", list: "a list", dict: "a mapping", int: "a whole number"}
PROFILE_EXAMPLE = ROOT / "config" / "profile.example.yaml"


def example_keys(raw: dict, example: Path | None = None) -> list[str]:
    """The top-level keys whose value is still the example's (Alex Example's), in file order."""
    import yaml

    path = example or PROFILE_EXAMPLE
    if not path.exists():
        return []
    ex = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [k for k, v in raw.items() if k in ex and ex[k] == v]


def profile_errors(raw) -> list[str]:
    """Every way `raw` is not a profile the pipeline can run on; [] = ok."""
    from .config import missing_profile_keys, profile

    if not isinstance(raw, dict):
        return ["the file must be a mapping of keys"]
    errors: list[str] = []
    for key, kind in PROFILE_REQUIRED:
        val = raw.get(key)
        if val is None or (kind is not int and not val):
            errors.append(f"{key} is required")
        elif not isinstance(val, kind) or (kind is int and isinstance(val, bool)):
            errors.append(f"{key} must be {_KIND[kind]}")
    try:
        profile(raw)
    except ValueError as e:
        errors.append(str(e).removeprefix("config/profile.yaml: "))
    errors += [f"{k} is missing (python -m src.init appends a default)" for k in missing_profile_keys(raw)]
    errors += [f"{p} contains an em-dash (U+2014)" for p in _emdash_paths(raw)]
    return errors


def _load(path: Path):
    import yaml

    if not path.exists():
        raise FileNotFoundError(f"{_rel(path)} does not exist (python -m src.init creates it)")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ValueError(f"{_rel(path)} is not valid YAML: {e}") from None


def check(what: str, path: Path | None = None) -> int:
    path = path or user_file("master_resume" if what == "resume" else "profile")
    try:
        data = _load(path)
    except (FileNotFoundError, ValueError) as e:
        print(f"  ! {e}")
        return 1
    errors = resume_errors(data) if what == "resume" else profile_errors(data)
    for line in errors:
        print(f"  ! {line}")
    if errors:
        print(f"{what} has {len(errors)} problem{'s' if len(errors) != 1 else ''}: {_rel(path)}")
        return 1
    if what == "resume":
        c = resume_counts(data)
        print(f"resume ok: {c['roles']} roles, {c['projects']} projects, {c['skills']} skills, "
              f"{c['education']} education  ({_rel(path)})")
    else:
        left = example_keys(data)
        if left:
            print(f"  example  still the example's value: {', '.join(left)}")
        print(f"profile ok ({_rel(path)})")
    return 0


# ---- CLI ----------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("extract", help="text of each document into data/onboard/, with sizes")
    p.add_argument("files", nargs="+", type=Path)
    p = sub.add_parser("check", help="validate the master resume or the profile")
    p.add_argument("what", choices=("resume", "profile"))
    p.add_argument("--file", type=Path, help="check this file instead of the real one")
    args = ap.parse_args(argv)

    if args.cmd == "extract":
        docs, errors = extract(args.files)
        for doc in docs:
            print(size_line(doc))
        for e in errors:
            print(f"  ! {e}")
        total = sum(d.tokens for d in docs)
        print(f"extracted {len(docs)} of {len(args.files)} document{'s' if len(args.files) != 1 else ''}, "
              f"~{total:,} tokens in all; read each text file once")
        return 1 if errors else 0
    if args.cmd == "check":
        return check(args.what, args.file)
    return 2


if __name__ == "__main__":
    sys.exit(main())
