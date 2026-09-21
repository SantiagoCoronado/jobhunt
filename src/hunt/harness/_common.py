"""What the event-stream adapters share (codex, opencode, pi print JSON lines, not one
object): reading the lines, the rate-limit wording, the "no envelope" result, a catalog
command, and the one prompt a harness with no system-prompt flag gets."""
from __future__ import annotations

import json
import re
import subprocess
from typing import Any

from . import Invocation, Result, Usage

RATE_LIMIT = re.compile(r"rate.?limit|too many requests|overloaded|usage limit|quota|\b429\b|\b529\b", re.I)

SMOKE_PROMPT = "Reply with the single word ok"
SMOKE_SYSTEM = "You are a smoke test."


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
