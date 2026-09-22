"""The run ledger: `data/hunt/<run_id>/` (spec section 7, decision 8).

    state.json      run_id, started, ended, harness, config snapshot,
                    stages[{name, state, started, ended, note, units[...], summary}],
                    usage {stages{}, harnesses{}, total} rolled up over the model units
    events.jsonl    one line per transition: {ts, stage, unit, from, to, note}
    prompts/<stage>/<unit>.md, logs/<stage>/<unit>.log
    picks.json, report.md

`state.json` is the truth a resume reads; it is rewritten atomically (write `.tmp`, rename)
after every transition so a crash at any point leaves the previous valid file. `events.jsonl`
is append-only and replays to the same stage and unit states, which is what the test checks.
Transitions are a small closed set (`STAGE_MOVES`, `UNIT_MOVES`); anything else is a bug and
raises. `data/` is git-ignored, so a run folder is local to one machine, which is the point:
any harness or session that can see the disk can resume it.
"""
from __future__ import annotations

import json
import os
import re
import threading
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config import ROOT

HUNT_DIR = ROOT / "data" / "hunt"
LOCK_NAME = ".lock"
STATE_FILE = "state.json"
EVENTS_FILE = "events.jsonl"
RUN_ID_RE = re.compile(r"^\d{8}-\d{4}$")

STAGE_STATES = ("pending", "running", "done", "failed", "skipped")
UNIT_STATES = ("pending", "running", "done", "failed")
# (from, to). A resume re-enters a failed stage or unit; done and skipped are terminal.
STAGE_MOVES: frozenset[tuple[str, str]] = frozenset({
    ("pending", "running"), ("pending", "skipped"), ("running", "done"), ("running", "failed"),
    ("running", "skipped"), ("failed", "running"),
})
UNIT_MOVES: frozenset[tuple[str, str]] = frozenset({
    ("pending", "running"), ("running", "done"), ("running", "failed"), ("failed", "running"),
    # resume only (decision 9): an output already on disk that verifies is done without a run,
    # and a done unit whose output no longer verifies is failed so it runs again
    ("pending", "done"), ("failed", "done"), ("done", "failed"),
})
USAGE_KEYS = ("input", "output", "cache_read", "cache_create", "cost_usd")


def new_run_id(now: datetime | None = None) -> str:
    """`YYYYMMDD-HHMM` (decision 8): sorts by time and reads as a time."""
    return (now or datetime.now()).strftime("%Y%m%d-%H%M")


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ---- reading ---------------------------------------------------------------------------

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
    """The `hunt status` tree: one line per stage with unit counts and the stage summary, one
    line per running or failed unit with its attempt count and the last log line."""
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
        summary = stage.get("summary") or {}
        scalars = [f"{k}={v}" for k, v in summary.items() if isinstance(v, (int, float, str)) and not isinstance(v, bool)]
        if scalars:
            line += "  " + " ".join(scalars)
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


# ---- writing ---------------------------------------------------------------------------

def write_state(run_dir: Path, state: dict[str, Any]) -> None:
    """Atomic: the new file is complete on disk before it takes the old one's name."""
    tmp = run_dir / (STATE_FILE + ".tmp")
    try:
        tmp.write_text(json.dumps(state, indent=1), encoding="utf-8")
        os.replace(tmp, run_dir / STATE_FILE)
    finally:
        if tmp.exists():
            tmp.unlink()


def add_usage(total: dict[str, Any] | None, usage: dict[str, Any] | None) -> dict[str, Any] | None:
    """Sum two usage records field by field; a field nobody reported stays None."""
    if usage is None:
        return total
    out: dict[str, Any] = dict(total or {})
    for k in USAGE_KEYS:
        a, b = out.get(k), usage.get(k)
        out[k] = a if b is None else (b if a is None else a + b)
    return out


def context_total(usage: dict[str, Any] | None) -> int | None:
    """Every token the model read: input + cache read + cache create, the number a long
    agentic run pays for (`docs/token-efficiency.md`); None when nothing was reported."""
    if not usage:
        return None
    parts = [usage.get(k) for k in ("input", "cache_read", "cache_create")]
    if all(p is None for p in parts):
        return None
    return sum(int(p) for p in parts if p is not None)


def _rollup_entry() -> dict[str, Any]:
    return {"units": 0, "attempts": 0, "models": [], **{k: None for k in USAGE_KEYS}}


