"""The deterministic half of `/jh-setup` (docs/spec-pre-release.md decisions 6, 7, 14).

    python -m src.onboard extract <files...>     text of each document into data/onboard/, one line of sizes each
    python -m src.onboard check resume [--file P]   validate a master resume (schema, dates, the renderer)
    python -m src.onboard check profile [--file P]  validate a profile (the prompt keys, the keys the pipeline reads)
    python -m src.onboard write {resume|profile|sources|env|dream} <json | file | -> [--yes]
                                                 validate, then write; a hand-edited file shows its diff and waits for --yes
    python -m src.onboard sources                the sources the profile's regions turn on, their keys and targeting
    python -m src.onboard verify-token <source> <token>   one live request: 200 and a non-empty board
    python -m src.onboard linkedin <url>         opt-in: the public profile page, one GET, no login (fragile)
    python -m src.onboard summary                what was read and written where, the interview's closing facts

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


# ---- write --------------------------------------------------------------------------------
#
# Every file the interview produces is written here, never by the agent's own edit tool. Each
# writer validates first and writes nothing on a problem. The show-diff-and-ask rule: a file
# that differs from both its tracked example (a fresh `src.init` copy) and the last version this
# helper wrote was edited by hand, so the writer prints the diff and stops (exit 3) until the
# call is repeated with `--yes` after the user agreed. The replaced version is kept under
# data/onboard/backup/. `data/onboard/written.json` holds the hash of what was last written.

WRITTEN = "written.json"
PROVENANCE = "provenance.json"
NEEDS_YES = 3
DIFF_LINES = 120
EXAMPLES = {
    "profile": ROOT / "config" / "profile.example.yaml",
    "master_resume": ROOT / "resume" / "master_resume.example.yaml",
    "sources_local": ROOT / "config" / "sources.local.example.yaml",
}


class Refused(Exception):
    """A write that did not happen: the message says why; `code` is the exit code."""

    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


def _sha(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _written() -> dict[str, str]:
    path = ONBOARD_DIR / WRITTEN
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def diff(old: str, new: str, name: str) -> str:
    import difflib

    lines = list(difflib.unified_diff(old.splitlines(), new.splitlines(), f"a/{name}", f"b/{name}", lineterm=""))
    if len(lines) > DIFF_LINES:
        lines = lines[:DIFF_LINES] + [f"... {len(lines) - DIFF_LINES} more diff lines"]
    return "\n".join(lines)


def hand_edited(path: Path, kind: str) -> bool:
    """True when the file exists and is neither its example nor what this helper last wrote."""
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    example = EXAMPLES.get(kind)
    if example is not None and example.exists() and example.read_text(encoding="utf-8") == text:
        return False
    return _written().get(_rel(path)) != _sha(text)


def commit_file(path: Path, kind: str, text: str, yes: bool) -> str:
    """Write `text` to `path` under the show-diff-and-ask rule. Returns "written" or
    "unchanged"; raises Refused(code=3) with the diff when the user must be asked first."""
    from datetime import datetime

    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == text:
        return "unchanged"
    if old is not None and hand_edited(path, kind) and not yes:
        raise Refused(f"{diff(old, text, _rel(path))}\n  ! {_rel(path)} was edited since onboarding last wrote it; "
                      "show the user this diff and repeat the call with --yes once they agree", NEEDS_YES)
    if old is not None:
        backup = ONBOARD_DIR / "backup" / f"{path.name}.{datetime.now():%Y%m%d-%H%M%S}"
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(old, encoding="utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    hashes = _written()
    hashes[_rel(path)] = _sha(text)
    ONBOARD_DIR.mkdir(parents=True, exist_ok=True)
    (ONBOARD_DIR / WRITTEN).write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return "written"


def _dump(value) -> str:
    import yaml

    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True, default_flow_style=False, width=100)


def set_keys(text: str, values: dict) -> str:
    """`text` (a YAML file) with each top-level key's block replaced by the new value, in place,
    so every comment outside those blocks stays; a key the file lacks is appended."""
    from .init import key_span

    for key, value in values.items():
        block = _dump({key: value})
        lines = text.splitlines(keepends=True)
        span = key_span(lines, key)
        if span is None:
            text = text.rstrip("\n") + "\n\n" + block if text.strip() else block
        else:
            start, end = span
            text = "".join(lines[:start]) + block + "".join(lines[end:])
    return text


# --- the master resume, with provenance (decision 7)

def _provenance_keys(data: dict) -> list[tuple[str, str]]:
    """(kind, name) of every entry that needs a source: each role, project, school, skill
    group, additional line, and the summary."""
    sections = data["cv"].get("sections") or {}
    keys: list[tuple[str, str]] = [("summary", "summary")] if sections.get("summary") else []
    for kind, field in (("experience", "company"), ("projects", "name"), ("education", "institution"),
                        ("skills", "label"), ("additional", "label")):
        keys += [(kind, str(e.get(field))) for e in sections.get(kind) or [] if isinstance(e, dict)]
    return keys


def _traces(what: str, name: str) -> bool:
    """`name` as a whole word or phrase in a provenance `what`, so a skill group "Go" is not
    traced by "experience Google" and "C" not by any line with a c in it."""
    return re.search(rf"(?<!\w){re.escape(name.lower())}(?!\w)", what) is not None


def provenance_errors(data: dict, prov) -> list[str]:
    """Every entry must be traced to a document in the manifest or to the interview."""
    if not isinstance(prov, list) or not prov:
        return ["`provenance` is required: a list of {what, from} naming where each entry came from"]
    known = set(document_ids()) | {INTERVIEW}
    errors = []
    for i, p in enumerate(prov):
        if not isinstance(p, dict) or not str(p.get("what") or "").strip():
            errors.append(f"provenance[{i}] needs `what` (the entry) and `from` (document ids or {INTERVIEW!r})")
            continue
        src = p.get("from")
        src = [src] if isinstance(src, str) else src
        if not isinstance(src, list) or not src:
            errors.append(f"provenance[{i}] ({p['what']}) needs `from`")
            continue
        unknown = [s for s in src if s not in known]
        if unknown:
            errors.append(f"provenance[{i}] ({p['what']}) cites {', '.join(map(str, unknown))}, which is not an "
                          f"extracted document (known: {', '.join(sorted(known))})")
    whats = [str(p.get("what") or "").lower() for p in prov if isinstance(p, dict)]
    for kind, name in _provenance_keys(data):
        if not any(_traces(w, name) for w in whats):
            errors.append(f"no provenance for {kind} {name!r}: ask the user where it comes from, or leave it out")
    return errors


def write_resume(payload, yes: bool = False, path: Path | None = None) -> str:
    from datetime import date

    if not isinstance(payload, dict):
        raise Refused("the resume payload is a mapping with `cv` and `provenance`")
    prov = payload.get("provenance")
    data = {k: v for k, v in payload.items() if k != "provenance"}
    errors = resume_errors(data) or provenance_errors(data, prov)
    if errors:
        raise Refused("\n".join(f"  ! {e}" for e in errors))
    path = path or user_file("master_resume")
    sources = sorted({s for p in prov or [] for s in ([p["from"]] if isinstance(p["from"], str) else p["from"])})
    head = (f"# MASTER RESUME, written by `python -m src.onboard` on {date.today().isoformat()} from: "
            f"{', '.join(sources)}.\n# Every entry is traced in data/onboard/{PROVENANCE}. Everything in it "
            "must be TRUE; edit freely.\n\n")
    state = commit_file(path, "master_resume", head + _dump(data), yes)
    ONBOARD_DIR.mkdir(parents=True, exist_ok=True)
    (ONBOARD_DIR / PROVENANCE).write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    c = resume_counts(data)
    return (f"  {state:8s} {_rel(path)}: {c['roles']} roles, {c['projects']} projects, {c['skills']} skills, "
            f"{c['education']} education; provenance in {_rel(ONBOARD_DIR / PROVENANCE)}")


# --- the profile, one section at a time

PROFILE_EXTRA_KEYS = ("resume_basename",)        # optional keys the example only mentions in a comment


def write_profile(payload, yes: bool = False, path: Path | None = None) -> str:
    import yaml

    if not isinstance(payload, dict) or not payload:
        raise Refused("the profile payload is a mapping of top-level keys to set")
    if "dream_companies" in payload:
        raise Refused("dream companies are data, not profile keys: use `write dream`")
    example = EXAMPLES["profile"]
    allowed = set(yaml.safe_load(example.read_text(encoding="utf-8")) or {}) | set(PROFILE_EXTRA_KEYS)
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise Refused(f"  ! unknown profile key(s) {', '.join(unknown)} (known: {', '.join(sorted(allowed))})")
    path = path or user_file("profile")
    base = path.read_text(encoding="utf-8") if path.exists() else example.read_text(encoding="utf-8")
    text = set_keys(base, payload)
    errors = profile_errors(yaml.safe_load(text))
    if errors:
        raise Refused("\n".join(f"  ! {e}" for e in errors))
    state = commit_file(path, "profile", text, yes)
    return f"  {state:8s} {_rel(path)}: {', '.join(payload)}"


# --- sources.local.yaml, one block per source

def write_sources(payload, yes: bool = False, path: Path | None = None) -> str:
    from .config import sources

    if not isinstance(payload, dict) or not payload:
        raise Refused("the sources payload is a mapping of source name to its block")
    known = set(sources())
    errors = [f"unknown source {name!r} (config/sources.yaml has no such block)" for name in payload
              if name not in known]
    errors += [f"{name}: the block must be a mapping" for name, block in payload.items() if not isinstance(block, dict)]
    errors += token_errors(payload)
    if errors:
        raise Refused("\n".join(f"  ! {e}" for e in errors))
    path = path or user_file("sources_local")
    base = path.read_text(encoding="utf-8") if path.exists() else EXAMPLES["sources_local"].read_text(encoding="utf-8")
    state = commit_file(path, "sources_local", set_keys(base, payload), yes)
    return f"  {state:8s} {_rel(path)}: {', '.join(payload)}"


# ---- sources: the proposal from coverage, and ATS tokens verified live ----------------------
#
# `sources` lists every block of the merged source config as the region gate leaves it for the
# profile (config.sources(), decision 10): on or off, the regions, the keys a keyed source needs
# with set/unset and the signup URL from .env.example, and the targeting still missing. The ATS
# families take the tokens of companies the user follows; `verify-token` makes ONE request per
# token (no retry) and records 200-and-non-empty in data/onboard/verified.json, and
# `write sources` refuses a token that is not recorded there.

VERIFIED = "verified.json"
# source -> the env keys it reads, and whether it runs without them
KEYED: dict[str, tuple[tuple[str, ...], bool]] = {
    "adzuna": (("ADZUNA_APP_ID", "ADZUNA_APP_KEY"), False),
    "careerjet": (("CAREERJET_AFFID",), False),
    "findwork": (("FINDWORK_TOKEN",), False),
    "themuse": (("THEMUSE_API_KEY",), True),
}


@dataclass(frozen=True)
class Board:
    """How one ATS family's public board is asked for its open roles."""
    url: str                       # `{t}` is the token
    count: str                     # the list's key in the JSON, "" when the body is the list
    params: tuple[tuple[str, str], ...] = ()


