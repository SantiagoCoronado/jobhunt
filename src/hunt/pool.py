"""The pool (spec decisions 10 and 11): runs a stage's units through a harness, one process
per unit, under the stage's concurrency cap and the run's global cap.

Per unit: attempt = one process; a timeout, a non-zero exit, a harness-reported error or a
failed output check each consume one attempt (`retries = N` in hunt.toml is `1 + N` attempts).
A rate-limit signal (the envelope says so, or the process died in under 10 s WITHOUT an
envelope) is a wait, not an attempt: sleep 30, 60, then 120 s and run the same attempt again;
after the third consecutive wait the attempt is marked failed and the counter moves. Every
transition goes through the ledger (state.json + events.jsonl); stderr streams into
`logs/<stage>/<unit>.log` while the process runs and the envelope is appended when it ends,
so `hunt status` can show the last line of a running unit. The agent's reply is never parsed
for a decision: the unit's `verify` callable looks at the output file (decision 4).
"""
from __future__ import annotations

import subprocess
import threading
import time
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .harness import Harness, Invocation, Result, Usage
from .ledger import Ledger, add_usage

BACKOFF_S: tuple[int, ...] = (30, 60, 120)
FAST_FAIL_S = 10.0


@dataclass(frozen=True)
class UnitSpec:
    stage: str
    id: str
    invocation: Invocation
    verify: Callable[[], str | None]     # None when the output passes, else why it did not


@dataclass(frozen=True)
class Outcome:
    stage: str
    id: str
    state: str                            # done | failed
    attempts: int
    verdict: str | None
    usage: dict[str, Any] | None
    waits: int                            # rate-limit waits over the whole unit


@dataclass
class _Exec:
    rc: int
    stdout: str
    stderr: str
    timed_out: bool
    elapsed: float


