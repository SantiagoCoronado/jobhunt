"""The pi adapter, against `pi --help` 0.85.1 and two real calls on 2026-09-21 (a bare smoke
prompt, and a read probe on a rolling model id with the prompt on stdin):

    pi -p --mode json --no-session --no-context-files --no-skills --no-prompt-templates
       --no-approve [--model {provider/id}] --system-prompt {system}
       (--tools read,write,edit,bash | --no-tools)

- the prompt goes on STDIN: an argument that starts with `@` is a file to attach and one that
  starts with `-` is an option, and a unit prompt is not ours to constrain;
- `--model` takes `provider/id`, which is how `models()` lists them, so there is no separate
  `--provider`; a rolling id keeps its own slash (`openrouter/~anthropic/claude-haiku-latest`
  answered);
- `--tools` is an allowlist over built-in AND extension tools, `--no-tools` for a unit with
  none. pi has no web tool, and `bash` cannot be narrowed to "python only" by a flag;
- the role body is the system prompt, so AGENTS.md / CLAUDE.md discovery, skills, prompt
  templates and project-local files are switched off (`--no-approve` also means no trust
  question can be asked). Extensions stay on: a provider may come from one.

Events (`--mode json`, one object per line): `session`, `agent_start`, `turn_start`,
`message_start` / `message_update` (streaming), `message_end` {message: {role, content:
[{type: text | thinking | toolCall, ...}], provider, model, usage: {input, output, cacheRead,
cacheWrite, reasoning, cost: {total}}, stopReason, errorMessage?}}, `tool_execution_start` /
`_end`, `turn_end`, `agent_end`, `agent_settled`. One assistant `message_end` PER TURN, so
usage is the sum; `output` already counts `reasoning`. The reply is the text of the last
assistant message. A failed call is `stopReason: "error"` (or "aborted") with `errorMessage`.
A model it does not know is no stream at all: exit 1 and `Error: Model "x" not found` on
stderr.

Catalog: `pi --list-models`, a table of `provider  model  context  max-out  thinking  images`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import TOOL_ORDER, Invocation, Model, Result, Usage
from ._common import RATE_LIMIT, SMOKE_PROMPT, SMOKE_SYSTEM, as_object, events, granted, no_envelope, run_catalog, table

_FAILED_STOPS = frozenset({"error", "aborted"})


class PiHarness:
    name = "pi"
    capabilities: frozenset[str] = frozenset({"read", "write", "edit", "bash"})

    def __init__(self, binary: str = "pi"):
        self.binary = binary

    def version_argv(self) -> list[str]:
        return [self.binary, "--version"]

    def argv(self, inv: Invocation) -> list[str]:
        tools = granted(self.name, inv.tools, self.capabilities)
        argv = [self.binary, "-p", "--mode", "json", "--no-session", "--no-context-files", "--no-skills",
                "--no-prompt-templates", "--no-approve"]
        if inv.model:
            argv += ["--model", inv.model]
        argv += ["--system-prompt", inv.system]
        names = [t for t in TOOL_ORDER if t in tools]
        return [*argv, *(["--tools", ",".join(names)] if names else ["--no-tools"])]

    def stdin(self, inv: Invocation) -> str | None:
        return inv.prompt

    def parse(self, stdout: str, stderr: str, rc: int) -> Result:
        evs = events(stdout)
        if not evs:
            return no_envelope(stdout, stderr, rc)
        text, error, answered = None, None, False
        totals: dict[str, float] = {}
        for ev in evs:
            message = table(ev.get("message"))
            if ev.get("type") != "message_end" or message.get("role") != "assistant":
                continue
            answered = True
            _add(totals, table(message.get("usage")))
            parts = [c.get("text") for c in message.get("content") or [] if isinstance(c, dict) and c.get("type") == "text"]
            said = "".join(p for p in parts if isinstance(p, str)).strip()
            text = said or text
            if message.get("stopReason") in _FAILED_STOPS:
                error = f"{message['stopReason']}: {str(message.get('errorMessage') or '')[:200]}".rstrip(": ")
            else:
                error = None                                   # a later turn that answered clears an earlier failed one
        if error is None and (rc != 0 or not answered):
            detail = stderr.strip()[:200]
            error = f"exit {rc}: {detail}" if detail else f"no assistant message (exit {rc})"
        usage = Usage(input=_int(totals, "input"), output=_int(totals, "output"), cache_read=_int(totals, "cacheRead"),
                      cache_create=_int(totals, "cacheWrite"), cost_usd=totals.get("cost")) if answered else Usage()
        rate_limited = error is not None and bool(RATE_LIMIT.search(f"{error} {stderr[-500:]}"))
        return Result(usage, error, rate_limited, text, structured=as_object(text))

    def models(self) -> list[Model] | None:
        cp = run_catalog([self.binary, "--list-models"])
        if cp.returncode != 0:
            raise ValueError(f"`pi --list-models` exit {cp.returncode}: {(cp.stderr.strip() or cp.stdout.strip())[:160]}")
        out: list[Model] = []
        for line in cp.stdout.splitlines():
            cols = line.split()
            if len(cols) < 2 or cols[:2] == ["provider", "model"]:
                continue
            note = " ".join(f"{k} {v}" for k, v in zip(("context", "max-out", "thinking", "images"), cols[2:], strict=False))
            out.append(Model(f"{cols[0]}/{cols[1]}", note))
        return out

    def smoke(self, model: str | None, cwd: Path) -> Invocation:
        return Invocation(prompt=SMOKE_PROMPT, system=SMOKE_SYSTEM, model=model, tools=frozenset(), cwd=cwd, timeout_s=120)


def _add(totals: dict[str, float], usage: dict[str, Any]) -> None:
    for key in ("input", "output", "cacheRead", "cacheWrite"):
        value = usage.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            totals[key] = totals.get(key, 0) + value
    cost = table(usage.get("cost")).get("total")
    if isinstance(cost, (int, float)) and not isinstance(cost, bool):
        totals["cost"] = totals.get("cost", 0) + cost


def _int(totals: dict[str, float], key: str) -> int | None:
    return int(totals[key]) if key in totals else None
