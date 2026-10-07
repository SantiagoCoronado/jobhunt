"""The installer behind `./setup.sh` (docs/spec-pre-release.md decision 3).

    python -m src.setup                      ask which agent CLIs you run, then set everything up
    python -m src.setup --harness claude,pi  the same without the question (`--yes` takes the CLIs found on PATH)
    python -m src.setup --check              report what is set up, write nothing, spend nothing

Steps: detect the agent CLIs on PATH (claude, codex, opencode, pi, gemini, agy); ask which you
run; make `.venv` (or reuse it) and install `requirements.txt` (skipped when every requirement
is already installed, so a re-run works offline); then, under the venv's python, `python -m
src.init` (your files from the examples, never overwriting one), the first chosen harness with
a shipped adapter as `[harness] default` in `config/hunt.toml`, `python -m src.hunt doctor
--harness H` for each chosen harness, and the next step in that harness's own words.

It never renders per-user files: every harness's agent and command files are committed and the
same for everyone (`python -m src.hunt sync-agents`). The one opt-in outside the checkout is
codex's home skills folder (`~/.codex/skills/<name>/SKILL.md`, decision 4): one pointer file per
`/jh-*` command, each carrying `HOME_SKILL_MARK`; a file there without the mark is never
touched, and nothing else outside the checkout is written.

This module imports only the standard library at the top: it runs first under the system
python, before the venv and its packages exist. The second half (`finish`) runs under the
venv's python and imports the project there.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tomllib
from collections.abc import Callable, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# the installer's harness list (spec section 2): the shipped adapters plus gemini, which runs the
# hunt through the documented `[harness.gemini]` command template
HARNESSES: tuple[str, ...] = ("claude", "codex", "opencode", "pi", "gemini", "agy")
SHIPPED: tuple[str, ...] = ("claude", "codex", "opencode", "pi", "agy")
SLASH_COMMANDS: frozenset[str] = frozenset({"claude", "opencode", "gemini", "pi"})   # prompts.NATIVE_COMMANDS
HOME_SKILL_MARK = ("<!-- written by the jobhunt installer (python -m src.setup); "
                   "it updates or removes only files carrying this line -->")
VENV_PYTHON = Path(".venv") / "bin" / "python"
MIN_PYTHON = (3, 11)                     # setup.sh checks the system python against the same
_VERSION_CHECK = f"import sys; sys.exit(0 if sys.version_info >= {MIN_PYTHON} else 1)"

# argv, cwd, capture -> (exit code, captured output; "" when not captured)
Runner = Callable[[Sequence[str], Path, bool], tuple[int, str]]


def run_command(argv: Sequence[str], cwd: Path, capture: bool = True) -> tuple[int, str]:
    if not capture:
        return subprocess.run(list(argv), cwd=cwd, check=False).returncode, ""
    done = subprocess.run(list(argv), cwd=cwd, capture_output=True, text=True, check=False)
    return done.returncode, (done.stdout or "") + (done.stderr or "")


# Every requirement in requirements.txt installed, by distribution name (an offline re-run
# skips pip). Run under the venv's python with the file as argv[1].
_DEPS_CHECK = """
import importlib.metadata as m, re, sys
missing = []
for line in open(sys.argv[1], encoding="utf-8"):
    line = line.split("#", 1)[0].strip()
    if not line:
        continue
    name = re.split(r"[\\[<>=!~ ;]", line, maxsplit=1)[0]
    try:
        m.version(name)
    except m.PackageNotFoundError:
        missing.append(name)
