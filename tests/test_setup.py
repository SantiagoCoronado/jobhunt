"""The installer (docs/spec-pre-release.md decision 3, PR 4 story 4) on a temp tree: fake agent
binaries on a fake PATH, a recording runner instead of subprocesses (no venv is made, nothing is
pip-installed, no doctor or agent CLI runs), a temp hunt.toml and a temp codex home. Nothing
here touches the real home directory or the checkout's own files."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from src import setup
from src.hunt import config as hc
from src.hunt import prompts

ROOT = Path(__file__).resolve().parent.parent


def _fake_path(tmp_path: Path, *names: str) -> str:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    for name in names:
        exe = bin_dir / name
        exe.write_text("#!/bin/sh\nexit 0\n")
        exe.chmod(0o755)
    (bin_dir / "codex").write_text("not executable\n")          # on PATH but not runnable: not found
    return str(bin_dir)


class Recorder:
    """A Runner that records every call and answers from a table keyed by a word in the argv."""

    def __init__(self, answers: dict[str, tuple[int, str]] | None = None):
        self.calls: list[tuple[list[str], bool]] = []
        self.answers = answers or {}

    def __call__(self, argv, cwd, capture=True):
        argv = [str(a) for a in argv]
        self.calls.append((argv, capture))
        for key, answer in self.answers.items():
            if key in argv or any(key in a for a in argv):
                return answer
        return 0, ""

    def has(self, *words: str) -> bool:
        return any(all(w in argv for w in words) for argv, _ in self.calls)


@pytest.fixture
def tree(tmp_path):
    """A temp checkout: requirements.txt, config/hunt.toml (a copy of the shipped one)."""
    root = tmp_path / "root"
    (root / "config").mkdir(parents=True)
    shutil.copy(ROOT / "config" / "hunt.toml", root / "config" / "hunt.toml")
    (root / "requirements.txt").write_text("PyYAML==6.0.3\n")
    return root


def test_detect_finds_only_executables_on_the_given_path(tmp_path):
    path = _fake_path(tmp_path, "claude", "pi", "gemini")
    assert setup.detect(path) == ["claude", "pi", "gemini"]
    assert setup.detect(str(tmp_path / "empty")) == []


def test_choose_flag_yes_and_the_question(capsys):
    assert setup.choose(["claude"], "pi, codex", False, lambda _q: "") == ["pi", "codex"]
    assert setup.choose(["claude", "pi"], None, True, lambda _q: "x") == ["claude", "pi"]
    with pytest.raises(ValueError, match="unknown harness cursor"):
        setup.choose([], "cursor", False, input)
    answers = iter(["nope", "opencode,claude,claude"])
    assert setup.choose(["claude"], None, False, lambda _q: next(answers)) == ["opencode", "claude"]
    out = capsys.readouterr().out
    assert "[x] claude  (on PATH)" in out and "[ ] codex" in out and "unknown harness nope" in out
    assert setup.choose(["agy"], None, False, lambda _q: "") == ["agy"]          # enter takes what was found


def test_install_makes_the_venv_installs_deps_then_hands_over_to_the_venv(tree, capsys):
    rec = Recorder({"-c": (1, "missing: PyYAML")})
    assert setup.install(["claude"], ["claude", "codex"], True, root=tree, runner=rec, python="/usr/bin/python3") == 0
    argvs = [argv for argv, _ in rec.calls]
    venv_py = str(tree / ".venv" / "bin" / "python")
    assert argvs[0] == ["/usr/bin/python3", "-m", "venv", ".venv"]
    assert argvs[1][:2] == [venv_py, "-c"] and argvs[1][-1] == "requirements.txt"
    assert argvs[2] == [venv_py, "-m", "pip", "install", "-r", "requirements.txt"]
    assert argvs[3] == [venv_py, "-m", "src.setup", "finish", "--harness", "claude,codex", "--home-skills"]
    assert rec.calls[3][1] is False                      # the second half streams to the terminal
    assert "venv: creating .venv" in capsys.readouterr().out


def test_install_reuses_the_venv_and_skips_pip_offline_when_deps_are_there(tree, capsys):
    (tree / ".venv" / "bin").mkdir(parents=True)
    (tree / ".venv" / "bin" / "python").write_text("")
    rec = Recorder({"-c": (0, "all installed")})
    assert setup.install([], ["pi"], False, root=tree, runner=rec) == 0
    assert not rec.has("venv") and not rec.has("pip")
    assert rec.calls[-1][0][-3:] == ["finish", "--harness", "pi"]
    assert "pip skipped" in capsys.readouterr().out


def test_install_refuses_a_venv_on_an_old_python_and_leaves_it(tree, capsys):
    (tree / ".venv" / "bin").mkdir(parents=True)
    (tree / ".venv" / "bin" / "python").write_text("")
    rec = Recorder({"version_info": (1, "")})
    assert setup.install([], ["pi"], False, root=tree, runner=rec) == 1
    assert not rec.has("pip") and not rec.has("finish") and (tree / ".venv").is_dir()
    assert "rm -rf .venv" in capsys.readouterr().out


def test_install_stops_when_pip_fails(tree, capsys):
    rec = Recorder({"-c": (1, "missing: PyYAML"), "pip": (1, "ERROR: no network")})
    assert setup.install([], ["claude"], False, root=tree, runner=rec) == 1
    assert not rec.has("finish") and "pip failed" in capsys.readouterr().out


def test_finish_init_default_harness_home_skills_doctor_and_next_step(tree, tmp_path, capsys):
    toml = tree / "config" / "hunt.toml"
    home = tmp_path / "codexhome"
    foreign = home / "skills" / "jh-hunt" / "SKILL.md"
    foreign.parent.mkdir(parents=True)
    foreign.write_text("my own skill\n")
    rec = Recorder({"init": (0, "init: 6 files from the examples"),
                    "codex": (1, "  FAIL  model haiku: not in the codex catalog")})
    assert setup.finish(["gemini", "codex", "claude"], True, root=tree, runner=rec, hunt_toml=toml,
                        home=home, python="/venv/python") == 0
    out = capsys.readouterr().out
    # init ran under the venv python; the first chosen harness with an adapter is the default
    assert rec.calls[0][0] == ["/venv/python", "-m", "src.init"] and "init: 6 files" in out
    assert hc.load(toml).harness == "codex" and "default harness: codex (config/hunt.toml, was claude)" in out
    # one pointer skill per command, the foreign file left alone
    commands = prompts.load_commands()
    assert foreign.read_text() == "my own skill\n"
    for name in commands:
        path = home / "skills" / name / "SKILL.md"
        if name != "jh-hunt":
            assert path.read_text() == prompts.render_home_skill(commands[name])
    assert f"{len(commands) - 1} written, 0 unchanged, 1 kept" in out
    # doctor for the adapters only; gemini has no template in the shipped hunt.toml
    assert rec.has("doctor", "--harness", "codex") and rec.has("doctor", "--harness", "claude")
    assert not rec.has("doctor", "--harness", "gemini") and "doctor gemini: skipped" in out
    assert "doctor codex: FAIL" in out and "model haiku" in out and "doctor claude: ok" in out
    # the next step in each harness's own words (jh-setup lands with the onboarding PR)
    assert "next: open gemini here and run /jh-discover" in out
    assert "also: open codex here and type $jh-discover" in out
    assert "also: open claude here and run /jh-discover" in out


def test_finish_a_second_time_changes_nothing(tree, tmp_path, capsys):
    toml, home = tree / "config" / "hunt.toml", tmp_path / "codexhome"
    setup.finish(["codex"], True, root=tree, runner=Recorder(), hunt_toml=toml, home=home)
    before = {p: p.read_text() for p in [toml, *home.rglob("*.md")]}
    capsys.readouterr()
    setup.finish(["codex"], True, root=tree, runner=Recorder(), hunt_toml=toml, home=home)
    assert {p: p.read_text() for p in [toml, *home.rglob("*.md")]} == before
    out = capsys.readouterr().out
    assert "default harness: codex (already in config/hunt.toml)" in out and " 0 written," in out


def test_finish_without_home_skills_writes_nothing_outside_the_tree(tree, tmp_path, capsys):
    home = tmp_path / "codexhome"
    (tree / "prompts" / "commands").mkdir(parents=True)
    (tree / "prompts" / "commands" / "jh-setup.md").write_text("---\ndescription: d\n---\nb\n")
    setup.finish(["codex", "agy"], False, root=tree, runner=Recorder(), hunt_toml=tree / "config" / "hunt.toml", home=home)
    out = capsys.readouterr().out
    assert not home.exists() and "--home-skills` adds them as skills" in out
    assert "next: open codex here and say: jh-setup" in out and "also: open agy here and say: jh-setup" in out


def test_check_reports_and_writes_nothing(tree, tmp_path, capsys):
    home = tmp_path / "codexhome"
    (home / "skills" / "jh-hunt").mkdir(parents=True)
    (home / "skills" / "jh-hunt" / "SKILL.md").write_text(f"x\n{setup.HOME_SKILL_MARK}\n")
    snapshot = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    rec = Recorder()
    assert setup.check(["claude"], root=tree, runner=rec, home=home) == 1          # no venv yet
    assert rec.calls == []                                                          # nothing ran
    out = capsys.readouterr().out
    assert "venv: missing" in out and "default harness: claude" in out and "codex home skills: 1 from this installer" in out
    (tree / ".venv" / "bin").mkdir(parents=True)
    (tree / ".venv" / "bin" / "python").write_text("")
    snapshot = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert setup.check([], root=tree, runner=Recorder({"-c": (0, "all installed")}), home=home) == 0
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == snapshot
    assert not any("doctor" in argv for argv, _ in rec.calls)


def test_main_refuses_an_unknown_harness_and_parses_finish(monkeypatch, capsys):
    monkeypatch.setattr(setup, "detect", lambda path=None: [])
    assert setup.main(["--harness", "cursor"]) == 2 and "unknown harness cursor" in capsys.readouterr().out
    seen = {}
    monkeypatch.setattr(setup, "finish", lambda chosen, home_skills: seen.update(chosen=chosen, home=home_skills) or 0)
    assert setup.main(["finish", "--harness", "claude,pi", "--home-skills"]) == 0
    assert seen == {"chosen": ["claude", "pi"], "home": True}
    calls = []
    monkeypatch.setattr(setup, "install", lambda found, chosen, home: calls.append((chosen, home)) or 0)
    assert setup.main(["--harness", "codex"]) == 0 and calls == [(["codex"], False)]      # opt-in: never by default
    assert setup.main([], ask=lambda q: "codex" if "which" in q or "names" in q else "y") == 0
    assert calls[-1] == (["codex"], True)


def test_main_takes_the_defaults_when_stdin_is_closed(monkeypatch, capsys):
    def closed(question):
        raise EOFError
    monkeypatch.setattr(setup, "detect", lambda path=None: ["codex"])
    calls = []
    monkeypatch.setattr(setup, "install", lambda found, chosen, home: calls.append((chosen, home)) or 0)
    assert setup.main([], ask=closed) == 0
    assert calls == [(["codex"], False)]                     # the CLIs on PATH, no home skills
    assert "taking the default" in capsys.readouterr().out


def test_setup_sh_is_a_thin_wrapper():
    text = (ROOT / "setup.sh").read_text()
    assert 'exec "$PY" -m src.setup "$@"' in text and "sys.version_info >= (3, 11)" in text
    assert "pip install" not in text and "venv" not in text
    assert subprocess.run(["bash", "-n", str(ROOT / "setup.sh")], check=False).returncode == 0


def test_run_command_keeps_the_order_through_a_pipe():
    """An agent runs ./setup.sh through a pipe, where print is block-buffered: without the
    flush the venv and deps lines printed after the child's whole output (full-flow run)."""
    code = ("import sys; from pathlib import Path; from src import setup; print('parent first'); "
            "setup.run_command([sys.executable, '-c', 'print(\"child\")'], Path('.'), False)")
    done = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=False)
    assert done.stdout.splitlines() == ["parent first", "child"]


def test_setup_imports_only_the_standard_library_at_the_top():
    """It runs under the system python before the venv exists."""
    import ast
    tree_ = ast.parse((ROOT / "src" / "setup.py").read_text())
    top = [n for n in tree_.body if isinstance(n, ast.Import | ast.ImportFrom)]
    names = {a.name.split(".")[0] for n in top if isinstance(n, ast.Import) for a in n.names}
    names |= {n.module.split(".")[0] for n in top if isinstance(n, ast.ImportFrom) and n.module and n.level == 0}
    assert names <= {"__future__", "argparse", "os", "shutil", "subprocess", "sys", "tomllib", "collections", "pathlib"}
    assert not [n for n in top if isinstance(n, ast.ImportFrom) and n.level]
