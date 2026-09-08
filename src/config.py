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


# ---- the profile-driven prompt keys (docs/spec-open-source.md section 4) -----------------
#
# `candidate_line`, `role_families`, `work_authorization` and `header_location` are the slots
# every prompt and every location or visa constant in the code read from; nothing names a
# person, a city or a visa outside profile.yaml. `profile()` is the validated view with
# defaults, so a profile written before these keys existed still loads: the candidate line
# falls back to the name, the families to one family built from `target_titles`, the work
# authorization to empty strings (nothing rendered, nothing claimed) and the header location
# to "" (callers fall back to the master resume's `cv.location`).

PROFILE_KEYS = ("candidate_line", "role_families", "work_authorization", "header_location")
STRENGTHS = ("strongest", "core", "adjacent")


def default_profile_keys(raw: dict) -> dict:
    """The derived defaults for the four keys, from the keys an older profile already has."""
    name = str(raw.get("name") or "").strip()
    titles = [str(t) for t in (raw.get("target_titles") or [])]
    skills = [str(s) for s in (raw.get("must_have_skills") or [])][:8]
    return {
        "candidate_line": name,
        "role_families": [{"key": "A", "name": "target roles", "titles": titles,
                           "skills": skills, "strength": "core"}] if titles else [],
        "work_authorization": {"summary": "", "header_item": "", "relocation_header": "",
                               "relocation_regions": []},
        "header_location": "",
    }


def _validate_families(raw_fams) -> list[dict]:
    if not isinstance(raw_fams, list):
        raise ValueError("config/profile.yaml: role_families must be a list of families")
    out: list[dict] = []
    seen: set[str] = set()
    for i, fam in enumerate(raw_fams):
        if not isinstance(fam, dict):
            raise ValueError(f"config/profile.yaml: role_families[{i}] must be a mapping")
        key = str(fam.get("key") or "").strip()
        if not key:
            raise ValueError(f"config/profile.yaml: role_families[{i}] needs a `key` (A, B, ...)")
        if key in seen:
            raise ValueError(f"config/profile.yaml: role_families key {key!r} appears twice")
        seen.add(key)
        strength = str(fam.get("strength") or "core").strip().lower()
        if strength not in STRENGTHS:
            raise ValueError(f"config/profile.yaml: role_families[{key}].strength must be one of "
                             f"{', '.join(STRENGTHS)}, got {strength!r}")
        titles = fam.get("titles") or []
        if not isinstance(titles, list) or not titles:
            raise ValueError(f"config/profile.yaml: role_families[{key}] needs a non-empty `titles` list")
        skills = fam.get("skills") or []
        if not isinstance(skills, list):
            raise ValueError(f"config/profile.yaml: role_families[{key}].skills must be a list")
        entry = {
            "key": key,
            "name": str(fam.get("name") or "").strip() or f"family {key}",
            "titles": [str(t) for t in titles],
            "skills": [str(s) for s in skills],
            "strength": strength,
        }
        match = fam.get("match")
        if match is not None:
            if not isinstance(match, list) or not all(isinstance(m, str) and m.strip() for m in match):
                raise ValueError(f"config/profile.yaml: role_families[{key}].match must be a list of phrases")
            entry["match"] = [m.strip() for m in match]
        if fam.get("note"):
            entry["note"] = " ".join(str(fam["note"]).split())
        if i > 0 and not entry.get("match") and not title_words(list(entry["titles"])):
            raise ValueError(f"config/profile.yaml: role_families[{key}] has no title word to match on "
                             f"(titles {entry['titles']}); add a role word to a title or a `match` list")
        out.append(entry)
    return out


def profile(raw: dict | None = None) -> dict:
    """The profile with the four prompt keys validated and defaulted. Every other key is
    passed through untouched. Raises ValueError naming the key on a malformed value."""
    if raw is None:
        raw = load_profile()
    out = dict(raw)
    defaults = default_profile_keys(raw)
    for key in ("candidate_line", "header_location"):
        val = raw.get(key)
        if val is None:
            out[key] = defaults[key]
        elif isinstance(val, str):
            out[key] = " ".join(val.split())
        else:
            raise ValueError(f"config/profile.yaml: {key} must be a string")
    fams = raw.get("role_families")
    out["role_families"] = _validate_families(fams) if fams is not None else defaults["role_families"]
    wa = raw.get("work_authorization")
    if wa is None:
        out["work_authorization"] = defaults["work_authorization"]
    elif isinstance(wa, dict):
        strings = ("summary", "header_item", "relocation_header")
        for k, v in wa.items():
            if k in strings and v is not None and not isinstance(v, str):
                raise ValueError(f"config/profile.yaml: work_authorization.{k} must be a string")
        regions = wa.get("relocation_regions") or []
        if not isinstance(regions, list) or not all(isinstance(r, str) for r in regions):
            raise ValueError("config/profile.yaml: work_authorization.relocation_regions must be a list of "
                             "region names from config/geo.yaml")
        from . import geo   # geo imports this module; resolved lazily

        known = geo.regions()
        unknown = [r for r in regions if r.strip().lower() not in known]
        if unknown:
            raise ValueError(f"config/profile.yaml: work_authorization.relocation_regions names no region in "
                             f"config/geo.yaml: {', '.join(unknown)} (known: {', '.join(known)})")
        out["work_authorization"] = {
            **{k: " ".join(str(wa.get(k) or "").split()) for k in strings},
            "relocation_regions": [r.strip().lower() for r in regions],
            **{k: v for k, v in wa.items() if k not in strings and k != "relocation_regions"},
        }
    else:
        raise ValueError("config/profile.yaml: work_authorization must be a mapping with summary and header_item")
    return out


