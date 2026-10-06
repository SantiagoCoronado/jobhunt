"""The region gate (docs/spec-pre-release.md decision 10): every tracked source block declares
`regions:`, `config.sources()` turns off a source whose regions miss the profile's coverage,
`enabled:` in sources.local.yaml forces it either way, and `discover` prints one line per
source it skipped by region, naming that key."""
from __future__ import annotations

import yaml

from src import config, discover, geo
from src.db import connect

# Shaped like a candidate at home in Latin America who would relocate to the US. Invented, and
# deliberately no city: only the region words the gate resolves.
LATAM_PROFILE = {
    "header_location": "Mexico",
    "locations": ["Remote (LATAM)", "Remote (worldwide)", "Mexico"],
    "work_authorization": {"relocation_regions": ["united states"]},
}


def _shipped() -> dict:
    return yaml.safe_load((config.CONFIG_DIR / "sources.yaml").read_text())


def _write_local(tmp_path, monkeypatch, data: dict) -> None:
    local = tmp_path / "sources.local.yaml"
    local.write_text(yaml.safe_dump(data))
    monkeypatch.setitem(config.USER_FILES, "sources_local", local)


def test_every_tracked_block_declares_known_regions():
    known = set(geo.regions()) | {config.GLOBAL}
    for name, block in _shipped().items():
        if name == "title_filter":
            continue
        regions = block.get("regions")
        assert isinstance(regions, list) and regions, f"{name} declares no regions: list"
        unknown = [r for r in regions if r not in known]
        assert not unknown, f"{name}: {unknown} is not a config/geo.yaml region nor global"


def test_shipped_tags_latam_europe_and_global_as_the_spec_says():
    shipped = _shipped()
    for name in ("getonbrd", "torre"):
        assert shipped[name]["regions"] == ["latam"]
    assert shipped["arbeitnow"]["regions"] == ["europe"]
    for name in ("remoteok", "remotive", "weworkremotely", "hackernews", "himalayas", "adzuna",
                 "greenhouse", "lever", "ashby", "smartrecruiters", "workday", "personio"):
        assert shipped[name]["regions"] == ["global"], name


def test_lisbon_fixture_covers_europe_not_latam():
    cover = config.coverage(config.load_profile())
    assert cover and geo.reachable({"europe"}, cover)
    assert not geo.reachable({"latam"}, cover)


def test_coverage_counts_locations_header_and_relocation_regions():
    cover = config.coverage(LATAM_PROFILE)
    assert {"latam", "mexico", "united states"} <= cover
    assert config.coverage({}) == set()
    assert config.coverage({"locations": ["Remote (worldwide)"]}) == set()


def test_meets_global_contained_and_containing_regions():
    assert config.meets(["global"], {"portugal"})
    assert config.meets(["europe"], {"portugal"})          # a European board serves Lisbon
    assert config.meets(["germany"], {"europe"})           # a German board serves "Europe"
    assert not config.meets(["latam"], {"portugal", "europe"})
    assert config.meets(["latam"], {"mexico"})
    assert not config.meets(["europe"], {"mexico", "united states"})
    assert not config.meets(["no-such-region"], {"mexico"})


def test_lisbon_profile_turns_latam_sources_off_and_keeps_the_rest():
    m = config.sources()
    for name in ("getonbrd", "torre"):
        assert m[name]["enabled"] is False
        assert m[name][config.REGION_GATED]["regions"] == ["latam"]
    for name in ("arbeitnow", "greenhouse", "remoteok", "softserve"):
        assert m[name]["enabled"] is True, name
        assert config.REGION_GATED not in m[name]
    # a tracked source that was already off is not "skipped by region"
    assert config.REGION_GATED not in m["workable"]


def test_latam_profile_keeps_latam_sources_and_turns_europe_off():
    m = config.sources(LATAM_PROFILE)
    for name in ("getonbrd", "torre", "softserve", "greenhouse", "adzuna", "careerjet"):
        assert m[name]["enabled"] is True, name
    assert m["arbeitnow"]["enabled"] is False
    assert m["arbeitnow"][config.REGION_GATED]["regions"] == ["europe"]


def test_local_enabled_forces_a_source_either_way(tmp_path, monkeypatch):
    _write_local(tmp_path, monkeypatch, {
        "getonbrd": {"enabled": True, "queries": ["react"]},
        "greenhouse": {"enabled": False},
    })
    m = config.sources()                                    # the Lisbon fixture profile
    assert m["getonbrd"]["enabled"] is True and config.REGION_GATED not in m["getonbrd"]
    assert m["greenhouse"]["enabled"] is False and config.REGION_GATED not in m["greenhouse"]


def test_a_block_without_regions_counts_as_global(tmp_path, monkeypatch):
    (tmp_path / "sources.yaml").write_text(yaml.safe_dump({
        "myboard": {"enabled": True},
        "latboard": {"enabled": True, "regions": ["latam"]},
        "title_filter": {"include": ["engineer"]},
    }))
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
    monkeypatch.setitem(config.USER_FILES, "sources_local", tmp_path / "absent.yaml")
    m = config.sources({"locations": ["Lisbon"]})
    assert m["myboard"] == {"enabled": True}
    assert m["latboard"]["enabled"] is False


def test_no_coverage_gates_nothing():
    """A profile whose locations name no geo.yaml region: nothing is known to be out of reach."""
    m = config.sources({"locations": ["Remote (worldwide)"]})
    assert m["getonbrd"]["enabled"] is True and m["arbeitnow"]["enabled"] is True


def test_discover_prints_one_line_per_region_skip_naming_the_forcing_key(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(discover, "ADAPTERS", ["getonbrd", "torre", "workable"])
    monkeypatch.setattr(discover, "load_sources", lambda: config.sources())
    monkeypatch.setattr(discover, "connect", lambda: connect(tmp_path / "jobs.db"))
    discover.main()
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if "off by region" in ln]
    assert len(lines) == 2
    assert "getonbrd" in lines[0] and "`getonbrd: {enabled: true}`" in lines[0]
    assert "config/sources.local.yaml" in lines[0] and "latam" in lines[0]
    assert "torre" in lines[1]
    assert "workable" not in out
    assert "FAILED" not in out
