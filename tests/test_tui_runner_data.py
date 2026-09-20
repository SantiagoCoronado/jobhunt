"""The runner's data layer: the stage list, the run ledgers, the per-source last run."""
import sys

import pytest

from src import db
from src.hunt import config as hunt_config
from src.hunt import ledger
from src.tui import data

pytestmark = pytest.mark.usefixtures("tmp_db")


def _ledger(run_id: str, stages=("triage", "pick")) -> ledger.Ledger:
    return ledger.Ledger.create(run_id, "claude", {}, stages, ledger.HUNT_DIR)


def test_stages_are_the_full_hunt_the_registry_in_order_then_the_two_extras():
    found = data.stages()
    assert [s.name for s in found] == ["hunt", *hunt_config.STAGES, "reconcile", "stats"]
    by = {s.name: s for s in found}
    assert by["hunt"].argv == (sys.executable, "-m", "src.hunt", "run") and by["hunt"].kind == "hunt"
    assert by["match"].argv == (sys.executable, "-m", "src.hunt", "run", "--only", "match")
    assert by["match"].kind == "fanned" and by["pick"].kind == "python" and by["stats"].kind == "extra"
    assert by["reconcile"].argv == (sys.executable, "-m", "src.reconcile")       # the dry run, never --apply
    assert by["stats"].argv[-2:] == ("src.stats", "funnel")


def test_only_tailor_and_research_take_the_selection_as_ids():
    by = {s.name: s for s in data.stages()}
    assert [n for n, s in by.items() if s.takes_selection] == ["research", "tailor"]
    assert by["tailor"].argv_for([3625, 9118])[-4:] == ("--only", "tailor", "--ids", "3625,9118")
    assert by["hunt"].argv_for([3625]) == by["hunt"].argv and by["pick"].argv_for([1]) == by["pick"].argv


def test_a_stage_note_names_the_model_and_harness_from_hunt_toml():
    hunt_config.HUNT_TOML.parent.mkdir(parents=True, exist_ok=True)
    hunt_config.HUNT_TOML.write_text('[stages.tailor]\nmodel = "fable"\nconcurrency = 3\n', encoding="utf-8")
    by = {s.name: s for s in data.stages()}
    assert by["tailor"].note == "fable on claude · 3 parallel"             # a setting, not a limit of the TUI
    assert by["hunt"].note == "every stage, on claude · cap 8 parallel"    # the global cap
    assert by["match"].note.startswith("harness default on claude")
    assert by["discover"].note == "python, in process"
    hunt_config.HUNT_TOML.write_text("[stages.nope]\n", encoding="utf-8")        # a broken file still lists
    assert len(data.stages()) == len(hunt_config.STAGES) + 3


def test_copy_text_is_the_slash_command_or_the_shell_line():
    by = {s.name: s for s in data.stages()}
    assert by["hunt"].copy_text == "/jh-hunt" and by["inbox"].copy_text == "/jh-gmail-sync"
    assert by["tailor"].copy_text == "python -m src.hunt run --only tailor"      # /jh-tailor needs an id
    assert by["stats"].copy_text == "python -m src.stats funnel"


def test_hunt_runs_newest_first_with_an_unreadable_ledger_listed():
    assert data.hunt_runs() == []
    _ledger("20260918-0900")
    led = _ledger("20260919-1000")
    led.move_stage("triage", "running")
    (ledger.HUNT_DIR / "20260917-0800").mkdir()                                  # no state.json
    (ledger.HUNT_DIR / "not-a-run").mkdir()
    runs = data.hunt_runs()
    assert [(r.run_id, r.state) for r in runs] == [
        ("20260919-1000", "running"), ("20260918-0900", "pending"), ("20260917-0800", "unreadable")]
    assert runs[0].harness == "claude" and runs[0].started and runs[0].path == ledger.HUNT_DIR / "20260919-1000"


def test_hunt_status_carries_stages_units_logs_and_the_tree():
    assert data.hunt_status("latest") is None and data.hunt_status("20260101-0000") is None
    led = _ledger("20260919-1000")
    led.move_stage("triage", "running")
    led.add_units("triage", [{"id": "chunk_001", "input": "a", "output": "b"},
                             {"id": "chunk_002", "input": "c", "output": "d"}])
    led.move_unit("triage", "chunk_001", "running")
    led.move_unit("triage", "chunk_001", "done")
    led.move_unit("triage", "chunk_002", "running")
    led.move_unit("triage", "chunk_002", "failed", verdict="ids missing: 7")
    led.set_summary("triage", kept=40, dropped=60, detail={"not": "a scalar"})
    st = data.hunt_status("latest")
    assert st is not None and st.run_id == "20260919-1000" and st.state == "running" and st.harness == "claude"
    triage, pick = st.stages
    assert triage.progress == "1/2, 1 failed" and triage.summary == "kept=40 dropped=60" and pick.progress == ""
    bad = triage.units[1]
    assert (bad.id, bad.state, bad.attempts, bad.verdict) == ("chunk_002", "failed", 1, "ids missing: 7")
    assert bad.log == led.run_dir / "logs" / "triage" / "chunk_002.log"
    assert [u.id for u in st.units()] == ["chunk_001", "chunk_002"]
    assert "chunk_002  failed  attempt 1" in st.tree and st.tree == ledger.render_status(led.state, led.run_dir)
    assert st.report_html is None
    (db.DB_PATH.parent / "report.html").write_text("<html>", encoding="utf-8")
    assert data.hunt_status("20260919-1000").report_html == db.DB_PATH.parent / "report.html"


def test_an_unreadable_ledger_is_a_status_with_an_error():
    (ledger.HUNT_DIR / "20260917-0800").mkdir(parents=True)
    (ledger.HUNT_DIR / "20260917-0800" / "state.json").write_text("{not json", encoding="utf-8")
    st = data.hunt_status("20260917-0800")
    assert st is not None and st.state == "unreadable" and "not valid JSON" in st.error and st.stages == ()


def test_tail_reads_the_end_of_a_log_from_a_line_start(tmp_path):
    log = tmp_path / "unit.log"
    assert data.tail(log) == ""
    log.write_text("".join(f"line {i}\n" for i in range(1000)), encoding="utf-8")
    assert data.tail(log).startswith("line 0\n")
    cut = data.tail(log, max_bytes=50)
    assert cut.endswith("line 999\n") and cut.startswith("line 99") and len(cut) <= 50


def test_source_runs_is_the_last_run_per_source_failures_first():
    conn = db.connect(db.DB_PATH)
    rows = [("2026-09-18T10:00", "ashby", 50, 5, 45, 1, None), ("2026-09-19T10:00", "ashby", 60, 9, 51, 1, None),
            ("2026-09-19T10:00", "lever", 0, 0, 0, 0, "HTTP 503"), ("2026-09-19T10:00", "adzuna", 10, 1, 9, 1, None)]
    conn.executemany("INSERT INTO runs (ts, source, pulled, new, seen, ok, error) VALUES (?,?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()
    found = data.source_runs()
    assert [(r.source, r.ok) for r in found] == [("lever", False), ("adzuna", True), ("ashby", True)]
    assert found[0].error == "HTTP 503" and (found[2].pulled, found[2].new, found[2].seen) == (60, 9, 51)