# The ATS families whose board one GET can count. Workday (a POST per site) and Personio (XML)
# are not verified here; their tokens are written as given.
BOARDS: dict[str, Board] = {
    "greenhouse": Board("https://boards-api.greenhouse.io/v1/boards/{t}/jobs", "jobs"),
    "lever": Board("https://api.lever.co/v0/postings/{t}", "", (("mode", "json"),)),
    "ashby": Board("https://api.ashbyhq.com/posting-api/job-board/{t}", "jobs"),
    "smartrecruiters": Board("https://api.smartrecruiters.com/v1/companies/{t}/postings", "content",
                             (("limit", "100"),)),
    "recruitee": Board("https://{t}.recruitee.com/api/offers/", "offers"),
    "teamtailor": Board("https://{t}.teamtailor.com/jobs.json", "items"),
    "pinpoint": Board("https://{t}.pinpointhq.com/postings.json", "data"),
    "rippling": Board("https://api.rippling.com/platform/api/ats/v1/board/{t}/jobs", "items"),
    "bamboohr": Board("https://{t}.bamboohr.com/careers/list", "result"),
}
_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")


def token_key(source: str) -> str:
    """The block key an ATS family lists its tokens under (`tokens`, `companies`, `clients`)."""
    from .config import TARGETING_KEYS

    return TARGETING_KEYS[source][0][0]


