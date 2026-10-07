"""prompts/agents/<role>.md, prompts/commands/<name>.md and sync-agents: the role and command
files parse, the generated files match them (the CI check), and drift is reported not silently
fixed."""
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


# one file per role per harness, plus opencode's narrowed `hunt-<role>` files, plus one file
# per command per harness that has a command format
N_AGENT_FILES = len(prompts.ROLE_STAGE) * len(prompts.NATIVE) + len(prompts.hunt_grants(prompts.load_roles()))
N_COMMAND_FILES = len(prompts.load_commands()) * len(prompts.NATIVE_COMMANDS) + 1     # + AGENTS.md
N_FILES = N_AGENT_FILES + N_COMMAND_FILES


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


def test_opencode_gets_a_narrowed_hunt_agent_where_the_stage_grants_less_than_the_role_file():
    """opencode applies tools only through an agent file, so the matcher's interactive bash
    (ingest) would reach a hunt unit, where ingest is Python's (decision 13; PR 31 review)."""
    roles = prompts.load_roles()
    assert prompts.hunt_grants(roles) == {"job-matcher": frozenset({"read", "write"})}
    yaml = __import__("yaml")
    own = yaml.safe_load(prompts.render_opencode(roles["job-matcher"], hc.load()).split("\n---\n")[0][4:])
    hunt = yaml.safe_load(prompts.render_opencode(roles["job-matcher"], hc.load(), frozenset({"read", "write"})).split("\n---\n")[0][4:])
    assert own["permission"]["bash"]["python *"] == "allow" and hunt["permission"]["bash"] == "deny"
    assert hunt["permission"]["edit"] == "allow" and hunt["description"].startswith("The hunt orchestrator's grant of job-matcher")
    targets = prompts.targets(hc.load())
    path = prompts.AGENTS_ROOT / ".opencode" / "agents" / "hunt-job-matcher.md"
    assert path in targets and targets[path].endswith(roles["job-matcher"].body)
    assert not [p for p in targets if p.name.startswith("hunt-") and ".opencode" not in p.parts]


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
    for harness_name, (folder, suffix, _render) in prompts.NATIVE.items():
        extra = [f"hunt-{r}{suffix}" for r in prompts.hunt_grants(prompts.load_roles())] if harness_name == "opencode" else []
        assert sorted(p.name for p in (tmp_path / folder).iterdir()) == sorted([*(f"{r}{suffix}" for r in prompts.ROLE_STAGE), *extra])
    for folder, suffix, _render in prompts.NATIVE_COMMANDS.values():
        assert sorted(p.name for p in (tmp_path / folder).iterdir()) == sorted(f"{c}{suffix}" for c in prompts.load_commands())
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
    assert capsys.readouterr().out.strip() == f"agents and commands in sync ({N_FILES} files)"
    assert (tmp_path / ".claude" / "agents" / "inbox-classifier.md").read_text().startswith("---\nname: inbox-classifier\n")
    assert Path(".claude/agents/triager.md").exists()


# --- commands (docs/spec-pre-release.md decision 4) ---

def test_every_command_source_parses_and_the_claude_render_is_the_committed_file():
    """The claude render of each source is the committed `.claude/commands` file (story 1 landed
    it byte-identical to the hand-written files before they became renders)."""
    commands = prompts.load_commands()
    assert len(commands) >= 13 and all(name.startswith("jh-") for name in commands)
    for cmd in commands.values():
        committed = (prompts.AGENTS_ROOT / ".claude" / "commands" / f"{cmd.name}.md").read_text(encoding="utf-8")
        assert prompts.render_claude_command(cmd) == committed, cmd.name


def test_render_claude_command_maps_the_vocabulary_and_quotes_only_what_yaml_would_misread(tmp_path):
    path = tmp_path / "jh-x.md"
    path.write_text("---\ndescription: 'Do x: then y'\nargument-hint: '[job_id]'\n"
                    "tools: [read, bash, glob, web, agent, gmail-read, gmail-draft]\n---\n\nBody $ARGUMENTS.\n")
    text = prompts.render_claude_command(prompts.parse_command(path))
    assert text == ("---\ndescription: Do x: then y\nargument-hint: \"[job_id]\"\n"
                    "allowed-tools: Read, Bash, Glob, WebSearch, WebFetch, Task, mcp__claude_ai_Gmail__search_threads, "
                    "mcp__claude_ai_Gmail__get_thread, mcp__claude_ai_Gmail__get_message, mcp__claude_ai_Gmail__create_draft\n"
                    "---\n" + prompts.COMMAND_MARK.format(name="jh-x") + "\n\nBody $ARGUMENTS.\n")
    path.write_text("---\ndescription: d\nargument-hint: <job_id>\n---\nb\n")
    assert prompts.render_claude_command(prompts.parse_command(path)) == (
        "---\ndescription: d\nargument-hint: <job_id>\n---\n" + prompts.COMMAND_MARK.format(name="jh-x") + "\nb\n")


