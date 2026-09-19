"""Headless pilot tests for the TUI shell (Textual's run_test; no terminal needed)."""
import asyncio

import pytest

from src import db, reconcile, research
from src.tui import commands
from src.tui.app import SECTIONS, JobhuntApp
from src.tui.presets import HOT
from src.tui.widgets.status_list import StatusList


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    """The app reads through src.tui.data, which resolves these at call time. Without this a
    pilot test would open the real jobs.db."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "jobs.db")
    monkeypatch.setattr(reconcile, "APPS_DIR", tmp_path / "applications")
    monkeypatch.setattr(research, "COMPANIES_DIR", tmp_path / "companies")
    OPENED.clear()
    monkeypatch.setattr(commands, "launch", OPENED.append)   # no test opens a browser or Finder
    return tmp_path


OPENED: list[str] = []


def _add(**cols) -> int:
    conn = db.connect(db.DB_PATH)
    n = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] + 1
    row = {"source": "t", "external_id": f"x{n}", "canonical_key": f"k{n}",
           "company": "Acme", "title": "Engineer", "status": "shortlisted", **cols}
    cur = conn.execute(f"INSERT INTO jobs ({','.join(row)}) VALUES ({','.join('?' for _ in row)})",
                       list(row.values()))
    conn.commit()
    conn.close()
    return int(cur.lastrowid or 0)


def _run(coro):
    return asyncio.run(coro)


async def _settle(app, pilot):
    """Wait for the workers. An exclusive worker that a newer one replaced counts as cancelled
    and `wait_for_complete` raises for it; that is the app working as designed, so wait again
    for the one that replaced it."""
    from textual.worker import WorkerCancelled

    for _ in range(5):
        try:
            await app.workers.wait_for_complete()
            break
        except WorkerCancelled:
            continue
    await pilot.pause()


def test_boots_on_board_and_number_keys_switch_sections():
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(120, 30)) as pilot:
            assert app.current_mode == "board"
            for i, (mode, _label) in enumerate(SECTIONS, start=1):
                await pilot.press(str(i))
                assert app.current_mode == mode
            await pilot.press("1")
            assert app.current_mode == "board"
            bar = app.screen.query_one("SectionBar").render().plain
            assert "1 board" in bar and "7 settings" in bar
    _run(scenario())


def test_q_quits():
    async def scenario():
        app = JobhuntApp()
        async with app.run_test() as pilot:
            await pilot.press("q")
        assert app.return_code == 0 or app.return_code is None
    _run(scenario())


def test_status_list_shows_hot_counts_in_order_with_a_dimmed_all():
    for status, n in (("shortlisted", 3), ("applied", 2), ("discovered", 4), ("irrelevant", 5)):
        for _ in range(n):
            _add(status=status)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            sl = app.screen.query_one(StatusList)
            assert [o.id for o in sl.options] == [*HOT, "all"]
            lines = {o.id: o.prompt for o in sl.options}
            assert lines["shortlisted"].plain.split() == ["shortlisted", "3"]
            assert lines["applied"].plain.split() == ["applied", "2"]
            assert lines["offer"].plain.split() == ["offer", "0"]
            assert lines["all"].plain.split() == ["all", "4"]
            assert lines["all"].style == "dim" and lines["applied"].style == ""
    _run(scenario())


def test_moving_in_the_status_list_sets_the_table_filter():
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            assert app.screen.status_filter == "shortlisted"
            app.screen.query_one(StatusList).focus()
            await pilot.press("j")
            await pilot.pause()
            assert app.screen.status_filter == "applied"
            await pilot.press("down", "k", "k")
            await pilot.pause()
            assert app.screen.status_filter == "shortlisted"
            await pilot.press("end")
            await pilot.pause()
            assert app.screen.status_filter == "all"
    _run(scenario())


def test_jobs_table_loads_the_filter_in_preset_order_and_jkgG_move():
    from src.tui.widgets.jobs_table import JobsTable

    ids = [_add(match_score=s, company=f"Co{s}") for s in (70, 95, 80)]
    applied = _add(status="applied", match_score=99, next_followup_at="2026-09-20")
    by_score = [ids[1], ids[2], ids[0]]

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            assert app.focused is table
            assert [c.label.plain for c in table.columns.values()] == [
                " ", "score", "company", "title", "loc", "fup"]
            assert table.job_ids == by_score and table.current_id == by_score[0]
            assert table.get_row(str(by_score[0]))[0].plain == ""      # star column reserved for PR 4
            await pilot.press("j")
            assert table.current_id == by_score[1]
            await pilot.press("G")
            assert table.current_id == by_score[2]
            await pilot.press("k")
            assert table.current_id == by_score[1]
            await pilot.press("g")
            assert table.current_id == by_score[0]

            app.screen.query_one(StatusList).focus()
            await pilot.press("j")
            await _settle(app, pilot)
            assert table.job_ids == [applied]
            assert table.get_row(str(applied))[5].plain == "2026-09-20"
    _run(scenario())


def test_shortlist_and_followups_list_only_their_statuses():
    _add(status="interview", next_followup_at="2026-09-10")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await pilot.press("2")
            await _settle(app, pilot)
            assert [o.id for o in app.screen.query_one(StatusList).options] == ["shortlisted"]
            await pilot.press("3")
            await _settle(app, pilot)
            assert [o.id for o in app.screen.query_one(StatusList).options] == [
                "followups", "applied", "screen", "interview"]
    _run(scenario())


def test_table_cells_clip_and_tag_dream_rows():
    from rich.text import Text

    from src.tui.data import JobRow
    from src.tui.widgets.jobs_table import JobsTable, clip

    assert clip("a  b\n c", 10) == "a b c" and clip("abcdefghij", 5) == "abcd…"
    row = JobRow(1, "Example Robotics", "T" * 60, "San Francisco, California, United States",
                 "ashby", "shortlisted", None, None, None, True)
    cells = JobsTable().cells(row)
    assert all(isinstance(c, Text) for c in cells)
    assert cells[1].plain == "·" and len(cells[3]) == 38
    assert cells[4].plain.endswith("(dream)") and len(cells[4]) <= 18 and cells[5].plain == "·"


def _seed_detail(tmp_db) -> int:
    jid = _add(company="EasyAudit AI, Inc.", title="Forward Deployed Engineer", location="Remote LATAM",
               source="ashby", status="applied", match_score=94, applied_at="2026-09-01",
               next_followup_at="2026-09-08", notes="talked to Ana", salary_min=90000,
               salary_max=120000, currency="USD", first_seen="2026-08-30T10:00:00+00:00",
               description="<p>We deploy agents.</p><ul><li>Python</li><li>Go</li></ul>",
               match_verdict='{"recommendation": "Strong Yes", "reasons": "family B", '
                             '"missing_skills": ["Go", "k8s"]}')
    conn = db.connect(db.DB_PATH)
    db.log_event(conn, jid, "status_change", {"from": "shortlisted", "to": "applied"})
    db.log_event(conn, jid, "contact", {"date": "2026-09-05", "bumped": True})
    conn.commit()
    conn.close()
    (tmp_db / "companies").mkdir()
    (tmp_db / "companies" / "easyaudit-ai.md").write_text("researched: 2026-09-01\n")
    (tmp_db / "applications" / "applied" / f"easyaudit-ai-{jid}").mkdir(parents=True)
    return jid


def test_detail_pane_shows_every_block_for_the_highlighted_row(tmp_db):
    from src.tui.widgets.detail import DetailPane

    jid = _seed_detail(tmp_db)
    _add(status="applied", match_score=50, company="Other", title="Second")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            await _settle(app, pilot)
            app.screen.query_one(StatusList).focus()
            await pilot.press("j")
            await _settle(app, pilot)
            pane = app.screen.query_one("#detail", DetailPane)
            assert pane.display and pane.job_id == jid
            text = pane.text
            for want in (f"#{jid} EasyAudit AI, Inc.", "Forward Deployed Engineer",
                         "Remote LATAM · ashby · dream: no · USD 90,000 to 120,000",
                         "score 94 · applied · seen 2026-08-30",
                         "applied 2026-09-01  fup 2026-09-08  contact ·  folder applied/",
                         "easyaudit-ai.md", "Strong Yes", "family B", "missing: Go, k8s",
                         "talked to Ana", "contact 2026-09-05 (follow-up bumped)",
                         "shortlisted -> applied", "We deploy agents.\n\n- Python\n- Go"):
                assert want in text, want
            assert text.index("contact 2026-09-05") < text.index("shortlisted -> applied")
            assert "—" not in text

            app.screen.query_one("#jobs-table").focus()
            await pilot.press("j")
            await _settle(app, pilot)
            assert "Second" in pane.text and "not scored yet" in pane.text
            await pilot.press("enter")
            await pilot.pause()
            assert app.focused is pane
    _run(scenario())


def test_detail_collapses_under_120_columns_and_enter_opens_the_overlay(tmp_db):
    from src.tui.widgets.detail import DetailPane
    from src.tui.widgets.modals import DetailOverlay

    jid = _seed_detail(tmp_db)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(100, 30)) as pilot:
            await _settle(app, pilot)
            app.screen.query_one(StatusList).focus()
            await pilot.press("j")
            await _settle(app, pilot)
            jobs = app.screen
            assert not jobs.query_one("#detail", DetailPane).display
            jobs.query_one("#jobs-table").focus()
            await pilot.press("enter")
            await _settle(app, pilot)
            assert isinstance(app.screen, DetailOverlay)
            assert f"#{jid} EasyAudit" in app.screen.query_one(DetailPane).text
            await pilot.press("escape")
            await pilot.pause()
            assert app.screen is jobs

            await pilot.resize_terminal(150, 30)
            await pilot.pause()
            assert jobs.query_one("#detail", DetailPane).display
    _run(scenario())


def test_presets_filter_sort_and_style_overdue_followups_red():
    from datetime import date

    from src.tui.widgets.jobs_table import JobsTable

    short = _add(status="shortlisted", match_score=80)
    overdue = _add(status="applied", match_score=60, next_followup_at="2026-09-10")
    due_later = _add(status="interview", match_score=90, next_followup_at="2026-09-25")
    undated = _add(status="screen", match_score=99)
    _add(status="rejected", match_score=70, next_followup_at="2026-09-01")

    async def scenario():
        app = JobhuntApp(today=date(2026, 9, 18))
        async with app.run_test(size=(140, 30)) as pilot:
            await pilot.press("2")
            await _settle(app, pilot)
            assert app.screen.query_one(JobsTable).job_ids == [short]

            await pilot.press("3")
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            sl = app.screen.query_one(StatusList)
            assert app.screen.status_filter is None
            assert sl.options[0].prompt.plain.split() == ["follow-ups", "3"]
            assert table.job_ids == [overdue, due_later, undated]
            late, fine = table.get_row(str(overdue))[5], table.get_row(str(due_later))[5]
            assert late.plain == "2026-09-10" and late.style == "red"
            assert (fine.plain, fine.style) == ("2026-09-25", "")
            assert table.get_row(str(undated))[5].plain == "·"

            sl.focus()
            await pilot.press("j")
            await _settle(app, pilot)
            assert app.screen.status_filter == "applied" and table.job_ids == [overdue]

            await pilot.press("1")
            await _settle(app, pilot)
            sl = app.screen.query_one(StatusList)
            sl.focus()
            for _ in range(5):
                await pilot.press("j")
            await _settle(app, pilot)
            assert app.screen.status_filter == "rejected"
            stale = app.screen.query_one(JobsTable).get_row(str(app.screen.query_one(JobsTable).job_ids[0]))[5]
            assert (stale.plain, stale.style) == ("2026-09-01", "")   # a closed row's old date: not chased
    _run(scenario())


def _events(job_id: int) -> list[tuple[str, str]]:
    conn = db.connect(db.DB_PATH)
    got = [(r["kind"], r["payload"]) for r in conn.execute(
        "SELECT kind, payload FROM events WHERE job_id=? ORDER BY id", (job_id,))]
    conn.close()
    return got


def _status(job_id: int) -> str:
    conn = db.connect(db.DB_PATH)
    got = conn.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()[0]
    conn.close()
    return got


def test_status_picker_filters_applies_writes_the_event_and_moves_the_folder(tmp_db):
    from src.tui.widgets.jobs_table import JobsTable
    from src.tui.widgets.modals import StatusPicker

    first = _add(match_score=90, company="Acme")
    second = _add(match_score=80, company="Beta")
    third = _add(match_score=70, company="Gamma")
    folder = tmp_db / "applications" / "pending" / f"acme-{first}"
    folder.mkdir(parents=True)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            await pilot.press("s")
            await pilot.pause()
            assert isinstance(app.screen, StatusPicker)
            await pilot.press("escape")
            await pilot.pause()
            assert _status(first) == "shortlisted" and _events(first) == []

            await pilot.press("s", "a", "p")
            await pilot.pause()
            assert [o.id for o in app.screen.query_one("#picker-list").options] == ["applied"]
            await pilot.press("enter")
            await _settle(app, pilot)
            await _settle(app, pilot)
            assert _status(first) == "applied"
            assert _events(first) == [("status_change", '{"from": "shortlisted", "to": "applied"}')]
            assert not folder.exists()
            assert (tmp_db / "applications" / "applied" / f"acme-{first}").is_dir()
            # The row left the filter; the cursor stays on its line, now the next job.
            assert table.job_ids == [second, third] and table.current_id == second
            counts = {o.id: o.prompt.plain.split()[-1] for o in app.screen.query_one(StatusList).options}
            assert counts["shortlisted"] == "2" and counts["applied"] == "1"
    _run(scenario())


def test_picker_matches_prefix_first_then_substring():
    from src.tui.widgets.modals import StatusPicker

    assert StatusPicker.matches("") == list(HOT)
    assert StatusPicker.matches("re") == ["rejected", "screen"]
    assert StatusPicker.matches("zz") == []


def test_b_backlogs_directly_and_leaving_applied_needs_y():
    from src.tui.widgets.jobs_table import JobsTable
    from src.tui.widgets.modals import Confirm

    fresh = _add(match_score=90)
    live = _add(status="applied", match_score=80, applied_at="2026-09-01")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            await pilot.press("b")
            await _settle(app, pilot)
            await _settle(app, pilot)
            assert _status(fresh) == "backlog"

            app.screen.query_one(StatusList).focus()
            await pilot.press("j")
            await _settle(app, pilot)
            app.screen.query_one(JobsTable).focus()
            await pilot.press("b")
            await pilot.pause()
            assert isinstance(app.screen, Confirm)
            await pilot.press("n")
            await _settle(app, pilot)
            assert _status(live) == "applied" and _events(live) == []

            await pilot.press("s", "r", "e", "j", "enter")
            await pilot.pause()
            assert isinstance(app.screen, Confirm)
            await pilot.press("y")
            await _settle(app, pilot)
            await _settle(app, pilot)
            assert _status(live) == "rejected"
            assert _events(live) == [("status_change", '{"from": "applied", "to": "rejected"}')]
    _run(scenario())


def test_n_edits_notes_f_sets_the_followup_t_and_T_touch(tmp_db):
    from datetime import date, timedelta

    from src.tui import data
    from src.tui.widgets.detail import DetailPane
    from src.tui.widgets.jobs_table import JobsTable
    from src.tui.widgets.modals import NotesEditor, Prompt

    jid = _add(status="applied", applied_at="2026-09-01", notes="first")
    app_today = date(2026, 9, 18)

    async def scenario():
        app = JobhuntApp(today=app_today)
        async with app.run_test(size=(160, 40)) as pilot:
            await _settle(app, pilot)
            app.screen.query_one(StatusList).focus()
            await pilot.press("j")
            await _settle(app, pilot)
            jobs = app.screen
            table = jobs.query_one(JobsTable)
            table.focus()

            await pilot.press("n")
            await _settle(app, pilot)
            assert isinstance(app.screen, NotesEditor)
            assert app.screen.query_one("#notes-text").text == "first"
            await pilot.press("space", "x", "escape")
            await _settle(app, pilot)
            assert data.notes(jid) == "first"

            await pilot.press("n")
            await _settle(app, pilot)
            await pilot.press("space", "a", "n", "a", "ctrl+s")
            await _settle(app, pilot)
            await _settle(app, pilot)
            assert data.notes(jid) == "first ana"
            assert "first ana" in jobs.query_one("#detail", DetailPane).text

            await pilot.press("f")
            await pilot.pause()
            assert isinstance(app.screen, Prompt)
            await pilot.press("s", "o", "o", "n", "enter")
            await pilot.pause()
            assert isinstance(app.screen, Prompt)
            assert "YYYY-MM-DD" in str(app.screen.query_one("#prompt-error").content)
            for _ in range(4):
                await pilot.press("backspace")
            await pilot.press("+", "3", "enter")
            await _settle(app, pilot)
            await _settle(app, pilot)
            assert table.get_row(str(jid))[5].plain == "2026-09-21"

            await pilot.press("t")
            await _settle(app, pilot)
            await _settle(app, pilot)
            d = data.detail(jid)
            assert d.last_contact_at == date.today().isoformat() and d.row.followup == "2026-09-21"
            await pilot.press("T")
            await _settle(app, pilot)
            await _settle(app, pilot)
            assert data.detail(jid).row.followup == (date.today() + timedelta(days=7)).isoformat()
    _run(scenario())


def test_o_opens_the_posting_O_the_folder_or_the_dossier(tmp_db):
    with_folder = _seed_detail(tmp_db)
    conn = db.connect(db.DB_PATH)
    conn.execute("UPDATE jobs SET url='https://jobs.example.com/p/1' WHERE id=?", (with_folder,))
    conn.commit()
    conn.close()
    dossier_only = _add(status="applied", match_score=50, company="Dossier Co", url="file:///etc/passwd")
    (tmp_db / "companies" / "dossier-co.md").write_text("researched: 2026-09-01\n")
    bare = _add(status="applied", match_score=10, company="Bare", url="")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            app.screen.query_one(StatusList).focus()
            await pilot.press("j")
            await _settle(app, pilot)
            app.screen.query_one("#jobs-table").focus()

            await pilot.press("o", "O")
            await _settle(app, pilot)
            assert OPENED == ["https://jobs.example.com/p/1",
                              str(tmp_db / "applications" / "applied" / f"easyaudit-ai-{with_folder}")]

            OPENED.clear()
            await pilot.press("j", "o", "O")
            await _settle(app, pilot)
            assert app.screen.query_one("#jobs-table").current_id == dossier_only
            assert OPENED == [str(tmp_db / "companies" / "dossier-co.md")]   # file: URL refused

            OPENED.clear()
            await pilot.press("j", "o", "O")
            await _settle(app, pilot)
            assert app.screen.query_one("#jobs-table").current_id == bare and OPENED == []
    _run(scenario())


def test_open_posting_only_hands_http_urls_to_the_desktop(tmp_db):
    assert commands.open_posting(" https://x.example/a?b=1 ") == "opened x.example"
    assert OPENED == ["https://x.example/a?b=1"]
    for bad in ("", "file:///etc/passwd", "javascript:alert(1)", "/Applications/Calculator.app",
                "https://", "-a Calculator"):
        with pytest.raises(ValueError):
            commands.open_posting(bad)
    with pytest.raises(ValueError):
        commands.open_path(tmp_db / "nope")
    assert len(OPENED) == 1


def test_slash_searches_inside_the_filter_d_prefix_in_all_and_esc_clears():
    from src.tui.widgets.jobs_table import JobsTable

    fde = _add(match_score=90, title="Forward Deployed Engineer")
    noted = _add(match_score=80, title="Backend", notes="ask about the forward team")
    plain = _add(match_score=70, title="Platform Engineer")
    _add(status="applied", match_score=99, title="Forward Deployed Engineer II")
    cold = _add(status="discovered", match_score=60, title="Data Engineer", description="Kafka all day")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            box = app.screen.query_one("#search")
            assert not box.display
            await pilot.press("slash")
            await pilot.pause()
            assert box.display and app.focused is box
            await pilot.press(*"forward")
            await _settle(app, pilot)
            assert table.job_ids == [fde, noted]          # `s`, `o`, `b` typed, not acted on

            await pilot.press("enter")
            await pilot.pause()
            assert app.focused is table and table.job_ids == [fde, noted] and box.display
            await pilot.press("escape")
            await _settle(app, pilot)
            assert table.job_ids == [fde, noted, plain] and not box.display and box.value == ""

            app.screen.query_one(StatusList).focus()
            await pilot.press("end")
            await _settle(app, pilot)
            await pilot.press("slash", *"kafka")
            await _settle(app, pilot)
            assert table.job_ids == []
            await pilot.press("escape", "slash", *"d:kafka")
            await _settle(app, pilot)
            assert table.job_ids == [cold]
            await pilot.press("escape")
            await _settle(app, pilot)
            assert app.focused is table and len(table.job_ids) == 5
    _run(scenario())


def test_live_refresh_reloads_on_an_outside_write_and_keeps_the_cursor(monkeypatch):
    from src.tui.screens.jobs import JobsScreen
    from src.tui.widgets.jobs_table import JobsTable

    monkeypatch.setattr(JobsScreen, "POLL_SECONDS", 0.05)
    top = _add(match_score=90)
    mine = _add(match_score=80)

    async def wait_for(app, pilot, cond):
        for _ in range(60):
            await pilot.pause(0.05)
            await _settle(app, pilot)
            if cond():
                return True
        return False

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            await pilot.press("j")
            assert table.current_id == mine

            newer = _add(match_score=99)                      # a hunt in another pane
            assert await wait_for(app, pilot, lambda: table.job_ids == [newer, top, mine])
            assert table.current_id == mine                   # same job, one line lower
            counts = app.screen.query_one(StatusList).options[0].prompt.plain.split()
            assert counts == ["shortlisted", "3"]

            # Under a modal nothing reloads; the change is picked up once it closes.
            await pilot.press("s")
            await pilot.pause()
            late = _add(match_score=95)
            await pilot.pause(0.3)
            assert late not in table.job_ids
            await pilot.press("escape")
            assert await wait_for(app, pilot, lambda: late in table.job_ids)
    _run(scenario())


def test_r_forces_a_reload(monkeypatch):
    from src.tui import data
    from src.tui.screens.jobs import JobsScreen
    from src.tui.widgets.jobs_table import JobsTable

    monkeypatch.setattr(JobsScreen, "POLL_SECONDS", 3600)
    first = _add(match_score=90)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            second = _add(match_score=80)
            monkeypatch.setattr(data, "db_mtime", lambda: app.screen.seen_mtime)   # a poll would miss it
            await pilot.pause(0.1)
            assert table.job_ids == [first]
            await pilot.press("r")
            await _settle(app, pilot)
            assert table.job_ids == [first, second]
    _run(scenario())


def test_help_overlay_lists_every_binding_by_group_and_footer_reads_the_same_tables():
    from textual.widgets import Footer

    from src.tui.screens.jobs import JobsScreen
    from src.tui.widgets.modals import HelpOverlay, help_text, key_name

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(180, 50)) as pilot:
            await _settle(app, pilot)
            jobs = app.screen
            await pilot.press("question_mark")
            await pilot.pause()
            assert isinstance(app.screen, HelpOverlay)
            text = app.screen.query_one("#help-text").content.plain
            groups = app.help_groups()
            assert text == help_text(groups).plain
            titles = [t for t, _ in groups]
            assert titles[:3] == ["everywhere", "sections 1 to 3", "jobs table"]
            lines = text.splitlines()
            assert [ln for ln in lines if ln and not ln.startswith(" ")] == titles
            for _title, bindings in groups:
                for b in bindings:
                    assert f"{key_name(b):<8}{b.description}" in text, b
            for want in ("/       search", "?       help", "esc     home", "1       board",
                         "7       settings", "s       status", "T       touch and bump"):
                assert want in text, want
            assert "—" not in text
            await pilot.press("escape")
            await pilot.pause()
            assert app.screen is jobs

            shown = {(k.key, k.description) for k in jobs.query_one(Footer).query("FooterKey")}
            table = {(b.key, b.description) for b in (*JobsScreen.BINDINGS, *JobhuntApp.BINDINGS) if b.show}
            assert table <= shown and ("question_mark", "help") in shown
            assert not any(key in ("j", "k", "escape") for key, _ in shown)
    _run(scenario())


def test_esc_is_home_from_every_pane_and_modal():
    from src.tui.widgets.detail import DetailPane
    from src.tui.widgets.jobs_table import JobsTable
    from src.tui.widgets.modals import HelpOverlay

    _add(match_score=90, status="applied", applied_at="2026-09-01")
    _add(match_score=80)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            await _settle(app, pilot)
            jobs = app.screen
            table = jobs.query_one(JobsTable)

            for pane in (jobs.query_one(StatusList), jobs.query_one("#detail", DetailPane)):
                pane.focus()
                await pilot.pause()
                await pilot.press("escape")
                await pilot.pause()
                assert app.focused is table

            await pilot.press("tab")
            await pilot.pause()
            assert app.focused is not table
            await pilot.press("escape")

            for opener in ("s", "f", "n", "question_mark"):
                await pilot.press(opener)
                await _settle(app, pilot)
                assert app.screen is not jobs, opener
                await pilot.press("escape")
                await _settle(app, pilot)
                assert app.screen is jobs and app.focused is table, opener

            await pilot.press("question_mark", "question_mark")      # `?` toggles
            await pilot.pause()
            assert not isinstance(app.screen, HelpOverlay)

            await pilot.press("5", "escape")                         # a section with no home
            await pilot.pause()
            assert app.current_mode == "stats"
    _run(scenario())


HOSTILE = ("Software Engineer [on-site]", "Lead [/bold] Engineer", "[link=file:///etc/passwd]Acme[/link]",
           "Remote :smile: [red]LATAM")


def test_feed_text_with_markup_loads_and_shows_literally(tmp_db):
    """Story 5. DataTable parses a `str` cell as Rich markup, and these strings come from
    scraped postings: a tag would vanish, a stray closing tag would raise and kill the table,
    a [link=...] would plant a link that never passed the http(s) check on `o`."""
    from src.tui.widgets.detail import DetailPane
    from src.tui.widgets.jobs_table import JobsTable

    ids = [_add(match_score=90 - i, title=text, company=text[:20], location=text[:18])
           for i, text in enumerate(HOSTILE)]
    live = _add(status="applied", applied_at="2026-09-01", match_score=50, company="[/b] Co [x]")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(170, 40)) as pilot:
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            assert table.job_ids == ids
            for jid, text in zip(ids, HOSTILE, strict=True):
                _star, _score, company, title, loc, _fup = table.get_row(str(jid))
                assert title.plain == text
                assert company.plain == text[:20].strip() and loc.plain == text[:18].strip()
                assert not title.spans and not company.spans and not loc.spans   # no link, no style
            for _ in ids:
                await pilot.press("j")
                await _settle(app, pilot)
            assert HOSTILE[-1] in app.screen.query_one("#detail", DetailPane).text

            # The same strings reach the confirm modal and the toast through a status change.
            app.screen.query_one(StatusList).focus()
            await pilot.press("j")
            await _settle(app, pilot)
            table.focus()
            await pilot.press("b", "y")
            await _settle(app, pilot)
            await _settle(app, pilot)
            assert _status(live) == "backlog"

            # A typed value is echoed in the prompt's error line.
            app.screen.query_one(StatusList).focus()
            await pilot.press("k")
            await _settle(app, pilot)
            table.focus()
            await pilot.press("f", *"[/bold]", "enter")
            await pilot.pause()
            assert "[/bold]" in app.screen.query_one("#prompt-error").content.plain
    _run(scenario())
