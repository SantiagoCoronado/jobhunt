"""`hunt run --ids`: rows a human chose stand in for the pick stage. Order, each refusal, resume."""
from __future__ import annotations

import json

import pytest
from hunt_fakes import FakeAgentHarness

from src import db
from src import pick as pick_mod
from src import research as research_mod
from src.hunt import cli, ledger
from src.hunt import config as hc
from src.hunt import run as run_mod


@pytest.fixture
def env(tmp_path, monkeypatch):
    real_connect = db.connect
    temp_connect = lambda *a, **k: real_connect(tmp_path / "jobs.db")  # noqa: E731
    monkeypatch.setattr(db, "connect", temp_connect)
    monkeypatch.setattr(pick_mod, "connect", temp_connect)
    monkeypatch.setattr(research_mod, "COMPANIES_DIR", tmp_path / "research" / "companies")
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path / "hunt")
    monkeypatch.setattr(run_mod, "validate_models", lambda cfg, stages, harness: [])
    conn = db.connect()
    rows = (("Acme", "shortlisted", 95), ("Beta Labs", "shortlisted", 60), ("Gamma", "applied", 90),
            ("Acme", "shortlisted", None), ("Example Robotics", "shortlisted", 80))
    for i, (company, status, score) in enumerate(rows, 1):
        conn.execute("INSERT INTO jobs (source, external_id, canonical_key, url, company, title, location, status, "
                     "match_score, match_verdict, first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                     ("greenhouse", f"e{i}", f"k{i}", "https://x", company, f"Engineer {i}",
                      "Berlin, Germany" if company == "Example Robotics" else "Remote", status, score,
                      json.dumps({"recommendation": "apply", "location_ok": True}), "2026-09-01", "2026-09-18"))
    conn.commit()
    return tmp_path


def test_parse_ids_keeps_the_order_and_drops_a_repeat():
    assert cli.parse_ids("3625, 9118,3625") == [3625, 9118]
    for bad in ("", " , ", "12,abc", "-4", "3\u00b2", "\u0663"):          # a superscript two and an Arabic-Indic three are digits to str.isdigit
        with pytest.raises(ValueError, match="--ids takes job ids"):
            cli.parse_ids(bad)


def test_a_range_that_does_not_read_picks_is_refused():
    for ok in (["tailor"], ["research"], ["research", "tailor"], ["research", "tailor", "report"]):
        cli.check_ids_range(ok)
    with pytest.raises(ValueError, match="replaces the pick stage, so pick cannot run"):
        cli.check_ids_range(["pick", "research", "tailor"])
    with pytest.raises(ValueError, match="discover, triage"):
        cli.check_ids_range(["discover", "triage"])
    with pytest.raises(ValueError, match="needs a stage that works on picks"):
        cli.check_ids_range(["report"])


def test_chosen_takes_what_the_star_rule_would_not_in_the_order_given(env):
    """Two rows of one company, an unscored one and a low score: the human chose, so all stand."""
    picks, refused = pick_mod.chosen([4, 2, 1])
    assert refused == [] and [p["id"] for p in picks] == [4, 2, 1]
    assert picks[0] == {"id": 4, "company": "Acme", "title": "Engineer 4", "location": "Remote", "match": None,
                        "dream": False, "recommendation": "apply", "location_ok": True, "visa_path": None}
    star, _skipped, _spares = pick_mod.pick()
    assert set(picks[0]) == set(star[0])                       # the shape the pick stage writes


def test_chosen_refuses_by_name(env, monkeypatch):
    monkeypatch.setattr(pick_mod, "is_dream", lambda company: company == "Example Robotics")
    monkeypatch.setattr(pick_mod, "outside_relocation_regions", lambda location, scope: "Germany" in (location or ""))
    picks, refused = pick_mod.chosen([1, 99, 3, 5])
    assert [p["id"] for p in picks] == [1]
    assert refused == ["#99 is not a row in the jobs table", "#3 Gamma is applied, not shortlisted",
                       "#5 Example Robotics is a dream row outside the relocation regions "
                       "(work_authorization.relocation_regions)"]


