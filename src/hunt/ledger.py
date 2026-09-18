"""The run ledger: `data/hunt/<run_id>/` (spec section 7).

    state.json      run_id, started, harness, config snapshot, stages[{name, state, units[...]}]
    events.jsonl    one line per transition
    prompts/, logs/ per stage and unit
    picks.json, report.md

This story is the READ side: list the runs, resolve `latest`, load a state file and render
the `hunt status` tree. The writer (atomic state.json, events.jsonl, transitions) is story 2.
`data/` is git-ignored, so the folder is local to one machine, which is the point: a run can be
resumed from any harness or session that can see the disk.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config import ROOT

HUNT_DIR = ROOT / "data" / "hunt"
LOCK_NAME = ".lock"
STATE_FILE = "state.json"
RUN_ID_RE = re.compile(r"^\d{8}-\d{4}$")

STAGE_STATES = ("pending", "running", "done", "failed", "skipped")
UNIT_STATES = ("pending", "running", "done", "failed")


def new_run_id(now: datetime | None = None) -> str:
    """`YYYYMMDD-HHMM` (decision 8): sorts by time and reads as a time."""
    return (now or datetime.now()).strftime("%Y%m%d-%H%M")


@dataclass(frozen=True)
class RunInfo:
    run_id: str
    path: Path
    state: str            # pending | running | done | failed | unreadable
    started: str | None
    harness: str | None


def load_state(run_dir: Path) -> dict[str, Any]:
    """The parsed state.json of one run; raises FileNotFoundError or ValueError."""
    path = run_dir / STATE_FILE
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"{path}: not valid JSON: {e}") from e
    if not isinstance(data, dict) or "run_id" not in data:
        raise ValueError(f"{path}: not a hunt state file")
    return data


def run_state(state: dict[str, Any]) -> str:
    """The run-level state derived from its stages: failed beats running beats pending."""
    states = [str(s.get("state", "pending")) for s in state.get("stages", [])]
    if not states:
        return "pending"
    if "failed" in states:
        return "failed"
    if "running" in states:
        return "running"
    if all(s in ("done", "skipped") for s in states):
        return "done"
    return "running" if any(s in ("done", "skipped") for s in states) else "pending"


def list_runs(hunt_dir: Path | None = None) -> list[RunInfo]:
    """Every run folder under data/hunt/, newest first; an unreadable ledger is listed, not hidden."""
    hunt_dir = hunt_dir or HUNT_DIR
    if not hunt_dir.is_dir():
        return []
    runs: list[RunInfo] = []
    for d in sorted((p for p in hunt_dir.iterdir() if p.is_dir() and RUN_ID_RE.match(p.name)), reverse=True):
        try:
            st = load_state(d)
        except (FileNotFoundError, ValueError):
            runs.append(RunInfo(d.name, d, "unreadable", None, None))
            continue
        runs.append(RunInfo(d.name, d, run_state(st), st.get("started"), st.get("harness")))
    return runs


def resolve(run: str | None, hunt_dir: Path | None = None) -> Path | None:
    """`latest` (or nothing) is the newest run folder; a run id is that folder if it exists."""
    hunt_dir = hunt_dir or HUNT_DIR
    if run in (None, "", "latest"):
        runs = list_runs(hunt_dir)
        return runs[0].path if runs else None
    assert run is not None
    path = hunt_dir / run
    return path if path.is_dir() else None


def format_runs(runs: list[RunInfo]) -> str:
    if not runs:
        return "no runs yet"
    width = max(len(r.run_id) for r in runs)
    lines = [f"{r.run_id:<{width}}  {r.state:<10}  {r.harness or '-':<9}  started {r.started or '-'}" for r in runs]
    return "\n".join(lines)


def _last_log_line(run_dir: Path, unit: dict[str, Any]) -> str | None:
    rel = unit.get("log")
    if not rel:
        return None
    path = run_dir / rel
    if not path.exists():
        return None
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if line.strip():
            return line.strip()[:120]
    return None


def render_status(state: dict[str, Any], run_dir: Path | None = None) -> str:
    """The `hunt status` tree: one line per stage with unit counts, one line per running or
    failed unit with its attempt count and the last log line."""
    head = (f"run {state.get('run_id')}  {state.get('harness') or '-'}  "
            f"started {state.get('started') or '-'}  {run_state(state)}")
    lines = [head]
    for stage in state.get("stages", []):
        name = str(stage.get("name"))
        st = str(stage.get("state", "pending"))
        units = stage.get("units") or []
        line = f"  {name:<9} {st:<8}"
        if units:
            counts = {k: sum(1 for u in units if u.get("state") == k) for k in UNIT_STATES}
            parts = [f"{counts['done']}/{len(units)} done"]
            if counts["running"]:
                parts.append(f"{counts['running']} running")
            if counts["failed"]:
                parts.append(f"{counts['failed']} failed")
            line += "  " + ", ".join(parts)
        note = stage.get("note")
        if note:
            line += f"  ({note})"
        lines.append(line)
        for u in units:
            if u.get("state") not in ("running", "failed"):
                continue
            uline = f"    {u.get('id')}  {u.get('state')}  attempt {u.get('attempts', 0)}"
            if u.get("state") == "failed" and u.get("verdict"):
                uline += f"  {str(u['verdict'])[:80]}"
            last = _last_log_line(run_dir, u) if run_dir else None
            if last:
                uline += f"  last: {last}"
            lines.append(uline)
    return "\n".join(line.rstrip() for line in lines)
