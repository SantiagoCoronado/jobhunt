"""The generic template harness: `[harness.<name>]` validation on load, placeholder
substitution (one argument each, dropped with its flag when there is nothing to put there),
where the prompt goes when the command has no place for it, both envelopes, and one template
run as a real process."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from src.hunt import config as hc
from src.hunt import doctor, harness
from src.hunt.harness import Invocation, Usage
from src.hunt.harness._common import SCHEMA_LINE
from src.hunt.harness.generic import GenericHarness

GEMINI = {"command": "gemini -m {model} --approval-mode auto_edit -o json -p {prompt}", "envelope": "json",
          "capabilities": ["read", "write", "edit", "bash", "web"]}


def _inv(tools=frozenset({"read"}), model="gemini-pro", schema=None, prompt="do the\n'thing' \"now\" $HOME") -> Invocation:
    return Invocation(prompt=prompt, system="You are a role.", model=model, tools=frozenset(tools),
                      cwd=Path("/tmp/x"), timeout_s=300, schema=schema, role="triager")


def test_placeholders_are_one_argument_each_and_never_see_a_shell(tmp_path):
    h = GenericHarness("gemini", GEMINI, scratch=tmp_path)
    assert h.argv(_inv()) == ["gemini", "-m", "gemini-pro", "--approval-mode", "auto_edit", "-o", "json", "-p",
                              "You are a role.\n\ndo the\n'thing' \"now\" $HOME"]
    assert h.stdin(_inv()) is None and h.binary == "gemini" and h.name == "gemini"
    assert h.capabilities == frozenset({"read", "write", "edit", "bash", "web"}) and h.models() is None
    assert h.version_argv() == ["gemini", "--version"]


def test_no_model_drops_the_argument_and_its_flag(tmp_path):
    h = GenericHarness("gemini", GEMINI, scratch=tmp_path)
    assert h.argv(_inv(model=None))[:3] == ["gemini", "--approval-mode", "auto_edit"]
    joined = GenericHarness("x", {"command": "tool --model={model} run {prompt}"}, scratch=tmp_path)
    assert joined.argv(_inv(model=None)) == ["tool", "run", "You are a role.\n\ndo the\n'thing' \"now\" $HOME"]   # `run` is no flag: it stays
    assert joined.argv(_inv(model="m"))[1] == "--model=m"
    # `--opt={model}` is its own flag: an empty one goes alone, the flag before it is not its to take
    after = GenericHarness("y", {"command": "tool --json --model={model} -p {prompt}"}, scratch=tmp_path)
    assert after.argv(_inv(model=None, prompt="task")) == ["tool", "--json", "-p", "You are a role.\n\ntask"]
    assert after.argv(_inv(model="m", prompt="task"))[1:3] == ["--json", "--model=m"]


def test_files_system_placement_and_the_schema(tmp_path):
    h = GenericHarness("x", {"command": "tool --system {system_file} --schema {schema_file} --in {prompt_file}"}, scratch=tmp_path)
    schema = {"type": "object"}
    argv = h.argv(_inv(schema=schema))
    system, schema_file, prompt = (Path(argv[i]) for i in (2, 4, 6))
    assert system.read_text() == "You are a role." and json.loads(schema_file.read_text()) == schema
    assert prompt.read_text() == "do the\n'thing' \"now\" $HOME"          # the system has its own place: not prepended
    assert {p.parent for p in (system, schema_file, prompt)} == {tmp_path}
    assert h.argv(_inv()) == ["tool", "--system", str(system), "--in", str(prompt)]      # no schema: flag and file both go
    # a schema the command has no place for rides in the prompt
    text = GenericHarness("y", {"command": "tool {prompt}"}, scratch=tmp_path).argv(_inv(schema=schema, prompt="classify"))[-1]
    assert text == f'You are a role.\n\nclassify\n\n{SCHEMA_LINE}\n{{"type":"object"}}\n'
    inline = GenericHarness("z", {"command": "tool --sys {system} {prompt}"}, scratch=tmp_path).argv(_inv(prompt="task"))
    assert inline == ["tool", "--sys", "You are a role.", "task"]


def test_a_command_with_no_place_for_the_prompt_gets_it_on_stdin(tmp_path):
    h = GenericHarness("x", {"command": "tool --json '{{\"mode\": 1}}' -m {model}"}, scratch=tmp_path)
    assert h.argv(_inv()) == ["tool", "--json", '{"mode": 1}', "-m", "gemini-pro"]      # {{ }} is a literal brace
    assert h.stdin(_inv(prompt="task")) == "You are a role.\n\ntask"


def test_a_tool_the_template_does_not_claim_is_refused(tmp_path):
    h = GenericHarness("x", {"command": "tool {prompt}"}, scratch=tmp_path)
    assert h.capabilities == frozenset({"read", "write", "edit", "bash"})
    with pytest.raises(ValueError, match="x grants no web tool"):
        h.argv(_inv({"read", "web"}))


def test_parse_both_envelopes(tmp_path):
    text = GenericHarness("t", {"command": "tool {prompt}"}, scratch=tmp_path)
    r = text.parse(' {"ok": true}\n', "", 0)
    assert r.error is None and r.text == '{"ok": true}' and r.structured == {"ok": True} and r.usage == Usage()
    r = text.parse("", "429 rate limit\n", 1)
    assert r.error == "exit 1: 429 rate limit" and r.rate_limited is True
    assert text.parse("", "", 9).error == "exit 9"
    js = GenericHarness("j", GEMINI, scratch=tmp_path)
    r = js.parse('Loaded cached credentials.\n{"response": "ok", "stats": {"models": {}}}\n', "", 0)
    assert r.error is None and r.text == "ok" and r.usage == Usage()                      # gemini's shape: no `usage`, so nulls
    r = js.parse(json.dumps({"result": "fine", "usage": {"input_tokens": 9, "output_tokens": 2, "cached_input_tokens": 4},
                             "structured_output": {"a": 1}}), "", 0)
    assert r.usage == Usage(input=9, output=2, cache_read=4) and r.structured == {"a": 1}
    assert js.parse(json.dumps({"error": {"message": "quota exceeded"}}), "", 1).error == "error: quota exceeded"
    assert js.parse(json.dumps({"error": {"message": "quota exceeded"}}), "", 1).rate_limited is True
    assert js.parse(json.dumps({"is_error": True, "result": "nope"}), "", 0).error == "error: nope"
    assert js.parse(json.dumps({"response": "ok"}), "died\n", 2).error == "exit 2: died"
    r = js.parse("no json here", "", 0)
    assert r.envelope is False and r.error == "exit 0, no JSON envelope: no json here"


@pytest.mark.parametrize("block,needle", [
    ({}, "needs a `command` template"),
    ({"command": "  "}, "needs a `command` template"),
    ({"command": "tool {prompt}", "envelop": "json"}, "unknown key(s) envelop"),
    ({"command": "tool {promt}"}, "unknown placeholder {promt}"),
    ({"command": "tool 'unclosed {prompt}"}, "does not split as a command line"),
    ({"command": "{model} run"}, "must start with the program to run"),
    ({"command": "tool {prompt}", "envelope": "xml"}, "envelope must be one of text, json"),
    ({"command": "tool {prompt}", "capabilities": ["read", "shell"]}, "capabilities must be a list from"),
    ({"command": "tool {prompt}", "capabilities": "read"}, "capabilities must be a list from"),
    ({"command": "tool {prompt"}, "bad braces"),
])
def test_a_bad_template_fails_when_the_config_loads(block, needle):
    with pytest.raises(ValueError, match=__import__("re").escape(needle)):
        hc.parse({"harness": {"mine": block}})


def test_a_template_cannot_shadow_a_shipped_adapter_and_the_registry_resolves_templates():
    with pytest.raises(ValueError, match="would shadow the shipped codex adapter"):
        hc.parse({"harness": {"codex": {"command": "codex {prompt}"}}})
    cfg = hc.parse({"harness": {"default": "gemini", "gemini": GEMINI}})
    h = harness.get("gemini", templates=cfg.harness_templates)
    assert isinstance(h, GenericHarness) and h.envelope == "json"
    with pytest.raises(ValueError, match="unknown harness 'qwen' \\(known: claude, codex, opencode, pi, agy, gemini;"):
        harness.get("qwen", templates=cfg.harness_templates)
    assert harness.get("claude", templates=cfg.harness_templates).name == "claude"


FAKE_CLI = r'''
import json, sys
args = sys.argv[1:]
model = args[args.index("-m") + 1] if "-m" in args else "default"
prompt = open(args[args.index("--in") + 1]).read()
print("a banner")
print(json.dumps({"response": f"{model}|{prompt}", "usage": {"input_tokens": len(prompt), "output_tokens": 1}}))
'''


def test_a_template_runs_as_a_real_process_and_doctor_names_the_missing_catalog(tmp_path, monkeypatch):
    script = tmp_path / "fakecli.py"
    script.write_text(FAKE_CLI)
    block = {"command": f"{sys.executable} {script} -m {{model}} --in {{prompt_file}}", "envelope": "json"}
    cfg = hc.parse({"harness": {"default": "mine", "mine": block}, "stages": {"triage": {"model": "big-one"}}})
    h = harness.get("mine", templates=cfg.harness_templates, scratch=tmp_path / "scratch")
    res, err, _secs = doctor.smoke(h, "big-one", cwd=tmp_path)
    assert err is None and res.text == "big-one|You are a smoke test.\n\nReply with the single word ok"
    assert res.usage.input == len("You are a smoke test.\n\nReply with the single word ok") and res.usage.output == 1
    res, err, _secs = doctor.smoke(h, None, cwd=tmp_path)
    assert err is None and res.text.startswith("default|")
    # no catalog: the configured model is passed through, validated by the smoke prompt, and doctor says so
    checks = doctor.validate_models(cfg, ["triage"], "mine", get=lambda n: h)
    assert [(c.name, c.status) for c in checks] == [("triage", "ok")] and "no catalog on mine" in checks[0].detail
