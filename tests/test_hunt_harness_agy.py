"""The agy adapter: argv (the prompt attached to `--print=`, last), the claude-shaped envelope
by the binary's own field names, the signed-out failure seen on the real CLI (2026-09-21), the
catalog, the doctor's sign-in and shell-permission checks, and the gemini and codex agent
files story 4 adds to `sync-agents`."""
from __future__ import annotations

import json
import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml

from src.hunt import config as hc
from src.hunt import doctor, harness, prompts
from src.hunt.harness import Invocation, Model, Usage
from src.hunt.harness import agy as agy_mod
from src.hunt.harness.agy import AgyHarness

SIGNED_OUT = ("Authentication required. Please visit the URL to log in:\n"
              "  https://accounts.google.com/o/oauth2/auth?access_type=offline&client_id=x\n")


def _inv(tools=frozenset(), model="gemini-pro-latest", schema=None, prompt="do the thing") -> Invocation:
    return Invocation(prompt=prompt, system="You are a role.", model=model, tools=frozenset(tools),
                      cwd=Path("/tmp/x"), timeout_s=300, schema=schema, role="triager")


def _cp(rc=0, out="", err=""):
    return lambda argv, timeout=60: subprocess.CompletedProcess(argv, rc, out, err)


@pytest.mark.parametrize("tools,mode", [
    (set(), []), ({"read"}, []), ({"read", "bash"}, []),
    ({"read", "write"}, ["--mode", "accept-edits"]), ({"edit"}, ["--mode", "accept-edits"]),
])
def test_argv_attaches_the_prompt_to_print_and_puts_it_last(tools, mode):
    assert AgyHarness().argv(_inv(tools)) == ["agy", "--output-format", "json", "--model", "gemini-pro-latest", *mode,
                                              "--print-timeout", "300s", "--print=You are a role.\n\ndo the thing"]


def test_argv_never_uses_a_bare_p_an_agent_or_the_permission_bypass():
    argv = AgyHarness(binary="/opt/agy").argv(_inv({"read", "write", "bash"}, model=None,
                                                   schema={"type": "object", "properties": {"ok": {"type": "boolean"}}}))
    assert argv[0] == "/opt/agy" and "--model" not in argv
    assert "-p" not in argv and "--agent" not in argv and "--dangerously-skip-permissions" not in argv
    assert argv[argv.index("--json-schema") + 1] == '{"type":"object","properties":{"ok":{"type":"boolean"}}}'
    assert argv[-1].startswith("--print=") and AgyHarness().stdin(_inv()) is None
    with pytest.raises(ValueError, match="agy grants no web tool"):
        AgyHarness().argv(_inv({"read", "web"}))


def test_parse_the_envelope_by_the_binarys_field_names():
    h = AgyHarness()
    env = {"result": "ok", "is_error": False, "subtype": "success", "session_id": "s", "num_turns": 1,
           "usage": {"input_tokens": 1200, "output_tokens": 4}, "structured_output": {"word": "ok"}}
    r = h.parse(json.dumps(env), "", 0)
    assert r.error is None and r.text == "ok" and r.structured == {"word": "ok"}
    assert r.usage == Usage(input=1200, output=4)
    r = h.parse("a banner line\n" + json.dumps({**env, "structured_output": None, "result": '{"a": 1}'}) + "\n", "", 0)
    assert r.error is None and r.structured == {"a": 1}                       # the reply itself, when it is the object
    r = h.parse(json.dumps({**env, "is_error": True, "subtype": "error_max_turns", "result": "gave up"}), "", 1)
    assert r.error == "error_max_turns: gave up" and r.rate_limited is False
    r = h.parse(json.dumps({**env, "is_error": True, "subtype": "success", "result": "429 quota exhausted"}), "", 1)
    assert r.error == "error: 429 quota exhausted" and r.rate_limited is True
    assert h.parse(json.dumps(env), "boom\n", 3).error == "exit 3: boom"
    assert h.parse(json.dumps(env), "", 3).error == "exit 3"


