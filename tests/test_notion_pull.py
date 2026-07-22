"""notion_pull: Notion mirror edits flow back into the DB, conservatively."""
import pytest

from src.db import connect
from src.notion_pull import apply_changes, plan, url_key


@pytest.fixture
def conn(tmp_path):
    c = connect(tmp_path / "jobs.db")
    rows = [
        (1, "Acme", "Engineer", "https://boards.example.com/acme/1", "applied", "2026-07-13", None),
        (2, "Beta", "AI Engineer", "https://boards.example.com/beta/2", "shortlisted", None, None),
        (3, "Gamma", "Founding Engineer", "https://boards.example.com/gamma/3", "backlog", None, None),
        (4, "Delta", "Platform Engineer", "https://boards.example.com/delta/4", "applied", "2026-07-10", None),
    ]
    for jid, co, title, url, status, applied, followup in rows:
        c.execute(
            "INSERT INTO jobs (id, source, external_id, canonical_key, company, title, url, "
            "status, applied_at, next_followup_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (jid, "test", f"x{jid}", f"k{jid}", co, title, url, status, applied, followup),
        )
    return c


def test_url_key_normalizes():
    assert url_key("https://www.Example.com/a/b/?utm_source=x") == "example.com/a/b"
    assert url_key("http://example.com/a/b") == "example.com/a/b"
    assert url_key(None) is None


def test_url_key_keeps_identifying_params():
    # HN postings share the /item path; only ?id= distinguishes them.
    a = url_key("https://news.ycombinator.com/item?id=111")
    b = url_key("https://news.ycombinator.com/item?id=222")
    assert a != b and a == "news.ycombinator.com/item?id=111"
    # adzuna tracking params are noise, the path id is identity
    assert url_key("https://www.adzuna.com.mx/details/579?utm_medium=api&se=abc&v=DEF") == "adzuna.com.mx/details/579"


def test_status_advance_and_date_correction(conn):
    p = plan(conn, [{"company": "Acme", "role": "Engineer", "status": "screen",
                     "applied": "2026-07-09", "followup": None, "notes": None,
                     "link": "https://boards.example.com/acme/1?utm=phone"}])
    assert len(p["changes"]) == 1
    c = p["changes"][0]
    assert c["status"] == "screen" and c["applied_at"] == "2026-07-09"
    apply_changes(conn, p)
    r = conn.execute("SELECT * FROM jobs WHERE id=1").fetchone()
    assert r["status"] == "screen" and r["applied_at"] == "2026-07-09"


def test_downgrade_is_skipped(conn):
    p = plan(conn, [{"company": "Acme", "role": "Engineer", "status": "shortlisted",
                     "applied": None, "followup": None, "notes": None,
                     "link": "https://boards.example.com/acme/1"}])
    assert not p["changes"]
    assert any("downgrade" in s for s in p["skipped"])


def test_declined_and_not_found_map_to_withdrawn(conn):
    rows = [
        {"company": "Beta", "role": "AI Engineer", "status": "declined",
         "applied": None, "followup": None, "notes": None,
         "link": "https://boards.example.com/beta/2"},
        {"company": "Delta", "role": "Platform Engineer", "status": "Not Found",
         "applied": None, "followup": None, "notes": None,
         "link": "https://boards.example.com/delta/4"},
    ]
    p = plan(conn, rows)
    assert [c["status"] for c in p["changes"]] == ["withdrawn", "withdrawn"]
    # provenance of the mapping lands in the notes
    assert p["changes"][0]["status_note"] == "[notion] status was 'declined'"


def test_backlog_hold_not_overwritten(conn):
    p = plan(conn, [{"company": "Gamma", "role": "Founding Engineer", "status": "shortlisted",
                     "applied": None, "followup": None, "notes": None,
                     "link": "https://boards.example.com/gamma/3"}])
    assert not p["changes"]
    assert any("backlog" in s for s in p["skipped"])


def test_backlog_can_still_be_terminated(conn):
    p = plan(conn, [{"company": "Gamma", "role": "Founding Engineer", "status": "rejected",
                     "applied": None, "followup": None, "notes": None,
                     "link": "https://boards.example.com/gamma/3"}])
    assert p["changes"][0]["status"] == "rejected"


def test_followup_only_change(conn):
    p = plan(conn, [{"company": "Beta", "role": "AI Engineer", "status": "shortlisted",
                     "applied": None, "followup": "2026-10-01", "notes": None,
                     "link": "https://boards.example.com/beta/2"}])
    assert p["changes"][0]["next_followup_at"] == "2026-10-01"
    apply_changes(conn, p)
    assert conn.execute("SELECT next_followup_at FROM jobs WHERE id=2").fetchone()[0] == "2026-10-01"


def test_terminal_with_followup_keeps_reapply_date(conn):
    p = plan(conn, [{"company": "Beta", "role": "AI Engineer", "status": "rejected",
                     "applied": None, "followup": "2026-10-06", "notes": None,
                     "link": "https://boards.example.com/beta/2"}])
    apply_changes(conn, p)
    r = conn.execute("SELECT * FROM jobs WHERE id=2").fetchone()
    assert r["status"] == "rejected" and r["next_followup_at"] == "2026-10-06"


def test_match_by_company_title_fallback(conn):
    p = plan(conn, [{"company": "ACME", "role": "Engineer!", "status": "screen",
                     "applied": None, "followup": None, "notes": None, "link": None}])
    assert p["changes"] and p["changes"][0]["id"] == 1


def test_unmatched_reported_and_created_on_request(conn):
    rows = [{"company": "NewCo", "role": "AI Lead", "status": "applied",
             "applied": "2026-07-06", "followup": None, "notes": "from notion",
             "link": "https://boards.example.com/newco/9"}]
    p = plan(conn, rows)
    assert p["unmatched"] == rows
    apply_changes(conn, p, create_missing=True)
    r = conn.execute("SELECT * FROM jobs WHERE source='manual'").fetchone()
    assert r["company"] == "NewCo" and r["status"] == "applied"
    assert r["applied_at"] == "2026-07-06" and r["notes"] == "[notion] from notion"


def test_notes_copied_only_when_db_empty(conn):
    conn.execute("UPDATE jobs SET notes='existing' WHERE id=1")
    p = plan(conn, [
        {"company": "Acme", "role": "Engineer", "status": "applied", "applied": None,
         "followup": None, "notes": "notion note", "link": "https://boards.example.com/acme/1"},
        {"company": "Beta", "role": "AI Engineer", "status": "shortlisted", "applied": None,
         "followup": None, "notes": "notion note", "link": "https://boards.example.com/beta/2"},
    ])
    ids = [c["id"] for c in p["changes"]]
    assert ids == [2]  # Acme already has notes; Beta gets the copy
    apply_changes(conn, p)
    assert conn.execute("SELECT notes FROM jobs WHERE id=2").fetchone()[0] == "[notion] notion note"
