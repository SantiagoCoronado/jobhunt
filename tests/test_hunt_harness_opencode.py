"""The opencode adapter: argv with and without a role, the schema in the prompt, the parser
on two captured streams (a three-step run with a granted read and a refused write, and a model
it does not know, both 2026-09-21), and the catalog from `opencode models`."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from src.hunt import harness
from src.hunt.harness import Invocation, Model, Usage
from src.hunt.harness import opencode as opencode_mod
from src.hunt.harness.opencode import SCHEMA_LINE, OpencodeHarness

FIX = Path(__file__).resolve().parent / "fixtures" / "hunt"


def _inv(tools=frozenset({"read"}), model="openrouter/~anthropic/claude-haiku-latest", schema=None, role="triager",
         prompt="do the thing") -> Invocation:
    return Invocation(prompt=prompt, system="You are a role.", model=model, tools=frozenset(tools),
                      cwd=Path("/tmp/x"), timeout_s=300, schema=schema, role=role)


def test_argv_with_a_role_sends_the_task_alone_and_the_agent_file_applies_the_tools():
    h = OpencodeHarness()
    assert h.argv(_inv()) == ["opencode", "run", "--format", "json", "-m", "openrouter/~anthropic/claude-haiku-latest",
                              "--agent", "triager", "do the thing"]
    assert h.argv(_inv({"read", "write", "bash"})) == h.argv(_inv())        # tools live in the agent file
    assert h.stdin(_inv()) is None
    assert "--auto" not in h.argv(_inv())


def test_argv_without_a_role_or_model_prepends_the_system_text():
    h = OpencodeHarness(binary="/opt/opencode")
    assert h.argv(_inv(model=None, role=None)) == ["/opt/opencode", "run", "--format", "json",
                                                   "You are a role.\n\ndo the thing"]
    with pytest.raises(ValueError, match="unknown tool\\(s\\) shell"):
        h.argv(_inv({"shell"}))


def test_a_schema_goes_into_the_prompt():
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
    prompt = OpencodeHarness().argv(_inv(schema=schema, prompt="classify\n"))[-1]
    assert prompt == f'classify\n\n{SCHEMA_LINE}\n{{"type":"object","properties":{{"ok":{{"type":"boolean"}}}}}}\n'


def test_web_is_claimed_only_where_the_search_tool_exists(monkeypatch):
    monkeypatch.delenv("OPENCODE_ENABLE_EXA", raising=False)
    assert OpencodeHarness().capabilities == frozenset({"read", "write", "edit", "bash"})
    monkeypatch.setenv("OPENCODE_ENABLE_EXA", "1")
    assert "web" in OpencodeHarness().capabilities
    assert "web" not in OpencodeHarness(web=False).capabilities and "web" in OpencodeHarness(web=True).capabilities


def test_parse_the_captured_three_step_run_sums_usage_and_takes_the_last_text():
    r = OpencodeHarness().parse((FIX / "opencode_events_success.jsonl").read_text(), "", 0)
    assert r.error is None and r.rate_limited is False and r.envelope is True
    assert r.text == "Writing to denied.txt did not work." and r.structured is None
    # three step_finish events: 7646+8071+8185 in, (13+128)+(28+0)+(9+0) out (reasoning is output)
    assert r.usage == Usage(input=23902, output=178, cache_read=0, cache_create=0, cost_usd=pytest.approx(0.0076156))


def test_parse_the_captured_unknown_model_error():
    r = OpencodeHarness().parse((FIX / "opencode_events_error.jsonl").read_text(), "", 1)
    assert r.error == "UnknownError: Unexpected server error. Check server logs for details."
    assert r.rate_limited is False and r.text is None and r.usage == Usage() and r.envelope is True


def test_parse_structured_rate_limit_bad_exit_and_garbage():
    h = OpencodeHarness()
    step = {"type": "step_finish", "part": {"reason": "stop", "tokens": {"input": 10, "output": 2}, "cost": 0.001}}
    reply = {"type": "text", "part": {"text": ' {"ok": true} '}}
    r = h.parse(f"{json.dumps(reply)}\n{json.dumps(step)}\n", "", 0)
    assert r.structured == {"ok": True} and r.usage == Usage(input=10, output=2, cost_usd=0.001)
    limited = {"type": "error", "error": {"name": "APIError", "data": {"message": "429 Too Many Requests"}}}
    r = h.parse(json.dumps(limited) + "\n", "", 1)
    assert r.rate_limited is True and r.error == "APIError: 429 Too Many Requests"
    assert h.parse(json.dumps({"type": "error", "error": "odd"}) + "\n", "", 1).error == "error"
    r = h.parse(f"{json.dumps(reply)}\n{json.dumps(step)}\n", "killed\n", 137)
    assert r.error == "exit 137: killed"
    assert h.parse(json.dumps({"type": "step_start"}) + "\n", "", 0).error == "no finished step (exit 0)"
    r = h.parse("", "Error: quota exceeded\n", 1)
    assert r.envelope is False and r.rate_limited is True and r.error == "exit 1, no JSON events: Error: quota exceeded"


def test_models_reads_the_live_catalog(monkeypatch):
    out = "opencode/big-pickle\nopenrouter/~anthropic/claude-fable-latest\n\nsome banner line\n"
    monkeypatch.setattr(opencode_mod, "run_catalog", lambda argv, timeout=60: subprocess.CompletedProcess(argv, 0, out, ""))
    assert OpencodeHarness().models() == [Model("opencode/big-pickle", "opencode"),
                                          Model("openrouter/~anthropic/claude-fable-latest", "openrouter")]
    monkeypatch.setattr(opencode_mod, "run_catalog", lambda argv, timeout=60: subprocess.CompletedProcess(argv, 1, "", "no auth"))
    with pytest.raises(ValueError, match="exit 1: no auth"):
        OpencodeHarness().models()


def test_registry_and_the_fan_out_names_the_role():
    assert isinstance(harness.get("opencode"), OpencodeHarness) and "opencode" in harness.SHIPPED
    assert OpencodeHarness().smoke("m", Path("/tmp/x")).role is None
