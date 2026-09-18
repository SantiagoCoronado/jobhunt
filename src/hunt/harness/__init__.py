"""Harness adapters (spec section 5): the one thing every agent CLI has in common is a
process that takes a prompt, a system prompt, a model and a tool allowlist and prints a JSON
envelope. An adapter builds that command line and reads that envelope; nothing else about a
harness leaks into the orchestrator. `claude` is the reference (this PR); codex, opencode, pi,
agy and the generic template arrive in PR 4.

Tools are named in the orchestrator's own vocabulary, `TOOLS` below, and each adapter maps them
to its flags: `bash` always means "python only", `web` is a capability a stage can require
(research) and a harness may not grant.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

TOOL_ORDER: tuple[str, ...] = ("read", "write", "edit", "bash", "web")
TOOLS: frozenset[str] = frozenset(TOOL_ORDER)


@dataclass(frozen=True)
class Invocation:
    prompt: str                        # user prompt: task line + contract (+ the role body on
    system: str                        # harnesses with no system-prompt flag)
    model: str | None                  # from hunt.toml; None = the harness default
    tools: frozenset[str]              # subset of TOOLS
    cwd: Path
    timeout_s: int
    schema: dict[str, Any] | None = None   # JSON schema when the reply itself is the output (inbox)


@dataclass(frozen=True)
class Usage:
    input: int | None = None
    output: int | None = None
    cache_read: int | None = None
    cache_create: int | None = None
    cost_usd: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Model:
    id: str
    note: str = ""


@dataclass(frozen=True)
class Result:
    """What `parse` makes of one finished process. `text` is the agent's final reply, logged
    and never parsed for a decision (decision 4); `error` is None on success; `rate_limited`
    is the decision 10 signal (a wait, not an attempt)."""
    usage: Usage
    error: str | None
    rate_limited: bool
    text: str | None
    envelope: bool = True              # False: the process died without printing one


class Harness(Protocol):
    name: str
    capabilities: frozenset[str]

    def argv(self, inv: Invocation) -> list[str]: ...
    def stdin(self, inv: Invocation) -> str | None: ...
    def parse(self, stdout: str, stderr: str, rc: int) -> Result: ...
    def models(self) -> list[Model] | None: ...


def get(name: str, **options: Any) -> Harness:
    """The adapter for a harness name; the shipped ones by name, anything else is PR 4's
    `[harness.<name>]` template (not yet) or unknown."""
    if name == "claude":
        from .claude import ClaudeHarness
        return ClaudeHarness(**options)
    raise ValueError(f"unknown harness '{name}' (shipped: claude)")


def check_tools(tools: frozenset[str] | set[str]) -> frozenset[str]:
    unknown = sorted(set(tools) - TOOLS)
    if unknown:
        raise ValueError(f"unknown tool(s) {', '.join(unknown)} (known: {', '.join(TOOL_ORDER)})")
    return frozenset(tools)
