"""Tiny YAML config loader shared across scripts."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"

# The user-owned files (docs/spec-open-source.md decision 3): git-ignored, created from the
# tracked `*.example.*` by `python -m src.init`. Every loader resolves them through this table
# at call time, so tests point it at tests/fixtures/ and never read a real person's data.
USER_FILES: dict[str, Path] = {
    "profile": CONFIG_DIR / "profile.yaml",
    "notify": CONFIG_DIR / "notify.yaml",
    "sources_local": CONFIG_DIR / "sources.local.yaml",
    "master_resume": ROOT / "resume" / "master_resume.yaml",
    "answers": ROOT / "resume" / "answers.yaml",
}


def user_file(key: str) -> Path:
    """Path of one user-owned file by logical name (see USER_FILES)."""
    return USER_FILES[key]


def load_yaml(name: str | Path) -> dict:
    import yaml  # PyYAML

    if isinstance(name, Path):
        path = name
    else:
        path = CONFIG_DIR / name if not name.startswith("/") else Path(name)
    if not path.exists():
        raise FileNotFoundError(f"Missing config: {path}. Copy the .example and edit it.")
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_profile() -> dict:
    """config/profile.yaml (or the test fixture): the single authority on what a fit is."""
    return load_yaml(user_file("profile"))


def resume_basename(name: str | None = None) -> str:
    """`<NameParts>Resume`, the stem of every tailored deliverable (docs/spec-open-source.md
    decision 5): NFKD fold to ASCII, keep letters and digits only, join the name parts in
    order, append `Resume`; an empty result falls back to `Resume`.
    "Zoë O'Brien-Smith" gives "ZoeOBrienSmithResume". The name defaults to profile.name."""
    import re
    import unicodedata

    if name is None:
        try:
            name = str(load_profile().get("name") or "")
        except FileNotFoundError:
            name = ""
    folded = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    stem = "".join(re.sub(r"[^A-Za-z0-9]", "", part) for part in folded.split())
    return f"{stem}Resume"


# ---- sources: tracked mechanics + ignored targeting ------------------------------------
#
# config/sources.yaml (tracked) carries adapter mechanics only: endpoints, page sizes,
# `enabled:`, field mappings, and the generic-engineering base of the title gate.
# config/sources.local.yaml (ignored, example tracked) carries the user's targeting: ATS
# tokens, countries, locales, query lists, dream boards, extra title words. `sources()` merges
# them per source block: a list or dict in the local file REPLACES the tracked one, a scalar
# OVERRIDES it, a source that only exists locally is ADDED. docs/spec-open-source.md decision 4.

# Title words that say nothing about the role family on their own (the generic base list
# already covers the engineering nouns); dropped when deriving gate words from the profile.
_TITLE_STOP = frozenset({
    "and", "or", "of", "the", "a", "an", "for", "in", "to", "with", "at", "on",
    "engineer", "engineers", "engineering", "developer", "developers", "development",
    "senior", "sr", "jr", "junior", "staff", "lead", "principal", "head", "director", "manager",
    "management", "ii", "iii", "iv", "product", "products", "program", "project", "technical",
    "specialist", "analyst", "associate", "intern", "internship", "remote", "roles", "role",
})


def title_words(titles: list[str]) -> list[str]:
    """Gate words derived from title strings: every cleaned multi-word phrase plus every
    word not in the stop list. "Software Engineer (AI products)" gives ["software"];
    "Deployment Strategist" gives ["deployment strategist", "deployment", "strategist"].
    Order is first-seen, no duplicates."""
    import re

    out: list[str] = []
    seen: set[str] = set()

    def add(w: str) -> None:
        if w and w not in seen:
            seen.add(w)
            out.append(w)

    for raw in titles:
        text = re.sub(r"\([^)]*\)", " ", str(raw)).lower()
        for phrase in re.split(r"\s*(?:/|,|\bor\b)\s*", text):
            words = [w for w in re.split(r"[^a-z0-9.+#-]+", phrase) if w]
            kept = [w for w in words if w not in _TITLE_STOP and len(w) > 1]
            if len(kept) >= 2:
                add(" ".join(kept))
            for w in kept:
                add(w)
    return out


def merge_sources(base: dict, local: dict | None) -> dict:
    """Per-source deep merge: lists and dicts replace, scalars override, new sources add."""
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in (base or {}).items()}
    for name, block in (local or {}).items():
        if not isinstance(block, dict):
            out[name] = block
            continue
        target = out.get(name)
        if not isinstance(target, dict):
            out[name] = dict(block)
            continue
        for key, val in block.items():
            target[key] = val
    return out


def sources(profile: dict | None = None) -> dict:
    """The merged source config with `title_filter.include` computed: the tracked base list,
    then words from the profile's `target_titles` and `role_families[].titles`, then the
    local file's `title_filter.include_extra`. Callers never read sources.yaml directly."""
    base = load_yaml("sources.yaml")
    local_path = user_file("sources_local")
    local = load_yaml(local_path) if local_path.exists() else {}
    merged = merge_sources(base, local)
    tf = dict(merged.get("title_filter") or {})
    include = list(tf.get("include") or [])
    if profile is None:
        try:
            profile = load_profile()
        except FileNotFoundError:
            profile = {}
    titles = [str(t) for t in (profile.get("target_titles") or [])]
    for fam in profile.get("role_families") or []:
        if isinstance(fam, dict):
            titles += [str(t) for t in (fam.get("titles") or [])]
    extra = list(((local.get("title_filter") or {}).get("include_extra")) or [])
    seen = {str(w).lower() for w in include}
    for w in title_words(titles) + [str(w).lower() for w in extra]:
        if w not in seen:
            seen.add(w)
            include.append(w)
    tf["include"] = include
    tf.pop("include_extra", None)
    merged["title_filter"] = tf
    return merged


