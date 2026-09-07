"""config.sources(): tracked mechanics + ignored targeting, the derived title gate, and the
discover hint for an enabled source with no targeting (docs/spec-open-source.md decision 4)."""
from __future__ import annotations

import yaml

from src import config, discover
from src.db import connect


def test_merge_sources_lists_replace_scalars_override_new_sources_add():
    base = {"greenhouse": {"enabled": True, "tokens": ["a"], "names": {"a": "A"}},
            "adzuna": {"enabled": True, "pages": 3}}
    local = {"greenhouse": {"tokens": ["b", "c"]},
             "adzuna": {"pages": 1, "countries": ["gb"]},
             "myboard": {"enabled": True, "url": "x"}}
    m = config.merge_sources(base, local)
    assert m["greenhouse"] == {"enabled": True, "tokens": ["b", "c"], "names": {"a": "A"}}
    assert m["adzuna"] == {"enabled": True, "pages": 1, "countries": ["gb"]}
    assert m["myboard"] == {"enabled": True, "url": "x"}
    assert base["greenhouse"]["tokens"] == ["a"]  # inputs untouched


def test_title_words_phrases_and_words_minus_stop_list():
    assert config.title_words(["Software Engineer (AI products)"]) == ["software"]
    assert config.title_words(["Deployment Strategist"]) == ["deployment strategist", "deployment", "strategist"]
    assert config.title_words(["Technical Program or Product (AI)"]) == []
    assert config.title_words(["Front-End Engineer", "Frontend Engineer"]) == ["front-end", "frontend"]
    assert config.title_words(["AI Solutions Architect / Engineer"]) == [
        "ai solutions architect", "ai", "solutions", "architect"]


def test_sources_derives_include_from_profile_and_local_extra(tmp_path, monkeypatch):
    base = tmp_path / "sources.yaml"
    base.write_text(yaml.safe_dump({
        "greenhouse": {"enabled": True},
        "title_filter": {"enabled": True, "include": ["engineer"], "exclude": ["nurse"]},
    }))
    local = tmp_path / "sources.local.yaml"
    local.write_text(yaml.safe_dump({
        "greenhouse": {"tokens": ["acme"]},
        "title_filter": {"include_extra": ["Strategist", "engineer"]},
    }))
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
    monkeypatch.setitem(config.USER_FILES, "sources_local", local)
    prof = {"target_titles": ["Deployment Lead"], "role_families": [{"titles": ["UI Engineer"]}]}
    m = config.sources(prof)
    assert m["greenhouse"] == {"enabled": True, "tokens": ["acme"]}
    assert m["title_filter"]["include"] == ["engineer", "deployment", "ui", "strategist"]
    assert "include_extra" not in m["title_filter"]
    assert m["title_filter"]["exclude"] == ["nurse"]


def test_sources_without_local_file_or_profile_still_loads(tmp_path, monkeypatch):
    (tmp_path / "sources.yaml").write_text(yaml.safe_dump({"title_filter": {"include": ["engineer"]}}))
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
    monkeypatch.setitem(config.USER_FILES, "sources_local", tmp_path / "absent.yaml")
    monkeypatch.setitem(config.USER_FILES, "profile", tmp_path / "absent-profile.yaml")
    assert config.sources()["title_filter"]["include"] == ["engineer"]


def test_shipped_sources_yaml_carries_no_targeting():
    """Every targeting key lives in sources.local.yaml; the tracked file only has mechanics."""
    shipped = yaml.safe_load((config.CONFIG_DIR / "sources.yaml").read_text())
    for name, keys in config.TARGETING_KEYS.items():
        block = shipped.get(name) or {}
        for k in keys:
            assert not block.get(k), f"{name}.{k} is set in the tracked sources.yaml"
    for name in ("teamtailor", "pinpoint", "rippling", "secretlab", "dreamsheet"):
        assert not shipped[name].get("enabled"), f"dream board {name} is on in the tracked file"


def test_missing_targeting_names_only_the_empty_keys():
    assert config.missing_targeting("careerjet", {"enabled": True, "locale_code": "en_GB"}) == ("location",)
    assert config.missing_targeting("adzuna", {"enabled": True, "countries": ["gb"]}) == ()
    assert config.missing_targeting("remoteok", {"enabled": True}) == ()


def test_discover_skips_untargeted_sources_with_one_hint(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(discover, "ADAPTERS", ["greenhouse", "careerjet"])
    monkeypatch.setattr(discover, "load_sources", lambda: {
        "greenhouse": {"enabled": True}, "careerjet": {"enabled": True, "location": "Remote"},
        "title_filter": {"enabled": True, "include": ["engineer"]}})
    monkeypatch.setattr(discover, "connect", lambda: connect(tmp_path / "jobs.db"))
    discover.main()
    out = capsys.readouterr().out
    assert "config/sources.local.yaml" in out
    assert "greenhouse (tokens)" in out and "careerjet (locale_code)" in out
    assert "FAILED" not in out
