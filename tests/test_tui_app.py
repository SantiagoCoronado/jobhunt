"""Headless pilot tests for the TUI shell (Textual's run_test; no terminal needed)."""
import pytest
from tui_fakes import _add, COPIED, _key, OPENED, _run, _settle

from src import db
from src.tui import commands
from src.tui.app import SECTIONS, JobhuntApp
from src.tui.presets import HOT
from src.tui.widgets.status_list import StatusList

pytestmark = pytest.mark.usefixtures("tmp_db")


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
            assert "1 board" in bar and "2 follow-ups" in bar and "6 settings" in bar
            assert len(SECTIONS) == 6 and "shortlist " not in bar
    _run(scenario())


def test_q_quits():
    async def scenario():
        app = JobhuntApp()
        async with app.run_test() as pilot:
            await pilot.press("q")
        assert app.return_code == 0 or app.return_code is None
    _run(scenario())


def test_status_list_shows_hot_counts_in_order_with_a_dimmed_all_then_the_dream_list():
    for status, n in (("shortlisted", 3), ("applied", 2), ("discovered", 4), ("irrelevant", 5)):
        for _ in range(n):
            _add(status=status)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            sl = app.screen.query_one(StatusList)
            assert [o.id for o in sl.options] == [*HOT, "all", "dream"]
            lines = {o.id: o.prompt for o in sl.options}
            assert lines["dream"].plain.split() == ["dream", "list", "0"]
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
            assert app.screen.status_filter == "dream"
            await pilot.press("k")
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
                " ", "score ▼", "company", "title", "loc", "fup"]      # the board leads with score
            assert table.job_ids == by_score and table.current_id == by_score[0]
            assert [table.get_row(str(i))[0].plain for i in by_score] == ["●"] * 3    # pre-selected: what a hunt would tailor
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


def test_followups_lists_only_its_statuses():
    _add(status="interview", next_followup_at="2026-09-10")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await pilot.press("2")                            # the shortlist section is gone: 2 is follow-ups
            await _settle(app, pilot)
            assert app.current_mode == "followups"
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
            await _settle(app, pilot)
            assert app.screen.query_one(JobsTable).job_ids == [short]   # the board opens on `shortlisted`

            await pilot.press(_key("followups"))
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
            # Acme has a folder, so it is in play and no pick: the two picks lead `shortlisted`.
            assert table.job_ids == [second, third, first]
            await pilot.press("G", "s")
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
            # The row left the filter; the cursor stays on its line, or the last one left.
            assert table.job_ids == [second, third] and table.current_id == third
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
            await pilot.press("end", "k")                 # `all`, just above the dream list
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
    from src.tui.widgets.modals import HelpOverlay, help_text, key_name, long_text

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
            assert titles[:3] == ["everywhere", "board and follow-ups", "jobs table"]
            lines = text.splitlines()
            assert [ln for ln in lines if ln and not ln.startswith(" ")] == titles
            for _title, bindings in groups:
                for b in bindings:
                    assert f"{key_name(b):<8}{long_text(b)}" in text, b       # shown in the footer or not
            for want in ("/       search", "?       help", "esc     home", "1       board", "q       quit",
                         "6       settings", "s       status", "T       touch and bump", "b       backlog",
                         "c       copy /jh-tailor lines", ">       sort by next column"):
                assert want in text, want
            assert "—" not in text
            await pilot.press("escape")
            await pilot.pause()
            assert app.screen is jobs

            shown = {(k.key, k.description) for k in jobs.query_one(Footer).query("FooterKey")}
            table = {(b.key, b.description) for b in (*JobsScreen.BINDINGS, *JobhuntApp.BINDINGS)
                     if b.show and jobs.check_action(b.action, ())}     # `a` `x` wait for the dream list entry
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

            await pilot.press(_key("stats"), "escape")                         # a section with no home
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
    from src.tui.widgets.jobs_table import JobsTable, clip

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
                _mark, _score, company, title, loc, _fup = table.get_row(str(jid))
                assert title.plain == clip(text, table.widths["title"])      # the title takes the table's slack
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


def test_real_run_path_boots_board_without_a_screen_stack_error():
    """`App.run()` turns on asyncio's eager task factory (run_test does not), which composes the
    first screen synchronously during registration. With board as DEFAULT_MODE that raised
    "No screens on stack" from the search Input's mount on every real launch (2026-09-19)."""
    app = JobhuntApp()
    seen: dict = {}

    async def auto_pilot(pilot):
        await pilot.pause()
        seen["mode"] = app.current_mode
        seen["screen"] = type(app.screen).__name__
        await pilot.press("q")

    app.run(headless=True, auto_pilot=auto_pilot, size=(140, 40))
    assert app._exception is None
    assert app.return_code == 0
    assert seen == {"mode": "board", "screen": "JobsScreen"}


