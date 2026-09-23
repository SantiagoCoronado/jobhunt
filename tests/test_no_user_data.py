"""The guard (docs/spec-open-source.md decision 9): no user-owned file is tracked, and no
tracked text outside docs/ carries the author's identity.

Path rule (always): every tracked path under config/, resume/, research/, applications/ and
interviews/ is an example, a README, a .gitkeep, or on the product allowlist.

Identity rule (opt-in): the patterns come from the ignored config/identity.local.yaml; this
file contains none of them. Absent file: the rule is skipped with a notice, so a fresh clone's
CI runs the path rule only. The release checklist runs it with the author's file present.
Two lines are provenance, not a leak, and pass: a dated attribution under docs/ (the file's
`attribution_regexes`) and the `Copyright (c) <year>` line of LICENSE (decision 11).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml

from src.config import ROOT

GUARDED_DIRS = ("config/", "resume/", "research/", "applications/", "interviews/")
PRODUCT_ALLOWLIST = {
    "config/sources.yaml", "config/skills_lexicon.yaml", "config/mail_hints.yaml",
    "config/hunt.toml", "config/tui.toml", "config/geo.yaml", "research/aliases.yaml",
}
IDENTITY_FILE = ROOT / "config" / "identity.local.yaml"
TEXT_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".toml", ".sh", ".txt", ".json", ".html", ".css", ".js", ".cfg", ".ini", ""}
_COPYRIGHT = re.compile(r"^Copyright \(c\) \d{4}")   # the one LICENSE line that names the author


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    return [p for p in out.decode().split("\0") if p]


def _is_example(path: str) -> bool:
    name = Path(path).name
    return ".example." in name or name.endswith(".example")


def test_no_user_owned_file_is_tracked():
    bad = []
    for p in tracked_files():
        if not p.startswith(GUARDED_DIRS):
            continue
        name = Path(p).name
        if _is_example(p) or name in ("README.md", ".gitkeep") or p in PRODUCT_ALLOWLIST:
            continue
        bad.append(p)
    assert bad == [], f"user-owned files in the index (add an .example or the allowlist): {bad}"


# Always-on generic rule (PR #21 review): the product text never carries an address at a
# personal mail provider or a phone-number-shaped string, whoever the author is. Placeholder
# local parts (you@, me@, example@) are documentation. docs/ and tests/ are exempt because
# their mail examples are invented, and the identity rule below covers the author's own.
PRODUCT_TEXT_DIRS = ("src/", "scripts/", "config/", ".claude/", ".github/", "prompts/")
PRODUCT_TEXT_FILES = ("CLAUDE.md", "README.md", "setup.sh", "pyproject.toml", "requirements.txt")
_PERSONAL_MAIL = re.compile(r"\b(?!(?:you|me|example|user|name)@)[a-z0-9._%+-]+@(?:gmail|googlemail|outlook|hotmail|yahoo|icloud|proton|protonmail|live)\.[a-z.]+", re.I)
_PHONE = re.compile(r"\+\d{1,3}[\s.-]\d{2,4}[\s.-]\d{3,4}[\s.-]\d{4}\b")


def test_no_personal_address_or_phone_in_product_text():
    hits = []
    for p in tracked_files():
        if not (p.startswith(PRODUCT_TEXT_DIRS) or p in PRODUCT_TEXT_FILES) or _is_example(p):
            continue
        path = ROOT / p
        if path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if _PERSONAL_MAIL.search(line) or _PHONE.search(line):
                hits.append(f"{p}:{n}")
    assert hits == [], f"personal address or phone number in product text: {hits}"


def _identity() -> dict | None:
    if not IDENTITY_FILE.exists():
        return None
    data = yaml.safe_load(IDENTITY_FILE.read_text()) or {}
    return {
        "patterns": [str(p) for p in (data.get("patterns") or []) if str(p).strip()],
        "attribution": [re.compile(r) for r in (data.get("attribution_regexes") or [])],
    }


def test_no_identity_string_in_tracked_text():
    ident = _identity()
    if ident is None or not ident["patterns"]:
        pytest.skip("config/identity.local.yaml absent: identity rule skipped (path rule still ran)")
    rx = re.compile("|".join(re.escape(p) for p in ident["patterns"]), re.I)
    hits = []
    for p in tracked_files():
        path = ROOT / p
        if path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
            continue
        if _is_example(p) or p.startswith("tests/fixtures/"):
            continue                       # the invented candidate lives there by design
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if not rx.search(line):
                continue
            if p.startswith("docs/") and any(a.search(line) for a in ident["attribution"]):
                continue
            if p == "LICENSE" and _COPYRIGHT.match(line):
                continue
            hits.append(f"{p}:{n}")
    assert hits == [], f"identity strings in tracked files: {hits[:40]}{' ...' if len(hits) > 40 else ''}"
