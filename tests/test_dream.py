"""Dream companies: profile matching, the two new adapters, and the pipeline hooks."""
import json

import pytest

import src.dream as dream
from src.adapters import dreamsheet, teamtailor
from src.db import connect


@pytest.fixture
def profile(monkeypatch):
    """A small dream list so tests never depend on the live profile."""
    p = {
        "shortlist_threshold": 70,
        "dream_shortlist_threshold": 60,
        "dream_companies": [
            {"name": "Riot Games", "match": ["riot games", "riotgames"]},
            {"name": "Steven.com", "match": ["steven.com", "flightstory", "diary of a ceo"]},
            "Valve",
        ],
        "dream_rule": "waived",
        "relocation_line": "open to relocating on a TN",
    }
    monkeypatch.setattr(dream, "_CACHE", p)
    yield p
    dream.reset_cache()


# ---- profile matching ----

@pytest.mark.parametrize("company,expected", [
    ("Riot Games", "Riot Games"),
    ("riotgames", "Riot Games"),
    ("Riot IQ", None),                    # a different company; bare "riot" is not an alias
    ("Chariot Games", None),              # word boundary: no "riot games" inside "Chariot Games"
    ("The Diary of a CEO / Steven.com", "Steven.com"),
    ("FlightStory", "Steven.com"),
    ("Valve", "Valve"),                    # bare-string entry
    ("Valvoline", None),
    ("Acme", None),
    (None, None),
    ("", None),
])
def test_dream_name_matches_aliases_on_word_boundaries(profile, company, expected):
    assert dream.dream_name(company) == expected
    assert dream.is_dream(company) is (expected is not None)


def test_dream_threshold_falls_back_to_shortlist_threshold(profile, monkeypatch):
    assert dream.dream_shortlist_threshold() == 60
    del profile["dream_shortlist_threshold"]
    monkeypatch.setattr(dream, "shortlist_threshold", lambda: 71)
    assert dream.dream_shortlist_threshold() == 71


def test_dream_rule_and_relocation_line_read_through(profile):
    assert dream.dream_rule() == "waived"
    assert dream.relocation_line() == "open to relocating on a TN"


# ---- dreamsheet adapter ----

SHEET = """\
|  |  |  |  |  |  |  |  |  |  |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Priority | Company | Role | Location | Work auth | Why it fits | Apply URL | Status | First seen | Notes |
| Strong | Riot Games | Staff Engineer, Client | Los Angeles | TN possible | React + Node. | https://www.riotgames.com/en/j/7844349 | Not applied | 2026-08-27 | LA base |
| Backup | The Diary of a CEO / Steven.com | Senior Fullstack Engineer | Remote (US) | TN | Stack match. | https://flightstory.teamtailor.com/jobs/8163037-senior-fullstack\\_engineer | Not applied | 2026-08-31 |  |
| Skip | Nobody | | | | | https://example.com/no-title | | | |
"""


def test_dreamsheet_parses_drive_markdown(profile, tmp_path):
    f = tmp_path / "sheet.md"
    f.write_text(SHEET)
    jobs = dreamsheet.fetch({"path": str(f)})
    assert [j.title for j in jobs] == ["Staff Engineer, Client", "Senior Fullstack Engineer"]
    riot, doac = jobs
    assert riot.source == "dreamsheet"
    assert riot.company == "Riot Games"           # canonical dream name
    assert doac.company == "Steven.com"           # sheet alias folded to the dream name
    assert riot.external_id == riot.url == "https://www.riotgames.com/en/j/7844349"
    assert doac.url.endswith("senior-fullstack_engineer")   # Drive's \\_ escape undone
    assert doac.remote is True and riot.remote is False
    assert riot.description.startswith("Curated (dream sheet):")
    assert "Priority: Strong" in riot.description
    assert "Work Auth: TN possible" in riot.description
    assert "Notes: LA base" in riot.description
    assert riot.tags == ["Strong"]
    assert riot.to_row()["posted_at"] == "2026-08-27T00:00:00+00:00"


def test_dreamsheet_missing_file_hints_and_yields_nothing(profile, tmp_path, capsys):
    assert dreamsheet.fetch({"path": str(tmp_path / "nope.md")}) == []
    assert "dreamsheet" in capsys.readouterr().out


def test_dreamsheet_skips_the_title_gate_by_config():
    from src.adapters import keep_title
    assert keep_title({"title_filter": {"enabled": False}}, "Head of Data Intelligence")


# ---- teamtailor adapter ----

