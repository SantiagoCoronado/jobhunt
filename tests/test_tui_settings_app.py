"""Pilot tests for the settings modal and what a setting changes on screen."""
from datetime import date

import pytest
from tui_fakes import _add, _run, _settle

from src.tui import settings
from src.tui.app import JobhuntApp
from src.tui.widgets.detail import DetailPane
from src.tui.widgets.jobs_table import JobsTable
from src.tui.widgets.modals import Prompt
from src.tui.widgets.settings_modal import TABS, SettingsModal

pytestmark = pytest.mark.usefixtures("tmp_db")


def _labels(modal: SettingsModal) -> list[str]:
    return [str(o.prompt) for o in modal.query_one("#settings-list").options]


async def _open(app, pilot) -> SettingsModal:
    await _settle(app, pilot)
    await pilot.press("comma")
    await pilot.pause()
    assert isinstance(app.screen, SettingsModal)
    return app.screen


def test_comma_opens_tab_walks_the_five_tabs_and_esc_closes():
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            modal = await _open(app, pilot)
            assert [label for _k, label in TABS] == ["theme", "sections", "harness", "follow-ups", "editor"]
            seen = [modal.tab]
            for _ in TABS:
                await pilot.press("tab")
                seen.append(modal.tab)
            assert seen == ["theme", "sections", "harness", "followups", "editor", "theme"]
            await pilot.press("shift+tab")
            assert modal.tab == "editor"
            await pilot.press("comma")                       # a second `,` does not stack a second modal
            assert sum(isinstance(s, SettingsModal) for s in app.screen_stack) == 1
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, SettingsModal)
            assert not settings.TUI_TOML.exists()            # looking saves nothing
    _run(scenario())


def test_enter_applies_and_saves_and_the_check_moves():
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            modal = await _open(app, pilot)
            await pilot.press("tab")                          # sections
            lines = _labels(modal)
            assert lines[lines.index("  board ✓")] and "  followups" in lines
            await pilot.press("j", "j", "enter")              # board -> shortlist -> followups
            await pilot.pause()
            assert app.settings.default_section == "followups"
            assert settings.load().default_section == "followups"
            lines = _labels(modal)
            assert "  followups ✓" in lines and "  board" in lines
            assert isinstance(app.screen, SettingsModal)      # `enter` applies, only `esc` closes
    _run(scenario())


def test_the_saved_launch_section_is_where_the_next_launch_opens(tmp_db):
    settings.save(settings.Settings(default_section="shortlist"))

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            assert app.current_mode == "shortlist"
    _run(scenario())


def test_a_warning_from_the_file_is_toasted_on_launch(tmp_db):
    settings.TUI_TOML.parent.mkdir(parents=True)
    settings.TUI_TOML.write_text('[theme]\nname = "vaporwave"\n', encoding="utf-8")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            notes = [n.message for n in app._notifications]
            assert any("vaporwave" in m for m in notes)
            assert app.current_mode == "board"
    _run(scenario())


def test_detail_pane_off_hides_the_pane_and_enter_opens_the_overlay():
    _add(company="Acme")

    async def scenario():
        from src.tui.widgets.modals import DetailOverlay
        app = JobhuntApp()
        async with app.run_test(size=(160, 40)) as pilot:
            await _settle(app, pilot)
            assert app.screen.query_one("#detail", DetailPane).display
            modal = await _open(app, pilot)
            await pilot.press("tab")
            lines = _labels(modal)
            modal.query_one("#settings-list").highlighted = lines.index("  always an overlay (enter)")
            await pilot.press("enter", "escape")
            await _settle(app, pilot)
            assert app.settings.detail_pane is False
            assert not app.screen.query_one("#detail", DetailPane).display
            await pilot.press("enter")
            await _settle(app, pilot)
            assert isinstance(app.screen, DetailOverlay)
    _run(scenario())


def test_overdue_style_and_the_followup_hint_come_from_the_settings():
    _add(company="Late", status="applied", next_followup_at="2026-09-01")

    async def scenario():
        app = JobhuntApp(today=date(2026, 9, 19))
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.press("3")
            await _settle(app, pilot)
            table = app.screen.query_one(JobsTable)
            assert str(table.get_row_at(0)[-1].style) == "red"
            modal = await _open(app, pilot)
            for _ in range(3):
                await pilot.press("tab")
            lines = _labels(modal)
            ol = modal.query_one("#settings-list")
            ol.highlighted = lines.index("  magenta")
            await pilot.press("enter")
            ol.highlighted = _labels(modal).index("  +10")
            await pilot.press("enter", "escape")
            await _settle(app, pilot)
            assert str(app.screen.query_one(JobsTable).get_row_at(0)[-1].style) == "magenta"
            await pilot.press("f")
            await pilot.pause()
            assert "+10" in app.screen.query_one("#prompt-input").placeholder
    _run(scenario())


def test_a_custom_editor_command_is_checked_before_it_is_saved():
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            modal = await _open(app, pilot)
            await pilot.press("shift+tab")                    # editor
            assert "  $EDITOR ✓" in _labels(modal)
            modal.query_one("#settings-list").highlighted = _labels(modal).index("  another command...")
            await pilot.press("enter")
            await pilot.pause()
            assert isinstance(app.screen, Prompt)
            box = app.screen.query_one("#prompt-input")
            box.value = "vim {line}"
            await pilot.press("enter")
            await pilot.pause()
            assert isinstance(app.screen, Prompt) and app.settings.editor == "$EDITOR"
            box.value = "nvim +1 {file}"
            await pilot.press("enter")
            await pilot.pause()
            assert app.settings.editor == "nvim +1 {file}"
            assert settings.load().editor == "nvim +1 {file}"
            assert "  nvim +1 {file} ✓" in _labels(modal)
    _run(scenario())
