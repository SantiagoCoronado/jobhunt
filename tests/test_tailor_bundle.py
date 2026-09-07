"""tailor_bundle: one inputs.md with every section in a fixed order (hermetic DB and folders)."""
from __future__ import annotations

import json
import re

import pytest

from src import tailor_bundle as tbd
from src.db import connect

COLS = "id, source, external_id, canonical_key, company, title, location, url, status, description, match_score, match_verdict, salary_min, salary_max, currency"


@pytest.fixture
def conn(tmp_path):
    c = connect(tmp_path / "jobs.db")
    rows = [
        (1, "ashby", "x1", "k1", "Acme", "Senior Engineer", "Remote", "https://a/1", "shortlisted",
         "Build things with React and Python.", 82, json.dumps({"recommendation": "Yes", "location_ok": True}), None, None, None),
        (2, "workday", "x2", "k2", "Example Robotics", "Senior Solutions Architect", "Santa Clara", "https://n/2", "shortlisted",
         "", 90, json.dumps({"visa_path": "TN, employer files"}), None, None, None),
        (3, "dreamsheet", "x3", "k2", "ExampleRobotics", "Senior Solutions Architect", "Santa Clara", "https://n/2", "discovered",
         "Curated (dream sheet):\nPriority: Apply this week", None, None, None, None, None),
        (4, "hackernews", "x4", "k4", "HN: Who is Hiring", "Quill", "", "https://hn/4", "shortlisted",
         "Quill | Fullstack SWE | Remote", 84, None, 150000, 210000, "USD"),
    ]
    for r in rows:
        c.execute(f"INSERT INTO jobs ({COLS}) VALUES ({','.join('?' * 15)})", r)
    c.commit()
    return c


@pytest.fixture
def apps(tmp_path):
    d = tmp_path / "applications"
    for b in ("applied", "pending", "other"):
        (d / b).mkdir(parents=True)
    return d


@pytest.fixture(autouse=True)
def no_dossier(monkeypatch):
    monkeypatch.setattr(tbd, "dossier_info", lambda name: {"path": None, "exists": False, "researched": None, "age_days": None, "stale": None})


def _headings(text: str) -> list[str]:
    return re.findall(r"^# (\d+)\. ", text, re.M)


def test_sections_in_fixed_order_and_meta(conn, apps):
    text, meta = tbd.build_bundle(conn, 1, apps_dir=apps)
    assert _headings(text) == ["1", "2", "3", "4", "5", "6", "7"]
    assert text.index("# 1. Voice") < text.index("# 2. Profile") < text.index("# 3. Master") < text.index("# 4. Page geometry")
    assert "dream_rule" in text and "relocation_line" in text          # profile verbatim
    assert "A full bullet line holds about" in text                     # geometry generated
    assert "company: Acme" in text and "dream: false" in text
    assert "matcher recommendation: Yes" in text
    assert "No dossier for this company" in text
    assert "## Why do you want to work at Acme?" in text and "<!-- TAILOR" in text
    assert meta["dream"] is False and meta["dossier"] is None and meta["answers_approved"] >= 1
    assert meta["folder"].endswith("pending/acme-1") and meta["sections"] == [1, 2, 3, 4, 5, 6, 7]
    assert "mail_" not in text and "interviews/" not in text


def test_dream_row_gets_flag_curated_block_and_empty_description_pointer(conn, apps):
    text, meta = tbd.build_bundle(conn, 2, apps_dir=apps)
    assert meta["dream"] is True and meta["curated"] is True
    assert "dream: true" in text
    assert "Priority: Apply this week" in text
    assert "Description: EMPTY in the DB" in text
    assert "matcher visa_path: TN, employer files" in text


def test_company_override_flows_into_answers_and_folder(conn, apps):
    text, meta = tbd.build_bundle(conn, 4, company="Quill", apps_dir=apps)
    assert "company: Quill" in text and "use 'Quill' everywhere" in text
    assert "## Why do you want to work at Quill?" in text
    assert meta["folder"].endswith("pending/quill-4")
    assert "salary: 150000-210000 USD" in text


def test_dossier_override_and_stale_note(conn, apps, tmp_path, monkeypatch):
    d = tmp_path / "acme.md"
    d.write_text("# Acme dossier\nresearched: 2026-07-01\nFacts here.\n")
    text, meta = tbd.build_bundle(conn, 1, dossier=str(d), apps_dir=apps)
    assert "Facts here." in text and meta["dossier"] == "acme.md"
    monkeypatch.setattr(tbd, "dossier_info", lambda name: {"path": d, "exists": True, "researched": "2026-07-01", "age_days": 63, "stale": True})
    text, meta = tbd.build_bundle(conn, 1, apps_dir=apps)
    assert "stale" in text and meta["dossier_stale"] is True


def test_existing_draft_and_review_items_become_sections_8_and_9(conn, apps):
    folder = apps / "pending" / "acme-1"
    folder.mkdir()
    (folder / "SantiagoCoronadoResume.yaml").write_text("cv:\n  name: Existing Draft\n")
    (folder / "review.json").write_text(json.dumps({"reviewer": "cv-reviewer", "at": "t", "items": [
        {"id": 1, "file": "CoverLetter.md", "anchor": "p1", "severity": "must", "comment": "Cut the second fact.", "resolved": False},
        {"id": 2, "file": "CoverLetter.md", "anchor": "p2", "severity": "nit", "comment": "done already", "resolved": True},
    ]}))
    text, meta = tbd.build_bundle(conn, 1, apps_dir=apps)
    assert _headings(text) == ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    assert "name: Existing Draft" in text
    assert "1. [must] CoverLetter.md @ p1: Cut the second fact." in text and "done already" not in text
    assert meta["existing_draft"] is True and meta["review_open"] == 1


def test_existing_folder_in_applied_bucket_is_reused(conn, apps):
    (apps / "applied" / "acme-1").mkdir()
    _, meta = tbd.build_bundle(conn, 1, apps_dir=apps)
    assert meta["folder"].endswith("applied/acme-1")


def test_unknown_job_exits(conn, apps):
    with pytest.raises(SystemExit):
        tbd.build_bundle(conn, 999, apps_dir=apps)


def test_geometry_block_numbers_are_sane():
    import yaml

    from src.config import user_file
    master = yaml.safe_load(user_file("master_resume").read_text())
    block = tbd.geometry_block(master)
    m = re.search(r"about (\d+) characters \((\d+) at level 3\)", block)
    assert m and 90 <= int(m.group(1)) <= 130 and int(m.group(2)) >= int(m.group(1))
    b = re.search(r"about (\d+) body lines remain", block)
    assert b and 25 <= int(b.group(1)) <= 60


def test_main_writes_inputs_and_state(conn, apps, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(tbd, "connect", lambda: conn)
    monkeypatch.setattr(tbd, "APPS_DIR", apps)
    monkeypatch.setattr(tbd, "application_folder", lambda jid, co, apps_dir=apps: apps / "pending" / f"acme-{jid}")
    out = tmp_path / "bundle"
    assert tbd.main(["1", "--out", str(out)]) == 0
    assert (out / "inputs.md").exists()
    printed = capsys.readouterr().out
    assert "wrote" in printed and "dream=false" in printed and "answers=" in printed
    state = json.loads((apps / "pending" / "acme-1" / "state.json").read_text())
    assert state["job_id"] == 1 and "bundled" in state["stages"]
