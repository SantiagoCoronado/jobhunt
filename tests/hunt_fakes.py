"""A fake agent for the fanned-stage tests: a real subprocess (so the pool, the logs and the
timeouts are the real ones) that reads the unit prompt, finds the input and output files the
task line names in backticks, and writes the output a well-behaved agent would. What it does
wrong, and how many times, comes from `fake_agent.json` in the working directory:

    {"<unit id>": {"short": 1}}      the first call writes a file missing its last row
    {"<unit id>": {"bad_keep": 9}}   every call writes keep as a string
    {"<unit id>": {"crash": 1}}      the first call exits 1 with an error envelope

    {"inbox": {"replies": [...]}}    the inbox unit's reply per call (the last one repeats)

The unit id is the input file's stem (`chunk_001`). Match scores: 90 on an even id, 65 on an
odd one, and every `reasons` carries an em-dash for the stage to scrub.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from src.hunt.harness import TOOL_ORDER, Invocation, Result, Usage

AGENT = r'''
import json, os, re, sys
prompt = sys.argv[1]
if "classify every line of the manifest" in prompt:       # the inbox unit: the reply is the output
    replies = (json.load(open("fake_agent.json")).get("inbox") or {}).get("replies") or []
    n = int(open(".fake_inbox.count").read()) if os.path.exists(".fake_inbox.count") else 0
    open(".fake_inbox.count", "w").write(str(n + 1))
    reply = replies[min(n, len(replies) - 1)]
    print(json.dumps({"ok": True, "result": json.dumps(reply), "structured": reply if isinstance(reply, dict) else None}))
    sys.exit(0)
paths = re.findall(r"`([^`]+\.(?:json|md))`", prompt)
src, out = paths[0], paths[1]
unit = os.path.splitext(os.path.basename(src))[0]
plan = json.load(open("fake_agent.json")) if os.path.exists("fake_agent.json") else {}
mine = plan.get(unit, {})
count_file = f".fake_{unit}.count"
n = int(open(count_file).read()) if os.path.exists(count_file) else 0
open(count_file, "w").write(str(n + 1))
if n < mine.get("crash", 0):
    print(json.dumps({"error": "agent crashed"})); sys.exit(1)
rows = json.load(open(src))
if "triage" in src:
    data = [{"id": r["id"], "keep": r["id"] % 3 != 0, "reason": "fake", "bucket": r["id"] % 4} for r in rows]
    if n < mine.get("bad_keep", 0):
        data[0]["keep"] = "maybe"
if "match" in src:
    data = [{"id": r["id"], "score": 90 if r["id"] % 2 == 0 else 65, "recommendation": "Yes",
             "reasons": "fake \u2014 verdict"} for r in rows]
    if n < mine.get("bad_score", 0):
        data[0]["score"] = "high"
if n < mine.get("short", 0):
    data = data[:-1]
json.dump(data, open(out, "w"))
print(json.dumps({"ok": True}))
'''


class FakeAgentHarness:
    name = "fake"
    binary = sys.executable
    capabilities = frozenset(TOOL_ORDER)

    def __init__(self, workdir: Path):
        self.script = workdir / "fake_agent.py"
        self.script.write_text(AGENT)
        self.calls: list[Invocation] = []

    def version_argv(self) -> list[str]:
        return [sys.executable, "--version"]

    def argv(self, inv: Invocation) -> list[str]:
        self.calls.append(inv)
        return [sys.executable, str(self.script), inv.prompt]

    def stdin(self, inv: Invocation) -> str | None:
        return None

    def parse(self, stdout: str, stderr: str, rc: int) -> Result:
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            return Result(Usage(), f"exit {rc}, no JSON envelope", False, None, envelope=False)
        if rc != 0:
            return Result(Usage(input=5), str(data.get("error")), False, None)
        return Result(Usage(input=100, output=10, cost_usd=0.01), None, False, data.get("result") or stdout.strip(),
                      structured=data.get("structured"))

    def models(self):
        return None
