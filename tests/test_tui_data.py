"""src/tui/data.py on a temp DB: hot/cold filtering, presets, search, verdicts, events, paths."""
import json
import os

import pytest

from src import db, reconcile, research
from src.tui import data
from src.tui.presets import HOT


@pytest.fixture
def env(tmp_path, monkeypatch):
    """A temp DB, applications tree and dossier dir; returns an `add(**cols) -> id` helper."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "jobs.db")
    monkeypatch.setattr(reconcile, "APPS_DIR", tmp_path / "applications")
    monkeypatch.setattr(research, "COMPANIES_DIR", tmp_path / "companies")
    (tmp_path / "companies").mkdir()
    seq = iter(range(1, 10_000))

    def add(**cols) -> int:
        n = next(seq)
        row = {"source": "t", "external_id": f"x{n}", "canonical_key": f"k{n}",
               "company": "Acme", "title": "Engineer", "status": "shortlisted", **cols}
        conn = db.connect(db.DB_PATH)
        cur = conn.execute(
            f"INSERT INTO jobs ({','.join(row)}) VALUES ({','.join('?' for _ in row)})",
            list(row.values()))
        conn.commit()
        conn.close()
        return int(cur.lastrowid or 0)

    add.tmp = tmp_path  # type: ignore[attr-defined]
    return add


def test_hot_is_db_statuses_order_without_cold_or_hidden():
    assert HOT == ("shortlisted", "applied", "screen", "interview", "offer",
                   "rejected", "ghosted", "withdrawn", "backlog")


def test_counts_hot_with_zeros_and_all_is_discovered(env):
    for status, n in (("shortlisted", 2), ("applied", 1), ("discovered", 3),
                      ("irrelevant", 4), ("expired", 5)):
        for _ in range(n):
            env(status=status)
    got = data.counts()
    assert list(got) == [*HOT, "all"]
    assert got["shortlisted"] == 2 and got["applied"] == 1 and got["offer"] == 0
    assert got["all"] == 3
    assert "irrelevant" not in got and "expired" not in got and "discovered" not in got


def test_board_hides_cold_rows_and_all_shows_discovered_never_dropped(env):
    hot = env(status="applied", match_score=70)
    cold = env(status="discovered", match_score=99)
    env(status="irrelevant")
    env(status="expired")
    assert [r.id for r in data.rows("board")] == [hot]
    assert [r.id for r in data.rows("board", "all")] == [cold, hot]
    for bad in ("discovered", "irrelevant", "expired", "nope"):
        with pytest.raises(ValueError):
            data.rows("board", bad)


def test_all_view_caps_only_the_discovered_rows(env, monkeypatch):
    monkeypatch.setattr(data, "ALL_CAP", 2)
    for _ in range(4):
        env(status="discovered")
    hot = env(status="applied")
    got = data.rows("board", "all")
    assert [r.status for r in got] == ["discovered", "discovered", "applied"] and got[-1].id == hot


def test_all_view_reaches_discovered_behind_more_hot_rows_than_the_cap(env, monkeypatch):
    """The shape of the real DB: hundreds of scored hot rows, discovered mostly unscored. One
    score-sorted list under one cap showed the hot rows only, with and without a query."""
    monkeypatch.setattr(data, "ALL_CAP", 5)
    for i in range(12):
        env(status="shortlisted", match_score=90 - i, title="Platform Engineer")
    cold = [env(status="discovered", title="Platform Engineer", match_score=40),
            env(status="discovered", title="Platform Engineer"),
            env(status="discovered", title="Data Analyst", description="Platform team, Kafka")]

    got = data.rows("board", "all")
    # Cold first (scored, then unscored newest first), and every hot row follows.
    assert [r.id for r in got[:3]] == [cold[0], cold[2], cold[1]] and len(got) == 15
    assert data.counts()["all"] == 3 == sum(r.status == "discovered" for r in got)

    broad = data.rows("board", "all", "engineer")
    assert [r.id for r in broad[:2]] == cold[:2] and len(broad) == 14
    assert all(r.status == "shortlisted" for r in broad[2:])
    assert [r.id for r in data.rows("board", "all", "d:kafka")] == [cold[2]]
    assert {r.id for r in data.rows("board", "all", "d:platform") if r.status == "discovered"} == set(cold)


def test_status_pick_filters_and_board_sorts_by_score_nulls_last(env):
    low = env(status="shortlisted", match_score=60)
    high = env(status="shortlisted", match_score=90)
    unscored = env(status="shortlisted")
    env(status="applied", match_score=95)
    assert [r.id for r in data.rows("board", "shortlisted")] == [high, low, unscored]
    assert [r.id for r in data.rows("shortlist")] == [high, low, unscored]


def test_followups_preset_pins_live_statuses_and_sorts_by_date(env):
    later = env(status="applied", next_followup_at="2026-09-20", match_score=90)
    sooner = env(status="interview", next_followup_at="2026-09-10", match_score=50)
    undated = env(status="screen", match_score=99)
    env(status="shortlisted", next_followup_at="2026-09-01")
    env(status="rejected")
    got = data.rows("followups")
    assert [r.id for r in got] == [sooner, later, undated]
    assert got[0].followup == "2026-09-10"


def test_query_matches_title_company_notes_inside_the_filter(env):
    by_title = env(title="Forward Deployed Engineer")
    by_company = env(company="Deployd Labs")
    by_notes = env(notes="recruiter said deploy team")
    env(title="Backend", description="we deploy daily")
    env(status="applied", title="Deployment Strategist")
    got = {r.id for r in data.rows("board", "shortlisted", "deploy")}
    assert got == {by_title, by_company, by_notes}


def test_query_escapes_like_wildcards(env):
    env(title="100% remote")
    env(title="Remote")
    assert [r.title for r in data.rows("board", None, "100%")] == ["100% remote"]
    assert data.rows("board", None, "_") == []


def test_description_prefix_only_in_the_all_view(env):
    hit = env(status="discovered", title="Backend", description="Kafka and Flink")
    assert [r.id for r in data.rows("board", "all", "d:kafka")] == [hit]
    assert data.rows("board", "all", "kafka") == []
    # Outside `all` the prefix is plain text, so nothing matches it.
    env(status="shortlisted", title="Backend", description="Kafka")
    assert data.rows("board", "shortlisted", "d:kafka") == []


def test_row_carries_the_dream_flag_from_the_profile(env):
    env(company="Example Robotics")
    env(company="Acme")
    flags = {r.company: r.dream for r in data.rows("board")}
    assert flags == {"Example Robotics": True, "Acme": False}


def test_parse_verdict_shapes():
    scored = data.parse_verdict(json.dumps({
        "score": 85, "recommendation": "Strong Yes", "missing_skills": ["Go", "k8s"],
        "strengths": ["TypeScript"], "reasons": "fits family B"}))
    assert scored.recommendation == "Strong Yes" and scored.reasons == "fits family B"
    assert scored.missing_skills == ("Go", "k8s") and scored.strengths == ("TypeScript",)
    assert scored.bucket is None and not scored.empty

    triaged = data.parse_verdict('{"triage": "keep", "reason": "in scope", "bucket": 2}')
    assert triaged.recommendation == "triage keep" and triaged.reasons == "in scope"
    assert triaged.bucket == 2 and triaged.missing_skills == ()

    assert data.parse_verdict(None).empty and data.parse_verdict("").empty
    assert data.parse_verdict("not json").raw == "not json"
    assert data.parse_verdict("[1, 2]").raw == "[1, 2]"
    assert data.parse_verdict('{"missing_skills": "Go"}').missing_skills == ("Go",)


def test_detail_fields_and_last_five_events_newest_first(env):
    jid = env(status="applied", url="https://x.test/1", remote=1, salary_min=90000,
              salary_max=120000, currency="USD", notes="hello", description="the JD",
              match_score=88, match_verdict='{"recommendation": "Yes", "missing_skills": ["Go"]}')
    other = env()
    conn = db.connect(db.DB_PATH)
    for i in range(7):
        db.log_event(conn, jid, "note", {"note": f"n{i}"})
    db.log_event(conn, other, "note", {"note": "someone else"})
    conn.execute("INSERT INTO events (job_id, ts, kind, payload) VALUES (?,?,?,?)",
                 (jid, "2026-09-18T00:00:00+00:00", "contact", "broken{"))
    conn.commit()
    conn.close()

    d = data.detail(jid)
    assert d is not None
    assert d.row.id == jid and d.row.status == "applied" and d.row.score == 88
    assert (d.url, d.remote, d.salary_min, d.salary_max, d.currency) == (
        "https://x.test/1", True, 90000, 120000, "USD")
    assert d.notes == "hello" and d.description == "the JD"
    assert d.verdict.missing_skills == ("Go",)
    assert len(d.events) == 5
    assert d.events[0].kind == "contact" and d.events[0].payload == {"raw": "broken{"}
    assert [e.payload["note"] for e in d.events[1:]] == ["n6", "n5", "n4", "n3"]


def test_detail_missing_id_is_none(env):
    env()
    assert data.detail(999) is None


def test_detail_resolves_dossier_and_folder(env):
    jid = env(company="EasyAudit AI, Inc.", status="applied")
    d = data.detail(jid)
    assert d is not None and d.dossier is None and d.folder is None and d.bucket is None

    dossier = env.tmp / "companies" / "easyaudit-ai.md"
    dossier.write_text("researched: 2026-09-01\n")
    folder = env.tmp / "applications" / "applied" / f"easyaudit-ai-{jid}"
    folder.mkdir(parents=True)
    (env.tmp / "applications" / "pending" / f"other-co-{jid}0").mkdir(parents=True)

    d = data.detail(jid)
    assert d is not None
    assert d.dossier == dossier
    assert (d.bucket, d.folder) == ("applied", folder)


def test_db_mtime_follows_the_wal_and_is_zero_without_a_db(env):
    assert data.db_mtime() == 0.0
    env()
    main = db.DB_PATH
    wal = main.with_name(main.name + "-wal")
    os.utime(main, (1_000, 1_000))
    assert wal.exists() or data.db_mtime() == 1_000
    wal.touch()
    os.utime(wal, (2_000, 2_000))
    assert data.db_mtime() == 2_000


def test_plain_description_keeps_paragraphs_and_handles_escaped_html():
    raw = '<div class="x"><h3>About</h3> <p>We build &amp; ship.</p><ul><li>Python</li><li> Go </li></ul></div>'
    assert data.plain_description(raw) == "About\n\nWe build & ship.\n\n- Python\n- Go"
    escaped = "&lt;p&gt;He didn&#39;t&amp;nbsp;stop.&lt;/p&gt;&lt;p&gt;Next&lt;/p&gt;"
    assert data.plain_description(escaped) == "He didn't stop.\n\nNext"
    assert data.plain_description("plain\n\n\n\ntext  here") == "plain\n\ntext here"
    assert data.plain_description(None) == ""


def test_concurrent_first_reads_on_a_fresh_db_do_not_lock(env):
    """The screen starts counts, rows and detail workers together. Each used to run the schema
    and the WAL switch, and on a fresh file one of them lost with "database is locked"."""
    from concurrent.futures import ThreadPoolExecutor

    for round_ in range(60):
        db.DB_PATH = env.tmp / f"fresh{round_}.db"      # env's monkeypatch restores it
        with ThreadPoolExecutor(8) as pool:
            got = list(pool.map(lambda _: data.counts()["all"], range(16)))
        assert got == [0] * 16


def test_set_status_writes_the_event_schedules_the_followup_and_moves_the_folder(env):
    jid = env(company="Acme", status="shortlisted")
    folder = env.tmp / "applications" / "pending" / f"acme-{jid}"
    folder.mkdir(parents=True)

    line = data.set_status(jid, "applied")
    assert line.startswith(f"#{jid} Acme: shortlisted -> applied") and "pending/ -> applied/" in line
    d = data.detail(jid)
    assert d is not None and d.row.status == "applied" and d.row.applied_at and d.row.followup
    assert d.bucket == "applied"
    assert [(e.kind, e.payload) for e in d.events] == [
        ("status_change", {"from": "shortlisted", "to": "applied"})]

    for bad in ("irrelevant", "expired", "discovered", "declined"):
        with pytest.raises(ValueError):
            data.set_status(jid, bad)
    with pytest.raises(ValueError):
        data.set_status(999, "applied")


def test_confirm_only_when_leaving_the_pipeline_statuses():
    assert data.needs_confirm("applied", "rejected") and data.needs_confirm("offer", "backlog")
    assert data.needs_confirm("screen", "interview")
    assert not data.needs_confirm("shortlisted", "applied")
    assert not data.needs_confirm("rejected", "applied") and not data.needs_confirm("applied", "applied")


def test_parse_followup_forms():
    from datetime import date

    today = date(2026, 9, 18)
    assert data.parse_followup("2026-10-01", today) == "2026-10-01"
    assert data.parse_followup(" +7 ", today) == "2026-09-25"
    assert data.parse_followup("+0", today) == data.parse_followup("T", today) == "2026-09-18"
    assert data.parse_followup("", today) == data.parse_followup("-", today) == ""
    for bad in ("tomorrow", "+x", "+", "2026-13-01", "09/18/2026"):
        with pytest.raises(ValueError):
            data.parse_followup(bad, today)


def test_notes_followup_and_touch_write_through_db(env):
    from datetime import date, timedelta

    jid = env(status="applied", notes="old")
    assert data.notes(jid) == "old" and data.notes(999) == ""

    assert data.set_notes(jid, "  new text \n") == f"#{jid} notes saved"
    assert data.set_followup(jid, "2026-10-01") == f"#{jid} follow-up 2026-10-01"
    d = data.detail(jid)
    assert d is not None and d.notes == "new text" and d.row.followup == "2026-10-01"
    assert d.row.status == "applied"
    assert d.events[0].kind == "note" and d.events[0].payload == {"note": "new text", "edit": True}

    assert data.set_followup(jid, "") == f"#{jid} follow-up cleared"
    assert data.touch(jid).endswith(f"contact {date.today().isoformat()}")
    d = data.detail(jid)
    assert d is not None and d.row.followup is None and d.last_contact_at == date.today().isoformat()

    bumped = (date.today() + timedelta(days=7)).isoformat()      # fixtures carry no notify.yaml: 7
    assert data.touch(jid, bump=True).endswith(f"follow-up {bumped}")
    d = data.detail(jid)
    assert d is not None and d.row.followup == bumped
    assert [e.kind for e in d.events[:2]] == ["contact", "contact"] and d.events[0].payload["bumped"]

    assert data.set_notes(jid, "") == f"#{jid} notes cleared" and data.notes(jid) == ""
    long = "x" * 500
    data.set_notes(jid, long)
    d = data.detail(jid)
    assert d is not None and d.notes == long and len(d.events[0].payload["note"]) == 200
    with pytest.raises(ValueError):
        data.set_followup(jid, "soon")
    with pytest.raises(ValueError):
        data.set_notes(999, "x")


def test_sort_orders_in_both_directions_with_empty_values_last(env):
    from src.tui.presets import Sort

    b = env(company="beta", title="Zeta", match_score=70, location="Berlin", next_followup_at="2026-09-20")
    a = env(company="Acme", title="alpha", match_score=90, location="", next_followup_at="2026-09-10")
    c = env(company="Core", title="Mid", location="Austin")             # no score, no date

    def ids(column, desc):
        return [r.id for r in data.rows("board", "shortlisted", sort=Sort(column, desc))]

    assert ids("score", True) == [a, b, c] and ids("score", False) == [b, a, c]
    assert ids("company", False) == [a, b, c] and ids("company", True) == [c, b, a]   # case-blind
    assert ids("title", False) == [a, c, b]
    assert ids("loc", False) == [c, b, a] and ids("loc", True) == [b, c, a]            # "" is empty too
    assert ids("fup", False) == [a, b, c] and ids("fup", True) == [b, a, c]
    assert [r.id for r in data.rows("board", "shortlisted")] == [a, b, c]              # preset order untouched

    assert Sort.first("score").desc and not Sort.first("company").desc
    with pytest.raises(ValueError):
        data.rows("board", sort=Sort("notes; DROP TABLE jobs", False))


def test_sort_keeps_the_query_and_the_cold_first_all_view(env, monkeypatch):
    from src.tui.presets import Sort

    monkeypatch.setattr(data, "ALL_CAP", 2)
    hot = [env(company=c, title="Engineer") for c in ("Zed", "Abc")]
    cold = [env(status="discovered", company=c, title="Engineer") for c in ("Yak", "Bee", "Cat")]
    env(company="Aaa", title="Designer")

    got = data.rows("board", "all", "engineer", Sort("company", False))
    assert [r.id for r in got] == [cold[1], cold[2], hot[1], hot[0]]    # each half A to Z, cold capped at 2


def test_stars_are_what_pick_would_choose(env):
    """A dream row takes a slot below higher scores, a company already in play is skipped,
    an unscored row is never starred, and the real applications tree is never read."""
    top = [env(match_score=s, company=f"Co{s}") for s in (95, 90, 85, 80, 75)]
    dream_row = env(match_score=60, company="Example Robotics", location="Berlin, Germany")
    far_dream = env(match_score=99, company="Example Robotics", location="Austin, TX, USA")
    busy = env(match_score=99, company="Busy Co")
    env(status="applied", company="Busy Co")
    foldered = env(match_score=98, company="Folder Co")
    (env.tmp / "applications" / "pending" / f"folder-co-{foldered}").mkdir(parents=True)
    env(match_score=None, company="Unscored")
    got = data.stars()
    assert got == {*top[:4], dream_row}
    assert far_dream not in got and busy not in got and foldered not in got

    # never stored: the star goes the moment the row leaves shortlisted, the next one takes it
    data.set_status(top[0], "backlog")
    assert data.stars() == {*top[1:5], dream_row}


def test_stars_first_keeps_each_half_in_order(env):
    found = [env(match_score=s, company=f"Co{s}") for s in (90, 80, 70, 60)]
    rows = data.rows("shortlist")
    assert [r.id for r in data.stars_first(rows, {found[3], found[1]})] == [
        found[1], found[3], found[0], found[2]]
