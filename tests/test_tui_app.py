"""Headless pilot tests for the TUI shell (Textual's run_test; no terminal needed)."""
import asyncio

import pytest

from src import db, reconcile, research
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
    return tmp_path


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
    await app.workers.wait_for_complete()
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
