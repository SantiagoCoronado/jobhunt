"""Where a posting's location string points, from the tracked region table config/geo.yaml.

The table is product data (docs/spec-open-source.md decision 7); which region is home comes
from the profile. Three questions the pipeline asks:

  * `hits("Berlin, DE")` -> {"germany"}: the regions one location part names.
  * `outside("London; Austin, TX", scope)` -> False: a string is OUTSIDE a scope of regions when
    at least one part resolves to a region and no part resolves to one inside the scope
    (inside = the region, a region within it, or a region containing it, so "Remote LATAM" is
    inside a scope that holds mexico). Unknown strings are never "outside".
  * `home(profile)` -> {"mexico"}: the home region from `header_location`, else `locations`.

Rules per part, in order, each the calibrated behaviour the tests pin. Every name is found
first and a name inside a longer name is dropped ("california" inside "baja california",
"mexico" inside "new mexico"). Then: a country or region word decides (with any city word next
to it); else a bare US state code ("NY / SF / EMEA") is the US; else a city followed by a
two-letter code is that city's country when the code is the country's ("Berlin, DE",
"Bengaluru, Karnataka, in") and otherwise the US ("Paris, TX", "Durango, CO"); else a state
name decides ("Baja California" is Mexico, "Santa Fe, New Mexico" is the US); else a city
word decides; else the part is unknown. Multi-location strings split on `;`, `|`, `/` and
" or ".

    python -m src.geo "<location>" [--scope region ...]     what a string resolves to
"""
from __future__ import annotations

import argparse
import re
from functools import lru_cache

from .config import CONFIG_DIR, load_yaml

GEO_FILE = CONFIG_DIR / "geo.yaml"
US = "united states"
REMOTE_WORDS = ("remote", "anywhere", "worldwide", "global", "distributed")

_PART_SPLIT = re.compile(r"\s*(?:;|\||/| or )\s*")


def _word_re(words) -> re.Pattern[str]:
    words = sorted({w for w in words if w}, key=len, reverse=True)
    if not words:
        return re.compile(r"(?!x)x")            # matches nothing
    return re.compile(r"(?<![a-z])(?:" + "|".join(re.escape(w) for w in words) + r")(?![a-z])")


@lru_cache(maxsize=1)
def table() -> dict:
    """{region: {aliases, cities, codes, within, state_codes, state_names}}, every list lowercased."""
    data = load_yaml(GEO_FILE)
    raw = data.get("regions") or {}
    out: dict[str, dict] = {}
    for name, block in raw.items():
        block = block or {}
        out[str(name).lower()] = {
            k: [str(x).lower() for x in (block.get(k) or [])]
            for k in ("aliases", "cities", "codes", "within", "states", "state_codes", "state_names")
        }
    for name, block in out.items():
        for parent in block["within"]:
            if parent not in out:
                raise ValueError(f"config/geo.yaml: {name} is within unknown region {parent!r}")
    out["_bare_country_codes"] = {k: [] for k in ("aliases", "cities", "codes", "within", "states", "state_codes", "state_names")}
    out["_bare_country_codes"]["codes"] = [str(c).lower() for c in (data.get("bare_state_codes_that_mean_a_country") or [])]
    return out


def regions() -> list[str]:
    return [r for r in table() if not r.startswith("_")]


def closure(region: str) -> set[str]:
    """The region and every region containing it, transitively."""
    t = table()
    if region not in t:
        raise ValueError(f"config/geo.yaml has no region {region!r} (known: {', '.join(t)})")
    out: set[str] = set()
    todo = [region]
    while todo:
        r = todo.pop()
        if r in out:
            continue
        out.add(r)
        todo.extend(t[r]["within"])
    return out


def contained(region: str) -> set[str]:
    """The region and every region within it, transitively."""
    t = table()
    out = {region}
    changed = True
    while changed:
        changed = False
        for name, block in t.items():
            if name.startswith("_"):
                continue
            if name not in out and any(p in out for p in block["within"]):
                out.add(name)
                changed = True
    return out


@lru_cache(maxsize=1)
def _compiled() -> dict:
    t = {r: b for r, b in table().items() if not r.startswith("_")}
    alias_re = {r: _word_re(b["aliases"]) for r, b in t.items()}
    state_re = {r: _word_re(b["states"] + b["state_names"]) for r, b in t.items() if b["states"] or b["state_names"]}
    city_re = {r: _word_re(b["cities"]) for r, b in t.items() if b["cities"]}
    us = t.get(US) or {"state_codes": [], "state_names": []}
    codes = set(us["state_codes"])
    return {
        "alias": alias_re,
        "state": state_re,
        "city": city_re,
        "state_codes": codes,
        "state_is_also_a_country": codes & set(table()["_bare_country_codes"]["codes"]),
        "state_re": re.compile(r",\s*(" + "|".join(sorted(codes, key=len, reverse=True)) + r")"
                               r"(?:\s*,|\s*$|\s+\d{5}|\s+usa?\b)") if codes else re.compile(r"(?!x)x"),
        "city_codes": {(city, code): r for r, b in t.items() for city in b["cities"] for code in b["codes"]},
    }