def test_sort_keys_and_header_click_order_the_table_and_mark_the_header():
    from src.tui.presets import Sort
    from src.tui.widgets.jobs_table import JobsTable

    low = _add(match_score=60, company="Acme")
    high = _add(match_score=90, company="Zed")
    mid = _add(match_score=75, company="Mid")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)

            def labels():
                return [c.label.plain for c in table.columns.values()]

            assert table.job_ids == [high, mid, low] and labels()[1] == "score ▼"
            await pilot.press("j")
            assert table.current_id == mid

            await pilot.press("minus")
            await _settle(app, pilot)
            assert table.job_ids == [low, mid, high] and labels()[1] == "score ▲"
            assert table.current_id == mid                                  # the cursor follows the job

            await pilot.press("greater_than_sign")
            await _settle(app, pilot)
            assert app.screen.sort == Sort("company", False)
            assert table.job_ids == [low, mid, high] and labels()[1:3] == ["score", "company ▲"]
            await pilot.press("minus")
            await _settle(app, pilot)
            assert table.job_ids == [high, mid, low] and labels()[2] == "company ▼"

            await pilot.press("less_than_sign")
            await _settle(app, pilot)
            assert app.screen.sort == Sort("score", True)
            await pilot.press("less_than_sign")                             # wraps to the last column
            await _settle(app, pilot)
            assert app.screen.sort == Sort("fup", False) and labels()[5] == "fup ▲"

            # A search and a reload keep the sort; `=` hands the order back to the section.
            await pilot.press("greater_than_sign", "greater_than_sign", "minus")   # score, company, desc
            await pilot.press("slash", "d", "enter")
            await _settle(app, pilot)
            assert table.job_ids == [high, mid]                             # Zed, Mid: company Z to A
            await pilot.press("escape", "r")
            await _settle(app, pilot)
            assert table.job_ids == [high, mid, low] and app.screen.sort == Sort("company", True)
            await pilot.press("equals_sign")
            await _settle(app, pilot)
            assert app.screen.sort is None and labels()[1] == "score ▼" and labels()[2] == "company"

            # Header click: first click sorts by the column, the next one flips it.
            title_x = 22 + 1 + 3 + 9 + 22 + 2                               # inside the title header
            await pilot.click(JobsTable, offset=(title_x - 22, 0))
            await _settle(app, pilot)
            assert app.screen.sort == Sort("title", False), labels()
            await pilot.click(JobsTable, offset=(title_x - 22, 0))
            await _settle(app, pilot)
            assert app.screen.sort == Sort("title", True) and labels()[3] == "title ▼"
            await pilot.click(JobsTable, offset=(1, 0))                     # the mark column: ignored
            await _settle(app, pilot)
            assert app.screen.sort == Sort("title", True)
    _run(scenario())


def test_followups_marks_its_own_lead_and_flips_from_it():
    from src.tui.presets import Sort
    from src.tui.widgets.jobs_table import JobsTable

    soon = _add(status="applied", next_followup_at="2026-09-10")
    late = _add(status="screen", next_followup_at="2026-09-25")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await pilot.press(_key("followups"))
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            assert table.columns["fup"].label.plain == "fup ▲" and table.job_ids == [soon, late]
            await pilot.press("minus")
            await _settle(app, pilot)
            assert app.screen.sort == Sort("fup", True) and table.job_ids == [late, soon]
    _run(scenario())


