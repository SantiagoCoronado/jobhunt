"""The codex adapter: argv pinned per tool set, the schema and last-message files, the prompt
on stdin, the event parser on a captured failed run (not logged in, 2026-09-21) and on the
documented success stream, and the catalog from `codex debug models`."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from src.hunt import harness
from src.hunt.harness import Invocation, Model, Usage
from src.hunt.harness import codex as codex_mod
from src.hunt.harness.codex import CodexHarness

FIX = Path(__file__).resolve().parent / "fixtures" / "hunt"


def _inv(tools=frozenset(), model="gpt-5.5", schema=None, prompt="do the thing", system="You are a role.") -> Invocation:
    return Invocation(prompt=prompt, system=system, model=model, tools=frozenset(tools),
                      cwd=Path("/tmp/x"), timeout_s=300, schema=schema)


@pytest.mark.parametrize("tools,sandbox", [
    (set(), "read-only"),
    ({"read"}, "read-only"),
    ({"read", "write"}, "workspace-write"),
    ({"read", "bash"}, "workspace-write"),
    ({"read", "write", "edit", "bash"}, "workspace-write"),
])
def test_argv_is_pinned_and_the_sandbox_is_the_grant(tools, sandbox, tmp_path):
    h = CodexHarness(scratch=tmp_path)
    argv = h.argv(_inv(tools))
    last = argv[4]
    assert argv == ["codex", "exec", "--json", "-o", last, "-m", "gpt-5.5", "--sandbox", sandbox,
                    "--ephemeral", "--skip-git-repo-check", "-"]
    assert Path(last).parent == tmp_path and Path(last).name.startswith("last_")


def test_argv_default_model_schema_file_and_binary(tmp_path):
    h = CodexHarness(binary="/opt/codex", scratch=tmp_path / "deep" / "er")
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
    argv = h.argv(_inv({"read"}, model=None, schema=schema))
    assert argv[0] == "/opt/codex" and "-m" not in argv
    path = Path(argv[argv.index("--output-schema") + 1])
    assert json.loads(path.read_text()) == schema and path.parent == tmp_path / "deep" / "er"
    assert h.argv(_inv({"read"}, model=None, schema=schema))[argv.index("--output-schema") + 1] == str(path)   # one file per schema
    assert argv[-3:] == ["--ephemeral", "--skip-git-repo-check", "-"]
    # two units never share a last-message file
    assert h.argv(_inv(prompt="unit a"))[4] != h.argv(_inv(prompt="unit b"))[4]


def test_the_role_body_and_the_task_go_on_stdin_as_one_prompt(tmp_path):
    h = CodexHarness(scratch=tmp_path)
    inv = _inv({"read"}, prompt="the task line\nthe contract")
    assert h.stdin(inv) == "You are a role.\n\nthe task line\nthe contract"
    assert "the task line" not in " ".join(h.argv(inv))
    assert h.stdin(_inv(system="")) == "do the thing"
    with pytest.raises(ValueError, match="unknown tool\\(s\\) shell"):
        h.argv(_inv({"shell"}))
    assert h.capabilities == frozenset({"read", "write", "edit", "bash"})       # no web: research falls back


def test_parse_the_captured_failed_run():
    r = CodexHarness().parse((FIX / "codex_events_failed.jsonl").read_text(), "", 1)
    assert r.error.startswith("turn failed: unexpected status 401 Unauthorized")
    assert r.envelope is True and r.rate_limited is False and r.text is None and r.usage == Usage()
    assert len(r.error) <= len("turn failed: ") + 200


def test_parse_the_success_stream_ignores_a_transient_reconnect():
    r = CodexHarness().parse((FIX / "codex_events_success.jsonl").read_text(), "noise on stderr\n", 0)
    assert r.error is None and r.rate_limited is False
    assert r.text == '{"word":"ok"}' and r.structured == {"word": "ok"}
    # input_tokens counts the cached ones; Usage.input is the uncached part, as on claude
    assert r.usage == Usage(input=1104, output=21, cache_read=4096, cache_create=None, cost_usd=None)


def test_parse_rate_limit_bad_exit_and_garbage():
    h = CodexHarness()
    limited = '{"type":"turn.started"}\n{"type":"turn.failed","error":{"message":"429 Too Many Requests: rate limit reached"}}\n'
    r = h.parse(limited, "", 1)
    assert r.rate_limited is True and r.error.startswith("turn failed: 429")
    r = h.parse('{"type":"turn.started"}\n{"type":"error","message":"stream closed"}\n', "", 1)
    assert r.error == "exit 1: stream closed" and r.rate_limited is False
    r = h.parse('{"type":"turn.started"}\n', "", 0)                 # exit 0 but no turn ever completed
    assert r.error == "no completed turn (exit 0)"
    ok = (FIX / "codex_events_success.jsonl").read_text()
    assert h.parse(ok, "sandbox denied", 3).error == "exit 3: Reconnecting... 2/5 (stream disconnected before completion)"
    r = h.parse("Reading additional input from stdin...\n", "error: usage limit reached\n", 1)
    assert r.envelope is False and r.rate_limited is True
    assert r.error == "exit 1, no JSON events: error: usage limit reached"
    r = h.parse("", "", 2)
    assert r.error == "exit 2, no JSON events: empty output" and r.usage == Usage()
    plain = '{"type":"item.completed","item":{"type":"agent_message","text":"ok"}}\n{"type":"turn.completed","usage":{}}\n'
    r = h.parse(plain, "", 0)
    assert r.error is None and r.text == "ok" and r.structured is None and r.usage == Usage()


def test_models_reads_the_live_catalog(monkeypatch):
    calls = []

    def fake(argv, timeout=60):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, json.dumps({"models": [
            {"slug": "gpt-5.5", "display_name": "GPT-5.5", "visibility": "list"},
            {"slug": "gpt-daybreak-blue-latest", "display_name": "Daybreak Blue", "visibility": "hide"},
            {"display_name": "no slug"}]}), "")
    monkeypatch.setattr(codex_mod, "run_catalog", fake)
    assert CodexHarness(binary="/opt/codex").models() == [
        Model("gpt-5.5", "GPT-5.5"), Model("gpt-daybreak-blue-latest", "Daybreak Blue (hidden in the picker)")]
    assert calls == [["/opt/codex", "debug", "models"]]
    monkeypatch.setattr(codex_mod, "run_catalog", lambda argv, timeout=60: subprocess.CompletedProcess(argv, 1, "", "boom"))
    with pytest.raises(ValueError, match="exit 1: boom"):
        CodexHarness().models()
    monkeypatch.setattr(codex_mod, "run_catalog", lambda argv, timeout=60: subprocess.CompletedProcess(argv, 0, "not json", ""))
    with pytest.raises(ValueError, match="did not print the JSON catalog"):
        CodexHarness().models()


def test_registry_and_smoke():
    assert isinstance(harness.get("codex"), CodexHarness) and "codex" in harness.SHIPPED
    smoke = CodexHarness().smoke(None, Path("/tmp/x"))
    assert smoke.model is None and smoke.tools == frozenset() and smoke.timeout_s == 120