_WARNED: set[str] = set()


def safe_profile() -> dict:
    """`profile()` for a command that only degrades without one: a missing file gives {}, a
    malformed key prints the validation error once (stderr) and gives the derived defaults
    for the four prompt keys, so `python -m src.stats funnel` never tracebacks on a typo in
    `strength:`. `python -m src.config check` is where the error is meant to be read."""
    import sys

    try:
        raw = load_profile()
    except FileNotFoundError:
        return {}
    try:
        return profile(raw)
    except ValueError as e:
        if str(e) not in _WARNED:
            _WARNED.add(str(e))
            print(f"  ! {e}; using defaults for the prompt keys (python -m src.config check)", file=sys.stderr)
        return profile({k: v for k, v in raw.items() if k not in PROFILE_KEYS})


def missing_profile_keys(raw: dict) -> list[str]:
    """The prompt keys an existing profile does not carry yet (what `src.init` migrates)."""
    return [k for k in PROFILE_KEYS if k not in raw]


def families_text(prof: dict | None = None) -> str:
    """`role_families` rendered as the lettered list the triage and match prompts open with:
    one line per family, key, name, titles, skills, and a closing line naming the strongest
    families, so a prompt never restates them by hand. Empty families give ""."""
    if prof is None:
        prof = profile()
    fams = prof.get("role_families") or []
    if not fams:
        return ""
    lines = [f"{len(fams)} role famil{'y' if len(fams) == 1 else 'ies'}, ALL in-scope:"]
    for fam in fams:
        bits = ", ".join(fam["titles"])
        if fam.get("skills"):
            bits += "; " + ", ".join(fam["skills"])
        lines.append(f"({fam['key']}) {fam['name']} ({bits})")
        if fam.get("note"):
            lines.append(f"    {fam['note']}")
    strongest = [f["key"] for f in fams if f["strength"] == "strongest"]
    adjacent = [f["key"] for f in fams if f["strength"] == "adjacent"]
    if strongest:
        lines.append(f"{' and '.join(strongest)} {'is' if len(strongest) == 1 else 'are'} the candidate's "
                     f"STRONGEST position{'' if len(strongest) == 1 else 's'}: bucket good ones 2-3.")
    if adjacent:
        lines.append(f"{' and '.join(adjacent)} {'is' if len(adjacent) == 1 else 'are'} adjacent: "
                     "in scope, weighted below the core families.")
    return "\n".join(lines)


def candidate_text(prof: dict | None = None) -> str:
    """The candidate block a prompt inlines: `Candidate: <candidate_line>`, the families,
    and the work-authorization summary when the profile carries one."""
    if prof is None:
        prof = profile()
    lines = [f"Candidate: {prof['candidate_line']}"] if prof.get("candidate_line") else []
    fams = families_text(prof)
    if fams:
        lines.append(fams)
    summary = (prof.get("work_authorization") or {}).get("summary")
    if summary:
        lines.append(f"Work authorization: {summary}")
    return "\n".join(lines)


def resume_basename(name: str | None = None) -> str:
    """`<NameParts>Resume`, the stem of every tailored deliverable (docs/spec-open-source.md
    decision 5): NFKD fold to ASCII, keep letters and digits only, join the name parts in
    order, append `Resume`; an empty result falls back to `Resume`.
    "Zoë O'Brien-Smith" gives "ZoeOBrienSmithResume". The name defaults to profile.name; a
    `resume_basename:` key in the profile overrides the stem (same normalization, `Resume`
    appended once), for a shorter form of a long name."""
    import re
    import unicodedata

    def fold(text: str) -> str:
        ascii_text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
        return "".join(re.sub(r"[^A-Za-z0-9]", "", part) for part in ascii_text.split())

    if name is None:
        try:
            prof = load_profile()
        except FileNotFoundError:
            prof = {}
        override = fold(str(prof.get("resume_basename") or ""))
        if override:
            return override if override.endswith("Resume") else f"{override}Resume"
        name = str(prof.get("name") or "")
    return f"{fold(name)}Resume"


