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
    assert record_seen(p["seen_batch"], state, today="2026-09-01") == 6
    seen = json.loads(state.read_text())["seen"]
    assert seen["root1"] == {"signal": "interview_invite", "at": "2026-09-01"}
    assert seen["ambthread@x"]["signal"] == "ambiguous" and "oos@x" not in seen and "nosuch@x" not in seen
    assert record_seen(p["seen_batch"], state) == 0                       # idempotent
    from src.mail_fetch import load_seen
    assert load_seen(None, json.loads(state.read_text()), full=False)["amb@x"] == "ambiguous"
    apply_changes(conn, p)
    payload = json.loads(conn.execute("SELECT payload FROM events WHERE kind='email_signal' AND job_id=1").fetchone()[0])
    assert payload["signal"] == "interview_invite" and payload["thread_id"] == "root1"


def test_folded_and_superseded_touches_are_still_recorded(conn):
    """Phase D finding: a touch folded into a status change (or beaten by a later touch on
    the same job) left no seen id, so its message resurfaced on the next sweep."""
    _insert(conn, 1)
    props = [_prop(1, ev={**EV, "message_id": "invite@x"}),                                          # change
             {"job_id": 1, "signal": "reply", "proposed_status": None, "contact_date": "2026-07-21",
              "evidence": {"message_id": "cal@x"}},                                                 # folded touch
             {"job_id": 1, "signal": "reply", "proposed_status": None, "contact_date": "2026-07-19",
              "evidence": {"message_id": "older@x"}}]                                               # superseded touch
    p = plan(conn, props)
    assert p["touches"] == []
    assert {e["evidence"]["message_id"] for e in p["seen_batch"]} == {"invite@x", "cal@x", "older@x"}


def test_resolve_manifest_requires_matching_sweep_stamp(tmp_path):
    import json

    from src.gmail_pull import resolve_manifest
    inbox = tmp_path / "mail_inbox.json"
    inbox.write_text(json.dumps({"generated_at": "2026-09-02T18:56:47+00:00", "threads": [
        {"id": 1, "account": "apps", "from": "a@b.c", "date": "2026-09-02", "subject": "Results",
         "message_id": "<m1>", "thread_id": "<t1>", "job_ids": [6984]}]}))
    ok = resolve_manifest([{"manifest_id": 1, "sweep": "2026-09-02T18:56:47+00:00", "signal": "rejection",
                            "proposed_status": "rejected"}], inbox)
    assert ok[0]["job_id"] == 6984 and ok[0]["evidence"]["message_id"] == "<m1>" and ok[0]["contact_date"] == "2026-09-02"
    with pytest.raises(SystemExit, match="names sweep"):
        resolve_manifest([{"manifest_id": 1, "sweep": "2026-09-01T00:00:00+00:00", "signal": "ignore"}], inbox)
    # the same instant written as Z, or with copy-paste whitespace, is the same sweep
    for stamp in ("2026-09-02T18:56:47Z", " 2026-09-02T18:56:47+00:00 "):
        assert resolve_manifest([{"manifest_id": 1, "sweep": stamp, "signal": "ignore"}], inbox)[0]["job_id"] == 6984
    with pytest.raises(SystemExit, match="names sweep"):
        resolve_manifest([{"manifest_id": 1, "signal": "ignore"}], inbox)
    # a bad line id or an unknown one skips THAT proposal; the batch goes on (53 lines, one typo)
    bad = resolve_manifest([{"manifest_id": "12b", "sweep": "2026-09-02T18:56:47+00:00", "signal": "ignore"},
                            {"manifest_id": 9, "sweep": "2026-09-02T18:56:47+00:00", "signal": "ignore"},
                            {"manifest_id": 1, "sweep": "2026-09-02T18:56:47+00:00", "signal": "ignore"}], inbox)
    assert "not a manifest line number" in bad[0]["_skip"] and "is not in" in bad[1]["_skip"]
    assert "_skip" not in bad[2] and bad[2]["job_id"] == 6984


