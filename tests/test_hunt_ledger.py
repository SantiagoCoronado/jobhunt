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


# ---- the writer (story 2) ---------------------------------------------------------------

def _clock():
    n = [0]

    def tick() -> str:
        n[0] += 1
        return f"2026-09-18T16:{n[0]:02d}:00"
    return tick


def _drive(hunt_dir: Path) -> ledger.Ledger:
    """A synthetic run: discover done, triage with a retry and a failure, inbox skipped."""
    led = ledger.Ledger.create("20260918-1630", "claude", {"harness": {"default": "claude"}},
                               ["discover", "triage", "inbox", "pick"], hunt_dir, clock=_clock())
    led.move_stage("discover", "running")
    led.add_units("discover", [{"id": "discover", "input": None, "output": "runs"}])
    led.move_unit("discover", "discover", "running")
    led.move_unit("discover", "discover", "done", verdict="17 sources ok")
    led.set_summary("discover", sources_ok=17, sources_failed=0)
    led.move_stage("discover", "done")
    led.move_stage("triage", "running")
    led.add_units("triage", [{"id": f"chunk_00{i}", "input": f"data/triage/chunk_00{i}.json",
                              "output": f"data/triage/out_00{i}.json", "harness": "claude", "model": "haiku"}
                             for i in range(3)])
    led.move_unit("triage", "chunk_000", "running")
    led.move_unit("triage", "chunk_000", "done", usage={"input": 100, "output": 20, "cost_usd": 0.01})
    led.move_unit("triage", "chunk_001", "running")
    led.move_unit("triage", "chunk_001", "failed", verdict="short output", usage={"input": 90, "output": 5})
    led.move_unit("triage", "chunk_001", "running")                       # the retry
    led.move_unit("triage", "chunk_001", "done", usage={"input": 95, "output": 25, "cost_usd": 0.02})
    led.move_unit("triage", "chunk_002", "running")
    led.move_unit("triage", "chunk_002", "failed", verdict="timeout")
    led.move_stage("triage", "failed", note="1 unit failed after 1 attempt")
    led.move_stage("inbox", "skipped", note="no mail account configured")
    return led


def test_create_writes_the_folder_and_the_first_event(tmp_path):
    led = ledger.Ledger.create("20260918-1630", "claude", {"x": 1}, ["discover"], tmp_path, clock=_clock())
    assert (tmp_path / "20260918-1630" / "prompts").is_dir() and (tmp_path / "20260918-1630" / "logs").is_dir()
    st = ledger.load_state(led.run_dir)
    assert st["started"] == "2026-09-18T16:01:00" and st["ended"] is None and st["config"] == {"x": 1}
    assert st["stages"] == [{"name": "discover", "state": "pending", "started": None, "ended": None,
                             "note": None, "units": [], "summary": {}}]
    assert led.events() == [{"ts": "2026-09-18T16:02:00", "stage": None, "unit": None, "from": None,
                             "to": "started", "note": None}]
    with pytest.raises(FileExistsError):
        ledger.Ledger.create("20260918-1630", "claude", {}, ["discover"], tmp_path)


