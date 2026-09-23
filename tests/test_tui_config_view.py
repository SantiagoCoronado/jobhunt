"""Section 7: the read-only config view and open-in-editor."""
import pytest
from tui_fakes import _key, _run, _settle

from src import config
from src.hunt import config as hunt_config
from src.tui import commands, data, settings
from src.tui.app import JobhuntApp
from src.tui.screens.config_view import ConfigScreen

pytestmark = pytest.mark.usefixtures("tmp_db")
FIND_PROGRAM = commands.find_program          # the real one: the pilot fixture replaces it with a stub


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
            path_line = str(screen.query_one("#config-path").render())
            assert path_line.startswith("tests/fixtures/profile.yaml") and "e edits" in path_line  # relative under ROOT
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


def test_a_gui_editor_is_found_inside_its_app_bundle_when_its_cli_is_not_on_path(monkeypatch, tmp_path):
    """`code -w` and `cursor -w` did not launch: the apps were installed, their shell commands
    were not, and a second VS Code install is "Visual Studio Code 2.app"."""
    import sys
    cli = tmp_path / "Visual Studio Code 2.app" / "Contents" / "Resources" / "app" / "bin" / "code"
    cli.parent.mkdir(parents=True)
    cli.write_text("#!/bin/sh\n")
    cli.chmod(0o755)
    monkeypatch.setattr(commands, "find_program", FIND_PROGRAM)
    monkeypatch.setattr(commands, "APP_DIRS", (tmp_path,))
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    assert commands.resolve_editor(["code", "-w", "f.yaml"]) == [str(cli), "-w", "f.yaml"]
    with pytest.raises(ValueError, match="cursor is not on PATH and no app bundle carries it: install its shell command"):
        commands.resolve_editor(["cursor", "-w", "f.yaml"])
    with pytest.raises(ValueError, match="myedit is not on PATH.*pick another editor"):
        commands.resolve_editor(["myedit", "f.yaml"])
    assert commands.find_program(sys.executable) == sys.executable               # a path is taken as given
    monkeypatch.setenv("PATH", str(cli.parent))
    assert commands.find_program("code") == str(cli)                             # PATH wins when it has it


def test_an_editor_nothing_can_find_is_an_error_toast_and_the_terminal_is_never_given_away(edits, monkeypatch):
    settings.save(settings.Settings(editor="code -w"))
    monkeypatch.setattr(commands, "find_program", lambda name: None)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.press(_key("settings"), "e")
            await _settle(app, pilot)
            assert edits == [] and isinstance(app.screen, ConfigScreen)
            assert any("code is not on PATH" in n.message and n.severity == "error" for n in app._notifications)
            await pilot.press("comma", "shift+tab")                               # the editor tab says so too
            await pilot.pause()
            lines = [str(o.prompt) for o in app.screen.query_one("#settings-list").options]
            assert any(ln.startswith("  code -w") and "not installed" in ln for ln in lines)
    _run(scenario())


def test_a_window_editor_opens_beside_the_tui_which_never_gives_the_terminal_away(edits, monkeypatch):
    """Santiago, 2026-09-20: `code -w` left the TUI to launch. A window editor needs nothing from
    the terminal, so it is started detached and the TUI stays up; only a terminal editor suspends."""
    import subprocess
    import sys
    assert commands.is_window_editor(["/Applications/Cursor.app/Contents/Resources/app/bin/cursor", "-w", "f"])
    assert commands.is_window_editor(["code", "f"]) and not commands.is_window_editor(["nvim", "f"])
    assert not commands.is_window_editor(["/usr/bin/nano", "f"]) and not commands.is_window_editor([])
    # Zed's bundle file is called `cli`, not `zed`: the resolved path must still be a window editor
    assert commands.is_window_editor(["/Applications/Zed.app/Contents/MacOS/cli", "-w", "f"])
    assert commands.is_window_editor(["/Users/x/Applications/Zed Preview.app/Contents/MacOS/cli", "f"])
    assert not commands.is_window_editor(["/usr/local/bin/cli", "f"])          # any other `cli` is not

    settings.save(settings.Settings(editor="code -w"))
    launched: list[list[str]] = []

    def launch(argv):
        launched.append(list(argv))
        return subprocess.Popen([sys.executable, "-c", "pass"])              # exits at once, as a saved-and-closed tab
    monkeypatch.setattr(commands, "launch_editor", launch)

    async def scenario():
        app = JobhuntApp()
        suspended: list[int] = []
        monkeypatch.setattr(app, "suspend", lambda: suspended.append(1))
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.press(_key("settings"), "e")
            await _settle(app, pilot)
            assert [a[:2] for a in launched] == [["code", "-w"]] and launched[0][2].endswith("profile.yaml")
            assert edits == [] and suspended == []                           # never the foreground path
            assert isinstance(app.screen, ConfigScreen) and app.is_running
            assert any("is open in code" in n.message for n in app._notifications)
            await pilot.press("j", "tab")                                    # the TUI takes keys while it is open
            await pilot.pause()
            assert app.screen.current.name != "profile.yaml"
    _run(scenario())


def test_the_view_follows_the_file_as_it_is_saved_elsewhere():
    import os

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.press(_key("settings"), "shift+tab")
            await _settle(app, pilot)
            screen = app.screen
            assert screen.current.name == "tui.toml" and app.theme == "kanagawa"
            settings.TUI_TOML.parent.mkdir(parents=True, exist_ok=True)
            settings.TUI_TOML.write_text('[theme]\nname = "nord"\n', encoding="utf-8")   # a save in the editor's window
            os.utime(settings.TUI_TOML, (1, 1))                              # whatever the clock's grain
            screen.poll()
            await pilot.pause()
            assert app.theme == "nord" and 'name = "nord"' in screen.shown.code
            shown = screen.shown
            screen.poll()                                                    # nothing moved: nothing redrawn
            assert screen.shown is shown
    _run(scenario())


def test_zed_found_in_its_bundle_still_opens_beside_the_tui(edits, monkeypatch, tmp_path):
    """Cursor review of PR #30: `resolve_editor` turns `zed` into `.../Zed.app/Contents/MacOS/cli`,
    whose name is not a known command, so `zed -w` took the suspend path."""
    import subprocess
    import sys
    cli = tmp_path / "Zed.app" / "Contents" / "MacOS" / "cli"
    cli.parent.mkdir(parents=True)
    cli.write_text("#!/bin/sh\n")
    cli.chmod(0o755)
    monkeypatch.setattr(commands, "find_program", FIND_PROGRAM)
    monkeypatch.setattr(commands, "APP_DIRS", (tmp_path,))
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    settings.save(settings.Settings(editor="zed -w"))
    launched: list[list[str]] = []
    monkeypatch.setattr(commands, "launch_editor",
                        lambda argv: (launched.append(list(argv)), subprocess.Popen([sys.executable, "-c", "pass"]))[1])

    async def scenario():
        app = JobhuntApp()
        suspended: list[int] = []
        monkeypatch.setattr(app, "suspend", lambda: suspended.append(1))
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.press(_key("settings"), "e")
            await _settle(app, pilot)
            assert [a[:2] for a in launched] == [[str(cli), "-w"]]
            assert edits == [] and suspended == [] and isinstance(app.screen, ConfigScreen)
            assert any("is open in zed" in n.message for n in app._notifications)      # named as typed, not `cli`
    _run(scenario())
