"""Adapter fetch() against recorded fixtures, no network. Greenhouse and adzuna
are the templates; add a fixture test whenever an adapter's parsing changes."""
import pytest
import requests

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
                                          "posthog", "teamtailor", "dreamsheet",
                                          "pinpoint", "rippling", "secretlab"])
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


class _FakeHTTPError(requests.exceptions.HTTPError):
    """Stand-in for what get_json raises via response.raise_for_status()."""

    def __init__(self, status_code: int, headers: dict | None = None):
        super().__init__(f"{status_code} Client Error")
        self.response = type("Resp", (), {"status_code": status_code,
                                           "headers": headers or {}})()


def test_findwork_retries_429_then_succeeds(monkeypatch):
    import src.adapters.findwork as findwork

    monkeypatch.setattr(findwork, "get_secret", lambda k: "tok")
    monkeypatch.setattr(findwork, "time", type("T", (), {"sleep": staticmethod(lambda s: None)}))

    calls = []

    def fake_get_json(url, **kw):
        calls.append(kw["params"]["page"])
        if len(calls) == 1:
            raise _FakeHTTPError(429, headers={"Retry-After": "1"})
        return {"results": [{"id": 1, "url": "u", "company_name": "Acme",
                              "role": "Eng", "remote": True}]} if len(calls) == 2 else {"results": []}

    monkeypatch.setattr(findwork, "get_json", fake_get_json)
    jobs = findwork.fetch({"search": ["ai"], "pages": 1})

    assert len(calls) == 2                 # one 429, one successful retry
    assert [j.external_id for j in jobs] == ["1"]


def test_findwork_429_exhausted_skips_query_not_whole_source(monkeypatch, capsys):
    import src.adapters.findwork as findwork

    monkeypatch.setattr(findwork, "get_secret", lambda k: "tok")
    monkeypatch.setattr(findwork, "time", type("T", (), {"sleep": staticmethod(lambda s: None)}))

    def fake_get_json(url, **kw):
        term = kw["params"].get("search")
        if term == "ai":
            raise _FakeHTTPError(429)
        return {"results": [{"id": 2, "url": "u", "company_name": "Beta", "role": "Dev"}]}

    monkeypatch.setattr(findwork, "get_json", fake_get_json)
    jobs = findwork.fetch({"search": ["ai", "backend"], "pages": 1})

    assert [j.external_id for j in jobs] == ["2"]      # 'backend' query still returned rows
    assert "rate-limited" in capsys.readouterr().out


# ---- shared role-family title gate (src/adapters/keep_title) ----

TITLE_FILTER = {
    "include": ["engineer", "ai", "full stack", "front-end", "ingeniero"],
    "exclude": ["mechanical", "sales engineer", "recruiter"],
}


@pytest.mark.parametrize("title,kept", [
    ("Applied AI Engineer", True),
    ("Full Stack Developer", True),          # "full stack"
    ("Front-End Engineer", True),            # hyphenated spelling
    ("Ingeniero de Software", True),
    ("Maintenance Technician", False),       # "ai" must not match inside "Maintenance"
    ("Retail Trainer", False),               # nor inside "Retail"/"Trainer"
    ("Mechanical Engineer", False),          # exclude beats include
    ("Sales Engineer", False),
    ("Technical Recruiter", False),
    ("Registered Nurse", False),
    ("", True),                              # no title to judge: keep, let triage decide
])
def test_keep_title_word_boundaries(title, kept):
    from src.adapters import keep_title

    assert keep_title({"title_filter": TITLE_FILTER}, title) is kept


def test_keep_title_can_be_disabled_per_source():
    from src.adapters import keep_title

    cfg = {"title_filter": {"enabled": False, "include": ["engineer"]}}
    assert keep_title(cfg, "Registered Nurse") is True


