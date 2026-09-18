"""The inbox stage on the gmail_pull fixtures' shapes: the manifest in the prompt, the schema
reply written as the proposals file, the applier's dry run as verify, the apply, needs_human,
and the clean skips (no account, no mail)."""
from __future__ import annotations

import json

import pytest
from hunt_fakes import FakeAgentHarness

from src import db, gmail_pull, mail_fetch
from src.hunt import config as hc
from src.hunt import ledger
from src.hunt import run as run_mod
from src.hunt.stages import inbox as stage

SWEEP = "2026-09-18T18:56:47+00:00"
THREADS = [
    {"id": 1, "account": "apps", "from": "talent@acme.com", "from_domain": "acme.com", "date": "2026-09-17",
     "subject": "Interview invitation", "lead": "we would like to schedule a call", "hints": ["schedule?"],
     "message_id": "<m1@acme>", "thread_id": "<t1>", "job_ids": [1]},
    {"id": 2, "account": "apps", "from": "no-reply@beta.io", "from_domain": "beta.io", "date": "2026-09-16",
     "subject": "Your application", "lead": "we have decided not to move forward", "hints": ["reject?"],
     "message_id": "<m2@beta>", "thread_id": "<t2>", "job_ids": [2]},
    {"id": 3, "account": "apps", "from": "hr@gamma.dev", "from_domain": "gamma.dev", "date": "2026-09-15",
     "subject": "Senior Data Engineer", "lead": "about the data role", "hints": [],
     "message_id": "<m3@gamma>", "thread_id": "<t3>", "job_ids": [3]},
]


@pytest.fixture
def env(tmp_path, monkeypatch):
    real_connect = db.connect
    temp_connect = lambda *a, **k: real_connect(tmp_path / "jobs.db")  # noqa: E731
    monkeypatch.setattr(db, "connect", temp_connect)
    monkeypatch.setattr(gmail_pull, "connect", temp_connect)
    monkeypatch.setattr(gmail_pull, "sync_folder", lambda *a, **k: None)     # never walk the real applications/ tree
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setattr(mail_fetch, "DATA_DIR", data)
    monkeypatch.setattr(mail_fetch, "INBOX_PATH", data / "mail_inbox.json")
    monkeypatch.setattr(mail_fetch, "STATE_PATH", data / "mail_state.json")
    monkeypatch.setattr(ledger, "HUNT_DIR", tmp_path / "hunt")
    monkeypatch.setattr(run_mod, "validate_models", lambda cfg, stages, harness: [])
    conn = db.connect()
    for jid, company in ((1, "Acme"), (2, "Beta"), (3, "Gamma")):
        conn.execute("INSERT INTO jobs (id, source, external_id, canonical_key, company, title, status, applied_at) "
                     "VALUES (?,?,?,?,?,?,?, '2026-09-01')", (jid, "test", f"x{jid}", f"k{jid}", company, "Engineer", "applied"))
    conn.commit()
    return tmp_path


def _mail(monkeypatch, env, threads=THREADS, accounts=True):
    monkeypatch.setattr(mail_fetch, "mail_accounts", lambda getenv=None: (
        [mail_fetch.MailAccount("apps", "a@example.com", "pw")] if accounts else []))

    def fake_fetch() -> str:
        doc = {"generated_at": SWEEP, "accounts": [{"label": "apps", "status": "ok"}], "legend": [], "threads": threads}
        mail_fetch.INBOX_PATH.write_text(json.dumps(doc))
        return f"sweep: {SWEEP}\n" + "\n".join(mail_fetch.format_manifest(doc, 1, 1000)) + "\n"
    monkeypatch.setattr(stage, "fetch", fake_fetch)


def _prop(mid, signal, status, **extra):
    return {"manifest_id": mid, "sweep": SWEEP, "signal": signal, "proposed_status": status, **extra}


def _run(env, run_id, replies):
    (env / "fake_agent.json").write_text(json.dumps({"inbox": {"replies": replies}}))
    fake = FakeAgentHarness(env)
    lines: list[str] = []
    rc = run_mod.run(hc.defaults(), ["inbox"], "fake", cwd=env, run_id=run_id, emit=lines.append,
                     get_harness=lambda name: fake, pool_options={"sleep": lambda s: None})
    return rc, lines, fake, ledger.load_state(env / "hunt" / run_id)["stages"][0]


