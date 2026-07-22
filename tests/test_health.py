"""Migrations runner, per-source run recording, and digest honesty helpers."""
import pytest

from src.db import MIGRATIONS, connect
from src.discover import _record_run
from src.notify import _dead_sources, _status_line, _unscored_count


@pytest.fixture
def conn(tmp_path):
    return connect(tmp_path / "jobs.db")


def test_migrations_apply_and_stamp_version(conn, tmp_path):
    assert conn.execute("PRAGMA user_version").fetchone()[0] == len(MIGRATIONS)
    # runs table exists (migration 1)
    conn.execute("SELECT ts, source, pulled, ok FROM runs")
    # reconnecting is a no-op, not a re-run
    again = connect(tmp_path / "jobs.db")
    assert again.execute("PRAGMA user_version").fetchone()[0] == len(MIGRATIONS)


def test_record_run_both_shapes(conn):
    _record_run(conn, "2026-07-16T08:00:00", "greenhouse", pulled=120, new=5, seen=115)
    _record_run(conn, "2026-07-16T08:00:00", "torre", ok=False, error="HTTP 500")
    rows = {r["source"]: r for r in conn.execute("SELECT * FROM runs")}
    assert rows["greenhouse"]["pulled"] == 120 and rows["greenhouse"]["ok"] == 1
    assert rows["torre"]["ok"] == 0 and rows["torre"]["error"] == "HTTP 500"


def test_dead_sources_needs_three_quiet_runs(conn):
    for i in range(3):
        _record_run(conn, f"t{i}", "deadsource", pulled=0)
        _record_run(conn, f"t{i}", "healthy", pulled=50, new=1, seen=49)
    _record_run(conn, "t0", "newsource", pulled=0)  # only 1 run: too early to flag
    assert _dead_sources(conn) == ["deadsource"]


def test_dead_sources_failures_count_as_quiet(conn):
    for i in range(3):
        _record_run(conn, f"t{i}", "flaky", ok=False, error="boom")
    assert _dead_sources(conn) == ["flaky"]


def test_dead_source_revives_on_success(conn):
    for i in range(3):
        _record_run(conn, f"t{i}", "src", pulled=0)
    _record_run(conn, "t3", "src", pulled=10)
    assert _dead_sources(conn) == []


def test_unscored_count_dedupes_by_canonical_key(conn):
    for i, key in enumerate(["k1", "k1", "k2"]):
        conn.execute(
            "INSERT INTO jobs (source, external_id, canonical_key, status) "
            "VALUES ('t', ?, ?, 'discovered')", (f"x{i}", key))
    conn.execute(
        "INSERT INTO jobs (source, external_id, canonical_key, status, match_score) "
        "VALUES ('t', 'x9', 'k3', 'discovered', 80)")
    assert _unscored_count(conn) == 2


def test_status_line_composition():
    assert _status_line(0, []) == ""
    assert "5 discovered jobs not yet scored" in _status_line(5, [])
    line = _status_line(5, ["torre", "consider"])
    assert "torre, consider" in line and "·" in line
