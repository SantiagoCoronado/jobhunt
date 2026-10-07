"""The commands over the orchestrator, locked (story 8 of docs/spec-hunt-orchestrator.md PR 3,
then decision 5 of docs/spec-pre-release.md): /jh-hunt, /jh-triage and /jh-match are shell-only
viewers of `python -m src.hunt run`; /jh-research, /jh-tailor and /jh-gmail-sync keep their
single-unit shape and name "the <role> agent"; no command names a fan-out feature of one
harness; CLAUDE.md names no step the skill no longer has. The sources in prompts/commands/ are
what is checked; the renders follow them (tests/test_hunt_prompts.py)."""
from __future__ import annotations

import re
from pathlib import Path

from src.hunt import prompts

ROOT = Path(__file__).resolve().parent.parent


def _body(name: str) -> str:
    """The command's body with its line wraps undone, so a phrase is found across a wrap."""
    return " ".join(prompts.load_commands()[name].body.split())


def test_fan_out_commands_are_shell_only_viewers_over_the_orchestrator():
    for name, run in (("jh-hunt", "python -m src.hunt run"), ("jh-triage", "python -m src.hunt run --only triage"),
                      ("jh-match", "python -m src.hunt run --only match")):
        assert prompts.load_commands()[name].tools == ("bash",), name
        body = _body(name)
        for needed in (run, "python -m src.hunt run --resume latest", "python -m src.hunt status latest",
                       "python -m src.hunt report latest", "in the background"):
            assert needed in body, (name, needed)
        # it drives nothing itself: none of the prose flow's own steps survive
        for gone in ("subagent", "sub-agent", "Workflow", "src.match export", "src.triage export", "src.triage ingest",
                     "src.tailor_bundle", "src.mail_fetch", "src.pick", "token_audit", "Haiku", "run_in_background"):
            assert gone not in body, (name, gone)
        assert "\u2014" not in body
    assert "needs_human" in _body("jh-hunt")


def test_single_unit_commands_name_the_role_agent_and_point_at_the_batch_path():
    for name, stage, role in (("jh-research", "research", "company-researcher"), ("jh-tailor", "tailor", "resume-tailor"),
                              ("jh-gmail-sync", "inbox", "inbox-classifier")):
        body = _body(name)
        assert f"python -m src.hunt run --only {stage}" in body, name
        assert f"**{role}** agent (your harness's native agent file supplies its" in body, name
        for gone in ("subagent", "sub-agent", 'model: "fable"', "Workflow"):
            assert gone not in body, (name, gone)
    # the session never holds the manifest: the agent prints it page by page
    body = _body("jh-gmail-sync")
    assert "python -m src.mail_fetch --summary" in body and "manifest --page N" in body


def test_claude_md_describes_the_orchestrator_and_no_step_of_the_old_flow():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert not re.search(r"/jh-hunt`?\s+step\s+\d", text)
    for needed in ("python -m src.hunt run", "run --resume RUN|latest", "data/hunt/<run_id>/", "needs_human",
                   "run --only triage", "run --only match"):
        assert needed in text, needed
