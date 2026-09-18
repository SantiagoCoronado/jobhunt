"""hunt run end to end on a temp DB: the Python stages (discover with fake adapters, pick,
report), the ledger they leave behind, the lock, the exit codes."""
from __future__ import annotations

import json
import types

import pytest

from src import db, discover
from src import pick as pick_mod
from src.hunt import cli, ledger
from src.hunt import config as hc
from src.hunt import run as run_mod
from src.hunt.stages import REGISTRY, report as report_stage
from src.models import Job


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Temp DB, temp hunt dir, temp report path. discover and pick bind `connect` at import,
    so they are patched by name too; without that a test writes into the real data/jobs.db."""
    real_connect = db.connect
    temp_connect = lambda *a, **k: real_connect(tmp_path / "jobs.db")  # noqa: E731
    monkeypatch.setattr(db, "connect", temp_connect)
    monkeypatch.setattr(discover, "connect", temp_connect)
    monkeypatch.setattr(pick_mod, "connect", temp_connect)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "jobs.db")
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path / "hunt")
    # never shell out to a real harness from here (the no-picks test selects stubbed fanned
    # stages, whose models the run would otherwise smoke-test); the validation test patches its own
    monkeypatch.setattr(run_mod, "validate_models", lambda cfg, stages, harness: [])
    return tmp_path


def _fake_sources(monkeypatch, fetchers: dict):
    """Two enabled sources whose adapters are replaced by `fetchers[name]()`."""
    monkeypatch.setattr(discover, "ADAPTERS", list(fetchers))
    monkeypatch.setattr(discover, "load_sources", lambda: {n: {"enabled": True} for n in fetchers})
    monkeypatch.setattr(discover, "missing_targeting", lambda name, cfg: [])
    monkeypatch.setattr(discover, "keep_title", lambda cfg, title: True)
    monkeypatch.setattr(discover.importlib, "import_module",
                        lambda name, package=None: types.SimpleNamespace(fetch=lambda cfg: fetchers[name.rsplit(".", 1)[-1]]()))


def _job(source: str, i: int) -> Job:
    return Job(source=source, external_id=f"{source}-{i}", url=f"https://x/{i}", company=f"Co{i}", title="Software Engineer")


def _boom():
    raise RuntimeError("api down")


def test_run_only_discover_end_to_end(env, monkeypatch, capsys):
    _fake_sources(monkeypatch, {"greenhouse": lambda: [_job("greenhouse", 1), _job("greenhouse", 2)], "lever": _boom})
    assert cli.main(["run", "--only", "discover"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("run ") and "started: discover on claude" in out[0]
    assert out[1] == "discover running"
    assert out[2] == "discover done  sources_ok=1 sources_failed=1 new=2 seen=0"
    assert out[3].endswith(" done")
    [run] = ledger.list_runs(env / "hunt")
    assert run.state == "done" and run.harness == "claude"
    st = ledger.load_state(run.path)
    disc = st["stages"][0]
    assert disc["summary"] == {"sources_ok": 1, "sources_failed": 1, "new": 2, "seen": 0, "failed": ["lever"]}
    assert disc["units"][0]["state"] == "done" and disc["units"][0]["verdict"] == "ok"
    log = (run.path / "logs" / "discover" / "discover.log").read_text()
    assert "greenhouse" in log and "lever" in log and "FAILED: api down" in log and "Maintenance:" in log
    assert st["config"]["stages"]["triage"]["model"] == "haiku"           # the snapshot travels with the run
    assert db.connect().execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 2
    assert not (env / "hunt" / ".lock").exists()
    assert cli.main(["status"]) == 0
    assert "  discover  done      1/1 done  sources_ok=1 sources_failed=1 new=2 seen=0" in capsys.readouterr().out


def test_discover_with_no_working_source_fails_the_run(env, monkeypatch, capsys):
    _fake_sources(monkeypatch, {"greenhouse": _boom, "lever": _boom})
    assert cli.main(["run", "--only", "discover"]) == 2
    out = capsys.readouterr().out
    assert "discover failed: no source succeeded: greenhouse, lever" in out
    st = ledger.load_state(ledger.resolve("latest", env / "hunt"))
    assert st["stages"][0]["state"] == "failed" and ledger.run_state(st) == "failed"
    _fake_sources(monkeypatch, {})
    assert run_mod.run(hc.defaults(), ["discover"], "claude", run_id="20260918-1600", emit=lambda s: None) == 2
    st = ledger.load_state(env / "hunt" / "20260918-1600")
    assert st["stages"][0]["note"] == "no source succeeded: none enabled or targeted"


def _shortlist(rows: list[tuple[str, str, int, str | None]]) -> None:
    conn = db.connect()
    for i, (company, title, score, flag_loc) in enumerate(rows, 1):
        conn.execute("INSERT INTO jobs (source, external_id, canonical_key, url, company, title, location, status, "
                     "match_score, match_verdict, first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                     ("greenhouse", f"e{i}", f"k{i}", "https://x", company, title, flag_loc or "Remote", "shortlisted",
                      score, json.dumps({"recommendation": "apply", "location_ok": True}), "2026-09-01", "2026-09-18"))
    conn.commit()


def test_pick_and_report_write_the_run_files_and_flag_aggregators(env, capsys):
    _shortlist([("Acme", "Backend Engineer", 90, None), ("Jobgether", "Platform Engineer", 88, None),
                ("Beta", "Frontend Engineer", 85, None), ("Gamma", "AI Engineer", 80, None)])
    lines: list[str] = []
    cfg = hc.parse({"pick": {"n": 2, "dream_slots": 1}})
    assert run_mod.run(cfg, ["pick", "report"], "claude", run_id="20260918-1700", emit=lines.append) == 0
    run_dir = env / "hunt" / "20260918-1700"
    picks = json.loads((run_dir / "picks.json").read_text())
    assert [p["company"] for p in picks["picks"]] == ["Acme", "Beta"]        # the aggregator row lost its slot
    assert [p["company"] for p in picks["flagged"]] == ["Jobgether"] and [p["company"] for p in picks["spares"]] == ["Gamma"]
    assert "pick done  picks=2 flagged=1 skipped=0 spares=1" in lines
    assert any(line.startswith("pick needs a human: pick: #2 Jobgether, aggregator row") for line in lines)
    st = ledger.load_state(run_dir)
    assert st["stages"][0]["summary"]["needs_human"][0].startswith("pick: #2 Jobgether")
    assert (env / "report.html").exists() and (run_dir / "report.md").exists()
    md = (run_dir / "report.md").read_text()
    assert md.startswith("# Hunt 20260918-1700\n") and "| pick | done | 1/1 | picks 2, flagged 1, skipped 0, spares 1 |" in md
    assert "- #1 Acme: Backend Engineer (Remote, match 90)" in md and "- pick: #2 Jobgether, aggregator row" in md
    assert st["stages"][1]["summary"]["md"] == "report.md"


def test_no_picks_skips_to_the_report_and_exits_3(env, monkeypatch):
    for name in ("research", "tailor"):                       # stand-ins until PR 3: they must be skipped, never run
        monkeypatch.setitem(REGISTRY, name, REGISTRY[name].__class__(name, "python", run=lambda ctx: 1 / 0))
    lines: list[str] = []
    rc = run_mod.run(hc.defaults(), ["pick", "research", "tailor", "report"], "claude", run_id="20260918-1701",
                     emit=lines.append)
    assert rc == 3, lines
    st = ledger.load_state(env / "hunt" / "20260918-1701")
    assert [(s["name"], s["state"]) for s in st["stages"]] == [("pick", "done"), ("research", "skipped"),
                                                              ("tailor", "skipped"), ("report", "done")]
    assert "pick: nothing to tailor, the report still runs, then the run stops" in lines
    assert "research skipped (no picks)" in lines and lines[-1] == "run 20260918-1701 done"
    assert "- none" in (env / "hunt" / "20260918-1701" / "report.md").read_text()


def test_a_stage_with_no_runner_resume_and_the_lock_are_refused_cleanly(env, capsys, monkeypatch):
    # never `cli.main(["run"])` bare in a test: every stage has a runner now, so that IS a hunt
    assert all(s.implemented for s in REGISTRY.values())
    monkeypatch.setitem(REGISTRY, "research", REGISTRY["research"].__class__("research", "fanned", role="company-researcher"))
    assert cli.main(["run", "--from", "pick", "--to", "research"]) == 2
    err = capsys.readouterr().out
    assert "research not in this build yet" in err and "select from discover, " in err
    assert cli.main(["run", "--only", "pick", "--resume", "latest"]) == 2
    assert "--resume continues the stages of that run" in capsys.readouterr().err
    (env / "hunt" / ".lock").mkdir(parents=True)
    assert cli.main(["run", "--only", "pick"]) == 2
    assert "another hunt holds" in capsys.readouterr().out
    assert ledger.list_runs(env / "hunt") == []
    (env / "hunt" / ".lock").rmdir()
    assert run_mod.run(hc.defaults(), [], "claude", emit=lambda s: None) == 0


def test_the_conftest_guard_refuses_a_real_agent_cli():
    import subprocess
    with pytest.raises(AssertionError, match="real agent CLI"):
        subprocess.run(["claude", "--version"], check=False)
    with pytest.raises(AssertionError, match="real agent CLI"):
        subprocess.Popen(["/opt/homebrew/bin/codex", "exec"])


def test_a_crashing_stage_is_a_failed_stage_with_its_traceback_logged(env, monkeypatch):
    def explode(ctx):
        raise KeyError("picks")
    monkeypatch.setitem(REGISTRY, "pick", REGISTRY["pick"].__class__("pick", "python", run=explode))
    lines: list[str] = []
    assert run_mod.run(hc.defaults(), ["pick", "report"], "claude", run_id="20260918-1702", emit=lines.append) == 2
    run_dir = env / "hunt" / "20260918-1702"
    assert "pick failed: KeyError: 'picks'" in lines and lines[-1] == "run 20260918-1702 failed"
    assert "KeyError" in (run_dir / "logs" / "pick" / "pick.log").read_text()
    st = ledger.load_state(run_dir)
    assert st["stages"][1]["state"] == "pending" and not (env / "hunt" / ".lock").exists()


def test_quiet_keeps_the_run_lines_and_a_same_minute_run_id_is_refused(env, capsys, monkeypatch):
    _shortlist([("Acme", "Backend Engineer", 90, None)])
    monkeypatch.setattr(run_mod, "new_run_id", lambda now=None: "20260918-1800")
    assert cli.main(["run", "--only", "pick", "--quiet"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 2 and out[0].startswith("run 20260918-1800 started") and out[1] == "run 20260918-1800 done"
    assert cli.main(["run", "--only", "pick"]) == 2
    assert "a run started this minute" in capsys.readouterr().out


def test_report_markdown_and_html_path(env):
    assert report_stage.html_path() == env / "report.html"
    led = ledger.Ledger.create("20260918-1900", "claude", {}, ["discover"], env / "hunt")
    md = report_stage.render_markdown(led)
    assert "| discover | pending | 0/0 |  |" in md and "## Needs a human\n\n- nothing" in md
    assert isinstance(REGISTRY["research"].needs, frozenset) and "web" in REGISTRY["research"].needs
