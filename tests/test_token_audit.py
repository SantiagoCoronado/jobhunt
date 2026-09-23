"""scripts/token_audit.py: real API calls only, synthetic placeholders excluded, clean exit on an empty project dir."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("token_audit", Path(__file__).resolve().parents[1] / "scripts" / "token_audit.py")
ta = importlib.util.module_from_spec(SPEC)
sys.modules["token_audit"] = ta
SPEC.loader.exec_module(ta)


def _assistant(rid, model, usage, content):
    return {"type": "assistant", "requestId": rid, "timestamp": "2026-09-02T18:00:00Z",
            "message": {"model": model, "usage": usage, "content": content}}


def test_synthetic_and_duplicate_lines_are_not_calls(tmp_path):
    real = {"input_tokens": 5, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 0, "output_tokens": 20}
    zero = {"input_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens": 0}
    lines = [
        _assistant("r1", "claude-fable-5-1", real, [{"type": "text", "text": "hi"}]),
        _assistant("r1", "claude-fable-5-1", real, [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "ls"}}]),
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "content": "a" * 40}]}},
        _assistant("r2", "<synthetic>", zero, [{"type": "text", "text": "You've hit your session limit"}]),
        _assistant("r3", "claude-fable-5-1", real, [{"type": "text", "text": "done"}]),
    ]
    p = tmp_path / "s.jsonl"
    p.write_text("\n".join(json.dumps(x) for x in lines))
    rep = ta.scan_file(p)
    assert rep["usage"]["calls"] == 2
    assert rep["usage"]["context_total"] == 210
    assert rep["tool_bytes"]["Bash"] == 40 and rep["tool_calls"]["Bash"] == 1


def test_messages_without_request_id_are_counted_not_deduped(tmp_path):
    real = {"input_tokens": 5, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 0, "output_tokens": 20}
    lines = [
        {"type": "assistant", "message": {"model": "claude-fable-5-1", "usage": real, "content": [{"type": "text", "text": "a"}]}},
        {"type": "assistant", "message": {"model": "claude-fable-5-1", "usage": real, "content": [{"type": "text", "text": "b"}]}},
    ]
    p = tmp_path / "s.jsonl"
    p.write_text("\n".join(json.dumps(x) for x in lines))
    assert ta.scan_file(p)["usage"]["calls"] == 2


def test_project_dir_derived_from_repo_path(monkeypatch):
    monkeypatch.delenv("JOBHUNT_TRANSCRIPTS_DIR", raising=False)
    d = ta.project_dir_for(Path("/Users/x/jobhunt"))
    assert d.name == "-Users-x-jobhunt" and d.parent.name == "projects"
    monkeypatch.setenv("JOBHUNT_TRANSCRIPTS_DIR", "/tmp/override")
    assert ta.project_dir_for(Path("/Users/x/jobhunt")) == Path("/tmp/override")


def test_claude_project_dir_is_not_read(monkeypatch):
    """Claude Code sets it to the repo root and exports it to hooks; it must not steer the audit."""
    monkeypatch.delenv("JOBHUNT_TRANSCRIPTS_DIR", raising=False)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/Users/x/jobhunt")
    assert ta.project_dir_for(Path("/Users/x/jobhunt")).name == "-Users-x-jobhunt"


def test_resolve_exits_cleanly_on_empty_project_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(ta, "PROJECT_DIR", tmp_path)
    with pytest.raises(SystemExit) as e:
        ta.resolve(None, latest=True)
    assert "no sessions" in str(e.value)


def test_prefix_lookup_prefers_the_newest_match(tmp_path, monkeypatch, capsys):
    import os
    import time
    monkeypatch.setattr(ta, "PROJECT_DIR", tmp_path)
    old = tmp_path / "abc-old.jsonl"
    new = tmp_path / "abc-new.jsonl"
    old.write_text("")
    new.write_text("")
    now = time.time()
    os.utime(old, (now - 100, now - 100))
    os.utime(new, (now, now))
    assert ta.resolve("abc", latest=False) == new
    assert "2 sessions match" in capsys.readouterr().err


def _hunt(hunt_dir: Path):
    """A ledger with two model stages on two harnesses, one retry, and a deterministic stage."""
    from src.hunt import ledger
    led = ledger.Ledger.create("20260922-0900", "claude", {}, ["discover", "triage", "tailor"], hunt_dir)
    led.move_stage("discover", "running")
    led.add_units("discover", [{"id": "discover", "input": None, "output": None}])
    led.move_unit("discover", "discover", "running")
    led.move_unit("discover", "discover", "done")
    led.move_stage("discover", "done")
    led.move_stage("triage", "running")
    led.add_units("triage", [{"id": f"chunk_00{i}", "input": None, "output": None, "harness": "claude", "model": "haiku"} for i in range(2)])
    led.move_unit("triage", "chunk_000", "running")
    led.move_unit("triage", "chunk_000", "done", usage={"input": 1000, "output": 100, "cache_read": 4000, "cost_usd": 0.10})
    led.move_unit("triage", "chunk_001", "running")
    led.move_unit("triage", "chunk_001", "failed", verdict="short", usage={"input": 900, "output": 10})
    led.move_unit("triage", "chunk_001", "running")
    led.move_unit("triage", "chunk_001", "done", usage={"input": 1100, "output": 120, "cost_usd": 0.12})
    led.move_stage("triage", "done")
    led.move_stage("tailor", "running")
    led.add_units("tailor", [{"id": "job_7", "input": None, "output": None, "harness": "codex", "model": None}])
    led.move_unit("tailor", "job_7", "running")
    led.move_unit("tailor", "job_7", "done", usage={"input": 20000, "output": 3000, "cache_create": 5000})
    led.move_stage("tailor", "done")
    led.finish()
    return led


def test_hunt_mode_reads_the_ledger_per_stage_harness_and_unit(tmp_path, monkeypatch, capsys):
    from src.hunt import ledger
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path)
    _hunt(tmp_path)
    ta.main.__globals__["sys"].argv = ["token_audit.py", "--hunt", "latest", "--top", "2", "--json", str(tmp_path / "out.json")]
    ta.main()
    out = capsys.readouterr().out
    assert out.startswith("# Token audit: hunt 20260922-0900 (claude, done)\n")
    assert "  units            3  (4 attempts, 1 retries)" in out
    assert "  context read     32.0k  (input 23.0k + cache_read 4.0k + cache_create 5.0k)" in out
    assert "  cost usd         0.22" in out and "  models           default, haiku" in out
    assert "  triage           2        3       7.0k      4.0k         -      230    0.22  haiku" in out
    assert "  codex            1        1      25.0k         -      5.0k     3.0k       -  default" in out
    assert out.count("  total            3        4      32.0k") == 2            # one total row per table
    biggest = out.split("## 2 biggest units by context read")[1].split("\n\n")[0].splitlines()
    assert biggest[2].startswith("  tailor/job_7") and "codex/default" in biggest[2]
    assert biggest[3].startswith("  triage/chunk_000") and len(biggest) == 4        # --top 2, chunk_001 cut
    assert "(json written to" in out
    rep = json.loads((tmp_path / "out.json").read_text())
    assert rep["total"]["context_total"] == 32000 and [u["id"] for u in rep["units"]] == ["job_7", "chunk_000", "chunk_001"]
    assert rep["units"][2]["attempts"] == 2 and rep["units"][2]["context_total"] == 2000


def test_hunt_mode_names_the_missing_run_and_the_ledger_dir(tmp_path, monkeypatch):
    from src.hunt import ledger
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path)
    with pytest.raises(SystemExit) as e:
        ta.resolve_hunt("latest")
    assert str(e.value).startswith("no hunt runs yet under")
    with pytest.raises(SystemExit) as e:
        ta.resolve_hunt("20260101-0000")
    assert "no run '20260101-0000'" in str(e.value)


def test_hunt_mode_exits_cleanly_on_an_empty_or_broken_ledger_folder(tmp_path, monkeypatch):
    """`ledger.resolve` hands back any run folder that exists, readable or not (Cursor review
    of PR #33): an empty folder and a broken state.json name the folder instead of a traceback,
    by id and as `latest` (the newest folder is the broken one)."""
    from src.hunt import ledger
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path)
    _hunt(tmp_path)
    (tmp_path / "20260923-0900").mkdir()                                            # no state.json
    (tmp_path / "20260924-0900").mkdir()
    (tmp_path / "20260924-0900" / "state.json").write_text("{not json", encoding="utf-8")
    for run in ("20260923-0900", "20260924-0900", "latest"):
        with pytest.raises(SystemExit) as e:
            ta.resolve_hunt(run)
        assert str(e.value).startswith(f"unreadable ledger {tmp_path / (run if run != 'latest' else '20260924-0900')}: ")
    assert "not valid JSON" in str(e.value)                                          # latest = the broken state.json
    assert ta.resolve_hunt("20260922-0900") == tmp_path / "20260922-0900"          # the readable one still resolves


def test_hunt_mode_counts_retries_per_unit_so_pending_units_never_go_negative(tmp_path, monkeypatch, capsys):
    from src.hunt import ledger
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path)
    led = ledger.Ledger.create("20260922-1000", "claude", {}, ["triage"], tmp_path)
    led.move_stage("triage", "running")
    led.add_units("triage", [{"id": f"chunk_00{i}", "input": None, "output": None, "harness": "claude", "model": "haiku"} for i in range(3)])
    led.move_unit("triage", "chunk_000", "running")                               # one running, two pending
    rep = ta.scan_hunt(tmp_path / "20260922-1000")
    assert rep["total"]["units"] == 3 and rep["total"]["attempts"] == 1 and rep["total"]["retries"] == 0
    ta.print_hunt_report(rep, 5)
    assert "  units            3  (1 attempts, 0 retries)" in capsys.readouterr().out
