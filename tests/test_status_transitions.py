"""db.set_status / db.touch_contact: the single write path for the CRM."""
from datetime import date, timedelta

import pytest

from src.db import connect, set_status, touch_contact

TODAY = date.today().isoformat()


@pytest.fixture
def conn(tmp_path):
    c = connect(tmp_path / "jobs.db")
    c.execute(
        "INSERT INTO jobs (id, source, external_id, canonical_key, company, title, status) "
        "VALUES (1, 'test', 'x1', 'k1', 'Acme', 'Engineer', 'shortlisted')"
    )
    return c


def _row(conn):
    return conn.execute("SELECT * FROM jobs WHERE id=1").fetchone()


def test_rejects_unknown_status(conn):
    with pytest.raises(ValueError, match="Unknown status"):
        set_status(conn, 1, "definitely-not-a-status")


def test_rejects_missing_job(conn):
    with pytest.raises(ValueError, match="No job with id"):
        set_status(conn, 999, "applied")


def test_rejects_bad_date(conn):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        set_status(conn, 1, "applied", next_followup="next tuesday")


def test_applied_stamps_date_and_schedules_followup(conn):
    set_status(conn, 1, "applied", followup_days=7)
    r = _row(conn)
    assert r["status"] == "applied"
    assert r["applied_at"] == TODAY
    assert r["next_followup_at"] == (date.today() + timedelta(days=7)).isoformat()


def test_applied_at_not_overwritten_on_reapply(conn):
    set_status(conn, 1, "applied", applied_at="2026-07-01")
    set_status(conn, 1, "screen")
    set_status(conn, 1, "applied")
    assert _row(conn)["applied_at"] == "2026-07-01"


def test_explicit_applied_at_drives_followup(conn):
    set_status(conn, 1, "applied", applied_at="2026-07-01", followup_days=7)
    assert _row(conn)["next_followup_at"] == "2026-07-08"


def test_explicit_followup_wins_over_auto(conn):
    set_status(conn, 1, "applied", next_followup="2026-08-01")
    assert _row(conn)["next_followup_at"] == "2026-08-01"


def test_empty_followup_from_form_still_autoschedules_on_apply(conn):
    # The viewer posts "" when the field is blank; flipping to applied must
    # still schedule the follow-up.
    set_status(conn, 1, "applied", next_followup="", followup_days=7)
    assert _row(conn)["next_followup_at"] == (date.today() + timedelta(days=7)).isoformat()


def test_empty_followup_clears_existing(conn):
    set_status(conn, 1, "shortlisted", next_followup="2026-08-01")
    set_status(conn, 1, "shortlisted", next_followup="")
    assert _row(conn)["next_followup_at"] is None


def test_reapply_after_terminal_reschedules_followup(conn):
    # Regression: scheduling used to be nested inside the first-time applied_at
    # stamp, so a re-apply after rejection left next_followup_at NULL forever
    # and the job vanished from /jh-followups.
    set_status(conn, 1, "applied", applied_at="2026-06-01")
    set_status(conn, 1, "rejected")
    assert _row(conn)["next_followup_at"] is None
    set_status(conn, 1, "applied", followup_days=7)
    r = _row(conn)
    assert r["applied_at"] == "2026-06-01"  # original submission date kept
    assert r["next_followup_at"] == (date.today() + timedelta(days=7)).isoformat()


def test_terminal_status_clears_followup(conn):
    set_status(conn, 1, "applied")
    assert _row(conn)["next_followup_at"] is not None
    set_status(conn, 1, "ghosted")
    assert _row(conn)["next_followup_at"] is None


def test_explicit_followup_survives_terminal(conn):
    # "rejected, reapply eligible in October" is an intentional reminder.
    set_status(conn, 1, "rejected", next_followup="2026-10-06")
    assert _row(conn)["next_followup_at"] == "2026-10-06"


def test_note_appends(conn):
    set_status(conn, 1, "applied", note="sent via portal")
    set_status(conn, 1, "screen", note="recruiter: Ana")
    assert _row(conn)["notes"] == "sent via portal\nrecruiter: Ana"


def test_notes_replaces(conn):
    set_status(conn, 1, "applied", note="old")
    set_status(conn, 1, "applied", notes="new text")
    assert _row(conn)["notes"] == "new text"


def test_touch_sets_last_contact(conn):
    touch_contact(conn, 1, contact_date="2026-07-10")
    assert _row(conn)["last_contact_at"] == "2026-07-10"


def test_touch_bump_pushes_followup(conn):
    touch_contact(conn, 1, contact_date="2026-07-10", bump_days=7)
    r = _row(conn)
    assert r["last_contact_at"] == "2026-07-10"
    assert r["next_followup_at"] == "2026-07-17"


def test_touch_missing_job(conn):
    with pytest.raises(ValueError, match="No job with id"):
        touch_contact(conn, 999)