def _verified() -> dict[str, dict[str, dict]]:
    path = ONBOARD_DIR / VERIFIED
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _get(url: str, params: dict[str, str]):
    """The one live request a verification makes (tests replace this)."""
    import requests

    from .adapters import UA

    return requests.get(url, params=params, timeout=20, headers={"User-Agent": UA, "Accept": "application/json"})


def verify_token(source: str, token: str) -> dict:
    """One GET to the board; {ok, jobs, status, note}. ok = HTTP 200 and at least one open role.
    The result is recorded either way."""
    from datetime import date

    if source not in BOARDS:
        raise ValueError(f"{source}: not a board verify-token can count (it knows {', '.join(BOARDS)})")
    if not _TOKEN.match(token):
        raise ValueError(f"{token!r}: a board token is letters, digits, dot, dash or underscore")
    board = BOARDS[source]
    result: dict = {"ok": False, "jobs": 0, "status": None, "note": "", "at": date.today().isoformat()}
    try:
        resp = _get(board.url.format(t=token), dict(board.params))
        result["status"] = resp.status_code
        if resp.status_code != 200:
            result["note"] = f"HTTP {resp.status_code}"
        else:
            body = resp.json()
            items = body if not board.count else (body.get(board.count) if isinstance(body, dict) else None)
            if not isinstance(items, list):
                result["note"] = "the answer is not a job board (wrong token?)"
            else:
                result["jobs"] = len(items)
                result["ok"] = bool(items)
                result["note"] = "" if items else "0 open roles"
    except ValueError:
        result["note"] = "the answer is not JSON (wrong token?)"
    except Exception as e:  # noqa: BLE001, a network failure is a result to report, not a crash
        result["note"] = f"request failed: {type(e).__name__}"
    done = _verified()
    done.setdefault(source, {})[token] = result
    ONBOARD_DIR.mkdir(parents=True, exist_ok=True)
    (ONBOARD_DIR / VERIFIED).write_text(json.dumps(done, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def token_errors(payload: dict) -> list[str]:
    """A token for a countable board must have been verified live with open roles."""
    done = _verified()
    errors = []
    for source, block in payload.items():
        if source not in BOARDS or not isinstance(block, dict):
            continue
        tokens = block.get(token_key(source)) or []
        if not isinstance(tokens, list):
            errors.append(f"{source}.{token_key(source)} must be a list")
            continue
        for t in tokens:
            res = done.get(source, {}).get(str(t))
            if res is None:
                errors.append(f"{source} {t}: not verified; run python -m src.onboard verify-token {source} {t}")
            elif not res.get("ok"):
                errors.append(f"{source} {t}: {res.get('note') or 'failed'} on {res.get('at')}; leave it out "
                              "(the summary keeps it as a note)")
    return errors


def proposal(prof: dict | None = None) -> list[str]:
    """The lines `sources` prints: the coverage, one line per source, the totals."""
    from .config import (
        REGION_GATED, coverage, env_catalog, env_value, get_secret, load_profile, missing_targeting,
        source_regions, sources,
    )

    if prof is None:
        try:
            prof = load_profile()
        except FileNotFoundError:
            prof = {}
    cover = sorted(coverage(prof))
    merged = sources(prof)
    urls = {e["name"]: e["url"] for e in env_catalog()}
    lines = [f"coverage: {', '.join(cover) or 'none (no location in the profile resolves; every source stays as configured)'}"]
    on: list[str] = []
    need_key: list[str] = []
    ats: list[str] = []
    for name, block in merged.items():
        if name == "title_filter" or not isinstance(block, dict):
            continue
        regions = ", ".join(source_regions(block))
        if name in BOARDS or name in ("workday", "personio"):
            if block.get("enabled") or block.get(REGION_GATED):
                listed = block.get(token_key(name)) or []
                ats.append(f"{name} ({token_key(name)}: {len(listed)} listed)")
            continue
        if not block.get("enabled"):
            why = "off by region" if block.get(REGION_GATED) else "off in config/sources.yaml"
            lines.append(f"  off  {name:18s} [{regions}]  {why}")
            continue
        notes = []
        keys, optional = KEYED.get(name, ((), True))
        unset = [k for k in keys if not (env_value(k) or get_secret(k))]
        if unset:
            url = urls.get(keys[0], "")
            notes.append(f"{'optional key' if optional else 'needs'} {', '.join(unset)} (unset){': ' + url if url else ''}")
            if not optional:
                need_key.append(name)
        missing = missing_targeting(name, block)
        if missing:
            notes.append(f"targeting: {', '.join(missing)}")
        on.append(name)
        lines.append(f"  on   {name:18s} [{regions}]" + (f"  {'; '.join(notes)}" if notes else ""))
    if ats:
        lines.append(f"  ats  {'; '.join(ats)}: ask for the companies the user follows, "
                     "verify each token, then write sources")
    lines.append(f"{len(on)} on" + (f", {len(need_key)} need a key ({', '.join(need_key)})" if need_key else ""))
    return lines


# --- .env, one line per key (config.set_env, shared with the TUI's Keys tab)

_MAIL_KEY = re.compile(r"^MAIL_[A-Z0-9]+_(USER|PASS|HOST|FOLDERS|ALIASES|REPLY_AS)$")


def env_keys_known() -> list[str]:
    """Every key .env.example names, set or commented out."""
    from .config import env_catalog

    return [e["name"] for e in env_catalog()]


def write_env(payload, yes: bool = False) -> str:
    """Set keys in .env. A key that already holds a different value is replaced only with
    `--yes`. The output names keys, never values."""
    from .config import env_value, set_env

    if not isinstance(payload, dict) or not payload:
        raise Refused("the env payload is a mapping of KEY to value (\"\" leaves a key empty)")
    known = set(env_keys_known())
    errors = [f"{k}: not a key .env.example knows (nor a MAIL_<LABEL>_* key)" for k in payload
              if k not in known and not _MAIL_KEY.match(str(k))]
    errors += [f"{k}: the value must be a string" for k, v in payload.items() if not isinstance(v, str)]
    errors += [f"{k}: the value must be one line" for k, v in payload.items()
               if isinstance(v, str) and ("\n" in v or "\r" in v)]
    if errors:
        raise Refused("\n".join(f"  ! {e}" for e in errors))
    replacing = [k for k, v in payload.items() if env_value(k) and env_value(k) != v]
    if replacing and not yes:
        raise Refused(f"  ! {', '.join(replacing)} already set in .env; ask before replacing "
                      "(write the payload again and repeat with --yes), or leave it out", NEEDS_YES)
    lines = [f"  {set_env(k, v):8s} .env {k}" for k, v in payload.items()]
    return "\n".join(lines)


# --- dream companies (the dream_companies table)

def write_dream(payload) -> str:
    from . import db, dream

    entries = payload.get("companies") if isinstance(payload, dict) else payload
    if not isinstance(entries, list) or not entries:
        raise Refused("the dream payload is a list of companies: a name, or {name, match, careers_url, note}")
    rows = [dream.normalize(e) for e in entries]
    if any(r is None for r in rows):
        raise Refused("  ! every dream company needs a name")
    added, kept = [], []
    conn = db.connect(db.DB_PATH)
    try:
        for d in rows:
            assert d is not None
            if db.get_dream(conn, d["name"]):
                kept.append(d["name"])
                continue
            db.add_dream(conn, d["name"], d["match"], d["careers_url"] or None, d["note"] or None)
            added.append(d["name"])
        conn.commit()
    finally:
        conn.close()
    dream.reset_cache()
    out = [f"  added    dream {name}" for name in added] + [f"  kept     dream {name} (already in the table)"
                                                             for name in kept]
    return "\n".join(out)


def _drop_payload(arg: str) -> None:
    """An env payload file holds the values in plain text: `write env` deletes it after the call,
    whatever the outcome, when it lies under data/onboard/ (a file anywhere else is the user's)."""
    path = Path(arg)
    if arg == "-" or len(arg) >= 4096 or not path.is_file():
        return
    try:
        path.resolve().relative_to(ONBOARD_DIR.resolve())
    except ValueError:
        return
    path.unlink(missing_ok=True)
    print(f"  removed  {arg} (it held the values)")


def read_payload(arg: str, secret: bool = False):
    """A payload given inline (JSON), as a .json/.yaml file, or `-` for stdin. A `secret` payload
    (`write env`) holds values: a parse error then names the line and column only, because
    PyYAML's own message quotes the offending line, value included."""
    import yaml

    if arg == "-":
        text = sys.stdin.read()
    elif len(arg) < 4096 and not arg.lstrip().startswith(("{", "[")) and Path(arg).is_file():
        text = Path(arg).read_text(encoding="utf-8")
    else:
        text = arg
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as e:
            if secret:
                mark = getattr(e, "problem_mark", None)
                where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark is not None else ""
                raise Refused(f"  ! the payload is neither JSON nor YAML{where}; its text is not shown, it holds "
                              "values (a quote inside a value needs a backslash in JSON)") from None
            raise Refused(f"  ! the payload is neither JSON nor YAML: {e}") from None


# ---- the public LinkedIn page (decision 7): opt-in, fragile, never logged in ------------------
#
# Off unless the user passes their own profile URL. One plain GET with no cookies and no
# session; LinkedIn answers most such requests with a login wall (HTTP 999 or a redirect to
# /authwall), and its terms discourage automated reads, so the warning is printed before the
# request and a wall is reported, never worked around. What the public page carries is the
# schema.org Person in its JSON-LD: name, headline, location, the roles (worksFor), the schools
# (alumniOf), languages, awards. It is recorded as one more document, so provenance can cite it.

LINKEDIN_WARNING = ("  note: this reads the public LinkedIn page only, with no login; LinkedIn often answers "
                    "with a login wall, and its terms discourage automated reads. LinkedIn's \"Save to PDF\" "
                    "or the data-export zip is the reliable route.")
_LINKEDIN_URL = re.compile(r"^https?://(?:[a-z]{2,3}\.|www\.)?linkedin\.com/in/([A-Za-z0-9%_-]{2,100})/?(?:[?#].*)?$")
_LD_JSON = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S | re.I)


def linkedin_slug(url: str) -> str:
    m = _LINKEDIN_URL.match(url.strip())
    if not m:
        raise ValueError(f"{url!r} is not a public profile URL (https://www.linkedin.com/in/<name>)")
    return m.group(1)


def _get_page(url: str):
    """The one GET the LinkedIn read makes (tests replace this). No cookies, no session."""
    import requests

    from .adapters import UA

    return requests.get(url, timeout=20, headers={"User-Agent": UA, "Accept": "text/html"})


def _person(html: str) -> dict | None:
    """The schema.org Person in the page's JSON-LD (top level or inside @graph)."""
    for block in _LD_JSON.findall(html):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        for node in nodes if isinstance(nodes, list) else []:
            if isinstance(node, dict) and node.get("@type") == "Person":
                return node
    return None


def _names(value) -> list[str]:
    items = value if isinstance(value, list) else [value] if value else []
    return [str(i.get("name") if isinstance(i, dict) else i).strip() for i in items
            if (i.get("name") if isinstance(i, dict) else i)]


def _org_lines(orgs) -> list[str]:
    out = []
    for org in orgs if isinstance(orgs, list) else [orgs] if orgs else []:
        if not isinstance(org, dict) or not org.get("name"):
            continue
        member = org.get("member")
        member = member if isinstance(member, dict) else {}
        dates = " to ".join(str(member[k]) for k in ("startDate", "endDate") if member.get(k))
        line = f"- {org['name']}" + (f" ({dates})" if dates else "")
        if member.get("description"):
            line += f": {' '.join(str(member['description']).split())}"
        out.append(line)
    return out


def linkedin_text(person: dict, url: str) -> str:
    """The Person as the plain text a resume reader expects, every line from the page."""
    lines = [f"Public LinkedIn profile: {url}", f"Name: {person.get('name', '')}"]
    titles = person.get("jobTitle")
    if titles:
        lines.append(f"Headline: {'; '.join(titles if isinstance(titles, list) else [titles])}")
    addr = person.get("address")
    addr = addr if isinstance(addr, dict) else {}
    where = ", ".join(str(addr[k]) for k in ("addressLocality", "addressCountry") if addr.get(k))
    if where:
        lines.append(f"Location: {where}")
    if person.get("description"):
        lines += ["", "About:", " ".join(str(person["description"]).split())]
    for title, key in (("Experience", "worksFor"), ("Education", "alumniOf")):
        body = _org_lines(person.get(key))
        if body:
            lines += ["", f"{title}:", *body]
    for title, key in (("Languages", "knowsLanguage"), ("Awards", "awards")):
        names = _names(person.get(key))
        if names:
            lines.append(f"{title}: {', '.join(names)}")
    return "\n".join(lines)


def linkedin(url: str) -> Document:
    """Read the public page once and record it as a document. Raises ValueError on a bad URL,
    a login wall, or a page with no public profile data."""
    slug = linkedin_slug(url)
    clean = f"https://www.linkedin.com/in/{slug}/"
    try:
        resp = _get_page(clean)
    except Exception as e:  # noqa: BLE001, a network failure is an answer to report
        raise ValueError(f"the request failed ({type(e).__name__}); use the PDF or the data export") from None
    final = str(getattr(resp, "url", "") or "")
    if resp.status_code == 999 or "authwall" in final or "/login" in final or "/signup" in final:
        raise ValueError("LinkedIn answered with a login wall; nothing was read. Use \"Save to PDF\" on the "
                         "profile or the data-export zip instead")
    if resp.status_code != 200:
        raise ValueError(f"LinkedIn answered HTTP {resp.status_code}; nothing was read")
    person = _person(resp.text)
    if person is None:
        raise ValueError("the page carries no public profile data (a login wall or a private profile); "
                         "use the PDF or the data export")
    return record(f"linkedin-{slug}", clean, "linkedin-public", linkedin_text(person, clean))


# ---- summary ------------------------------------------------------------------------------

def _yaml_or_none(path: Path):
    try:
        return _load(path)
    except (FileNotFoundError, ValueError):
        return None


def summary() -> list[str]:
    """What the interview read and wrote, one line per file: the closing message's facts."""
    from collections import Counter

    from . import db
    from .config import env_value

    lines = []
    docs = load_manifest()
    lines.append(f"documents ({len(docs)}): " + (", ".join(f"{d.id} ~{d.tokens:,} tokens" for d in docs) or "none")
                 + (f"; ~{sum(d.tokens for d in docs):,} tokens in all" if docs else ""))
    resume_path = user_file("master_resume")
    data = _yaml_or_none(resume_path)
    if isinstance(data, dict) and not resume_errors(data):
        c = resume_counts(data)
        prov_path = ONBOARD_DIR / PROVENANCE
        prov = json.loads(prov_path.read_text(encoding="utf-8")) if prov_path.exists() else []
        cited = Counter(s for p in prov for s in ([p["from"]] if isinstance(p["from"], str) else p["from"]))
        traced = (f"; {len(prov)} entries traced ({', '.join(f'{k}: {v}' for k, v in sorted(cited.items()))})"
                  if prov else "; no provenance recorded (not written by the interview)")
        lines.append(f"{_rel(resume_path)}: {c['roles']} roles, {c['projects']} projects, {c['skills']} skills, "
                     f"{c['education']} education{traced}")
    else:
        lines.append(f"{_rel(resume_path)}: missing or invalid (python -m src.onboard check resume)")
    prof_path = user_file("profile")
    prof = _yaml_or_none(prof_path)
    if isinstance(prof, dict) and not profile_errors(prof):
        left = example_keys(prof)
        lines.append(f"{_rel(prof_path)}: ok" + (f"; still the example's value: {', '.join(left)}" if left else ""))
    else:
        lines.append(f"{_rel(prof_path)}: missing or invalid (python -m src.onboard check profile)")
    local_path = user_file("sources_local")
    local = _yaml_or_none(local_path) or {}
    blocks = []
    for name, block in local.items() if isinstance(local, dict) else []:
        if name in BOARDS and isinstance(block, dict):
            n = len(block.get(token_key(name)) or [])
            blocks.append(f"{name} ({n} token{'s' if n != 1 else ''})")
        else:
            blocks.append(name)
    lines.append(f"{_rel(local_path)}: {', '.join(blocks) or 'no targeting yet'}")
    checked = [(s, t, r) for s, toks in _verified().items() for t, r in toks.items()]
    if checked:
        notes = [f"{s} {t}: {r.get('note')}" for s, t, r in checked if not r.get("ok")]
        lines.append(f"tokens verified: {sum(1 for _s, _t, r in checked if r.get('ok'))} of {len(checked)}"
                     + (f"; not written, kept as notes: {'; '.join(notes)}" if notes else ""))
    keyed = [k for keys, _opt in KEYED.values() for k in keys]
    set_keys_ = [k for k in keyed if env_value(k)]
    lines.append(f".env: {len(set_keys_)} of {len(keyed)} source keys set"
                 + (f" ({', '.join(set_keys_)})" if set_keys_ else "")
                 + (f"; unset: {', '.join(k for k in keyed if k not in set_keys_)}" if len(set_keys_) < len(keyed) else ""))
    labels = [lab.strip() for lab in env_value("MAIL_ACCOUNTS").split(",") if lab.strip()]
    if labels:
        no_pass = [lab for lab in labels if not env_value(f"MAIL_{lab.upper()}_PASS")]
        lines.append(f"mail: {', '.join(labels)}"
                     + (f"; no app password for {', '.join(no_pass)}" if no_pass else "; app passwords set"))
    else:
        lines.append("mail: skipped (docs/mail-setup.md when you want the inbox pull)")
    names: list[str] = []
    if db.DB_PATH.exists():
        conn = db.connect(db.DB_PATH)
        try:
            names = [d["name"] for d in db.list_dream(conn)]
        finally:
            conn.close()
    lines.append(f"dream companies: {len(names)}" + (f" ({', '.join(names)})" if names else ""))
    written = sorted(_written())
    lines.append(f"written by onboarding: {', '.join(written) or 'nothing yet'}")
    return lines


WRITERS = ("resume", "profile", "sources", "env", "dream")


def write(what: str, payload, yes: bool = False) -> str:
    if what == "resume":
        return write_resume(payload, yes)
    if what == "profile":
        return write_profile(payload, yes)
    if what == "sources":
        return write_sources(payload, yes)
    if what == "env":
        return write_env(payload, yes)
    return write_dream(payload)


# ---- CLI ----------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("extract", help="text of each document into data/onboard/, with sizes")
    p.add_argument("files", nargs="+", type=Path)
    p = sub.add_parser("check", help="validate the master resume or the profile")
    p.add_argument("what", choices=("resume", "profile"))
    p.add_argument("--file", type=Path, help="check this file instead of the real one")
    p = sub.add_parser("write", help="validate and write one file (show-diff-and-ask for a hand-edited one)")
    p.add_argument("what", choices=WRITERS)
    p.add_argument("payload", help="JSON inline, a .json/.yaml file, or - for stdin")
    p.add_argument("--yes", action="store_true", help="the user saw the diff and agreed")
    p = sub.add_parser("linkedin", help="opt-in: read a public LinkedIn profile page once (no login)")
    p.add_argument("url")
    sub.add_parser("summary", help="what the interview read and wrote, one line per file")
    sub.add_parser("sources", help="the sources the profile's regions turn on, keys and targeting they need")
    p = sub.add_parser("verify-token", help="one live request: does this ATS board answer with open roles?")
    p.add_argument("source", choices=tuple(BOARDS))
    p.add_argument("token")
    args = ap.parse_args(argv)

    if args.cmd == "sources":
        print("\n".join(proposal()))
        return 0
    if args.cmd == "summary":
        print("\n".join(summary()))
        return 0
    if args.cmd == "linkedin":
        print(LINKEDIN_WARNING)
        try:
            print(size_line(linkedin(args.url)))
        except ValueError as bad:
            print(f"  ! {bad}")
            return 1
        return 0
    if args.cmd == "verify-token":
        try:
            res = verify_token(args.source, args.token)
        except ValueError as bad:
            print(f"  ! {bad}")
            return 1
        if res["ok"]:
            print(f"  ok       {args.source} {args.token}: {res['jobs']} open roles")
            return 0
        print(f"  ! {args.source} {args.token}: {res['note']}")
        return 1

    if args.cmd == "write":
        try:
            print(write(args.what, read_payload(args.payload, secret=args.what == "env"), args.yes))
        except Refused as refused:
            print(refused)
            return refused.code
        except ValueError as bad:
            print(f"  ! {bad}")
            return 1
        finally:
            if args.what == "env":
                _drop_payload(args.payload)
        return 0

    if args.cmd == "extract":
        docs, errors = extract(args.files)
        for doc in docs:
            print(size_line(doc))
        for line in errors:
            print(f"  ! {line}")
        total = sum(d.tokens for d in docs)
        print(f"extracted {len(docs)} of {len(args.files)} document{'s' if len(args.files) != 1 else ''}, "
              f"~{total:,} tokens in all; read each text file once")
        return 1 if errors else 0
    if args.cmd == "check":
        return check(args.what, args.file)
    return 2


if __name__ == "__main__":
    sys.exit(main())
