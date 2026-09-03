"""src.pick: the star rule from SQLite (dream slots, one per company, busy and non-TN skips)."""
from __future__ import annotations

import json
from datetime import date

import pytest

from src import pick as pk
from src.db import connect, log_event

COLS = "id, source, external_id, canonical_key, company, title, location, status, match_score, match_verdict, first_seen, applied_at"


@pytest.fixture
def env(tmp_path, monkeypatch):
    c = connect(tmp_path / "jobs.db")
    rows = [
        (1, "ashby", "x1", "k1", "Steven.com", "Founding Product Engineer", "London, GB", "shortlisted", 86, "{}", "2026-09-01"),
        (2, "workday", "x2", "k2", "Riot Games", "Principal Engineer, AI Enablement", "Los Angeles, USA", "shortlisted", 84, "{}", "2026-09-01"),
        (3, "ashby", "x3", "k3", "Cursor", "Forward Deployed Strategist", "Remote", "shortlisted", 86, "{}", "2026-08-27"),
        (4, "lever", "x4", "k4", "Acme", "Senior Engineer", "Mexico City", "shortlisted", 82, json.dumps({"recommendation": "Yes"}), "2026-09-01"),
        (5, "lever", "x5", "k5", "Acme", "Staff Engineer", "Mexico City", "shortlisted", 81, "{}", "2026-09-01"),
        (6, "lever", "x6", "k6", "Busy Co", "Engineer", "Remote", "shortlisted", 90, "{}", "2026-09-01"),
        (7, "lever", "x7", "k7", "Busy Co", "Old role", "Remote", "applied", 70, "{}", "2026-08-01"),
        (8, "lever", "x8", "k8", "Jobgether", "AI Engineer", "Mexico", "shortlisted", 85, "{}", "2026-09-01"),
        (9, "lever", "x9", "k9", "Nvidia", "Solutions Architect", "Santa Clara", "shortlisted", 90, "{}", "2026-09-01"),
        (10, "lever", "x10", "k10", "Old Reject", "Engineer", "Remote", "shortlisted", 83, "{}", "2026-09-01"),
        (11, "lever", "x11", "k11", "Old Reject", "Past role", "Remote", "rejected", 70, "{}", "2026-01-01"),
        (12, "lever", "x12", "k12", "Fresh Reject", "Engineer", "Remote", "shortlisted", 83, "{}", "2026-09-01"),
        (13, "lever", "x13", "k13", "Fresh Reject", "Past role", "Remote", "rejected", 70, "{}", "2026-08-20"),
        (14, "lever", "x14", "k14", "Undated Co", "Engineer", "Remote", "shortlisted", 83, "{}", "2026-09-01"),
        (15, "lever", "x15", "k15", "Undated Co", "Declined in Notion", "Remote", "withdrawn", 60, "{}", "2026-05-01"),
        (16, "lever", "x16", "k16", "Recent Event Co", "Engineer", "Remote", "shortlisted", 83, "{}", "2026-09-01"),
        (17, "lever", "x17", "k17", "Recent Event Co", "Declined in Notion", "Remote", "withdrawn", 60, "{}", "2026-05-01"),
        (18, "lever", "x18", "k18", "Backlog Co", "Engineer", "Remote", "shortlisted", 83, "{}", "2026-09-01"),
        (19, "lever", "x19", "k19", "Backlog Co", "Held role", "Remote", "backlog", 70, "{}", "2026-08-01"),
        (20, "lever", "x20", "k20", "Wonderful", "FDE (CDMX)", "Mexico City", "shortlisted", None, None, "2026-09-01"),
        (21, "lever", "x21", "k21", "Weird Verdict", "Engineer", "Remote", "shortlisted", 83, "[1, 2]", "2026-09-01"),
        (22, "lever", "x22", "k22", "Late Reject", "Engineer", "Remote", "shortlisted", 83, "{}", "2026-09-01"),
        (23, "lever", "x23", "k23", "Late Reject", "Past role", "Remote", "rejected", 70, "{}", "2026-01-10"),
        (24, "ashby", "x24", "k24", "Nvidia", "Solutions Architect, London", "London, UK", "shortlisted", 91, "{}", "2026-09-01"),
        (25, "workday", "x25", "k25", "Nvidia", "Solutions Architect, Indy", "Indianapolis, IN, USA", "shortlisted", 89, "{}", "2026-09-01"),
        (26, "lever", "x26", "k26", "No Title Co", None, "Remote", "shortlisted", 83, "{}", "2026-09-01"),
    ]
    dated = {11: "2026-02-01", 13: "2026-08-25", 7: "2026-08-01", 23: "2026-01-15"}
    for r in rows:
        c.execute(f"INSERT INTO jobs ({COLS}) VALUES ({','.join('?' * 12)})", (*r, dated.get(r[0])))
    log_event(c, 17, "status_change", {"to": "withdrawn"})     # today's ts: inside any cooldown
    log_event(c, 23, "status_change", {"to": "rejected"})      # applied in January, rejected today
    (tmp_path / "applications" / "other" / "old-reject-11").mkdir(parents=True)
    c.commit()
    monkeypatch.setattr(pk, "connect", lambda: c)
    monkeypatch.setattr(pk, "ROOT", tmp_path)
    monkeypatch.setattr(pk, "is_dream", lambda co: co in ("Steven.com", "Riot Games", "Cursor", "Nvidia"))
    return c


