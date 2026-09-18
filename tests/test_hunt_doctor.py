"""hunt models, hunt doctor and the run-start model check, on a fake harness whose binary
sits on PATH and whose catalog is a file the test edits between two calls."""
from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

import pytest

from src.hunt import cli, doctor
from src.hunt import config as hc
from src.hunt import harness as harness_mod
from src.hunt import run as run_mod
from src.hunt.harness import TOOL_ORDER, Invocation, Model, Result, Usage
from src.hunt.harness.claude import ClaudeHarness

FAKE_BIN = '''#!/usr/bin/env python3
import json, sys
from pathlib import Path
cat = Path(sys.argv[0]).with_suffix(".catalog")
if sys.argv[1:2] == ["--version"]:
    print("fakeh 0.9.1"); sys.exit(0)
if sys.argv[1:2] == ["models"]:
    print(cat.read_text() if cat.exists() else ""); sys.exit(0)
model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "default"
prompt = sys.stdin.read()
known = cat.read_text().split() if cat.exists() else []
if model != "default" and model not in known:
    print(json.dumps({"error": f"unknown model {model}"})); sys.exit(1)
text = "ok"
if "Read tool on" in prompt:
    path = prompt.split("Read tool on ", 1)[1].split(" and reply", 1)[0]
    text = Path(path).read_text() if "nonce-eater" not in known else "I refuse"
print(json.dumps({"text": text, "usage": {"in": 12, "out": 3}}))
'''


class FakeHarness:
    """A catalog harness: models() shells out to the fake binary."""
    name = "fakeh"
    capabilities = frozenset(TOOL_ORDER)

    def __init__(self, binary: str):
        self.binary = binary

    def version_argv(self):
        return [self.binary, "--version"]

    def argv(self, inv: Invocation):
        argv = [self.binary, "run"]
        if inv.model:
            argv += ["--model", inv.model]
        return argv

    def stdin(self, inv: Invocation):
        return inv.prompt

    def parse(self, stdout: str, stderr: str, rc: int) -> Result:
        try:
            d = json.loads(stdout)
        except ValueError:
            return Result(Usage(), f"exit {rc}: {stderr.strip()[:80]}", False, None, envelope=False)
        if rc != 0 or "error" in d:
            return Result(Usage(), d.get("error", f"exit {rc}"), False, None)
        return Result(Usage(input=d["usage"]["in"], output=d["usage"]["out"]), None, False, d["text"])

    def models(self):
        import subprocess
        out = subprocess.run([self.binary, "models"], capture_output=True, text=True, check=True).stdout
        return [Model(m, "fake") for m in out.split()]