# ---- sources: tracked mechanics + ignored targeting ------------------------------------
#
# config/sources.yaml (tracked) carries adapter mechanics only: endpoints, page sizes,
# `enabled:`, field mappings, and the generic-engineering base of the title gate.
# config/sources.local.yaml (ignored, example tracked) carries the user's targeting: ATS
# tokens, countries, locales, query lists, dream boards, extra title words. `sources()` merges
# them per source block: a list or dict in the local file REPLACES the tracked one, a scalar
# OVERRIDES it, a source that only exists locally is ADDED. docs/spec-open-source.md decision 4.

# Words that carry no role family at all: grammar, seniority, and posting format. Dropped
# from every title, and never the reason a title yields no gate words.
_TITLE_NOISE = frozenset({
    "and", "or", "of", "the", "a", "an", "for", "in", "to", "with", "at", "on",
    "senior", "sr", "jr", "junior", "staff", "principal", "associate",
    "ii", "iii", "iv", "intern", "internship", "remote", "roles", "role",
})

# Title words that say nothing about the role family on their own (the generic base list
# already covers the engineering nouns); dropped when deriving gate words from the profile.
_TITLE_STOP = _TITLE_NOISE | frozenset({
    "engineer", "engineers", "engineering", "developer", "developers", "development",
    "lead", "head", "director", "manager", "management", "product", "products",
    "program", "project", "technical", "specialist", "analyst",
})


def title_words(titles: list[str]) -> list[str]:
    """Gate words derived from title strings: every cleaned multi-word phrase plus every
    word not in the stop list. "Software Engineer (AI products)" gives ["software"];
    "Deployment Strategist" gives ["deployment strategist", "deployment", "strategist"].
    Order is first-seen, no duplicates.

    A title made entirely of stop words never yields nothing: "Product Manager" would leave
    no gate words at all and drop that user's whole role family at discovery, so such a
    phrase falls back to the narrower noise list and gives
    ["product manager", "product", "manager"]."""
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
            if not kept:
                kept = [w for w in words if w not in _TITLE_NOISE and len(w) > 1]
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
# decision 4): `discover` skips an enabled source whose targeting is missing or empty and
# prints one hint naming config/sources.local.yaml.
#
# One entry per source, listing the groups of keys it needs. A group holds the keys the
# adapter accepts interchangeably (`adzuna` reads `countries:` or singular `country:`) or
# the independent filters any one of which targets the source (`themuse` narrows by
# location, by category, or by both). A group is satisfied when any of its keys is set, and
# a source counts as targeted once every group is satisfied, so `careerjet`, which raises
# without both, keeps needing `locale_code:` and `location:`.
TARGETING_KEYS: dict[str, tuple[tuple[str, ...], ...]] = {
    "greenhouse": (("tokens",),), "lever": (("companies",),), "ashby": (("clients",),),
    "workable": (("accounts",),), "recruitee": (("companies",),),
    "smartrecruiters": (("companies",),), "personio": (("companies",),),
    "bamboohr": (("companies",),), "workday": (("sites",),), "consider": (("boards",),),
    "teamtailor": (("companies",),), "pinpoint": (("companies",),),
    "rippling": (("companies",),), "dreamsheet": (("file_id",),),
    "adzuna": (("countries", "country"),), "careerjet": (("locale_code",), ("location",)),
    "getonbrd": (("queries",),), "torre": (("queries",),), "findwork": (("search",),),
    "themuse": (("locations", "location", "categories"),), "softserve": (("countries",),),
    "jobicy": (("tags",),),
}


def missing_targeting(name: str, cfg: dict) -> tuple[str, ...]:
    """The targeting a source needs that its merged block leaves absent or empty: one entry
    per unsatisfied key group, alternatives joined by `|` for the hint discover prints."""
    return tuple(
        "|".join(group)
        for group in TARGETING_KEYS.get(name, ())
        if not any(cfg.get(k) for k in group)
    )


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
    """`python -m src.config resume-basename` prints the deliverable stem for shell scripts;
    `python -m src.config candidate` prints the candidate block a prompt inlines (the
    candidate line, the lettered role families, the work-authorization summary);
    `python -m src.config check` validates the profile's prompt keys and lists missing ones."""
    import argparse

    ap = argparse.ArgumentParser(description="jobhunt config helpers")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("resume-basename", help="print <NameParts>Resume from profile.name")
    sub.add_parser("candidate", help="print the candidate block for prompts (candidate_line, role_families)")
    sub.add_parser("check", help="validate the profile's prompt keys; exit 1 on a malformed or missing one")
    args = ap.parse_args(argv)
    if args.cmd == "resume-basename":
        print(resume_basename())
    elif args.cmd == "candidate":
        try:
            print(candidate_text())
        except ValueError as e:
            print(f"  ! {e}")
            return 1
    elif args.cmd == "check":
        raw = load_profile()
        try:
            profile(raw)
        except ValueError as e:
            print(f"  ! {e}")
            return 1
        missing = missing_profile_keys(raw)
        for k in missing:
            print(f"  missing  {k}  (python -m src.init appends a default; edit it)")
        print("profile keys complete" if not missing else "profile keys incomplete")
        return 1 if missing else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