def test_shortlisted_on_the_board_leads_with_the_hunt_picks_and_a_chosen_sort_overrides_them():
    """Seven scored companies: `pick` takes five, the dream row among them at 60, below two
    rows it passed over. The board's `shortlisted` view lifts it above them (the rule the
    shortlist section had); every other status keeps plain score order."""
    ids = [_add(match_score=s, company=f"Co{s}") for s in (95, 90, 85, 80, 75, 70)]
    dream = _add(match_score=60, company="Example Robotics", location="Berlin, Germany")
    held = _add(match_score=99, company="Busy Co")
    busy = _add(status="applied", company="Busy Co")
    from src.tui.widgets.jobs_table import JobsTable

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            assert app.screen.status_filter == "shortlisted"
            assert table.job_ids == [*ids[:4], dream, held, *ids[4:]]
            marked = [i for i in table.job_ids if table.get_row(str(i))[0].plain == "●"]
            assert marked == [*ids[:4], dream]           # a dream slot, Busy Co in play, five in all
            assert table.preselected == set(marked) and table.selected == set()
            await pilot.press("minus")                    # score ascending: the reader's sort wins
            await _settle(app, pilot)
            assert table.job_ids == [dream, *reversed(ids), held]
            await pilot.press("equals_sign")
            await _settle(app, pilot)
            assert table.job_ids[:5] == [*ids[:4], dream]
            app.screen.query_one(StatusList).highlighted = len(HOT)   # `all`: any other status
            await _settle(app, pilot)
            assert app.screen.status_filter == "all"
            assert table.job_ids == [held, *ids, dream, busy]          # plain score order
    _run(scenario())


def test_space_v_and_esc_select_rows_and_the_footer_counts_them():
    ids = [_add(company=f"Co{n}") for n in range(3)][::-1]   # unscored: no hunt picks, newest first
    from src.tui.widgets.footer import SectionFooter
    from src.tui.widgets.jobs_table import JobsTable

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            footer = app.screen.query_one(SectionFooter)
            assert footer.note == ""
            await pilot.press("space")                       # marks the row, steps down
            await pilot.pause()
            assert table.selected == {ids[0]} and table.current_id == ids[1]
            assert table.get_row(str(ids[0]))[0].plain == "●"
            assert table.get_row(str(ids[1]))[0].plain == ""
            assert footer.note == "1 selected"
            await pilot.pause()
            assert footer.query_one("#footer-note").render().plain == "1 selected"
            await pilot.press("k", "space")                  # a second space takes the mark off
            await pilot.pause()
            assert table.selected == set() and footer.note == ""
            await pilot.press("v")
            await pilot.pause()
            assert table.selected == set(ids) and footer.note == "3 selected"
            assert [r.id for r in table.selected_rows] == ids
            await pilot.press("r")                           # a reload of the same view keeps it
            await _settle(app, pilot)
            assert table.selected == set(ids)
            assert table.get_row(str(ids[2]))[0].plain == "●"
            await pilot.press("escape")
            await pilot.pause()
            assert table.selected == set() and footer.note == ""
            assert table.get_row(str(ids[2]))[0].plain == ""
            await pilot.press("v")
            app.screen.query_one(StatusList).focus()
            await pilot.press("j")                           # another filter: the selection is the app's, it stays
            await _settle(app, pilot)
            assert table.job_ids == [] and table.selected == set(ids) and footer.note == "3 selected"
            assert [r.id for r in app.selection.selected_rows] == ids
            await pilot.press("k")
            await _settle(app, pilot)
            assert [table.get_row(str(i))[0].plain for i in ids] == ["●"] * 3
    _run(scenario())


def test_marks_are_shared_by_the_jobs_sections_and_go_when_the_row_leaves_the_listed_statuses():
    live = _add(status="applied", company="Live Co")
    short = _add(company="Short Co")
    from src.tui.widgets.footer import SectionFooter
    from src.tui.widgets.jobs_table import JobsTable

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await pilot.press(_key("followups"))
            await _settle(app, pilot)
            await pilot.press("space")                       # marked in follow-ups
            await pilot.pause()
            assert app.selection.selected == {live}
            await pilot.press(_key("board"))
            await _settle(app, pilot)
            board = app.screen.query_one(JobsTable)
            assert board.job_ids == [short] and app.screen.query_one(SectionFooter).note == "1 selected"
            await pilot.press("space")
            app.screen.query_one(StatusList).highlighted = list(HOT).index("applied")
            await _settle(app, pilot)
            assert board.job_ids == [live] and board.get_row(str(live))[0].plain == "●"   # shows in section 1
            for section in ("apps", "stats", "run", "settings", "followups"):
                await pilot.press(_key(section))
                await _settle(app, pilot)
                assert app.screen.query_one(SectionFooter).note == "2 selected", section
            assert app.screen.query_one(JobsTable).get_row(str(live))[0].plain == "●"

            conn = db.connect(db.DB_PATH)                    # a hunt expires the posting meanwhile
            conn.execute("UPDATE jobs SET status='expired' WHERE id=?", (short,))
            conn.commit()
            conn.close()
            await pilot.press("r")
            await _settle(app, pilot)
            assert app.selection.selected == {live} and app.screen.query_one(SectionFooter).note == "1 selected"
            await pilot.press("escape")
            await pilot.pause()
            assert app.selection.marked == set()
    _run(scenario())


