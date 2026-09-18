"""src/hunt/ledger.py, the read side: run ids, listing, `latest`, the status tree."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from src.hunt import ledger


def _run(hunt_dir: Path, run_id: str, stages: list[dict], started: str = "2026-09-18T16:30") -> Path:
    d = hunt_dir / run_id
    d.mkdir(parents=True)
    (d / "state.json").write_text(json.dumps({"run_id": run_id, "started": started, "harness": "claude",
                                              "stages": stages}))
    return d


def test_run_id_is_sortable_and_readable():
    assert ledger.new_run_id(datetime(2026, 9, 18, 16, 30)) == "20260918-1630"
    assert ledger.RUN_ID_RE.match(ledger.new_run_id())


def test_empty_folder_lists_nothing_and_resolves_nothing(tmp_path):
    assert ledger.list_runs(tmp_path) == []
    assert ledger.list_runs(tmp_path / "absent") == []
    assert ledger.resolve("latest", tmp_path) is None and ledger.resolve(None, tmp_path) is None
    assert ledger.resolve("20260918-1630", tmp_path) is None
    assert ledger.format_runs([]) == "no runs yet"


def test_runs_sort_newest_first_and_derive_their_state(tmp_path):
    _run(tmp_path, "20260917-0900", [{"name": "discover", "state": "done"}, {"name": "report", "state": "done"}])
    _run(tmp_path, "20260918-1630", [{"name": "discover", "state": "done"}, {"name": "triage", "state": "running"}])
    _run(tmp_path, "20260918-1700", [{"name": "discover", "state": "failed"}])
    (tmp_path / "20260918-1800").mkdir()                       # a crashed run with no state yet
    (tmp_path / "scratch").mkdir()                             # not a run folder
    runs = ledger.list_runs(tmp_path)
    assert [r.run_id for r in runs] == ["20260918-1800", "20260918-1700", "20260918-1630", "20260917-0900"]
    assert [r.state for r in runs] == ["unreadable", "failed", "running", "done"]
    assert ledger.resolve("latest", tmp_path) == tmp_path / "20260918-1800"
    assert ledger.resolve("20260917-0900", tmp_path) == tmp_path / "20260917-0900"
    text = ledger.format_runs(runs)
    assert "20260918-1630  running     claude     started 2026-09-18T16:30" in text
    assert "20260918-1800  unreadable  -          started -" in text


def test_run_state_rules():
    assert ledger.run_state({"stages": []}) == "pending"
    assert ledger.run_state({"stages": [{"state": "pending"}, {"state": "pending"}]}) == "pending"
    assert ledger.run_state({"stages": [{"state": "done"}, {"state": "pending"}]}) == "running"
    assert ledger.run_state({"stages": [{"state": "done"}, {"state": "skipped"}]}) == "done"
    assert ledger.run_state({"stages": [{"state": "running"}, {"state": "failed"}]}) == "failed"


def test_load_state_rejects_missing_and_broken_files(tmp_path):
    with pytest.raises(FileNotFoundError):
        ledger.load_state(tmp_path)
    (tmp_path / "state.json").write_text("{not json")
    with pytest.raises(ValueError, match="not valid JSON"):
        ledger.load_state(tmp_path)
    (tmp_path / "state.json").write_text('{"stages": []}')
    with pytest.raises(ValueError, match="not a hunt state file"):
        ledger.load_state(tmp_path)


def test_status_tree_counts_units_and_tails_the_running_log(tmp_path):
    d = _run(tmp_path, "20260918-1630", [
        {"name": "discover", "state": "done", "units": [{"id": "discover", "state": "done", "attempts": 1}]},
        {"name": "triage", "state": "running", "units": [
            {"id": "chunk_000", "state": "done", "attempts": 1},
            {"id": "chunk_001", "state": "running", "attempts": 2, "log": "logs/triage/chunk_001.log"},
            {"id": "chunk_002", "state": "failed", "attempts": 3, "verdict": "short output: 40 of 100 ids"},
            {"id": "chunk_003", "state": "pending", "attempts": 0},
        ]},
        {"name": "inbox", "state": "skipped", "note": "no mail account configured"},
        {"name": "match", "state": "pending"},
    ])
    (d / "logs" / "triage").mkdir(parents=True)
    (d / "logs" / "triage" / "chunk_001.log").write_text("reading chunk\nwrote 60 of 100\n\n")
    out = ledger.render_status(ledger.load_state(d), d)
    lines = out.splitlines()
    assert lines[0] == "run 20260918-1630  claude  started 2026-09-18T16:30  running"   # a failed unit in a running stage is a retry, not a failed run
    assert "  discover  done      1/1 done" in lines
    assert "  triage    running   1/4 done, 1 running, 1 failed" in lines
    assert "    chunk_001  running  attempt 2  last: wrote 60 of 100" in lines
    assert "    chunk_002  failed  attempt 3  short output: 40 of 100 ids" in lines
    assert "  inbox     skipped   (no mail account configured)" in lines
    assert "  match     pending" in lines
    assert "chunk_000" not in out and "chunk_003" not in out
