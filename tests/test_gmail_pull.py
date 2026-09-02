"""Phase 2 of docs/spec-email-report-upskill.md: the Gmail signal applier."""
import json

import pytest

from src.db import connect
from src.gmail_pull import apply_changes, plan

EV = {"from": "recruiter@acme.com", "subject": "Interview invitation",
      "date": "2026-07-20", "message_id": "<m1@acme>"}


@pytest.fixture
def conn(tmp_path, monkeypatch):
    # sync_folder walks the real applications/ tree; keep the test hermetic
    monkeypatch.setattr("src.gmail_pull.sync_folder", lambda *a, **k: None)
    return connect(tmp_path / "jobs.db")


def _insert(conn, jid, status="applied", company="Acme"):
    conn.execute(
        "INSERT INTO jobs (id, source, external_id, canonical_key, company, title, "
        "status, applied_at) VALUES (?,?,?,?,?,?,?, '2026-07-01')",
        (jid, "test", f"x{jid}", f"k{jid}", company, "Engineer", status))


def _prop(jid, signal="interview_invite", status="screen", ev=EV, contact=None):
    return {"job_id": jid, "signal": signal, "proposed_status": status,
            "contact_date": contact, "evidence": ev}


def test_forward_move_applied_with_note_and_event(conn):
    _insert(conn, 1, "applied")
    p = plan(conn, [_prop(1)])
    assert [(c["id"], c["from_status"], c["to_status"]) for c in p["changes"]] == \
        [(1, "applied", "screen")]
    apply_changes(conn, p)
    row = conn.execute("SELECT status, notes, last_contact_at FROM jobs WHERE id=1").fetchone()
    assert row["status"] == "screen"
    assert "Interview invitation" in row["notes"]
    assert row["last_contact_at"] == "2026-07-20"
    ev = conn.execute("SELECT payload FROM events WHERE job_id=1 AND kind='email_signal'").fetchone()
    payload = json.loads(ev["payload"])
    assert payload["message_id"] == "m1@acme"      # RFC 822 id, brackets stripped
    assert "body" not in payload


def test_non_forward_proposal_degrades_to_touch(conn):
    _insert(conn, 1, "interview")
    p = plan(conn, [_prop(1, status="screen")])   # would downgrade
    assert not p["changes"]
    assert p["touches"][0]["id"] == 1
    apply_changes(conn, p)
    row = conn.execute("SELECT status, last_contact_at FROM jobs WHERE id=1").fetchone()
    assert row["status"] == "interview"           # untouched
    assert row["last_contact_at"] == "2026-07-20"


def test_out_of_scope_statuses_skipped(conn):
    for jid, status in ((1, "backlog"), (2, "rejected"), (3, "shortlisted")):
        _insert(conn, jid, status)
    p = plan(conn, [_prop(1), _prop(2), _prop(3)])
    assert not p["changes"] and not p["touches"] and len(p["skipped"]) == 3
    assert any("backlog hold" in s for s in p["skipped"])


def test_unknown_job_skipped(conn):
    p = plan(conn, [_prop(99)])
    assert p["skipped"] == ["#99: no such job"]


def test_contact_only_touch(conn):
    _insert(conn, 1, "applied")
    p = plan(conn, [_prop(1, signal="reply", status=None, contact="2026-07-21")])
    apply_changes(conn, p)
    row = conn.execute("SELECT status, last_contact_at FROM jobs WHERE id=1").fetchone()
    assert row["status"] == "applied" and row["last_contact_at"] == "2026-07-21"
    kinds = {r["kind"] for r in conn.execute("SELECT kind FROM events WHERE job_id=1")}
    assert kinds == {"contact", "email_signal"}


def test_terminal_proposals_need_full_evidence(conn):
    _insert(conn, 1, "applied")
    _insert(conn, 2, "screen")
    thin = {"date": "2026-07-20"}   # no subject, no sender
    p = plan(conn, [_prop(1, signal="rejection", status="rejected", ev=thin),
                    _prop(2, signal="offer", status="offer", ev=thin)])
    assert not p["changes"] and len(p["skipped"]) == 2
    assert all("needs evidence" in s for s in p["skipped"])


def test_rejected_allowed_from_any_open_stage(conn):
    _insert(conn, 1, "interview")
    p = plan(conn, [_prop(1, signal="rejection", status="rejected")])
    assert p["changes"][0]["to_status"] == "rejected"


def test_never_email_proposable_statuses_rejected(conn):
    _insert(conn, 1, "applied")
    p = plan(conn, [_prop(1, status="ghosted"), _prop(1, status="withdrawn")])
    assert not p["changes"]
    assert all("never email-proposable" in s for s in p["skipped"])


def test_duplicates_collapse_to_most_advanced(conn):
    _insert(conn, 1, "applied")
    p = plan(conn, [_prop(1, status="screen"), _prop(1, status="interview")])
    assert [(c["id"], c["to_status"]) for c in p["changes"]] == [(1, "interview")]


