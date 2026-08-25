"""Adapter fetch() against recorded fixtures, no network. Greenhouse and adzuna
are the templates; add a fixture test whenever an adapter's parsing changes."""
import pytest

import src.adapters.adzuna as adzuna
import src.adapters.greenhouse as greenhouse

GREENHOUSE_PAYLOAD = {
    "jobs": [
        {"id": 123, "absolute_url": "https://boards.greenhouse.io/acme/jobs/123",
         "title": "AI Engineer", "location": {"name": "Remote - Mexico"},
         "content": "<p>Build &amp; ship</p>", "updated_at": "2026-07-15T10:00:00Z"},
        {"id": 124, "absolute_url": "https://boards.greenhouse.io/acme/jobs/124",
         "title": "Office Manager", "location": {"name": "NYC"},
         "content": "x", "updated_at": None},
    ]
}


def test_greenhouse_fetch_normalizes(monkeypatch):
    monkeypatch.setattr(greenhouse, "get_json", lambda url, **kw: GREENHOUSE_PAYLOAD)
    jobs = greenhouse.fetch({"tokens": ["acme-corp"]})
    assert [j.external_id for j in jobs] == ["123", "124"]
    j = jobs[0]
    assert j.source == "greenhouse"
    assert j.company == "Acme Corp"
    assert j.remote is True and jobs[1].remote is False
    assert j.description == "Build & ship"  # HTML stripped, entity intact
    assert j.to_row()["posted_at"] == "2026-07-15T10:00:00+00:00"


def test_greenhouse_bad_token_skips_not_raises(monkeypatch, capsys):
    def boom(url, **kw):
        raise ValueError("HTTP 404")
    monkeypatch.setattr(greenhouse, "get_json", boom)
    assert greenhouse.fetch({"tokens": ["dead"]}) == []
    assert "failed" in capsys.readouterr().out


ADZUNA_PAGE = {
    "results": [
        {"id": 555, "redirect_url": "https://adzuna.com.mx/details/555",
         "title": "Remote AI Dev", "location": {"display_name": "Ciudad de México"},
         "company": {"display_name": "MexCo"}, "description": "<b>hola</b>",
         "salary_min": "40000.0", "salary_max": None, "created": "2026-07-14",
         "category": {"label": "IT Jobs"}},
        {"redirect_url": "https://adzuna.com.mx/details/none-id",
         "title": "No-id row", "location": {}, "company": {}, "description": "",
         "salary_min": 0, "salary_max": 0, "created": None, "category": {}},
    ]
}


def test_adzuna_fetch_uses_shared_helpers(monkeypatch):
    monkeypatch.setattr(adzuna, "get_secret", lambda k: "key")
    calls = []

    def fake_get_json(url, params=None):
        calls.append(url)
        return ADZUNA_PAGE if url.endswith("/1") else {"results": []}

    monkeypatch.setattr(adzuna, "get_json", fake_get_json)
    jobs = adzuna.fetch({"country": "mx", "pages": 3, "queries": ["ai"]})

    assert len(jobs) == 2
    assert jobs[0].external_id == "555"
    assert jobs[0].salary_min == 40000        # int_or_none coerced the float string
    assert jobs[1].salary_min is None          # 0 collapses to None
    assert jobs[1].external_id.endswith("none-id")  # require_id fell back to url, never "None"
    assert jobs[0].remote is True
    # pagination stopped at the first empty page, not at pages=3
    assert len(calls) == 2


def test_adzuna_missing_keys_yields_nothing(monkeypatch, capsys):
    monkeypatch.setattr(adzuna, "get_secret", lambda k: None)
    assert adzuna.fetch({}) == []
    assert "ADZUNA_APP_ID" in capsys.readouterr().out


@pytest.mark.parametrize("adapter_name", ["greenhouse", "adzuna", "lever", "ashby",
                                          "remoteok", "themuse", "torre", "findwork",
                                          "posthog"])
def test_adapters_import_and_expose_fetch(adapter_name):
    import importlib
    mod = importlib.import_module(f"src.adapters.{adapter_name}")
    assert callable(mod.fetch)


POSTHOG_PAGE = {
    "data": [
        {"id": 205821, "attributes": {
            "title": "UX Engineer", "url": "https://jobs.ashbyhq.com/posthog/2ef3",
            "department": "Engineering", "postedDate": "2026-08-20T18:46:44.330Z",
            "isRemote": True, "location": "", "description": "<p>Build &amp; ship</p>",
            "company": {"data": {"attributes": {"name": "PostHog", "remoteOnly": True}}}}},
        {"id": 205793, "attributes": {
            "title": "Founding Growth", "url": "https://jobs.gem.com/converge/am9i",
            "department": "Sales", "postedDate": "2026-08-25T00:00:56.067Z",
            "isRemote": False, "location": "New York", "description": "",
            "company": {"data": {"attributes": {"name": "Converge", "remoteOnly": False,
                                                "description": "Marketing measurement"}}}}},
    ]
}


def _posthog_pages(monkeypatch, calls=None):
    import src.adapters.posthog as posthog

    def fake_get_json(url, **kw):
        page = kw["params"]["pagination[page]"]
        if calls is not None:
            calls.append(page)
        return POSTHOG_PAGE if page == 1 else {"data": []}

    monkeypatch.setattr(posthog, "get_json", fake_get_json)
    return posthog


def test_posthog_fetch_normalizes(monkeypatch):
    calls: list[int] = []
    posthog = _posthog_pages(monkeypatch, calls)
    jobs = posthog.fetch({"pages": 3})

    assert [j.external_id for j in jobs] == ["205821", "205793"]
    j = jobs[0]
    assert j.source == "posthog"
    assert j.company == "PostHog" and j.title == "UX Engineer"
    assert j.remote is True and j.location == "Remote"   # blank location + isRemote
    assert j.description == "Build & ship"               # HTML stripped, entity intact
    assert j.tags == ["Engineering"]
    assert j.to_row()["posted_at"] == "2026-08-20T18:46:44.330000+00:00"
    # empty description falls back to the company blurb, not a blank row
    assert jobs[1].remote is False and jobs[1].description == "Marketing measurement"
    assert len(calls) == 2                               # stopped at the first empty page


def test_posthog_filters_department_and_remote(monkeypatch):
    posthog = _posthog_pages(monkeypatch)
    assert [j.title for j in posthog.fetch({"departments": ["engineering"]})] == ["UX Engineer"]
    posthog = _posthog_pages(monkeypatch)
    assert [j.title for j in posthog.fetch({"remote_only": True})] == ["UX Engineer"]
