"""python -m src.query add: the only insert path outside discovery (replaced notion_pull --create-missing)."""
import json

from src import query
from src.db import connect


def _run(monkeypatch, capsys, conn, **kw):
    monkeypatch.setattr(query, "connect", lambda: conn)
    query.cmd_add(kw.get("company", "Handle"), kw.get("title", "FDE Mexico"),
                  kw.get("url"), kw.get("status", "shortlisted"), kw.get("note"))
    return json.loads(capsys.readouterr().out)


def test_add_inserts_manual_row_with_status_and_event(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    out = _run(monkeypatch, capsys, conn, url="https://usehandle.ai", status="applied", note="via jobs@")
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (out["id"],)).fetchone()
    assert out["outcome"] == "new"
    assert row["source"] == "manual" and row["status"] == "applied"
    assert row["applied_at"] is not None and row["url"] == "https://usehandle.ai"
    assert "via jobs@" in (row["notes"] or "")
    assert conn.execute("SELECT COUNT(*) FROM events WHERE job_id=?", (out["id"],)).fetchone()[0] == 1


def test_add_is_idempotent_on_company_title(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    first = _run(monkeypatch, capsys, conn, status="applied")
    again = _run(monkeypatch, capsys, conn, status="shortlisted")
    assert again["id"] == first["id"] and again["outcome"] == "seen"
    assert again["status"] == "unchanged"
    assert conn.execute("SELECT status FROM jobs WHERE id=?", (first["id"],)).fetchone()[0] == "applied"
    assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1
