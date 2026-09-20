"""Pilot tests for section 6. The stages here are tiny Python scripts: the real spawn, stream
and stop path runs, and no agent CLI or hunt is ever started."""
import asyncio
import sys

import pytest
from tui_fakes import COPIED, _key, OPENED, _run, _settle

from src import db
from src.hunt import ledger
from src.tui import commands, data
from src.tui.app import JobhuntApp
from src.tui.screens.run import RunScreen
from src.tui.widgets.modals import Confirm

pytestmark = pytest.mark.usefixtures("tmp_db")


def _stage(name: str, code: str, kind: str = "python", slash: str = "") -> data.RunStage:
    return data.RunStage(name, kind, (sys.executable, "-c", code), f"{name} note", slash)


SLEEPER = "import time; print('up', flush=True); time.sleep(60)"


@pytest.fixture
def stages(monkeypatch):
    found = [
        _stage("hunt", "print('hunting')", "hunt", "/jh-hunt"),
        _stage("discover", "import sys; print('pulled 3'); print('warn', file=sys.stderr); sys.exit(0)"),
        _stage("match", "print('[bold]scored[/bold]'); raise SystemExit(2)", "fanned"),
        _stage("report", "print('report written')"),
        _stage("slow", SLEEPER),
    ]
    monkeypatch.setattr(data, "stages", lambda: found)
    return found


async def _open(app, pilot) -> RunScreen:
    await pilot.press(_key("run"))
    await _settle(app, pilot)
    assert isinstance(app.screen, RunScreen)
    return app.screen


async def _until(pilot, done, tries: int = 200) -> None:
    for _ in range(tries):
        if done():
            return
        await asyncio.sleep(0.05)
        await pilot.pause()
    raise AssertionError("the process did not get there in time")


def _pane(screen) -> str:
    return "\n".join(screen.query_one("#run-log").lines)


def _go(screen, list_id: str, option_id: str) -> None:
    ol = screen.query_one(f"#{list_id}")
    ol.focus()
    ol.highlighted = [o.id for o in ol.options].index(option_id)


def test_the_stage_list_is_data_stages_and_the_pane_opens_on_the_source_summary(stages):
    conn = db.connect(db.DB_PATH)
    conn.execute("INSERT INTO runs (ts, source, pulled, new, seen, ok, error) VALUES "
                 "('2026-09-19T10:00:00', 'lever', 0, 0, 0, 0, 'HTTP 503')")
    conn.commit()
    conn.close()

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            screen = await _open(app, pilot)
            ol = screen.query_one("#run-stages")
            assert [o.id for o in ol.options] == [s.name for s in stages] and ol.has_focus
            assert "discover  discover note" in str(ol.options[1].prompt)
            pane = _pane(screen)
            assert "last discover run per source" in pane and "lever" in pane and "HTTP 503" in pane
    _run(scenario())


def test_enter_runs_the_stage_and_streams_stdout_and_stderr(stages):
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            screen = await _open(app, pilot)
            await pilot.press("j", "enter")
            await _until(pilot, lambda: screen.proc is None and any("exited" in ln for ln in screen.lines))
            pane = _pane(screen)
            assert "pulled 3" in pane and "warn" in pane and "--- discover exited (0)" in pane
            assert pane.splitlines()[0].startswith("$ python -c")
            assert app.running == "" and screen.query_one("SectionFooter").note == ""
    _run(scenario())


def test_a_failing_stage_shows_its_exit_code_and_its_output_is_never_markup(stages):
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            screen = await _open(app, pilot)
            _go(screen, "run-stages", "match")
            await pilot.press("enter")
            await _until(pilot, lambda: screen.proc is None and len(screen.lines) > 1)
            assert "[bold]scored[/bold]" in _pane(screen) and "--- match exited (2)" in _pane(screen)
            assert OPENED == []
    _run(scenario())


def test_one_process_at_a_time_and_ctrl_c_stops_it(stages):
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            screen = await _open(app, pilot)
            _go(screen, "run-stages", "slow")
            await pilot.press("enter")
            await _until(pilot, lambda: "up" in screen.lines)
            proc = screen.proc
            assert proc is not None and app.running == "slow"
            assert screen.query_one("SectionFooter").note == "running slow"
            assert "▶" in str(screen.query_one("#run-stages").get_option("slow").prompt)
            _go(screen, "run-stages", "discover")
            await pilot.press("enter")                        # refused: slow is still going
            await pilot.pause()
            assert screen.proc is proc and "pulled 3" not in screen.lines
            await pilot.press("ctrl+c")
            await _until(pilot, lambda: screen.proc is None)
            assert proc.poll() is not None and any("slow stopped" in ln for ln in screen.lines)
            assert "▶" not in str(screen.query_one("#run-stages").get_option("slow").prompt)
            await pilot.press("ctrl+c")                       # nothing running: a toast, no error
    _run(scenario())


