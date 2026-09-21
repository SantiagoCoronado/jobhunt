"""The opencode adapter, against `opencode run --help` 1.18.29 and two real calls on
2026-09-21 (a bare smoke prompt, and a probe agent that was granted read and refused a write):

    opencode run --format json [-m {provider/model}] [--agent {role}] {prompt}

- `run` has no tool flags: the generated agent file (`.opencode/agents/<role>.md`, written by
  `sync-agents`, `prompts.render_opencode`) carries the permissions and the role body, and
  `--agent` is what applies them. So a unit's prompt is the task alone; the body is not sent
  twice. A call with no role (the smoke prompt, the doctor probe) runs on opencode's default
  agent with the system text prepended;
- a tool call the agent file refuses comes back to the model as an error ("The user has
  specified a rule which prevents you from using this specific tool call"); nothing prompts,
  nothing hangs. `--auto` is never passed;
- there is no schema flag: a schema unit gets the schema in its prompt, and the reply is
  read as the object when it parses as one;
- the prompt is an argument (`message..`), stdin is not read;
- `web`: `webfetch` is always there, but the `websearch` tool exists only on the opencode
  provider or with OPENCODE_ENABLE_EXA set, and a dossier needs search, so `web` is claimed
  only with that variable in the environment.

Events (`--format json`, one object per line): `step_start`; `tool_use` {part: {tool, state:
{status, output | error}}}; `text` {part: {text}}; `step_finish` {part: {reason, tokens:
{input, output, reasoning, cache: {read, write}}, cost}}, ONE PER STEP, so usage is the sum;
`error` {error: {name, data: {message}}} with exit 1 (seen for a model it does not know).
The reply is the last `text` part. Reasoning tokens are billed as output and counted there.

Catalog: `opencode models`, one `provider/model` per line.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from . import Invocation, Model, Result, Usage, check_tools
from ._common import RATE_LIMIT, SCHEMA_LINE, SMOKE_PROMPT, SMOKE_SYSTEM, as_object, events, no_envelope, one_prompt, run_catalog, table


class OpencodeHarness:
    name = "opencode"

    def __init__(self, binary: str = "opencode", web: bool | None = None):
        self.binary = binary
        has_search = bool(os.environ.get("OPENCODE_ENABLE_EXA")) if web is None else web
        self.capabilities: frozenset[str] = frozenset({"read", "write", "edit", "bash"} | ({"web"} if has_search else set()))

    def version_argv(self) -> list[str]:
        return [self.binary, "--version"]

    def argv(self, inv: Invocation) -> list[str]:
        check_tools(inv.tools)
        argv = [self.binary, "run", "--format", "json"]
        if inv.model:
            argv += ["-m", inv.model]
        if inv.role:
            argv += ["--agent", inv.role]
        prompt = inv.prompt if inv.role else one_prompt(inv)
        if inv.schema is not None:
            prompt = f"{prompt.rstrip()}\n\n{SCHEMA_LINE}\n{json.dumps(inv.schema, separators=(',', ':'))}\n"
        return [*argv, prompt]

    def stdin(self, inv: Invocation) -> str | None:
        return None

    def parse(self, stdout: str, stderr: str, rc: int) -> Result:
        evs = events(stdout)
        if not evs:
            return no_envelope(stdout, stderr, rc)
        text, error, finished = None, None, False
        totals: dict[str, float] = {}
        for ev in evs:
            kind = ev.get("type")
            part = table(ev.get("part"))
            if kind == "text" and isinstance(part.get("text"), str) and part["text"].strip():
                text = part["text"].strip()
            elif kind == "step_finish":
                finished = True
                _add(totals, part)
            elif kind == "error":
                err = table(ev.get("error"))
                data = table(err.get("data"))
                error = f"{err.get('name') or 'error'}: {str(data.get('message') or '')[:200]}".rstrip(": ")
        if error is None and (rc != 0 or not finished):
            detail = stderr.strip()[:200]
            error = f"exit {rc}: {detail}" if detail else f"no finished step (exit {rc})"
        usage = Usage(input=_int(totals, "input"), output=_int(totals, "output"), cache_read=_int(totals, "cache_read"),
                      cache_create=_int(totals, "cache_create"), cost_usd=totals.get("cost")) if finished else Usage()
        rate_limited = error is not None and bool(RATE_LIMIT.search(f"{error} {stderr[-500:]}"))
        return Result(usage, error, rate_limited, text, structured=as_object(text))

    def models(self) -> list[Model] | None:
        cp = run_catalog([self.binary, "models"])
        if cp.returncode != 0:
            raise ValueError(f"`opencode models` exit {cp.returncode}: {(cp.stderr.strip() or cp.stdout.strip())[:160]}")
        ids = [ln.strip() for ln in cp.stdout.splitlines() if "/" in ln and " " not in ln.strip()]
        return [Model(i, i.split("/", 1)[0]) for i in ids]

    def smoke(self, model: str | None, cwd: Path) -> Invocation:
        return Invocation(prompt=SMOKE_PROMPT, system=SMOKE_SYSTEM, model=model, tools=frozenset(), cwd=cwd, timeout_s=120)


def _add(totals: dict[str, float], part: dict[str, Any]) -> None:
    tokens = table(part.get("tokens"))
    cache = table(tokens.get("cache"))
    for key, value in (("input", tokens.get("input")), ("output", tokens.get("output")),
                       ("output", tokens.get("reasoning")), ("cache_read", cache.get("read")),
                       ("cache_create", cache.get("write")), ("cost", part.get("cost"))):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            totals[key] = totals.get(key, 0) + value


def _int(totals: dict[str, float], key: str) -> int | None:
    return int(totals[key]) if key in totals else None
