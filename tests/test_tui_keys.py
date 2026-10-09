"""Pilot tests for the settings modal's keys tab (docs/spec-pre-release.md PR 5 story 6): the
catalog from .env.example, set or unset, edits through config.set_env, and never a value on
screen. conftest points .env at a temp file."""
import pytest
from textual.widgets import Input
from tui_fakes import _run, _settle

from src import config
from src.tui.app import JobhuntApp
from src.tui.widgets.modals import Prompt
from src.tui.widgets.settings_modal import SettingsModal

pytestmark = pytest.mark.usefixtures("tmp_db")
SECRET = "s3cret-value-123"


def _labels(modal: SettingsModal) -> list[str]:
    return [str(o.prompt) for o in modal.query_one("#settings-list").options]


def _line(modal: SettingsModal, name: str) -> str:
    return next(label for label in _labels(modal) if label.strip().startswith(name))


async def _keys_tab(app, pilot) -> SettingsModal:
    await _settle(app, pilot)
    await pilot.press("comma")
    await pilot.pause()
    modal = app.screen
    assert isinstance(modal, SettingsModal)
    modal.show_tab("keys")
    await pilot.pause()
    return modal


async def _to(modal: SettingsModal, pilot, name: str) -> None:
    ol = modal.query_one("#settings-list")
    ol.highlighted = next(i for i, ln in enumerate(modal.lines) if ln.key == f"key={name}")
    await pilot.pause()


@pytest.fixture(autouse=True)
def _no_real_env_keys(monkeypatch):
    for e in config.env_catalog():
        monkeypatch.delenv(e["name"], raising=False)


def test_the_tab_lists_the_catalog_set_or_unset_and_never_a_value():
    config.set_env("FINDWORK_TOKEN", SECRET)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            modal = await _keys_tab(app, pilot)
            labels = _labels(modal)
            names = [e["name"] for e in config.env_catalog()]
            assert all(any(lab.strip().startswith(n) for lab in labels) for n in names)
            assert "set" in _line(modal, "FINDWORK_TOKEN") and "unset" not in _line(modal, "FINDWORK_TOKEN")
            assert "unset" in _line(modal, "ADZUNA_APP_ID")
            assert "optional" in _line(modal, "THEMUSE_API_KEY")
            assert not any(SECRET in lab for lab in labels)
            assert SECRET not in str(modal.query_one("#settings-box").render())
            tabs = modal.query_one("#settings-tabs")
            assert modal.tab_bar().cell_len <= tabs.region.width          # six tabs still fit on one line
    _run(scenario())


def test_enter_sets_a_key_through_the_one_line_editor_typed_as_dots():
    async def scenario():
        app = JobhuntApp()
        notes: list[str] = []
        app.notify = lambda message, **kw: notes.append(str(message))  # type: ignore[method-assign]
        async with app.run_test(size=(140, 40)) as pilot:
            modal = await _keys_tab(app, pilot)
            await _to(modal, pilot, "ADZUNA_APP_ID")
            await pilot.press("enter")
            await pilot.pause()
            prompt = app.screen
            assert isinstance(prompt, Prompt)
            box = prompt.query_one(Input)
            assert box.password and box.value == ""                 # never prefilled, typed as dots
            assert "developer.adzuna.com" in box.placeholder
            for ch in SECRET:
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause()
            assert app.screen is modal
            assert config.env_value("ADZUNA_APP_ID") == SECRET
            assert "set" in _line(modal, "ADZUNA_APP_ID") and "unset" not in _line(modal, "ADZUNA_APP_ID")
            assert notes and notes[-1] == ".env: ADZUNA_APP_ID set"
            assert not any(SECRET in n for n in notes)
            assert not any(SECRET in lab for lab in _labels(modal))
    _run(scenario())
    text = config.ENV_PATH.read_text()
    assert text.startswith("# jobhunt secrets") and f"ADZUNA_APP_ID={SECRET}\n" in text   # comments kept


def test_an_empty_answer_changes_nothing_and_a_dash_clears_the_key():
    config.set_env("CAREERJET_AFFID", SECRET)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            modal = await _keys_tab(app, pilot)
            await _to(modal, pilot, "CAREERJET_AFFID")
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("enter")                              # empty: keep it
            await pilot.pause()
            assert config.env_value("CAREERJET_AFFID") == SECRET
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("escape")                             # esc: keep it
            await pilot.pause()
            assert app.screen is modal and config.env_value("CAREERJET_AFFID") == SECRET
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("minus", "enter")
            await pilot.pause()
            assert config.env_value("CAREERJET_AFFID") == ""
            assert "CAREERJET_AFFID=" in config.ENV_PATH.read_text()   # the line stays, empty
            assert "unset" in _line(modal, "CAREERJET_AFFID")
    _run(scenario())


def test_a_key_from_the_environment_says_so():
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            modal = await _keys_tab(app, pilot)
            assert "from the environment" in _line(modal, "THEMUSE_API_KEY")
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("THEMUSE_API_KEY", SECRET)
        _run(scenario())
