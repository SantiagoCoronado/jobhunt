"""Phase 6: event log + the deterministic stats behind /jh-review."""
import json

import pytest

from src.db import connect, log_event, set_status, touch_contact
from src.config import profile
from src.stats import _band, _outcome, calibration, comp, families, funnel, latency, title_family


@pytest.fixture
def conn(tmp_path):
    return connect(tmp_path / "jobs.db")


def _insert(conn, jid, title="Role", status="discovered", score=None,
            applied=None, salary_max=None, currency=None, remote=0):
    conn.execute(
        "INSERT INTO jobs (id, source, external_id, canonical_key, company, title, "
        "status, match_score, applied_at, salary_max, currency, remote) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (jid, "test", f"x{jid}", f"k{jid}", "Co", title, status, score,
         applied, salary_max, currency, remote))


# ---- events (6.1) ----

def test_status_change_logs_event(conn):
    _insert(conn, 1, status="shortlisted")
    set_status(conn, 1, "applied")
    set_status(conn, 1, "applied", note="same status: no event")
    events = conn.execute("SELECT kind, payload FROM events WHERE job_id=1").fetchall()
    assert len(events) == 1
    assert json.loads(events[0]["payload"]) == {"from": "shortlisted", "to": "applied"}


def test_touch_logs_contact_event(conn):
    _insert(conn, 1, status="applied")
    touch_contact(conn, 1, contact_date="2026-07-16", bump_days=7)
    e = conn.execute("SELECT payload FROM events WHERE job_id=1 AND kind='contact'").fetchone()
    assert json.loads(e["payload"]) == {"date": "2026-07-16", "bumped": True}


def test_backfill_migration_seeds_applied_events(tmp_path):
    # Simulate a pre-migration DB: create it, wipe events + reset version to 2,
    # then reconnect so migration 3 re-runs its backfill INSERT.
    db_path = tmp_path / "jobs.db"
    conn = connect(db_path)
    conn.execute("INSERT INTO jobs (id, source, external_id, canonical_key, status, applied_at) "
                 "VALUES (1, 't', 'x', 'k', 'applied', '2026-07-08')")
    conn.execute("DELETE FROM events")
    conn.execute("PRAGMA user_version = 2")
    conn.commit()
    conn.close()
    conn = connect(db_path)
    e = conn.execute("SELECT ts, payload FROM events WHERE job_id=1").fetchone()
    assert e["ts"] == "2026-07-08"
    assert json.loads(e["payload"])["backfill"] is True


def test_log_event_generic(conn):
    _insert(conn, 1)
    log_event(conn, 1, "debrief", {"note": "screen: went well"})
    e = conn.execute("SELECT kind FROM events WHERE job_id=1").fetchone()
    assert e["kind"] == "debrief"


# ---- stats primitives ----

def test_title_family_from_the_fixture_profile():
    """Fixture families: A full-stack (first = catch-all), B frontend; B's phrases come from
    its titles (Frontend Engineer, UI Engineer) since it declares no `match` list."""
    assert [k for k, _ in families()] == ["B", "A"]
    assert title_family("Senior Frontend Engineer") == "B"
    assert title_family("UI Engineer (design systems)") == "B"
    assert title_family("Software Engineer") == "A"
    assert title_family("Backend Engineer") == "A"
    assert title_family(None) == "A"


FOUR = profile({"name": "X", "role_families": [
    {"key": "A", "name": "hands-on AI / full-stack", "titles": ["Applied AI Engineer"]},
    {"key": "B", "name": "AI deployment", "titles": ["Deployment Strategist"],
     "match": ["deployment", "solutions architect", "solutions engineer", "enablement", "strategist",
               "forward deployed", "field engineer", "gtm", "technical program", "adoption"]},
    {"key": "C", "name": "frontend", "titles": ["Frontend Engineer"],
     "match": ["front-end", "frontend", "ui", "react", "web engineer"]},
    {"key": "D", "name": "internal tooling", "titles": ["Internal Tools Engineer"],
     "match": ["internal tool", "internal platform", "internal application", "developer experience",
               "developer productivity", "business systems", "workflow automation", "devex"]},
]})


def test_title_family_with_match_lists_reproduces_the_four_family_calibration():
    """The regexes stats.py used to hardcode, expressed as `match` phrases: same buckets."""
    fams = families(FOUR)
    assert [k for k, _ in fams] == ["B", "C", "D", "A"]
    assert title_family("Forward Deployed Engineer", fams) == "B"
    assert title_family("Forward-Deployed Engineer", fams) == "B"
    assert title_family("Deployment Strategist Lead - Mexico", fams) == "B"
    assert title_family("Solutions Engineer", fams) == "B"
    assert title_family("Senior Frontend Engineer", fams) == "C"
    assert title_family("Front End Developer", fams) == "C"
    assert title_family("React Engineer, AI tools", fams) == "C"
    assert title_family("Internal Tools Engineer", fams) == "D"
    assert title_family("Developer Experience Engineer", fams) == "D"
    assert title_family("Applied AI Engineer", fams) == "A"
    assert title_family("Guitar Builder", fams) == "A"
    assert title_family(None, fams) == "A"


