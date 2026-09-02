"""Phase A of docs/spec-mail-fetch.md: the read-only multi-account inbox pull.
Hermetic: a fake IMAP client with canned RFC 822 messages, tmp_path DB/state/output."""
from __future__ import annotations

import json
import re
from datetime import date
from email.message import EmailMessage
from pathlib import Path

import pytest

from src import mail_fetch as mf
from src.db import connect, log_event

TODAY = date(2026, 9, 2)
ME = "me@apps.example"


# ----------------------------------------------------------------------------- fixtures

def mk(uid, frm, subject, body, *, day="01 Sep 2026", to=ME, mid=None, refs=None, reply_to=None,
       headers=None, html_body=None):
    msg = EmailMessage()
    msg["From"] = frm
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = f"Tue, {day} 10:00:00 +0000"
    msg["Message-ID"] = f"<{mid or f'm{uid}@x'}>"
    if reply_to:
        msg["In-Reply-To"] = f"<{reply_to}>"
    if refs:
        msg["References"] = " ".join(f"<{r}>" for r in refs)
    for k, v in (headers or {}).items():
        msg[k] = v
    msg.set_content(body)
    if html_body is not None:
        msg.add_alternative(html_body, subtype="html")
    return uid, msg.as_bytes()


class FakeImap:
    """Enough of imaplib for the sweep. Asserts read-only usage."""
    def __init__(self, folders: dict[str, list[tuple[int, bytes]]], *, gmail=False, fail_login=False):
        self.folders = folders
        self.gmail = gmail
        self.fail_login = fail_login
        self.calls: list[tuple] = []
        self.cur = ""

    def capability(self):
        return ("OK", [b"IMAP4rev1 IDLE" + (b" X-GM-EXT-1" if self.gmail else b"")])

    def login(self, user, password):
        self.calls.append(("login", user))
        if self.fail_login:
            raise Exception("[AUTHENTICATIONFAILED] Invalid credentials (Failure)")  # noqa: TRY002

    def select(self, mailbox="INBOX", readonly=False):
        self.calls.append(("select", mailbox, readonly))
        if mailbox not in self.folders:
            raise Exception(f"SELECT failed: {mailbox}")  # noqa: TRY002
        self.cur = mailbox
        return ("OK", [b"1"])

    @staticmethod
    def _terms(args):
        s = " ".join(a for a in args if a).replace('\\"', '"')
        terms = re.findall(r'"([^"]+)"', s)
        for tok in re.sub(r'"[^"]*"', " ", s).split():
            if tok.upper() in ("OR", "TEXT", "SINCE", "X-GM-RAW") or tok.startswith("after:") \
                    or re.match(r"\d{1,2}-\w{3}-\d{4}$", tok):
                continue
            terms.append(tok[5:] if tok.startswith("from:") else tok)
        return [t.lower() for t in terms]

    def uid(self, command, *args):
        self.calls.append(("uid", command, args))
        msgs = self.folders[self.cur]
        if command == "SEARCH":
            terms = self._terms(args[1:])
            hit = [u for u, raw in msgs if not terms or any(t in raw.decode(errors="replace").lower() for t in terms)]
            return ("OK", [" ".join(str(u) for u in hit).encode()])
        if command == "FETCH":
            uids = [int(x) for x in args[0].split(",")]
            what = args[1]
            assert "PEEK" in what, f"non-PEEK fetch: {what}"
            data = []
            for u, raw in msgs:
                if u not in uids:
                    continue
                payload = raw.split(b"\n\n", 1)[0] + b"\n\n" if "HEADER.FIELDS" in what else raw
                data.append((f"{u} (UID {u} {what[1:-1]} {{{len(payload)}}}".encode(), payload))
                data.append(b")")
            return ("OK", data)
        raise AssertionError(f"write command issued on a read-only sweep: {command}")

    def logout(self):
        self.calls.append(("logout",))


def uid_calls(fake, cmd):
    return [c for c in fake.calls if c[0] == "uid" and c[1] == cmd]


def factory_for(*fakes: FakeImap):
    """client_factory returning fakes in order, one per (account) connection."""
    it = iter(fakes)

    def _factory(host, port):
        f = next(it)
        f.calls.append(("connect", host, port))
        return f
    return _factory


def row(jid, company, url=None, status="applied", applied="2026-08-20", contact=None, title="Engineer"):
    return {"id": jid, "company": company, "title": title, "url": url, "status": status,
            "applied_at": applied, "last_contact_at": contact, "first_seen": "2026-08-01"}