def test_bulk_status_change_asks_once_and_writes_every_row():
    live = [_add(status="applied", company=f"Live{i}", match_score=90 - i) for i in range(2)]
    fresh = _add(status="shortlisted", company="Fresh", match_score=50)
    from src.tui.widgets.jobs_table import JobsTable
    from src.tui.widgets.modals import Confirm, StatusPicker

    def statuses():
        conn = db.connect(db.DB_PATH)
        got = dict(conn.execute("SELECT id, status FROM jobs").fetchall())
        conn.close()
        return got

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            app.screen.status_filter = None                  # every hot row in one table
            app.screen.load_rows()
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            table.focus()
            await pilot.press("v", "s")
            await pilot.pause()
            assert isinstance(app.screen, StatusPicker) and app.screen.heading == "3 selected"
            await pilot.press("r", "e", "j", "enter")
            await pilot.pause()
            assert isinstance(app.screen, Confirm)           # one question for the batch
            assert app.screen.question == "3 jobs to rejected: 2 of them leave applied?"
            await pilot.press("n")
            await _settle(app, pilot)
            assert set(statuses().values()) == {"applied", "shortlisted"}
            assert table.selected == {*live, fresh}          # backing out spends nothing
            await pilot.press("s", "r", "e", "j", "enter", "y")
            await _settle(app, pilot)
            assert set(statuses().values()) == {"rejected"}
            assert table.selected == set()
            conn = db.connect(db.DB_PATH)
            n = conn.execute("SELECT COUNT(*) FROM events WHERE kind='status_change'").fetchone()[0]
            conn.close()
            assert n == 3                                    # each row keeps its own event

            await pilot.press("v", "b")                      # nothing live is left: no question
            await _settle(app, pilot)
            assert set(statuses().values()) == {"backlog"}
    _run(scenario())


def test_hunt_picks_arrive_preselected_feed_c_and_never_the_bulk_verbs(monkeypatch):
    from src.tui.widgets.footer import SectionFooter
    from src.tui.widgets.jobs_table import PICK_STYLE, JobsTable

    ids = [_add(match_score=s, company=f"Co{s}") for s in (90, 80, 70)]
    plain = _add(match_score=None, company="Unscored")       # listed, never a pick
    toasts: list[str] = []

    def statuses():
        conn = db.connect(db.DB_PATH)
        got = dict(conn.execute("SELECT id, status FROM jobs").fetchall())
        conn.close()
        return got

    async def scenario():
        app = JobhuntApp()
        monkeypatch.setattr(app, "notify", lambda line, **kw: toasts.append(line))
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            footer = app.screen.query_one(SectionFooter)
            assert table.preselected == set(ids) and footer.note == "3 hunt picks"
            mark = table.get_row(str(ids[0]))[0]
            assert mark.plain == "●" and mark.style == PICK_STYLE
            await pilot.press("c")                           # a fresh table: what a hunt would tailor
            await _settle(app, pilot)
            assert COPIED[-1] == "\n".join(f"/jh-tailor {i}" for i in ids)
            assert toasts[-1] == f"copied 3 commands: /jh-tailor {', '.join(map(str, ids))}"

            await pilot.press("b")                           # the pre-selection is not a bulk target
            await _settle(app, pilot)
            assert statuses() == {ids[0]: "backlog", ids[1]: "shortlisted", ids[2]: "shortlisted",
                                  plain: "shortlisted"}
            assert table.preselected == set(ids[1:]) and footer.note == "2 hunt picks"

            await pilot.press("g", "space")                  # space takes a pick's mark off
            await pilot.pause()
            assert table.preselected == {ids[2]} and table.get_row(str(ids[1]))[0].plain == ""
            await pilot.press("j", "space")                  # and marks a plain row by hand
            await pilot.pause()
            hand = table.get_row(str(plain))[0]
            assert table.selected == {plain} and hand.plain == "●" and hand.style == ""
            assert footer.note == "1 selected · 1 hunt pick"
            await pilot.press("c")                           # both kinds, in table order
            await _settle(app, pilot)
            assert COPIED[-1] == f"/jh-tailor {ids[2]}\n/jh-tailor {plain}"
            await pilot.press("r")                           # a reload keeps what was taken off
            await _settle(app, pilot)
            assert table.preselected == {ids[2]} and table.selected == {plain}

            await pilot.press("escape", "g", "c")            # esc clears both: c is the row again
            await _settle(app, pilot)
            assert footer.note == "" and COPIED[-1] == f"/jh-tailor {ids[1]}"
            await pilot.press("C")                           # the hunt's picks, back
            await pilot.pause()
            assert table.preselected == set(ids[1:]) and footer.note == "2 hunt picks"
    _run(scenario())