def test_q_asks_before_it_takes_a_running_stage_down(stages):
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            screen = await _open(app, pilot)
            _go(screen, "run-stages", "slow")
            await pilot.press("enter")
            await _until(pilot, lambda: "up" in screen.lines)
            proc = screen.proc
            await pilot.press("q")
            await pilot.pause()
            assert isinstance(app.screen, Confirm)
            await pilot.press("n")
            await pilot.pause()
            assert app.is_running and proc.poll() is None
            await pilot.press("q", "y")
            await pilot.pause()
        assert proc.wait(timeout=10) is not None              # the unmount stopped it
    _run(scenario())


def test_a_clean_report_opens_the_html(stages):
    (db.DB_PATH.parent / "report.html").write_text("<html>", encoding="utf-8")
    ledger.Ledger.create("20260919-1000", "claude", {}, ("report",), ledger.HUNT_DIR)
    _report_opens()


def test_the_first_report_ever_written_opens_too(stages):
    """No report.html and no run ledger when the screen loads: the stage itself writes the
    file, which is what a first `report` or `hunt` does (Cursor review of PR #28)."""
    path = db.DB_PATH.parent / "report.html"
    assert not path.exists()
    writes = f"import pathlib; pathlib.Path({str(path)!r}).write_text('<html>'); print('report written')"
    stages[3] = _stage("report", writes)
    _report_opens()


def test_a_failed_report_opens_nothing_and_o_says_there_is_no_report(stages):
    stages[3] = _stage("report", "raise SystemExit(2)")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            screen = await _open(app, pilot)
            _go(screen, "run-stages", "report")
            await pilot.press("enter")
            await _until(pilot, lambda: screen.proc is None and len(screen.lines) > 1)
            await pilot.press("o")
            await pilot.pause()
            assert OPENED == [] and any("no data/report.html" in n.message for n in app._notifications)
    _run(scenario())


def _report_opens():
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            screen = await _open(app, pilot)
            _go(screen, "run-stages", "report")
            await pilot.press("enter")
            await _until(pilot, lambda: OPENED != [])
            assert OPENED == [str(db.DB_PATH.parent / "report.html")]
    _run(scenario())


def test_c_copies_the_slash_command_or_the_shell_line(stages):
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            screen = await _open(app, pilot)
            await pilot.press("c", "j", "c")
            await pilot.pause()
            assert COPIED[0] == "/jh-hunt" and COPIED[1].startswith("python -c ")
            assert screen.proc is None
    _run(scenario())


def test_a_run_shows_its_tree_and_a_unit_the_tail_of_its_log(stages):
    led = ledger.Ledger.create("20260919-1000", "claude", {}, ("triage", "pick"), ledger.HUNT_DIR)
    ledger.Ledger.create("20260918-0900", "claude", {}, ("pick",), ledger.HUNT_DIR)
    led.move_stage("triage", "running")
    led.add_units("triage", [{"id": "chunk_001", "input": "a", "output": "b"}])
    led.move_unit("triage", "chunk_001", "running")
    log = led.run_dir / "logs" / "triage" / "chunk_001.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("reading chunk\nwrote scores\n", encoding="utf-8")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            screen = await _open(app, pilot)
            runs = screen.query_one("#run-runs")
            assert [o.id for o in runs.options] == ["20260919-1000", "20260918-0900"]
            await pilot.press("tab", "tab")                   # stages -> selection -> runs
            await _settle(app, pilot)
            assert runs.has_focus and "run 20260919-1000" in _pane(screen) and "triage    running" in _pane(screen)
            assert [o.id for o in screen.query_one("#run-units").options] == ["triage/chunk_001"]
            await pilot.press("tab")                          # runs -> units
            await _settle(app, pilot)
            assert _pane(screen).strip() == "reading chunk\nwrote scores"
            log.write_text("reading chunk\nwrote scores\nverified\n", encoding="utf-8")
            screen.poll()                                     # the 2 s tick
            await _settle(app, pilot)
            assert _pane(screen).strip().endswith("verified")
            _go(screen, "run-runs", "20260918-0900")
            await _settle(app, pilot)
            assert "run 20260918-0900" in _pane(screen) and screen.query_one("#run-units").option_count == 0
    _run(scenario())