print("missing: " + ", ".join(missing) if missing else "all installed")
sys.exit(1 if missing else 0)
"""


def detect(path: str | None = None) -> list[str]:
    """The harnesses whose binary is on PATH (`path` overrides the environment's)."""
    return [h for h in HARNESSES if shutil.which(h, path=path)]


def parse_harnesses(text: str) -> list[str]:
    names = [n.strip().lower() for n in text.replace(" ", ",").split(",") if n.strip()]
    unknown = [n for n in names if n not in HARNESSES]
    if unknown:
        raise ValueError(f"unknown harness {', '.join(unknown)} (known: {', '.join(HARNESSES)})")
    return list(dict.fromkeys(names))


def choose(found: list[str], harness: str | None, yes: bool, ask: Callable[[str], str]) -> list[str]:
    """`--harness` wins; `--yes` takes what is on PATH; otherwise one multi-select question."""
    if harness:
        return parse_harnesses(harness)
    if yes:
        return list(found)
    print("which agent CLIs do you use?")
    for h in HARNESSES:
        print(f"  [{'x' if h in found else ' '}] {h}{'  (on PATH)' if h in found else ''}")
    default = ", ".join(found) or "none"
    while True:
        answer = ask(f"names, comma separated (enter for: {default}): ").strip()
        if not answer:
            return list(found)
        try:
            return parse_harnesses(answer)
        except ValueError as e:
            print(e)


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def next_command(root: Path) -> str:
    """`/jh-setup` (the onboarding interview) once it exists, the first discovery until then."""
    return "jh-setup" if (root / "prompts" / "commands" / "jh-setup.md").exists() else "jh-discover"


def next_step(harness: str, command: str, home_skills: bool) -> str:
    """The next step in the harness's own words (decision 3)."""
    if harness in SLASH_COMMANDS:
        return f"open {harness} here and run /{command}"
    if harness == "codex" and home_skills:
        return f"open codex here and type ${command}"
    return f"open {harness} here and say: {command}   (AGENTS.md lists every flow)"


# --- the first half: system python, standard library only --------------------------------------

def install(found: list[str], chosen: list[str], home_skills: bool, root: Path = ROOT,
            runner: Runner = run_command, python: str = sys.executable) -> int:
    print(f"agent CLIs on PATH: {', '.join(found) or 'none'};  chosen: {', '.join(chosen) or 'none'}")
    venv_py = root / VENV_PYTHON
    if venv_py.exists():
        rc, _ = runner([str(venv_py), "-c", _VERSION_CHECK], root, True)
        if rc != 0:                      # an older clone's venv, or one whose python is gone
            need = ".".join(map(str, MIN_PYTHON))
            print(f"setup: .venv does not run python {need} or newer; remove it (rm -rf .venv) and re-run ./setup.sh")
            return 1
        print("venv: .venv (kept)")
    else:
        print("venv: creating .venv")
        rc, out = runner([python, "-m", "venv", ".venv"], root, True)
        if rc != 0:
            print(out.rstrip())
            print("setup: could not create .venv; nothing else was done")
            return 1
    rc, out = runner([str(venv_py), "-c", _DEPS_CHECK, "requirements.txt"], root, True)
    if rc == 0:
        print("deps: every requirement is installed (pip skipped)")
    else:
        print(f"deps: installing requirements.txt ({out.strip()})")
        rc, out = runner([str(venv_py), "-m", "pip", "install", "-r", "requirements.txt"], root, True)
        if rc != 0:
            print("\n".join(out.rstrip().splitlines()[-15:]))
            print("setup: pip failed (offline? a pin your python cannot build?); fix that and re-run ./setup.sh")
            return 1
    argv = [str(venv_py), "-m", "src.setup", "finish", "--harness", ",".join(chosen) or "none"]
    if home_skills:
        argv.append("--home-skills")
    rc, _ = runner(argv, root, False)
    return rc


# --- the second half: the venv's python, the project importable ---------------------------------

def write_home_skills(home: Path | None = None) -> tuple[list[str], list[str], list[str]]:
    """(written, unchanged, kept) for codex's home skills: one pointer per command. `kept` are
    files without HOME_SKILL_MARK: somebody else's, never overwritten."""
    from .hunt import prompts
    home = home or codex_home()
    written: list[str] = []
    same: list[str] = []
    kept: list[str] = []
    for cmd in prompts.load_commands().values():
        path = home / "skills" / cmd.name / "SKILL.md"
        text = prompts.render_home_skill(cmd)
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current is not None and HOME_SKILL_MARK not in current:
            kept.append(str(path))
        elif current == text:
            same.append(str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written.append(str(path))
    return written, same, kept


def finish(chosen: list[str], home_skills: bool, root: Path = ROOT, runner: Runner = run_command,
           hunt_toml: Path | None = None, home: Path | None = None, python: str = sys.executable) -> int:
    from .hunt import config as hunt_config
    rc, out = runner([python, "-m", "src.init"], root, True)
    print(out.rstrip())
    if rc != 0:
        print("setup: init failed; see above")
        return 1

    cfg = hunt_config.load(hunt_toml)
    default = next((h for h in chosen if h in SHIPPED), None)
    if default is None:
        print(f"default harness: {cfg.harness} (unchanged; none of {', '.join(chosen) or 'the chosen'} has a shipped adapter)")
    elif cfg.harness == default:
        print(f"default harness: {default} (already in config/hunt.toml)")
    else:
        hunt_config.set_default_harness(default, hunt_toml)
        print(f"default harness: {default} (config/hunt.toml, was {cfg.harness})")
        cfg = hunt_config.load(hunt_toml)

    if "codex" in chosen:
        if home_skills:
            written, same, kept = write_home_skills(home)
            where = (home or codex_home()) / "skills"
            print(f"codex home skills in {where}: {len(written)} written, {len(same)} unchanged"
                  + (f", {len(kept)} kept (not written by this installer): {', '.join(kept)}" if kept else ""))
        else:
            print("codex: AGENTS.md lists the flows; `./setup.sh --harness codex --home-skills` adds them as skills")

    failed = []
    for h in chosen:
        if h not in SHIPPED and h not in cfg.harness_templates:
            print(f"doctor {h}: skipped, no [harness.{h}] template in config/hunt.toml (docs/hunt-harnesses.md)")
            continue
        rc, out = runner([python, "-m", "src.hunt", "doctor", "--harness", h], root, True)
        if rc == 0:
            print(f"doctor {h}: ok")
        else:
            failed.append(h)
            print(f"doctor {h}: FAIL")
            print("\n".join("  " + line for line in out.rstrip().splitlines() if "FAIL" in line or "WARN" in line))
    if failed:
        print("  a model the harness does not list: pick one with `python -m src.hunt models --harness H`,"
              " then set it in the TUI settings (`,`) or config/hunt.toml")

    command = next_command(root)
    print()
    for i, h in enumerate(chosen):
        print(f"{'next' if i == 0 else 'also'}: {next_step(h, command, home_skills)}")
    if not chosen:
        print(f"next: open your agent CLI here and run /{command} (AGENTS.md lists every flow)")
    print("TUI: .venv/bin/python -m src.tui  (one word: scripts/install_launcher.sh);  schedule: docs/scheduling.md")
    return 0


# --- --check: report, write nothing, spend nothing ----------------------------------------------

def check(found: list[str], root: Path = ROOT, runner: Runner = run_command, home: Path | None = None) -> int:
    ok = True
    print(f"agent CLIs on PATH: {', '.join(found) or 'none'}")
    venv_py = root / VENV_PYTHON
    if not venv_py.exists():
        print("venv: missing (./setup.sh makes it)")
        ok = False
    else:
        rc, out = runner([str(venv_py), "-c", _DEPS_CHECK, "requirements.txt"], root, True)
        print(f"venv: .venv;  deps: {out.strip()}")
        ok &= rc == 0
        rc, out = runner([str(venv_py), "-m", "src.init", "--check"], root, True)
        print(out.rstrip())
        ok &= rc == 0
    try:
        raw = tomllib.loads((root / "config" / "hunt.toml").read_text(encoding="utf-8"))
        print(f"default harness: {raw.get('harness', {}).get('default', 'claude')} (config/hunt.toml)")
    except (OSError, tomllib.TOMLDecodeError) as e:
        print(f"default harness: unreadable config/hunt.toml ({e})")
        ok = False
    skills = sorted((home or codex_home()).glob("skills/jh-*/SKILL.md"))
    ours = [p for p in skills if HOME_SKILL_MARK in p.read_text(encoding="utf-8", errors="replace")]
    print(f"codex home skills: {len(ours)} from this installer" + (f", {len(skills) - len(ours)} not" if len(skills) > len(ours) else ""))
    print("doctor: not run by --check (it spends a smoke call); run `python -m src.hunt doctor --harness H`")
    return 0 if ok else 1


def main(argv: list[str] | None = None, ask: Callable[[str], str] = input) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    fin = sub.add_parser("finish", help=argparse.SUPPRESS)       # the second half, under the venv
    fin.add_argument("--harness", default="none")
    fin.add_argument("--home-skills", action="store_true")
    ap.add_argument("--harness", help=f"comma list from {', '.join(HARNESSES)}; skips the question")
    ap.add_argument("--yes", action="store_true", help="no questions: the CLIs found on PATH, no home skills")
    ap.add_argument("--check", action="store_true", help="report only; writes nothing, runs no doctor")
    ap.add_argument("--home-skills", action="store_true", help="also write codex's home skills (~/.codex/skills)")
    args = ap.parse_args(argv)

    if args.cmd == "finish":
        chosen = [] if args.harness == "none" else parse_harnesses(args.harness)
        return finish(chosen, args.home_skills)
    found = detect()
    if args.check:
        return check(found)

    def asked(question: str) -> str:
        try:
            return ask(question)
        except EOFError:                 # no one to answer (a pipe, CI, < /dev/null): the default
            print("(no answer on stdin; taking the default)")
            return ""

    try:
        chosen = choose(found, args.harness, args.yes, asked)
    except ValueError as e:
        print(f"setup: {e}")
        return 2
    home_skills = args.home_skills
    if "codex" in chosen and not home_skills and not args.yes and not args.harness:
        answer = asked(f"codex: also copy the /jh-* commands into {codex_home() / 'skills'} as skills? [y/N] ")
        home_skills = answer.strip().lower() in ("y", "yes")
    return install(found, chosen, home_skills)


if __name__ == "__main__":
    raise SystemExit(main())
