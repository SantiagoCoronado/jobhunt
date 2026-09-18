"""The state machine behind `hunt run` (spec sections 4, 7, 8).

One run = one ledger folder. Stages run in registry order; a Python stage is one unit that
runs in-process and passes or fails on its own check; a fanned stage plans units for the pool
(PR 3). The first failed stage stops the run (later stages stay pending for `--resume`, PR 3
story 7). A pick stage that finds nothing marks the rest skipped, still writes the report
and exits 3. A mkdir lock under data/hunt/ refuses a second concurrent run.

Exit codes: 0 every selected stage done or skipped; 2 a stage failed, the lock is held, or a
selected stage is not in this build; 3 nothing to tailor.
"""
from __future__ import annotations

import traceback
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from ..config import ROOT
from . import ledger as ledger_mod
from .config import HuntConfig
from .doctor import validate_models
from .ledger import Ledger, new_run_id
from .stages import REGISTRY, Context, StageResult

NOT_IN_BUILD = "not in this build yet (fanned stages land in PR 3, feat/hunt-fanout)"


class LockHeld(RuntimeError):
    pass


def acquire_lock(hunt_dir: Path) -> Path:
    lock = hunt_dir / ledger_mod.LOCK_NAME
    try:
        lock.mkdir()
    except FileExistsError:
        raise LockHeld(f"another hunt holds {lock}; wait for it or remove the folder if it is stale") from None
    return lock


def release_lock(lock: Path) -> None:
    try:
        lock.rmdir()
    except OSError:
        pass


def _summary_line(res: StageResult) -> str:
    parts = [f"{k}={v}" for k, v in res.summary.items() if isinstance(v, (int, float, str)) and not isinstance(v, bool)]
    return " ".join(parts)


def run(cfg: HuntConfig, stages: Sequence[str], harness: str, *, hunt_dir: Path | None = None,
        cwd: Path = ROOT, emit: Callable[[str], None] | None = None, run_id: str | None = None,
        resume: str | None = None, clock: Callable[[], str] | None = None) -> int:
    say = emit or (lambda line: print(line, flush=True))
    if resume:
        say("hunt run: --resume lands in PR 3 (feat/hunt-fanout story 7)")
        return 2
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
    hunt_dir = hunt_dir or ledger_mod.HUNT_DIR
    hunt_dir.mkdir(parents=True, exist_ok=True)
    try:
        lock = acquire_lock(hunt_dir)
    except LockHeld as e:
        say(f"hunt run: {e}")
        return 2
    try:
        return _run_locked(cfg, list(stages), harness, hunt_dir, cwd, say, run_id, clock)
    finally:
        release_lock(lock)


def _run_locked(cfg: HuntConfig, stages: list[str], harness: str, hunt_dir: Path, cwd: Path,
                say: Callable[[str], None], run_id: str | None, clock: Callable[[], str] | None) -> int:
    kwargs: dict[str, Any] = {"clock": clock} if clock else {}
    try:
        led = Ledger.create(run_id or new_run_id(), harness, cfg.snapshot(), stages, hunt_dir, **kwargs)
    except FileExistsError as e:
        say(f"hunt run: {e} (a run started this minute; wait for the next one)")
        return 2
    say(f"run {led.run_id} started: {', '.join(stages)} on {harness} ({led.run_dir})")
    ctx = Context(cfg, led, harness, cwd, say)
    failed = stopped = False
    for name in stages:
        if stopped and name != "report":
            led.move_stage(name, "skipped", note="no picks")
            say(f"{name} skipped (no picks)")
            continue
        stage = REGISTRY[name]
        assert stage.run is not None
        led.move_stage(name, "running")
        led.add_units(name, [{"id": name, "input": None, "output": None}])
        led.move_unit(name, name, "running")
        say(f"{name} running")
        try:
            res = stage.run(ctx)
        except Exception as e:  # noqa: BLE001, a crashing stage is a failed stage with its traceback in the log
            with open(ctx.log_path(name, name), "a", encoding="utf-8") as log:
                log.write(traceback.format_exc())
            res = StageResult({}, f"{type(e).__name__}: {e}"[:300])
        fields = dict(res.summary)
        if res.needs_human:
            fields["needs_human"] = list(res.needs_human)
        if fields:
            led.set_summary(name, **fields)
        if res.verdict:
            led.move_unit(name, name, "failed", verdict=res.verdict)
            led.move_stage(name, "failed", note=res.verdict)
            say(f"{name} failed: {res.verdict}")
            failed = True
            break
        led.move_unit(name, name, "done", verdict="ok")
        led.move_stage(name, "done")
        say(f"{name} done  {_summary_line(res)}".rstrip())
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
