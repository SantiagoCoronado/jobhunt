"""reconcile: two-way sync between applications/ folders and DB statuses."""
from pathlib import Path

import pytest

from src.db import connect
from src.reconcile import find_folder, folder_job_id, plan, scan, sync_folder


@pytest.fixture
def conn(tmp_path):
    c = connect(tmp_path / "jobs.db")
    rows = [
        (1, "shortlisted"),   # folder correctly in pending/
        (2, "shortlisted"),   # folder in applied/ -> DB should flip (rule 1)
        (3, "applied"),       # folder in pending/ -> folder moves forward (rule 2)
        (4, "rejected"),      # folder in applied/ -> folder moves forward to other/
        (5, "shortlisted"),   # folder in other/ -> human outcome missing, flag (rule 3)
    ]
    for jid, status in rows:
        c.execute(
            "INSERT INTO jobs (id, source, external_id, canonical_key, company, title, status) "
            f"VALUES ({jid}, 'test', 'x{jid}', 'k{jid}', 'Co{jid}', 'Role', '{status}')"
        )
    return c


@pytest.fixture
def apps(tmp_path):
    d = tmp_path / "applications"
    for bucket, name in [
        ("pending", "co1-1"), ("applied", "co2-2"), ("pending", "co3-3"),
        ("applied", "co4-4"), ("other", "co5-5"),
        ("applied", "no-id-folder"), ("pending", "orphan-99"),
    ]:
        (d / bucket / name).mkdir(parents=True)
    return d


def test_folder_job_id():
    assert folder_job_id("acme-123") == 123
    assert folder_job_id("acme-ai-director") is None
    assert folder_job_id("99minutos-10478") == 10478


def test_plan_finds_all_drift(conn, apps):
    p = plan(conn, apps)

    assert [u["id"] for u in p["db_updates"]] == [2]
    assert p["db_updates"][0]["old_status"] == "shortlisted"

    moves = {m["id"]: (m["from"], m["to"]) for m in p["folder_moves"]}
    assert moves == {3: ("pending", "applied"), 4: ("applied", "other")}

    assert any("no-id-folder" in u for u in p["unmatched"])
    assert any("orphan-99" in u for u in p["unmatched"])
    # correctly-filed folder generates no noise
    assert 1 not in moves and 1 not in [u["id"] for u in p["db_updates"]]


def test_folder_ahead_of_db_is_flagged_not_moved_back(conn, apps):
    # A folder deliberately filed in other/ records a human outcome the DB never
    # got; reconcile must NOT undo the filing by moving it back to pending/.
    p = plan(conn, apps)
    assert 5 not in {m["id"] for m in p["folder_moves"]}
    flag = [u for u in p["unmatched"] if "co5-5" in u]
    assert flag and "set-status 5" in flag[0]


def test_plan_flags_duplicate_buckets(conn, apps):
    (apps / "pending" / "co2-dupe-2").mkdir()
    p = plan(conn, apps)
    assert any("multiple buckets" in u for u in p["unmatched"])
    assert not p["db_updates"]  # conflicted id is skipped, not guessed


def test_sync_folder_moves_to_expected_bucket(conn, apps):
    note = sync_folder(3, "applied", apps)
    assert note == "moved co3-3: pending/ -> applied/"
    assert (apps / "applied" / "co3-3").is_dir()
    assert not (apps / "pending" / "co3-3").exists()


def test_sync_folder_noop_when_correct(conn, apps):
    assert sync_folder(1, "shortlisted", apps) is None


def test_sync_folder_refuses_to_clobber(conn, apps):
    (apps / "other" / "co4-4").mkdir()
    note = sync_folder(4, "rejected", apps)
    assert note.startswith("CONFLICT")
    assert (apps / "applied" / "co4-4").is_dir()  # source untouched


def test_main_apply_end_to_end(conn, apps, monkeypatch):
    import src.reconcile as rec

    monkeypatch.setattr(rec, "connect", lambda: conn)
    monkeypatch.setattr(rec, "APPS_DIR", apps)
    monkeypatch.setattr(rec, "followup_days", lambda: 7)
    monkeypatch.setattr("sys.argv", ["reconcile", "--apply"])
    rec.main()

    # Rule 1: folder in applied/ flipped the shortlisted row.
    r = conn.execute("SELECT * FROM jobs WHERE id=2").fetchone()
    assert r["status"] == "applied"
    assert r["applied_at"] and r["next_followup_at"]
    # Rule 2: folders moved forward to match the DB.
    assert (apps / "applied" / "co3-3").is_dir()
    assert (apps / "other" / "co4-4").is_dir()
    # Rule 3: folder-ahead-of-DB untouched.
    assert (apps / "other" / "co5-5").is_dir()
    assert conn.execute("SELECT status FROM jobs WHERE id=5").fetchone()[0] == "shortlisted"


def test_scan_and_find(conn, apps):
    buckets = {p.name: b for b, p in scan(apps)}
    assert buckets["co1-1"] == "pending"
    found = find_folder(4, apps)
    assert found and found[0] == "applied"
    assert find_folder(12345, apps) is None