def test_rejection_conflicting_with_advance_goes_ambiguous(conn):
    _insert(conn, 1, "applied")
    p = plan(conn, [_prop(1, status="interview"),
                    _prop(1, signal="rejection", status="rejected")])
    assert not p["changes"] and len(p["ambiguous"]) == 2


def test_ambiguous_signal_never_applied(conn):
    _insert(conn, 1, "applied")
    p = plan(conn, [_prop(1, signal="ambiguous", status=None)])
    assert p["ambiguous"] and not p["changes"] and not p["touches"]
    apply_changes(conn, p)
    assert conn.execute("SELECT status FROM jobs WHERE id=1").fetchone()["status"] == "applied"


def test_dry_run_plan_writes_nothing(conn):
    _insert(conn, 1, "applied")
    plan(conn, [_prop(1)])
    row = conn.execute("SELECT status, last_contact_at FROM jobs WHERE id=1").fetchone()
    assert row["status"] == "applied" and row["last_contact_at"] is None
    assert not conn.execute("SELECT 1 FROM events").fetchone()


def test_touch_not_doubled_when_status_change_wins(conn):
    _insert(conn, 1, "applied")
    p = plan(conn, [_prop(1, status="screen"),
                    _prop(1, signal="reply", status=None, contact="2026-07-19")])
    assert len(p["changes"]) == 1 and not p["touches"]



# ----------------------------------------------------------------------------- spec-mail-fetch Phase B

from src.gmail_pull import _headers, _note, record_seen  # noqa: E402


def test_headers_carry_account_and_thread_id():
    ev = {**EV, "thread_id": "<root@acme>", "account": "apps", "snippet": "NEVER"}
    h = _headers(ev)
    assert h == {"from": EV["from"], "subject": EV["subject"], "date": EV["date"],
                 "message_id": "m1@acme", "thread_id": "root@acme", "account": "apps"}
    assert "[apps]" in _note(ev) and "[" not in _note(EV)


def test_ignore_signal_never_touches_the_db(conn):
    _insert(conn, 1)
    p = plan(conn, [{"job_id": 1, "signal": "ignore", "proposed_status": None, "contact_date": None,
                     "evidence": {**EV, "subject": "Thank you for applying"}}])
    assert p["changes"] == [] and p["touches"] == [] and p["ambiguous"] == [] and len(p["ignored"]) == 1
    apply_changes(conn, p)
    assert conn.execute("SELECT last_contact_at FROM jobs WHERE id=1").fetchone()[0] is None
    assert conn.execute("SELECT COUNT(*) FROM events WHERE kind='email_signal'").fetchone()[0] == 0


def test_seen_batch_covers_accepted_proposals_only(conn, tmp_path):
    """PR #10 review finding 2: out-of-scope and skipped proposals are never recorded."""
    for jid, status in ((1, "applied"), (2, "applied"), (3, "applied"), (4, "applied"), (5, "backlog")):
        _insert(conn, jid, status=status)
    props = [_prop(1, ev={**EV, "thread_id": "<root1>", "account": "apps"}),
             {"job_id": 2, "signal": "ambiguous", "proposed_status": None, "contact_date": None,
              "evidence": {"message_id": "amb@x", "thread_id": "ambthread@x"}},
             {"job_id": 3, "signal": "ignore", "proposed_status": None, "contact_date": None,
              "evidence": {"thread_id": "root3"}},
             {"job_id": 4, "signal": "reply", "proposed_status": None, "contact_date": "2026-07-20",
              "evidence": {"message_id": "touch@x"}},
             {"job_id": 5, "signal": "rejection", "proposed_status": "rejected", "contact_date": None,
              "evidence": {**EV, "message_id": "oos@x"}},                       # backlog: out of scope
             {"job_id": 999, "signal": "reply", "proposed_status": None, "contact_date": "2026-07-20",
              "evidence": {"message_id": "nosuch@x"}}]
    p = plan(conn, props)
    recorded = {(e["evidence"].get("message_id") or e["evidence"].get("thread_id")).strip("<>"): e["signal"]
                for e in p["seen_batch"]}
    assert recorded == {"m1@acme": "interview_invite", "amb@x": "ambiguous", "root3": "ignore", "touch@x": "reply"}
    state = tmp_path / "mail_state.json"
    assert record_seen(p["seen_batch"], state, today="2026-09-01") == 5
    seen = json.loads(state.read_text())["seen"]
    assert seen["root1"] == {"signal": "interview_invite", "at": "2026-09-01"}
    assert seen["ambthread@x"]["signal"] == "ambiguous" and "oos@x" not in seen and "nosuch@x" not in seen
    assert record_seen(p["seen_batch"], state) == 0                       # idempotent
    from src.mail_fetch import load_seen
    assert load_seen(None, json.loads(state.read_text()), full=False)["amb@x"] == "ambiguous"
    apply_changes(conn, p)
    payload = json.loads(conn.execute("SELECT payload FROM events WHERE kind='email_signal' AND job_id=1").fetchone()[0])
    assert payload["signal"] == "interview_invite" and payload["thread_id"] == "root1"
