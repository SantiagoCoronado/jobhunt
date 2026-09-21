"""What the event-stream adapters share (codex, opencode, pi print JSON lines, not one
object): reading the lines, the rate-limit wording, the "no envelope" result, a catalog
command, and the one prompt a harness with no system-prompt flag gets."""
from __future__ import annotations

import json
import re
import subprocess
from typing import Any

from . import Invocation, Result, Usage, check_tools

RATE_LIMIT = re.compile(r"rate.?limit|too many requests|overloaded|usage limit|quota|\b429\b|\b529\b", re.I)

SMOKE_PROMPT = "Reply with the single word ok"
SMOKE_SYSTEM = "You are a smoke test."
# for a harness with no schema flag: the schema rides in the prompt and the reply is read as the object
SCHEMA_LINE = "Return only one JSON object that validates against this JSON schema, with no prose and no code fence:"


def events(stdout: str) -> list[dict[str, Any]]:
    """Every line of `stdout` that is a JSON object; anything else (a banner, a warning that
    went to stdout) is skipped, never an error."""
    out: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            out.append(data)
    return out


def last_object(stdout: str) -> dict[str, Any] | None:
    """The one JSON object a single-envelope CLI prints: all of stdout, or the last line that
    is one when a banner came first."""
    text = stdout.strip()
    for candidate in (text, *reversed(text.splitlines())):
        candidate = candidate.strip()
        if not candidate.startswith("{"):
            continue
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return None


def table(value: Any) -> dict[str, Any]:
    """`value` when it is a JSON object, else an empty one: event fields are never trusted."""
    return value if isinstance(value, dict) else {}


def granted(name: str, tools: frozenset[str] | set[str], capabilities: frozenset[str]) -> frozenset[str]:
    """The unit's tools, refused by name when the harness cannot grant one: dropping `web`
    in silence would run a research unit that can never pass its check. `fan.resolve_harness`
    routes a stage before this can happen; this is the adapter saying so itself."""
    tools = check_tools(tools)
    lacking = sorted(tools - capabilities)
    if lacking:
        raise ValueError(f"{name} grants no {', '.join(lacking)} tool; run this stage on a harness that does")
    return tools


def no_envelope(stdout: str, stderr: str, rc: int, what: str = "JSON events") -> Result:
    tail = (stderr.strip() or stdout.strip())[-300:]
    return Result(Usage(), f"exit {rc}, no {what}: {tail or 'empty output'}", bool(RATE_LIMIT.search(tail)),
                  None, envelope=False)


def as_object(text: str | None) -> Any:
    """A schema-constrained reply as the object it is, None when the text is not one."""
    if not text:
        return None
    try:
        data = json.loads(text.strip())
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def one_prompt(inv: Invocation) -> str:
    """The role body and the task as one prompt, for a harness with no system-prompt flag
    (spec section 4, "Unit prompt": prepended to the user prompt)."""
    system = inv.system.strip()
    return f"{system}\n\n{inv.prompt}" if system else inv.prompt


def run_catalog(argv: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    """The harness's own list command. OSError and TimeoutExpired reach `doctor.catalog`,
    which turns them into the reason the catalog could not be read."""
    return subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=timeout, check=False)
