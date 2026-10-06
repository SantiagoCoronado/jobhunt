"""Story 8 of docs/spec-hunt-orchestrator.md PR 3, locked: /jh-hunt is a Bash-only viewer over
the orchestrator, the single-use commands
point at the batch path, and CLAUDE.md names no step the skill no longer has."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS = ROOT / ".claude" / "commands"


def _command(name: str) -> tuple[dict, str]:
    text = (COMMANDS / name).read_text(encoding="utf-8")
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
    assert m, f"{name}: no frontmatter"
    # `key: value` per line, split once: descriptions carry colons, so this is not strict YAML
    front = dict((k.strip(), v.strip()) for k, v in (line.split(":", 1) for line in m.group(1).splitlines() if ":" in line))
    return front, m.group(2)


def test_jh_hunt_is_a_bash_only_viewer_over_the_orchestrator():
    front, body = _command("jh-hunt.md")
    assert front["allowed-tools"] == "Bash"
    for needed in ("python -m src.hunt run", "run_in_background", "python -m src.hunt run --resume latest",
                   "python -m src.hunt status latest", "python -m src.hunt report latest", "needs_human"):
        assert needed in body, needed
    # it drives nothing itself: none of the prose flow's own steps survive
    for gone in ("subagent", "sub-agent", "src.match export", "src.triage export", "src.tailor_bundle", "src.mail_fetch",
                 "src.pick", "token_audit"):
        assert gone not in body, gone
    assert "No Agent calls, no Workflow" in body and "\u2014" not in body


def test_single_use_commands_point_at_the_batch_path():
    for name, stage in (("jh-triage.md", "triage"), ("jh-match.md", "match"), ("jh-research.md", "research"),
                        ("jh-tailor.md", "tailor"), ("jh-gmail-sync.md", "inbox")):
        assert f"python -m src.hunt run --only {stage}" in _command(name)[1], name


def test_claude_md_describes_the_orchestrator_and_no_step_of_the_old_flow():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert not re.search(r"/jh-hunt`?\s+step\s+\d", text)
    for needed in ("python -m src.hunt run", "run --resume RUN|latest", "hunt run --to match", "data/hunt/<run_id>/", "needs_human"):
        assert needed in text, needed
