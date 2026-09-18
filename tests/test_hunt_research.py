"""The research stage: staleness decides the units, the dossier verify (today's researched
line, a Sources section, zero em-dashes), and web-capability routing to another harness."""
from __future__ import annotations

import json
from datetime import date

import pytest
from hunt_fakes import FakeAgentHarness

from src import db
from src import pick as pick_mod
from src import research as research_mod
from src.hunt import config as hc
from src.hunt import ledger
from src.hunt import run as run_mod
from src.hunt.stages import research as stage

TODAY = date.today().isoformat()


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
    for i, company in enumerate(("Acme", "Beta Labs", "Gamma"), 1):
        conn.execute("INSERT INTO jobs (source, external_id, canonical_key, url, company, title, location, status, "
                     "match_score, match_verdict, first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                     ("greenhouse", f"e{i}", f"k{i}", "https://x", company, "Backend Engineer", "Remote", "shortlisted",
                      95 - i, json.dumps({"recommendation": "apply", "location_ok": True}), "2026-09-01", "2026-09-18"))
    conn.commit()
    return tmp_path


def _dossier(env, slug: str, researched: str) -> None:
    d = env / "research" / "companies"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{slug}.md").write_text(f"# {slug}\n\n## Sources\n- https://example.com\n- researched: {researched}\n")


def _run(env, run_id, plan=None, get_harness=None):
    (env / "fake_agent.json").write_text(json.dumps(plan or {}))
    fake = FakeAgentHarness(env)
    lines: list[str] = []
    rc = run_mod.run(hc.defaults(), ["pick", "research"], "fake", cwd=env, run_id=run_id, emit=lines.append,
                     get_harness=get_harness or (lambda name: fake), pool_options={"sleep": lambda s: None})
    return rc, lines, fake, ledger.load_state(env / "hunt" / run_id)["stages"][1]


def test_only_missing_and_stale_dossiers_are_researched_and_a_bad_one_runs_again(env):
    _dossier(env, "acme", TODAY)                      # fresh: no unit
    _dossier(env, "gamma", "2026-01-01")              # stale: refreshed
    rc, lines, fake, st = _run(env, "20260918-2300", plan={"beta-labs": {"no_sources": 1}})
    assert rc == 0, lines
    units = {u["id"]: u for u in st["units"]}
    assert sorted(units) == ["beta-labs", "gamma"] and units["beta-labs"]["attempts"] == 2 and units["gamma"]["attempts"] == 1
    assert units["gamma"]["output"] == "research/companies/gamma.md" and units["gamma"]["input"] == "job #3"
    assert "research beta-labs failed: beta-labs.md has no Sources section" in lines
    summ = st["summary"]
    assert (summ["picks"], summ["fresh"], summ["units"], summ["written"], summ["failed_units"]) == (3, 1, 2, 2, 0)
    assert f"researched: {TODAY}" in (env / "research" / "companies" / "gamma.md").read_text()
    inv = next(i for i in fake.calls if "research Gamma" in i.prompt)
    assert inv.tools == frozenset({"read", "write", "bash", "web"}) and inv.timeout_s == 900
    assert "refresh the stale dossier at `research/companies/gamma.md`" in inv.prompt and f"Today is {TODAY}." in inv.prompt
    assert "`python -m src.query job 3` prints its description" in inv.prompt
    assert any("write the dossier at `research/companies/beta-labs.md`" in i.prompt for i in fake.calls)


def test_every_dossier_fresh_skips_the_stage_and_no_picks_file_fails_it(env):
    for slug in ("acme", "beta-labs", "gamma"):
        _dossier(env, slug, TODAY)
    rc, _lines, fake, st = _run(env, "20260918-2301")
    assert rc == 0 and st["state"] == "skipped" and st["note"] == "every pick has a fresh dossier" and fake.calls == []
    lines: list[str] = []
    rc = run_mod.run(hc.defaults(), ["research"], "fake", cwd=env, run_id="20260918-2302", emit=lines.append,
                     get_harness=lambda name: fake)
    assert rc == 2 and any("no picks.json in this run" in line for line in lines)


def test_a_harness_without_web_hands_research_to_one_that_grants_it(env):
    blind = FakeAgentHarness(env, capabilities=frozenset({"read", "write", "bash"}))
    webbed = FakeAgentHarness(env, name="claude")
    cfg_harnesses = {"fake": blind, "claude": webbed}

    def get(name):
        if name not in cfg_harnesses:
            raise ValueError(f"unknown harness '{name}'")
        return cfg_harnesses[name]
    rc, lines, _fake, st = _run(env, "20260918-2303", get_harness=get)
    assert rc == 0, lines
    assert "research: fake does not grant web, running on claude with its default model" in lines
    assert blind.calls == [] and len(webbed.calls) == 3
    assert all(u["harness"] == "claude" and u["model"] is None for u in st["units"]) and st["summary"]["harness"] == "claude"
    cfg_harnesses.pop("claude")
    rc, lines, _fake, st = _run(env, "20260918-2304", get_harness=get)
    assert rc == 0 and st["state"] == "skipped"                     # all three were just written
    (env / "research" / "companies" / "acme.md").unlink()
    rc, lines, _fake, st = _run(env, "20260918-2305", get_harness=get)
    assert rc == 2 and st["note"].startswith("no configured harness grants web, which research needs")


def test_verify_dossier_names_what_is_wrong(tmp_path):
    p = tmp_path / "acme.md"
    assert stage.verify_dossier(p, TODAY) == "no dossier at acme.md"
    for text, why in (("# Acme\n## Sources\n", "has no `researched: YYYY-MM-DD` line"),
                      (f"# Acme\n- researched: {TODAY}\n", "has no Sources section"),
                      ("# Acme\n## Sources\nresearched: 2026-01-01\n", "not today"),
                      (f"# Acme \u2014 x\n## 9. Sources\nresearched: {TODAY}\n", "1 em-dash(es)")):
        p.write_text(text)
        assert why in stage.verify_dossier(p, TODAY)
    p.write_text(f"# Acme\n## 10. Sources\n- researched: {TODAY}\n")
    assert stage.verify_dossier(p, TODAY) is None