def test_copy_falls_back_to_the_terminal_clipboard_when_pbcopy_fails(monkeypatch):
    def no_pbcopy(text):
        raise FileNotFoundError("pbcopy")
    monkeypatch.setattr(commands, "pbcopy", no_pbcopy)
    got: list[str] = []
    commands.copy("/jh-tailor 7", got.append)
    assert got == ["/jh-tailor 7"]
    assert commands.tailor_commands([3, 1]) == "/jh-tailor 3\n/jh-tailor 1"


def _app_folder(tmp, bucket: str, name: str, files: tuple[str, ...] = (), age: int = 0):
    import os
    path = tmp / "applications" / bucket / name
    path.mkdir(parents=True)
    for f in files:
        (path / f).write_text("x", encoding="utf-8")
    os.utime(path, (1_800_000_000 - age, 1_800_000_000 - age))
    return path


def test_apps_lists_pending_first_and_opens_posting_folder_and_pdf(tmp_db, monkeypatch):
    from src.tui.screens.apps import AppsScreen
    from src.tui.widgets.apps_table import AppsTable

    sent = _add(status="applied", company="Sent [bold]Co", title="Backend", url="https://sent.example/j")
    wait = _add(company="Wait Co", url="ftp://nope")
    _app_folder(tmp_db, "applied", f"sent-co-{sent}", ("AlexExampleResume.pdf", "CoverLetter.pdf"))
    pending = _app_folder(tmp_db, "pending", f"wait-co-{wait}")
    (pending / "build.json").write_text('{"ok": false, "failures": ["x"]}', encoding="utf-8")
    toasts: list[str] = []

    async def scenario():
        app = JobhuntApp()
        monkeypatch.setattr(app, "notify", lambda line, **kw: toasts.append(line))
        async with app.run_test(size=(160, 30)) as pilot:
            await pilot.press(_key("apps"))
            await _settle(app, pilot)
            assert isinstance(app.screen, AppsScreen)
            table = app.screen.query_one(AppsTable)
            assert app.focused is table
            assert [a.job_id for a in table.apps] == [wait, sent]
            bucket, company, _title, status, files, build, drift = (
                c.plain for c in table.get_row(f"pending/wait-co-{wait}"))
            assert (bucket, company, status, build, drift) == ("pending", "Wait Co", "shortlisted", "fail 1", "")
            assert files == "······ ··· ······ ·······"
            row = [c.plain for c in table.get_row(f"applied/sent-co-{sent}")]
            assert row[1] == "Sent [bold]Co" and row[4] == "······ pdf letter ·······"   # never markup

            await pilot.press("p")                           # pending row: nothing to open yet
            assert OPENED == [] and "no resume PDF" in toasts[-1]
            await pilot.press("o")                           # a bad URL still opens the folder
            assert OPENED == [str(pending)] and "no posting URL" in toasts[-1]
            await pilot.press("j", "o")
            assert OPENED[1:] == ["https://sent.example/j", str(tmp_db / "applications" / "applied" / f"sent-co-{sent}")]
            await pilot.press("p")
            assert OPENED[-1].endswith("AlexExampleResume.pdf")
    _run(scenario())


def test_apps_status_change_moves_the_folder_and_keeps_the_cursor_on_it(tmp_db):
    from src.tui.widgets.apps_table import AppsTable
    from src.tui.widgets.modals import Confirm

    first = _add(company="First Co")
    second = _add(company="Second Co")
    _app_folder(tmp_db, "pending", f"first-co-{first}")
    _app_folder(tmp_db, "pending", f"second-co-{second}", age=100)
    _app_folder(tmp_db, "pending", "no-suffix", age=200)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 30)) as pilot:
            await pilot.press(_key("apps"))
            await _settle(app, pilot)
            table = app.screen.query_one(AppsTable)
            await pilot.press("s", "a", "p", "p", "enter")   # shortlisted -> applied: no question
            await _settle(app, pilot)
            assert (tmp_db / "applications" / "applied" / f"first-co-{first}").is_dir()
            assert [(a.bucket, a.job_id) for a in table.apps] == [
                ("pending", second), ("pending", None), ("applied", first)]
            assert table.current is not None and table.current.job_id == first
            await pilot.press("s", "r", "e", "j", "enter")   # leaving applied asks
            await pilot.pause()
            assert isinstance(app.screen, Confirm)
            await pilot.press("y")
            await _settle(app, pilot)
            assert (tmp_db / "applications" / "other" / f"first-co-{first}").is_dir()
            await pilot.press("g", "j", "s")                 # a folder with no row has no status to set
            await pilot.pause()
            assert not isinstance(app.screen, Confirm) and app.screen.query(AppsTable)
    _run(scenario())


