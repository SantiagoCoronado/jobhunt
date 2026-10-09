"""First-run setup: create every user-owned file from its tracked example, never overwrite.

    python -m src.init            copy the examples that have no real file yet, make the data dirs,
                                  append the prompt keys an older profile.yaml lacks
    python -m src.init --check    report only, exit 1 when a user file or a profile key is missing

The user-owned files (docs/spec-open-source.md decision 3) are git-ignored and come from the
tracked `<name>.example.<ext>` next to them (`.env.example` is the one suffix form). This never
touches a tracked file and never overwrites an existing real file, so it is safe to re-run.
`config/identity.local.example.yaml` is documentation only and is deliberately NOT copied:
the guard test's identity rule is opt-in (write `config/identity.local.yaml` by hand).

Migration: a profile.yaml written before the prompt keys existed (`candidate_line`,
`role_families`, `work_authorization`, `header_location`, docs/spec-open-source.md section 4)
gets the missing ones APPENDED with defaults derived from its own keys (the name, the target
titles), under a dated comment, so the file keeps every line the user wrote. Keys already
present are never touched; a second run appends nothing.

Migration: a profile.yaml that still carries a `dream_companies:` list (docs/spec-pre-release.md
decision 9) gets it moved into the `dream_companies` table of `data/jobs.db`: every entry is
added (a name the table already has is left as it is), then the list's lines are commented out
in place under a dated note, so nothing the user wrote is lost and a second run moves nothing.
"""
from __future__ import annotations

import argparse
import shutil
from datetime import date
from pathlib import Path

from .config import PROFILE_KEYS, ROOT, default_profile_keys, missing_profile_keys

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


PROFILE = "config/profile.yaml"
KEY_HELP = {
    "candidate_line": "one sentence the triage and match prompts open with (who you are, where, work status)",
    "role_families": "ordered families the prompts use; strength: strongest | core | adjacent",
    "work_authorization": ("summary told to the prompts; header_item rendered in the resume header (\"\" = nothing, "
                           "so set it or the header shows no work status); relocation_regions = config/geo.yaml "
                           "regions relocation_line covers ([] = home only); relocation_header = the header note then"),
    "header_location": "what the tailored resume header must say; \"\" = the master resume's cv.location",
}


def profile_missing_keys(root: Path = ROOT) -> list[str]:
    """The prompt keys the real profile under `root` lacks ([] when the file is absent)."""
    import yaml

    path = root / PROFILE
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return missing_profile_keys(raw) if isinstance(raw, dict) else list(PROFILE_KEYS)


def migration_block(raw: dict, keys: list[str], today: str | None = None) -> str:
    """The YAML text appended to an older profile: one dated comment, then each missing key
    with its derived default and a one-line comment saying who reads it."""
    import yaml

    defaults = default_profile_keys(raw)
    lines = [
        "",
        f"# ---- added by `python -m src.init` on {today or date.today().isoformat()}: the prompt keys from",
        "# docs/spec-open-source.md section 4. The values are derived from the keys above; edit them.",
    ]
    for key in keys:
        lines.append(f"# {key}: {KEY_HELP[key]}")
        lines.append(yaml.safe_dump({key: defaults[key]}, sort_keys=False, allow_unicode=True,
                                    default_flow_style=False, width=100).rstrip())
    return "\n".join(lines) + "\n"


def migrate_profile(root: Path = ROOT, today: str | None = None) -> list[str]:
    """Append the missing prompt keys to the real profile; returns the keys added."""
    import yaml

    keys = profile_missing_keys(root)
    if not keys:
        return []
    path = root / PROFILE
    text = path.read_text(encoding="utf-8")
    raw = yaml.safe_load(text) or {}
    block = migration_block(raw if isinstance(raw, dict) else {}, keys, today)
    path.write_text(text.rstrip("\n") + "\n" + block, encoding="utf-8")
    return keys


DREAM_KEY = "dream_companies"


def _db_path(root: Path) -> Path:
    return root / "data" / "jobs.db"


def profile_dream_list(root: Path = ROOT) -> list[dict]:
    """The dream entries the real profile under `root` still lists ([] when moved or absent)."""
    import yaml

    from .dream import normalize

    path = root / PROFILE
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = raw.get(DREAM_KEY) if isinstance(raw, dict) else None
    if not isinstance(entries, list):
        return []
    return [d for d in (normalize(e) for e in entries) if d]


def key_span(lines: list[str], key: str) -> tuple[int, int] | None:
    """(start, end) of the top-level `key:` block in `lines`: its own line through its last
    indented or list line. None when the key is absent. Shared with src.onboard's writers."""
    start = next((i for i, ln in enumerate(lines) if ln.startswith(f"{key}:")), None)
    if start is None:
        return None
    end = start + 1                       # one past the block's last indented or list line
    for i in range(start + 1, len(lines)):
        ln = lines[i]
        if not ln.strip() or ln.startswith("#"):
            continue                      # blanks and comments inside the list ride along
        if ln[0] in " \t" or ln.startswith("-"):
            end = i + 1
            continue
        break                             # the next top-level key
    return start, end


