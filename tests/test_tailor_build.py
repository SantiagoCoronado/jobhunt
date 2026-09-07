"""tailor_build: split draft.md, deterministic checks, render, verdict, exit codes (hermetic, --no-pdf)."""
from __future__ import annotations

import json

import pytest
import yaml

from src import tailor_build as tb
from src.config import user_file
from src.dream import relocation_line

from src import render_docx as _rd

_real_estimate = _rd.estimate_height_pts

RESUME = "AlexExampleResume.yaml"
RESUME_DOCX = "AlexExampleResume.docx"
NAME = "Alex Example"
CONTACT = "Lisbon, Portugal | alex@example.com | +351-900-000-000"


def _body(words: int) -> str:
    sentence = "I build and ship production software with small teams and honest metrics."
    out: list[str] = []
    while sum(len(s.split()) for s in out) < words:
        out.append(sentence)
    text = " ".join(out).split()
    return " ".join(text[:words]) + "."


def letter(words: int = 250, extra: str = "") -> str:
    """A plain-text letter whose body (everything after the Re: line) has exactly `words` words."""
    fixed = len("Dear Acme team,".split()) + len("Sincerely,".split()) + len(NAME.split()) + len(extra.split())
    return f"{NAME}\n{CONTACT}\nRe: Senior Engineer, Acme\n\nDear Acme team,\n\n{_body(words - fixed)}\n{extra}\n\nSincerely,\n{NAME}\n"


def small_resume(location: str = "Lisbon, Portugal") -> dict:
    master = yaml.safe_load(user_file("master_resume").read_text())
    cv = master["cv"]
    secs = cv["sections"]
    return {"cv": {**cv, "location": location, "sections": {
        "summary": secs["summary"][:1],
        "experience": [{**secs["experience"][0], "highlights": secs["experience"][0]["highlights"][:3]}],
        "projects": [{**secs["projects"][0], "highlights": secs["projects"][0]["highlights"][:2]}] if secs.get("projects") else [],
        "skills": secs["skills"][:3],
        "education": secs.get("education", [])[:1],
    }}}


@pytest.fixture(autouse=True)
def clean_audit(monkeypatch):
    """The fixture resume is cut from the unfitted master and fills ~70% of a page; audit and
    fill behaviour have their own tests, so the other checks see a clean, full page."""
    monkeypatch.setattr(tb.rd, "audit_line_fill", lambda data, level: [])
    real_estimate = tb.rd.estimate_height_pts
    monkeypatch.setattr(tb.rd, "estimate_height_pts",
                        lambda data, level: max(real_estimate(data, level), tb.rd.PAGE_AVAIL_PTS * 0.97))


@pytest.fixture
def folder(tmp_path):
    d = tmp_path / "acme-7"
    d.mkdir()
    (d / RESUME).write_text(yaml.safe_dump(small_resume(), allow_unicode=True, sort_keys=False))
    (d / "CoverLetter.md").write_text(letter())
    (d / "match_report.md").write_text("# Match report\n\nGaps: none.\n")
    (d / "answers.md").write_text("## Why Acme?\nBecause of the product.\n")
    return d


JOB = {"id": 7, "company": "Acme", "dream": False}


def test_green_build_writes_build_and_state(folder):
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert v.ok, v.failures
    assert (folder / RESUME_DOCX).exists()
    assert (folder / "CoverLetter.docx").exists()
    doc = json.loads((folder / "build.json").read_text())
    assert doc["ok"] is True and doc["stage"] == "tailor" and doc["job_id"] == 7
    assert doc["metrics"]["letter_words"] == 250
    state = json.loads((folder / "state.json").read_text())
    assert "built" in state["stages"] and state["last_verdict_ok"] is True
    assert len(v.lines) <= 12 and v.lines[-1].startswith("RESULT  OK")


def test_split_draft_writes_allowed_files_and_removes_draft(folder):
    (folder / RESUME).unlink()
    (folder / "CoverLetter.md").unlink()
    draft = (f"=== FILE: {RESUME} ===\n"
             + yaml.safe_dump(small_resume(), allow_unicode=True, sort_keys=False)
             + "=== FILE: CoverLetter.md ===\n" + letter()
             + "=== FILE: match_report.md ===\n# report\n")
    (folder / "draft.md").write_text(draft)
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert v.ok, v.failures
    assert not (folder / "draft.md").exists()
    assert (folder / "CoverLetter.md").read_text().startswith(NAME)
    assert v.metrics["split"] == [RESUME, "CoverLetter.md", "match_report.md"]