def test_R_shows_the_plan_asks_once_and_applies_it(tmp_db, monkeypatch):
    from src.tui.widgets.apps_table import AppsTable
    from src.tui.widgets.modals import Confirm

    flip = _add(company="Flip Co")                           # folder already in applied/
    ahead = _add(company="Ahead Co", status="rejected")      # DB ahead of the folder
    _app_folder(tmp_db, "applied", f"flip-co-{flip}")
    _app_folder(tmp_db, "pending", f"ahead-co-{ahead}")
    _app_folder(tmp_db, "pending", "no-suffix")
    toasts: list[str] = []

    async def scenario():
        app = JobhuntApp()
        monkeypatch.setattr(app, "notify", lambda line, **kw: toasts.append(line))
        async with app.run_test(size=(160, 30)) as pilot:
            await pilot.press(_key("apps"))
            await _settle(app, pilot)
            table = app.screen.query_one(AppsTable)
            assert sum(bool(a.drift) for a in table.apps) == 3
            await pilot.press("R")
            await _settle(app, pilot)
            assert isinstance(app.screen, Confirm)
            assert app.screen.question == "reconcile: 1 DB update, 1 folder move, 1 by hand. apply?"
            await pilot.press("n")
            await _settle(app, pilot)
            assert (tmp_db / "applications" / "pending" / f"ahead-co-{ahead}").is_dir()
            await pilot.press("R")
            await _settle(app, pilot)
            await pilot.press("y")
            await _settle(app, pilot)
            assert (tmp_db / "applications" / "other" / f"ahead-co-{ahead}").is_dir()
            assert toasts[-1].startswith("reconciled: 1 DB update, 1 folder move, 1 by hand · ")
            assert "no-suffix" in toasts[-1]
            assert [a.drift for a in table.apps if a.job_id is not None] == ["", ""]
            conn = db.connect(db.DB_PATH)
            assert conn.execute("SELECT status FROM jobs WHERE id=?", (flip,)).fetchone()[0] == "applied"
            conn.close()

            await pilot.press("R")                           # only the hand-made case is left: no question
            await _settle(app, pilot)
            assert not isinstance(app.screen, Confirm)
            assert toasts[-1].startswith("reconcile: 0 DB updates, 0 folder moves, 1 by hand")
    _run(scenario())


def test_a_click_on_a_section_tab_is_its_number_key():
    from src.tui.widgets.modals import HelpOverlay
    from src.tui.widgets.section_bar import PAD, SectionBar, tabs

    spans = {mode: (start, end) for mode, _text, start, end in tabs()}
    assert [mode for mode, *_ in tabs()] == [mode for mode, _label in SECTIONS]      # drawn from the same table

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            bar = app.screen.query_one(SectionBar).render().plain
            start, end = spans["apps"]
            assert bar[start:end] == f" {_key('apps')} apps "
            await pilot.click(SectionBar, offset=(PAD + start + 1, 0))           # on the number
            await _settle(app, pilot)
            assert app.current_mode == "apps"
            await pilot.click(SectionBar, offset=(PAD + spans["run"][1] - 1, 0))  # the label's last cell
            await _settle(app, pilot)
            assert app.current_mode == "run"                                      # works on every section's bar
            await pilot.click(SectionBar, offset=(PAD + spans["settings"][1] + 3, 0))   # past the last tab
            await pilot.click(SectionBar, offset=(135, 0))                        # the date
            await _settle(app, pilot)
            assert app.current_mode == "run"

            await pilot.press("question_mark")                                    # a modal owns the screen
            await pilot.pause()
            assert isinstance(app.screen, HelpOverlay)
            await pilot.click(offset=(PAD + spans["board"][0] + 1, 0))
            await pilot.pause()
            assert app.current_mode == "run"
    _run(scenario())