def test_the_cli_refuses_before_anything_runs(env, monkeypatch, capsys):
    started: list[object] = []
    monkeypatch.setattr(run_mod, "run", lambda *a, **k: started.append(k) or 0)
    for argv, why in (
        (["run", "--only", "tailor", "--ids", "1,99"], "--ids: #99 is not a row"),
        (["run", "--only", "tailor", "--ids", "3"], "--ids: #3 Gamma is applied, not shortlisted"),
        (["run", "--from", "pick", "--ids", "1"], "--ids replaces the pick stage"),
        (["run", "--only", "match", "--ids", "1"], "match cannot run with it"),
        (["run", "--only", "tailor", "--ids", "one"], "--ids takes job ids"),
        (["run", "--resume", "latest", "--ids", "1"], "--resume continues the stages of that run (and keeps its picks)"),
    ):
        assert cli.main(argv) == 2
        assert why in capsys.readouterr().err, argv
    assert started == [] and not (env / "hunt").exists()

    assert cli.main(["run", "--from", "research", "--to", "tailor", "--ids", "2,1"]) == 0
    assert [p["id"] for p in started[0]["picks"]] == [2, 1]
    assert cli.main(["run", "--only", "tailor"]) == 0 and started[1]["picks"] is None     # no --ids: as before


def _run(env, run_id=None, plan=None, **kw):
    (env / "fake_agent.json").write_text(json.dumps(plan or {}))
    fake = FakeAgentHarness(env)
    lines: list[str] = []
    rc = run_mod.run(hc.defaults(), ["research"], "fake", cwd=env, run_id=run_id, emit=lines.append,
                     get_harness=lambda name: fake, pool_options={"sleep": lambda s: None}, **kw)
    return rc, lines


def test_a_run_with_ids_writes_picks_json_and_skips_the_pick_stage(env):
    picks, _ = pick_mod.chosen([2, 1])
    rc, lines = _run(env, "20260920-1000", picks=picks)
    assert rc == 0, lines
    run_dir = env / "hunt" / "20260920-1000"
    doc = json.loads((run_dir / "picks.json").read_text())
    assert [p["id"] for p in doc["picks"]] == [2, 1] and doc["source"] == "ids"
    assert set(doc) == {"picks", "flagged", "skipped", "spares", "source"}
    assert "picks from --ids: #2, #1" in lines
    state = ledger.load_state(run_dir)
    assert [s["name"] for s in state["stages"]] == ["research"]              # no pick stage in the run
    assert [u["id"] for u in state["stages"][0]["units"]] == ["beta-labs", "acme"]


def test_a_resume_keeps_the_picks_of_the_run(env):
    picks, _ = pick_mod.chosen([2, 1])
    rc, lines = _run(env, "20260920-1100", plan={"acme": {"no_sources": 9}}, picks=picks)
    assert rc == 2, lines
    before = (env / "hunt" / "20260920-1100" / "picks.json").read_text()
    rc, lines = _run(env, resume="20260920-1100")
    assert rc == 0, lines
    assert (env / "hunt" / "20260920-1100" / "picks.json").read_text() == before
    units = {u["id"]: u["state"] for u in ledger.load_state(env / "hunt" / "20260920-1100")["stages"][0]["units"]}
    assert units == {"beta-labs": "done", "acme": "done"}


def test_a_dry_run_with_ids_names_the_picks_it_resolved(env, capsys):
    assert cli.main(["run", "--dry-run", "--from", "research", "--to", "tailor", "--ids", "2,1"]) == 0
    out = capsys.readouterr().out
    assert "  picks from --ids (2): #2 Beta Labs, #1 Acme" in out
    assert "one per pick above" in out and "picks from pick" not in out
    assert not (env / "hunt").exists()                                       # nothing ran
    assert cli.main(["run", "--dry-run", "--only", "tailor", "--ids", "99"]) == 2   # and it still refuses by name
    assert "--ids: #99 is not a row" in capsys.readouterr().err
    assert cli.main(["run", "--dry-run", "--only", "tailor"]) == 0           # without --ids: as before
    assert "picks from pick" in capsys.readouterr().out
