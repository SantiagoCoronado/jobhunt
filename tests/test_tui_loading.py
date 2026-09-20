"""The loading state (PRA-119): the animated indicator on a first load that takes a while, a
spinning mark in the footer on a reload, never a flash on a fast load, never left spinning."""
import asyncio
import threading

import pytest
from tui_fakes import _key, _run, _settle

from src.tui import data, loading
from src.tui.app import JobhuntApp
from src.tui.widgets.apps_table import AppsTable
from src.tui.widgets.footer import SectionFooter

pytestmark = pytest.mark.usefixtures("tmp_db")


@pytest.fixture(autouse=True)
def quick(monkeypatch):
    monkeypatch.setattr(loading, "SHOW_AFTER", 0.05)          # the rule is the same, the wait shorter


async def _wait(pilot, done, tries: int = 100) -> None:
    for _ in range(tries):
        if done():
            return
        await asyncio.sleep(0.02)
        await pilot.pause()
    raise AssertionError("never got there")


def test_a_slow_first_load_shows_the_indicator_until_the_rows_arrive(monkeypatch):
    gate, calls = threading.Event(), []

    def slow_apps():
        calls.append(1)
        gate.wait(10)
        return []
    monkeypatch.setattr(data, "apps", slow_apps)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            await pilot.press(_key("apps"))
            table = app.screen.query_one(AppsTable)
            await _wait(pilot, lambda: table.loading)
            assert calls == [1]                                # one load on the first show, not two
            gate.set()
            await _settle(app, pilot)
            assert not table.loading and not app.screen.busy.active
    try:
        _run(scenario())
    finally:
        gate.set()


def test_a_fast_load_never_shows_it_and_a_slow_reload_spins_the_footer_instead(monkeypatch):
    gate, seen, slow = threading.Event(), [], []

    def apps():
        if slow:
            gate.wait(10)
        return []
    monkeypatch.setattr(data, "apps", apps)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            await pilot.press(_key("apps"))
            table = app.screen.query_one(AppsTable)
            watch = table.watch(table, "loading", lambda value: seen.append(value), init=False)  # noqa: F841
            await _settle(app, pilot)
            await asyncio.sleep(0.15)
            await pilot.pause()
            assert seen == [] and not table.loading            # answered inside SHOW_AFTER: no flash

            slow.append(1)
            await pilot.press("r")                             # a reload: the rows stay, the footer spins
            footer = app.screen.query_one(SectionFooter)
            await _wait(pilot, lambda: footer.note != "")
            assert footer.note[0] in loading.FRAMES and not table.loading and seen == []
            gate.set()
            await _settle(app, pilot)
            assert footer.note == "" and not app.screen.busy.active
    try:
        _run(scenario())
    finally:
        gate.set()


def test_a_failing_load_clears_the_indicator_and_says_why(monkeypatch):
    """Held on a gate, not on a sleep: a sleep races the first look at `table.loading`, and on
    a slow runner the load had already failed and cleared it (the red check on PR #30)."""
    gate = threading.Event()

    def broken():
        gate.wait(10)
        raise OSError("applications/ is unreadable")
    monkeypatch.setattr(data, "apps", broken)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            await pilot.press(_key("apps"))
            table = app.screen.query_one(AppsTable)
            await _wait(pilot, lambda: table.loading)          # in flight: the worker is blocked
            assert not any("did not load" in str(n.message) for n in app._notifications)
            gate.set()                                         # now it raises
            await _settle(app, pilot)
            await _wait(pilot, lambda: not table.loading)
            assert not app.screen.busy.active
            assert any("applications did not load: applications/ is unreadable" in str(n.message)
                       for n in app._notifications)
    try:
        _run(scenario())
    finally:
        gate.set()


def test_a_superseded_load_cannot_clear_the_newer_loads_indicator():
    """The token: an exclusive worker that was replaced still reaches its `finally`."""
    drawn: list[str] = []

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 30)) as pilot:
            await _settle(app, pilot)
            busy = loading.Busy(app.screen, drawn.append)
            old = busy.start("rows")
            new = busy.start("rows")
            busy.done("rows", old)                             # the old worker's finally
            assert busy.active
            await _wait(pilot, lambda: bool(drawn))            # the newer load's mark still comes up
            busy.done("rows", new)
            assert not busy.active and drawn[-1] == "" and busy.ticker is None
    _run(scenario())


def test_the_model_picker_says_it_is_asking_while_the_catalog_loads(monkeypatch):
    from src.hunt import config as hunt_config
    from src.tui.widgets.modals import Picker
    from src.tui.widgets.settings_modal import KEYS_HINT, SettingsModal
    gate = threading.Event()

    def models(harness):
        gate.wait(10)
        return data.ModelChoices(harness, ("fable",), "aliases", True)
    monkeypatch.setattr(data, "harness_models", models)
    hunt_config.HUNT_TOML.parent.mkdir(parents=True, exist_ok=True)
    hunt_config.HUNT_TOML.write_text('[stages.triage]\nmodel = "haiku"\n', encoding="utf-8")

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 44)) as pilot:
            await _settle(app, pilot)
            await pilot.press("comma", "tab", "tab")
            await pilot.pause()
            modal = app.screen
            assert isinstance(modal, SettingsModal)
            ol = modal.query_one("#settings-list")
            ol.highlighted = [str(o.prompt) for o in ol.options].index("  triage    haiku")
            await pilot.press("enter")
            hint = modal.query_one("#settings-keys")
            await _wait(pilot, lambda: "asking claude for its models" in str(hint.render()))
            gate.set()
            await _settle(app, pilot)
            assert isinstance(app.screen, Picker)
            assert str(hint.render()) == KEYS_HINT and not modal.busy.active
    try:
        _run(scenario())
    finally:
        gate.set()
