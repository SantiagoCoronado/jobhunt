"""The state machine behind `hunt run` (spec sections 4, 7, 8, decision 9).

One run = one ledger folder. Stages run in registry order; a Python stage is one unit that
runs in-process and passes or fails on its own check; a fanned stage plans its own units,
runs them through the pool and may skip itself (nothing to do). The first failed stage stops
the run and the later stages stay pending. A pick stage that finds nothing marks the rest
skipped, still writes the report and exits 3.

`--resume RUN|latest` re-enters that ledger instead of starting one: done and skipped stages
stay as they are, whatever a dead run left `running` is closed as failed first, and the first
stage that is not finished runs again with its unit list taken from the ledger (a fanned
stage never exports twice; outputs on disk are verified again, not redone). Ctrl+C or SIGTERM
kills the unit processes and closes the ledger the same way, so an interrupted run resumes.

A mkdir lock under data/hunt/ refuses a second concurrent run. It records its pid: a lock
whose process is gone is taken over, since a killed run cannot release its own.

Exit codes: 0 every selected stage done or skipped; 2 a stage failed, the run was interrupted,
the lock is held, or a selected stage is not in this build; 3 nothing to tailor.
"""
from __future__ import annotations

import contextlib
import os
import traceback
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from ..config import ROOT
from . import ledger as ledger_mod
from .config import HuntConfig
from .doctor import validate_models
from . import harness as harness_mod
from .harness import Harness
from .ledger import Ledger, new_run_id
from .stages import REGISTRY, Context, StageResult
from .stages import pick as pick_stage

NOT_IN_BUILD = "not in this build yet (docs/spec-hunt-orchestrator.md section 12)"
PID_FILE = "pid"


class LockHeld(RuntimeError):
    pass


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def acquire_lock(hunt_dir: Path) -> Path:
    lock = hunt_dir / ledger_mod.LOCK_NAME
    try:
        lock.mkdir()
    except FileExistsError:
        try:
            pid = int((lock / PID_FILE).read_text().strip())
        except (OSError, ValueError):
            pid = None                                  # no pid recorded: never guess that it is stale
        if pid is None or _alive(pid):
            who = f"pid {pid}" if pid else "no pid recorded"
            raise LockHeld(f"another hunt holds {lock} ({who}); wait for it or remove the folder if it is stale") from None
    (lock / PID_FILE).write_text(str(os.getpid()))
    return lock


def release_lock(lock: Path) -> None:
    with contextlib.suppress(OSError):
        (lock / PID_FILE).unlink()
    with contextlib.suppress(OSError):
        lock.rmdir()


def _summary_line(summary: dict[str, Any]) -> str:
    parts = [f"{k}={v}" for k, v in summary.items() if isinstance(v, (int, float, str)) and not isinstance(v, bool)]
    return " ".join(parts)