TODAY = date(2026, 9, 2)


def test_star_rule(env):
    picks, skipped, spares = pk.pick(12, 2, today=TODAY)
    ids = [p["id"] for p in picks]
    # two dream slots: NVIDIA Santa Clara (90, after its London row 24 is skipped row-level) and Cursor (86);
    # Steven.com (86, London) and NVIDIA London (91) are skipped without consuming the company
    assert ids[:2] == [9, 3]
    assert all(p["dream"] for p in picks[:2])
    assert 24 not in ids and 25 not in ids          # London skipped, Indianapolis blocked by one-per-company
    # then highest overall, one per company, Busy Co skipped (applied row), Acme once
    assert 8 in ids and 4 in ids and 5 not in ids and 6 not in ids
    why = {s["id"]: s["why"] for s in skipped}
    assert "outside the TN countries" in why[1]
    assert "live application" in why[6]
    assert "outside the TN countries" in why[24]
    # the outcome date is the newest date: applied in January, rejected today -> still held
    assert 22 not in ids and "rejected on" in why[22] and "cooldown" in why[22]
    # terminal outcomes: released after the cooldown (Old Reject, Feb, folder only under other/), blocked inside it
    assert 10 in ids and 12 not in ids and "rejected on 2026-08-25, within the 90-day cooldown" in why[12]
    # undated terminal rows: first_seen in May is past the cooldown -> released; an events ts today -> held
    assert 14 in ids or 14 in [p["id"] for p in spares]
    assert "withdrawn on" in why[16] and "cooldown" in why[16]
    # backlog hold is honoured, unscored rows are listed not picked, a non-dict verdict does not crash
    assert "backlog hold" in why[18]
    assert why[20].startswith("not scored yet") and 20 not in ids
    assert 21 in ids or 21 in [p["id"] for p in spares]
    picks5, _, spares5 = pk.pick(5, 2, today=TODAY)
    assert sum(p["company"] == "Nvidia" for p in picks5) == 1      # one NVIDIA row per pick list
    ids5 = [p["id"] for p in picks5]
    assert len(picks5) == 5 and len(spares5) == 2 and all(p["id"] not in ids5 for p in spares5)
    agg = next(p for p in picks if p["id"] == 8)
    assert "aggregator" in agg["flag"]


def test_cli_prints_picks_and_skips(env, capsys):
    assert pk.main(["--n", "3"]) == 0
    out = capsys.readouterr().out
    assert "picks (3)" in out and "spares (2)" in out and "skipped" in out and "outside the TN countries" in out
    assert "held by the 90-day cooldown" in out          # counted over every held company, not only rows reached
    assert out.count("Steven.com #1") == 1               # a row is evaluated once, whichever loop reaches it first
    assert pk.main(["--n", "12"]) == 0               # includes the NULL-title row without a traceback
    assert "No Title Co" in capsys.readouterr().out


def test_cooldown_window_is_configurable(env):
    picks, skipped, _ = pk.pick(8, 2, cooldown_days=5, today=TODAY)
    assert 12 in [p["id"] for p in picks]            # Aug 25 rejection released with a 5-day window (cutoff Aug 28)
    picks, skipped, _ = pk.pick(8, 2, cooldown_days=400, today=TODAY)
    assert 10 not in [p["id"] for p in picks]        # Feb rejection blocked again with a 400-day window
    picks, skipped, _ = pk.pick(12, 2, cooldown_days=400, today=TODAY)
    assert 14 not in [p["id"] for p in picks]        # the May first_seen fallback is inside a 400-day window


def test_folder_in_pending_blocks_company(env, tmp_path):
    (tmp_path / "applications" / "pending" / "nvidia-9").mkdir(parents=True)
    picks, skipped, spares = pk.pick(12, 2, today=TODAY)
    why = {s["id"]: s["why"] for s in skipped}
    assert all(p["company"] != "Nvidia" for p in picks + spares)
    assert any("application folder" in w for w in why.values())