def _names(p: str, res: dict, tier: str) -> list[tuple[int, int, str, str]]:
    return [(m.start(), m.end(), r, tier) for r, rx in res.items() for m in rx.finditer(p)]


def hits(part: str) -> set[str]:
    """The regions one location part names (see the module docstring for the order)."""
    c = _compiled()
    p = " ".join(str(part or "").lower().split())
    if not p:
        return set()
    found = _names(p, c["alias"], "alias") + _names(p, c["state"], "state") + _names(p, c["city"], "city")
    # a name inside a longer name is that longer name: "california" in "baja california"
    kept = [m for m in found
            if not any(o is not m and o[0] <= m[0] and m[1] <= o[1] and (o[1] - o[0]) > (m[1] - m[0]) for o in found)]
    aliases = {r for _, _, r, tier in kept if tier == "alias"}
    cities = {(r, p[a:b]) for a, b, r, tier in kept if tier == "city"}
    if aliases:
        return aliases | {r for r, _ in cities}    # "Europe + San Francisco" names both
    bare = p.strip(" ()-.,")
    if bare in c["state_codes"] and bare not in c["state_is_also_a_country"]:
        return {US}
    state = c["state_re"].search(p)
    if state:
        for _region, city in cities:
            if (city, state.group(1)) in c["city_codes"]:
                return {c["city_codes"][(city, state.group(1))]}
        return {US}                                # "Paris, TX", "Durango, CO"
    states = {r for _, _, r, tier in kept if tier == "state"}
    if states:
        return states                              # "Baja California", "Santa Fe, New Mexico"
    if cities:
        return {r for r, _ in cities}
    return set()


def reachable(found: set[str], scope: set[str]) -> bool:
    """True when one of the regions found is inside the scope: the region itself, a region
    within one of the scope's, or a region containing one of them (mexico reaches latam)."""
    for h in found:
        cl = closure(h)
        for s in scope:
            if h in closure(s) or s in cl:
                return True
    return False


def outside(location: str | None, scope: set[str] | list[str] | tuple[str, ...]) -> bool:
    """True when the string names somewhere and none of it is reachable from `scope`.
    Empty scope: nothing is ever outside; callers pass the home region in the scope
    (`tailor_build.relocation_scope`), so an empty scope means no region resolved at all."""
    scope = set(scope or ())
    loc = str(location or "").strip()
    if not loc or not scope:
        return False
    verdicts = []
    for part in _PART_SPLIT.split(loc.lower()):
        if not part:
            continue
        found = hits(part)
        verdicts.append(None if not found else not reachable(found, scope))
    if any(v is False for v in verdicts):
        return False
    return any(v is True for v in verdicts)


def home(profile: dict) -> set[str]:
    """The home region(s): what `header_location` names, else what the `locations` list names.
    Empty when neither resolves (the location prefilter then keeps everything)."""
    found = hits(str(profile.get("header_location") or ""))
    if found:
        return found
    for entry in profile.get("locations") or []:
        found |= hits(str(entry))
    return found


def home_words(home_regions: set[str]) -> list[str]:
    """Every alias and city of the home regions and the regions containing them, plus the
    remote words: a posting naming any of these is reachable from home."""
    t = table()
    words = list(REMOTE_WORDS)
    for r in {c for h in home_regions for c in closure(h)}:
        words += t[r]["aliases"] + t[r]["cities"] + t[r]["states"] + t[r]["state_names"]
    return words


def locked_out_words(home_regions: set[str]) -> list[str]:
    """Every alias, city and state name of a region that is neither home, nor contains home,
    nor sits within home: a non-remote posting naming one of these sits somewhere else."""
    t = table()
    keep = {c for h in home_regions for c in closure(h)} | {c for h in home_regions for c in contained(h)}
    words: list[str] = []
    for r, b in t.items():
        if r in keep or r.startswith("_"):
            continue
        words += b["aliases"] + b["cities"] + b["states"] + b["state_names"]
    return words


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="what a location string resolves to in config/geo.yaml")
    ap.add_argument("location")
    ap.add_argument("--scope", nargs="*", default=None, help="regions to test `outside` against")
    args = ap.parse_args(argv)
    for part in _PART_SPLIT.split(args.location.lower()):
        if part:
            print(f"  {part!r}: {', '.join(sorted(hits(part))) or 'unknown'}")
    if args.scope:
        scope = {r.strip().lower() for r in args.scope if r.strip()}
        unknown = sorted(scope - set(regions()))
        if unknown:
            print(f"unknown region(s): {', '.join(unknown)} (known: {', '.join(regions())})")
            return 1
        print(f"outside {sorted(scope)}: {outside(args.location, scope)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
