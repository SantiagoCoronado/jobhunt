"""Flask-level tests for the CRM viewer's update route (the second write path)."""
from datetime import date, timedelta

import pytest

from src.crm import viewer
from src.db import connect


@pytest.fixture
def env(tmp_path, monkeypatch):
    db_path = tmp_path / "jobs.db"
    conn = connect(db_path)
    conn.execute(
        "INSERT INTO jobs (id, source, external_id, canonical_key, company, title, status) "
        "VALUES (1, 'test', 'x1', 'k1', 'Acme', 'Engineer', 'shortlisted')"
    )
    conn.commit()
    conn.close()
    monkeypatch.setattr(viewer, "connect", lambda: connect(db_path))
    moves = []
    monkeypatch.setattr(viewer, "sync_folder", lambda jid, st: moves.append((jid, st)))
    viewer.app.config["TESTING"] = True
    return viewer.app.test_client(), db_path, moves


def _row(db_path):
    return connect(db_path).execute("SELECT * FROM jobs WHERE id=1").fetchone()


def test_board_renders(env):
    client, _, _ = env
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Engineer" in resp.data


def test_update_applies_and_schedules(env):
    client, db_path, moves = env
    resp = client.post("/update", data={"id": "1", "status": "applied",
                                        "next_followup": "", "notes": ""})
    assert resp.status_code == 302
    r = _row(db_path)
    assert r["status"] == "applied"
    assert r["applied_at"] == date.today().isoformat()
    assert r["next_followup_at"] is not None
    assert moves == [(1, "applied")]


def test_update_preserves_original_applied_at(env):
    client, db_path, _ = env
    conn = connect(db_path)
    conn.execute("UPDATE jobs SET status='applied', applied_at='2026-07-01' WHERE id=1")
    conn.commit()
    client.post("/update", data={"id": "1", "status": "applied",
                                 "next_followup": "", "notes": "ping"})
    assert _row(db_path)["applied_at"] == "2026-07-01"


def test_update_rejects_bad_status(env):
    client, db_path, moves = env
    resp = client.post("/update", data={"id": "1", "status": "not-a-status",
                                        "next_followup": "", "notes": ""})
    assert resp.status_code == 400
    assert _row(db_path)["status"] == "shortlisted"  # unchanged
    assert moves == []


def test_update_rejects_bad_date(env):
    client, db_path, _ = env
    resp = client.post("/update", data={"id": "1", "status": "applied",
                                        "next_followup": "soon", "notes": ""})
    assert resp.status_code == 400
    assert _row(db_path)["status"] == "shortlisted"