@pytest.mark.parametrize("name,text,needle", [
    ("jh-x.md", "no frontmatter\n", "missing the --- frontmatter"),
    ("x.md", "---\ndescription: d\n---\nb\n", "starts with jh-"),
    ("jh-x.md", "---\ntools: [read]\n---\nb\n", "description is required"),
    ("jh-x.md", "---\ndescription: d\ntools: [read, Bash]\n---\nb\n", "unknown tool(s) Bash"),
    ("jh-x.md", "---\ndescription: d\ntools: [read, read]\n---\nb\n", "listed twice"),
    ("jh-x.md", "---\ndescription: d\nallowed-tools: Read\n---\nb\n", "unknown frontmatter key(s) allowed-tools"),
    ("jh-x.md", "---\ndescription: d\n---\nb \u2014 dash\n", "contains an em-dash"),
])
def test_command_file_validation(tmp_path, name, text, needle):
    path = tmp_path / name
    path.write_text(text)
    with pytest.raises(ValueError, match=__import__("re").escape(needle)):
        prompts.parse_command(path)


def test_check_reports_a_hand_edited_command(tmp_path):
    cfg = hc.load()
    prompts.sync(cfg, root=tmp_path)
    rendered = tmp_path / ".claude" / "commands" / "jh-hunt.md"
    rendered.write_text(rendered.read_text() + "edited by hand\n")
    changed, _same = prompts.sync(cfg, check=True, root=tmp_path)
    assert changed == [str(rendered)]


# --- renders per harness (decision 4) ---

_NEUTRAL_GONE = ("with Bash", "Bash tool", "Agent tool", "Task tool", "run_in_background", "CLAUDE_PROJECT_DIR",
                 "subagent", "sub-agent", "Workflow", "MCP", "WebSearch", "Glob ")


def test_command_sources_use_harness_neutral_wording():
    for cmd in prompts.load_commands().values():
        for gone in _NEUTRAL_GONE:
            assert gone not in cmd.body, (cmd.name, gone)


def _front(text: str) -> dict:
    return __import__("yaml").safe_load(text.split("\n---\n", 1)[0].removeprefix("---\n"))


def test_opencode_and_pi_renders_parse_and_carry_only_their_keys():
    for cmd in prompts.load_commands().values():
        oc = prompts.render_opencode_command(cmd)
        assert _front(oc) == {"description": cmd.description}
        pi = prompts.render_pi_command(cmd)
        want = {"description": cmd.description} | ({"argument-hint": cmd.argument_hint} if cmd.argument_hint else {})
        assert _front(pi) == want
        for text in (oc, pi, prompts.render_claude_command(cmd)):
            assert prompts.COMMAND_MARK.format(name=cmd.name) in text and text.endswith(cmd.body)


def test_gemini_render_is_toml_with_its_args_placeholder(tmp_path):
    import tomllib
    for cmd in prompts.load_commands().values():
        doc = tomllib.loads(prompts.render_gemini_command(cmd))
        assert set(doc) == {"description", "prompt"} and doc["description"] == cmd.description
        # TOML drops the newline right after the opening quotes, the body's leading blank line
        assert doc["prompt"] == cmd.body.replace("$ARGUMENTS", "{{args}}").removeprefix("\n")
        assert "$ARGUMENTS" not in doc["prompt"] and ("{{args}}" in doc["prompt"]) == ("$ARGUMENTS" in cmd.body)
    for bad in ("run !{ls}", "read @{x.md}", "already {{args}}"):
        path = tmp_path / "jh-bad.md"
        path.write_text(f"---\ndescription: d\n---\n{bad}\n")
        with pytest.raises(ValueError, match="injection"):
            prompts.render_gemini_command(prompts.parse_command(path))


def test_agents_md_lists_every_command_with_the_text_to_say():
    commands = prompts.load_commands()
    text = prompts.render_agents_md(commands)
    assert "## Commands" in text and "prompts/commands/<name>.md" in text and "codex and agy" in text
    for cmd in commands.values():
        assert f"- `{prompts.command_say(cmd)}`: " in text, cmd.name
    assert "- `jh-tailor <job_id>`: Tailor resume + cover letter for a job." in text   # the Usage tail is dropped
    assert (prompts.AGENTS_ROOT / "AGENTS.md").read_text(encoding="utf-8") == text
    assert "\u2014" not in text


def test_every_harness_with_a_shipped_adapter_or_a_template_is_covered():
    """Decision 4: each harness gets native commands or the AGENTS.md list, never neither."""
    assert set(prompts.NATIVE_COMMANDS) | set(prompts.AGENTS_MD_HARNESSES) == {"claude", "codex", "opencode", "pi", "gemini", "agy"}
    assert not set(prompts.NATIVE_COMMANDS) & set(prompts.AGENTS_MD_HARNESSES)


def test_home_skill_points_at_the_source_and_carries_the_installer_mark():
    cmd = prompts.load_commands()["jh-tailor"]
    text = prompts.render_home_skill(cmd)
    assert _front(text) == {"name": "jh-tailor", "description": "Tailor resume + cover letter for a job."}
    assert prompts.HOME_SKILL_MARK in text and "`prompts/commands/jh-tailor.md`" in text