def test_split_rejects_unknown_file_name(folder):
    (folder / "draft.md").write_text("=== FILE: evil.sh ===\nrm -rf /\n")
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert not v.ok and "unknown file" in v.failures[0]
    assert not (folder / "evil.sh").exists()


def test_missing_required_file_fails(folder):
    (folder / "match_report.md").unlink()
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert not v.ok and "missing match_report.md" in v.failures[0]


def test_emdash_anywhere_fails_with_location(folder):
    (folder / "match_report.md").write_text("line one\nbad — dash\n")
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert not v.ok and any("match_report.md:2" in f for f in v.failures)


def test_tailor_marker_left_fails(folder):
    (folder / "answers.md").write_text("## Why Acme?\n<!-- TAILOR: replace -->\nTEMPLATE\n"
                                        "## What do you know about Acme?\n<!-- TAILOR: three facts -->\nTEMPLATE\n")
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert not v.ok and any("2 TAILOR block(s) under: Why Acme?; What do you know about Acme?" in f for f in v.failures)


def test_markdown_in_letter_fails(folder):
    (folder / "CoverLetter.md").write_text(letter().replace("Re: ", "**Re: "))
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert not v.ok and any("Markdown" in f for f in v.failures)


@pytest.mark.parametrize("words,ok", [(219, False), (220, True), (280, True), (281, False)])
def test_letter_word_bounds(folder, words, ok):
    (folder / "CoverLetter.md").write_text(letter(words))
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert v.ok is ok, v.failures
    assert v.metrics["letter_words"] == words


def test_letter_without_re_line_fails(folder):
    (folder / "CoverLetter.md").write_text(f"{NAME}\n{CONTACT}\n\nDear team,\n\n{_body(250)}\n")
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert not v.ok and any("Re:" in f for f in v.failures)


def test_dream_header_without_relocation_line_fails(folder):
    res = small_resume("Mexico City, Mexico (open to US relocation, TN eligible)")
    (folder / RESUME).write_text(yaml.safe_dump(res, allow_unicode=True, sort_keys=False))
    v = tb.build(folder, job={"id": 7, "company": "NVIDIA", "dream": True}, no_pdf=True)
    assert not v.ok and any(relocation_line() in f for f in v.failures)


def test_dream_relocation_line_matches_header(folder):
    res = small_resume("Mexico City, Mexico (open to US relocation, TN eligible)")
    (folder / RESUME).write_text(yaml.safe_dump(res, allow_unicode=True, sort_keys=False))
    (folder / "CoverLetter.md").write_text(letter(240, relocation_line()))
    v = tb.build(folder, job={"id": 7, "company": "NVIDIA", "dream": True}, no_pdf=True)
    assert v.ok, v.failures
    assert v.metrics["relocation_line"] is True


def test_dream_letter_line_without_header_fails(folder):
    (folder / "CoverLetter.md").write_text(letter(240, relocation_line()))
    v = tb.build(folder, job={"id": 7, "company": "NVIDIA", "dream": True}, no_pdf=True)
    assert not v.ok and any("header" in f for f in v.failures)


def test_non_dream_relocation_line_is_only_a_warning(folder):
    (folder / "CoverLetter.md").write_text(letter(240, relocation_line()))
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert v.ok and any("non-dream" in w for w in v.warnings)


def test_overflow_at_level_3_fails(folder, monkeypatch):
    monkeypatch.setattr(tb.rd, "estimate_height_pts", tb.rd.estimate_height_pts.__wrapped__
                        if hasattr(tb.rd.estimate_height_pts, "__wrapped__") else _real_estimate)
    res = small_resume()
    long_bullet = "Shipped a feature that mattered to customers and measured the outcome honestly across teams. " * 3
    res["cv"]["sections"]["experience"][0]["highlights"] = [long_bullet] * 30
    (folder / RESUME).write_text(yaml.safe_dump(res, allow_unicode=True, sort_keys=False))
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert not v.ok and any("fit level 3" in f for f in v.failures)
    assert v.metrics["fit_level"] == 3


