"""The European boards (docs/sources-europe.md) against fixtures trimmed from real responses
recorded 2026-10-06 (tests/fixtures/sources/), no network; and the region gate keeping them
off for a profile that does not cover Europe."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import src.adapters.berlinstartupjobs as bsj
import src.adapters.jobindex as jobindex
import src.adapters.jobtech as jobtech
from src import config, discover

FIX = Path(__file__).resolve().parent / "fixtures" / "sources"
EUROPEAN = ("jobtech", "jobindex", "berlinstartupjobs")


def _jobtech_payload() -> dict:
    return json.loads((FIX / "jobtech_search.json").read_text(encoding="utf-8"))


def test_jobtech_normalizes_a_real_search_response(monkeypatch):
    calls = []

    def fake_get_json(url, params=None, **kw):
        calls.append(params)
        return _jobtech_payload()

    monkeypatch.setattr(jobtech, "get_json", fake_get_json)
    jobs = jobtech.fetch({"queries": ["react"], "limit": 100, "pages": 2})
    # two hits, fewer than the limit, so the second page is never asked for
    assert calls == [{"q": "react", "limit": 100, "offset": 0}]
    assert [j.external_id for j in jobs] == ["31493144", "31256399"]
    j = jobs[1]
    assert j.source == "jobtech"
    assert j.title == "Senior Frontend developer– React"
    assert j.company == "Nexer AB"
    assert j.location == "Göteborg, Sweden"
    assert j.url == "https://arbetsformedlingen.se/platsbanken/annonser/31256399"
    assert j.description and not j.remote
    assert j.to_row()["posted_at"] == "2026-07-07T16:04:30+00:00"
    # an ad whose address has no city still names the country
    assert jobs[0].location.endswith("Sweden")


def test_jobtech_failed_query_skips_not_raises(monkeypatch, capsys):
    def boom(url, **kw):
        raise ValueError("HTTP 500")

    monkeypatch.setattr(jobtech, "get_json", boom)
    assert jobtech.fetch({"queries": ["react"]}) == []
    assert "failed" in capsys.readouterr().out


def test_jobindex_normalizes_a_real_feed(monkeypatch):
    raw = (FIX / "jobindex_search.rss").read_bytes().decode("iso-8859-1")
    monkeypatch.setattr(jobindex, "get_text", lambda url, **kw: raw)
    jobs = jobindex.fetch({"queries": ["react", "frontend"]})     # same feed twice: deduped
    assert [j.external_id for j in jobs] == ["1704690", "1704198", "1703573"]
    j = jobs[1]
    assert (j.title, j.company) == ("Software Developer", "Grundfos A/S")
    assert j.location == "Bjerringbro, Hybrid position, Denmark"
    assert j.url == "https://www.jobindex.dk/vis-job/h1704198"
    assert j.source == "jobindex" and "Manufacturing Execution Systems" in j.description
    # a company name the title cannot split on its last comma comes from the logo's alt text
    assert jobs[2].company == "Nordisk Film"
    assert jobs[2].title == "Social Media & Influencer Specialist for PlayStation, Nordisk Interactive"
    assert jobs[0].location == "København Ø, Denmark"


def test_berlinstartupjobs_normalizes_a_real_feed_and_stops_at_the_404(monkeypatch):
    raw = (FIX / "berlinstartupjobs_engineering.rss").read_text(encoding="utf-8")
    pages = []

    def fake_get_text(url, params=None, **kw):
        pages.append((params or {}).get("paged", 1))
        if pages[-1] > 1:
            raise ValueError("404 Client Error")
        return raw

    monkeypatch.setattr(bsj, "get_text", fake_get_text)
    jobs = bsj.fetch({"pages": 3})
    assert pages == [1, 2]
    assert [j.external_id for j in jobs] == ["452945", "452868", "452858"]
    j = jobs[1]
    assert (j.title, j.company) == ("Senior Software Engineer – Node.js (m/f/d)", "Solarize")
    assert j.location == "Berlin, Germany" and j.source == "berlinstartupjobs"
    assert jobs[0].remote is True and j.remote is False
    assert j.url.startswith("https://berlinstartupjobs.com/engineering/")


@pytest.mark.parametrize("name", EUROPEAN)
def test_european_boards_are_wired_and_country_gated(name):
    assert name in discover.ADAPTERS
    import yaml

    block = yaml.safe_load((config.CONFIG_DIR / "sources.yaml").read_text())[name]
    assert block["enabled"] is True
    assert block["regions"] in (["sweden"], ["denmark"], ["germany"])


def test_european_boards_off_for_a_profile_outside_europe():
    prof = {"header_location": "Mexico", "locations": ["Remote (LATAM)"],
            "work_authorization": {"relocation_regions": ["united states"]}}
    m = config.sources(prof)
    for name in EUROPEAN:
        assert m[name]["enabled"] is False, name
        assert m[name][config.REGION_GATED]["regions"]


def test_european_boards_on_for_the_lisbon_fixture():
    """The fixture covers europe through relocation_regions, so every European country board
    meets it; a profile at home in Portugal only would get none of them."""
    m = config.sources()
    for name in EUROPEAN:
        assert m[name]["enabled"] is True, name
    only_portugal = config.sources({"locations": ["Lisbon"]})
    for name in EUROPEAN:
        assert only_portugal[name]["enabled"] is False, name