@pytest.fixture
def hints():
    return mf.load_hints(Path(__file__).resolve().parent.parent / "config" / "mail_hints.yaml")


@pytest.fixture
def acct():
    return mf.MailAccount("apps", ME, "pw", "imap.example.com", 993, ["INBOX"], ["alias@apps.example"])


def run(acct, fake, jobs, hints, tmp_path, **kw):
    kw.setdefault("today", TODAY)
    return mf.sweep(None, [acct], hints, jobs=jobs, state_path=tmp_path / "state.json",
                    client_factory=factory_for(fake), **kw)


# ----------------------------------------------------------------------------- config

def test_mail_accounts_parsing():
    env = {"MAIL_ACCOUNTS": "Personal, apps",
           "MAIL_PERSONAL_USER": "p@gmail.com", "MAIL_PERSONAL_PASS": "",
           "MAIL_APPS_USER": "a@corp.io", "MAIL_APPS_PASS": "abcd efgh ijkl mnop",
           "MAIL_APPS_HOST": "mail.corp.io:1993", "MAIL_APPS_FOLDERS": "INBOX, Archive",
           "MAIL_APPS_ALIASES": "Me@Corp.io", "MAIL_APPS_REPLY_AS": "a@corp.io"}
    accts = mf.mail_accounts(env.get)
    assert [a.label for a in accts] == ["personal", "apps"]
    p, a = accts
    assert p.password is None and p.user == "p@gmail.com" and p.host == "imap.gmail.com" and p.port == 993
    assert a.password == "abcdefghijklmnop" and a.host == "mail.corp.io" and a.port == 1993
    assert a.folders == ["INBOX", "Archive"] and a.aliases == ["me@corp.io"] and a.reply_as == "a@corp.io"
    assert mf.mail_accounts({}.get) == []
    with pytest.raises(ValueError):
        mf.mail_accounts({"MAIL_ACCOUNTS": "bad label"}.get)


@pytest.mark.parametrize("raw,norm", [
    ("Acme Labs Inc.", "acme"), ("Wizeline", "wizeline"), ("Cosuno GmbH", "cosuno"),
    ("Grupo Bimbo S.A. de C.V.", "grupo bimbo"), ("Framework Computer", "framework computer"),
    ("Clara", "clara"), ("Handle, Inc", "handle"), ("Wízeline", "wizeline"),
])
def test_normalize_company(raw, norm):
    assert mf.normalize_company(raw) == norm


@pytest.mark.parametrize("url,domain,slug", [
    ("https://boards.greenhouse.io/clara/jobs/123", None, "clara"),
    ("https://job-boards.greenhouse.io/framework-computer/jobs/9", None, "framework computer"),
    ("https://jobs.ashbyhq.com/openai/abc-123", None, "openai"),
    ("https://jobs.lever.co/acme/uuid", None, "acme"),
    ("https://acme.teamtailor.com/jobs/1", None, "acme"),
    ("https://acme.wd5.myworkdayjobs.com/en-US/careers/job/1", None, "acme"),
    ("https://jobs.cosuno.com/o/senior-dev", "cosuno.com", None),
    ("https://boards.wizeline.com/x", "wizeline.com", None),
    ("https://www.getonbrd.com/jobs/x", None, None),
    ("https://kraken.co.uk/careers/1", "kraken.co.uk", None),
    (None, None, None),
])
def test_domain_and_slug(url, domain, slug):
    assert mf.domain_from_url(url) == domain
    assert mf.slug_from_url(url) == slug


def test_job_keys_strength_and_aliases(hints):
    clara = mf.job_keys(row(1, "Clara", "https://boards.greenhouse.io/clara/jobs/1"), hints)
    openai = mf.job_keys(row(2, "OpenAI", "https://jobs.ashbyhq.com/openai/x"), hints)
    wiz = mf.job_keys(row(3, "Wizeline", "https://boards.wizeline.com/x"), hints)
    fw = mf.job_keys(row(4, "Framework Computer", "https://ats.rippling.com/framework-computer/jobs/1"), hints)
    handle = mf.job_keys(row(5, "Handle", None), hints)
    assert clara.is_weak and openai.is_weak and not wiz.is_weak and not fw.is_weak and handle.is_weak
    assert ("framework", "alias") in fw.names and "frame.work" in fw.domains
    assert "usehandle.ai" in handle.domains
    assert wiz.domains == ["wizeline.com"] and clara.domains == []
    assert clara.window == "2026-08-18"        # applied 08-20 minus 2 days
    late = mf.job_keys(row(6, "X", None, contact="2026-08-30"), hints)
    assert late.window == "2026-08-28"


