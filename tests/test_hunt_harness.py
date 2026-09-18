"""src/hunt/harness: the protocol types and the claude adapter, argv pinned per tool set
and the envelope parser on two captured envelopes (a success and a login failure)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.hunt import harness
from src.hunt.harness import Invocation, Usage
from src.hunt.harness.claude import ClaudeHarness

FIX = Path(__file__).resolve().parent / "fixtures" / "hunt"


def _inv(tools=frozenset(), model="haiku", schema=None, prompt="do the thing") -> Invocation:
    return Invocation(prompt=prompt, system="You are a role.", model=model, tools=frozenset(tools),
                      cwd=Path("/tmp/x"), timeout_s=300, schema=schema)


BASE = ["claude", "-p", "--output-format", "json", "--no-session-persistence", "--strict-mcp-config",
        "--permission-mode", "acceptEdits", "--permission-prompts", "none"]


@pytest.mark.parametrize("tools,tail", [
    (set(), ["--tools", ""]),
    ({"read"}, ["--tools", "Read", "--allowedTools", "Read"]),
    ({"bash", "read", "write", "edit"}, ["--tools", "Read,Write,Edit,Bash", "--allowedTools", "Read", "Write", "Edit",
                                         "Bash(python:*)", "Bash(.venv/bin/python:*)"]),
    ({"web", "read"}, ["--tools", "Read,WebSearch,WebFetch", "--allowedTools", "Read", "WebSearch", "WebFetch"]),
])
def test_argv_is_pinned_per_tool_set(tools, tail):
    h = ClaudeHarness(bare=False)
    assert h.argv(_inv(tools)) == [*BASE, "--model", "haiku", "--system-prompt", "You are a role.", *tail]


def test_argv_model_default_schema_and_bare(monkeypatch):
    h = ClaudeHarness(bare=False)
    argv = h.argv(_inv({"read"}, model=None, schema={"type": "object", "properties": {"ok": {"type": "boolean"}}}))
    assert "--model" not in argv
    assert argv[-2:] == ["--json-schema", '{"type":"object","properties":{"ok":{"type":"boolean"}}}']
    assert ClaudeHarness(bare=True).argv(_inv())[:3] == ["claude", "-p", "--bare"]
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert ClaudeHarness().bare is False and "--bare" not in ClaudeHarness().argv(_inv())
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert ClaudeHarness().bare is True and ClaudeHarness().argv(_inv())[2] == "--bare"
    assert ClaudeHarness(binary="/opt/claude").argv(_inv())[0] == "/opt/claude"


def test_prompt_goes_on_stdin_and_unknown_tools_raise():
    h = ClaudeHarness(bare=False)
    inv = _inv({"read"}, prompt="the task line\nthe contract")
    assert h.stdin(inv) == "the task line\nthe contract"
    assert "the task line" not in " ".join(h.argv(inv))
    with pytest.raises(ValueError, match="unknown tool\\(s\\) shell"):
        h.argv(_inv({"shell"}))
    assert h.capabilities == frozenset({"read", "write", "edit", "bash", "web"})


def test_parse_the_captured_success_envelope():
    h = ClaudeHarness()
    r = h.parse((FIX / "claude_envelope_success.json").read_text(), "", 0)
    assert r.error is None and r.rate_limited is False and r.text == "ok"
    assert r.usage == Usage(input=1750, output=40, cache_read=0, cache_create=0, cost_usd=pytest.approx(0.002898))
    assert set(r.usage.as_dict()) == {"input", "output", "cache_read", "cache_create", "cost_usd"}


def test_parse_the_captured_login_failure_envelope():
    r = ClaudeHarness().parse((FIX / "claude_envelope_error.json").read_text(), "", 1)
    assert r.error == "api_error: Not logged in · Please run /login"
    assert r.rate_limited is False and r.usage.input == 0 and r.usage.cost_usd == 0
    assert r.text.startswith("Not logged in")


def test_parse_rate_limit_signals_and_garbage():
    h = ClaudeHarness()
    env = json.loads((FIX / "claude_envelope_error.json").read_text())
    env["result"] = "API Error: 429 rate limit reached, retry later"
    r = h.parse(json.dumps(env), "", 1)
    assert r.rate_limited is True and r.error.startswith("api_error: API Error: 429")
    env["result"] = "boom"
    env["api_error_status"] = 529
    r = h.parse(json.dumps(env), "", 1)
    assert r.rate_limited is True and r.error == "api_error (529): boom"
    r = h.parse("", "Error: Overloaded, please retry\n", 1)
    assert r.error == "exit 1, no JSON envelope: Error: Overloaded, please retry" and r.rate_limited is True
    r = h.parse("not json at all", "", 0)
    assert r.error == "exit 0, no JSON envelope: not json at all" and r.rate_limited is False and r.usage == Usage()
    assert r.envelope is False
    ok = json.loads((FIX / "claude_envelope_success.json").read_text())
    r = h.parse(json.dumps(ok), "", 1)                       # a clean envelope but a non-zero exit
    assert r.error == "completed (exit 1)" and r.rate_limited is False


def test_aliases_are_parsed_from_help_and_models_is_none():
    h = ClaudeHarness()
    help_text = ("  --model <model>                       Model for the current session. Provide\n"
                 "                                        an alias for the latest model (e.g.\n"
                 "                                        'fable', 'opus', or 'sonnet') or a\n"
                 "                                        model's full name (e.g.\n"
                 "                                        'claude-fable-5').\n"
                 "  -n, --name <name>                     Set a display name\n")
    assert h.aliases(help_text) == ["fable", "opus", "sonnet"]
    assert h.aliases("no such flag here") == []
    assert h.models() is None
    smoke = h.smoke("haiku", Path("/tmp/x"))
    assert smoke.model == "haiku" and smoke.tools == frozenset() and smoke.timeout_s == 60
    assert ClaudeHarness(bare=False).argv(smoke)[-2:] == ["--tools", ""]


def test_registry_and_tool_check():
    assert isinstance(harness.get("claude"), ClaudeHarness)
    assert harness.get("claude", bare=True).bare is True
    with pytest.raises(ValueError, match="unknown harness 'gemini'"):
        harness.get("gemini")
    assert harness.check_tools({"read", "web"}) == frozenset({"read", "web"})
