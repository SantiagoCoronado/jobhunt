"""The guard (docs/spec-open-source.md decision 9): no user-owned file is tracked, and no
tracked text outside docs/ carries the author's identity.

Path rule (always): every tracked path under config/, resume/, research/, applications/ and
interviews/ is an example, a README, a .gitkeep, or on the product allowlist.

Identity rule (opt-in): the patterns come from the ignored config/identity.local.yaml; this
file contains none of them. Absent file: the rule is skipped with a notice, so a fresh clone's
CI runs the path rule only. The release checklist runs it with the author's file present.
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
            hits.append(f"{p}:{n}")
    assert hits == [], f"identity strings in tracked files: {hits[:40]}{' ...' if len(hits) > 40 else ''}"
