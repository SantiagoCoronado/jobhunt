"""src/hunt/pool.py on a fake harness: caps, retries, timeouts, rate-limit waits, verify
failures and the streamed unit log, every transition landing in the ledger."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

from src.hunt import pool as hp
from src.hunt.harness import TOOL_ORDER, Invocation, Result, Usage
from src.hunt.ledger import Ledger

FAKE = '''
import json, os, sys, time
b = json.loads(sys.argv[1])
n = 0
if b.get("counter"):
    p = b["counter"]
    n = int(open(p).read()) if os.path.exists(p) else 0
    open(p, "w").write(str(n + 1))
for line in b.get("stderr", []):
    print(line, file=sys.stderr, flush=True)
time.sleep(b.get("sleep", 0))
if n < b.get("rate_until", 0):
    print("429 too many requests"); sys.exit(1)
if n < b.get("crash_until", 0):
    sys.exit(3)
if n < b.get("fail_until", 0):
    print("boom", file=sys.stderr); sys.exit(1)
if b.get("write"):
    open(b["write"], "w").write("out")
print(json.dumps({"ok": True, "n": n}))
'''


class FakeHarness:
    name = "fake"
    capabilities = frozenset(TOOL_ORDER)

    def __init__(self, script: Path):
        self.script = script

    def argv(self, inv: Invocation) -> list[str]:
        return [sys.executable, str(self.script), inv.prompt]

    def stdin(self, inv: Invocation) -> str | None:
        return None

    def parse(self, stdout: str, stderr: str, rc: int) -> Result:
        if "429" in stdout:
            return Result(Usage(input=1), "429 too many requests", True, stdout.strip())
        if rc != 0 and "boom" in stderr:
            return Result(Usage(input=5, cost_usd=0.001), "boom", False, None)          # a harness-reported error
        if rc != 0:
            return Result(Usage(), f"exit {rc}, no JSON envelope", False, None, envelope=False)
        return Result(Usage(input=10, output=2, cost_usd=0.01), None, False, stdout.strip())

    def models(self):
        return None


@pytest.fixture
def setup(tmp_path):
    script = tmp_path / "fake_harness.py"
    script.write_text(FAKE)
    led = Ledger.create("20260918-1630", "fake", {}, ["triage"], tmp_path / "hunt")
    led.move_stage("triage", "running")
    lines: list[str] = []
    sleeps: list[float] = []
    p = hp.Pool(FakeHarness(script), led, global_concurrency=8, sleep=sleeps.append, emit=lines.append)
    return tmp_path, led, p, lines, sleeps


def _spec(tmp_path: Path, uid: str, behaviour: dict, verify=None, timeout_s: int = 30) -> hp.UnitSpec:
    b = dict(behaviour)
    b.setdefault("counter", str(tmp_path / f"{uid}.count"))
    inv = Invocation(prompt=json.dumps(b), system="", model=None, tools=frozenset(), cwd=tmp_path, timeout_s=timeout_s)
    return hp.UnitSpec("triage", uid, inv, verify or (lambda: None))


def _plan(led: Ledger, *ids: str) -> None:
    led.add_units("triage", [{"id": i, "input": None, "output": None} for i in ids])


def test_happy_path_streams_the_log_and_records_usage(setup):
    tmp, led, p, lines, sleeps = setup
    _plan(led, "u1")
    out = tmp / "u1.out"
    spec = _spec(tmp, "u1", {"stderr": ["reading", "writing"], "write": str(out)},
                 verify=lambda: None if out.exists() else "no output file")
    [o] = p.run_stage("triage", [spec], concurrency=2, attempts=3)
    assert o.state == "done" and o.attempts == 1 and o.waits == 0 and o.verdict == "ok"
    assert o.usage == {"input": 10, "output": 2, "cache_read": None, "cache_create": None, "cost_usd": 0.01}
    u = led.unit("triage", "u1")
    assert u["state"] == "done" and u["attempts"] == 1 and u["usage"]["input"] == 10
    log = (led.run_dir / u["log"]).read_text()
    assert "--- attempt 1:" in log and "reading\nwriting\n" in log and '"ok": true' in log and "--- exit 0" in log
    assert lines == ["triage u1 running attempt 1", "triage u1 done"] and sleeps == []
    assert [e["to"] for e in led.events() if e["unit"] == "u1"] == ["pending", "running", "done"]


def test_retries_consume_attempts_and_accumulate_usage(setup):
    tmp, led, p, lines, sleeps = setup
    _plan(led, "flaky", "dead")
    flaky = _spec(tmp, "flaky", {"fail_until": 1})                      # fails once, then ok
    dead = _spec(tmp, "dead", {"fail_until": 99})
    outs = {o.id: o for o in p.run_stage("triage", [flaky, dead], concurrency=2, attempts=3)}
    assert outs["flaky"].state == "done" and outs["flaky"].attempts == 2
    assert outs["flaky"].usage["input"] == 15 and outs["flaky"].usage["cost_usd"] == pytest.approx(0.011)
    assert outs["dead"].state == "failed" and outs["dead"].attempts == 3 and outs["dead"].verdict == "boom"
    assert led.unit("triage", "dead")["attempts"] == 3 and led.unit("triage", "dead")["state"] == "failed"
    assert "triage dead failed: boom" in lines and lines.count("triage dead failed: boom") == 3
    assert sleeps == []                                                 # a reported error is not a wait
    assert [e["to"] for e in led.events() if e["unit"] == "flaky"] == ["pending", "running", "failed", "running", "done"]


def test_verify_failure_is_an_attempt(setup):
    tmp, led, p, lines, sleeps = setup
    _plan(led, "short")
    calls = []

    def verify():
        calls.append(1)
        return "short output: 40 of 100 ids" if len(calls) == 1 else None
    [o] = p.run_stage("triage", [_spec(tmp, "short", {}, verify=verify)], concurrency=1, attempts=2)
    assert o.state == "done" and o.attempts == 2 and len(calls) == 2
    assert "triage short failed: short output: 40 of 100 ids" in lines


def test_timeout_kills_and_counts_as_an_attempt(setup):
    tmp, led, p, lines, sleeps = setup
    _plan(led, "hang")
    t0 = time.monotonic()
    [o] = p.run_stage("triage", [_spec(tmp, "hang", {"sleep": 30}, timeout_s=1)], concurrency=1, attempts=2)
    assert time.monotonic() - t0 < 6
    assert o.state == "failed" and o.attempts == 2 and o.verdict == "timeout after 1s" and sleeps == []
    log = (led.run_dir / led.unit("triage", "hang")["log"]).read_text()
    assert log.count("--- killed after 1s") == 2


def test_rate_limit_is_a_wait_not_an_attempt(setup):
    tmp, led, p, lines, sleeps = setup
    _plan(led, "rl")
    [o] = p.run_stage("triage", [_spec(tmp, "rl", {"rate_until": 2})], concurrency=1, attempts=1)
    assert o.state == "done" and o.attempts == 1 and o.waits == 2
    assert sleeps == [30, 60]
    assert lines == ["triage rl running attempt 1", "triage rl wait 30s (rate limit)", "triage rl wait 60s (rate limit)", "triage rl done"]
    assert led.unit("triage", "rl")["attempts"] == 1
    assert "--- wait 30s (rate limit signal 1/3)" in (led.run_dir / led.unit("triage", "rl")["log"]).read_text()


def test_three_waits_then_the_attempt_fails_and_a_fast_crash_is_a_signal(setup):
    tmp, led, p, lines, sleeps = setup
    _plan(led, "rl", "crash")
    rl = _spec(tmp, "rl", {"rate_until": 4})                            # 4 signals: 3 waits, then a failed attempt
    crash = _spec(tmp, "crash", {"crash_until": 1})                     # exit 3 in under 10 s, no envelope
    outs = {o.id: o for o in p.run_stage("triage", [rl, crash], concurrency=1, attempts=2)}
    assert outs["rl"].state == "done" and outs["rl"].attempts == 2 and outs["rl"].waits == 3
    assert sleeps[:3] == [30, 60, 120]
    assert led.unit("triage", "rl")["attempts"] == 2
    failed = [e for e in led.events() if e["unit"] == "rl" and e["to"] == "failed"]
    assert failed[0]["note"] == "rate limited 3 times: 429 too many requests"
    assert outs["crash"].state == "done" and outs["crash"].attempts == 1 and outs["crash"].waits == 1
    assert sleeps == [30, 60, 120, 30]


def test_concurrency_caps_bound_the_parallelism(setup):
    tmp, led, p, lines, sleeps = setup
    _plan(led, "a", "b", "c")
    specs = [_spec(tmp, i, {"sleep": 0.4}) for i in "abc"]
    t0 = time.monotonic()
    p.run_stage("triage", specs, concurrency=3, attempts=1)
    wide = time.monotonic() - t0
    assert wide < 1.0, f"3 units at cap 3 took {wide:.2f}s"
    for i in "abc":
        (tmp / f"{i}.count").unlink()
    led2 = Ledger.create("20260918-1631", "fake", {}, ["triage"], tmp / "hunt")
    led2.move_stage("triage", "running")
    _plan(led2, "a", "b", "c")
    narrow_pool = hp.Pool(p.harness, led2, global_concurrency=1, sleep=sleeps.append, emit=lines.append)
    t0 = time.monotonic()
    narrow_pool.run_stage("triage", specs, concurrency=3, attempts=1)  # the global cap wins
    assert time.monotonic() - t0 >= 1.15
    assert all(led2.unit("triage", i)["state"] == "done" for i in "abc")


def test_units_must_be_planned_first_and_empty_is_fine(setup):
    tmp, led, p, lines, sleeps = setup
    assert p.run_stage("triage", [], concurrency=2, attempts=1) == []
    with pytest.raises(ValueError, match="has no unit 'ghost'"):
        p.run_stage("triage", [_spec(tmp, "ghost", {})], concurrency=1, attempts=1)
