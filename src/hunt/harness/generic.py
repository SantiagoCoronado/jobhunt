"""The generic template harness (spec section 5, last row): any agent CLI with a headless
mode, described in `config/hunt.toml` instead of in Python.

    [harness.gemini]
    command = "gemini -m {model} --approval-mode auto_edit -o json -p {prompt}"
    envelope = "json"                                  # or "text" (the default)
    capabilities = ["read", "write", "edit", "bash", "web"]

The command is split ONCE with shell rules and never goes through a shell, so a placeholder
is always one argument, whatever the prompt holds. Placeholders:

    {prompt}       the unit's prompt as text          {prompt_file}   the same, in a file
    {system}       the role body as text              {system_file}   the same, in a file
    {schema_file}  the JSON schema in a file          {model}         the stage's model

- no `{system}` / `{system_file}` in the command: the role body is prepended to the prompt;
- no `{prompt}` / `{prompt_file}`: the prompt goes on stdin, so one of the three always holds;
- `{model}` with no model configured, or `{schema_file}` on a unit with no schema: that
  argument is dropped, and the flag before it too when it starts with `-` (`-m {model}`
  vanishes whole, the CLI takes its default). A schema the command has no place for goes
  into the prompt, as on opencode;
- files land in `scratch`, named by their content's hash.

`envelope = "json"`: the one JSON object the CLI prints (the last line that is one). The
reply is the first string among `result`, `response`, `text`, `output`, `message`; an error is
`is_error` true, a non-empty `error`, or a bad exit; usage is read from `usage` when it has the
common token names, null otherwise. `envelope = "text"`: stdout is the reply, a bad exit is
the error, usage is null. There is no catalog: `models()` is None, the configured model is
passed through unvalidated and `doctor` says so (the smoke prompt is the check).

`capabilities` is what the USER says the CLI can do (default: read, write, edit, bash); the
template has no way to grant or withhold a tool, that is the command line's job.
"""
from __future__ import annotations

import hashlib
import json
import shlex
import string
import tempfile
from pathlib import Path
from typing import Any

from . import TOOL_ORDER, TOOLS, Invocation, Model, Result, Usage
from ._common import RATE_LIMIT, SCHEMA_LINE, SMOKE_PROMPT, SMOKE_SYSTEM, as_object, granted, last_object, no_envelope, one_prompt, table

PLACEHOLDERS: tuple[str, ...] = ("prompt", "prompt_file", "system", "system_file", "schema_file", "model")
KEYS: frozenset[str] = frozenset({"command", "envelope", "capabilities"})
ENVELOPES: tuple[str, ...] = ("text", "json")
_DEFAULT_CAPABILITIES = ("read", "write", "edit", "bash")
_REPLY_KEYS = ("result", "response", "text", "output", "message")


def check_template(name: str, block: Any, where: str = "hunt config") -> None:
    """Raise ValueError for a `[harness.<name>]` block that could not run. Called on load,
    so a typo fails the command and never a hunt at minute 40."""
    here = f"{where}: [harness.{name}]"
    if not isinstance(block, dict) or not isinstance(block.get("command"), str) or not block["command"].strip():
        raise ValueError(f"{here} needs a `command` template (spec section 5)")
    unknown = sorted(set(block) - KEYS)
    if unknown:
        raise ValueError(f"{here} unknown key(s) {', '.join(unknown)} (allowed: {', '.join(sorted(KEYS))})")
    try:
        tokens = shlex.split(block["command"])
    except ValueError as e:
        raise ValueError(f"{here} command does not split as a command line ({e})") from e
    if not tokens or "{" in tokens[0]:
        raise ValueError(f"{here} command must start with the program to run")
    for token in tokens:
        for field in _fields(token):
            if field not in PLACEHOLDERS:
                raise ValueError(f"{here} unknown placeholder {{{field}}} (known: {', '.join('{' + p + '}' for p in PLACEHOLDERS)})")
    if block.get("envelope", "text") not in ENVELOPES:
        raise ValueError(f"{here} envelope must be one of {', '.join(ENVELOPES)}, got {block.get('envelope')!r}")
    caps = block.get("capabilities", list(_DEFAULT_CAPABILITIES))
    if not isinstance(caps, list) or not all(isinstance(c, str) for c in caps) or set(caps) - TOOLS:
        raise ValueError(f"{here} capabilities must be a list from {', '.join(TOOL_ORDER)}, got {caps!r}")


def _fields(token: str) -> list[str]:
    """The `{name}` fields of one argument. A brace that is not a field (JSON in an argument)
    is written `{{` and `}}`, as in any Python format string."""
    try:
        return [f for _lit, f, _spec, _conv in string.Formatter().parse(token) if f is not None]
    except ValueError as e:
        raise ValueError(f"bad braces in {token!r} ({e}); write a literal brace as {{{{ or }}}}") from e


