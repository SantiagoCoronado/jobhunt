"""prompts/agents/<role>.md and sync-agents: the role files parse, the generated
.claude/agents files match them (the CI check), and drift is reported not silently fixed."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.hunt import config as hc
from src.hunt import prompts
from src.hunt.cli import main
from src.hunt.stages import REGISTRY


def test_every_role_file_parses_and_matches_the_registry():
    roles = prompts.load_roles()
    assert sorted(roles) == sorted(prompts.ROLE_STAGE)
    for role in roles.values():
        stage = REGISTRY[role.stage]
        assert stage.role == role.name, role.name
        # the hunt grants a unit at most what the role file allows (the matcher keeps bash for
        # interactive ingest; under the orchestrator ingest is Python's, decision 13)
        assert stage.tools <= role.tools, f"{role.name}: registry tools {sorted(stage.tools)} vs role file {sorted(role.tools)}"
        assert role.body.strip() and role.output and "—" not in role.body


def test_generated_claude_agents_are_in_sync_with_the_role_files_and_hunt_toml():
    """The CI gate: `python -m src.hunt sync-agents --check`."""
    changed, same = prompts.sync(hc.load(), check=True)
    assert changed == [], f"run: python -m src.hunt sync-agents ({changed})"
    assert len(same) == len(prompts.ROLE_STAGE)


def test_render_claude_carries_tools_model_and_the_generated_mark():
    cfg = hc.parse({"stages": {"match": {"model": "opus"}, "triage": {}}})
    roles = prompts.load_roles()
    text = prompts.render_claude(roles["job-matcher"], cfg)
    head = text.split("\n---\n")[0].splitlines()
    assert head == ["---", "name: job-matcher",
                    "description: " + roles["job-matcher"].description, "tools: Read, Write, Bash", "model: opus"]
    assert prompts.GENERATED_MARK.format(name="job-matcher") in text and text.endswith(roles["job-matcher"].body)
    text = prompts.render_claude(roles["triager"], cfg)
    assert "model:" not in text.split("\n---\n")[0] and "tools: Read, Write" in text
    text = prompts.render_claude(roles["company-researcher"], hc.load())
    assert "tools: Read, Write, Bash, WebSearch, WebFetch" in text and "model: sonnet" in text


def test_sync_writes_then_check_reports_drift(tmp_path):
    cfg = hc.load()
    out = tmp_path / "agents"
    changed, same = prompts.sync(cfg, check=True, agents_dir=out)
    assert len(changed) == 5 and same == []
    changed, same = prompts.sync(cfg, agents_dir=out)
    assert len(changed) == 5 and sorted(p.name for p in out.glob("*.md")) == sorted(f"{r}.md" for r in prompts.ROLE_STAGE)
    assert prompts.sync(cfg, check=True, agents_dir=out) == ([], sorted(str(p) for p in out.glob("*.md")))
    (out / "triager.md").write_text("edited by hand\n")
    changed, same = prompts.sync(cfg, check=True, agents_dir=out)
    assert changed == [str(out / "triager.md")] and (out / "triager.md").read_text() == "edited by hand\n"


@pytest.mark.parametrize("text,needle", [
    ("no frontmatter\n", "missing the --- frontmatter"),
    ("---\nname: other\ndescription: d\ntools: [read]\noutput: o\n---\nbody\n", "must equal the file stem"),
    ("---\nname: triager\ndescription: d\ntools: [read, shell]\noutput: o\n---\nbody\n", "unknown tool(s) shell"),
    ("---\nname: triager\ndescription: d\ntools: [read]\n---\nbody\n", "output (the contract line) is required"),
    ("---\nname: triager\ndescription: d\ntools: [read]\noutput: o\nmodel: x\n---\nbody\n", "unknown frontmatter key(s) model"),
    ("---\nname: triager\ndescription: d\ntools: [read]\noutput: o\n---\nbody — dash\n", "contains an em-dash"),
])
def test_role_file_validation(tmp_path, text, needle):
    path = tmp_path / "triager.md"
    path.write_text(text)
    with pytest.raises(ValueError, match=__import__("re").escape(needle)):
        prompts.parse_role(path)


def test_cli_sync_agents_check_and_write(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(prompts, "CLAUDE_AGENTS_DIR", tmp_path / "agents")
    assert main(["sync-agents", "--check"]) == 1
    assert "out of sync (run `python -m src.hunt sync-agents`)" in capsys.readouterr().out
    assert main(["sync-agents"]) == 0
    out = capsys.readouterr().out
    assert out.count("wrote    ") == 5 and out.endswith("5 written, 0 unchanged\n")
    assert main(["sync-agents", "--check"]) == 0
    assert capsys.readouterr().out.strip() == "agents in sync (5 files)"
    assert (tmp_path / "agents" / "inbox-classifier.md").read_text().startswith("---\nname: inbox-classifier\n")
    assert Path(".claude/agents/triager.md").exists()
