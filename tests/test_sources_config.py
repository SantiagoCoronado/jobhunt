"""config.sources(): tracked mechanics + ignored targeting, the derived title gate, and the
discover hint for an enabled source with no targeting (docs/spec-open-source.md decision 4)."""
from __future__ import annotations

from pathlib import Path

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
    assert config.title_words(["Technical Program or Product (AI)"]) == [
        "technical program", "technical", "program", "product"]
    assert config.title_words(["Front-End Engineer", "Frontend Engineer"]) == ["front-end", "frontend"]
    # "engineer" alone is all stop words, so it falls back to itself; the tracked base list
    # already carries it, and sources() dedupes.
    assert config.title_words(["AI Solutions Architect / Engineer"]) == [
        "ai solutions architect", "ai", "solutions", "architect", "engineer"]


def test_title_words_never_leaves_a_role_family_with_no_gate_words():
    """A title of nothing but stop words used to give [], which drops that user's whole
    family at discovery with only a count to show for it. It falls back to the narrower
    noise list instead."""
    assert config.title_words(["Product Manager"]) == ["product manager", "product", "manager"]
    assert config.title_words(["Engineering Manager"]) == ["engineering manager", "engineering", "manager"]
    assert config.title_words(["Technical Program Manager"]) == [
        "technical program manager", "technical", "program", "manager"]
    # Seniority and format words are noise in the fallback too, so they never become gate words.
    assert config.title_words(["Senior Staff Engineer (Remote)"]) == ["engineer"]


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
    for name, groups in config.TARGETING_KEYS.items():
        block = shipped.get(name) or {}
        for k in (k for group in groups for k in group):
            assert not block.get(k), f"{name}.{k} is set in the tracked sources.yaml"
    for name in ("teamtailor", "pinpoint", "rippling", "secretlab"):
        assert not shipped[name].get("enabled"), f"dream board {name} is on in the tracked file"


def test_missing_targeting_names_only_the_empty_keys():
    assert config.missing_targeting("careerjet", {"enabled": True, "locale_code": "en_GB"}) == ("location",)
    assert config.missing_targeting("adzuna", {"enabled": True, "countries": ["gb"]}) == ()
    assert config.missing_targeting("remoteok", {"enabled": True}) == ()


def test_missing_targeting_accepts_the_aliases_the_adapters_read():
    """A key group is satisfied by any of its keys, so a source is never skipped over a
    spelling its own adapter accepts, or over an optional filter it does not need."""
    # adzuna.fetch: `cfg.get("countries") or [cfg["country"]]`
    assert config.missing_targeting("adzuna", {"country": "mx"}) == ()
    # themuse.fetch: locations, location and categories are independent optional filters
    assert config.missing_targeting("themuse", {"categories": ["Engineering"]}) == ()
    assert config.missing_targeting("themuse", {"location": "Mexico"}) == ()
    assert config.missing_targeting("themuse", {}) == ("locations|location|categories",)
    assert config.missing_targeting("jobicy", {"enabled": True}) == ("tags",)      # PR #21 review
    assert config.missing_targeting("jobicy", {"tags": ["react"]}) == ()
    # careerjet.fetch raises without both, so both stay required and are named separately
    assert config.missing_targeting("careerjet", {}) == ("locale_code", "location")


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


# ---- the loader rule: no module reaches around config for a user-owned file ----

def _src_modules() -> list[Path]:
    return sorted(p for p in (config.ROOT / "src").rglob("*.py"))


def test_no_module_loads_a_user_owned_file_by_bare_name():
    """USER_FILES is the one table the loaders resolve through (tests point it at the
    fixtures). A `load_yaml("profile.yaml")` anywhere bypasses it and reads a real person's
    file even under the suite."""
    bad = []
    for path in _src_modules():
        text = path.read_text(encoding="utf-8")
        for name in ("profile.yaml", "notify.yaml", "sources.local.yaml", "master_resume.yaml", "answers.yaml"):
            for quote in ('"', "'"):
                if f"load_yaml({quote}{name}{quote}" in text:
                    bad.append(f"{path.relative_to(config.ROOT)}: load_yaml({name})")
    assert bad == [], f"use load_yaml(user_file(...)) instead: {bad}"


def test_only_config_reads_sources_yaml_directly():
    """Targeting lives in sources.local.yaml, so the tracked file alone is half a config:
    `torre.backfill_eligibility` read it that way and silently fell back to one default
    query. Everything outside config.py goes through config.sources()."""
    bad = [
        str(path.relative_to(config.ROOT))
        for path in _src_modules()
        if path.name != "config.py" and ('load_yaml("sources.yaml"' in path.read_text(encoding="utf-8")
                                         or "load_yaml('sources.yaml'" in path.read_text(encoding="utf-8"))
    ]
    assert bad == [], f"read the merged config with config.sources() instead: {bad}"