@pytest.fixture
def fake(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "fakeh"
    script.write_text(FAKE_BIN.replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    (bin_dir / "fakeh.catalog").write_text("small-1 big-2\n")
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    h = FakeHarness("fakeh")
    monkeypatch.setattr(harness_mod, "get", lambda name, **kw: h if name == "fakeh" else (_ for _ in ()).throw(ValueError(f"unknown harness '{name}'")))
    cfg = hc.parse({"harness": {"default": "fakeh"},
                    "stages": {"triage": {"model": "small-1"}, "match": {"model": "big-2"}, "inbox": {"model": "small-1"},
                               "research": {"model": "big-2"}, "tailor": {"model": "big-2"}}})
    monkeypatch.setattr(hc, "load", lambda path=None: cfg)
    return bin_dir, cfg, h


def test_models_lists_the_live_catalog_and_greps(fake, capsys):
    assert cli.main(["models"]) == 0
    out = capsys.readouterr().out
    assert out.splitlines()[0] == "fakeh: 2 models" and "  small-1  fake" in out and "  big-2    fake" in out
    assert cli.main(["models", "--grep", "BIG"]) == 0
    assert capsys.readouterr().out.splitlines() == ["fakeh: 1 of 2 models", "  big-2  fake"]
    assert cli.main(["models", "--grep", "nope"]) == 0
    assert "no model matches 'nope' (2 in the catalog)" in capsys.readouterr().out
    assert cli.main(["models", "--harness", "gemini"]) == 2
    assert "unknown harness 'gemini'" in capsys.readouterr().err


def test_doctor_passes_then_fails_when_the_catalog_drops_a_model(fake, capsys):
    bin_dir, cfg, h = fake
    assert cli.main(["doctor"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "doctor: fakeh"
    assert out[1].startswith("  binary    ok    ") and out[1].endswith("/bin/fakeh")
    assert out[2] == "  version   ok    fakeh 0.9.1"
    assert out[3] == "  catalog   ok    2 models"
    assert "  triage    ok    small-1 (fakeh, in the catalog of 2)" in out
    assert "  tailor    ok    big-2 (fakeh, in the catalog of 2)" in out
    assert any(line.startswith("  tools     ok    Read granted and used") for line in out)
    assert out[-1] == "result: ok"
    (bin_dir / "fakeh.catalog").write_text("small-1 huge-3\n")                  # big-2 retired
    assert cli.main(["doctor"]) == 2
    out = capsys.readouterr().out
    assert "  match     FAIL  'big-2' is not in the fakeh catalog (2 models; nearest: small-1, huge-3); pick one from `hunt models`" in out
    assert "  tools" not in out                                                 # no probe on a broken config
    assert out.rstrip().endswith("result: 3 problem(s)")


def test_doctor_reports_a_failed_probe_and_a_missing_binary(fake, capsys, monkeypatch):
    bin_dir, cfg, h = fake
    (bin_dir / "fakeh.catalog").write_text("small-1 big-2 nonce-eater\n")
    assert cli.main(["doctor"]) == 2
    assert "  tools     FAIL  read probe: the reply did not carry the file's nonce ('I refuse')" in capsys.readouterr().out
    assert not list((Path.cwd() / "data" / "hunt").glob(".doctor-probe-*"))          # probe files are removed
    h.binary = "fakeh-missing"
    assert cli.main(["doctor"]) == 2
    assert "  binary    FAIL  'fakeh-missing' is not on PATH" in capsys.readouterr().out


def test_run_start_validation_refuses_a_retired_model(fake, monkeypatch):
    bin_dir, cfg, h = fake
    (bin_dir / "fakeh.catalog").write_text("small-1\n")
    lines: list[str] = []
    monkeypatch.setattr(run_mod, "validate_models", lambda cfg, stages, harness: doctor.validate_models(cfg, stages, harness, get=harness_mod.get))
    from src.hunt.stages import REGISTRY
    monkeypatch.setitem(REGISTRY, "match", REGISTRY["match"].__class__("match", "fanned", run=lambda ctx: None))
    rc = run_mod.run(cfg, ["match"], "fakeh", hunt_dir=bin_dir.parent / "hunt", emit=lines.append)
    assert rc == 2 and lines == ["hunt run: stage match: 'big-2' is not in the fakeh catalog (1 models; nearest: small-1); pick one from `hunt models`"]
    assert not (bin_dir.parent / "hunt").exists()                                # nothing was created


def test_validate_models_without_a_catalog_smokes_each_model_once():
    calls: list[str | None] = []

    def fake_smoke(h, model):
        calls.append(model)
        return (None, None if model != "retired" else "api_error: unknown model", 0.5)
    cfg = hc.parse({"stages": {"triage": {"model": "haiku"}, "match": {"model": "haiku"}, "tailor": {"model": "retired"},
                               "inbox": {}}})
    checks = doctor.validate_models(cfg, ["triage", "match", "tailor", "inbox", "pick"], "claude",
                                    get=lambda n: ClaudeHarness(), smoke_fn=fake_smoke)
    assert [c.name for c in checks] == ["triage", "match", "tailor", "inbox"]
    assert calls == ["haiku", "retired", None]                                   # haiku smoked once for two stages
    assert checks[0].status == "ok" and "smoke prompt ok in 0.5s, no catalog on claude" in checks[0].detail
    assert checks[2].status == "FAIL" and checks[2].detail == "retired (claude): smoke prompt failed, api_error: unknown model"
    assert checks[3].detail.startswith("harness default (claude, smoke prompt ok")


def test_render_models_for_a_catalog_less_harness():
    text = doctor.render_models("claude", None, None, None, ["fable", "opus", "sonnet"])
    assert text.splitlines()[0] == "claude: claude has no model catalog."
    assert "aliases named by `claude --help`: fable, opus, sonnet" in text and "smoke prompt" in text
