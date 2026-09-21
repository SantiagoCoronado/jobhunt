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


N_FILES = len(prompts.ROLE_STAGE) * len(prompts.NATIVE)      # one file per role per harness


def test_generated_agents_are_in_sync_with_the_role_files_and_hunt_toml():
    """The CI gate: `python -m src.hunt sync-agents --check`, every harness's folder."""
    changed, same = prompts.sync(hc.load(), check=True)
    assert changed == [], f"run: python -m src.hunt sync-agents ({changed})"
    assert len(same) == N_FILES


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


def test_a_model_is_written_only_into_the_files_of_the_harness_it_was_picked_from():
    roles = prompts.load_roles()
    cfg = hc.parse({"harness": {"default": "opencode"},
                    "stages": {"match": {"model": "openrouter/x"}, "tailor": {"model": "fable", "harness": "claude"}}})
    assert "model: openrouter/x" in prompts.render_opencode(roles["job-matcher"], cfg)
    assert "model:" not in prompts.render_claude(roles["job-matcher"], cfg).split("\n---\n")[0]
    assert "model: fable" in prompts.render_claude(roles["resume-tailor"], cfg)
    assert "model:" not in prompts.render_opencode(roles["resume-tailor"], cfg).split("\n---\n")[0]


def test_render_opencode_carries_the_permissions_and_no_name():
    roles = prompts.load_roles()
    text = prompts.render_opencode(roles["inbox-classifier"], hc.load())
    head, body = text.split("\n---\n", 1)
    front = __import__("yaml").safe_load(head.removeprefix("---\n"))
    assert front == {"description": roles["inbox-classifier"].description, "mode": "all",
                     "permission": {"read": "allow", "edit": "deny", "webfetch": "deny", "websearch": "deny",
                                    "bash": {"*": "deny", "python *": "allow", ".venv/bin/python *": "allow"}}}
    assert list(front["permission"]["bash"])[0] == "*"            # the last matching pattern wins: deny first
    assert prompts.GENERATED_MARK.format(name="inbox-classifier") in body and body.endswith(roles["inbox-classifier"].body)
    front = __import__("yaml").safe_load(prompts.render_opencode(roles["company-researcher"], hc.load()).split("\n---\n")[0][4:])
    assert front["permission"]["websearch"] == "allow" and front["permission"]["edit"] == "allow"
    front = __import__("yaml").safe_load(prompts.render_opencode(roles["triager"], hc.load()).split("\n---\n")[0][4:])
    assert front["permission"]["bash"] == "deny" and front["permission"]["edit"] == "allow"


def test_sync_writes_then_check_reports_drift(tmp_path):
    cfg = hc.load()
    out = tmp_path / ".claude" / "agents"
    changed, same = prompts.sync(cfg, check=True, root=tmp_path)
    assert len(changed) == N_FILES and same == []
    changed, same = prompts.sync(cfg, root=tmp_path)
    assert len(changed) == N_FILES
    for folder, suffix, _render in prompts.NATIVE.values():
        assert sorted(p.name for p in (tmp_path / folder).iterdir()) == sorted(f"{r}{suffix}" for r in prompts.ROLE_STAGE)
    changed, same = prompts.sync(cfg, check=True, root=tmp_path)
    assert changed == [] and sorted(same) == sorted(str(p) for p in tmp_path.rglob("*") if p.is_file())
    (out / "triager.md").write_text("edited by hand\n")
    changed, same = prompts.sync(cfg, check=True, root=tmp_path)
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
    monkeypatch.setattr(prompts, "AGENTS_ROOT", tmp_path)
    assert main(["sync-agents", "--check"]) == 1
    assert "out of sync (run `python -m src.hunt sync-agents`)" in capsys.readouterr().out
    assert main(["sync-agents"]) == 0
    out = capsys.readouterr().out
    assert out.count("wrote    ") == N_FILES and out.endswith(f"{N_FILES} written, 0 unchanged\n")
    assert main(["sync-agents", "--check"]) == 0
    assert capsys.readouterr().out.strip() == f"agents in sync ({N_FILES} files)"
    assert (tmp_path / ".claude" / "agents" / "inbox-classifier.md").read_text().startswith("---\nname: inbox-classifier\n")
    assert Path(".claude/agents/triager.md").exists()