# Sources that do nothing useful without the user's targeting (docs/spec-open-source.md
# decision 4): `discover` skips an enabled source whose keys are all missing or empty and
# prints one hint naming config/sources.local.yaml.
TARGETING_KEYS: dict[str, tuple[str, ...]] = {
    "greenhouse": ("tokens",), "lever": ("companies",), "ashby": ("clients",),
    "workable": ("accounts",), "recruitee": ("companies",), "smartrecruiters": ("companies",),
    "personio": ("companies",), "bamboohr": ("companies",), "workday": ("sites",),
    "consider": ("boards",), "teamtailor": ("companies",), "pinpoint": ("companies",),
    "rippling": ("companies",), "dreamsheet": ("file_id",),
    "adzuna": ("countries",), "careerjet": ("locale_code", "location"),
    "getonbrd": ("queries",), "torre": ("queries",), "findwork": ("search",),
    "themuse": ("locations", "categories"), "softserve": ("countries",),
}


def missing_targeting(name: str, cfg: dict) -> tuple[str, ...]:
    """The targeting keys a source needs that are absent or empty in its merged block."""
    return tuple(k for k in TARGETING_KEYS.get(name, ()) if not cfg.get(k))


def notify_setting(key: str, default):
    """Read one key from config/notify.yaml; falls back to default if the file
    is absent (it is gitignored, so fresh clones won't have it)."""
    try:
        return load_yaml(user_file("notify")).get(key, default)
    except FileNotFoundError:
        return default


def followup_days() -> int:
    """Days after applying (or after a contact bump) that a follow-up comes due."""
    raw = notify_setting("followup_days", 7)
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"config/notify.yaml: followup_days must be an integer, got {raw!r}") from None


def shortlist_threshold() -> int:
    """The one shortlist cutoff (profile.yaml: shortlist_threshold, default 70).
    match ingest and the notify digest both read THIS; nothing hardcodes 70."""
    try:
        raw = load_profile().get("shortlist_threshold", 70)
    except FileNotFoundError:
        return 70
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"config/profile.yaml: shortlist_threshold must be an integer, got {raw!r}") from None


_ENV_CACHE: dict | None = None


def load_env() -> dict:
    """Parse ROOT/.env into a dict (cached). Blanks and `# comments` skipped.

    Supports optional `export ` prefix and single/double-quoted values. Does NOT
    mutate os.environ, so real environment variables always win in get_secret().
    """
    global _ENV_CACHE
    if _ENV_CACHE is not None:
        return _ENV_CACHE
    env: dict[str, str] = {}
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key:
                env[key] = val
    _ENV_CACHE = env
    return env


def get_secret(key: str, default: str | None = None) -> str | None:
    """Read a secret: real environment first, then .env, then default."""
    val = os.environ.get(key)
    if val:
        return val
    return load_env().get(key, default)


def main(argv: list[str] | None = None) -> int:
    """`python -m src.config resume-basename` prints the deliverable stem for shell scripts."""
    import argparse

    ap = argparse.ArgumentParser(description="jobhunt config helpers")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("resume-basename", help="print <NameParts>Resume from profile.name")
    args = ap.parse_args(argv)
    if args.cmd == "resume-basename":
        print(resume_basename())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
