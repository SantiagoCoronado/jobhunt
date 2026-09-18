"""The tailor stage on the tailor_build fixtures: bundle per pick, the build as verify, the one
fix round with the verdict in the prompt, build metrics in the ledger, a unit that wrote nothing."""
from __future__ import annotations

import json

import pytest
import yaml
from hunt_fakes import FakeAgentHarness
from test_tailor_build import RESUME, letter, small_resume

from src import tailor_build as tb
from src.hunt import config as hc
from src.hunt import ledger
from src.hunt import run as run_mod
from src.hunt.stages import tailor as stage


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path / "hunt")
    monkeypatch.setattr(run_mod, "validate_models", lambda cfg, stages, harness: [])
    monkeypatch.setattr(tb.rd, "audit_line_fill", lambda data, level: [])          # as test_tailor_build.clean_audit
    real_estimate = tb.rd.estimate_height_pts
    monkeypatch.setattr(tb.rd, "estimate_height_pts",
                        lambda data, level: max(real_estimate(data, level), tb.rd.PAGE_AVAIL_PTS * 0.97))
    monkeypatch.setattr(stage, "build", lambda folder: tb.build(
        folder, job={"id": int(folder.name.rsplit("-", 1)[1]), "company": "Acme", "dream": False}, no_pdf=True).to_dict())

    def fake_bundle(job_id, company, log):
        inputs = tmp_path / "data" / "tailor" / str(job_id) / "inputs.md"
        inputs.parent.mkdir(parents=True, exist_ok=True)
        inputs.write_text("bundle")
        folder = tmp_path / "applications" / "pending" / f"{company.lower()}-{job_id}"
        folder.mkdir(parents=True, exist_ok=True)
        return inputs, folder
    monkeypatch.setattr(stage, "bundle", fake_bundle)
    monkeypatch.setattr(stage.tailor_bundle, "application_folder",
                        lambda job_id, company: tmp_path / "applications" / "pending" / f"{company.lower()}-{job_id}")
    for variant, text in (("good", letter()), ("bad", letter(extra="A dash \u2014 here."))):
        d = tmp_path / "fake_out" / variant
        d.mkdir(parents=True)
        (d / RESUME).write_text(yaml.safe_dump(small_resume(), allow_unicode=True, sort_keys=False))
        (d / "CoverLetter.md").write_text(text)
        (d / "match_report.md").write_text("# Match report\n\nGaps: none.\n")
        (d / "answers.md").write_text("## Why Acme?\nBecause of the product.\n")
    return tmp_path


def _run(env, run_id, picks, plan=None, cfg=None):
    (env / "fake_agent.json").write_text(json.dumps(plan or {}))
    fake = FakeAgentHarness(env)
    lines: list[str] = []
    led_dir = env / "hunt"

    def seed_picks(ctx):
        from src.hunt.stages import StageResult
        (ctx.run_dir / "picks.json").write_text(json.dumps({"picks": picks}))
        return StageResult({"picks": len(picks)})
    from src.hunt.stages import REGISTRY
    REGISTRY["pick"] = REGISTRY["pick"].__class__("pick", "python", run=seed_picks)
    rc = run_mod.run(cfg or hc.defaults(), ["pick", "tailor"], "fake", cwd=env, hunt_dir=led_dir, run_id=run_id,
                     emit=lines.append, get_harness=lambda name: fake, pool_options={"sleep": lambda s: None})
    return rc, lines, fake, ledger.load_state(led_dir / run_id)["stages"][1]


@pytest.fixture(autouse=True)
def _restore_registry():
    from src.hunt.stages import REGISTRY
    saved = REGISTRY["pick"]
    yield
    REGISTRY["pick"] = saved


PICKS = [{"id": 7, "company": "Acme", "title": "Senior Engineer"}, {"id": 8, "company": "Acme", "title": "Staff Engineer"}]


def test_a_failed_build_gets_one_fix_round_with_the_verdict_in_the_prompt(env):
    rc, lines, fake, st = _run(env, "20260919-0900", PICKS, plan={"job_8": {"bad": 1}})
    assert rc == 0, lines
    units = {u["id"]: u for u in st["units"]}
    assert units["job_7"]["attempts"] == 1 and units["job_8"]["attempts"] == 2 and all(u["state"] == "done" for u in units.values())
    assert units["job_7"]["input"] == "data/tailor/7/inputs.md" and units["job_7"]["output"] == "applications/pending/acme-7"
    assert any(line.startswith("tailor job_8 failed: build FAIL: ") and "em-dash" in line for line in lines)
    first, fix = [i.prompt for i in fake.calls if "job #8" in i.prompt]
    assert "FIX ROUND" not in first and "write `applications/pending/acme-8/draft.md`" in first
    assert "FIX ROUND. Your draft is already split into files in `applications/pending/acme-8` and the build failed:" in fix
    assert "EMDASH  1" in fix and "Do not write a new draft.md" in fix
    run_dir = env / "hunt" / "20260919-0900"
    assert "FIX ROUND" in (run_dir / "prompts" / "tailor" / "job_8.retry.md").read_text()
    assert not (run_dir / "prompts" / "tailor" / "job_7.retry.md").exists()
    builds = st["summary"]["builds"]
    assert builds["job_7"]["ok"] and builds["job_7"]["letter_words"] == 250 and builds["job_7"]["fit_level"] in (0, 1, 2, 3)
    assert builds["job_7"]["fill_pct"] >= 90 and any(ln.startswith("RESUME") for ln in builds["job_7"]["lines"])
    assert (st["summary"]["picks"], st["summary"]["passed"], st["summary"]["failed_units"]) == (2, 2, 0)
    assert fake.calls[0].tools == frozenset({"read", "write", "edit", "bash"}) and fake.calls[0].timeout_s == 900


def test_a_second_failure_is_reported_not_retried_and_nothing_written_never_passes(env):
    folder = env / "applications" / "pending" / "acme-7"
    folder.mkdir(parents=True)
    for p in (env / "fake_out" / "good").iterdir():                      # an older, passing application
        (folder / p.name).write_text(p.read_text())
    rc, lines, _fake, st = _run(env, "20260919-0901", PICKS, plan={"job_7": {"nothing": 9}, "job_8": {"bad": 9}})
    assert rc == 2 and st["state"] == "failed" and st["note"].startswith("2 of 2 tailor unit(s) failed")
    units = {u["id"]: u for u in st["units"]}
    assert units["job_7"]["verdict"] == "the unit wrote nothing in acme-7" and units["job_8"]["attempts"] == 2
    assert units["job_8"]["verdict"].startswith("build FAIL: ")
    needs = st["summary"]["needs_human"]
    assert any(n.startswith("tailor: job_8 did not pass its build after the fix round: ") for n in needs)
    assert st["summary"]["builds"]["job_8"]["ok"] is False and st["summary"]["passed"] == 0


def test_no_picks_skips_and_a_missing_picks_file_fails(env):
    rc, _lines, fake, st = _run(env, "20260919-0902", [])
    assert rc == 0 and st["state"] == "skipped" and st["note"] == "no picks" and fake.calls == []
    lines: list[str] = []
    rc = run_mod.run(hc.defaults(), ["tailor"], "fake", cwd=env, hunt_dir=env / "hunt", run_id="20260919-0903",
                     emit=lines.append, get_harness=lambda name: fake)
    assert rc == 2 and any("no picks.json in this run" in line for line in lines)
