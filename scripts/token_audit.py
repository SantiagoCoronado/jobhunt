#!/usr/bin/env python3
"""Token audit over Claude Code session transcripts.

Reads the JSONL transcript of one session (plus its in-process subagents under
``<session>/subagents/``) and reports where the tokens went:

* per agent (main session + each subagent): API calls, input / cache-read /
  cache-create / output tokens, model;
* per tool: how many bytes of tool results were injected into a context (the
  thing every later API call re-reads);
* the biggest single tool results;
* a per-phase split of the main session, cut at each user prompt / skill load.

Usage:
    python scripts/token_audit.py [session_id_or_path] [--top 15] [--json out.json]
    python scripts/token_audit.py --latest          # newest session in this project
    python scripts/token_audit.py --all             # one summary row per session
    python scripts/token_audit.py --hunt RUN|latest # a hunt run, from its ledger

``--hunt`` reads ``data/hunt/<run>/state.json`` (the orchestrator's ledger, spec row 16)
instead of a transcript: per stage, per harness and the biggest units, whatever harness ran
them. The transcript mode stays for interactive sessions, where the tokens are the
session's own.

Costs are reported in tokens only; multiply by your plan's prices yourself. A hunt's
``cost_usd`` column is what the harness printed, when it prints one.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))         # --hunt reads the ledger through src.hunt.ledger


def project_dir_for(repo: Path = REPO) -> Path:
    """Claude Code names the transcript folder after the working directory, '/' -> '-'."""
    # NOT CLAUDE_PROJECT_DIR: Claude Code sets that to the repo root and exports it to hooks,
    # so reusing the name makes --latest fail from any hook-inherited environment.
    override = os.environ.get("JOBHUNT_TRANSCRIPTS_DIR")
    if override:
        return Path(override)
    return Path.home() / ".claude" / "projects" / str(repo).replace("/", "-")


PROJECT_DIR = project_dir_for()


@dataclass
class Usage:
    calls: int = 0
    input: int = 0
    cache_read: int = 0
    cache_create: int = 0
    output: int = 0
    thinking: int = 0
    models: Counter = field(default_factory=Counter)

    def add(self, u: dict, model: str | None) -> None:
        self.calls += 1
        self.input += u.get("input_tokens", 0) or 0
        self.cache_read += u.get("cache_read_input_tokens", 0) or 0
        self.cache_create += u.get("cache_creation_input_tokens", 0) or 0
        self.output += u.get("output_tokens", 0) or 0
        self.thinking += (u.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0
        if model:
            self.models[model] += 1

    @property
    def context_total(self) -> int:
        """Every token the model read across all calls (what you pay input for)."""
        return self.input + self.cache_read + self.cache_create

    def row(self) -> dict:
        return {
            "calls": self.calls,
            "input": self.input,
            "cache_read": self.cache_read,
            "cache_create": self.cache_create,
            "output": self.output,
            "thinking": self.thinking,
            "context_total": self.context_total,
            "models": dict(self.models),
        }


@dataclass
class Phase:
    """One slice of the main session, cut at each skill load / user prompt."""
    label: str
    usage: Usage = field(default_factory=Usage)
    tool_bytes: int = 0
    tool_calls: int = 0

    def row(self) -> dict:
        return {"label": self.label, "tool_bytes": self.tool_bytes, "tool_calls": self.tool_calls, **self.usage.row()}


def _usage_total(u: dict) -> int:
    return sum(int(u.get(k, 0) or 0) for k in
               ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens"))


def _content_bytes(content) -> int:
    if content is None:
        return 0
    if isinstance(content, str):
        return len(content.encode("utf-8", "ignore"))
    if isinstance(content, list):
        n = 0
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    n += len((block.get("text") or "").encode("utf-8", "ignore"))
                elif block.get("type") == "tool_result":
                    n += _content_bytes(block.get("content"))
                else:
                    n += len(json.dumps(block).encode("utf-8", "ignore"))
            else:
                n += len(str(block).encode("utf-8", "ignore"))
        return n
    return len(json.dumps(content).encode("utf-8", "ignore"))


def _tool_label(name: str, inp: dict) -> str:
    if name == "Bash":
        cmd = (inp.get("command") or "").strip().split("\n")[0]
        return f"Bash: {cmd[:70]}"
    if name in ("Read", "Write", "Edit"):
        return f"{name}: {inp.get('file_path', '')}"
    if name == "Agent":
        return f"Agent[{inp.get('subagent_type', '?')}]: {inp.get('description', '')}"
    if name == "Skill":
        return f"Skill: {inp.get('skill', '')}"
    if name.startswith("mcp__"):
        return name
    return name


def scan_file(path: Path) -> dict:
    """Scan one JSONL transcript. Returns usage, tool stats and phase cuts."""
    usage = Usage()
    tool_uses: dict[str, tuple[str, str]] = {}  # tool_use_id -> (tool name, label)
    tool_bytes: Counter = Counter()
    tool_calls: Counter = Counter()
    biggest: list[tuple[int, str]] = []
    phases: list[Phase] = []
    cur = Phase("(start)")
    user_prompt_bytes = 0
    assistant_text_bytes = 0
    agent_name = None
    cost_state = None
    first_ts = last_ts = None
    seen_requests: set[str] = set()  # one assistant message spans several JSONL lines, same usage

    def cut(label: str) -> None:
        nonlocal cur
        if cur.usage.calls or cur.tool_calls:
            phases.append(cur)
        cur = Phase(label[:90])

    with path.open() as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = d.get("type")
            ts = d.get("timestamp")
            if ts:
                first_ts = first_ts or ts
                last_ts = ts
            if t == "agent-name":
                agent_name = d.get("agentName")
            elif t == "cost-state":
                cost_state = {k: d.get(k) for k in ("totalCostUSD", "totalAPIDuration", "modelUsage")}
            elif t == "assistant":
                msg = d.get("message") or {}
                u = msg.get("usage")
                rid = str(d.get("requestId") or msg.get("id") or "")
                # Rate-limit / interrupt placeholders carry model "<synthetic>" and zero usage;
                # they are not API calls and must not inflate the per-agent call count.
                synthetic = msg.get("model") == "<synthetic>" or not _usage_total(u or {})
                # A message with no request id at all is counted, never deduped: folding every
                # id-less entry onto one key would drop real calls and make a hunt look cheaper.
                duplicate = bool(rid) and rid in seen_requests
                if u and not duplicate and not synthetic:
                    if rid:
                        seen_requests.add(rid)
                    usage.add(u, msg.get("model"))
                    cur.usage.add(u, msg.get("model"))
                for block in msg.get("content") or []:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_use":
                        name = block.get("name", "?")
                        inp = block.get("input") or {}
                        tool_uses[str(block.get("id") or "")] = (name, _tool_label(name, inp))
                        tool_calls[name] += 1
                        cur.tool_calls += 1
                        if name == "Skill":
                            cut(f"Skill:{inp.get('skill')}")
                    elif block.get("type") == "text":
                        assistant_text_bytes += len((block.get("text") or "").encode())
            elif t == "user":
                msg = d.get("message") or {}
                content = msg.get("content")
                is_tool_result = isinstance(content, list) and any(
                    isinstance(b, dict) and b.get("type") == "tool_result" for b in content
                )
                if is_tool_result and isinstance(content, list):
                    for b in content:
                        if not (isinstance(b, dict) and b.get("type") == "tool_result"):
                            continue
                        n = _content_bytes(b.get("content"))
                        name, label = tool_uses.get(str(b.get("tool_use_id") or ""), ("?", "?"))
                        tool_bytes[name] += n
                        cur.tool_bytes += n
                        biggest.append((n, label))
                elif not d.get("isMeta"):
                    n = _content_bytes(content)
                    user_prompt_bytes += n
                    text = content if isinstance(content, str) else json.dumps(content)
                    if "<command-name>" in text:
                        # skill / slash command expansion
                        m = re.search(r"<command-name>([^<]+)</command-name>", text)
                        cut(f"cmd:{m.group(1) if m else '?'}")
                    elif n > 0 and not text.startswith("<local-command"):
                        cut(f"user: {text.strip()[:60]!r}")
            if t == "system" and d.get("subtype") == "compact_boundary":
                cut("(compaction)")
    cut("(end)")
    biggest.sort(reverse=True)
    meta = {}
    mp = path.with_suffix(".meta.json")
    if mp.exists():
        try:
            meta = json.loads(mp.read_text())
        except (OSError, ValueError):
            meta = {}
    return {
        "path": str(path),
        "agent_name": agent_name or meta.get("agentType") or meta.get("agentName"),
        "meta": meta,
        "usage": usage.row(),
        "tool_bytes": dict(tool_bytes),
        "tool_calls": dict(tool_calls),
        "biggest_tool_results": biggest[:40],
        "user_prompt_bytes": user_prompt_bytes,
        "assistant_text_bytes": assistant_text_bytes,
        "phases": [p.row() for p in phases],
        "cost_state": cost_state,
        "first_ts": first_ts,
        "last_ts": last_ts,
    }


def scan_session(session: Path) -> dict:
    main = scan_file(session)
    subs = []
    subdir = session.with_suffix("") / "subagents"
    if subdir.is_dir():
        for p in sorted(subdir.glob("agent-*.jsonl")):
            subs.append(scan_file(p))
    total = Usage()
    for r in [main] + subs:
        u = r["usage"]
        total.calls += u["calls"]
        total.input += u["input"]
        total.cache_read += u["cache_read"]
        total.cache_create += u["cache_create"]
        total.output += u["output"]
        total.thinking += u["thinking"]
        for m, c in u["models"].items():
            total.models[m] += c
    return {"session": session.stem, "main": main, "subagents": subs, "total": total.row()}


def fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)


def print_report(rep: dict, top: int) -> None:
    main = rep["main"]
    subs = rep["subagents"]
    tot = rep["total"]
    print(f"# Token audit: session {rep['session']}")
    print(f"  span: {main['first_ts']} .. {main['last_ts']}")
    if main.get("cost_state"):
        print(f"  cost-state: totalCostUSD={main['cost_state'].get('totalCostUSD')}")
    print()
    print("## Totals (main + subagents)")
    print(f"  API calls        {tot['calls']}")
    print(f"  context read     {fmt(tot['context_total'])}  (input {fmt(tot['input'])} + cache_read {fmt(tot['cache_read'])} + cache_create {fmt(tot['cache_create'])})")
    print(f"  output           {fmt(tot['output'])}  (thinking {fmt(tot['thinking'])})")
    print(f"  models           {tot['models']}")
    print()
    print("## Per agent")
    hdr = f"  {'agent':<38} {'calls':>5} {'ctx_total':>10} {'cache_rd':>9} {'cache_cr':>9} {'output':>8} {'tool_in':>8}  model"
    print(hdr)
    rows = [("MAIN", main)] + [(f"{s['agent_name'] or '?'} {Path(s['path']).stem[-8:]}", s) for s in subs]
    for label, r in rows:
        u = r["usage"]
        tb = sum(r["tool_bytes"].values())
        model = ",".join(sorted(u["models"])) if u["models"] else "-"
        model = model.replace("claude-", "")
        print(f"  {label:<38} {u['calls']:>5} {fmt(u['context_total']):>10} {fmt(u['cache_read']):>9} {fmt(u['cache_create']):>9} {fmt(u['output']):>8} {fmt(tb):>8}  {model}")
    if subs:
        by_type: dict[str, Usage] = defaultdict(Usage)
        for s in subs:
            k = s["agent_name"] or "?"
            u = s["usage"]
            by_type[k].calls += u["calls"]
            by_type[k].input += u["input"]
            by_type[k].cache_read += u["cache_read"]
            by_type[k].cache_create += u["cache_create"]
            by_type[k].output += u["output"]
        print()
        print("## Subagents grouped by type")
        for k, u in sorted(by_type.items(), key=lambda kv: -kv[1].context_total):
            n = sum(1 for s in subs if (s["agent_name"] or "?") == k)
            print(f"  {k:<28} n={n:<3} calls={u.calls:<4} ctx_total={fmt(u.context_total):>8} output={fmt(u.output):>7}  avg_ctx/agent={fmt(u.context_total // max(n,1))}")
    print()
    print("## Main session: bytes injected per tool (tool_result sizes) ~ tokens = bytes/4")
    for name, b in sorted(main["tool_bytes"].items(), key=lambda kv: -kv[1])[:top]:
        print(f"  {name:<30} {fmt(b):>8} B  ~{fmt(b//4):>7} tok  calls={main['tool_calls'].get(name, 0)}")
    print(f"  user prompts (incl. skill expansions): {fmt(main['user_prompt_bytes'])} B; assistant text: {fmt(main['assistant_text_bytes'])} B")
    print()
    print(f"## Main session: {top} biggest single tool results")
    for n, label in main["biggest_tool_results"][:top]:
        print(f"  {fmt(n):>8} B  ~{fmt(n//4):>6} tok  {label}")
    print()
    print("## Main session: per phase (cut at each skill load / user prompt)")
    print(f"  {'phase':<52} {'calls':>5} {'ctx_total':>10} {'cache_cr':>9} {'output':>8} {'tool_in':>9}")
    for p in main["phases"]:
        print(f"  {p['label']:<52} {p['calls']:>5} {fmt(p['context_total']):>10} {fmt(p['cache_create']):>9} {fmt(p['output']):>8} {fmt(p['tool_bytes']):>9}")
    # Per-subagent biggest tool results, aggregated by label prefix
    if subs:
        agg: Counter = Counter()
        for s in subs:
            for n, label in s["biggest_tool_results"]:
                agg[label.split(":")[0] + ":" + label.split(":", 1)[-1][:60]] += n
        print()
        print(f"## Subagents: {top} biggest aggregated tool inputs")
        for label, n in agg.most_common(top):
            print(f"  {fmt(n):>8} B  ~{fmt(n//4):>6} tok  {label}")


# ---- hunt ledger mode ----------------------------------------------------------------------

def _ctx(usage: dict[str, Any] | None) -> int | None:
    from src.hunt import ledger
    return ledger.context_total(usage)


def _num(n: int | float | None) -> str:
    if n is None:
        return "-"
    return f"{n:.2f}" if isinstance(n, float) else fmt(n)


def scan_hunt(run_dir: Path) -> dict:
    """One hunt run from its ledger: the rollup per stage and per harness, and every model
    unit with its own numbers, biggest context first."""
    from src.hunt import ledger

    st = ledger.load_state(run_dir)
    roll = ledger.rollup(st)
    units: list[dict[str, Any]] = []
    for s in st.get("stages", []):
        for u in s.get("units") or []:
            if not u.get("harness"):
                continue
            use = u.get("usage") or {}
            units.append({"stage": s["name"], "id": u["id"], "harness": u["harness"], "model": u.get("model") or "default",
                          "state": u.get("state"), "attempts": int(u.get("attempts") or 0),
                          "context_total": _ctx(use), "output": use.get("output"), "cost_usd": use.get("cost_usd")})
    units.sort(key=lambda r: -(r["context_total"] or 0))
    stages = [{"name": name, **e, "context_total": _ctx(e)} for name, e in roll["stages"].items()]
    harnesses = [{"name": name, **e, "context_total": _ctx(e)} for name, e in roll["harnesses"].items()]
    total = {**roll["total"], "context_total": _ctx(roll["total"])}
    return {"run_id": st.get("run_id"), "path": str(run_dir), "state": ledger.run_state(st),
            "harness": st.get("harness"), "started": st.get("started"), "ended": st.get("ended"),
            "stages": stages, "harnesses": harnesses, "units": units, "total": total}


def print_hunt_report(rep: dict, top: int) -> None:
    tot = rep["total"]
    print(f"# Token audit: hunt {rep['run_id']} ({rep['harness'] or '-'}, {rep['state']})")
    print(f"  span: {rep['started'] or '-'} .. {rep['ended'] or '-'}")
    print(f"  ledger: {rep['path']}")
    print()
    if not tot["units"]:
        print("No model unit ran.")
        return
    print("## Totals (model units)")
    print(f"  units            {tot['units']}  ({tot['attempts']} attempts, {tot['attempts'] - tot['units']} retries)")
    print(f"  context read     {_num(tot['context_total'])}  (input {_num(tot['input'])} + cache_read {_num(tot['cache_read'])} "
          f"+ cache_create {_num(tot['cache_create'])})")
    print(f"  output           {_num(tot['output'])}")
    print(f"  cost usd         {_num(tot['cost_usd'])}")
    print(f"  models           {', '.join(tot['models'])}")
    hdr = f"  {'':<12} {'units':>5} {'attempts':>8} {'ctx_total':>10} {'cache_rd':>9} {'cache_cr':>9} {'output':>8} {'cost':>7}  models"
    for title, rows in (("## Per stage", rep["stages"]), ("## Per harness", rep["harnesses"])):
        print()
        print(title)
        print(hdr)
        for r in rows + [{"name": "total", **tot}]:
            print(f"  {r['name']:<12} {r['units']:>5} {r['attempts']:>8} {_num(r['context_total']):>10} {_num(r['cache_read']):>9} "
                  f"{_num(r['cache_create']):>9} {_num(r['output']):>8} {_num(r['cost_usd']):>7}  {', '.join(r['models'])}")
    print()
    print(f"## {top} biggest units by context read")
    print(f"  {'stage/unit':<34} {'state':<7} {'attempts':>8} {'ctx_total':>10} {'output':>8} {'cost':>7}  harness/model")
    for u in rep["units"][:top]:
        print(f"  {u['stage'] + '/' + u['id']:<34} {u['state'] or '-':<7} {u['attempts']:>8} {_num(u['context_total']):>10} "
              f"{_num(u['output']):>8} {_num(u['cost_usd']):>7}  {u['harness']}/{u['model']}")


def resolve_hunt(run: str) -> Path:
    from src.hunt import ledger

    path = ledger.resolve(run)
    if path is None:
        what = "no hunt runs yet" if run in ("", "latest") else f"no run {run!r}"
        sys.exit(f"{what} under {ledger.HUNT_DIR} (this mode reads the orchestrator's ledger)")
    return path


def resolve(arg: str | None, latest: bool) -> Path:
    if latest or not arg:
        files = sorted(PROJECT_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        if not files:
            sys.exit(f"no sessions in {PROJECT_DIR} (this script reads Claude Code transcripts of this project)")
        return files[-1]
    p = Path(arg)
    if p.exists():
        return p
    cands = sorted(PROJECT_DIR.glob(f"{arg}*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not cands:
        sys.exit(f"no session matching {arg!r} in {PROJECT_DIR}")
    if len(cands) > 1:
        print(f"note: {len(cands)} sessions match {arg!r}, using the newest ({cands[-1].name}); "
              "give more of the id to pick another", file=sys.stderr)
    return cands[-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("session", nargs="?")
    ap.add_argument("--latest", action="store_true")
    ap.add_argument("--all", action="store_true", help="one summary row per session")
    ap.add_argument("--hunt", metavar="RUN", help="a hunt run id or 'latest': read data/hunt/<run>/state.json instead of a transcript")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--json", help="also dump the full report as JSON")
    a = ap.parse_args()
    if a.hunt is not None:
        rep = scan_hunt(resolve_hunt(a.hunt))
        print_hunt_report(rep, a.top)
        if a.json:
            Path(a.json).write_text(json.dumps(rep, indent=1, default=str))
            print(f"\n(json written to {a.json})")
        return
    if a.all:
        print(f"{'session':<10} {'first_ts':<22} {'calls':>5} {'ctx_total':>10} {'cache_cr':>9} {'output':>8} {'subagents':>9}  models")
        for f in sorted(PROJECT_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime):
            rep = scan_session(f)
            t = rep["total"]
            models = ",".join(m.replace("claude-", "") for m in sorted(t["models"]))
            print(f"{rep['session'][:8]:<10} {(rep['main']['first_ts'] or '')[:19]:<22} {t['calls']:>5} {fmt(t['context_total']):>10} {fmt(t['cache_create']):>9} {fmt(t['output']):>8} {len(rep['subagents']):>9}  {models}")
        return
    path = resolve(a.session, a.latest)
    rep = scan_session(path)
    print_report(rep, a.top)
    if a.json:
        Path(a.json).write_text(json.dumps(rep, indent=1, default=str))
        print(f"\n(json written to {a.json})")


if __name__ == "__main__":
    main()
