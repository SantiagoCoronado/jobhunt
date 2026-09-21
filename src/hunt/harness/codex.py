"""The codex adapter, against `codex exec --help` 0.153.4 on 2026-09-21:

    codex exec --json -o {last_msg} [-m {model}] --sandbox {mode} [--output-schema {file}]
               --ephemeral --skip-git-repo-check -

- no system-prompt flag: the role body is prepended to the task and the whole prompt goes on
  STDIN (`-`); with a prompt argument and a closed stdin codex still prints "Reading
  additional input from stdin";
- no tool allowlist either, the sandbox is the grant: `workspace-write` when the unit may
  write, edit or run python, `read-only` otherwise. `bash` cannot be narrowed to "python only"
  by a flag here (that is an execpolicy `.rules` file, the user's to write);
- `exec` never asks for approval, so nothing can hang on a prompt;
- `--output-schema` takes a FILE, so `argv` writes the schema under `scratch` (named by its
  hash, so the same schema is one file). `-o` lands beside it, named by the prompt's hash, for
  a human re-running a unit; the parser reads the same final message from the event stream,
  because `parse` is never told which invocation it is reading;
- `web` is not claimed: `browser_use` is on in `codex features list`, but no headless call
  could be verified here (the install is not logged in), so research falls back to a harness
  that grants it (spec section 5).

Events (`--json`, one JSON object per line). Seen on a real failed call: `thread.started`,
`turn.started`, `error` {message} (also the transient "Reconnecting... 2/5" lines),
`item.completed` {item: {type: "error", message}}, `turn.failed` {error: {message}}, exit 1.
From the CLI's documented stream, not yet seen on a successful call here: `item.completed`
{item: {type: "agent_message", text}} and `turn.completed` {usage: {input_tokens,
cached_input_tokens, output_tokens}}; `input_tokens` counts the cached ones, so they are
taken out to match `Usage.input` on the other adapters. No cost is reported.

Catalog: `codex debug models` prints {"models": [{slug, display_name, visibility, ...}]} and
answers without a login.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from . import Invocation, Model, Result, Usage, check_tools
from ._common import RATE_LIMIT, SMOKE_PROMPT, SMOKE_SYSTEM, as_object, events, no_envelope, one_prompt, run_catalog, table

_WRITES = frozenset({"write", "edit", "bash"})


def _key(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


class CodexHarness:
    name = "codex"
    capabilities: frozenset[str] = frozenset({"read", "write", "edit", "bash"})

    def __init__(self, binary: str = "codex", scratch: Path | None = None):
        self.binary = binary
        self.scratch = scratch or Path(tempfile.gettempdir()) / "jobhunt-hunt-codex"

    def version_argv(self) -> list[str]:
        return [self.binary, "--version"]

    def argv(self, inv: Invocation) -> list[str]:
        tools = check_tools(inv.tools)
        self.scratch.mkdir(parents=True, exist_ok=True)
        last = self.scratch / f"last_{_key(f'{inv.model}|{self.stdin(inv)}')}.txt"
        argv = [self.binary, "exec", "--json", "-o", str(last)]
        if inv.model:
            argv += ["-m", inv.model]
        argv += ["--sandbox", "workspace-write" if tools & _WRITES else "read-only"]
        if inv.schema is not None:
            text = json.dumps(inv.schema, separators=(",", ":"))
            schema = self.scratch / f"schema_{_key(text)}.json"
            schema.write_text(text, encoding="utf-8")
            argv += ["--output-schema", str(schema)]
        return [*argv, "--ephemeral", "--skip-git-repo-check", "-"]

    def stdin(self, inv: Invocation) -> str | None:
        return one_prompt(inv)

    def parse(self, stdout: str, stderr: str, rc: int) -> Result:
        evs = events(stdout)
        if not evs:
            return no_envelope(stdout, stderr, rc)
        usage, text, failed, last_error, completed = Usage(), None, None, None, False
        for ev in evs:
            kind = ev.get("type")
            item = table(ev.get("item"))
            if kind == "turn.completed":
                completed = True
                usage = _usage(table(ev.get("usage")))
            elif kind == "turn.failed":
                failed = str(table(ev.get("error")).get("message") or "turn failed")
            elif kind == "error":
                last_error = str(ev.get("message") or "error")
            elif kind == "item.completed" and item.get("type") == "agent_message" and isinstance(item.get("text"), str):
                text = item["text"]
        error = None
        if failed is not None:
            error = f"turn failed: {failed[:200]}"
        elif rc != 0 or not completed:
            # the "Reconnecting..." error lines are transient; they only explain a run that
            # never completed a turn
            detail = (last_error or stderr.strip())[:200]
            error = f"exit {rc}: {detail}" if detail else f"no completed turn (exit {rc})"
        rate_limited = error is not None and bool(RATE_LIMIT.search(f"{error} {stderr[-500:]}"))
        return Result(usage, error, rate_limited, text, structured=as_object(text))

    def models(self) -> list[Model] | None:
        cp = run_catalog([self.binary, "debug", "models"])
        if cp.returncode != 0:
            raise ValueError(f"`codex debug models` exit {cp.returncode}: {(cp.stderr.strip() or cp.stdout.strip())[:160]}")
        try:
            rows = json.loads(cp.stdout).get("models") or []
        except (json.JSONDecodeError, AttributeError) as e:
            raise ValueError(f"`codex debug models` did not print the JSON catalog ({e})") from e
        out: list[Model] = []
        for row in rows:
            if isinstance(row, dict) and row.get("slug"):
                # `visibility: hide` rows stay: the rolling `-latest` slugs are among them
                hidden = " (hidden in the picker)" if row.get("visibility") == "hide" else ""
                out.append(Model(str(row["slug"]), f"{row.get('display_name') or ''}{hidden}".strip()))
        return out

    def smoke(self, model: str | None, cwd: Path) -> Invocation:
        return Invocation(prompt=SMOKE_PROMPT, system=SMOKE_SYSTEM, model=model, tools=frozenset(), cwd=cwd, timeout_s=120)


def _usage(u: dict[str, Any]) -> Usage:
    total, cached = u.get("input_tokens"), u.get("cached_input_tokens")
    fresh = max(total - cached, 0) if isinstance(total, int) and isinstance(cached, int) else total
    return Usage(input=fresh, output=u.get("output_tokens"), cache_read=cached)
