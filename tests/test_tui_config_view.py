"""Section 7: the read-only config view and open-in-editor."""
import pytest
from tui_fakes import _key, _run, _settle

from src import config
from src.hunt import config as hunt_config
from src.tui import commands, data, settings
from src.tui.app import JobhuntApp
from src.tui.screens.config_view import ConfigScreen

pytestmark = pytest.mark.usefixtures("tmp_db")


@pytest.fixture
def edits(monkeypatch):
    ran: list[list[str]] = []
    monkeypatch.setattr(commands, "run_editor", lambda argv: (ran.append(list(argv)), 0)[1])
    return ran


def _body(screen) -> str:
    from rich.console import Console
    import io
    console = Console(width=200, file=io.StringIO(), color_system=None)
    console.print(screen.shown)
    return console.file.getvalue()


def test_config_files_are_the_five_files_resolved_where_the_loaders_read_them():
    files = data.config_files()
    assert [f.name for f in files] == ["profile.yaml", "sources.yaml", "sources.local.yaml", "hunt.toml", "tui.toml"]
    by = {f.name: f for f in files}
    assert by["profile.yaml"].path == config.USER_FILES["profile"]          # the fixture candidate here
    assert by["hunt.toml"].path == hunt_config.HUNT_TOML and by["tui.toml"].path == settings.TUI_TOML
    assert "target_titles" in data.read_config(by["profile.yaml"])
    assert data.read_config(by["tui.toml"]) == ""                            # not written yet


def test_section_7_shows_each_file_read_only_and_tab_walks_them(edits):
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.press(_key("settings"))
            await _settle(app, pilot)
            screen = app.screen
            assert isinstance(screen, ConfigScreen) and screen.current.name == "profile.yaml"
            assert "target_titles" in _body(screen)
            assert "read-only" in str(screen.query_one("#config-path").render())
            seen = []
            for _ in range(5):
                await pilot.press("tab")
                seen.append(screen.current.name)
            assert seen == ["sources.yaml", "sources.local.yaml", "hunt.toml", "tui.toml", "profile.yaml"]
            await pilot.press("h")
            assert screen.current.name == "tui.toml" and "does not exist yet" in _body(screen)
            for key in "xsdn":                                # no editing keys: nothing is typed into a file
                await pilot.press(key)
            assert edits == [] and not settings.TUI_TOML.exists()
    _run(scenario())


def test_a_value_that_looks_like_markup_is_shown_as_typed(edits, monkeypatch, tmp_path):
    odd = tmp_path / "profile.yaml"
    odd.write_text("note: '[bold]not markup[/bold] [/nope]'\n", encoding="utf-8")
    monkeypatch.setitem(config.USER_FILES, "profile", odd)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.press(_key("settings"))
            await _settle(app, pilot)
            assert "[bold]not markup[/bold] [/nope]" in _body(app.screen)
    _run(scenario())


def test_e_opens_the_file_in_the_configured_editor_and_reads_it_again(edits, monkeypatch, tmp_path):
    settings.save(settings.Settings(editor="myedit --wait {file}"))
    target = tmp_path / "profile.yaml"
    target.write_text("before: 1\n", encoding="utf-8")
    monkeypatch.setitem(config.USER_FILES, "profile", target)

    def editor(argv):
        edits.append(list(argv))
        target.write_text("after: 2\n", encoding="utf-8")
        return 0
    monkeypatch.setattr(commands, "run_editor", editor)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.press(_key("settings"))
            await _settle(app, pilot)
            assert "before" in _body(app.screen)
            await pilot.press("e")
            await _settle(app, pilot)
            assert edits == [["myedit", "--wait", str(target)]]
            assert "after" in _body(app.screen) and "before" not in _body(app.screen)
    _run(scenario())


def test_editing_tui_toml_takes_effect_at_once_and_a_bad_value_is_toasted(monkeypatch):
    def editor(argv):
        settings.TUI_TOML.parent.mkdir(parents=True, exist_ok=True)
        settings.TUI_TOML.write_text('[theme]\nname = "nord"\n[sections]\ndefault = "nowhere"\n', encoding="utf-8")
        return 0
    monkeypatch.setattr(commands, "run_editor", editor)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.press(_key("settings"), "shift+tab")
            await _settle(app, pilot)
            assert app.screen.current.name == "tui.toml" and app.theme == "kanagawa"
            await pilot.press("e")
            await _settle(app, pilot)
            assert app.theme == "nord" and app.settings.default_section == "board"
            assert any("nowhere" in n.message for n in app._notifications)
    _run(scenario())


def test_an_editor_that_fails_is_a_toast_not_a_crash(monkeypatch):
    monkeypatch.setattr(commands, "run_editor", lambda argv: -1)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.press(_key("settings"), "e")
            await _settle(app, pilot)
            assert any("did not start" in n.message for n in app._notifications)
            assert isinstance(app.screen, ConfigScreen)
    _run(scenario())


def test_input_is_dropped_for_a_moment_after_an_editor_round_trip_and_q_quits_after_it():
    """PRA-116: a terminal's late reply to the editor's queries must not be read as `q`."""
    from src.tui import app as app_mod

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.press(_key("settings"))
            await _settle(app, pilot)
            app.deafen(60)                                   # as the round trip leaves it, only longer
            await pilot.press("q", "1")
            await pilot.pause()
            assert app.is_running and app.current_mode == "settings"
            app.deafen(0)
            await pilot.press("1")
            await pilot.pause()
            assert app.current_mode == "board"
        assert app_mod.DEAF_SECONDS <= 0.5                   # never long enough to eat a human key
    _run(scenario())