TEAMTAILOR_FEED = {
    "version": "https://jsonfeed.org/version/1.1",
    "title": "FlightStory",
    "items": [
        {"id": "61d5", "title": "Senior Fullstack Engineer",
         "url": "https://flightstory.teamtailor.com/jobs/8163037-senior-fullstack-engineer",
         "date_published": "2026-08-03T14:49:17+01:00",
         "content_html": "<p>Build &amp; ship</p>",
         "_jobposting": {
             "hiringOrganization": {"name": "FlightStory"},
             "jobLocation": [{"address": {"addressLocality": "Los Angeles",
                                          "addressRegion": "CA", "addressCountry": "US"}}]}},
        {"id": "aa11", "title": "Marketing Lead",
         "url": "https://flightstory.teamtailor.com/jobs/1-marketing-lead",
         "date_published": None, "content_html": "",
         "_jobposting": {"jobLocationType": "TELECOMMUTE", "jobLocation": []}},
        {"title": "no id at all", "content_html": ""},
    ],
}


def test_teamtailor_fetch_normalizes(monkeypatch):
    monkeypatch.setattr(teamtailor, "get_json", lambda url, **kw: TEAMTAILOR_FEED)
    jobs = teamtailor.fetch({"companies": ["flightstory"], "names": {"flightstory": "Steven.com"}})
    assert [j.external_id for j in jobs] == ["flightstory:61d5", "flightstory:aa11"]
    j = jobs[0]
    assert j.source == "teamtailor"
    assert j.company == "Steven.com"                     # names map wins over the org name
    assert j.location == "Los Angeles, CA, US"
    assert j.description == "Build & ship"
    assert j.to_row()["posted_at"] == "2026-08-03T13:49:17+00:00"
    assert jobs[1].location == "Remote" and jobs[1].remote is True


def test_teamtailor_org_name_when_no_names_map(monkeypatch):
    monkeypatch.setattr(teamtailor, "get_json", lambda url, **kw: TEAMTAILOR_FEED)
    assert teamtailor.fetch({"companies": ["flightstory"]})[0].company == "FlightStory"


def test_teamtailor_bad_slug_skips_not_raises(monkeypatch, capsys):
    def boom(url, **kw):
        raise ValueError("HTTP 404")
    monkeypatch.setattr(teamtailor, "get_json", boom)
    assert teamtailor.fetch({"companies": ["dead"]}) == []
    assert "failed" in capsys.readouterr().out


def test_teamtailor_ranks_as_ats_in_canonical_view(tmp_path):
    conn = connect(tmp_path / "jobs.db")
    for jid, src in ((1, "careerjet"), (2, "teamtailor")):
        conn.execute(
            "INSERT INTO jobs (id, source, external_id, canonical_key, company, title) "
            "VALUES (?,?,?,?,?,?)", (jid, src, f"x{jid}", "k", "Co", "Role"))
    assert conn.execute("SELECT id FROM canonical_jobs").fetchone()["id"] == 2


# ---- pipeline hooks ----

def _insert(conn, jid, source, key, company, title="Role", location="", status="discovered",
            score=None, desc=None, verdict=None):
    conn.execute(
        "INSERT INTO jobs (id, source, external_id, canonical_key, company, title, location, "
        "status, match_score, description, match_verdict, last_seen) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (jid, source, f"x{jid}", key, company, title, location, status, score, desc, verdict,
         "2026-09-01T00:00:00"))


def test_match_export_flags_and_front_loads_dream_rows(profile, tmp_path, monkeypatch):
    import src.match as match
    conn = connect(tmp_path / "jobs.db")
    _insert(conn, 1, "greenhouse", "k1", "Acme", desc="python react llm", location="Remote",
            verdict=json.dumps({"bucket": 3}))
    _insert(conn, 2, "greenhouse", "k2", "Riot Games", title="Staff Engineer",
            location="Los Angeles", desc="c++")                       # untriaged, on-site
    _insert(conn, 3, "dreamsheet", "k2", "Riot Games", title="Staff Engineer",
            desc="Curated (dream sheet):\nPriority: Strong")
    monkeypatch.setattr(match, "connect", lambda: conn)
    monkeypatch.setattr(match, "PENDING", tmp_path / "pending.json")
    match.export(limit=10, min_bucket=3, eligible_only=True)
    out = json.loads((tmp_path / "pending.json").read_text())
    # Riot: locked-out city AND no triage bucket, yet it survives both gates and sorts first.
    assert [o["id"] for o in out] == [2, 1]
    assert out[0]["dream"] is True
    assert out[0]["curated_note"].startswith("Curated (dream sheet):")
    assert "dream" not in out[1] and "curated_note" not in out[1]


