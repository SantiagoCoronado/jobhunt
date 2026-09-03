"""src.pick: the star rule from SQLite (dream slots, one per company, busy and non-TN skips)."""
from __future__ import annotations

import json

import pytest

from src import pick as pk
from src.db import connect

COLS = "id, source, external_id, canonical_key, company, title, location, status, match_score, match_verdict, first_seen"


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
    ]
    for r in rows:
        c.execute(f"INSERT INTO jobs ({COLS}) VALUES ({','.join('?' * 11)})", r)
    c.commit()
    (tmp_path / "applications" / "pending" / "nvidia-9").mkdir(parents=True)
    monkeypatch.setattr(pk, "connect", lambda: c)
    monkeypatch.setattr(pk, "ROOT", tmp_path)
    monkeypatch.setattr(pk, "is_dream", lambda co: co in ("Steven.com", "Riot Games", "Cursor", "Nvidia"))
    return c


def test_star_rule(env):
    picks, skipped = pk.pick(5, 2)
    ids = [p["id"] for p in picks]
    # two dream slots: Cursor (86) and Riot (84); Steven.com (86, London) and Nvidia (folder) are skipped
    assert ids[:2] == [3, 2]
    assert all(p["dream"] for p in picks[:2])
    # then highest overall, one per company, Busy Co skipped (applied row), Acme once
    assert 8 in ids and 4 in ids and 5 not in ids and 6 not in ids
    why = {s["id"]: s["why"] for s in skipped}
    assert "outside the TN countries" in why[1]
    assert "already has an application" in why[6] and "already has an application" in why[9]
    agg = next(p for p in picks if p["id"] == 8)
    assert "aggregator" in agg["flag"]


def test_cli_prints_picks_and_skips(env, capsys):
    assert pk.main(["--n", "3"]) == 0
    out = capsys.readouterr().out
    assert "picks (3)" in out and "skipped" in out and "outside the TN countries" in out
