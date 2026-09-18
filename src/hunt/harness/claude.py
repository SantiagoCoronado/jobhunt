"""The claude adapter (reference harness), verified against `claude --help` 2.1.276 on
2026-09-18 with one real call each way:

- the prompt goes on STDIN: `--allowedTools` and `--tools` are variadic and swallow a trailing
  prompt argument;
- `--bare` reads only ANTHROPIC_API_KEY (OAuth and the keychain are never read), so a
  subscription login fails with `terminal_reason: api_error`, "Not logged in". It is passed
  only when that variable is set; without it the run uses the normal login and pays for the
  hooks, plugin and CLAUDE.md discovery it would have skipped;
- `--tools` restricts the built-in set (an ungranted tool does not exist for the model) and
  `--allowedTools` pre-approves the granted ones; `--permission-prompts none` denies anything
  that would still prompt instead of hanging a headless run;
- `--no-session-persistence` and `--strict-mcp-config`: no session store, no MCP servers.

The envelope (`--output-format json`) is one JSON object: `usage.{input_tokens,output_tokens,
cache_read_input_tokens,cache_creation_input_tokens}`, `total_cost_usd`, `is_error`,
`terminal_reason`, `api_error_status`, `result` (the reply text). The CLI has no model
catalog: `models()` is None and validation is the smoke prompt (story 6, decision 6).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from . import TOOL_ORDER, Invocation, Model, Result, Usage, check_tools

_TOOL_NAMES: dict[str, list[str]] = {
    "read": ["Read"], "write": ["Write"], "edit": ["Edit"], "bash": ["Bash"], "web": ["WebSearch", "WebFetch"],
}
_ALLOWED: dict[str, list[str]] = {
    "read": ["Read"], "write": ["Write"], "edit": ["Edit"],
    "bash": ["Bash(python:*)", "Bash(.venv/bin/python:*)"],       # bash means "python only"
    "web": ["WebSearch", "WebFetch"],
}
_RATE_LIMIT = re.compile(r"rate.?limit|too many requests|overloaded|usage limit|\b429\b|\b529\b", re.I)
_ALIAS = re.compile(r"'([a-z][a-z0-9-]*)'")

SMOKE_PROMPT = "Reply with the single word ok"
SMOKE_SYSTEM = "You are a smoke test."


class ClaudeHarness:
    name = "claude"
    capabilities: frozenset[str] = frozenset(TOOL_ORDER)

    def __init__(self, binary: str = "claude", bare: bool | None = None):
        self.binary = binary
        self._bare = bare

    @property
    def bare(self) -> bool:
        """`--bare` only where it can authenticate: an API key in the environment."""
        if self._bare is not None:
            return self._bare
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    def argv(self, inv: Invocation) -> list[str]:
        tools = check_tools(inv.tools)
        argv = [self.binary, "-p"]
        if self.bare:
            argv.append("--bare")
        argv += ["--output-format", "json", "--no-session-persistence", "--strict-mcp-config",
                 "--permission-mode", "acceptEdits", "--permission-prompts", "none"]
        if inv.model:
            argv += ["--model", inv.model]
        argv += ["--system-prompt", inv.system]
        names = [n for t in TOOL_ORDER if t in tools for n in _TOOL_NAMES[t]]
        argv += ["--tools", ",".join(names)]                 # "" disables every built-in tool
        allowed = [a for t in TOOL_ORDER if t in tools for a in _ALLOWED[t]]
        if allowed:
            argv += ["--allowedTools", *allowed]
        if inv.schema is not None:
            argv += ["--json-schema", json.dumps(inv.schema, separators=(",", ":"))]
        return argv

    def stdin(self, inv: Invocation) -> str | None:
        return inv.prompt

    def parse(self, stdout: str, stderr: str, rc: int) -> Result:
        text_out = stdout.strip()
        try:
            data = json.loads(text_out) if text_out else None
        except json.JSONDecodeError:
            data = None
        if not isinstance(data, dict):
            tail = (stderr.strip() or text_out)[-300:]
            return Result(Usage(), f"exit {rc}, no JSON envelope: {tail or 'empty output'}",
                          bool(_RATE_LIMIT.search(tail)), None)
        u: dict[str, Any] = data.get("usage") or {}
        usage = Usage(input=u.get("input_tokens"), output=u.get("output_tokens"),
                      cache_read=u.get("cache_read_input_tokens"), cache_create=u.get("cache_creation_input_tokens"),
                      cost_usd=data.get("total_cost_usd"))
        text = data.get("result") if isinstance(data.get("result"), str) else None
        status = data.get("api_error_status")
        envelope_error = bool(data.get("is_error")) or data.get("subtype") not in (None, "success")
        failed = envelope_error or rc != 0
        error = None
        if failed:
            reason = data.get("terminal_reason") or data.get("subtype") or f"exit {rc}"
            # an error envelope explains itself in `result`; a bad exit under a clean envelope
            # can only be explained by stderr, never by the reply text
            detail = (text if envelope_error else None) or stderr.strip() or ""
            detail = detail[:200]
            error = f"{reason}{f' ({status})' if status else ''}: {detail}" if detail else f"{reason} (exit {rc})"
        rate_limited = failed and (status in (429, 529) or bool(_RATE_LIMIT.search(f"{text or ''} {stderr}")))
        return Result(usage, error, rate_limited, text)

    def models(self) -> list[Model] | None:
        """No catalog on this CLI (spec section 5); the aliases are display only."""
        return None

    def aliases(self, help_text: str | None = None) -> list[str]:
        """The rolling aliases `claude --help` names under --model ('fable', 'opus', ...)."""
        if help_text is None:
            try:
                help_text = subprocess.run([self.binary, "--help"], capture_output=True, text=True,
                                           timeout=30, check=False).stdout
            except (OSError, subprocess.TimeoutExpired):
                return []
        m = re.search(r"--model <model>(.*?)(?:\n\s+-|\n\s+--)", help_text, re.S)
        block = m.group(1) if m else ""
        out: list[str] = []
        for a in _ALIAS.findall(block):
            if "-" not in a and a not in out:               # aliases, not full ids like claude-fable-5
                out.append(a)
        return out

    def smoke(self, model: str | None, cwd: Path) -> Invocation:
        """The 10-token call `doctor` and the pre-run check make per configured model."""
        return Invocation(prompt=SMOKE_PROMPT, system=SMOKE_SYSTEM, model=model, tools=frozenset(),
                          cwd=cwd, timeout_s=60)