def _fold(entry: dict[str, Any], unit: dict[str, Any]) -> None:
    entry["units"] += 1
    entry["attempts"] += int(unit.get("attempts") or 0)
    model = str(unit.get("model") or "default")
    if model not in entry["models"]:
        entry["models"] = sorted([*entry["models"], model])
    entry.update(add_usage(entry, unit.get("usage")) or {})


def rollup(state: dict[str, Any]) -> dict[str, Any]:
    """Usage rolled up over the model units (the ones with a harness; a deterministic stage
    reads no model): per stage in stage order, per harness, and in total (spec row 16). Each
    entry counts units and attempts (attempts minus units is the retries), lists the models
    those units named, and sums the usage fields, a field no adapter reported staying None.
    Derived from the units every time, so it never drifts from them; `state.json` carries
    the result under `usage` so a reader need not sum."""
    stages: dict[str, dict[str, Any]] = {}
    harnesses: dict[str, dict[str, Any]] = {}
    total = _rollup_entry()
    for s in state.get("stages", []):
        for u in s.get("units") or []:
            if not u.get("harness"):
                continue
            for entry in (stages.setdefault(str(s["name"]), _rollup_entry()),
                          harnesses.setdefault(str(u["harness"]), _rollup_entry()), total):
                _fold(entry, u)
    return {"stages": stages, "harnesses": dict(sorted(harnesses.items())), "total": total}


def _locked(method):
    def wrapper(self, *args, **kwargs):
        with self.lock:
            return method(self, *args, **kwargs)
    wrapper.__name__ = method.__name__
    wrapper.__doc__ = method.__doc__
    return wrapper


