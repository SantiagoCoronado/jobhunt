"""`python -m src.stats hunts` (hunt orchestrator PR 5 story 3): every run's ledger as one
line per run and one per stage with units, retries, failures and usage; the DB is never
opened; an unreadable ledger is a line, not a crash."""
from __future__ import annotations

from pathlib import Path

import pytest

from src import stats
from src.hunt import ledger


def _run(hunt_dir: Path, run_id: str, fail_tailor: bool) -> None:
    led = ledger.Ledger.create(run_id, "claude", {}, ["discover", "triage", "tailor", "report"], hunt_dir)
    led.move_stage("discover", "running")
    led.add_units("discover", [{"id": "discover", "input": None, "output": None}])
    led.move_unit("discover", "discover", "running")
    led.move_unit("discover", "discover", "done")
    led.move_stage("discover", "done")
    led.move_stage("triage", "running")
    led.add_units("triage", [{"id": f"chunk_00{i}", "input": None, "output": None, "harness": "claude", "model": "haiku"} for i in range(2)])
    led.move_unit("triage", "chunk_000", "running")
    led.move_unit("triage", "chunk_000", "done", usage={"input": 1000, "output": 100, "cache_read": 4000, "cost_usd": 0.10})
    led.move_unit("triage", "chunk_001", "running")
    led.move_unit("triage", "chunk_001", "failed", verdict="short", usage={"input": 900, "output": 10})
    led.move_unit("triage", "chunk_001", "running")
    led.move_unit("triage", "chunk_001", "done", usage={"input": 1100, "output": 120, "cost_usd": 0.12})
    led.move_stage("triage", "done")
    led.move_stage("tailor", "running")
    led.add_units("tailor", [{"id": "job_7", "input": None, "output": None, "harness": "codex", "model": None}])
    led.move_unit("tailor", "job_7", "running")
    led.move_unit("tailor", "job_7", "failed" if fail_tailor else "done", verdict="build FAIL" if fail_tailor else "ok",
                  usage={"input": 20000, "output": 3000, "cache_create": 5000})
    led.move_stage("tailor", "failed" if fail_tailor else "done")
    led.move_stage("report", "skipped", note="--to tailor")
    led.finish()


@pytest.fixture
def hunt_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path / "hunt")
    monkeypatch.setattr(stats, "connect", lambda *a, **k: pytest.fail("hunts must never open the DB"))
    _run(tmp_path / "hunt", "20260921-0900", fail_tailor=False)
    _run(tmp_path / "hunt", "20260922-0900", fail_tailor=True)
    (tmp_path / "hunt" / "20260923-0900").mkdir()
    (tmp_path / "hunt" / "20260923-0900" / "state.json").write_text("{not json", encoding="utf-8")
    return tmp_path / "hunt"


def test_hunts_data_counts_units_retries_failures_and_usage_per_stage(hunt_dir):
    runs = stats.hunts_data()
    assert [r["run_id"] for r in runs] == ["20260923-0900", "20260922-0900", "20260921-0900"]
    assert runs[0]["state"] == "unreadable" and runs[0]["stages"] == [] and runs[0]["context"] is None
    failed = runs[1]
    assert (failed["state"], failed["harness"], failed["units"], failed["retries"], failed["failed"]) == ("failed", "claude", 4, 1, 1)
    assert (failed["context"], failed["output"], failed["cost_usd"]) == (32000, 3230, 0.22)      # model units only
    by_name = {s["name"]: s for s in failed["stages"]}
    assert list(by_name) == ["discover", "triage", "tailor"]                                    # report planned no unit
    assert by_name["discover"] == {"name": "discover", "state": "done", "units": 1, "retries": 0, "failed": 0,
                                   "context": None, "output": None, "cost_usd": None}
    assert by_name["triage"] == {"name": "triage", "state": "done", "units": 2, "retries": 1, "failed": 0,
                                 "context": 7000, "output": 230, "cost_usd": 0.22}
    assert by_name["tailor"]["failed"] == 1 and by_name["tailor"]["context"] == 25000 and by_name["tailor"]["cost_usd"] is None
    assert runs[2]["failed"] == 0 and runs[2]["state"] == "done"
    assert [r["run_id"] for r in stats.hunts_data(last=1)] == ["20260923-0900"]


def test_hunts_prints_one_line_per_run_then_per_stage(hunt_dir, capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["stats", "hunts", "--last", "2"])
    stats.main()
    out = capsys.readouterr().out
    assert out.startswith("Hunt runs: 2 (newest first;")
    assert "  20260923-0900  unreadable -             0       0      0           -         -       -  -" in out
    assert "  20260922-0900  failed     claude        4       1      1      32,000     3,230    0.22  " in out
    assert "20260921-0900" not in out
    block = out.split("\n20260922-0900  failed  claude\n")[1]
    assert "  triage     done         2       1      0       7,000       230    0.22" in block
    assert "  tailor     failed       1       0      1      25,000     3,000       -" in block
    assert "  discover   done         1       0      0           -         -       -" in block and "report" not in block
    assert "—" not in out


def test_hunts_with_no_runs_says_so(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path / "none")
    stats.hunts()
    assert capsys.readouterr().out.startswith("No hunt runs under ")
