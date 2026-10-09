"""The interview (docs/spec-pre-release.md PR 5 story 4): the golden transcript of /jh-setup
replayed against src.onboard on Alex Example's documents in a temp tree, and the command file
checked against the helper it drives (every call it names exists, every call the transcript
makes is in it, the token budget of decision 14)."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest
import yaml

from src import config, onboard
from src.hunt import prompts

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TRANSCRIPT = yaml.safe_load((FIXTURES / "onboard" / "transcript.yaml").read_text())
COMMAND = prompts.COMMANDS_DIR / "jh-setup.md"
TOKEN_BUDGET = 300_000                  # decision 14: a three-document intake under 0.3M tokens


class _Board:
    def __init__(self, n: int) -> None:
        self.status_code = 200
        self.n = n

    def json(self):
        return {"jobs": [{"id": i} for i in range(self.n)]}


@pytest.fixture
def tree(tmp_path, monkeypatch):
    """A fresh clone after `src.init`: the example copies, no .env, no database rows."""
    for key, name in (("profile", "profile.yaml"), ("master_resume", "master_resume.yaml"),
                      ("sources_local", "sources.local.yaml")):
        shutil.copyfile(FIXTURES / name, tmp_path / name)
        monkeypatch.setitem(config.USER_FILES, key, tmp_path / name)
    monkeypatch.setattr(onboard, "ONBOARD_DIR", tmp_path / "onboard")
    for key in ("ADZUNA_APP_ID", "ADZUNA_APP_KEY", "FINDWORK_TOKEN", "CAREERJET_AFFID", "THEMUSE_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    boards = TRANSCRIPT["boards"]
    monkeypatch.setattr(onboard, "_get", lambda url, params: _Board(boards[url.rstrip("/").split("/")[-2]]))
    return tmp_path


def _payload(raw):
    if isinstance(raw, dict) and "resume_from" in raw:
        data = yaml.safe_load((FIXTURES / raw["resume_from"]).read_text())
        data.pop("design", None)
        return {**data, "provenance": raw["provenance"]}
    return raw


def test_the_golden_transcript_replays(tree, capsys):
    for step in TRANSCRIPT["steps"]:
        if "payload" in step:                                  # the agent writes the payload file first
            (tree / "onboard").mkdir(exist_ok=True)
            (tree / "onboard" / Path(step["args"][-1]).name).write_text(json.dumps(_payload(step["payload"])))
        args = [a.format(fixtures=FIXTURES, onboard=tree / "onboard") for a in step["args"]]
        rc = onboard.main(args)
        out = capsys.readouterr().out
        assert rc == step.get("rc", 0), f"{step['say']}: exit {rc}\n{out}"
        for want in step["out"]:
            assert want in out, f"{step['say']}: {want!r} not in\n{out}"
        for secret in step.get("never", []):
            assert secret not in out, f"{step['say']} printed a value"
    # what the transcript left behind is a working setup
    assert onboard.main(["check", "resume"]) == 0 and onboard.main(["check", "profile"]) == 0
    assert config.sources()["greenhouse"]["tokens"] == ["ledgerly"]
    assert config.get_secret("ADZUNA_APP_KEY") == "alex-app-key"
    for path in (tree / "master_resume.yaml", tree / "profile.yaml", tree / "sources.local.yaml", config.ENV_PATH):
        assert "—" not in path.read_text(), path


def test_the_intake_fits_the_token_budget(tree, capsys):
    onboard.main(["extract", str(FIXTURES / "onboard" / "alex-example-resume.pdf"),
                  str(FIXTURES / "onboard" / "alex-example-resume.docx")])
    docs = onboard.load_manifest()
    command = len(COMMAND.read_text()) // 4
    profile = len((FIXTURES / "profile.yaml").read_text()) // 4
    read_once = sum(d.tokens for d in docs) + command + profile
    assert read_once < TOKEN_BUDGET // 10                     # what is read leaves room for the chat itself
    assert all(not d.large for d in docs)


def _commands_in_prompt() -> set[str]:
    return set(re.findall(r"python -m src\.onboard ([a-z-]+)", COMMAND.read_text()))


def test_every_helper_call_the_command_names_exists_and_the_transcript_uses_them():
    import argparse

    parser_cmds: set[str] = set()
    orig = argparse.ArgumentParser.parse_args

    def capture(self, args=None, namespace=None):
        for action in self._actions:
            if isinstance(action, argparse._SubParsersAction):
                parser_cmds.update(action.choices)
        raise SystemExit(0)

    argparse.ArgumentParser.parse_args = capture  # type: ignore[method-assign]
    try:
        with pytest.raises(SystemExit):
            onboard.main([])
    finally:
        argparse.ArgumentParser.parse_args = orig  # type: ignore[method-assign]
    named = _commands_in_prompt()
    assert named <= parser_cmds, named - parser_cmds
    replayed = {s["args"][0] for s in TRANSCRIPT["steps"]}
    assert replayed <= named, replayed - named
    for what in ("resume", "profile", "sources", "env", "dream"):
        assert f"python -m src.onboard write {what}" in COMMAND.read_text(), what


def test_the_command_is_harness_neutral_and_plain():
    cmd = prompts.parse_command(COMMAND)
    body = cmd.body
    for word in ("Bash tool", "Agent tool", "Task tool", "Glob", "run_in_background", "CLAUDE_PROJECT_DIR"):
        assert word not in body, word
    assert "your shell tool" in body
    assert "—" not in body and "docs/writing-voice.md" in body
    assert "provenance" in body and "never a guess" in body
    assert cmd.tools == ("read", "write", "bash")