def comment_out_key(text: str, key: str, note: list[str]) -> str:
    """`text` with the top-level `key:` block (its line and every indented, list or blank line
    under it) turned into comments, preceded by the `note` lines. Unchanged when the key is absent."""
    lines = text.splitlines(keepends=True)
    span = key_span(lines, key)
    if span is None:
        return text
    start, end = span
    block = [("# " + ln if ln.strip() else ln) for ln in lines[start:end]]
    block = [b if b.endswith("\n") else b + "\n" for b in block]
    return "".join(lines[:start] + [n + "\n" for n in note] + block + lines[end:])


def migrate_dream(root: Path = ROOT, today: str | None = None) -> dict[str, list[str]]:
    """Move the profile's dream list into the table, then comment it out under a dated note.
    Returns {'moved': [names added], 'kept': [names the table already had]}; both empty when
    there was nothing to move. The table is written and committed before the profile changes."""
    import yaml

    from . import db

    entries = profile_dream_list(root)
    if not entries:
        return {"moved": [], "kept": []}
    path = root / PROFILE
    text = path.read_text(encoding="utf-8")
    note = [
        f"# ---- moved by `python -m src.init` on {today or date.today().isoformat()}: the dream companies",
        "# now live in the dream_companies table of data/jobs.db (docs/spec-pre-release.md decision 9).",
        "# Edit them with `python -m src.query dream {list|add|rm}` or the TUI's Dream tab. As it was:",
    ]
    new_text = comment_out_key(text, DREAM_KEY, note)
    before = yaml.safe_load(text) or {}
    after = yaml.safe_load(new_text) or {}
    before.pop(DREAM_KEY, None)
    if after != before:                   # the rewrite must remove that one key and nothing else
        raise SystemExit(f"{PROFILE}: could not comment out {DREAM_KEY} cleanly; move it by hand "
                         "(python -m src.query dream add) and delete the list")
    moved, kept = [], []
    conn = db.connect(_db_path(root))
    try:
        for d in entries:
            if db.get_dream(conn, d["name"]):
                kept.append(d["name"])
                continue
            db.add_dream(conn, d["name"], d["match"], d["careers_url"] or None, d["note"] or None)
            moved.append(d["name"])
        conn.commit()
    finally:
        conn.close()
    path.write_text(new_text, encoding="utf-8")
    return {"moved": moved, "kept": kept}


def plan(root: Path = ROOT) -> dict[str, list[str]]:
    """What a run would do: {'copy': [...], 'keep': [...], 'missing_example': [...], 'mkdir': [...],
    'migrate': [<profile keys to append>], 'dream': [<dream names to move into the table>]}."""
    out: dict[str, list[str]] = {"copy": [], "keep": [], "missing_example": [], "mkdir": [],
                                 "migrate": profile_missing_keys(root),
                                 "dream": [d["name"] for d in profile_dream_list(root)]}
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
        for key in p["migrate"]:
            print(f"  missing  {PROFILE}: {key}  (python -m src.init appends a default)")
        if p["dream"]:
            print(f"  pending  {PROFILE}: {DREAM_KEY} ({len(p['dream'])}) still in the profile "
                  "(python -m src.init moves them into the dream_companies table)")
        incomplete = bool(p["copy"] or p["missing_example"] or p["migrate"] or p["dream"])
        print("user files incomplete" if incomplete else "user files complete")
        return 1 if incomplete else 0
    for ex, real in EXAMPLES.items():
        if real in p["copy"]:
            (root / real).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / ex, root / real)
            note = ("empty keys; /jh-setup or the TUI keys tab sets them" if real == ".env"
                    else "an invented person until /jh-setup or your edits replace it")
            print(f"  created  {real}  (from {ex}; {note})")
    for real in p["keep"]:
        print(f"  kept     {real}")
    for ex in p["missing_example"]:
        print(f"  ! no example on disk: {ex}")
    for d in p["mkdir"]:
        (root / d).mkdir(parents=True, exist_ok=True)
        print(f"  mkdir    {d}/")
    if p["migrate"] and PROFILE not in p["copy"]:      # a fresh copy of the example has them all
        added = migrate_profile(root)
        print(f"  migrated {PROFILE}: appended {', '.join(added)} with derived defaults; edit them")
    if p["dream"]:
        res = migrate_dream(root)
        print(f"  migrated {PROFILE}: {DREAM_KEY} moved into data/jobs.db ({len(res['moved'])} added"
              + (f", {len(res['kept'])} already there" if res["kept"] else "") + "); the list is commented "
              "out under a dated note; edit it with `python -m src.query dream` or the TUI")
    for ex in SKIPPED_EXAMPLES:
        print(f"  skipped  {ex}  (documentation; write {real_name(ex)} by hand to enable the identity guard)")
    print("Next: run /jh-setup in your agent CLI (it writes the master resume, the profile and the "
          "sources from your documents), or edit config/profile.yaml, resume/master_resume.yaml and "
          "resume/answers.yaml by hand, then uncomment your targeting in config/sources.local.yaml.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="report only, exit 1 when a user file is missing")
    args = ap.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