def test_audit_findings_warn_then_fail(folder, monkeypatch):
    monkeypatch.setattr(tb.rd, "audit_line_fill", lambda data, level: ["[b1] 2 lines, last 40% full"] * 2)
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert v.ok and v.metrics["audit_findings"] == 2 and any("AUDIT   2 block" in ln for ln in v.lines)
    monkeypatch.setattr(tb.rd, "audit_line_fill", lambda data, level: ["[b1] 2 lines, last 40% full"] * 4)
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert not v.ok and any("trailing white space" in f for f in v.failures)


def test_broken_yaml_fails_cleanly(folder):
    (folder / RESUME).write_text("cv: [unclosed\n")
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert not v.ok and "does not parse" in v.failures[0]


def test_review_items_tracked_and_resolved_by_response(folder):
    review = {"reviewer": "cv-reviewer", "at": "2026-09-03T00:00:00Z", "items": [
        {"id": 1, "file": "CoverLetter.md", "anchor": "p2", "severity": "must", "comment": "hook repeats", "resolved": False},
        {"id": 2, "file": RESUME, "anchor": "experience/0", "severity": "nit", "comment": "tighten", "resolved": False},
    ]}
    (folder / "review.json").write_text(json.dumps(review))
    v = tb.build(folder, job=JOB, no_pdf=True, strict_review=True)
    assert not v.ok and any("must-fix" in f for f in v.failures)
    (folder / "review_response.md").write_text("#1 rewrote the hook paragraph.\n")
    v = tb.build(folder, job=JOB, no_pdf=True, strict_review=True)
    assert v.ok, v.failures
    assert v.metrics["review_open"] == 1
    assert json.loads((folder / "review.json").read_text())["items"][0]["resolved"] is True


