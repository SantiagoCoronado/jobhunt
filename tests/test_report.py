"""Phase 1 of docs/spec-email-report-upskill.md: the offline HTML report."""
import re
from datetime import date

import pytest

from src.db import connect
from src.report import (build_html, followups_due, reached_stages, source_health,
                        status_distribution)
from src.stats import calibration_data, comp_data, funnel_data, latency_data

TODAY = date(2026, 7, 24)


@pytest.fixture
def conn(tmp_path):
    return connect(tmp_path / "jobs.db")


def _insert(conn, jid, title="Role", status="discovered", score=None,
            applied=None, salary_max=None, currency=None, remote=0, source="test",
            followup=None, company="Co"):
    conn.execute(
        "INSERT INTO jobs (id, source, external_id, canonical_key, company, title, "
        "status, match_score, applied_at, salary_max, currency, remote, next_followup_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (jid, source, f"x{jid}", f"k{jid}", company, title, status, score,
         applied, salary_max, currency, remote, followup))


def _seed(conn):
    _insert(conn, 1, title="AI Engineer", status="screen", score=92,
            applied="2026-07-01", company="Acme <AI>")
    _insert(conn, 2, title="Frontend Engineer", status="applied", score=75,
            applied="2026-07-02", followup="2026-07-10")
    _insert(conn, 3, title="AI Engineer", status="rejected", score=88, applied="2026-07-03")
    _insert(conn, 4, title="Watcher", status="shortlisted", score=90)
    _insert(conn, 5, title="Junk", status="irrelevant")
    conn.execute("INSERT INTO events (job_id, ts, kind, payload) VALUES "
                 "(1, '2026-07-01T00:00:00', 'status_change', '{\"to\": \"applied\"}'),"
                 "(1, '2026-07-05T00:00:00', 'status_change', '{\"to\": \"screen\"}')")
    conn.execute("INSERT INTO runs (ts, source, pulled, new, ok) VALUES "
                 "('2026-07-20T00:00:00', 'livesource', 40, 5, 1),"
                 "('2026-07-21T00:00:00', 'livesource', 38, 2, 1),"
                 "('2026-07-20T00:00:00', 'deadsource', 0, 0, 1),"
                 "('2026-07-21T00:00:00', 'deadsource', 0, 0, 0)")


# ---- data helpers ----

def test_reached_stages_uses_events_and_current_status(conn):
    _seed(conn)
    reached = reached_stages(conn)
    # 1 (screen via events), 2 (applied), 3 (rejected but applied_at set) = 3 applied
    assert reached["applied"] == 3
    assert reached["screen"] == 1
    assert reached["offer"] == 0


def test_status_distribution_follows_canonical_order(conn):
    _seed(conn)
    dist = status_distribution(conn)
    assert dist[0][0] == "shortlisted"          # db.STATUSES order, zeros dropped
    assert ("irrelevant", 1) in dist


def test_followups_due_only_open_and_due(conn):
    _seed(conn)
    due = followups_due(conn, TODAY)
    assert [r["id"] for r in due] == [2]
    assert not followups_due(conn, date(2026, 7, 1))


def test_source_health_flags_dead_source(conn):
    _seed(conn)
    health = {h["source"]: h for h in source_health(conn)}
    assert health["deadsource"]["dead"] is True
    assert health["livesource"]["dead"] is False
    assert health["livesource"]["pulled"] == 78


def test_source_health_needs_two_runs_to_flag(conn):
    conn.execute("INSERT INTO runs (ts, source, pulled, new, ok) VALUES "
                 "('2026-07-21T00:00:00', 'newsource', 0, 0, 1)")
    assert source_health(conn)[0]["dead"] is False


# ---- stats data layer (the refactor contract) ----

def test_funnel_data_shape(conn):
    _seed(conn)
    d = funnel_data(conn)
    assert d["total"] == 3 and d["responded"] == 2
    assert d["by_stage"]["screen"] == 1 and d["by_stage"]["waiting"] == 1
    assert ("90+", 1, 1) in d["segments"]["score band"]
    assert ("B", 1, 0) in d["segments"]["title family"]   # fixture family B = frontend


def test_calibration_and_latency_and_comp_data(conn):
    _seed(conn)
    assert ("90+", 1, 0) in calibration_data(conn)["bands"]
    assert latency_data(conn)["days"] == [4]
    _insert(conn, 10, title="AI Engineer", salary_max=120000, currency="USD",
            remote=1, score=80)
    d = comp_data(conn, 70)
    assert d["segments"][0]["median"] == 120000


def test_stats_cli_output_unchanged_by_refactor(conn, capsys):
    # Golden lock on the printed format the refactor must preserve.
    from src.stats import funnel
    _seed(conn)
    funnel(conn)
    out = capsys.readouterr().out
    assert "Applications: 3" in out
    assert "  responded (screen+ or rejected): 2  (66%)" in out
    assert "  screen     1" in out
    assert "\nBy score band:" in out
    assert "  90+          applied=  1  responded=1  (100%)" in out


# ---- the HTML itself ----

def test_report_is_self_contained_and_escaped(conn):
    _seed(conn)
    page = build_html(conn, TODAY)
    assert page.startswith("<!doctype html>")
    # no external requests of any kind
    assert not re.search(r"""(src|href)\s*=\s*["']\s*(https?:)?//""", page, re.I)
    assert "@import" not in page and "url(" not in page
    # zero em-dashes (canonical repo rule)
    assert "—" not in page
    # DB text is escaped
    assert "Acme &lt;AI&gt;" in page and "<AI>" not in page


def test_report_sections_and_numbers(conn):
    _seed(conn)
    page = build_html(conn, TODAY)
    for anchor in ("funnel", "rates", "statuses", "followups",
                   "applications", "comp", "sources"):
        assert f'id="{anchor}"' in page
    assert "Generated 2026-07-24" in page
    assert "possibly dead" in page          # deadsource flagged
    assert "Response rate" in page


def test_report_empty_db(conn):
    page = build_html(conn, TODAY)
    assert "No applications yet." in page
    assert "—" not in page