def test_R_resumes_the_highlighted_run_through_the_orchestrator(stages, monkeypatch):
    ledger.Ledger.create("20260919-1000", "claude", {}, ("pick",), ledger.HUNT_DIR)
    spawned = []
    real = commands.spawn

    def spawn(argv):
        spawned.append(list(argv))
        return real([sys.executable, "-c", "print('resumed')"])
    monkeypatch.setattr(commands, "spawn", spawn)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            screen = await _open(app, pilot)
            await pilot.press("R")
            await _until(pilot, lambda: screen.proc is None and "resumed" in screen.lines)
            assert spawned == [commands.hunt_argv("run", "--resume", "20260919-1000")]
    _run(scenario())


# The selection in the runner (PRA-111). `tailor` here prints the argv it was given, so the test
# sees the ids the real spawn carried; nothing starts a hunt.

ECHO = "import sys; print('argv', *sys.argv[1:])"


@pytest.fixture
def selection_stages(monkeypatch):
    found = [
        _stage("hunt", "print('hunting')", "hunt", "/jh-hunt"),
        _stage("research", ECHO, "fanned"),
        _stage("tailor", ECHO, "fanned"),
        _stage("failing", "raise SystemExit(2)"),
    ]
    monkeypatch.setattr(data, "stages", lambda: found)
    monkeypatch.setattr(data, "ON_SELECTION", ("research", "tailor", "failing"))
    return found


def _lines(screen, list_id: str) -> list[str]:
    return [str(o.prompt) for o in screen.query_one(f"#{list_id}").options]


def test_marked_rows_show_in_the_runner_and_enter_runs_tailor_on_them(selection_stages):
    from tui_fakes import _add
    ids = [_add(company=f"Co{n}", title=f"Role {n}") for n in range(3)][::-1]      # unscored: no hunt picks

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            await _settle(app, pilot)
            await pilot.press("space", "space")                                     # the two top rows of the board
            screen = await _open(app, pilot)
            assert _lines(screen, "run-selection") == [f"● #{ids[0]} Co2, Role 2", f"● #{ids[1]} Co1, Role 1"]
            assert str(screen.query_one("#run-selection-title").render()) == "selection (2)"
            stage_lines = dict(zip([s.name for s in selection_stages], _lines(screen, "run-stages"), strict=True))
            assert "2 selected · tailor note" in stage_lines["tailor"] and "2 selected" in stage_lines["research"]
            assert stage_lines["hunt"].endswith("ignores selection")
            assert screen.query_one("SectionFooter").note == "2 selected"

            _go(screen, "run-stages", "tailor")
            await pilot.press("enter")
            await _until(pilot, lambda: screen.proc is None and any("exited" in ln for ln in screen.lines))
            assert f"argv --ids {ids[0]},{ids[1]}" in _pane(screen)
            await pilot.pause()
            assert app.selection.marked == set()                                   # spent: the run exited 0
            assert _lines(screen, "run-selection")[0].strip().startswith("nothing marked: space marks a row in sections 1 and 2")
            assert "0 selected" in _lines(screen, "run-stages")[2]
    _run(scenario())


def test_enter_on_tailor_with_nothing_marked_spawns_nothing(selection_stages, monkeypatch):
    spawned: list[list[str]] = []
    monkeypatch.setattr(commands, "spawn", lambda argv: spawned.append(list(argv)))

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            screen = await _open(app, pilot)
            for name in ("tailor", "research"):
                _go(screen, "run-stages", name)
                await pilot.press("enter")
                await pilot.pause()
            assert spawned == [] and screen.proc is None and app.running == ""
    _run(scenario())


def test_a_failed_run_keeps_the_selection_and_the_block_drops_and_jumps(selection_stages):
    from tui_fakes import _add

    from src.tui.screens.jobs import JobsScreen
    from src.tui.widgets.jobs_table import JobsTable
    ids = [_add(company=f"Co{n}") for n in range(3)][::-1]

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            await _settle(app, pilot)
            await pilot.press("v")
            screen = await _open(app, pilot)
            _go(screen, "run-stages", "failing")
            await pilot.press("enter")
            await _until(pilot, lambda: screen.proc is None and any("exited (2)" in ln for ln in screen.lines))
            await pilot.pause()
            assert app.selection.selected == set(ids)                              # not spent: exit 2

            _go(screen, "run-selection", str(ids[0]))
            await pilot.press("backspace")
            await pilot.pause()
            assert app.selection.selected == set(ids[1:]) and len(_lines(screen, "run-selection")) == 2
            assert screen.query_one("SectionFooter").note == "2 selected"
            _go(screen, "run-selection", str(ids[2]))
            await pilot.press("enter")                                              # jumps to the row in section 1
            await _settle(app, pilot)
            assert isinstance(app.screen, JobsScreen) and app.current_mode == "board"
            table = app.screen.query_one(JobsTable)
            assert table.current_id == ids[2] and table.get_row(str(ids[0]))[0].plain == ""
    _run(scenario())