def test_cli_exit_codes_and_json(folder, capsys):
    rc = tb.main([str(folder), "--no-pdf", "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is True and out["verdict"][-1].startswith("RESULT")
    (folder / "match_report.md").write_text("x — y\n")
    assert tb.main([str(folder), "--no-pdf"]) == 1


def test_missing_folder_fails_without_writing(tmp_path):
    v = tb.build(tmp_path / "gone-9", job=JOB, no_pdf=True)
    assert not v.ok and "not a folder" in v.failures[0]
    assert not (tmp_path / "gone-9").exists()


def test_failures_and_warnings_print_in_verdict_lines(folder):
    (folder / "match_report.md").write_text("line one\nbad \u2014 dash\n")
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert any(ln.startswith("FAIL") and "match_report.md:2" in ln for ln in v.lines)
    res = small_resume("Mexico City, Mexico (open to US relocation, TN eligible)")
    (folder / "match_report.md").write_text("clean\n")
    (folder / RESUME).write_text(yaml.safe_dump(res, allow_unicode=True, sort_keys=False))
    v = tb.build(folder, job={"id": 7, "company": "NVIDIA", "dream": True}, no_pdf=True)
    assert any(ln.startswith("LETTER") and ln.rstrip().endswith("FAIL") for ln in v.lines)
    assert any(ln.startswith("FAIL") and "relocation_line" in ln for ln in v.lines)
    assert v.lines[-1].startswith("RESULT") and len(v.lines) <= 12


def test_underfill_at_level_0_is_a_failure_with_free_lines(folder, monkeypatch):
    monkeypatch.setattr(tb.rd, "estimate_height_pts", lambda data, level: tb.rd.PAGE_AVAIL_PTS * 0.91)
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert not v.ok and any("body lines free" in f for f in v.failures)
    assert v.metrics["free_lines"] > 0
    assert any(ln.startswith("FAIL") and "body lines free" in ln for ln in v.lines)


def test_split_strips_code_fences(folder):
    (folder / RESUME).unlink()
    draft = (f"=== FILE: {RESUME} ===\n```yaml\n"
             + yaml.safe_dump(small_resume(), allow_unicode=True, sort_keys=False)
             + "```\n=== FILE: CoverLetter.md ===\n```\n" + letter() + "```\n")
    (folder / "draft.md").write_text(draft)
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert v.ok, v.failures
    assert not (folder / RESUME).read_text().startswith("```")


def test_non_us_dream_row_rejects_tn_line_and_wants_visa_note(folder):
    berlin = {"id": 7, "company": "Peec", "dream": True, "location": "Berlin"}
    (folder / "CoverLetter.md").write_text(letter(240, relocation_line()))
    v = tb.build(folder, job=berlin, no_pdf=True)
    assert not v.ok and any("outside the TN countries" in f for f in v.failures)
    (folder / "CoverLetter.md").write_text(letter(240))
    v = tb.build(folder, job=berlin, no_pdf=True)
    assert v.ok and any("no visa note" in w for w in v.warnings)
    (folder / "CoverLetter.md").write_text(letter(240, "A German or EU work visa would be needed."))
    v = tb.build(folder, job=berlin, no_pdf=True)
    assert v.ok and not any("visa" in w for w in v.warnings)


def test_missing_pypdf_is_a_printed_warning_not_a_silent_pass(folder, monkeypatch):
    monkeypatch.setattr(tb.rd, "to_pdf", lambda docx: docx.with_suffix(".pdf"))
    monkeypatch.setattr(tb, "_pdf_pages", lambda pdf: None)
    v = tb.build(folder, job=JOB, no_pdf=False)
    assert v.ok
    assert any(ln.startswith("RESUME") and "page count skipped" in ln for ln in v.lines)
    assert any("pypdf" in w for w in v.warnings)


def test_cap_keeps_fail_and_result_lines():
    lines = ["BUILD x", "RESUME y", "AUDIT z"] + [f"WARN {i}" for i in range(6)] + ["FAIL a", "FAIL b", "FILES f", "RESULT FAIL"]
    out = tb._cap(list(lines), 12)
    assert len(out) <= 12 and "FAIL a" in out and "FAIL b" in out and out[-1] == "RESULT FAIL"
    assert "FILES f" not in out


def test_header_tn_item_not_duplicated_with_relocation_header():
    from src.render_docx import _contact_items
    cv = {"phone": "+52", "email": "a@b.c", "location": "Mexico City, Mexico (open to US relocation, TN eligible)",
          "sections": {"additional": [{"label": "Work authorization", "details": "Mexico (citizen) · TN Visa eligible"}]}}
    texts = [t for t, _ in _contact_items(cv)]
    assert sum("tn" in t.lower() for t in texts) == 1
    cv["location"] = "Mexico City, Mexico"
    texts = [t for t, _ in _contact_items(cv)]
    assert "TN Visa Eligible" in texts


@pytest.mark.parametrize("location,expected", [
    ("Berlin", True), ("London, GB", True), ("Singapore", True), ("Remote, EU", True), ("Bangalore, India", True),
    ("Bengaluru, Karnataka, in", True), ("Berlin, DE", True), ("Tel Aviv, IL", True), ("Berlin, Germany", True),
    ("Indianapolis, IN, USA", False), ("Ukiah, CA", False), ("Paris, TX", False), ("New Madrid, MO", False),
    ("London, KY", False), ("London, UK; San Francisco, CA", False), ("Remote (US) or London", False),
    ("Santa Clara, CA", False), ("Mexico City", False), ("Toronto, Canada", False), ("Remote", False), ("", False),
    (None, False), ("US remote", False),
    # A US option anywhere in a multi-region string keeps the row TN-eligible, including the
    # spelled-out state names and the bare "US" the marker list used not to recognise.
    ("Austin, Texas; London, England, United Kingdom; New York, New York", False),
    ("NY / SF / EMEA", False), ("Remote (US/EU)", False), ("Remote - US or Europe", False),
    ("Remote, APAC; Remote, EMEA; Remote, US", False), ("US, UK, Singapore, Remote", False),
    ("Europe + San Francisco", False), ("Hybrid - San Francisco, New York City, London", False),
    # LATAM includes Mexico, so it is TN territory, not "outside".
    ("LATAM remote-first", False), ("Remote LATAM", False), ("LATAM (remote)", False),
    # ... but a foreign-only multi-part string is still outside.
    ("Berlin; Munich", True), ("London; Dublin; Amsterdam", True),
])
def test_outside_tn_countries_word_boundaries_and_us_override(location, expected):
    assert tb.outside_tn_countries(location) is expected


def test_fill_failure_only_at_fit_level_0(folder, monkeypatch):
    monkeypatch.setattr(tb.rd, "pick_fit_level", lambda data: 2)
    monkeypatch.setattr(tb.rd, "estimate_height_pts", lambda data, level: tb.rd.PAGE_AVAIL_PTS * 0.94)
    v = tb.build(folder, job=JOB, no_pdf=True)
    assert v.ok and not any("body lines free" in f for f in v.failures + v.warnings)
    assert "free_lines" not in v.metrics