def test_families_with_an_explicit_profile_never_poison_the_cache():
    """PR #22 review: only the profile-less call populates the module cache."""
    assert [k for k, _ in families(FOUR)] == ["B", "C", "D", "A"]
    assert [k for k, _ in families()] == ["B", "A"]            # still the fixture profile
    assert title_family("Deployment Strategist") == "A"         # not FOUR's B


def test_families_without_a_profile_bucket_everything_as_a():
    assert families({"name": "X"}) == [("A", None)]
    assert title_family("Anything", families({"name": "X"})) == "A"


def test_band_and_outcome():
    assert _band(None) == "unscored"
    assert _band(92) == "90+" and _band(70) == "70-79" and _band(69) == "<70"
    assert _outcome("screen") == "responded"
    assert _outcome("rejected") == "responded"   # a rejection is a reply
    assert _outcome("ghosted") == "ghosted"
    assert _outcome("applied") == "waiting"


def test_funnel_and_calibration_output(conn, capsys):
    _insert(conn, 1, title="AI Engineer", status="screen", score=92, applied="2026-07-01")
    _insert(conn, 2, title="Frontend Engineer", status="applied", score=75, applied="2026-07-02")
    _insert(conn, 3, title="AI Engineer", status="rejected", score=88, applied="2026-07-03")
    _insert(conn, 4, title="Shortlisted only", status="shortlisted", score=90)  # not an application
    funnel(conn)
    out = capsys.readouterr().out
    assert "Applications: 3" in out
    assert "responded (screen+ or rejected): 2" in out
    calibration(conn)
    out = capsys.readouterr().out
    assert "90+" in out and "n=  1" in out


def test_comp_groups_by_currency_family_remote(conn, capsys):
    _insert(conn, 1, title="AI Engineer", salary_max=120000, currency="USD", remote=1, score=80)
    _insert(conn, 2, title="AI Engineer", salary_max=100000, currency="USD", remote=1, score=80)
    _insert(conn, 3, title="Frontend Engineer", salary_max=900000, currency="MXN", remote=0, score=80)
    comp(conn, min_score=70)
    out = capsys.readouterr().out
    assert "USD" in out and "MXN" in out
    assert "110,000" in out  # median of the two USD rows


def _event(conn, jid, ts, to):
    conn.execute("INSERT INTO events (job_id, ts, kind, payload) VALUES (?,?,?,?)",
                 (jid, ts, "status_change", f'{{"to": "{to}"}}'))


def test_latency_from_events(conn, capsys):
    _insert(conn, 1, status="screen")
    _event(conn, 1, "2026-07-01T00:00:00", "applied")
    _event(conn, 1, "2026-07-09T00:00:00", "screen")
    latency(conn)
    out = capsys.readouterr().out
    assert "n=1" in out and "median 8 days" in out


def test_latency_picks_first_response_deterministically(conn, capsys):
    # Regression: bare column under GROUP BY with no aggregate was
    # implementation-defined; MIN() must pick the FIRST response.
    _insert(conn, 1, status="interview")
    _event(conn, 1, "2026-06-01T00:00:00", "applied")
    _event(conn, 1, "2026-06-04T00:00:00", "screen")      # first response: 3 days
    _event(conn, 1, "2026-06-20T00:00:00", "interview")   # later, must not win
    latency(conn)
    out = capsys.readouterr().out
    assert "n=1" in out and "min 3, max 3" in out


def test_latency_reapply_cycles_never_cross(conn, capsys):
    # Regression: applied -> rejected -> re-applied -> screen used to collapse
    # into one arbitrary row per job. Each applied event is its own cycle, and
    # a response only counts within its cycle.
    _insert(conn, 1, status="screen")
    _event(conn, 1, "2026-01-01T00:00:00", "applied")
    _event(conn, 1, "2026-01-21T00:00:00", "rejected")    # cycle 1: 20 days
    _event(conn, 1, "2026-04-11T00:00:00", "applied")
    _event(conn, 1, "2026-04-16T00:00:00", "screen")      # cycle 2: 5 days
    latency(conn)
    out = capsys.readouterr().out
    assert "n=2" in out and "min 5, max 20" in out


def test_backfill_migration_is_idempotent_after_crash_window(tmp_path):
    # Regression: executescript commits before the user_version bump, so a
    # crash between the two re-runs the migration; the NOT IN guard must
    # prevent duplicate backfill events.
    db_path = tmp_path / "jobs.db"
    conn = connect(db_path)
    conn.execute("INSERT INTO jobs (id, source, external_id, canonical_key, status, applied_at) "
                 "VALUES (1, 't', 'x', 'k', 'applied', '2026-07-08')")
    conn.execute("PRAGMA user_version = 2")
    conn.commit()
    conn.close()
    conn = connect(db_path)  # re-run: inserts the backfill event, bumps to 3
    assert conn.execute("SELECT COUNT(*) FROM events WHERE job_id=1").fetchone()[0] == 1
    conn.execute("PRAGMA user_version = 2")  # the crash window: event on disk, version not bumped
    conn.commit()
    conn.close()
    conn = connect(db_path)  # migration 3 re-runs WITH the event present
    assert conn.execute("SELECT COUNT(*) FROM events WHERE job_id=1").fetchone()[0] == 1
