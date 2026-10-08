"""data.stats() (pre-release PR 6 story 1): one frozen snapshot for the stats screen, on an
empty DB, a day-1 DB (discovered rows only) and a DB with applications and events."""
import dataclasses
import json
from datetime import date

import pytest
from tui_fakes import _add

from src import db
from src.hunt import ledger as hunt_ledger
from src.tui import data

pytestmark = pytest.mark.usefixtures("tmp_db")

TODAY = date(2026, 10, 8)


def _runs(*rows: tuple[str, str, int, int, int]) -> None:
    conn = db.connect(db.DB_PATH)
    conn.executemany("INSERT INTO runs (ts, source, pulled, new, ok) VALUES (?,?,?,?,?)", rows)
    conn.commit()
    conn.close()


def _event(job_id: int, ts: str, to: str) -> None:
    conn = db.connect(db.DB_PATH)
    conn.execute("INSERT INTO events (job_id, ts, kind, payload) VALUES (?,?,?,?)",
                 (job_id, ts, "status_change", json.dumps({"from": "x", "to": to})))
    conn.commit()
    conn.close()


def test_an_empty_db_is_a_snapshot_of_zeros():
    s = data.stats(TODAY)
    assert dataclasses.is_dataclass(s)
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.applications = 3  # type: ignore[misc]
    assert [step for step, _n in s.funnel] == list(data.FUNNEL)
    assert all(n == 0 for _step, n in s.funnel)
    assert (s.applications, s.replied, s.waiting, s.interviewing, s.applied_7d, s.applied_28d) == (0, 0, 0, 0, 0, 0)
    assert s.reply_rate is None and s.median_reply is None
    assert s.last_discover is None and s.discover_age is None and s.hunt is None
    assert s.bands == () and s.sources == ()


def test_a_day_1_db_has_found_and_sources_with_pulled_and_new_only():
    for i in range(12):
        _add(status="discovered", source="adzuna" if i % 3 else "greenhouse")
    _add(status="irrelevant", source="adzuna")
    _runs(("2026-10-07T10:00:00+00:00", "adzuna", 9, 9, 1), ("2026-10-07T10:00:00+00:00", "greenhouse", 4, 4, 1),
          ("2026-10-06T10:00:00+00:00", "remotive", 0, 0, 1), ("2026-10-07T10:00:00+00:00", "remotive", 0, 0, 0))
    s = data.stats(TODAY)
    assert s.count("found") == 13                       # every row discovery ever wrote, dropped ones too
    assert s.count("scored") == 0 and s.count("shortlisted") == 0 and s.count("applied") == 0
    assert s.last_discover == "2026-10-07" and s.discover_age == 1
    assert [x.source for x in s.sources] == ["remotive", "adzuna", "greenhouse"]   # dead first, then by pulled
    dead, adzuna = s.sources[0], s.sources[1]
    assert dead.dead and dead.runs == 2 and dead.rate is None
    assert (adzuna.pulled, adzuna.new, adzuna.applied, adzuna.replied, adzuna.dead) == (9, 9, 0, 0, False)
    assert s.bands == ()


def test_a_seeded_db_fills_every_part_of_the_snapshot(tmp_db):
    for _ in range(30):
        _add(status="discovered", source="adzuna")
    _add(status="discovered", source="adzuna", match_score=55)
    _add(status="shortlisted", source="adzuna", match_score=88)
    backlog = _add(status="backlog", source="lever", match_score=91)
    held = _add(status="rejected", source="lever", match_score=72)          # shortlisted, then dropped by hand
    _event(held, "2026-09-01T10:00:00+00:00", "shortlisted")
    waiting = _add(status="applied", source="adzuna", match_score=93, applied_at="2026-10-05")
    screen = _add(status="screen", source="adzuna", match_score=85, applied_at="2026-09-20")
    interview = _add(status="interview", source="lever", match_score=95, applied_at="2026-09-01")
    rejected = _add(status="rejected", source="manual", match_score=None, applied_at="2026-08-01")
    _event(screen, "2026-09-20T09:00:00+00:00", "applied")
    _event(screen, "2026-09-30T09:00:00+00:00", "screen")
    _event(interview, "2026-09-01T09:00:00+00:00", "applied")
    _event(interview, "2026-09-05T09:00:00+00:00", "screen")
    _event(interview, "2026-09-15T09:00:00+00:00", "interview")
    _event(rejected, "2026-08-01T09:00:00+00:00", "applied")
    _event(rejected, "2026-08-21T09:00:00+00:00", "rejected")
    _runs(("2026-09-20T10:00:00+00:00", "adzuna", 50, 20, 1), ("2026-09-21T10:00:00+00:00", "adzuna", 40, 11, 1),
          ("2026-09-21T10:00:00+00:00", "lever", 7, 1, 1))
    led = hunt_ledger.Ledger.create("20260919-1702", "claude", {}, ["triage"], tmp_db / "hunt")
    led.move_stage("triage", "running")
    led.add_units("triage", [{"id": "chunk_000", "input": None, "output": None, "harness": "claude", "model": "haiku"}])
    led.move_unit("triage", "chunk_000", "running")
    led.move_unit("triage", "chunk_000", "failed", verdict="short", usage={"input": 1000, "output": 10, "cost_usd": 0.05})
    led.move_stage("triage", "failed")
    led.finish()

    s = data.stats(TODAY)
    assert dict(s.funnel) == {"found": 38, "scored": 7, "shortlisted": 7, "applied": 4, "replied": 3,
                              "screen": 2, "interview": 1, "offer": 0}
    assert (backlog, waiting) and s.applications == 4 and s.replied == 3 and s.reply_rate == 75
    assert (s.waiting, s.interviewing) == (1, 2)
    assert (s.applied_7d, s.applied_28d) == (1, 2)          # 10-05 inside 7 days, 09-20 inside 28, 09-01 outside
    assert sorted(s.reply_days) == [4, 10, 20] and s.median_reply == 10
    assert s.last_discover == "2026-09-21" and s.discover_age == 17
    assert s.hunt == data.HuntLine("20260919-1702", "failed", 1, 1, 1000, 0.05)
    assert [(b.band, b.n, b.replied, b.rate) for b in s.bands] == [
        ("90+", 2, 1, 50), ("80-89", 1, 1, 100), ("unscored", 1, 1, 100)]
    assert [(x.source, x.runs, x.pulled, x.new, x.applied, x.replied, x.rate) for x in s.sources] == [
        ("adzuna", 2, 90, 31, 2, 1, 50), ("lever", 1, 7, 1, 1, 1, 100), ("manual", 0, 0, 0, 1, 1, 100)]


def test_a_hunt_with_no_usage_reports_none_not_zero(tmp_db):
    hunt_ledger.Ledger.create("20261001-0900", "pi", {}, ["discover"], tmp_db / "hunt")
    hunt = data.stats(TODAY).hunt
    assert hunt is not None and (hunt.units, hunt.failed, hunt.context, hunt.cost_usd) == (0, 0, None, None)