class Pool:
    def __init__(self, harness: Harness, ledger: Ledger, global_concurrency: int = 8,
                 backoff_s: Sequence[int] = BACKOFF_S, sleep: Callable[[float], None] = time.sleep,
                 emit: Callable[[str], None] | None = None):
        self.harness = harness
        self.ledger = ledger
        self.global_slots = threading.BoundedSemaphore(max(1, global_concurrency))
        self.backoff_s = tuple(backoff_s)
        self.sleep = sleep
        self.emit = emit or (lambda line: print(line, flush=True))

    # -- the stage entry point
    def run_stage(self, stage: str, specs: Sequence[UnitSpec], concurrency: int, attempts: int) -> list[Outcome]:
        """Run every unit of one stage; returns one Outcome per spec, in spec order."""
        for spec in specs:
            self.ledger.unit(stage, spec.id)                     # planned first, or it is a bug
        if not specs:
            return []
        with ThreadPoolExecutor(max_workers=max(1, concurrency)) as ex:
            return list(ex.map(lambda s: self._run_unit(s, attempts), specs))

    # -- one unit
    def _run_unit(self, spec: UnitSpec, max_attempts: int) -> Outcome:
        stage, uid = spec.stage, spec.id
        log_path = self.ledger.run_dir / self.ledger.unit(stage, uid)["log"]
        log_path.parent.mkdir(parents=True, exist_ok=True)
        attempts, waits_total = 0, 0
        verdict: str | None = None
        while True:
            self.ledger.move_unit(stage, uid, "running")
            attempts += 1
            self.emit(f"{stage} {uid} running attempt {attempts}")
            usage: dict[str, Any] | None = None
            waits = 0
            while True:                                          # one attempt, with rate-limit waits
                with self.global_slots:
                    ex = self._execute(spec.invocation, log_path, attempts)
                res = self._result(ex, spec.invocation.timeout_s)
                usage = _merge(usage, res.usage)
                if self._rate_limited(res, ex) and waits < len(self.backoff_s):
                    wait = self.backoff_s[waits]
                    waits += 1
                    waits_total += 1
                    self._log(log_path, f"--- wait {wait}s (rate limit signal {waits}/{len(self.backoff_s)}): {res.error}")
                    self.emit(f"{stage} {uid} wait {wait}s (rate limit)")
                    self.sleep(wait)
                    continue
                break
            if self._rate_limited(res, ex):
                verdict = f"rate limited {waits} times: {res.error}"
            elif res.error:
                verdict = res.error
            else:
                verdict = spec.verify()
            if verdict is None:
                self.ledger.move_unit(stage, uid, "done", verdict="ok", usage=usage)
                self.emit(f"{stage} {uid} done")
                return Outcome(stage, uid, "done", attempts, "ok", self.ledger.unit(stage, uid)["usage"], waits_total)
            self.ledger.move_unit(stage, uid, "failed", verdict=verdict, usage=usage)
            self.emit(f"{stage} {uid} failed: {verdict}")
            if attempts >= max_attempts:
                return Outcome(stage, uid, "failed", attempts, verdict, self.ledger.unit(stage, uid)["usage"], waits_total)

    # -- helpers
    def _rate_limited(self, res: Result, ex: _Exec) -> bool:
        if ex.timed_out:
            return False
        return res.rate_limited or (ex.rc != 0 and not res.envelope and ex.elapsed < FAST_FAIL_S)

    def _result(self, ex: _Exec, timeout_s: int) -> Result:
        if ex.timed_out:
            return Result(Usage(), f"timeout after {timeout_s}s", False, None, envelope=False)
        return self.harness.parse(ex.stdout, ex.stderr, ex.rc)

    @staticmethod
    def _log(log_path: Path, line: str) -> None:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line.rstrip("\n") + "\n")

    def _execute(self, inv: Invocation, log_path: Path, attempt: int) -> _Exec:
        """One process: stderr streams to the log as it comes, stdout (the envelope) is kept
        and appended at the end, the timeout kills the process."""
        argv = self.harness.argv(inv)
        stdin = self.harness.stdin(inv)
        out_lines: list[str] = []
        started = time.monotonic()
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(f"--- attempt {attempt}: {' '.join(argv[:3])} ... ({len(argv)} args)\n")
            log.flush()
            proc = subprocess.Popen(argv, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=inv.cwd, text=True,
                                    encoding="utf-8", errors="replace")

            def pump_err() -> None:
                assert proc.stderr is not None
                for line in proc.stderr:
                    log.write(line)
                    log.flush()
                    err_lines.append(line)

            def pump_out() -> None:
                assert proc.stdout is not None
                for line in proc.stdout:
                    out_lines.append(line)

            def feed() -> None:
                assert proc.stdin is not None
                try:
                    proc.stdin.write(stdin or "")
                    proc.stdin.close()
                except (BrokenPipeError, OSError):
                    pass

            err_lines: list[str] = []
            threads = [threading.Thread(target=pump_err, daemon=True), threading.Thread(target=pump_out, daemon=True)]
            if stdin is not None:
                threads.append(threading.Thread(target=feed, daemon=True))
            for t in threads:
                t.start()
            timed_out = False
            try:
                proc.wait(timeout=inv.timeout_s)
            except subprocess.TimeoutExpired:
                timed_out = True
                proc.kill()
                proc.wait()
            for t in threads:
                t.join(timeout=5)
            elapsed = time.monotonic() - started
            stdout = "".join(out_lines)
            if timed_out:
                log.write(f"--- killed after {inv.timeout_s}s\n")
            if stdout.strip():
                log.write("--- stdout:\n" + stdout + ("" if stdout.endswith("\n") else "\n"))
            log.write(f"--- exit {proc.returncode} after {elapsed:.1f}s\n")
        return _Exec(proc.returncode, stdout, "".join(err_lines), timed_out, elapsed)


def _merge(total: dict[str, Any] | None, usage: Usage) -> dict[str, Any] | None:
    return add_usage(total, usage.as_dict())
