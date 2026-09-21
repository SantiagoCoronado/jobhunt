"""The agy (Antigravity CLI) adapter, against `agy --help` 1.1.27, the documentation embedded
in its binary and its real signed-out behaviour on 2026-09-21. NOT yet seen answering: this
install is signed out, so the success envelope below is read from the binary's own field
names, not from a captured call. `HUNT_SMOKE=1 pytest -m harness_smoke` is the live check.

    agy --output-format json [--model {model}] [--mode accept-edits] [--json-schema {schema}]
        --print-timeout {timeout}s --print={system + prompt}

What changed from the spec's line (section 5), each seen on the real CLI:
- `-p` TAKES the prompt as its value: `agy -p --output-format json ... PROMPT` exits 2 with
  "-p took "--output-format" as its prompt". The prompt is attached, `--print=...`, and goes
  last. Stdin is not an alternative (`-p` alone: "flag needs an argument");
- no `--agent {role}`: custom agents are `agent.md` files in a layout the docs in the binary
  do not spell out and a signed-out CLI cannot list, so no agent file is generated and the
  role body is prepended to the task instead;
- signed out, a headless call prints "Authentication required. Please visit the URL" on
  stderr and then WAITS, past `--print-timeout`. The pool's timeout kills it; `checks()` below
  finds it first, in a tenth of a second, through `agy models`.

Tools: there is no allowlist flag. `--mode accept-edits` is passed when the unit may write or
edit. Shell commands that `permissions.allow` in `~/.gemini/antigravity-cli/settings.json`
does not cover are auto-denied in headless mode (the CLI's own message: "headless mode cannot
prompt for ... Add an allow-rule under permissions.allow in settings.json"), rules look like
`command(git status)`. So `bash` works only when the user allowed python there; `checks()`
reads the file and says which rule to add. `--dangerously-skip-permissions` is never passed.
`web` is not claimed: nothing about it could be verified signed out, so research falls back.

Envelope (`--output-format json`), by the struct tags in the binary, the claude shape:
`result`, `is_error`, `subtype`, `usage.{input_tokens, output_tokens}`, `structured_output`,
`session_id`, `num_turns`, `duration_ms`.

Catalog: `agy models`; signed out it exits 1 with "Please sign in to view available models".
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from . import Invocation, Model, Result, Usage
from ._common import RATE_LIMIT, SMOKE_PROMPT, SMOKE_SYSTEM, as_object, granted, no_envelope, one_prompt, run_catalog, table

SETTINGS = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
_PYTHON_RULE = re.compile(r"^command\(\s*(?:\S*/)?python[\d.]*(?:\s[^)]*)?\)$")
_SIGN_IN = re.compile(r"sign in|authentication required|log in", re.I)
RULES_TO_ADD = ('"command(python)"', '"command(.venv/bin/python)"')


class AgyHarness:
    name = "agy"
    capabilities: frozenset[str] = frozenset({"read", "write", "edit", "bash"})

    def __init__(self, binary: str = "agy", settings: Path | None = None):
        self.binary = binary
        self.settings = settings or SETTINGS

    def version_argv(self) -> list[str]:
        return [self.binary, "--version"]

    def argv(self, inv: Invocation) -> list[str]:
        tools = granted(self.name, inv.tools, self.capabilities)
        argv = [self.binary, "--output-format", "json"]
        if inv.model:
            argv += ["--model", inv.model]
        if tools & {"write", "edit"}:
            argv += ["--mode", "accept-edits"]
        if inv.schema is not None:
            argv += ["--json-schema", json.dumps(inv.schema, separators=(",", ":"))]
        return [*argv, "--print-timeout", f"{inv.timeout_s}s", f"--print={one_prompt(inv)}"]

    def stdin(self, inv: Invocation) -> str | None:
        return None

    def parse(self, stdout: str, stderr: str, rc: int) -> Result:
        data = _envelope(stdout)
        if data is None:
            res = no_envelope(stdout, stderr, rc, what="JSON envelope")
            if _SIGN_IN.search(stderr):
                return Result(Usage(), "agy is signed out: launch `agy` once with no arguments to sign in", False, None,
                              envelope=False)
            return res
        u = table(data.get("usage"))
        usage = Usage(input=u.get("input_tokens"), output=u.get("output_tokens"),
                      cache_read=u.get("cache_read_input_tokens"), cache_create=u.get("cache_creation_input_tokens"),
                      cost_usd=data.get("total_cost_usd"))
        text = data.get("result") if isinstance(data.get("result"), str) else None
        envelope_error = bool(data.get("is_error")) or data.get("subtype") not in (None, "success")
        error = None
        if envelope_error:
            # an error envelope explains itself in `result`
            reason = str(data["subtype"]) if data.get("subtype") not in (None, "success") else "error"
            detail = (text or stderr.strip())[:200]
            error = f"{reason}: {detail}" if detail else reason
        elif rc != 0:
            detail = stderr.strip()[:200]                       # a bad exit under a clean envelope: only stderr can say why
            error = f"exit {rc}: {detail}" if detail else f"exit {rc}"
        rate_limited = error is not None and bool(RATE_LIMIT.search(f"{error} {stderr[-500:]}"))
        structured = data.get("structured_output")
        return Result(usage, error, rate_limited, text, structured=structured if structured is not None else as_object(text))

    def models(self) -> list[Model] | None:
        cp = run_catalog([self.binary, "models"])
        out = f"{cp.stdout}\n{cp.stderr}"
        if cp.returncode != 0:
            if _SIGN_IN.search(out):
                raise ValueError("sign in: launch `agy` once with no arguments, then run this again")
            raise ValueError(f"`agy models` exit {cp.returncode}: {(cp.stderr.strip() or cp.stdout.strip())[:160]}")
        ids: list[Model] = []
        for line in cp.stdout.splitlines():
            cols = line.strip().lstrip("*-• ").split()
            if cols and not line.lower().startswith(("fetching", "available")) and re.fullmatch(r"[\w.~/:-]+", cols[0]):
                ids.append(Model(cols[0], " ".join(cols[1:])))
        return ids

    def smoke(self, model: str | None, cwd: Path) -> Invocation:
        return Invocation(prompt=SMOKE_PROMPT, system=SMOKE_SYSTEM, model=model, tools=frozenset(), cwd=cwd, timeout_s=120)

    # -- doctor (spec section 5: "`doctor` checks that and says so")
    def checks(self) -> list[tuple[str, str, str]]:
        """(name, status, detail) rows `doctor` prints before it spends a call. A FAIL here
        stops the doctor: a signed-out agy would hold the smoke prompt until its timeout."""
        return [self._signed_in(), self.shell_permission()]

    def _signed_in(self) -> tuple[str, str, str]:
        try:
            cp = run_catalog([self.binary, "models"], timeout=40)
        except (OSError, subprocess.SubprocessError) as e:
            return ("sign-in", "FAIL", f"`agy models` did not run: {type(e).__name__}")
        if cp.returncode != 0 and _SIGN_IN.search(f"{cp.stdout}\n{cp.stderr}"):
            return ("sign-in", "FAIL", "signed out: launch `agy` once with no arguments to sign in (a headless call "
                                       "would print a login URL and wait)")
        return ("sign-in", "ok", "signed in") if cp.returncode == 0 else \
               ("sign-in", "warn", f"`agy models` exit {cp.returncode}; sign-in not confirmed")

    def shell_permission(self) -> tuple[str, str, str]:
        """Does `permissions.allow` cover python? Without it every `bash` unit (inbox, research,
        tailor) has its shell call auto-denied in headless mode."""
        fix = f"add {' and '.join(RULES_TO_ADD)} to permissions.allow in {self.settings}"
        if not self.settings.exists():
            return ("shell", "warn", f"no settings file, so python is auto-denied headless; {fix}")
        try:
            allow: Any = table(table(json.loads(self.settings.read_text(encoding="utf-8"))).get("permissions")).get("allow")
        except (OSError, json.JSONDecodeError) as e:
            return ("shell", "warn", f"{self.settings} is unreadable ({type(e).__name__}); {fix}")
        rules = [r for r in allow if isinstance(r, str)] if isinstance(allow, list) else []
        covering = [r for r in rules if _PYTHON_RULE.match(r.strip())]
        if covering:
            return ("shell", "ok", f"permissions.allow covers python ({', '.join(covering[:3])})")
        return ("shell", "warn", f"permissions.allow does not cover python, so inbox, research and tailor units "
                                 f"cannot run it headless; {fix}")


def _envelope(stdout: str) -> dict[str, Any] | None:
    """The one JSON object agy prints; the last line that is one, when a banner came first."""
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
