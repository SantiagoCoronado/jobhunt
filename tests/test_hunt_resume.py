"""--resume: a hunt killed mid-stage (a real SIGKILL of a child process running the triage
stage) is resumed in this process: the dead run's lock is taken over, done units are skipped,
the interrupted unit runs again, nothing is exported twice; plus the re-verify of outputs on
disk, a changed chunk list, Ctrl+C closing the ledger, and the CLI's refusals."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
from hunt_fakes import FakeAgentHarness

from src import db
from src import triage as triage_mod
from src.hunt import cli, ledger
from src.hunt import config as hc
from src.hunt import run as run_mod

REPO = Path(__file__).resolve().parent.parent
RUN_ID = "20260919-1000"
CFG = {"stages": {"triage": {"chunk": 10, "min_pile": 5, "retries": 1, "concurrency": 1}}}

DRIVER = '''
import json, sys
from pathlib import Path
sys.path.insert(0, {repo!r}); sys.path.insert(0, {tests!r})
tmp = Path({tmp!r})
from src import config, db
from src import triage as triage_mod
from src.hunt import config as hc, ledger, run as run_mod
from hunt_fakes import FakeAgentHarness
for key, name in (("profile", "profile.yaml"), ("master_resume", "master_resume.yaml"), ("answers", "answers.yaml")):
    config.USER_FILES[key] = Path({tests!r}) / "fixtures" / name
real = db.connect
triage_mod.connect = db.connect = lambda *a, **k: real(tmp / "jobs.db")
triage_mod.TRIAGE_DIR = tmp / "data" / "triage"
run_mod.validate_models = lambda cfg, stages, harness: []
fake = FakeAgentHarness(tmp)
rc = run_mod.run(hc.parse({cfg!r}), ["triage"], "fake", cwd=tmp, hunt_dir=tmp / "hunt", run_id={run_id!r},
                 emit=lambda s: None, get_harness=lambda name: fake)
sys.exit(rc)
'''


@pytest.fixture
def env(tmp_path, monkeypatch):
    real_connect = db.connect
    temp_connect = lambda *a, **k: real_connect(tmp_path / "jobs.db")  # noqa: E731
    monkeypatch.setattr(db, "connect", temp_connect)
    monkeypatch.setattr(triage_mod, "connect", temp_connect)
    monkeypatch.setattr(triage_mod, "TRIAGE_DIR", tmp_path / "data" / "triage")
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path / "hunt")
    monkeypatch.setattr(run_mod, "validate_models", lambda cfg, stages, harness: [])
    conn = db.connect()
    for i in range(1, 26):
        conn.execute("INSERT INTO jobs (source, external_id, canonical_key, url, company, title, location, description, "
                     "status, first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                     ("greenhouse", f"e{i}", f"k{i:03d}", "https://x", f"Co{i}", "Software Engineer", "Remote",
                      "Build things.", "discovered", "2026-09-01", "2026-09-18"))
    conn.commit()
    return tmp_path


def _resume(env, run="latest", plan=None):
    (env / "fake_agent.json").write_text(json.dumps(plan or {}))
    fake = FakeAgentHarness(env)
    lines: list[str] = []
    rc = run_mod.run(hc.parse(CFG), [], None, cwd=env, resume=run, emit=lines.append,
                     get_harness=lambda name: fake, pool_options={"sleep": lambda s: None})
    return rc, lines, fake, ledger.load_state(env / "hunt" / RUN_ID)


def _killed_run(env) -> None:
    """A child process runs the triage stage; the agent for chunk_001 SIGKILLs it."""
    (env / "fake_agent.json").write_text(json.dumps({"chunk_001": {"kill_parent": 1}}))
    driver = env / "driver.py"
    driver.write_text(DRIVER.format(repo=str(REPO), tests=str(REPO / "tests"), tmp=str(env), cfg=CFG, run_id=RUN_ID))
    cp = subprocess.run([sys.executable, str(driver)], cwd=REPO, capture_output=True, text=True, timeout=60, check=False)
    assert cp.returncode == -9, cp.stderr


def test_a_hunt_killed_mid_stage_is_resumed_where_it_died(env, monkeypatch):
    _killed_run(env)
    dead = ledger.load_state(env / "hunt" / RUN_ID)
    units = {u["id"]: u["state"] for u in dead["stages"][0]["units"]}
    assert units == {"chunk_000": "done", "chunk_001": "running", "chunk_002": "pending"} and dead["stages"][0]["state"] == "running"
    assert (env / "hunt" / ".lock" / "pid").exists()                     # nobody was left to release it
    assert db.connect().execute("SELECT COUNT(*) FROM jobs WHERE match_verdict IS NOT NULL").fetchone()[0] == 0
    monkeypatch.setattr(triage_mod, "export", lambda *a, **k: pytest.fail("a resume must never export again"))
    rc, lines, fake, st = _resume(env)
    assert rc == 0, lines
    assert lines[0].startswith(f"run {RUN_ID} resumed: triage on fake")
    assert "closed what the earlier run left running: triage/chunk_001, triage" in lines
    assert "triage chunk_000 running attempt 1" not in lines and len(fake.calls) == 2       # chunk_001 and chunk_002 only
    stage = st["stages"][0]
    assert stage["state"] == "done" and stage["note"] is None and st["ended"] is not None
    got = {u["id"]: (u["state"], u["attempts"]) for u in stage["units"]}
    assert got == {"chunk_000": ("done", 1), "chunk_001": ("done", 2), "chunk_002": ("done", 1)}
    assert stage["summary"]["kept"] + stage["summary"]["dropped"] == 25 and stage["summary"]["failed_units"] == 0
    assert db.connect().execute("SELECT COUNT(*) FROM jobs WHERE match_verdict IS NOT NULL").fetchone()[0] == 25
    assert not (env / "hunt" / ".lock").exists()
    led = ledger.Ledger.open(env / "hunt" / RUN_ID)
    assert ledger.Ledger.replay(led.events(), led.stage_names()) == led.skeleton()          # the resume replays too
    rc, lines, _fake, _st = _resume(env, RUN_ID)
    assert rc == 0 and lines == [f"run {RUN_ID} has nothing left to resume: every stage is done or skipped"]


def test_outputs_on_disk_are_verified_again_not_redone(env):
    _killed_run(env)
    tdir = env / "data" / "triage"
    rows = json.loads((tdir / "chunk_001.json").read_text())             # the killed unit had in fact finished its file
    (tdir / "out_001.json").write_text(json.dumps([{"id": r["id"], "keep": True, "reason": "ok", "bucket": 1} for r in rows]))
    (tdir / "out_000.json").write_text("[]")                              # and a done unit's file was damaged since
    rc, lines, fake, st = _resume(env)
    assert rc == 0, lines
    assert "triage chunk_001 done (output on disk verified, not run again)" in lines
    assert any(line.startswith("triage chunk_000 was done but its output no longer verifies (short file: 0 of 10 ids") for line in lines)
    ran = sorted(i.prompt.split("`")[1] for i in fake.calls)
    assert ran == ["data/triage/chunk_000.json", "data/triage/chunk_002.json"]
    got = {u["id"]: (u["state"], u["attempts"]) for u in st["stages"][0]["units"]}
    assert got == {"chunk_000": ("done", 2), "chunk_001": ("done", 1), "chunk_002": ("done", 1)}


def test_a_chunk_list_that_changed_is_reported_not_replanned(env):
    _killed_run(env)
    (env / "data" / "triage" / "chunk_002.json").unlink()
    (env / "data" / "triage" / "chunk_001.json").write_text("[]")
    rc, lines, fake, st = _resume(env)
    assert rc == 2 and fake.calls == []
    note = st["stages"][0]["note"]
    assert note.startswith("data/triage changed since this run exported it (missing chunk_002; resized chunk_001)")
    assert "Start a new run" in note


def test_ctrl_c_kills_the_units_and_leaves_a_run_that_resumes(env):
    (env / "fake_agent.json").write_text(json.dumps({"chunk_000": {"hang": 60}}))
    fake = FakeAgentHarness(env)
    lines: list[str] = []
    def interrupt_when_running() -> None:
        while not any(line == "triage chunk_000 running attempt 1" for line in lines):
            time.sleep(0.02)
        time.sleep(0.3)
        os.kill(os.getpid(), signal.SIGINT)               # a real signal: it wakes the main thread out of its wait
    threading.Thread(target=interrupt_when_running, daemon=True).start()
    started = time.monotonic()
    rc = run_mod.run(hc.parse(CFG), ["triage"], "fake", cwd=env, run_id=RUN_ID, emit=lines.append,
                     get_harness=lambda name: fake)
    assert rc == 2 and time.monotonic() - started < 20, lines             # the hanging agent was killed, not waited for
    assert lines[-1] == f"run {RUN_ID} interrupted (triage); `python -m src.hunt run --resume {RUN_ID}` continues it"
    st = ledger.load_state(env / "hunt" / RUN_ID)["stages"][0]
    got = {u["id"]: (u["state"], u["verdict"]) for u in st["units"]}
    assert got["chunk_000"] == ("failed", "interrupted") and got["chunk_002"] == ("pending", None)
    assert st["state"] == "failed" and not (env / "hunt" / ".lock").exists()
    rc, lines, _fake, state = _resume(env)
    assert rc == 0 and state["stages"][0]["state"] == "done", lines


def test_the_lock_of_a_live_run_holds_and_the_cli_refuses_a_resume_with_selectors(env, capsys):
    lock = env / "hunt" / ".lock"
    lock.mkdir(parents=True)
    (lock / "pid").write_text("1")                                        # pid 1 is always alive
    assert run_mod.run(hc.parse(CFG), ["triage"], "fake", emit=lambda s: None) == 2
    (lock / "pid").write_text("not a pid")
    lines: list[str] = []
    assert run_mod.run(hc.parse(CFG), ["triage"], "fake", emit=lines.append) == 2 and "no pid recorded" in lines[0]
    (lock / "pid").unlink()
    lock.rmdir()
    assert cli.main(["run", "--resume", "latest", "--only", "triage"]) == 2
    assert "--resume continues the stages of that run" in capsys.readouterr().err
    assert cli.main(["run", "--resume", "latest"]) == 2 and "no run to resume (latest)" in capsys.readouterr().out