def test_search_args(hints):
    fw = mf.job_keys(row(4, "Framework Computer", "https://ats.rippling.com/framework-computer/jobs/1"), hints)
    std = mf.search_args(fw, gmail=False)
    assert std == ('SINCE 18-Aug-2026 OR TEXT "framework computer" OR TEXT "framework" TEXT "frame.work"',)
    gm = mf.search_args(fw, gmail=True)
    assert gm[0] == "X-GM-RAW"
    assert gm[1] == '"(\\"framework computer\\" OR framework OR from:frame.work) after:2026/08/18"'
    assert mf.search_args(mf.job_keys(row(7, "日本", None), hints), gmail=False) is None


# ----------------------------------------------------------------------------- the sweep

def test_sweep_end_to_end_read_only(acct, hints, tmp_path):
    jobs = [mf.job_keys(row(412, "Wizeline", "https://boards.wizeline.com/x", status="screen"), hints),
            mf.job_keys(row(388, "Cosuno", "https://jobs.cosuno.com/o/x"), hints)]
    fake = FakeImap({"INBOX": [
        mk(1, "Alejandro <alejandro@wizeline.com>", "Wizeline | Zoom Interview",
           "Hello Santiago,\n\nMy name is Alejandro. I would like to invite you to a Zoom interview; "
           "could you share your availability this week?\n\nBest,\nAlejandro\n-- \nWizeline Talent"),
        mk(2, "Cosuno <no-reply@cosuno.com>", "Your application at Cosuno - Senior Dev",
           "Hi Santiago, Thanks so much for your application. We have now reviewed it and unfortunately "
           "decided to move forward with other candidates whose experience more closely matches.",
           day="29 Aug 2026"),
        mk(3, "Suno <hello@suno.com>", "Guess what today is", "You joined Suno 665 days ago!"),
    ]})
    res = run(acct, fake, jobs, hints, tmp_path)
    rep = res.accounts[0]
    assert rep.status == "ok" and rep.candidates == 2 and rep.threads == 2
    assert [t["job_ids"] for t in res.threads] == [[412], [388]]
    wiz, cos = res.threads
    assert wiz["hints"] == ["schedule?"] and "availability" in wiz["lead"]
    assert cos["hints"] == ["reject?"] and "other candidates" in cos["lead"]
    assert wiz["message_id"] == "m1@x" and wiz["thread_id"] == "m1@x"
    assert "snippet" not in wiz and "Wizeline Talent" not in res.snippets[1]
    assert res.legend[0] == {"job_id": 412, "company": "Wizeline", "title": "Engineer", "status": "screen",
                             "applied_at": "2026-08-20", "threads": 1, "capped": 0}
    # read-only by protocol
    assert ("select", "INBOX", True) in fake.calls
    fetches = uid_calls(fake, "FETCH")
    assert fetches and all("PEEK" in c[2][1] for c in fetches)
    assert fake.calls[-1] == ("logout",)
    # standard server: SINCE + OR chain, never X-GM-RAW even on a gmail hostname
    searches = [c[2] for c in uid_calls(fake, "SEARCH")]
    assert all(s[1].startswith("SINCE ") for s in searches)
    state = json.loads((tmp_path / "state.json").read_text())
    assert "swept_at" in state["accounts"]["apps"]


def test_gmail_capability_detected_not_hostname(acct, hints, tmp_path):
    jobs = [mf.job_keys(row(1, "Wizeline", "https://boards.wizeline.com/x"), hints)]
    fake = FakeImap({"INBOX": []}, gmail=True)
    acct.host = "mail.notgoogle.example"
    run(acct, fake, jobs, hints, tmp_path)
    searches = [c[2] for c in uid_calls(fake, "SEARCH")]
    assert searches and searches[0][1] == "X-GM-RAW"


def test_scan_all_pulls_horizon_headers(acct, hints, tmp_path):
    jobs = [mf.job_keys(row(1, "Wizeline", "https://boards.wizeline.com/x"), hints)]
    fake = FakeImap({"INBOX": [mk(1, "a@wizeline.com", "hi", "hello there")]})
    res = run(acct, fake, jobs, hints, tmp_path, scan_all=True)
    searches = [c[2] for c in uid_calls(fake, "SEARCH")]
    assert searches == [(None, "SINCE 18-Aug-2026")]
    assert res.accounts[0].threads == 1