def test_shipped_title_filter_keeps_every_target_role_family():
    """config/sources.yaml must not gate out any of profile.yaml's role families."""
    import src.adapters as adapters

    adapters._TITLE_FILTER = None  # re-read the shipped config
    try:
        for title in [
            "Applied AI Engineer", "Forward Deployed Engineer", "Founding Engineer",
            "Full-Stack Engineer", "Deployment Strategist", "AI Solutions Architect",
            "AI Enablement Director, LATAM", "GTM Engineer", "Frontend Engineer",
            "React Engineer", "UI Engineer", "Internal Tools Engineer",
            "Developer Experience Engineer", "Workflow Automation Engineer",
            "Software Engineer, Web", "Technical Program Manager, AI",
        ]:
            assert adapters.keep_title({}, title), title
        for title in ["Registered Nurse", "Manufacturing Engineer", "Account Executive"]:
            assert not adapters.keep_title({}, title), title
    finally:
        adapters._TITLE_FILTER = None


# ---- Torre eligibility capture (job 18645 postmortem: Spain/UK-only role scored
# and tailored because the description omitted the timezone-gated eligibility) ----

TORRE_RESULT_EUROPE_ONLY = {
    "id": "qdP99pLr",
    "objective": "Full-Stack Engineer: Retail Media",
    "organizations": [{"name": "Constructor"}],
    "locations": [],
    "timezones": ["GMT+00:00", "GMT+03:00"],
    "remote": True,
    "opportunity": "employee",
    "compensation": {"data": {"minAmount": 80000.0, "maxAmount": 120000.0, "currency": "USD"}},
    "created": "2026-08-08T04:46:26.000Z",
    "skills": [],
}

TORRE_RESULT_LATAM = {
    "id": "Vro7o8mr",
    "objective": "Software Development Engineer in Test",
    "organizations": [{"name": "FreightPOP"}],
    "locations": ["Colombia", "Argentina", "Mexico"],
    "timezones": None,
    "remote": True,
    "opportunity": "employee",
    "compensation": {"data": {"minAmount": 33000.0, "maxAmount": 65000.0, "currency": "USD"}},
    "created": "2026-08-11T19:13:02.000Z",
    "skills": [],
}


def test_torre_fetch_prepends_eligibility_header(monkeypatch):
    import src.adapters.torre as torre

    monkeypatch.setattr(torre, "post_json",
                        lambda url, **kw: {"results": [TORRE_RESULT_EUROPE_ONLY]})
    jobs = torre.fetch({"queries": ["full-stack engineer"], "pages": 1})
    assert len(jobs) == 1
    j = jobs[0]
    assert j.external_id == "qdP99pLr"
    assert j.description.startswith(
        "Eligibility: remote, timezone GMT+00:00 to GMT+03:00, agreement: employee.")
    assert "scale global ecommerce discovery" not in j.description[:11]  # header comes first
    # empty `locations` (timezone-gated, not country-gated): location falls back to Remote
    assert j.location == "Remote"


def test_torre_fetch_captures_country_list_when_present(monkeypatch):
    import src.adapters.torre as torre

    monkeypatch.setattr(torre, "post_json",
                        lambda url, **kw: {"results": [TORRE_RESULT_LATAM]})
    jobs = torre.fetch({"queries": ["sdet"], "pages": 1})
    j = jobs[0]
    assert j.location == "Colombia, Argentina, Mexico"
    assert "countries: Colombia, Argentina, Mexico" in j.description
    assert "timezone" not in j.description  # no band on this one


@pytest.mark.parametrize("timezones,excludes", [
    (["GMT+00:00", "GMT+03:00"], True),           # Europe/EMEA band, no GMT-6
    (["GMT-08:00", "GMT-05:00"], False),           # US band covers GMT-6
    (["GMT-06:00"], False),                        # exact match
    ([], False),                                   # no band at all: not "excluded"
    (None, False),
])
def test_torre_timezone_band_excludes_gmt6(timezones, excludes):
    import src.adapters.torre as torre

    assert torre.timezone_band_excludes(timezones) is excludes


def test_torre_eligibility_header_strip_is_idempotent():
    import src.adapters.torre as torre

    header = torre.eligibility_header(remote=True, timezones=["GMT+00:00", "GMT+03:00"],
                                      locations=[], opportunity="employee")
    original = "You will scale global ecommerce discovery."
    once = (header + " " + original).strip()
    stripped = torre.strip_eligibility_header(once)
    assert stripped == original
    # re-prepending after a strip never stacks headers
    twice = (header + " " + stripped).strip()
    assert twice.count("Eligibility:") == 1
