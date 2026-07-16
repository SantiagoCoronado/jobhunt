"""Phase 3: canonical dedup view, expiry/pruning, HTTP retry policy, helpers."""
import pytest
import requests

from src.adapters import (_retryable, int_or_none, paginate, remote_from_text,
                          require_id)
from src.db import connect
from src.maintain import TRIAGE_EXCERPT, run as maintain_run
from src.models import iso_date
from src.research import company_slug


# ---- canonical_jobs view (3.1) ----

@pytest.fixture
def conn(tmp_path):
    return connect(tmp_path / "jobs.db")


def _insert(conn, jid, source, key, status="discovered", score=None,
            last_seen="2026-07-16T00:00:00", desc=None):
    conn.execute(
        "INSERT INTO jobs (id, source, external_id, canonical_key, company, title, "
        "status, match_score, last_seen, description) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (jid, source, f"x{jid}", key, "Co", "Role", status, score, last_seen, desc))


def test_canonical_view_prefers_ats_then_lowest_id(conn):
    _insert(conn, 1, "careerjet", "k1")
    _insert(conn, 2, "greenhouse", "k1")   # ATS beats the earlier aggregator row
    _insert(conn, 3, "careerjet", "k1")
    _insert(conn, 4, "remoteok", "k2")
    _insert(conn, 5, "careerjet", "k2")    # no ATS in group: lowest id wins
    reps = {r["canonical_key"]: r["id"]
            for r in conn.execute("SELECT * FROM canonical_jobs")}
    assert reps == {"k1": 2, "k2": 4}


def test_match_ingest_propagates_to_duplicates(conn, tmp_path, monkeypatch):
    import src.match as match
    _insert(conn, 1, "greenhouse", "k1")
    _insert(conn, 2, "careerjet", "k1")
    scores = tmp_path / "scores.json"
    scores.write_text('[{"id": 1, "score": 88, "reasons": "fits"}]')
    monkeypatch.setattr(match, "SCORES", scores)
    monkeypatch.setattr(match, "connect", lambda: conn)
    match.ingest(70)
    rows = conn.execute("SELECT id, match_score, status FROM jobs ORDER BY id").fetchall()
    assert [(r["match_score"], r["status"]) for r in rows] == [
        (88, "shortlisted"), (88, "shortlisted")]


# ---- expiry + pruning (3.2 / 3.3) ----

def _run_row(conn, source, ts, pulled=10):
    conn.execute("INSERT INTO runs (ts, source, pulled, ok) VALUES (?,?,?,1)",
                 (ts, source, pulled))


def test_expiry_needs_a_later_successful_run(conn):
    old = "2026-06-01T00:00:00"
    _insert(conn, 1, "greenhouse", "k1", last_seen=old)   # source ran after: expire
    _insert(conn, 2, "torre", "k2", last_seen=old)        # source never ran: keep
    _insert(conn, 3, "greenhouse", "k3", status="shortlisted", last_seen=old)  # not discovered: keep
    _run_row(conn, "greenhouse", "2026-07-15T00:00:00")
    r = maintain_run(conn)
    assert r["expired"] == 1
    status = {row["id"]: row["status"] for row in conn.execute("SELECT id, status FROM jobs")}
    assert status == {1: "expired", 2: "discovered", 3: "shortlisted"}


def test_expiry_boundary_is_days_not_days_plus_one(conn):
    # Regression: comparing now_iso()'s 'T'-separated ISO string against
    # datetime('now',...) raw made the cutoff silently days+1 ('T' > ' ').
    from datetime import datetime, timedelta, timezone
    just_over = (datetime.now(timezone.utc) - timedelta(days=14, hours=1)).isoformat()
    _insert(conn, 1, "greenhouse", "k1", last_seen=just_over)
    _run_row(conn, "greenhouse", "2099-01-01T00:00:00+00:00")
    assert maintain_run(conn)["expired"] == 1


def test_match_ingest_reports_unknown_ids(conn, tmp_path, monkeypatch, capsys):
    import src.match as match
    _insert(conn, 1, "greenhouse", "k1")
    scores = tmp_path / "scores.json"
    scores.write_text('[{"id": 1, "score": 90}, {"id": 999, "score": 90}]')
    monkeypatch.setattr(match, "SCORES", scores)
    monkeypatch.setattr(match, "connect", lambda: conn)
    match.ingest(70)
    out = capsys.readouterr().out
    assert "Ingested 1 scores" in out and "1 skipped (unknown id)" in out
    assert conn.execute("SELECT match_score FROM jobs WHERE id=1").fetchone()[0] == 90


def test_prune_truncates_irrelevant_and_clears_old_expired(conn):
    _insert(conn, 1, "t", "k1", status="irrelevant", desc="x" * 5000)
    _insert(conn, 2, "t", "k2", status="expired", desc="y" * 5000,
            last_seen="2026-05-01T00:00:00")
    _insert(conn, 3, "t", "k3", status="discovered", desc="z" * 5000)  # untouched
    r = maintain_run(conn)
    rows = {row["id"]: row["description"] for row in conn.execute("SELECT id, description FROM jobs")}
    assert len(rows[1]) == TRIAGE_EXCERPT
    assert rows[2] is None
    assert len(rows[3]) == 5000
    assert r["pruned"] == 2


# ---- HTTP retry policy (3.4) ----

def _http_error(status):
    resp = requests.Response()
    resp.status_code = status
    return requests.HTTPError(response=resp)


def test_retryable_statuses_only():
    assert _retryable(_http_error(429))
    assert _retryable(_http_error(503))
    assert not _retryable(_http_error(404))
    assert not _retryable(_http_error(401))
    assert _retryable(requests.ConnectionError())
    assert _retryable(requests.Timeout())


# ---- shared adapter helpers (3.5) ----

def test_int_or_none():
    assert int_or_none("85000") == 85000
    assert int_or_none(85000.5) == 85000
    assert int_or_none(None) is None
    assert int_or_none("") is None
    assert int_or_none("negotiable") is None


def test_remote_from_text():
    assert remote_from_text("Engineer (Remote)", None)
    assert remote_from_text("Engineer", "Mexico City") is False


def test_require_id_never_yields_none_string():
    assert require_id({"id": 42}, "id") == "42"
    assert require_id({"id": None, "url": "u"}, "id", "url") == "u"
    with pytest.raises(KeyError):
        require_id({"id": None}, "id")


def test_paginate_stops_on_empty_and_survives_errors():
    pages = {1: [1, 2], 2: [3], 3: []}
    assert paginate(lambda p: pages[p], 5) == [1, 2, 3]

    def flaky(p):
        if p == 2:
            raise ValueError("boom")
        return [p]
    assert paginate(flaky, 5) == [1]  # keeps page 1, stops at the failure


# ---- posted_at normalization (3.7) ----

def test_iso_date_formats():
    assert iso_date(None) is None
    assert iso_date("2026-07-16") == "2026-07-16T00:00:00+00:00"
    assert iso_date("2026-07-16T10:00:00Z") == "2026-07-16T10:00:00+00:00"
    assert iso_date("Wed, 15 Jul 2026 10:00:00 GMT") == "2026-07-15T10:00:00+00:00"
    assert iso_date("1783852800") == "2026-07-12T10:40:00+00:00"
    assert iso_date("last week") == "last week"  # unparseable passes through


# ---- research slug (3.6) ----

def test_company_slug_normalization():
    assert company_slug("99minutos.com") == company_slug("99minutos") == "99minutos"
    assert company_slug("EasyAudit AI, Inc.") == "easyaudit-ai"
    assert company_slug("Sira AI") == "sira-ai"          # no dot: 'ai' is the name
    assert company_slug("BC Tecnología") == "bc-tecnologia"
    assert company_slug("Lemon.io") == "lemon"