def test_local_confirmation_word_boundary_and_window(acct, hints, tmp_path):
    jobs = [mf.job_keys(row(1, "Clara", "https://boards.greenhouse.io/clara/jobs/1", applied="2026-08-20"), hints),
            mf.job_keys(row(2, "Kraken", "https://kraken.com/careers/1", applied="2026-08-25"), hints)]
    fake = FakeImap({"INBOX": [
        mk(1, "Legal <legal@somewhere.com>", "Declaration of conformity", "your declaration is ready"),
        mk(2, "Ana <ana@gmail.com>", "Clara interview", "Hi, from Clara here, interview?"),
        mk(3, "Corp <hr@corp.com>", "Clara role", "we at Clara would like to talk"),   # corporate sender: no subject match
        mk(4, "Kraken <jobs@kraken.com>", "Kraken: next steps", "next steps", day="20 Aug 2026"),  # before window
        mk(5, "Kraken <jobs@kraken.com>", "Kraken: next steps", "next steps", day="28 Aug 2026"),
    ]})
    res = run(acct, fake, jobs, hints, tmp_path)
    got = {t["message_id"]: t for t in res.threads}
    assert "m1@x" not in got and "m3@x" not in got and "m4@x" not in got
    assert got["m2@x"]["strength"] == "weak" and got["m2@x"]["match_on"] == ["name_subject"]
    assert got["m5@x"]["match_on"] == ["domain", "name_from"] and got["m5@x"]["strength"] == "strong"


def test_relay_pass_body_match_only_for_relay_domains(acct, hints, tmp_path):
    jobs = [mf.job_keys(row(1, "Acme Robotics", "https://boards.greenhouse.io/acmerobotics/jobs/1"), hints)]
    fake = FakeImap({"INBOX": [
        mk(1, "no-reply@us.greenhouse-mail.io", "Interview with the team",
           "Hi Santiago, Acme Robotics would like to schedule an interview.", headers={"List-Unsubscribe": "<x>"}),
        mk(2, "news@random.com", "Acme Robotics newsletter", "Acme Robotics in the body only"),
    ]})
    res = run(acct, fake, jobs, hints, tmp_path)
    assert [t["match_on"] for t in res.threads] == [["body"]]
    assert res.threads[0]["strength"] == "strong"          # List-Unsubscribe never cuts a body-matched ATS mail
    body_fetches = [c[2][0] for c in uid_calls(fake, "FETCH") if c[2][1] == "(UID BODY.PEEK[])"]
    assert body_fetches == ["1"]                           # the non-relay message was never body-fetched


# ----------------------------------------------------------------------------- noise cuts

def _msg(frm, subject, *, day="2026-09-01", mid="m1", refs=None, reply_to="", headers=None, matches=None):
    h = headers or {}
    m = mf.Message(1, "apps", "INBOX", "", frm, frm.rsplit("@", 1)[-1], ME, subject, day, mid, reply_to,
                   refs or [], bool(h.get("List-Unsubscribe")), h.get("Precedence", ""), h.get("Auto-Submitted", ""))
    m.matches = matches or {1: ["name_subject"]}
    return m


def test_cut_reasons(hints):
    job = mf.job_keys(row(1, "Acme", "https://acme.com/jobs/1", applied="2026-08-30"), hints)
    cuts = mf.Cuts({"root9"}, {"kraken.com"}, {ME, "alias@apps.example"}, hints.receipts, {1: job})
    cr = mf.cut_reason
    assert cr(_msg("a@acme.com", "x", refs=["root9", "m2"]), cuts) == "seen"
    assert cr(_msg("bot@news.kraken.com", "x"), cuts) == "ignored"
    assert cr(_msg("alias@apps.example", "Re: x"), cuts) == "own"
    assert cr(_msg("hr@acme.com", "x", headers={"Auto-Submitted": "auto-replied"}), cuts) == "autoreply"
    assert cr(_msg("jobs-noreply@linkedin.com", "New jobs for you"), cuts) == "alerts"
    assert cr(_msg("messages-noreply@linkedin.com", "Recruiter sent you a message"), cuts) is None
    assert cr(_msg("promo@x.com", "Acme sale", headers={"List-Unsubscribe": "<u>", "Precedence": "bulk"}), cuts) == "alerts"
    assert cr(_msg("hr@acme.com", "Invite", headers={"List-Unsubscribe": "<u>", "Precedence": "bulk"},
                   matches={1: ["domain"]}), cuts) is None                  # domain match protects
    assert cr(_msg("hr@acme.com", "Accepted: Interview @ Tue"), cuts) == "echoes"
    assert cr(_msg("hr@acme.com", "Invitation: Interview @ Tue"), cuts) is None
    assert cr(_msg("no-reply@acme.com", "Thank you for your application", day="2026-08-31"), cuts) == "receipts"
    assert cr(_msg("no-reply@acme.com", "Thank you for your application", day="2026-09-08"), cuts) is None
    assert cr(_msg("no-reply@acme.com", "Thank you for your application", day="2026-08-31",
                   reply_to="m0"), cuts) is None                              # not first in thread
    cuts.enabled = False
    assert cr(_msg("jobs-noreply@linkedin.com", "New jobs for you"), cuts) is None
    assert cr(_msg("a@acme.com", "x", refs=["root9"]), cuts) == "seen"       # seen survives --keep-noise


