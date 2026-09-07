"""Regenerate tests/fixtures/ from the tracked *.example.* files.

The example files are the one source for the invented candidate ("Alex Example"); the
fixtures are copies of them so tests never read a real user's profile, resume or answers.
`tests/test_fixtures_sync.py` fails when the two drift, so after editing an example run:

    python scripts/gen_fixtures.py

Usage: python scripts/gen_fixtures.py [--check]   (--check exits 1 on drift, writes nothing)
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"

# example (tracked) -> fixture name under tests/fixtures/
PAIRS: dict[str, str] = {
    "config/profile.example.yaml": "profile.yaml",
    "config/sources.local.example.yaml": "sources.local.yaml",
    "resume/master_resume.example.yaml": "master_resume.yaml",
    "resume/answers.example.yaml": "answers.yaml",
}


def drift() -> list[str]:
    """Fixture names whose content differs from (or is missing against) their example."""
    out = []
    for src, dst in PAIRS.items():
        a, b = ROOT / src, FIXTURES / dst
        if not a.exists():
            out.append(f"missing example: {src}")
        elif not b.exists() or a.read_bytes() != b.read_bytes():
            out.append(dst)
    return out


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
