"""The triage stage on a temp DB and a fake agent process: export into chunks, one unit per
chunk, coverage verify with a short file run again, ingest, the summary, the skip under
min_pile, and a chunk that never passes (moved aside, the rest ingested, the stage failed)."""
from __future__ import annotations

import json

import pytest
from hunt_fakes import FakeAgentHarness

from src import db
from src import triage as triage_mod
from src.hunt import config as hc
from src.hunt import ledger
from src.hunt import run as run_mod
from src.hunt.stages import triage as stage


@pytest.fixture
def env(tmp_path, monkeypatch):
    real_connect = db.connect
    temp_connect = lambda *a, **k: real_connect(tmp_path / "jobs.db")  # noqa: E731
    monkeypatch.setattr(db, "connect", temp_connect)
    monkeypatch.setattr(triage_mod, "connect", temp_connect)          # bound at import, like discover and pick
    monkeypatch.setattr(triage_mod, "TRIAGE_DIR", tmp_path / "data" / "triage")
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path / "hunt")
    monkeypatch.setattr(run_mod, "validate_models", lambda cfg, stages, harness: [])
    return tmp_path


def _discovered(n: int) -> None:
    conn = db.connect()
    for i in range(1, n + 1):
        conn.execute("INSERT INTO jobs (source, external_id, canonical_key, url, company, title, location, description, "
                     "status, first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                     ("greenhouse", f"e{i}", f"k{i:03d}", "https://x", f"Co{i}", "Software Engineer", "Remote",
                      "Build things.", "discovered", "2026-09-01", "2026-09-18"))
    conn.commit()


def _run(env, run_id, cfg=None, plan=None):
    (env / "fake_agent.json").write_text(json.dumps(plan or {}))
    fake = FakeAgentHarness(env)
    lines: list[str] = []
    cfg = cfg or hc.parse({"stages": {"triage": {"chunk": 10, "min_pile": 5, "retries": 1}}})
    rc = run_mod.run(cfg, ["triage"], "fake", cwd=env, run_id=run_id, emit=lines.append,
                     get_harness=lambda name: fake, pool_options={"sleep": lambda s: None})
    return rc, lines, fake, ledger.load_state(env / "hunt" / run_id)["stages"][0]


def test_a_short_file_is_run_again_then_everything_is_ingested(env):
    _discovered(25)
    rc, lines, fake, st = _run(env, "20260918-2000", plan={"chunk_001": {"short": 1}})
    assert rc == 0, lines
    units = {u["id"]: u for u in st["units"]}
    assert sorted(units) == ["chunk_000", "chunk_001", "chunk_002"]
    assert units["chunk_001"]["attempts"] == 2 and units["chunk_000"]["attempts"] == 1
    assert all(u["state"] == "done" and u["harness"] == "fake" and u["model"] is None for u in units.values())
    assert units["chunk_000"]["input"] == "data/triage/chunk_000.json" and units["chunk_000"]["output"] == "data/triage/out_000.json"
    assert any(line.startswith("triage chunk_001 failed: short file: 9 of 10 ids, missing ") for line in lines)
    ids = [r["id"] for r in db.connect().execute("SELECT id FROM jobs ORDER BY id")]
    kept = [i for i in ids if i % 3]
    summ = st["summary"]
    assert (summ["units"], summ["rows"], summ["kept"], summ["dropped"], summ["failed_units"]) == (3, 25, len(kept), 25 - len(kept), 0)
    assert summ["b3"] + summ["b2"] + summ["b1"] + summ["b0"] == summ["kept"] and summ["chunk_rows"]["chunk_002"] == 5
    assert f"triage done  units=3 rows=25 failed_units=0 kept={len(kept)} dropped={25 - len(kept)}" in " ".join(lines)
    conn = db.connect()
    assert conn.execute("SELECT COUNT(*) FROM jobs WHERE status='irrelevant'").fetchone()[0] == 25 - len(kept)
    assert conn.execute("SELECT COUNT(*) FROM jobs WHERE status='discovered' AND match_verdict LIKE '%\"keep\"%'").fetchone()[0] == len(kept)
    run_dir = env / "hunt" / "20260918-2000"
    prompt = (run_dir / "prompts" / "triage" / "chunk_001.md").read_text()
    assert prompt.startswith("You are a triage screener") and "Candidate: " in prompt
    assert "Task: triage the 10 jobs in `data/triage/chunk_001.json` and write `data/triage/out_001.json`." in prompt
    assert prompt.rstrip().endswith("Reply with one line. Your reply is not read; the output file is.")
    inv = fake.calls[0]
    assert inv.tools == frozenset({"read", "write"}) and inv.timeout_s == 300 and inv.system.startswith("You are a triage screener")
    assert "Exported 25 jobs" in (run_dir / "logs" / "triage" / "export.log").read_text()
    assert "Triage ingest" in (run_dir / "logs" / "triage" / "ingest.log").read_text()
    assert "\u2014" not in prompt + "\n".join(lines)