def run(cfg: HuntConfig, stages: Sequence[str], harness: str | None, *, hunt_dir: Path | None = None,
        cwd: Path = ROOT, emit: Callable[[str], None] | None = None, run_id: str | None = None,
        resume: str | None = None, clock: Callable[[], str] | None = None,
        get_harness: Callable[[str], Harness] | None = None, pool_options: dict[str, Any] | None = None,
        picks: list[dict[str, Any]] | None = None) -> int:
    say = emit or (lambda line: print(line, flush=True))
    hunt_dir = hunt_dir or ledger_mod.HUNT_DIR
    kwargs: dict[str, Any] = {"clock": clock} if clock else {}
    led: Ledger | None = None
    if resume:
        path = ledger_mod.resolve(resume, hunt_dir)
        if path is None:
            say(f"hunt run: no run to resume ({resume}) under {hunt_dir}")
            return 2
        try:
            led = Ledger.open(path, **kwargs)
        except (FileNotFoundError, ValueError) as e:
            say(f"hunt run: {path.name}: unreadable ledger ({e})")
            return 2
        stages = [s["name"] for s in led.state["stages"] if s["state"] not in ("done", "skipped")]
        harness = harness or led.state.get("harness")
        if not stages:
            say(f"run {led.run_id} has nothing left to resume: every stage is done or skipped")
            return 0
    harness = harness or cfg.harness
    missing = [s for s in stages if not REGISTRY[s].implemented]
    if missing:
        say(f"hunt run: {', '.join(missing)} {NOT_IN_BUILD}; select from "
            f"{', '.join(n for n, s in REGISTRY.items() if s.implemented)} with --only, --from/--to or --skip")
        return 2
    if not stages:
        say("hunt run: no stage selected")
        return 0
    problems = [c for c in validate_models(cfg, list(stages), harness) if c.status == "FAIL"]
    if problems:                                   # decision 6: a retired model fails at minute zero
        for c in problems:
            say(f"hunt run: stage {c.name}: {c.detail}")
        return 2
    hunt_dir.mkdir(parents=True, exist_ok=True)
    try:
        lock = acquire_lock(hunt_dir)
    except LockHeld as e:
        say(f"hunt run: {e}")
        return 2
    try:
        if led is None:
            try:
                led = Ledger.create(run_id or new_run_id(), harness, cfg.snapshot(), stages, hunt_dir, **kwargs)
            except FileExistsError as e:
                say(f"hunt run: {e} (a run started this minute; wait for the next one)")
                return 2
            say(f"run {led.run_id} started: {', '.join(stages)} on {harness} ({led.run_dir})")
            if picks is not None:                  # `--ids`: a resume finds the file, so it keeps them
                pick_stage.write_chosen(led.run_dir, picks)
                say(f"picks from --ids: {', '.join('#' + str(p['id']) for p in picks)}")
        else:
            closed = led.interrupt("interrupted: the run died here")
            led.reopen()
            say(f"run {led.run_id} resumed: {', '.join(stages)} on {harness} ({led.run_dir})")
            if closed:
                say(f"closed what the earlier run left running: {', '.join(closed)}")
        ctx = Context(cfg, led, harness, cwd, say, pool_options=pool_options or {})
        # the run's own config names the templates, not whatever hunt.toml holds by now
        ctx.get_harness = get_harness or (lambda name: harness_mod.get(name, templates=cfg.harness_templates))
        try:
            return _run_stages(ctx, list(stages))
        except KeyboardInterrupt:
            closed = led.interrupt()
            led.finish()
            say(f"run {led.run_id} interrupted ({', '.join(closed) or 'between stages'}); "
                f"`python -m src.hunt run --resume {led.run_id}` continues it")
            return 2
    finally:
        release_lock(lock)


def _run_stages(ctx: Context, stages: list[str]) -> int:
    led, say = ctx.ledger, ctx.emit
    failed = False
    stopped = any(s["state"] == "skipped" and s.get("note") == "no picks" for s in led.state["stages"])
    for name in stages:
        if stopped and name != "report":
            led.move_stage(name, "skipped", note="no picks")
            say(f"{name} skipped (no picks)")
            continue
        stage = REGISTRY[name]
        assert stage.run is not None
        python = stage.kind == "python"                # one in-process unit; a fanned stage owns its units
        led.move_stage(name, "running")
        if python:
            if not led.stage(name)["units"]:
                led.add_units(name, [{"id": name, "input": None, "output": None}])
            led.move_unit(name, name, "running")
        say(f"{name} running")
        try:
            res = stage.run(ctx)
        except Exception as e:  # noqa: BLE001, a crashing stage is a failed stage with its traceback in the log
            with open(ctx.log_path(name, name) if python else ctx.stage_log(name), "a", encoding="utf-8") as log:
                log.write(traceback.format_exc())
            res = StageResult({}, f"{type(e).__name__}: {e}"[:300])
        fields = dict(res.summary)
        if res.needs_human:
            fields["needs_human"] = list(res.needs_human)
        if fields:
            led.set_summary(name, **fields)
        if res.skipped and not res.verdict:
            led.move_stage(name, "skipped", note=res.skipped)
            say(f"{name} skipped ({res.skipped})")
            continue
        if res.verdict:
            if python:
                led.move_unit(name, name, "failed", verdict=res.verdict)
            led.move_stage(name, "failed", note=res.verdict)
            say(f"{name} failed: {res.verdict}")
            failed = True
            break
        if python:
            led.move_unit(name, name, "done", verdict="ok")
        led.move_stage(name, "done")
        say(f"{name} done  {_summary_line(led.stage(name)['summary'])}".rstrip())
        for item in res.needs_human:
            say(f"{name} needs a human: {item}")
        if res.stop:
            stopped = True
            say(f"{name}: nothing to tailor, the report still runs, then the run stops")
    final = led.finish()
    say(f"run {led.run_id} {final}")
    if failed:
        return 2
    if stopped:
        return 3
    return 0
