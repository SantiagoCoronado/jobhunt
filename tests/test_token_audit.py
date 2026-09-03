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
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    d = ta.project_dir_for(Path("/Users/x/jobhunt"))
    assert d.name == "-Users-x-jobhunt" and d.parent.name == "projects"
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/tmp/override")
    assert ta.project_dir_for(Path("/Users/x/jobhunt")) == Path("/tmp/override")


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
