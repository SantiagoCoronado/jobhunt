"""python -m src.query add: the only insert path outside discovery (replaced notion_pull --create-missing)."""
import json
from datetime import date

from src import query
from src.db import connect


def _run(monkeypatch, capsys, conn, company="Handle", title="FDE Mexico", **kw):
    monkeypatch.setattr(query, "connect", lambda: conn)
    query.cmd_add(company, title, **kw)
    return json.loads(capsys.readouterr().out)


def _row(conn, job_id):
    return conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()


def test_new_row_is_manual_and_discovered_so_the_matcher_can_score_it(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    out = _run(monkeypatch, capsys, conn, url="https://usehandle.ai", description="Deploy agents for clients")
    row = _row(conn, out["id"])
    assert out["outcome"] == "new" and out["status"] == "discovered"
    assert row["source"] == "manual" and row["status"] == "discovered" and row["match_score"] is None
    assert row["description"] == "Deploy agents for clients"


def test_explicit_status_note_and_applied_at_go_through_set_status(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    out = _run(monkeypatch, capsys, conn, status="applied", note="via jobs@", applied_at="2026-08-20")
    row = _row(conn, out["id"])
    assert row["status"] == "applied" and row["applied_at"] == "2026-08-20"
    assert row["next_followup_at"] > "2026-08-20" and "via jobs@" in row["notes"]
    assert conn.execute("SELECT COUNT(*) FROM events WHERE job_id=?", (out["id"],)).fetchone()[0] == 1


def test_second_call_updates_the_same_row_instead_of_ignoring_arguments(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    first = _run(monkeypatch, capsys, conn, status="shortlisted")
    again = _run(monkeypatch, capsys, conn, status="applied", note="sent via referral")
    assert again["id"] == first["id"] and again["outcome"] == "seen" and again["status"] == "applied"
    row = _row(conn, first["id"])
    assert row["status"] == "applied" and row["applied_at"] == date.today().isoformat()
    assert "sent via referral" in row["notes"]
    assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1


def test_call_without_status_leaves_status_alone_but_appends_note(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    first = _run(monkeypatch, capsys, conn, status="applied")
    again = _run(monkeypatch, capsys, conn, note="recruiter replied")
    assert again["status"] == "applied"
    assert "recruiter replied" in _row(conn, first["id"])["notes"]


def test_existing_board_row_with_same_company_title_is_reused_not_duplicated(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    from src.models import Job
    board = Job(source="greenhouse", external_id="g1", url="https://boards.greenhouse.io/handle/1",
                company="Handle", title="FDE Mexico", description="board text").to_row()
    conn.execute("INSERT INTO jobs (source, external_id, canonical_key, url, company, title, description, status) "
                 "VALUES (:source, :external_id, :canonical_key, :url, :company, :title, :description, 'discovered')", board)
    out = _run(monkeypatch, capsys, conn, url="https://usehandle.ai", status="applied")
    assert out["outcome"] == "matched" and out["source"] == "greenhouse"
    row = _row(conn, out["id"])
    assert row["status"] == "applied" and row["url"] == "https://boards.greenhouse.io/handle/1"
    assert row["description"] == "board text"
    assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1
