"""The match stage on a temp DB and a fake agent process: export under the unit budget, verify,
ingest, the second pass after the first is ingested, dream rows on their own line, a chunk that
never passes."""
from __future__ import annotations

import json

import pytest
from hunt_fakes import FakeAgentHarness

from src import db
from src import match as match_mod
from src.hunt import config as hc
from src.hunt import ledger
from src.hunt import run as run_mod
from src.hunt.stages import match as stage


@pytest.fixture
def env(tmp_path, monkeypatch):
    real_connect = db.connect
    temp_connect = lambda *a, **k: real_connect(tmp_path / "jobs.db")  # noqa: E731
    monkeypatch.setattr(db, "connect", temp_connect)
    monkeypatch.setattr(match_mod, "connect", temp_connect)           # bound at import
    monkeypatch.setattr(match_mod, "MATCH_DIR", tmp_path / "data" / "match")
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path / "hunt")
    monkeypatch.setattr(run_mod, "validate_models", lambda cfg, stages, harness: [])
    return tmp_path


def _keepers(buckets: list[int], dream_at: int | None = None) -> None:
    conn = db.connect()
    for i, b in enumerate(buckets, 1):
        company = "Example Robotics" if i == dream_at else f"Co{i}"
        conn.execute("INSERT INTO jobs (source, external_id, canonical_key, url, company, title, location, description, "
                     "status, match_verdict, first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                     ("greenhouse", f"e{i}", f"k{i:03d}", "https://x", company, "Software Engineer", "Remote",
                      "Build things.", "discovered", json.dumps({"triage": "keep", "bucket": b}), "2026-09-01", "2026-09-18"))
    conn.commit()


def _cfg(**over):
    return hc.parse({"stages": {"match": {"chunk": 4, "budget_units": 3, "retries": 1, **over}}})


def _run(env, run_id, cfg, plan=None):
    (env / "fake_agent.json").write_text(json.dumps(plan or {}))
    fake = FakeAgentHarness(env)
    lines: list[str] = []
    rc = run_mod.run(cfg, ["match"], "fake", cwd=env, run_id=run_id, emit=lines.append,
                     get_harness=lambda name: fake, pool_options={"sleep": lambda s: None})
    return rc, lines, fake, ledger.load_state(env / "hunt" / run_id)["stages"][0]


def test_two_passes_each_ingested_before_the_next_export_and_dream_rows_on_their_own_line(env):
    _keepers([3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 1], dream_at=5)       # 6 strong, 6 good, 1 plausible
    rc, lines, fake, st = _run(env, "20260918-2100", _cfg())
    assert rc == 0, lines
    assert [u["id"] for u in st["units"]] == ["p1_chunk_000", "p1_chunk_001", "p2_chunk_000"]   # budget 3: 2 + 1
    assert all(u["state"] == "done" for u in st["units"])
    summ = st["summary"]
    assert (summ["units"], summ["pass1_units"], summ["pass2_units"], summ["scored"], summ["failed_units"]) == (3, 2, 1, 10, 0)
    conn = db.connect()
    scored = {r["id"]: (r["match_score"], r["status"]) for r in conn.execute("SELECT * FROM jobs WHERE match_score IS NOT NULL")}
    assert set(scored) == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}                # pass 1 survived pass 2's export wipe
    assert scored[2] == (90, "shortlisted") and scored[1] == (65, "discovered")
    assert scored[5] == (65, "shortlisted")                              # the dream cutoff is 60
    assert summ["shortlisted"] == 6 and (summ["dream_scored"], summ["dream_shortlisted"]) == (1, 1)
    assert "match dream: 1 scored, 1 shortlisted: #5 Example Robotics 65 shortlisted" in lines
    assert summ["chunk_rows"] == {"p1_chunk_000": 4, "p1_chunk_001": 2, "p2_chunk_000": 4}
    verdict = json.loads(conn.execute("SELECT match_verdict FROM jobs WHERE id=2").fetchone()[0])
    assert verdict["reasons"] == "fake, verdict"                         # the em-dash never reaches the DB
    run_dir = env / "hunt" / "20260918-2100"
    prompt = (run_dir / "prompts" / "match" / "p1_chunk_000.md").read_text()
    assert "Task: score the 4 jobs in `data/match/chunk_000.json` against `config/profile.yaml` and write `data/match/scores_000.json`." in prompt
    assert "Do not run `src.match ingest`" in prompt and fake.calls[0].tools == frozenset({"read", "write"})
    assert "Ingested 6 scores" in (run_dir / "logs" / "match" / "ingest_p1.log").read_text()
    assert "\u2014" not in "\n".join(lines)


def test_no_second_pass_when_disabled_or_when_the_budget_is_spent(env):
    _keepers([3] * 9 + [2] * 4)
    rc, _lines, _fake, st = _run(env, "20260918-2101", _cfg())
    assert rc == 0 and [u["id"] for u in st["units"]] == ["p1_chunk_000", "p1_chunk_001", "p1_chunk_002"]
    assert st["summary"]["scored"] == 9 and st["summary"]["pass2_units"] == 0
    rc, _lines, _fake, st = _run(env, "20260918-2102", _cfg(second_pass_min_bucket=0, budget_units=1))
    assert rc == 0 and st["summary"]["scored"] == 0 and st["state"] == "skipped" and st["note"] == "nothing to score"


def test_a_failed_chunk_is_moved_aside_the_rest_ingested_and_pass_2_not_planned(env):
    _keepers([3, 3, 3, 3, 3, 3, 2, 2])
    rc, _lines, _fake, st = _run(env, "20260918-2103", _cfg(), plan={"chunk_001": {"bad_score": 9}})
    assert rc == 2 and st["state"] == "failed" and "score must be an integer 0..100, got 'high'" in st["note"]
    assert [(u["id"], u["state"], u["attempts"]) for u in st["units"]] == [("p1_chunk_000", "done", 1), ("p1_chunk_001", "failed", 2)]
    mdir = env / "data" / "match"
    assert (mdir / "scores_001.json.failed").exists() and (mdir / "chunk_001.json").exists()
    assert db.connect().execute("SELECT COUNT(*) FROM jobs WHERE match_score IS NOT NULL").fetchone()[0] == 4
    assert st["summary"]["failed_units"] == 1 and st["summary"]["scored"] == 4


def test_verify_scores_names_what_is_wrong(tmp_path):
    chunk, out = tmp_path / "chunk_000.json", tmp_path / "scores_000.json"
    chunk.write_text(json.dumps([{"id": 1}, {"id": 2}]))
    assert stage.verify_scores(chunk, out) == "no output file scores_000.json"
    ok = {"score": 70, "reasons": "fine"}
    for data, why in (([{"id": 1, **ok}], "short file: 1 of 2 ids scored, missing 2"),
                      ([{"id": 1, **ok}, {"id": 2, **ok, "score": 101}], "id 2: score must be an integer 0..100, got 101"),
                      ([{"id": 1, **ok}, {"id": 2, "score": 50}], "id 2: reasons must be a string"),
                      ([{"id": 1, **ok}, {"id": 2, **ok}, {"id": 2, **ok}], "appears twice")):
        out.write_text(json.dumps(data))
        assert why in stage.verify_scores(chunk, out)
    out.write_text(json.dumps([{"id": 1, **ok}, {"id": 2, **ok}]))
    assert stage.verify_scores(chunk, out) is None