def test_parse_the_signed_out_failure_and_garbage():
    h = AgyHarness()
    r = h.parse("", SIGNED_OUT, 1)
    assert r.envelope is False and r.error == "agy is signed out: launch `agy` once with no arguments to sign in"
    assert r.rate_limited is False
    r = h.parse("", 'Error: -p took "--output-format" as its prompt\n', 2)
    assert r.error == 'exit 2, no JSON envelope: Error: -p took "--output-format" as its prompt' and r.usage == Usage()
    assert h.parse("[1, 2]", "", 0).envelope is False


def test_models_and_the_sign_in_message(monkeypatch):
    monkeypatch.setattr(agy_mod, "run_catalog", _cp(1, "", "Fetching available models...\nError: Please sign in to view available models.\n"))
    with pytest.raises(ValueError, match="^sign in: launch `agy` once"):
        AgyHarness().models()
    models, reason = doctor.catalog(AgyHarness())
    assert models is None and reason.startswith("ValueError: sign in")
    monkeypatch.setattr(agy_mod, "run_catalog", _cp(0, "Fetching available models...\nAvailable models:\n  * gemini-pro-latest  (default)\n  - gemini-flash-latest\n"))
    assert AgyHarness().models() == [Model("gemini-pro-latest", "(default)"), Model("gemini-flash-latest", "")]
    monkeypatch.setattr(agy_mod, "run_catalog", _cp(3, "", "network down"))
    with pytest.raises(ValueError, match="exit 3: network down"):
        AgyHarness().models()


def test_shell_permission_reads_the_users_settings(tmp_path):
    settings = tmp_path / "settings.json"
    h = AgyHarness(settings=settings)
    name, status, detail = h.shell_permission()
    assert (name, status) == ("shell", "warn") and "no settings file" in detail and '"command(python)"' in detail
    settings.write_text(json.dumps({"permissions": {"allow": ["command(git status)", "read_file(*)"]}}))
    assert h.shell_permission()[1] == "warn" and "does not cover python" in h.shell_permission()[2]
    for rule in ("command(python)", "command(.venv/bin/python)", "command(python3 -m src.mail_fetch show)", "command(/usr/bin/python3.12)"):
        settings.write_text(json.dumps({"permissions": {"allow": [rule]}}))
        assert h.shell_permission() == ("shell", "ok", f"permissions.allow covers python ({rule})"), rule
    for rule in ("command(pythonic-tool)", "command(echo python)", "unsandboxed(python)"):
        settings.write_text(json.dumps({"permissions": {"allow": [rule]}}))
        assert h.shell_permission()[1] == "warn", rule
    settings.write_text("{not json")
    assert "unreadable (JSONDecodeError)" in h.shell_permission()[2]
    settings.write_text(json.dumps({"permissions": "odd"}))
    assert h.shell_permission()[1] == "warn"


def test_doctor_stops_at_a_signed_out_agy_before_it_spends_a_call(monkeypatch, tmp_path):
    monkeypatch.setattr(agy_mod, "run_catalog", _cp(1, "", "Error: Please sign in to view available models.\n"))
    monkeypatch.setattr(doctor.shutil, "which", lambda b: f"/bin/{b}")
    monkeypatch.setattr(doctor.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, "1.1.27\n", ""))
    h = AgyHarness(settings=tmp_path / "none.json")
    spent = []
    checks, rc = doctor.doctor(hc.parse({"harness": {"default": "agy"}}), get=lambda n: h,
                               smoke_fn=lambda *a: spent.append("smoke"), probe_fn=lambda *a: spent.append("probe"))
    assert rc == 2 and spent == []
    assert [(c.name, c.status) for c in checks] == [("binary", "ok"), ("version", "ok"), ("sign-in", "FAIL"), ("shell", "warn")]
    assert "launch `agy` once" in checks[2].detail and "—" not in doctor.render("agy", checks, rc)


