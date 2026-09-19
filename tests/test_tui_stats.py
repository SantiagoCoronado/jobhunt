"""Section 5: the stats placeholder."""
import sys

import pytest
from tui_fakes import CAPTURED, _run, _settle

from src.tui import commands
from src.tui.app import JobhuntApp
from src.tui.screens.stats import StatsScreen

pytestmark = pytest.mark.usefixtures("tmp_db")


def _text(screen) -> str:
    return str(screen.query_one("#stats-text").render())


def test_section_5_renders_the_funnel_output_with_the_placeholder_note(monkeypatch):
    funnel = "Applications: 121\n  screen     8\n[bold]Acme[/bold] applied= 9\n" + "\n".join(f"row {i}" for i in range(80))
    monkeypatch.setattr(commands, "capture", lambda argv, timeout=600: (CAPTURED.append(list(argv)), (0, funnel))[1])

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(120, 30)) as pilot:
            await pilot.press("5")
            await _settle(app, pilot)
            screen = app.screen
            assert isinstance(screen, StatsScreen)
            assert CAPTURED == [[sys.executable, "-m", "src.stats", "funnel"]]
            shown = _text(screen)
            assert "Applications: 121" in shown and "[bold]Acme[/bold]" in shown and "row 79" in shown
            assert "come later" in str(screen.query_one("#stats-note").render())
            pane = screen.query_one("#stats-scroll")
            assert pane.max_scroll_y > 0                       # longer than the screen: it scrolls
            await pilot.press("j", "j")
            await pilot.pause()
            assert pane.scroll_y > 0
            await pilot.press("g")
            await pilot.pause()
            assert pane.scroll_y == 0
            await pilot.press("r")
            await _settle(app, pilot)
            assert len(CAPTURED) == 2
    _run(scenario())


def test_a_failing_stats_command_shows_its_exit_code_and_what_it_printed(monkeypatch):
    monkeypatch.setattr(commands, "capture", lambda argv, timeout=600: (1, "sqlite3.OperationalError: no such table"))

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(120, 30)) as pilot:
            await pilot.press("5")
            await _settle(app, pilot)
            assert "exit 1" in _text(app.screen) and "no such table" in _text(app.screen)
    _run(scenario())