def test_resolve_manifest_guards_job_id_and_null_contact_date(tmp_path):
    import json

    from src.gmail_pull import resolve_manifest
    inbox = tmp_path / "mail_inbox.json"
    inbox.write_text(json.dumps({"generated_at": "2026-09-02T18:56:47+00:00", "threads": [
        {"id": 1, "account": "apps", "from": "a@b.c", "date": "2026-09-02", "subject": "Results",
         "message_id": "<m1>", "thread_id": "<t1>", "job_ids": [6984, 7000]}]}))
    base = {"manifest_id": 1, "sweep": "2026-09-02T18:56:47+00:00", "signal": "rejection",
            "proposed_status": "rejected"}
    # an explicit null contact_date still takes the thread date (setdefault would have left it None)
    ok = resolve_manifest([{**base, "job_id": 7000, "contact_date": None}], inbox)
    assert ok[0]["contact_date"] == "2026-09-02"
    # a job_id the cited thread never matched would file this thread's evidence on an unrelated job
    res = resolve_manifest([{**base, "job_id": 7001}, {**base}, {**base, "job_id": "7000"}, {**base, "job_id": "x"}], inbox)
    assert "is not on manifest_id" in res[0]["_skip"]
    assert "maps to 2 jobs" in res[1]["_skip"]
    assert "_skip" not in res[2] and res[2]["job_id"] == 7000        # "7000" coerced like manifest_id is
    assert "is not a job id" in res[3]["_skip"]
    assert set(res[2]["evidence"]) == {"from", "subject", "date", "message_id", "thread_id", "account"}


def test_resolve_manifest_archive_headers_win_and_signal_is_required(tmp_path):
    import json

    from src.gmail_pull import resolve_manifest
    inbox = tmp_path / "mail_inbox.json"
    inbox.write_text(json.dumps({"generated_at": "2026-09-02T18:56:47+00:00", "threads": [
        {"id": 1, "account": "apps", "from": "Bob <bob@acme.com>", "date": "2026-09-02", "subject": "Results",
         "message_id": "<m1>", "thread_id": "<t1>", "job_ids": [6984]}]}))
    base = {"manifest_id": 1, "sweep": "2026-09-02T18:56:47+00:00"}
    # the model only ever saw a domain and no ids: its evidence cannot override the archive's
    got = resolve_manifest([{**base, "signal": "rejection", "proposed_status": "rejected",
                             "evidence": {"from": "acme.com", "message_id": "", "extra": "kept"}}], inbox)[0]
    assert got["evidence"]["from"] == "Bob <bob@acme.com>" and got["evidence"]["message_id"] == "<m1>"
    assert got["evidence"]["extra"] == "kept"
    # no recognized signal: skipped (reported, not seen), never a silent contact touch
    res = resolve_manifest([{**base, "proposed_status": None}, {**base, "signal": "maybe"}], inbox)
    assert "no recognized signal" in res[0]["_skip"] and "'maybe'" in res[1]["_skip"]
    # a missing or corrupt archive is named as such, not reported as a stale stamp
    with pytest.raises(SystemExit, match="not found"):
        resolve_manifest([{**base, "signal": "ignore"}], tmp_path / "absent.json")
    inbox.write_text("{not json")
    with pytest.raises(SystemExit, match="not valid JSON"):
        resolve_manifest([{**base, "signal": "ignore"}], inbox)


def test_plan_reports_unresolved_manifest_lines_and_keeps_the_rest(conn):
    _insert(conn, 1)
    props = [{"manifest_id": 9, "signal": "ignore", "_skip": "manifest_id 9 is not in inbox, skipped"},
             {"job_id": 1, "signal": "rejection", "proposed_status": "rejected",
              "evidence": {"from": "hr@acme.com", "subject": "Results", "date": "2026-07-20", "message_id": "m1"}}]
    p = plan(conn, props)
    assert p["skipped"] == ["manifest_id 9 is not in inbox, skipped"]
    assert [c["to_status"] for c in p["changes"]] == ["rejected"]
    assert {e["evidence"].get("message_id") for e in p["seen_batch"]} == {"m1"}   # the skipped line is never seen