def test_the_pre_run_check_fails_a_signed_out_agy_without_spending_a_smoke_prompt(monkeypatch, tmp_path):
    """`hunt run` has one gate, `validate_models`, and never calls `checks()`. A catalog that
    exists and cannot be read is a FAIL there, not "no catalog": the smoke prompt on a
    signed-out agy prints a login URL and waits 120 s, once per distinct model (PR 31 review)."""
    monkeypatch.setattr(agy_mod, "run_catalog", _cp(1, "", "Fetching available models...\nError: Please sign in to view available models.\n"))
    cfg = hc.parse({"harness": {"default": "agy"}, "stages": {"triage": {"model": "gemini-flash"}, "match": {"model": "gemini-pro"}}})
    smoked = []
    checks = doctor.validate_models(cfg, ["triage", "match", "pick"], "agy", get=lambda n: AgyHarness(settings=tmp_path / "none.json"),
                                    smoke_fn=lambda *a: smoked.append(a) or (None, None, 0.0))
    assert smoked == []
    assert [(c.name, c.status) for c in checks] == [("triage", "FAIL"), ("match", "FAIL")]
    assert "the model catalog could not be read" in checks[0].detail and "sign in: launch `agy` once" in checks[0].detail
    assert "doctor --harness agy" in checks[0].detail and "\u2014" not in checks[0].detail


def test_a_harness_with_honestly_no_catalog_still_smokes(tmp_path):
    class NoCatalog(AgyHarness):
        def models(self):
            return None
    smoked = []
    checks = doctor.validate_models(hc.parse({"harness": {"default": "agy"}, "stages": {"triage": {"model": "m"}}}), ["triage"], "agy",
                                    get=lambda n: NoCatalog(settings=tmp_path / "none.json"),
                                    smoke_fn=lambda h, model: smoked.append(model) or (None, None, 1.5))
    assert smoked == ["m"] and checks[0].status == "ok" and "no catalog on agy" in checks[0].detail


def test_doctor_goes_on_when_agy_is_signed_in(monkeypatch, tmp_path):
    monkeypatch.setattr(agy_mod, "run_catalog", _cp(0, "gemini-pro-latest\n"))
    monkeypatch.setattr(doctor.shutil, "which", lambda b: f"/bin/{b}")
    monkeypatch.setattr(doctor.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, "1.1.27\n", ""))
    h = AgyHarness(settings=tmp_path / "none.json")
    checks, rc = doctor.doctor(hc.parse({"harness": {"default": "agy"}, "stages": {"triage": {"model": "gemini-pro-latest"}}}),
                               get=lambda n: h, probe_fn=lambda h, m, cwd: doctor.Check("tools", "ok", "probe"))
    assert rc == 0 and [c.name for c in checks][:4] == ["binary", "version", "sign-in", "shell"]
    assert ("catalog", "ok") in [(c.name, c.status) for c in checks] and checks[-1].name == "tools"


def test_registry():
    assert isinstance(harness.get("agy"), AgyHarness) and harness.SHIPPED == ("claude", "codex", "opencode", "pi", "agy")


def test_render_gemini_and_codex_agent_files():
    roles = prompts.load_roles()
    cfg = hc.load()
    head, body = prompts.render_gemini(roles["company-researcher"], cfg).split("\n---\n", 1)
    front = yaml.safe_load(head.removeprefix("---\n"))
    assert front == {"name": "company-researcher", "description": roles["company-researcher"].description, "kind": "local",
                     "tools": ["read_file", "write_file", "run_shell_command", "google_web_search", "web_fetch"]}
    assert body.endswith(roles["company-researcher"].body) and prompts.GENERATED_MARK.format(name="company-researcher") in body
    for name, role in roles.items():
        text = prompts.render_codex(role, cfg)
        data = tomllib.loads(text)
        assert data["name"] == name and data["description"] == role.description
        assert data["developer_instructions"] == role.body.rstrip("\n") + "\n" and "model" not in data
        assert text.startswith(f"# generated by `python -m src.hunt sync-agents` from prompts/agents/{name}.md")
    assert tomllib.loads(prompts.render_codex(roles["inbox-classifier"], cfg))["sandbox_mode"] == "workspace-write"   # bash
    on_codex = hc.parse({"harness": {"default": "codex"}, "stages": {"match": {"model": "gpt-5.5"}}})
    assert tomllib.loads(prompts.render_codex(roles["job-matcher"], on_codex))["model"] == "gpt-5.5"
    assert prompts._toml_basic('a "q" \\ b\tc\x01') == 'a \\"q\\" \\\\ b\\tc\\u0001'
