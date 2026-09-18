"""python -m src.hunt: stage selection, `runs` and `status` over an empty folder, `run --dry-run`."""
from __future__ import annotations

import json

import pytest

from src.hunt import cli, ledger
from src.hunt.config import STAGES


@pytest.fixture
def hunt_dir(tmp_path, monkeypatch):
    d = tmp_path / "hunt"
    monkeypatch.setattr(ledger, "HUNT_DIR", d)
    return d


def test_select_stages_semantics():
    assert cli.select_stages() == list(STAGES)
    assert cli.select_stages(from_="pick") == ["pick", "research", "tailor", "report"]
    assert cli.select_stages(to="match") == ["discover", "triage", "match"]
    assert cli.select_stages(from_="triage", to="inbox", skip=["match"]) == ["triage", "inbox"]
    assert cli.select_stages(only="discover") == ["discover"]
    assert cli.select_stages(only="discover", skip=["discover"]) == []
    with pytest.raises(ValueError, match="unknown stage 'foo'"):
        cli.select_stages(only="foo")
    with pytest.raises(ValueError, match="comes after"):
        cli.select_stages(from_="tailor", to="triage")
    with pytest.raises(ValueError, match="--only cannot be combined"):
        cli.select_stages(only="pick", to="report")


def test_argparse_rejects_an_unknown_stage(capsys):
    with pytest.raises(SystemExit) as e:
        cli.main(["run", "--only", "triag"])
    assert e.value.code == 2
    assert "invalid choice: 'triag'" in capsys.readouterr().err


def test_runs_and_status_over_an_empty_folder(hunt_dir, capsys):
    assert cli.main(["runs"]) == 0
    assert capsys.readouterr().out.strip() == f"no runs yet under {hunt_dir}"
    assert cli.main(["status"]) == 1
    assert capsys.readouterr().out.strip() == f"no runs yet under {hunt_dir}"
    assert cli.main(["status", "20260101-0000"]) == 1
    assert "no run '20260101-0000'" in capsys.readouterr().out
    hunt_dir.mkdir(parents=True)                                # an empty data/hunt/ is the same
    assert cli.main(["runs"]) == 0 and cli.main(["status", "latest"]) == 1


def test_runs_and_status_over_a_run(hunt_dir, capsys):
    d = hunt_dir / "20260918-1630"
    d.mkdir(parents=True)
    (d / "state.json").write_text(json.dumps({
        "run_id": "20260918-1630", "started": "2026-09-18T16:30", "harness": "claude",
        "stages": [{"name": "discover", "state": "done"}, {"name": "triage", "state": "running"}]}))
    assert cli.main(["runs"]) == 0
    assert "20260918-1630  running     claude     started 2026-09-18T16:30" in capsys.readouterr().out
    assert cli.main(["status"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("run 20260918-1630  claude  started 2026-09-18T16:30  running")
    assert "  triage    running" in out
    (d / "state.json").write_text("nope")
    assert cli.main(["status", "latest"]) == 2
    assert "unreadable ledger" in capsys.readouterr().out


def test_dry_run_prints_the_selected_stages_with_harness_and_model(capsys):
    assert cli.main(["run", "--dry-run", "--from", "pick", "--skip", "research"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("dry run: 3 stage(s) on claude, config ")
    assert out[1] == "  pick      python"
    assert out[2].startswith("  tailor    fanned  claude  fable  x3 900s 2 attempts")
    assert out[3] == "  report    python"
    assert cli.main(["run", "--dry-run", "--only", "triage", "--harness", "codex"]) == 0
    assert "  triage    fanned  codex  haiku  x8 300s 3 attempts" in capsys.readouterr().out


def test_the_other_commands_say_they_land_later(capsys):
    for argv in (["report"],):
        assert cli.main(argv) == 2
        err = capsys.readouterr().err
        assert "lands in " in err and "docs/spec-hunt-orchestrator.md section 12" in err
        assert ("PR 3, feat/hunt-fanout" in err) == (argv[0] == "report")   # report is PR 3, not this PR