def test_seen_from_events_and_state(tmp_path):
    conn = connect(tmp_path / "jobs.db")
    conn.execute("INSERT INTO jobs (id, source, external_id, canonical_key, company, status) VALUES (1,'t','x','k','A','applied')")
    log_event(conn, 1, "email_signal", {"message_id": "<abc@x>", "thread_id": "root1"})
    log_event(conn, 1, "email_signal", {"message_id": "19f7ff19e2d8c72f"})     # legacy hex id, harmless
    conn.commit()
    seen = mf.load_seen(conn, {"seen": {"m9": "ambiguous"}}, full=False)
    assert seen == {"abc@x", "root1", "19f7ff19e2d8c72f", "m9"}
    assert mf.load_seen(conn, {"seen": {"m9": "ambiguous"}}, full=True) == set()


# ----------------------------------------------------------------------------- threads, rank, cap

def test_collapse_threads_and_own_reply(acct, hints, tmp_path):
    jobs = [mf.job_keys(row(1, "Acme", "https://acme.com/jobs/1"), hints)]
    fake = FakeImap({"INBOX": [
        mk(1, "hr@acme.com", "Interview", "first: can you do Tuesday?", day="25 Aug 2026", mid="r1"),
        mk(2, ME, "Re: Acme interview", "Tuesday works for me", day="26 Aug 2026", refs=["r1"], reply_to="r1"),
        mk(3, "hr@acme.com", "Re: Interview", "Great, confirmed for Tuesday at 10.", day="27 Aug 2026",
           refs=["r1", "m2@x"], reply_to="m2@x"),
        # fallback-keyed thread (no References): same subject + domain, within 7 days
        mk(4, "no-reply@acme.com", "Update on your application", "we are still reviewing", day="20 Aug 2026"),
        mk(5, "no-reply@acme.com", "Update on your application", "unfortunately we will not be moving forward",
           day="24 Aug 2026"),
        # same subject but 20 days later: its own thread
        mk(6, "no-reply@acme.com", "Update on your application", "new role opened, interested?", day="01 Sep 2026"),
    ]})
    res = run(acct, fake, jobs, hints, tmp_path, limit_per_job=0)
    by_mid = {t["message_id"]: t for t in res.threads}
    assert set(by_mid) == {"m3@x", "m5@x", "m6@x"}
    assert by_mid["m3@x"]["thread_len"] == 2 and by_mid["m3@x"]["thread_id"] == "r1"
    assert by_mid["m5@x"]["thread_len"] == 2 and by_mid["m6@x"]["thread_len"] == 1
    assert res.accounts[0].noise == {"own": 1, "collapsed": 2}


def test_rank_then_cap_keeps_recruiter_reply(acct, hints, tmp_path):
    jobs = [mf.job_keys(row(1, "Linear", "https://jobs.ashbyhq.com/linear/x"), hints)]
    msgs = [mk(i, f"Linear <updates{i}@linear.app>", f"Linear changelog {i}", "new features shipped",
               day=f"{25 + i} Aug 2026") for i in range(1, 6)]
    msgs.append(mk(9, "Recruiting <no-reply@hire.lever.co>", "Linear: next steps",
                   "Hi Santiago, the Linear team would like to schedule a call.", day="20 Aug 2026"))
    fake = FakeImap({"INBOX": msgs})
    res = run(acct, fake, jobs, hints, tmp_path, limit_per_job=3)
    assert len(res.threads) == 3
    assert res.threads[0]["message_id"] == "m9@x" and res.threads[0]["match_on"] == ["name_subject", "relay"]
    assert res.threads[0]["strength"] == "strong"
    assert res.legend[0]["threads"] == 3 and res.legend[0]["capped"] == 3
    # 'linear' is weak (yaml), so the changelog lines carry the flag
    assert all(t["strength"] == "weak" for t in res.threads[1:])


