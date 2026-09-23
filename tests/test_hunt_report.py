"""report.md on a synthetic ledger (spec section 7): stages, picks with dossier and application
paths, each build's RESUME and LETTER lines, the visa path and relocation line on a dream row,
needs_human, usage per stage; `hunt report` on a finished, a failed and a missing run."""
from __future__ import annotations

import json

import pytest

from src import research as research_mod
from src.hunt import cli, ledger
from src.hunt.stages import report as report_stage

USE = {"input": 1000, "output": 200, "cache_read": 5000, "cache_create": None, "cost_usd": 0.25}


@pytest.fixture
def led(tmp_path, monkeypatch):
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path / "hunt")
    monkeypatch.setattr(research_mod, "COMPANIES_DIR", tmp_path / "research" / "companies")
    (tmp_path / "research" / "companies").mkdir(parents=True)
    (tmp_path / "research" / "companies" / "acme.md").write_text("# Acme\n## Sources\n- researched: 2026-09-18\n")
    led = ledger.Ledger.create("20260918-0700", "claude", {}, ["discover", "triage", "match", "inbox", "pick",
                                                              "research", "tailor", "report"], tmp_path / "hunt")

    def stage(name, summary, units=(), fail=None):
        led.move_stage(name, "running")
        led.add_units(name, [{"id": u, "input": None, "output": None, "harness": h, "model": "m"} for u, h, *_ in units])
        for u, _h, attempts, state in units:
            for _ in range(attempts - 1):
                led.move_unit(name, u, "running")
                led.move_unit(name, u, "failed", verdict="short file: 9 of 10 ids", usage=USE)
            led.move_unit(name, u, "running")
            led.move_unit(name, u, state, verdict="ok" if state == "done" else "build FAIL: EMDASH 1", usage=USE)
        led.set_summary(name, **summary)
        led.move_stage(name, "failed" if fail else "done", note=fail)

    stage("discover", {"sources_ok": 12, "sources_failed": 1, "new": 40, "failed": ["lever"]}, [("discover", None, 1, "done")])
    stage("triage", {"units": 2, "kept": 150, "dropped": 50, "chunk_rows": {"chunk_000": 100}},
          [("chunk_000", "claude", 1, "done"), ("chunk_001", "claude", 2, "done")])
    stage("match", {"scored": 60, "shortlisted": 9, "dream_rows": ["#5 Example Robotics 65 shortlisted"]}, [("p1_chunk_000", "claude", 1, "done")])
    stage("inbox", {"changes": 1, "moves": ["#3 Beta: applied -> screen"],
                    "needs_human": ["inbox: line 3: mail names a data role"]}, [("inbox", "claude", 1, "done")])
    stage("pick", {"picks": 2, "needs_human": ["pick: #9 Jobgether, aggregator row"]}, [("pick", None, 1, "done")])
    stage("research", {"written": 1}, [("example-robotics", "claude", 1, "done")])
    builds = {"job_1": {"ok": True, "folder": str(tmp_path / "applications" / "pending" / "acme-1"), "relocation_line": False,
                        "lines": ["RESUME  fit level 1, 97% fill, 1 page (pdf)        OK", "LETTER  250 words, plain text, relocation line absent   OK"]},
              "job_5": {"ok": False, "folder": str(tmp_path / "applications" / "pending" / "example-robotics-5"), "relocation_line": True,
                        "lines": ["RESUME  fit level 2, 99% fill        OK", "LETTER  262 words, plain text, relocation line present   FAIL",
                                  "FAIL    em-dash in CoverLetter.md line 9"]}}
    stage("tailor", {"picks": 2, "passed": 1, "builds": builds, "needs_human": ["tailor: job_5 did not pass its build after the fix round"]},
          [("job_1", "claude", 1, "done"), ("job_5", "claude", 2, "failed")], fail="1 of 2 tailor unit(s) failed")
    (led.run_dir / "picks.json").write_text(json.dumps({"picks": [
        {"id": 1, "company": "Acme", "title": "Backend Engineer", "location": "Remote", "match": 90, "dream": False},
        {"id": 5, "company": "Example Robotics", "title": "AI Engineer", "location": "Berlin", "match": 65, "dream": True,
         "visa_path": "EU national, no sponsorship needed"}]}))
    return led


def test_report_carries_every_section_7_item(led, capsys):
    assert cli.main(["report", "20260918-0700"]) == 0
    out = capsys.readouterr().out
    assert out == (led.run_dir / "report.md").read_text()
    assert out.startswith("# Hunt 20260918-0700\n") and "state failed." in out
    assert "| triage | done | 2/2 | units 2, kept 150, dropped 50 |" in out
    assert "| tailor | failed (1 of 2 tailor unit(s) failed) | 1/2 | picks 2, passed 1 |" in out and "| report | pending | 0/0 |  |" in out
    assert "- discover failed: lever" in out and "- match dream_rows: #5 Example Robotics 65 shortlisted" in out
    assert "- inbox moves: #3 Beta: applied -> screen" in out and "chunk_rows" not in out
    assert "- tailor unit job_5 failed after 2 attempt(s): build FAIL: EMDASH 1" in out
    assert "- #1 Acme: Backend Engineer (Remote, match 90)\n  - dossier: " in out and "acme.md (researched 2026-09-18)" in out
    assert "acme-1 (build PASS)\n  - RESUME  fit level 1, 97% fill, 1 page (pdf)        OK\n  - LETTER  250 words" in out
    assert "- #5 Example Robotics: AI Engineer (Berlin, match 65, dream)" in out and "example-robotics.md (missing)" in out
    assert "example-robotics-5 (build FAIL)" in out and "  - FAIL    em-dash in CoverLetter.md line 9" in out
    assert "  - visa path: EU national, no sponsorship needed\n  - relocation line in the letter: present" in out
    needs = out.split("## Needs a human")[1].split("## Usage")[0]
    assert [ln for ln in needs.splitlines() if ln] == ["- inbox: line 3: mail names a data role", "- pick: #9 Jobgether, aggregator row",
                                                       "- tailor: job_5 did not pass its build after the fix round"]
    assert "| triage | 2 | 3 | 3,000 | 600 | 15,000 | - | 0.75 |" in out          # 3 attempts, usage summed over them
    assert "| tailor | 2 | 3 | 3,000 | 600 | 15,000 | - | 0.75 |" in out
    assert "| total | 7 | 9 | 9,000 | 1,800 | 45,000 | - | 2.25 |" in out and "| discover |" not in out.split("## Usage")[1]
    assert "| harness | models | units | attempts |" in out and "| claude | m | 7 | 9 | 9,000 | 1,800 | 45,000 | - | 2.25 |" in out
    assert out.count("| total | m | 7 | 9 |") == 1                  # the harness table has its own total row
    assert "\u2014" not in out


def test_report_on_an_empty_run_a_missing_run_and_an_unreadable_one(led, capsys, tmp_path):
    fresh = ledger.Ledger.create("20260918-0800", "claude", {}, ["discover"], tmp_path / "hunt")
    md = report_stage.render_markdown(fresh)
    assert "| discover | pending | 0/0 |  |" in md and "## Needs a human\n\n- nothing" in md and "No model unit ran." in md
    assert "## Picks" not in md
    assert cli.main(["report", "20260101-0000"]) == 1 and "no run '20260101-0000'" in capsys.readouterr().out
    (tmp_path / "hunt" / "20260918-0900").mkdir()
    assert cli.main(["report", "latest"]) == 2 and "unreadable ledger" in capsys.readouterr().out
