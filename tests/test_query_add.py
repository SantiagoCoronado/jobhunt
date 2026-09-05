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


def _board(conn, source, ext, status, company="Handle", title="FDE Mexico", desc="board text"):
    from src.models import Job
    row = Job(source=source, external_id=ext, url=f"https://{source}.example/{ext}",
              company=company, title=title, description=desc).to_row()
    row["status"] = status
    conn.execute("INSERT INTO jobs (source, external_id, canonical_key, url, company, title, description, status) "
                 "VALUES (:source, :external_id, :canonical_key, :url, :company, :title, :description, :status)", row)
    return conn.execute("SELECT id FROM jobs WHERE source=? AND external_id=?", (source, ext)).fetchone()[0]


def test_existing_board_row_with_same_company_title_is_reused_not_duplicated(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    _board(conn, "greenhouse", "1", "discovered")
    out = _run(monkeypatch, capsys, conn, url="https://usehandle.ai", status="applied")
    assert out["outcome"] == "matched" and out["source"] == "greenhouse"
    row = _row(conn, out["id"])
    assert row["status"] == "applied" and row["url"] == "https://greenhouse.example/1"
    assert row["description"] == "board text"
    assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1


def test_lookup_prefers_live_ats_row_like_canonical_jobs(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    _board(conn, "jobicy", "a", "expired")            # lowest id, aggregator, dead
    _board(conn, "remoteok", "b", "discovered")       # live aggregator
    live_ats = _board(conn, "workday", "c", "discovered")
    out = _run(monkeypatch, capsys, conn, status="applied")
    assert out["id"] == live_ats and out["outcome"] == "matched"
    view = conn.execute("SELECT id FROM canonical_jobs").fetchone()[0]
    assert view == live_ats


def test_only_junk_rows_get_revived_to_discovered(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    junk = _board(conn, "greenhouse", "1", "irrelevant")
    out = _run(monkeypatch, capsys, conn)
    assert out["id"] == junk and out["outcome"] == "revived" and out["status"] == "discovered"
    assert _row(conn, junk)["status"] == "discovered"
    assert conn.execute("SELECT COUNT(*) FROM events WHERE job_id=?", (junk,)).fetchone()[0] == 1


def test_live_matched_row_without_status_is_left_alone(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    live = _board(conn, "greenhouse", "1", "screen")
    out = _run(monkeypatch, capsys, conn)
    assert out["status"] == "screen" and _row(conn, live)["status"] == "screen"


def test_applied_at_alone_corrects_an_existing_date(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    first = _run(monkeypatch, capsys, conn, status="applied")
    assert _row(conn, first["id"])["applied_at"] == date.today().isoformat()
    _run(monkeypatch, capsys, conn, applied_at="2026-08-20")
    assert _row(conn, first["id"])["applied_at"] == "2026-08-20"


def test_slug_collision_does_not_land_on_the_wrong_row(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    a = _run(monkeypatch, capsys, conn, company="Arga Labs", title="Engineer", status="applied")
    b = _run(monkeypatch, capsys, conn, company="Arga", title="Labs Engineer", status="shortlisted")
    assert a["id"] != b["id"] and b["outcome"] == "new"
    assert _row(conn, a["id"])["status"] == "applied" and _row(conn, b["id"])["status"] == "shortlisted"


def test_manual_description_can_be_corrected_like_url(tmp_path, monkeypatch, capsys):
    conn = connect(tmp_path / "jobs.db")
    first = _run(monkeypatch, capsys, conn, description="v1", url="https://a")
    _run(monkeypatch, capsys, conn, description="v2", url="https://b")
    row = _row(conn, first["id"])
    assert row["description"] == "v2" and row["url"] == "https://b"