def test_the_footer_carries_the_necessary_keys_only_and_fits_120_columns_with_a_note():
    """PRA-112. Everything else is under `?` (the help test above walks every binding)."""
    from textual.widgets import Footer

    from src.tui.widgets.footer import SectionFooter
    want = {
        "board": [("space", "select"), ("/", "search"), ("s", "status"), ("c", "copy"), ("?", "help")],
        "followups": [("space", "select"), ("/", "search"), ("s", "status"), ("c", "copy"), ("?", "help")],
        "apps": [("o", "open"), ("s", "status"), ("R", "reconcile"), ("?", "help")],
        "stats": [("again", "r")[::-1], ("?", "help")],
        "run": [("enter", "run"), ("^c", "stop"), ("R", "resume"), ("?", "help")],
        "settings": [("tab", "next"), ("e", "edit"), ("?", "help")],
    }
    ids = [_add(company=f"Co{n}") for n in range(3)]

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(120, 30)) as pilot:
            await _settle(app, pilot)
            await pilot.press("v")                                   # a selection note on every section
            assert app.selection.selected == set(ids)
            for mode, _label in SECTIONS:
                await pilot.press(_key(mode))
                await _settle(app, pilot)
                footer = app.screen.query_one(Footer)
                assert app.screen.query_one(SectionFooter).note == "3 selected"
                keys = list(footer.query("FooterKey"))
                shown = [(k.key_display, k.description) for k in keys]
                assert sorted(shown) == sorted(want[mode]), mode
                assert all(len(k.description.split()) <= 2 for k in keys)
                for k in keys:                                        # nothing cut, nothing wrapped
                    assert k.region.right <= footer.region.right and k.region.height == 1, (mode, k.key)
    _run(scenario())


def test_there_is_no_command_palette():
    from textual.widgets import Footer

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            jobs, theme = app.screen, app.theme
            await pilot.press("ctrl+p")
            await pilot.pause()
            assert app.screen is jobs and len(app.screen_stack) == 1            # no screen pushed
            for mode, _label in SECTIONS:
                await pilot.press(_key(mode))
                await _settle(app, pilot)
                keys = [(k.key, k.description) for k in app.screen.query_one(Footer).query("FooterKey")]
                assert not any("palette" in d or key == "ctrl+p" for key, d in keys), mode
            assert app.theme == theme                                           # only the settings modal changes it
    _run(scenario())


def test_scrollbars_are_one_cell_in_the_theme_colours_and_the_title_column_takes_the_slack():
    from textual.color import Color

    from src.tui.widgets.detail import DetailPane
    from src.tui.widgets.jobs_table import TITLE_MIN, JobsTable
    ids = [_add(company=f"Co{n}", title="Senior Staff Principal Forward Deployed Engineer, Platform " + "x" * 40,
                description="line\n" * 200) for n in range(60)]

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 30)) as pilot:
            await _settle(app, pilot)
            table, pane = app.screen.query_one(JobsTable), app.screen.query_one("#detail", DetailPane)
            for widget in (table, pane, app.screen.query_one(StatusList)):
                assert widget.styles.scrollbar_size_vertical == 1 and widget.styles.scrollbar_size_horizontal == 1
            assert table.show_vertical_scrollbar and not table.show_horizontal_scrollbar    # 60 rows, columns that fit
            assert table.virtual_size.width <= table.size.width
            wide = table.widths["title"]
            assert len(table.get_row(str(ids[0]))[3].plain) == wide

            for theme in ("kanagawa", "textual-light"):                   # the bar colours are the theme's
                app.theme = theme
                await pilot.pause()
                assert table.styles.scrollbar_color == Color.parse(app.get_css_variables()["scrollbar"]), theme

            await pilot.resize_terminal(157, 30)                          # narrower: the title gives way, not a bar
            await _settle(app, pilot)
            assert TITLE_MIN <= table.widths["title"] < wide and not table.show_horizontal_scrollbar
            assert len(table.get_row(str(ids[0]))[3].plain) == table.widths["title"]
            await pilot.press("j", "G")                                   # keys scroll as before
            await pilot.pause()
            assert table.current_id == ids[0] and table.scroll_y > 0
    _run(scenario())