class Ledger:
    """One run folder. Every mutating method saves state.json atomically and appends the
    event, so the folder is always readable and always replayable."""

    def __init__(self, run_dir: Path, state: dict[str, Any], clock: Callable[[], str] = _now):
        self.run_dir = run_dir
        self.state = state
        self.clock = clock
        self.lock = threading.RLock()        # pool threads move units concurrently

    # -- lifecycle
    @classmethod
    def create(cls, run_id: str, harness: str, config: dict[str, Any], stages: Iterable[str],
               hunt_dir: Path | None = None, clock: Callable[[], str] = _now) -> Ledger:
        run_dir = (hunt_dir or HUNT_DIR) / run_id
        if run_dir.exists():
            raise FileExistsError(f"run folder exists: {run_dir}")
        run_dir.mkdir(parents=True)
        (run_dir / "prompts").mkdir()
        (run_dir / "logs").mkdir()
        state: dict[str, Any] = {
            "run_id": run_id, "started": clock(), "ended": None, "harness": harness, "config": config,
            "stages": [{"name": n, "state": "pending", "started": None, "ended": None, "note": None,
                        "units": [], "summary": {}} for n in stages],
            "usage": rollup({}),
        }
        led = cls(run_dir, state, clock)
        led._save()
        led._event(None, None, None, "started", None)
        return led

    @classmethod
    def open(cls, run_dir: Path, clock: Callable[[], str] = _now) -> Ledger:
        return cls(run_dir, load_state(run_dir), clock)

    @property
    def run_id(self) -> str:
        return str(self.state["run_id"])

    # -- lookups
    def stage(self, name: str) -> dict[str, Any]:
        for s in self.state["stages"]:
            if s["name"] == name:
                return s
        raise ValueError(f"run {self.run_id}: no stage '{name}'")

    def unit(self, stage: str, unit_id: str) -> dict[str, Any]:
        for u in self.stage(stage)["units"]:
            if u["id"] == unit_id:
                return u
        raise ValueError(f"run {self.run_id}: stage {stage} has no unit '{unit_id}'")

    def stage_names(self) -> list[str]:
        return [s["name"] for s in self.state["stages"]]

    # -- transitions
    @_locked
    def move_stage(self, name: str, to: str, note: str | None = None) -> None:
        s = self.stage(name)
        frm = s["state"]
        if (frm, to) not in STAGE_MOVES:
            raise ValueError(f"run {self.run_id}: stage {name} cannot move {frm} -> {to}")
        s["state"] = to
        if to == "running":
            s["started"] = s["started"] or self.clock()
            s["ended"] = None
            s["note"] = None                     # a resumed stage sheds the note of the failure it re-enters
        elif to in ("done", "failed", "skipped"):
            s["ended"] = self.clock()
        if note is not None:
            s["note"] = note
        self._save()
        self._event(name, None, frm, to, note)

    @_locked
    def add_units(self, stage: str, units: Iterable[dict[str, Any]]) -> None:
        """Plan units for a stage: each needs `id`, `input`, `output`; `harness` and `model`
        record what will run it; `log` is derived. Ids are unique within the stage."""
        s = self.stage(stage)
        if s["state"] not in ("pending", "running"):
            raise ValueError(f"run {self.run_id}: stage {stage} is {s['state']}, cannot add units")
        specs = list(units)
        seen = {u["id"] for u in s["units"]}
        for spec in specs:                      # validate the whole batch before touching state
            uid = str(spec["id"])
            if uid in seen:
                raise ValueError(f"run {self.run_id}: stage {stage} already has unit '{uid}'")
            seen.add(uid)
        added: list[str] = []
        for spec in specs:
            uid = str(spec["id"])
            s["units"].append({
                "id": uid, "input": spec.get("input"), "output": spec.get("output"),
                "attempts": 0, "state": "pending", "verdict": None, "usage": None,
                "harness": spec.get("harness"), "model": spec.get("model"),
                "log": f"logs/{stage}/{uid}.log",
            })
            added.append(uid)
        self._save()
        for uid in added:
            self._event(stage, uid, None, "pending", None)

    @_locked
    def move_unit(self, stage: str, unit_id: str, to: str, verdict: str | None = None,
                  usage: dict[str, Any] | None = None, note: str | None = None) -> None:
        u = self.unit(stage, unit_id)
        frm = u["state"]
        if (frm, to) not in UNIT_MOVES:
            raise ValueError(f"run {self.run_id}: unit {stage}/{unit_id} cannot move {frm} -> {to}")
        u["state"] = to
        if to == "running":
            u["attempts"] += 1
        if verdict is not None:
            u["verdict"] = verdict
        if usage is not None:
            u["usage"] = add_usage(u["usage"], usage)
        self._save()
        self._event(stage, unit_id, frm, to, note if note is not None else verdict)

    @_locked
    def interrupt(self, note: str = "interrupted") -> list[str]:
        """Close what a dead or cancelled run left open: every running unit and stage becomes
        failed, which is the state `--resume` re-enters. Returns what it closed."""
        closed: list[str] = []
        for s in self.state["stages"]:
            for u in s["units"]:
                if u["state"] == "running":
                    self.move_unit(s["name"], u["id"], "failed", verdict=note)
                    closed.append(f"{s['name']}/{u['id']}")
            if s["state"] == "running":
                self.move_stage(s["name"], "failed", note=note)
                closed.append(s["name"])
        return closed

    @_locked
    def reopen(self) -> None:
        """A resumed run is not ended."""
        self.state["ended"] = None
        self._save()
        self._event(None, None, None, "resumed", None)

    @_locked
    def set_summary(self, stage: str, **fields: Any) -> None:
        self.stage(stage)["summary"].update(fields)
        self._save()

    @_locked
    def finish(self) -> str:
        """Stamp the end of the run; returns the derived run state."""
        self.state["ended"] = self.clock()
        self._save()
        final = run_state(self.state)
        self._event(None, None, None, "ended", final)
        return final

    # -- persistence
    def _save(self) -> None:
        self.state["usage"] = rollup(self.state)          # per stage, per harness, total: always current
        write_state(self.run_dir, self.state)

    def _event(self, stage: str | None, unit: str | None, frm: str | None, to: str,
               note: str | None) -> None:
        line = json.dumps({"ts": self.clock(), "stage": stage, "unit": unit, "from": frm, "to": to,
                           "note": note})
        with open(self.run_dir / EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def events(self) -> list[dict[str, Any]]:
        path = self.run_dir / EVENTS_FILE
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    # -- replay
    def skeleton(self) -> dict[str, Any]:
        """The replayable core of state.json: each stage's state and each unit's state and
        attempt count. `replay(events)` must produce exactly this."""
        return {s["name"]: {"state": s["state"],
                            "units": {u["id"]: {"state": u["state"], "attempts": u["attempts"]} for u in s["units"]}}
                for s in self.state["stages"]}

    @staticmethod
    def replay(events: Iterable[dict[str, Any]], stages: Iterable[str]) -> dict[str, Any]:
        """Rebuild the skeleton from events.jsonl alone (every transition is recoverable)."""
        out: dict[str, Any] = {n: {"state": "pending", "units": {}} for n in stages}
        for e in events:
            stage, unit, to = e.get("stage"), e.get("unit"), e["to"]
            if stage is None:
                continue                                   # run-level: started, ended
            if unit is None:
                out[stage]["state"] = to
                continue
            units = out[stage]["units"]
            if to == "pending":
                units[unit] = {"state": "pending", "attempts": 0}
                continue
            units[unit]["state"] = to
            if to == "running":
                units[unit]["attempts"] += 1
        return out
