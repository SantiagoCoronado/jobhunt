"""First-run setup: create every user-owned file from its tracked example, never overwrite.

    python -m src.init            copy the examples that have no real file yet, make the data dirs
    python -m src.init --check    report only, exit 1 when a user file is missing

The user-owned files (docs/spec-open-source.md decision 3) are git-ignored and come from the
tracked `<name>.example.<ext>` next to them (`.env.example` is the one suffix form). This never
touches a tracked file and never overwrites an existing real file, so it is safe to re-run.
`config/identity.local.example.yaml` is documentation only and is deliberately NOT copied:
the guard test's identity rule is opt-in (write `config/identity.local.yaml` by hand).
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from .config import ROOT

# example (tracked) -> real (ignored); both spellings of "example" are handled
EXAMPLES: dict[str, str] = {
    "config/profile.example.yaml": "config/profile.yaml",
    "config/sources.local.example.yaml": "config/sources.local.yaml",
    "config/notify.example.yaml": "config/notify.yaml",
    "resume/master_resume.example.yaml": "resume/master_resume.yaml",
    "resume/answers.example.yaml": "resume/answers.yaml",
    ".env.example": ".env",
}
SKIPPED_EXAMPLES = ("config/identity.local.example.yaml",)   # documentation only, opt-in guard
DATA_DIRS = (
    "data", "applications/pending", "applications/applied", "applications/other",
    "interviews", "research/companies", "research/upskill",
)


def real_name(example: str) -> str:
    """`profile.example.yaml` -> `profile.yaml`; `.env.example` -> `.env`."""
    if example.endswith(".example"):
        return example[: -len(".example")]
    return example.replace(".example.", ".", 1)


def plan(root: Path = ROOT) -> dict[str, list[str]]:
    """What a run would do: {'copy': [...], 'keep': [...], 'missing_example': [...], 'mkdir': [...]}."""
    out: dict[str, list[str]] = {"copy": [], "keep": [], "missing_example": [], "mkdir": []}
    for ex, real in EXAMPLES.items():
        assert real_name(ex) == real, ex
        if not (root / ex).exists():
            out["missing_example"].append(ex)
        elif (root / real).exists():
            out["keep"].append(real)
        else:
            out["copy"].append(real)
    for d in DATA_DIRS:
        if not (root / d).is_dir():
            out["mkdir"].append(d)
    return out


def run(root: Path = ROOT, check: bool = False) -> int:
    p = plan(root)
    if check:
        for real in p["copy"]:
            print(f"  missing  {real}  (python -m src.init creates it)")
        for real in p["keep"]:
            print(f"  present  {real}")
        for ex in p["missing_example"]:
            print(f"  ! no example on disk: {ex}")
        print("user files complete" if not p["copy"] and not p["missing_example"] else "user files incomplete")
        return 1 if p["copy"] or p["missing_example"] else 0
    for ex, real in EXAMPLES.items():
        if real in p["copy"]:
            (root / real).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / ex, root / real)
            print(f"  created  {real}  (from {ex}; edit it, the person in it is invented)")
    for real in p["keep"]:
        print(f"  kept     {real}")
    for ex in p["missing_example"]:
        print(f"  ! no example on disk: {ex}")
    for d in p["mkdir"]:
        (root / d).mkdir(parents=True, exist_ok=True)
        print(f"  mkdir    {d}/")
    for ex in SKIPPED_EXAMPLES:
        print(f"  skipped  {ex}  (documentation; write {real_name(ex)} by hand to enable the identity guard)")
    print("Next: edit config/profile.yaml, resume/master_resume.yaml and resume/answers.yaml, "
          "then uncomment your targeting in config/sources.local.yaml.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="report only, exit 1 when a user file is missing")
    args = ap.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
