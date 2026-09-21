"""The pi adapter: argv pinned per tool set, the prompt on stdin, the parser on a captured
two-turn run (a read probe, 2026-09-21) and on the failure shapes, the catalog table from
`pi --list-models`, and the `.pi/agents` renderer."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from src.hunt import config as hc
from src.hunt import harness, prompts
from src.hunt.harness import Invocation, Model, Usage
from src.hunt.harness import pi as pi_mod
from src.hunt.harness.pi import PiHarness

FIX = Path(__file__).resolve().parent / "fixtures" / "hunt"
BASE = ["pi", "-p", "--mode", "json", "--no-session", "--no-context-files", "--no-skills", "--no-prompt-templates",
        "--no-approve"]


def _inv(tools=frozenset(), model="openrouter/~anthropic/claude-haiku-latest", prompt="do the thing") -> Invocation:
    return Invocation(prompt=prompt, system="You are a role.", model=model, tools=frozenset(tools),
                      cwd=Path("/tmp/x"), timeout_s=300, role="triager")


@pytest.mark.parametrize("tools,tail", [
    (set(), ["--no-tools"]),
    ({"read"}, ["--tools", "read"]),
    ({"bash", "edit", "write", "read"}, ["--tools", "read,write,edit,bash"]),
])
def test_argv_is_pinned_per_tool_set(tools, tail):
    assert PiHarness().argv(_inv(tools)) == [*BASE, "--model", "openrouter/~anthropic/claude-haiku-latest",
                                             "--system-prompt", "You are a role.", *tail]


def test_argv_default_model_binary_and_a_tool_pi_cannot_grant():
    argv = PiHarness(binary="/opt/pi").argv(_inv({"read"}, model=None))
    assert argv[0] == "/opt/pi" and "--model" not in argv and "--provider" not in argv
    with pytest.raises(ValueError, match="pi grants no web tool"):
        PiHarness().argv(_inv({"read", "web"}))
    with pytest.raises(ValueError, match="unknown tool\\(s\\) shell"):
        PiHarness().argv(_inv({"shell"}))
    assert PiHarness().capabilities == frozenset({"read", "write", "edit", "bash"})


def test_the_prompt_goes_on_stdin_never_in_argv():
    inv = _inv({"read"}, prompt="@not-a-file and\n- not an option")
    assert PiHarness().stdin(inv) == "@not-a-file and\n- not an option"
    assert not any("not-a-file" in a for a in PiHarness().argv(inv))


def test_parse_the_captured_two_turn_run_sums_usage_and_takes_the_last_reply():
    r = PiHarness().parse((FIX / "pi_events_success.jsonl").read_text(), "", 0)
    assert r.error is None and r.rate_limited is False and r.envelope is True
    assert r.text == "probe 5c2e77" and r.structured is None
    # two assistant messages: 796+840 in, 165+10 out (`output` already counts reasoning)
    assert r.usage == Usage(input=1636, output=175, cache_read=0, cache_create=0, cost_usd=pytest.approx(0.002511))


def _end(role="assistant", text="ok", stop="stop", **extra) -> str:
    message = {"role": role, "content": [{"type": "thinking", "thinking": "hm"}, {"type": "text", "text": text}],
               "usage": {"input": 5, "output": 1, "cost": {"total": 0.5}}, "stopReason": stop, **extra}
    return json.dumps({"type": "message_end", "message": message}) + "\n"


def test_parse_failures_rate_limit_structured_and_garbage():
    h = PiHarness()
    r = h.parse(_end(text="", stop="error", errorMessage="429 rate limit exceeded"), "", 1)
    assert r.error == "error: 429 rate limit exceeded" and r.rate_limited is True and r.usage.input == 5
    assert h.parse(_end(text="", stop="aborted"), "", 0).error == "aborted"
    # a failed turn followed by one that answered is a success
    r = h.parse(_end(text="", stop="error", errorMessage="boom") + _end(text='{"ok": true}'), "", 0)
    assert r.error is None and r.structured == {"ok": True} and r.usage == Usage(input=10, output=2, cost_usd=1.0)
    assert h.parse(_end(), "killed\n", 137).error == "exit 137: killed"
    assert h.parse(_end(role="user"), "", 0).error == "no assistant message (exit 0)"      # the echo of the prompt is not an answer
    r = h.parse("", 'Error: Model "no-such/model-xyz" not found. Use --list-models to see available models.\n', 1)
    assert r.envelope is False and r.rate_limited is False
    assert r.error == 'exit 1, no JSON events: Error: Model "no-such/model-xyz" not found. Use --list-models to see available models.'


def test_models_reads_the_live_catalog_table(monkeypatch):
    out = ("provider    model                            context  max-out  thinking  images\n"
           "openrouter  ~anthropic/claude-fable-latest   1M       128K     yes       yes   \n"
           "google      gemini-flash-latest              1M       64K      yes       no\n\n")
    monkeypatch.setattr(pi_mod, "run_catalog", lambda argv, timeout=60: subprocess.CompletedProcess(argv, 0, out, ""))
    assert PiHarness().models() == [
        Model("openrouter/~anthropic/claude-fable-latest", "context 1M max-out 128K thinking yes images yes"),
        Model("google/gemini-flash-latest", "context 1M max-out 64K thinking yes images no")]
    monkeypatch.setattr(pi_mod, "run_catalog", lambda argv, timeout=60: subprocess.CompletedProcess(argv, 2, "", "offline"))
    with pytest.raises(ValueError, match="exit 2: offline"):
        PiHarness().models()


def test_registry_and_smoke():
    assert isinstance(harness.get("pi"), PiHarness) and "pi" in harness.SHIPPED
    assert PiHarness().argv(PiHarness().smoke(None, Path("/tmp/x")))[-1] == "--no-tools"


def test_render_pi_names_pi_tools_and_drops_web():
    roles = prompts.load_roles()
    cfg = hc.parse({"harness": {"default": "pi"}, "stages": {"research": {"model": "openrouter/x", "harness": "pi"}}})
    head = prompts.render_pi(roles["company-researcher"], cfg).split("\n---\n")[0].splitlines()
    assert head[:2] == ["---", "name: company-researcher"] and head[3:] == ["tools: read, write, bash", "model: openrouter/x"]
    assert "model:" not in prompts.render_pi(roles["company-researcher"], hc.load()).split("\n---\n")[0]   # hunt.toml runs it on claude
    text = prompts.render_pi(roles["resume-tailor"], hc.load())
    assert "tools: read, write, edit, bash" in text and text.endswith(roles["resume-tailor"].body)
    assert prompts.GENERATED_MARK.format(name="resume-tailor") in text