def test_match_export_rescore_keeps_dream_rows_under_the_bucket_gate(profile, tmp_path, monkeypatch):
    import src.match as match
    conn = connect(tmp_path / "jobs.db")
    # shortlisted at the dream threshold (60), which is bucket 0 on the general 85/75/65 ladder
    _insert(conn, 1, "greenhouse", "k1", "Riot Games", title="Staff Engineer", location="Los Angeles",
            status="shortlisted", score=62, desc="c++")
    _insert(conn, 2, "greenhouse", "k2", "Acme", status="shortlisted", score=70, desc="python")
    _insert(conn, 3, "greenhouse", "k3", "Riot Games", title="Triaged out", location="Los Angeles",
            desc="c++", verdict=json.dumps({"bucket": 0}))            # triaged bucket 0: gate applies
    monkeypatch.setattr(match, "connect", lambda: conn)
    monkeypatch.setattr(match, "PENDING", tmp_path / "pending.json")
    match.export(limit=0, min_bucket=3, rescore=True)
    out = json.loads((tmp_path / "pending.json").read_text())
    assert [o["id"] for o in out] == [1]     # the stale dream row rides along, Acme and the bucket-0 row do not


def test_match_ingest_uses_dream_threshold(profile, tmp_path, monkeypatch):
    import src.match as match
    conn = connect(tmp_path / "jobs.db")
    _insert(conn, 1, "greenhouse", "k1", "Acme")
    _insert(conn, 2, "greenhouse", "k2", "Riot Games")
    scores = tmp_path / "scores.json"
    scores.write_text(json.dumps([{"id": 1, "score": 65, "reasons": "ok"},
                                  {"id": 2, "score": 65, "reasons": "ok"}]))
    monkeypatch.setattr(match, "SCORES", scores)
    monkeypatch.setattr(match, "connect", lambda: conn)
    match.ingest()
    rows = {r["id"]: r["status"] for r in conn.execute("SELECT id, status FROM jobs")}
    assert rows == {1: "discovered", 2: "shortlisted"}


def test_match_ingest_explicit_threshold_applies_to_both(profile, tmp_path, monkeypatch):
    import src.match as match
    conn = connect(tmp_path / "jobs.db")
    _insert(conn, 2, "greenhouse", "k2", "Riot Games")
    scores = tmp_path / "scores.json"
    scores.write_text(json.dumps([{"id": 2, "score": 65, "reasons": "ok"}]))
    monkeypatch.setattr(match, "SCORES", scores)
    monkeypatch.setattr(match, "connect", lambda: conn)
    match.ingest(80)
    assert conn.execute("SELECT status FROM jobs WHERE id=2").fetchone()["status"] == "discovered"


def test_triage_export_marks_dream_rows(profile, tmp_path, monkeypatch):
    import src.triage as triage
    conn = connect(tmp_path / "jobs.db")
    _insert(conn, 1, "greenhouse", "k1", "Acme")
    _insert(conn, 2, "greenhouse", "k2", "Riot Games")
    monkeypatch.setattr(triage, "connect", lambda: conn)
    monkeypatch.setattr(triage, "TRIAGE_DIR", tmp_path / "triage")
    triage.export(chunk=200, limit=None)
    recs = {r["id"]: r for r in json.loads((tmp_path / "triage" / "chunk_000.json").read_text())}
    assert recs[2]["dream"] is True and "dream" not in recs[1]


def test_query_rows_carry_dream(profile, tmp_path, monkeypatch, capsys):
    import src.query as query
    conn = connect(tmp_path / "jobs.db")
    _insert(conn, 1, "greenhouse", "k1", "Acme", status="shortlisted", score=80)
    _insert(conn, 2, "greenhouse", "k2", "Riot Games", status="shortlisted", score=75)
    monkeypatch.setattr(query, "connect", lambda: conn)
    query.crm()
    rows = {r["id"]: r["dream"] for r in json.loads(capsys.readouterr().out)}
    assert rows == {1: False, 2: True}
    query.job("2")
    assert json.loads(capsys.readouterr().out)["dream"] is True


def test_discover_title_gate_lets_dream_companies_through(profile, monkeypatch):
    """The gate expression in discover.main: keep_title OR (skip_dream AND is_dream)."""
    from src.adapters import keep_title
    cfg = {"title_filter": {"enabled": True, "include": ["engineer"]}}
    assert not keep_title(cfg, "Member of Technical Staff")
    assert keep_title(cfg, "Member of Technical Staff") or dream.is_dream("xAI") is False
    assert keep_title(cfg, "Member of Technical Staff") or dream.is_dream("Riot Games")


# ---- second-batch boards: pinpoint / rippling / secretlab ----