def test_under_min_pile_the_stage_is_skipped_and_nothing_is_exported(env):
    _discovered(4)
    rc, lines, fake, st = _run(env, "20260918-2001")
    assert rc == 0 and st["state"] == "skipped" and st["note"] == "pile 4 is under min_pile 5"
    assert "triage skipped (pile 4 is under min_pile 5)" in lines and fake.calls == [] and st["units"] == []
    assert not (env / "data" / "triage").exists()


def test_a_chunk_that_never_passes_is_moved_aside_and_the_rest_is_ingested(env):
    _discovered(20)
    rc, lines, _fake, st = _run(env, "20260918-2002", plan={"chunk_000": {"bad_keep": 9}})
    assert rc == 2 and st["state"] == "failed"
    assert st["note"].startswith("1 of 2 triage unit(s) failed after their retries, first chunk_000: id ")
    assert "keep must be true or false, got 'maybe'" in st["note"] and "--resume" in st["note"]
    units = {u["id"]: u for u in st["units"]}
    assert units["chunk_000"]["state"] == "failed" and units["chunk_000"]["attempts"] == 2 and units["chunk_001"]["state"] == "done"
    tdir = env / "data" / "triage"
    assert (tdir / "out_000.json.failed").exists() and not (tdir / "out_000.json").exists()
    conn = db.connect()
    touched = conn.execute("SELECT COUNT(*) FROM jobs WHERE match_verdict IS NOT NULL").fetchone()[0]
    assert touched == 10 and st["summary"]["failed_units"] == 1 and st["summary"]["kept"] + st["summary"]["dropped"] == 10


def test_verify_out_names_what_is_wrong(tmp_path):
    chunk, out = tmp_path / "chunk_000.json", tmp_path / "out_000.json"
    chunk.write_text(json.dumps([{"id": 1}, {"id": 2}]))
    assert stage.verify_out(chunk, out) == "no output file out_000.json"
    out.write_text("[{")
    assert stage.verify_out(chunk, out).startswith("out_000.json is not valid JSON")
    row = {"keep": True, "reason": "x", "bucket": 2}
    for data, why in (({"a": 1}, "must be a JSON array"), ([{"id": 1, **row}], "short file: 1 of 2 ids, missing 2"),
                      ([{"id": 1, **row}, {"id": 2, **row}, {"id": 7, **row}], "not in chunk_000.json: 7"),
                      ([{"id": 1, **row}, {"id": 2, **row}, {"id": 2, **row}], "appears twice"),
                      ([{"id": 1, **row}, {"id": 2, **row, "bucket": 4}], "id 2: bucket must be 0..3, got 4"),
                      ([{"id": 1, **row}, {"id": 2, **row, "bucket": True}], "bucket must be 0..3")):
        out.write_text(json.dumps(data))
        assert why in stage.verify_out(chunk, out)
    out.write_text(json.dumps([{"id": 1, **row}, {"id": 2, "keep": False, "reason": "off-field"}]))
    assert stage.verify_out(chunk, out) is None                       # a drop may leave the bucket out