def test_transitions_land_in_state_and_events_and_replay_to_the_same_skeleton(tmp_path):
    led = _drive(tmp_path)
    st = ledger.load_state(led.run_dir)                     # what a resume or `status` reads
    assert ledger.run_state(st) == "failed"
    tri = next(s for s in st["stages"] if s["name"] == "triage")
    assert tri["state"] == "failed" and tri["note"] == "1 unit failed after 1 attempt"
    assert tri["started"] and tri["ended"] and tri["started"] < tri["ended"]
    by_id = {u["id"]: u for u in tri["units"]}
    assert by_id["chunk_001"]["attempts"] == 2 and by_id["chunk_001"]["state"] == "done"
    assert by_id["chunk_001"]["usage"] == {"input": 185, "output": 30, "cache_read": None,
                                           "cache_create": None, "cost_usd": 0.02}       # both attempts count
    assert by_id["chunk_002"]["verdict"] == "timeout" and by_id["chunk_002"]["log"] == "logs/triage/chunk_002.log"
    disc = st["stages"][0]
    assert disc["summary"] == {"sources_ok": 17, "sources_failed": 0}
    events = led.events()
    assert [e["to"] for e in events][:6] == ["started", "running", "pending", "running", "done", "done"]
    assert ledger.Ledger.replay(events, led.stage_names()) == led.skeleton()
    assert led.skeleton()["pick"] == {"state": "pending", "units": {}}
    reopened = ledger.Ledger.open(led.run_dir, clock=_clock())        # a later session continues
    reopened.move_stage("triage", "running")
    reopened.move_unit("triage", "chunk_002", "running")
    reopened.move_unit("triage", "chunk_002", "done")
    reopened.move_stage("triage", "done", note="")
    assert reopened.finish() == "running"                            # pick is still pending
    assert ledger.load_state(led.run_dir)["ended"] is not None
    assert ledger.Ledger.replay(reopened.events(), reopened.stage_names()) == reopened.skeleton()
    assert reopened.skeleton()["triage"]["units"]["chunk_002"] == {"state": "done", "attempts": 2}
    assert ledger.render_status(reopened.state).splitlines()[1] == "  discover  done      1/1 done  sources_ok=17 sources_failed=0"


@pytest.mark.parametrize("call,needle", [
    (lambda led: led.move_stage("discover", "running"), "stage discover cannot move done -> running"),
    (lambda led: led.move_stage("pick", "done"), "stage pick cannot move pending -> done"),
    (lambda led: led.move_unit("triage", "chunk_000", "running"), "unit triage/chunk_000 cannot move done -> running"),
    (lambda led: led.move_unit("triage", "chunk_002", "done"), "cannot move failed -> done"),
    (lambda led: led.add_units("pick", [{"id": "a"}, {"id": "a"}]), "already has unit 'a'"),
    (lambda led: led.add_units("triage", [{"id": "chunk_009"}]), "stage triage is failed, cannot add units"),
    (lambda led: led.add_units("inbox", [{"id": "x"}]), "stage inbox is skipped, cannot add units"),
    (lambda led: led.stage("nope"), "no stage 'nope'"),
    (lambda led: led.unit("triage", "nope"), "has no unit 'nope'"),
])
def test_illegal_transitions_raise_and_change_nothing(tmp_path, call, needle):
    led = _drive(tmp_path)
    before = json.loads((led.run_dir / "state.json").read_text())
    n_events = len(led.events())
    with pytest.raises(ValueError, match=__import__("re").escape(needle)):
        call(led)
    assert json.loads((led.run_dir / "state.json").read_text()) == before
    assert len(led.events()) == n_events


def test_a_crash_mid_save_leaves_the_previous_state_readable(tmp_path, monkeypatch):
    led = _drive(tmp_path)
    before = (led.run_dir / "state.json").read_text()

    def boom(src, dst):
        raise OSError("disk full")
    monkeypatch.setattr(ledger.os, "replace", boom)
    with pytest.raises(OSError):
        led.move_stage("pick", "running")
    assert (led.run_dir / "state.json").read_text() == before
    assert not (led.run_dir / "state.json.tmp").exists()
    assert ledger.load_state(led.run_dir)["run_id"] == "20260918-1630"


def test_add_usage_keeps_unreported_fields_none():
    assert ledger.add_usage(None, None) is None
    assert ledger.add_usage(None, {"input": 5})["input"] == 5
    total = ledger.add_usage({"input": 5, "output": None, "cache_read": None, "cache_create": None, "cost_usd": None},
                             {"input": 2, "output": 3})
    assert total == {"input": 7, "output": 3, "cache_read": None, "cache_create": None, "cost_usd": None}