def test_auto_demotion_and_tune_line(acct, hints, tmp_path):
    hints.weak_names.discard("mercury")
    jobs = [mf.job_keys(row(1, "Mercury", "https://jobs.ashbyhq.com/mercury/x"), hints)]
    assert not jobs[0].is_weak
    msgs = [mk(i, f"Mercury <m@site{i}.com>", "Mercury update", "hello", day=f"{20 + i} Aug 2026") for i in range(1, 8)]
    fake = FakeImap({"INBOX": msgs})
    res = run(acct, fake, jobs, hints, tmp_path, limit_per_job=0)
    assert jobs[0].demoted and all(t["strength"] == "weak" for t in res.threads)
    assert any('"Mercury" matched mail from 7 sender domains' in t and "weak_names" in t for t in res.tune)
    # two domains: stays strong, no tune line
    jobs2 = [mf.job_keys(row(1, "Mercury", "https://jobs.ashbyhq.com/mercury/x"), hints)]
    res2 = run(acct, FakeImap({"INBOX": msgs[:2]}), jobs2, hints, tmp_path, limit_per_job=0)
    assert not jobs2[0].demoted and res2.tune == [] and res2.threads[0]["strength"] == "strong"


def test_zero_candidate_tune_after_three_sweeps(acct, hints, tmp_path):
    jobs = [mf.job_keys(row(3077, "Ghostco", "https://ghostco.com/jobs/1", title="Software Engineer"), hints)]
    tune = []
    for _ in range(3):
        res = run(acct, FakeImap({"INBOX": []}), jobs, hints, tmp_path)
        tune = res.tune
    assert any("job 3077 (Ghostco, Software Engineer) produced 0 candidates in 3" in t and "aliases" in t
               for t in tune)
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["zero_candidates"] == {"apps": {"3077": 3}}


def test_zero_candidate_tune_waits_for_every_mailbox(acct, hints, tmp_path):
    """--account apps three times must not blame the company for mail on `personal`."""
    jobs = [mf.job_keys(row(3077, "Ghostco", "https://ghostco.com/jobs/1"), hints)]
    for _ in range(4):
        res = run(acct, FakeImap({"INBOX": []}), jobs, hints, tmp_path, all_labels=["apps", "personal"])
    assert not any("produced 0 candidates" in t for t in res.tune)
    # a sweep where the account errors must not move the counter either
    bad = mf.MailAccount("apps", ME, "pw", "imap.x.com")
    res = mf.sweep(None, [bad], hints, jobs=jobs, state_path=tmp_path / "state.json",
                   client_factory=factory_for(FakeImap({}, fail_login=True)), today=TODAY)
    assert json.loads((tmp_path / "state.json").read_text())["zero_candidates"] == {"apps": {"3077": 4}}