def test_classify_dry_run_apply_and_needs_human(env, monkeypatch):
    _mail(monkeypatch, env)
    good = {"proposals": [_prop(1, "interview_invite", "screen"), _prop(2, "rejection", "rejected"),
                          _prop(3, "ambiguous", None, needs_human="mail names a data role, the job is Engineer")]}
    short = {"proposals": good["proposals"][:2]}
    rc, lines, fake, st = _run(env, "20260918-2200", [short, good])
    assert rc == 0, lines
    [unit] = st["units"]
    assert unit["id"] == "inbox" and unit["attempts"] == 2 and unit["state"] == "done" and unit["output"] == "data/gmail_pull.json"
    assert "inbox inbox failed: 1 of 3 manifest lines have no proposal: 3" in lines
    conn = db.connect()
    assert [r["status"] for r in conn.execute("SELECT status FROM jobs ORDER BY id")] == ["screen", "rejected", "applied"]
    summ = st["summary"]
    assert (summ["threads"], summ["proposals"], summ["changes"], summ["ambiguous"]) == (3, 3, 2, 1)
    assert summ["moves"] == ["#1 Acme: applied -> screen", "#2 Beta: applied -> rejected"]
    assert "inbox: line 3: mail names a data role, the job is Engineer" in summ["needs_human"]
    assert any(n.startswith("inbox: #3 ambiguous, Senior Data Engineer from hr@gamma.dev") for n in summ["needs_human"])
    assert "inbox needs a human: inbox: line 3: mail names a data role, the job is Engineer" in lines
    written = json.loads((env / "data" / "gmail_pull.json").read_text())
    assert [p["manifest_id"] for p in written] == [1, 2, 3]
    seen = json.loads((env / "data" / "mail_state.json").read_text())["seen"]
    assert seen["m1@acme"]["signal"] == "interview_invite" and "t3" in seen
    inv = fake.calls[0]
    assert inv.tools == frozenset({"read", "bash"}) and inv.schema == stage.SCHEMA
    assert "Interview invitation | we would like to schedule a call" in inv.prompt and f"sweep: {SWEEP}" in inv.prompt
    assert "Your reply is the output: return only the JSON object" in inv.prompt and "Your reply is not read" not in inv.prompt
    run_dir = env / "hunt" / "20260918-2200"
    assert "#1 Acme" in (run_dir / "logs" / "inbox" / "apply.log").read_text()
    assert set(stage.SCHEMA["properties"]["proposals"]["items"]["properties"]["signal"]["enum"]) <= gmail_pull.KNOWN_SIGNALS


def test_a_stale_stamp_or_a_reply_that_is_not_the_schema_fails_and_nothing_is_applied(env, monkeypatch):
    _mail(monkeypatch, env, threads=THREADS[:1])
    stale = {"proposals": [{**_prop(1, "rejection", "rejected"), "sweep": "2026-09-01T00:00:00+00:00"}]}
    rc, lines, _fake, st = _run(env, "20260918-2201", ["sorry, no JSON", stale])
    assert rc == 2 and st["state"] == "failed" and "names sweep 2026-09-01" in st["note"]
    assert "inbox inbox failed: the reply was not the proposals object the schema describes" in lines
    assert db.connect().execute("SELECT status FROM jobs WHERE id=1").fetchone()[0] == "applied"
    assert not (env / "data" / "mail_state.json").exists()


def test_skipped_cleanly_with_no_account_and_with_no_mail(env, monkeypatch):
    _mail(monkeypatch, env, accounts=False)
    rc, lines, fake, st = _run(env, "20260918-2202", [])
    assert rc == 0 and st["state"] == "skipped" and st["note"].startswith("no mail account configured")
    assert fake.calls == [] and st["units"] == []
    _mail(monkeypatch, env, threads=[])
    rc, lines, fake, st = _run(env, "20260918-2203", [])
    assert rc == 0 and st["state"] == "skipped" and st["note"] == "no new mail on the open applications"
    assert st["summary"] == {"accounts": 1, "threads": 0} and fake.calls == []


def test_a_resumed_done_unit_whose_file_is_gone_runs_again_with_the_manifest_not_a_second_fetch(env, monkeypatch):
    _mail(monkeypatch, env, threads=THREADS[:2])
    good = {"proposals": [_prop(1, "interview_invite", "screen"), _prop(2, "rejection", "rejected")]}
    rc, _lines, _fake, _st = _run(env, "20260918-2204", [good])
    assert rc == 0
    led = ledger.Ledger.open(env / "hunt" / "20260918-2204")                 # as if the run died after the unit, before the stage closed
    led.state["stages"][0]["state"] = "failed"
    led._save()
    (env / "data" / "gmail_pull.json").unlink()
    monkeypatch.setattr(stage, "fetch", lambda: pytest.fail("a resume after the unit never fetches again"))
    (env / "fake_agent.json").write_text(json.dumps({"inbox": {"replies": [good]}}))
    (env / ".fake_inbox.count").unlink()
    fake = FakeAgentHarness(env)
    lines: list[str] = []
    rc = run_mod.run(hc.defaults(), [], None, cwd=env, resume="20260918-2204", emit=lines.append,
                     get_harness=lambda name: fake, pool_options={"sleep": lambda s: None})
    assert rc == 0, lines
    assert any(line.startswith("inbox inbox was done but its output no longer verifies") for line in lines)
    [inv] = fake.calls
    assert f"sweep: {SWEEP}" in inv.prompt and "Interview invitation | we would like to schedule a call" in inv.prompt
    assert "Your application | we have decided not to move forward" in inv.prompt