def test_the_legend_under_the_status_list_says_what_the_marks_mean_per_section():
    from src.tui import settings
    from src.tui.widgets import jobs_table
    from src.tui.widgets.legend import SAMPLE_DATE, Legend, entries
    _add(company="Acme")

    def lines(legend) -> list[str]:
        return legend.text().plain.splitlines()

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 34)) as pilot:
            await _settle(app, pilot)
            legend, sl = app.screen.query_one(Legend), app.screen.query_one(StatusList)
            assert lines(legend) == ["● marked by hand", "● hunt pick", f"{SAMPLE_DATE} overdue",
                                     "(dream) dream list", "all discovered rows", "· no value"]
            assert all(len(ln) <= 19 for ln in lines(legend))                   # fits the 22-cell pane
            assert legend.region.y >= sl.region.bottom and legend.region.bottom == sl.parent.region.bottom
            assert sl.region.height == len(HOT) + 2

            spans = {legend.text().plain[s.start:s.end]: str(s.style) for s in legend.text().spans}
            assert spans[SAMPLE_DATE] == "red"
            app.apply_settings(settings.Settings(overdue_style="magenta"))      # as the settings modal does
            app.screen.apply_settings()
            await pilot.pause()
            spans = {legend.text().plain[s.start:s.end]: str(s.style) for s in legend.text().spans}
            assert spans[SAMPLE_DATE] == "magenta" and SAMPLE_DATE in str(legend.render())

            await pilot.press(_key("followups"))                                 # no picks, no `all` there
            await _settle(app, pilot)
            assert lines(app.screen.query_one(Legend)) == [
                "● marked by hand", f"{SAMPLE_DATE} overdue", "(dream) dream list", "· no value"]

        # the samples are the table's own constants
        first = entries("board")
        assert first[0][0].plain == jobs_table.MARK and str(first[1][0].style) == jobs_table.PICK_STYLE
        assert first[3][0].plain == jobs_table.DREAM_TAG.strip() and first[5][0].plain == jobs_table.NONE

        short = JobhuntApp()
        async with short.run_test(size=(140, 14)) as pilot:                      # a short terminal
            await _settle(short, pilot)
            sl = short.screen.query_one(StatusList)
            assert sl.region.height == len(HOT) + 2                              # the status list keeps every line
            assert short.screen.query_one(Legend).region.height < 6              # the legend gave way
    _run(scenario())


def test_the_dream_list_entry_filters_the_board_and_a_x_edit_the_list():
    """The board's Dream tab (docs/spec-pre-release.md decision 9): the rows at a dream company,
    hot or discovered; `a` adds a company and `x` removes one, both only on that entry, every
    write through src.tui.data and the db accessors."""
    from src import dream
    from src.tui.data import dream_companies
    from src.tui.widgets.jobs_table import JobsTable
    from src.tui.widgets.modals import Confirm, Picker, Prompt

    robo = _add(company="Example Robotics", match_score=70)
    cold = _add(company="ExampleRobotics GmbH", status="discovered", match_score=50)
    acme = _add(company="Acme Corp", match_score=90)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            await _settle(app, pilot)
            jobs, table = app.screen, app.screen.query_one(JobsTable)
            await pilot.press("a")                                  # not on the dream entry: nothing opens
            await pilot.pause()
            assert app.screen is jobs and not jobs.check_action("dream_add", ())

            jobs.query_one(StatusList).focus()
            await pilot.press("end")
            await _settle(app, pilot)
            assert jobs.status_filter == "dream" and jobs.check_action("dream_remove", ())
            assert table.job_ids == [robo, cold]                    # hot and discovered, score order
            counts = {o.id: o.prompt.plain.split()[-1] for o in jobs.query_one(StatusList).options}
            assert counts["dream"] == "2"

            await pilot.press("a")
            await pilot.pause()
            assert isinstance(app.screen, Prompt)
            await pilot.press("enter")                              # a name is required
            await pilot.pause()
            assert isinstance(app.screen, Prompt) and "company name" in str(app.screen.query_one("#prompt-error").content)
            await pilot.press(*"Acme, acme corp", "enter")
            await _settle(app, pilot)
            await _settle(app, pilot)
            assert [d.name for d in dream_companies()] == ["Acme"]
            assert table.job_ids == [acme]                          # the table's list now: the seed is not in it

            await pilot.press("x")
            await _settle(app, pilot)
            assert isinstance(app.screen, Picker)
            await pilot.press("enter")
            await pilot.pause()
            assert isinstance(app.screen, Confirm)
            await pilot.press("y")
            await _settle(app, pilot)
            await _settle(app, pilot)
            assert dream_companies() == [] and table.job_ids == []
            assert not dream.is_dream("Acme Corp")

            await pilot.press("x")                                  # an empty list: a toast, no picker
            await _settle(app, pilot)
            assert app.screen is jobs
    _run(scenario())
