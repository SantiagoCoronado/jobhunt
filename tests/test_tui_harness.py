"""The settings modal's harness tab: config/hunt.toml through src.hunt.config, and doctor."""
import pytest
from tui_fakes import _run, _settle

from src.hunt import config as hunt_config
from src.tui import commands, data
from src.tui.app import JobhuntApp
from src.tui.widgets.modals import OutputModal, Picker
from src.tui.widgets.settings_modal import SettingsModal

pytestmark = pytest.mark.usefixtures("tmp_db")

HUNT = """[harness]
default = "claude"                # the reference harness

[harness.mine]
command = "mine -p {prompt}"

[stages.triage]
model = "haiku"                   # cheap
[stages.research]
harness = "mine"
"""


@pytest.fixture
def hunt_toml():
    hunt_config.HUNT_TOML.parent.mkdir(parents=True, exist_ok=True)
    hunt_config.HUNT_TOML.write_text(HUNT, encoding="utf-8")
    return hunt_config.HUNT_TOML


def _labels(modal) -> list[str]:
    return [str(o.prompt) for o in modal.query_one("#settings-list").options]


async def _harness_tab(app, pilot) -> SettingsModal:
    await _settle(app, pilot)
    await pilot.press("comma", "tab", "tab")
    await pilot.pause()
    assert isinstance(app.screen, SettingsModal) and app.screen.tab == "harness"
    return app.screen


def test_harness_view_reads_the_default_the_templates_and_the_fanned_stages(hunt_toml):
    view = data.harness_view()
    assert view.default == "claude" and view.harnesses == ("claude", "mine") and not view.error
    assert [s.stage for s in view.stages] == ["triage", "match", "inbox", "research", "tailor"]
    by = {s.stage: s for s in view.stages}
    assert by["triage"].model == "haiku" and by["match"].model is None
    assert by["research"].harness == "mine" and by["tailor"].harness == "claude"


def test_a_hunt_toml_that_does_not_load_is_named_not_raised(hunt_toml):
    hunt_toml.write_text("[stages.nope]\n", encoding="utf-8")
    assert "unknown stage" in data.harness_view().error

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 40)) as pilot:
            modal = await _harness_tab(app, pilot)
            assert any("unknown stage" in ln for ln in _labels(modal))
            await pilot.press("enter")                        # nothing to apply, nothing breaks
            assert isinstance(app.screen, SettingsModal)
    _run(scenario())


def test_models_come_from_the_live_catalog_or_the_aliases(monkeypatch):
    from src.hunt import harness as harness_mod
    from src.hunt.harness import Model

    class Cataloged:
        name = "cat"
        def models(self):
            return [Model("big-1"), Model("small-1", "cheap")]

    class Aliased:
        name = "claude"
        def models(self):
            return None
        def aliases(self):
            return ["fable", "opus"]

    monkeypatch.setattr(harness_mod, "get", lambda name: {"cat": Cataloged(), "claude": Aliased()}[name])
    got = data.harness_models("cat")
    assert got.ids == ("big-1", "small-1") and not got.open_ended and "2 models" in got.note
    got = data.harness_models("claude")
    assert got.ids == ("fable", "opus") and got.open_ended and "full model id" in got.note


def test_enter_on_a_stage_picks_a_model_and_writes_one_line(hunt_toml, monkeypatch):
    asked = []

    def models(harness):
        asked.append(harness)
        return data.ModelChoices(harness, ("fable", "opus", "sonnet"), "aliases", True)
    monkeypatch.setattr(data, "harness_models", models)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 44)) as pilot:
            modal = await _harness_tab(app, pilot)
            lines = _labels(modal)
            assert "  claude ✓" in lines and "  mine" in lines
            assert "  triage    haiku" in lines and "  match     harness default" in lines
            assert "  research  harness default  on mine" in lines
            ol = modal.query_one("#settings-list")
            ol.highlighted = lines.index("  triage    haiku")
            await pilot.press("enter")
            await _settle(app, pilot)
            assert isinstance(app.screen, Picker) and asked == ["claude"]
            await pilot.press("s", "o", "n", "enter")
            await _settle(app, pilot)
            assert isinstance(app.screen, SettingsModal)
            assert "  triage    sonnet" in _labels(modal)
            assert ol.highlighted == lines.index("  triage    haiku")     # the cursor stayed put
    _run(scenario())
    text = hunt_toml.read_text(encoding="utf-8")
    assert 'model = "sonnet"                  # cheap' in text
    assert text.replace('model = "sonnet"                  # cheap', 'model = "haiku"                   # cheap') == HUNT
    assert hunt_config.load().stage("triage").model == "sonnet"


def test_a_typed_full_model_id_and_the_harness_default(hunt_toml, monkeypatch):
    monkeypatch.setattr(data, "harness_models",
                        lambda h: data.ModelChoices(h, ("fable", "opus"), "aliases", True))

    async def pick(app, pilot, modal, stage_line, keys):
        modal.query_one("#settings-list").highlighted = _labels(modal).index(stage_line)
        await pilot.press("enter")
        await _settle(app, pilot)
        await pilot.press(*keys, "enter")
        await _settle(app, pilot)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 44)) as pilot:
            modal = await _harness_tab(app, pilot)
            await pick(app, pilot, modal, "  match     harness default", list("claude-opus-5"))
            assert hunt_config.load().stage("match").model == "claude-opus-5"
            await pick(app, pilot, modal, "  triage    haiku", list("harness"))
            assert hunt_config.load().stage("triage").model is None
            assert "  triage    harness default" in _labels(modal)
    _run(scenario())


def test_enter_on_a_harness_sets_the_default(hunt_toml):
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 44)) as pilot:
            modal = await _harness_tab(app, pilot)
            modal.query_one("#settings-list").highlighted = _labels(modal).index("  mine")
            await pilot.press("enter")
            await pilot.pause()
            assert "  mine ✓" in _labels(modal) and "  claude" in _labels(modal)
    _run(scenario())
    assert hunt_config.load().harness == "mine"
    assert "# the reference harness" in hunt_toml.read_text(encoding="utf-8")


def test_doctor_runs_the_orchestrator_and_shows_its_table(hunt_toml, monkeypatch):
    ran = []

    def capture(argv, timeout=600):
        ran.append(list(argv))
        return 2, "doctor: claude\n  binary    ok    /usr/bin/claude\n  tailor    FAIL  [bold]nope[/bold]\nresult: 1 problem(s)"
    monkeypatch.setattr(commands, "capture", capture)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(140, 44)) as pilot:
            modal = await _harness_tab(app, pilot)
            modal.query_one("#settings-list").highlighted = len(_labels(modal)) - 1
            await pilot.press("enter")
            await _settle(app, pilot)
            assert isinstance(app.screen, OutputModal)
            shown = str(app.screen.query_one("#output-text").render())
            assert "[bold]nope[/bold]" in shown and "result: 1 problem(s)" in shown   # text, never markup
            await pilot.press("escape")
            await pilot.pause()
            assert isinstance(app.screen, SettingsModal)
    _run(scenario())
    assert ran == [commands.hunt_argv("doctor")] and ran[0][1:] == ["-m", "src.hunt", "doctor"]