def test_cli_rejects_unknown_status(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(mf, "connect", lambda: connect(tmp_path / "jobs.db"))
    with pytest.raises(SystemExit) as e:
        mf.main(["--status", "aplied"])
    assert e.value.code == 2 and "invalid choice" in capsys.readouterr().err


def test_message_identity_semantics():
    a = _msg("a@acme.com", "x")
    b = _msg("a@acme.com", "x")
    assert a != b and len({a, b}) == 2 and a in [a] and b not in [a]


# ----------------------------------------------------------------------------- text

def test_extract_and_clean_text():
    _, raw = mk(1, "a@b.com", "s", "Plain body here.", html_body="<p>HTML body</p>")
    assert mf.extract_text(raw).strip() == "Plain body here."
    m = EmailMessage()
    m["From"] = "a@b.com"
    m.set_content("<html><body><p>Hi Santiago,</p><p>Only &amp; html &mdash; here</p><style>p{}</style></body></html>",
                  subtype="html", charset="utf-8", cte="quoted-printable")
    assert mf.html_to_text(mf.extract_text(m.as_bytes())).split() == "Hi Santiago, Only & html , here".split()
    text = ("Hola Santiago,\n\nGracias por tu tiempo. Queremos agendar una entrevista técnica.\n"
            "Ver https://calendly.com/x/y?token=abc para reservar.\n\n"
            "On Mon, Aug 31 2026, Santiago wrote:\n> old stuff\n> more\n\n-- \nAna\nUnsubscribe here")
    clean = mf.clean_text(text)
    assert clean == "Hola Santiago, Gracias por tu tiempo. Queremos agendar una entrevista técnica. Ver calendly.com para reservar."
    assert mf.clean_text("A — B") == "A , B"
    assert mf.clean_text("") == "(no text)" and mf.clean_text("   \n ") == "(no text)"
    long = mf.clean_text("word " * 400, limit=100)
    assert len(long) <= 104 and long.endswith("...")
    sig = mf.clean_text("Short note about the interview slot tomorrow morning.\nSent from my iPhone")
    assert sig == "Short note about the interview slot tomorrow morning."


def test_hints_and_lead(hints):
    m = _msg("hr@acme.com", "Update", matches={1: ["domain"]})
    m.snippet = ("Hi Santiago, Thank you so much for taking the time to speak with our team last week. "
                 "After careful review we have decided to move forward with other candidates whose "
                 "experience is a closer fit. We will keep your profile on file.")
    mf.tag_hints(m, hints)
    assert m.hints == ["reject?"]
    assert "other candidates" in m.lead and m.lead.startswith("...") and "Hi Santiago" not in m.lead
    assert len(m.lead) <= 150
    m2 = _msg("ana@gmail.com", "Quick question", matches={1: ["name_subject"]})
    m2.snippet = "Hi Santiago, Thanks for reaching out. I saw your profile and wanted to ask whether you are open to a chat about our platform team and what you are looking for next."
    mf.tag_hints(m2, hints)
    assert m2.hints == ["human?"]
    assert m2.lead.startswith("I saw your profile") and m2.lead.endswith("...") and len(m2.lead) <= 124
    m3 = _msg("no-reply@acme.com", "Thank you for your application", matches={1: ["domain"]})
    m3.snippet = "(no text)"
    mf.tag_hints(m3, hints)
    assert m3.hints == ["receipt?"] and m3.lead == "(no text)"
    m4 = _msg("hr@acme.com", "Entrevista técnica", matches={1: ["domain"]})
    m4.snippet = "Hola, queremos agendar una prueba técnica contigo la próxima semana."
    mf.tag_hints(m4, hints)
    assert set(m4.hints) == {"schedule?", "assessment?"}


# ----------------------------------------------------------------------------- output + CLI

def _doc(n=3, **acct_over):
    threads = [{"id": i, "account": "apps", "accounts_seen": ["apps"], "job_ids": [10 + i], "match_on": ["domain"],
                "strength": "weak" if i == 2 else "strong", "hints": ["reject?"] if i == 1 else [],
                "thread_id": f"t{i}", "thread_len": 1, "from": f"Ana <ana{i}@acme.com>", "from_domain": "acme.com",
                "to": ME, "subject": f"Subject {i}", "date": "2026-09-01", "message_id": f"m{i}", "lead": f"lead {i}"}
               for i in range(1, n + 1)]
    acct = {"label": "apps", "user": ME, "host": "h", "folders": ["INBOX"], "status": "ok",
            "candidates": n, "threads": n, "noise": {"receipts": 2, "collapsed": 0}, **acct_over}
    legend = [{"job_id": 10 + i, "company": "Acme", "title": "Eng", "status": "applied", "applied_at": "2026-08-20",
               "threads": 1, "capped": 0} for i in range(1, n + 1)]
    return {"generated_at": "x", "since": "2026-08-01", "open_jobs": n, "accounts": [acct],
            "tune": ["tune: something"], "legend": legend, "threads": threads}


def test_write_and_format(tmp_path, acct, hints):
    jobs = [mf.job_keys(row(1, "Acme", "https://acme.com/jobs/1"), hints)]
    res = run(acct, FakeImap({"INBOX": [mk(1, "hr@acme.com", "Hi", "the body text")]}), jobs, hints, tmp_path)
    inbox, snips = tmp_path / "inbox.json", tmp_path / "snips.jsonl"
    mf.write_result(res, inbox, snips)
    doc = json.loads(inbox.read_text())
    assert "snippet" not in doc["threads"][0] and doc["threads"][0]["lead"] == "the body text"
    assert mf.load_snippets(snips) == {1: "the body text"}
    summary = mf.format_summary(doc)
    assert summary[0].startswith("apps") and "candidates 1  threads 1" in summary[0]
    show = mf.format_show(doc, mf.load_snippets(snips), [1, 7])
    assert show[0].startswith("[1] apps job 1 | hr@acme.com | 2026-09-01 | Hi") and show[1] == "the body text"
    assert show[3] == "[7] unknown id"


def test_manifest_paging_and_columns():
    doc = _doc(5)
    page1 = mf.format_manifest(doc, page=1, page_size=2)
    assert len(page1) == 4 and page1[-1] == "3 more lines, run: python -m src.mail_fetch manifest --page 2"
    assert page1[1].split("|")[0].strip().endswith("Subject 1") and "reject?" in page1[1]
    assert " weak " in page1[2] or page1[2].rstrip().split()[-4:-2] == ["weak", "Subject"]
    page3 = mf.format_manifest(doc, page=3, page_size=2)
    assert len(page3) == 2 and "more lines" not in page3[-1]
    empty = mf.format_manifest({"threads": []})
    assert empty[-1] == "(no threads)"
    free = dict(doc["threads"][0], from_domain="gmail.com", **{"from": "Ana Ruiz <ana@gmail.com>"})
    assert mf._from_col(free) == "Ana Ruiz (freemail)"


def test_cli_show_limit_and_no_accounts(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(mf, "INBOX_PATH", tmp_path / "inbox.json")
    monkeypatch.setattr(mf, "SNIPPETS_PATH", tmp_path / "snips.jsonl")
    monkeypatch.setattr(mf, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(mf, "connect", lambda: connect(tmp_path / "jobs.db"))
    monkeypatch.setattr(mf, "get_secret", lambda k, default=None: None)
    assert mf.main([]) == 0
    out = capsys.readouterr().out
    assert "no mail accounts configured" in out and "(no threads)" in out
    doc = json.loads((tmp_path / "inbox.json").read_text())
    assert doc["accounts"] == [] and doc["threads"] == []
    assert mf.main(["show", *[str(i) for i in range(26)]]) == 1
    assert mf.main(["manifest"]) == 0


def test_account_error_row_alongside_working(hints, tmp_path):
    jobs = [mf.job_keys(row(1, "Acme", "https://acme.com/jobs/1"), hints)]
    bad = mf.MailAccount("personal", "p@x.com", "pw", "imap.x.com")
    good = mf.MailAccount("apps", ME, "pw", "imap.y.com")
    skipped = mf.MailAccount("old", "", None)
    fakes = factory_for(FakeImap({}, fail_login=True), FakeImap({"INBOX": [mk(1, "hr@acme.com", "Hi", "body")]}))
    res = mf.sweep(None, [bad, good, skipped], hints, jobs=jobs, state_path=tmp_path / "s.json",
                   client_factory=fakes, today=TODAY)
    st = {a.label: a.status for a in res.accounts}
    assert st["personal"].startswith("error: Exception: [AUTHENTICATIONFAILED]")
    assert st["apps"] == "ok" and st["old"] == "skipped: MAIL_OLD_USER not set"
    assert len(res.threads) == 1
    assert "pw" not in json.dumps([a.__dict__ for a in res.accounts])


def test_cross_account_dedupe(hints, tmp_path):
    jobs = [mf.job_keys(row(1, "Acme", "https://acme.com/jobs/1"), hints)]
    a1 = mf.MailAccount("apps", ME, "pw", "imap.a.com")
    a2 = mf.MailAccount("personal", "p@x.com", "pw", "imap.b.com")
    same = mk(1, "hr@acme.com", "Hi", "body", mid="shared@acme")
    fakes = factory_for(FakeImap({"INBOX": [same]}), FakeImap({"INBOX": [same]}))
    res = mf.sweep(None, [a1, a2], hints, jobs=jobs, state_path=tmp_path / "s.json", client_factory=fakes, today=TODAY)
    assert len(res.threads) == 1 and res.threads[0]["accounts_seen"] == ["apps", "personal"]


def test_max_days_floor_and_since(acct, hints, tmp_path):
    jobs = [mf.job_keys(row(1, "Acme", "https://acme.com/jobs/1", applied="2026-01-05"), hints)]
    res = run(acct, FakeImap({"INBOX": []}), jobs, hints, tmp_path, max_days=30)
    assert res.since == "2026-08-03" and res.tune[0].startswith("note: horizon floored to 2026-08-03")
    assert jobs[0].window == "2026-08-03"
    res2 = run(acct, FakeImap({"INBOX": []}), jobs, hints, tmp_path, since="2026-07-01", max_days=30)
    assert res2.since == "2026-07-01"


def test_receipt_gate_end_to_end(acct, hints, tmp_path):
    jobs = [mf.job_keys(row(1, "Acme", "https://acme.com/jobs/1", applied="2026-08-30"), hints)]
    fake = FakeImap({"INBOX": [
        mk(1, "no-reply@acme.com", "Thank you for your application", "We received it.", day="30 Aug 2026"),
        mk(2, "no-reply@acme.com", "Thank you for your application",
           "After review, unfortunately we will not be moving forward.", day="01 Sep 2026"),
    ]})
    res = run(acct, fake, jobs, hints, tmp_path)
    assert res.accounts[0].noise == {"receipts": 1}
    assert len(res.threads) == 1 and set(res.threads[0]["hints"]) == {"reject?", "receipt?"}
    assert res.threads[0]["message_id"] == "m2@x"