class GenericHarness:
    def __init__(self, name: str, block: dict[str, Any], scratch: Path | None = None):
        check_template(name, block)
        self.name = name
        self.tokens = shlex.split(block["command"])
        self.binary = self.tokens[0]
        self.envelope: str = block.get("envelope", "text")
        self.capabilities: frozenset[str] = frozenset(block.get("capabilities", _DEFAULT_CAPABILITIES))
        self.scratch = scratch or Path(tempfile.gettempdir()) / f"jobhunt-hunt-{name}"
        used = {f for t in self.tokens for f in _fields(t)}
        self._system_placed = bool(used & {"system", "system_file"})
        self._prompt_placed = bool(used & {"prompt", "prompt_file"})
        self._schema_placed = "schema_file" in used

    def version_argv(self) -> list[str]:
        return [self.binary, "--version"]

    def _prompt(self, inv: Invocation) -> str:
        prompt = inv.prompt if self._system_placed else one_prompt(inv)
        if inv.schema is not None and not self._schema_placed:
            prompt = f"{prompt.rstrip()}\n\n{SCHEMA_LINE}\n{json.dumps(inv.schema, separators=(',', ':'))}\n"
        return prompt

    def _file(self, kind: str, text: str, suffix: str) -> str:
        self.scratch.mkdir(parents=True, exist_ok=True)
        path = self.scratch / f"{kind}_{hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]}{suffix}"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def argv(self, inv: Invocation) -> list[str]:
        granted(self.name, inv.tools, self.capabilities)
        prompt = self._prompt(inv)
        values: dict[str, str | None] = {"prompt": prompt, "system": inv.system, "model": inv.model or None,
                                         "schema_file": None, "prompt_file": None, "system_file": None}
        out: list[str] = []
        for token in self.tokens:
            fields = _fields(token)
            if "prompt_file" in fields:
                values["prompt_file"] = self._file("prompt", prompt, ".md")
            if "system_file" in fields:
                values["system_file"] = self._file("system", inv.system, ".md")
            if "schema_file" in fields and inv.schema is not None:
                values["schema_file"] = self._file("schema", json.dumps(inv.schema, separators=(",", ":")), ".json")
            if any(values[f] is None for f in fields):          # nothing to put there: the argument goes, and its flag
                if out and out[-1].startswith("-") and len(out) > 1:
                    out.pop()
                continue
            out.append(token.format(**{f: values[f] for f in fields}) if fields else token.replace("{{", "{").replace("}}", "}"))
        return out

    def stdin(self, inv: Invocation) -> str | None:
        return None if self._prompt_placed else self._prompt(inv)

    def parse(self, stdout: str, stderr: str, rc: int) -> Result:
        if self.envelope == "text":
            text = stdout.strip() or None
            error = None if rc == 0 else f"exit {rc}: {(stderr.strip() or stdout.strip())[-200:]}".rstrip(": ")
            return Result(Usage(), error, error is not None and bool(RATE_LIMIT.search(f"{error} {stderr[-500:]}")),
                          text, structured=as_object(text))
        data = last_object(stdout)
        if data is None:
            return no_envelope(stdout, stderr, rc, what="JSON envelope")
        text = next((data[k] for k in _REPLY_KEYS if isinstance(data.get(k), str)), None)
        said = data.get("error")
        failed = bool(data.get("is_error")) or bool(said)
        error = None
        if failed:
            detail = said if isinstance(said, str) else str(table(said).get("message") or text or "")
            error = f"error: {detail[:200]}".rstrip(": ")
        elif rc != 0:
            error = f"exit {rc}: {stderr.strip()[:200]}".rstrip(": ")
        u = table(data.get("usage"))
        usage = Usage(input=_tokens(u, "input_tokens", "inputTokens", "input"), output=_tokens(u, "output_tokens", "outputTokens", "output"),
                      cache_read=_tokens(u, "cache_read_input_tokens", "cached_input_tokens", "cacheRead"),
                      cache_create=_tokens(u, "cache_creation_input_tokens", "cacheWrite"))
        structured = data.get("structured_output")
        return Result(usage, error, error is not None and bool(RATE_LIMIT.search(f"{error} {stderr[-500:]}")), text,
                      structured=structured if structured is not None else as_object(text))

    def models(self) -> list[Model] | None:
        return None

    def smoke(self, model: str | None, cwd: Path) -> Invocation:
        return Invocation(prompt=SMOKE_PROMPT, system=SMOKE_SYSTEM, model=model, tools=frozenset(), cwd=cwd, timeout_s=120)


def _tokens(usage: dict[str, Any], *names: str) -> int | None:
    for name in names:
        value = usage.get(name)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None