def test_pinpoint_fetch_normalizes(monkeypatch):
    from src.adapters import pinpoint
    payload = {"data": [
        {"id": "460903", "title": "Order Experience Team Lead",
         "location": {"name": "Mississauga"}, "workplace_type": "hybrid",
         "compensation_minimum": 60000.0, "compensation_maximum": 65000.0,
         "compensation_currency": "CAD", "compensation_frequency": "year",
         "description": "<p>Lead &amp; ship</p>", "key_responsibilities": "<ul><li>Run it</li></ul>",
         "url": "https://dbrand.pinpointhq.com/en/postings/892d", "employment_type_text": "Full-time"},
        {"id": "1", "title": "Cutter", "location": {"name": "Mississauga"}, "workplace_type": "onsite",
         "compensation_minimum": 20.0, "compensation_frequency": "hour", "path": "/en/postings/x"},
    ]}
    monkeypatch.setattr(pinpoint, "get_json", lambda url, **kw: payload)
    jobs = pinpoint.fetch({"companies": ["dbrand"]})
    a, b = jobs
    assert (a.source, a.external_id, a.company) == ("pinpoint", "dbrand:460903", "Dbrand")
    assert a.location == "Mississauga (hybrid)" and a.remote is False
    assert (a.salary_min, a.salary_max, a.currency) == (60000, 65000, "CAD")
    assert a.description == "Lead & ship Run it"
    assert a.tags == ["Full-time"]
    assert b.salary_min is None and b.currency is None     # hourly band never read as annual
    assert b.url == "https://dbrand.pinpointhq.com/en/postings/x"


def test_rippling_fetch_normalizes(monkeypatch):
    from src.adapters import rippling
    payload = [{"uuid": "119a", "name": "Logistics Manager ", "department": {"label": "Supply Chain"},
                "url": "https://ats.rippling.com/framework/jobs/119a",
                "workLocation": {"label": "Taipei City, Taiwan"}},
               {"uuid": "22b", "name": "Remote Engineer", "workLocation": {"label": "Remote - US"}}]
    monkeypatch.setattr(rippling, "get_json", lambda url, **kw: payload)
    jobs = rippling.fetch({"companies": ["framework"], "names": {"framework": "Framework Computer"}})
    a, b = jobs
    assert (a.source, a.external_id, a.company, a.title) == (
        "rippling", "framework:119a", "Framework Computer", "Logistics Manager")
    assert a.tags == ["Supply Chain"] and a.remote is False
    assert b.remote is True and b.url == "https://ats.rippling.com/framework/jobs/22b"


def test_secretlab_fetch_normalizes(monkeypatch):
    from src.adapters import secretlab
    payload = {"data": [
        {"id": "10403", "job_title": "Senior Backend Engineer I", "position_type": "Full-Time",
         "required_experience": "5 Years", "department_name": "Product &amp; Engineering",
         "office_location": "Singapore", "updated_at": "2026-08-17T02:29:52.000000Z"},
        {"job_title": "no id"},
    ]}
    monkeypatch.setattr(secretlab, "get_json", lambda url, **kw: payload)
    jobs = secretlab.fetch({})
    assert len(jobs) == 1
    j = jobs[0]
    assert (j.source, j.external_id, j.company) == ("secretlab", "10403", "Secretlab")
    assert j.url == "https://secretlab.co/pages/careers#id-10403"
    assert j.location == "Singapore" and j.remote is False
    assert "Department: Product &amp; Engineering" in j.description
    assert "Required experience: 5 Years" in j.description
    assert j.to_row()["posted_at"] == "2026-08-17T02:29:52+00:00"


def test_second_batch_boards_rank_as_ats(tmp_path):
    conn = connect(tmp_path / "jobs.db")
    for jid, src in ((1, "remoteok"), (2, "pinpoint"), (3, "careerjet"), (4, "rippling"),
                     (5, "jobicy"), (6, "secretlab")):
        conn.execute(
            "INSERT INTO jobs (id, source, external_id, canonical_key, company, title) "
            "VALUES (?,?,?,?,?,?)", (jid, src, f"x{jid}", f"k{(jid + 1) // 2}", "Co", "Role"))
    reps = {r["canonical_key"]: r["id"] for r in conn.execute("SELECT * FROM canonical_jobs")}
    assert reps == {"k1": 2, "k2": 4, "k3": 6}


@pytest.mark.parametrize("company,expected", [
    ("Framework Computer", "Framework Computer"),
    ("Framework Computer Inc", "Framework Computer"),
    ("Django Framework Co", None),          # bare "framework" is deliberately not an alias
    ("Arga Labs", "Arga Labs"),
    ("Peec", "Peec AI"),
    ("Secretlab", "Secretlab"),
    ("Dbrand", "dbrand"),
    ("ASUSTeK", "ASUS"),
])
def test_second_batch_aliases_against_live_profile(company, expected):
    dream.reset_cache()
    try:
        assert dream.dream_name(company) == expected
    finally:
        dream.reset_cache()
