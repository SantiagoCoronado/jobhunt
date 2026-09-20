"""The settings modal (spec decision 13): `,` opens it, `tab` walks the tabs, `enter` applies the
highlighted line and saves, `esc` closes. One list per tab, every line a value to choose."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import partial
from typing import Any

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, OptionList, Static
from textual.widgets.option_list import Option

from .. import commands, data, settings
from ..loading import Busy
from ..sections import number
from ..settings import Settings
from .modals import OutputModal, Picker, Prompt

TABS: tuple[tuple[str, str], ...] = (
    ("theme", "theme"), ("sections", "sections"), ("harness", "harness"),
    ("followups", "follow-ups"), ("editor", "editor"),
)
FOLLOWUP_DAYS: tuple[int, ...] = (3, 5, 7, 10, 14)
CHECK = " ✓"
KEYS_HINT = "↑↓ select   tab section          ↵ apply   esc close"
CUSTOM = "custom"


@dataclass(frozen=True)
class Line:
    """One line of a tab. A heading has no `pick`; a choice carries what `enter` does with it."""
    label: Text
    key: str = ""                                    # option id, unique inside the tab
    pick: Callable[[], object] | None = None
    chosen: bool = False


def heading(text: str) -> Line:
    return Line(Text(text, style="dim"))


class SettingsModal(ModalScreen[None]):
    DEFAULT_CSS = """
    SettingsModal { align: center middle; }
    /* One size for every tab: the box is as tall as the longest list needs (22 lines, plus the
       title, the tabs, the hint and the border) and a longer list scrolls inside it, so `tab`
       never moves an edge. On a short terminal the 90% cap wins and the list gives way. */
    SettingsModal #settings-box { width: 64; height: 29; max-height: 90%; border: round $primary;
                                  background: $surface; padding: 0 1; }
    SettingsModal #settings-tabs { height: 1; margin-bottom: 1; }
    SettingsModal OptionList, SettingsModal OptionList:focus { height: 1fr; border: none; background: $surface; }
    SettingsModal #settings-keys { color: $text-muted; margin-top: 1; }
    """
    BINDINGS = [
        Binding("escape", "dismiss", "close"),
        Binding("tab", "tab(1)", "next tab"),
        Binding("shift+tab", "tab(-1)", "previous tab", show=False),
        Binding("right", "tab(1)", "next tab", show=False),
        Binding("left", "tab(-1)", "previous tab", show=False),
        Binding("j", "move(1)", "down", show=False),
        Binding("k", "move(-1)", "up", show=False),
        Binding("enter", "apply", "apply and save", show=False),   # the list's own `enter` does it
    ]

    def __init__(self, tab: str = "theme") -> None:
        super().__init__()
        self.tab = tab
        self.lines: list[Line] = []
        self.busy_text = ""
        self.busy = Busy(self, self.draw_busy)

    @property
    def current(self) -> Settings:
        return self.app.settings  # type: ignore[attr-defined]

    def compose(self) -> ComposeResult:
        with Vertical(id="settings-box"):
            yield Label(Text("settings", style="bold"))
            yield Static(id="settings-tabs")
            yield OptionList(id="settings-list")
            yield Label(KEYS_HINT, id="settings-keys")

    def on_mount(self) -> None:
        self.query_one(OptionList).focus()
        self.show_tab(self.tab)

    # Tabs

    def tab_bar(self) -> Text:
        t = Text()
        for key, label in TABS:
            t.append(f" {label} ", style="reverse bold" if key == self.tab else "")
            t.append("  ")
        return t

    def action_tab(self, step: int) -> None:
        keys = [k for k, _label in TABS]
        self.show_tab(keys[(keys.index(self.tab) + step) % len(keys)])

    def show_tab(self, tab: str, keep: bool = False) -> None:
        """Fill the list for `tab`. The highlight lands on the chosen value, or stays on its
        line when `keep` (after an apply)."""
        self.tab = tab
        self.query_one("#settings-tabs", Static).update(self.tab_bar())
        ol = self.query_one(OptionList)
        was = ol.highlighted
        self.lines = self.build(tab)
        ol.clear_options()
        ol.add_options(
            Option(Text.assemble(ln.label, (CHECK, "bold green") if ln.chosen else ""),
                   id=ln.key or None, disabled=ln.pick is None)
            for ln in self.lines)
        picks = [i for i, ln in enumerate(self.lines) if ln.pick is not None]
        if not picks:
            return
        if keep and was in picks:
            ol.highlighted = was
        else:
            ol.highlighted = next((i for i in picks if self.lines[i].chosen), picks[0])

    def action_move(self, step: int) -> None:
        ol = self.query_one(OptionList)
        if step > 0:
            ol.action_cursor_down()
        else:
            ol.action_cursor_up()

    # What each tab lists

    def build(self, tab: str) -> list[Line]:
        return {"theme": self.theme_lines, "sections": self.section_lines, "harness": self.harness_lines,
                "followups": self.followup_lines, "editor": self.editor_lines}[tab]()

    def choice(self, label: str | Text, field: str, value: Any) -> Line:
        text = label if isinstance(label, Text) else Text(f"  {label}")
        return Line(text, f"{field}={value}", lambda: self.set(field, value),
                    chosen=getattr(self.current, field) == value)

    def theme_lines(self) -> list[Line]:
        return [self.choice(name, "theme", name) for name in settings.THEMES]

    def section_lines(self) -> list[Line]:
        return [
            heading("opens on"),
            *(self.choice(s, "default_section", s) for s in settings.SECTIONS),
            heading("detail pane"),
            self.choice("beside the table (overlay when the terminal is narrow)", "detail_pane", True),
            self.choice("always an overlay (enter)", "detail_pane", False),
        ]

    def harness_lines(self) -> list[Line]:
        """`config/hunt.toml`, not tui.toml: how a hunt runs is the orchestrator's file."""
        view = data.harness_view()
        if view.error:
            return [heading(f"config/hunt.toml does not load; fix it in the editor (section {number('settings')})"),
                    heading(view.error)]
        return [
            heading("harness (config/hunt.toml)"),
            *(Line(Text(f"  {name}"), f"harness={name}", partial(self.set_harness, name),
                   chosen=name == view.default) for name in view.harnesses),
            heading("model per stage (enter picks from the live catalog)"),
            *(Line(Text.assemble(f"  {sm.stage:<10}", (sm.model or "harness default", "" if sm.model else "dim"),
                                 (f"  on {sm.harness}" if sm.harness != view.default else "", "dim")),
                   f"model={sm.stage}", partial(self.pick_model, sm)) 
              for sm in view.stages),
            heading("parallel harness processes (enter takes a number; a rate-limit and cost guard)"),
            *(Line(Text.assemble(f"  {sm.stage:<10}", f"{sm.concurrency}"), f"parallel={sm.stage}",
                   partial(self.ask_parallel, sm.stage, sm.concurrency)) for sm in view.stages),
            Line(Text.assemble(f"  {'all stages':<10}", f"{view.global_concurrency}", ("  the cap over the numbers above", "dim")),
                 "parallel=", partial(self.ask_parallel, "", view.global_concurrency)),
            heading("check"),
            Line(Text("  run doctor (binary, catalog, models, read tool)"), "doctor", self.run_doctor),
        ]

    def followup_lines(self) -> list[Line]:
        days = sorted({*FOLLOWUP_DAYS, self.current.followup_days})
        styles = list(dict.fromkeys([*settings.OVERDUE_STYLES, self.current.overdue_style]))
        return [
            heading("days the follow-up prompt suggests (display only; notify.yaml schedules)"),
            *(self.choice(f"+{n}", "followup_days", n) for n in days),
            heading("overdue follow-ups"),
            *(self.choice(Text.assemble("  ", (s, s)), "overdue_style", s) for s in styles),
        ]

    @staticmethod
    def editor_label(cmd: str) -> Text:
        """An editor nothing can find says so here, before `e` is pressed on a file."""
        from pathlib import Path
        try:
            found = commands.find_program(settings.editor_argv(cmd, Path("file"))[0])
        except ValueError:
            found = None
        return Text.assemble(f"  {cmd}", ("" if found else "  not installed", "dim"))

    def editor_lines(self) -> list[Line]:
        known = list(dict.fromkeys([*settings.EDITORS, self.current.editor]))
        return [
            heading(f"opens a config file (e in section {number('settings')})"),
            *(self.choice(self.editor_label(cmd), "editor", cmd) for cmd in known),
            Line(Text("  another command..."), CUSTOM, self.ask_editor),
        ]

    # Apply

    def action_apply(self) -> None:
        self.apply_line(self.query_one(OptionList).highlighted)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self.apply_line(event.option_index)

    def apply_line(self, index: int | None) -> None:
        if index is not None and 0 <= index < len(self.lines):
            pick = self.lines[index].pick
            if pick is not None:
                pick()

    def set(self, field: str, value: Any) -> None:
        """Apply and save in one step (spec: `enter` applies and saves)."""
        self.app.apply_settings(replace(self.current, **{field: value}), save=True)  # type: ignore[attr-defined]
        self.show_tab(self.tab, keep=True)

    # Harness tab: every write goes through src.hunt.config, which validates before it lands.

    def hunt_write(self, op: Callable[[], str]) -> None:
        try:
            line = op()
        except (ValueError, OSError) as e:
            self.app.notify(str(e), severity="error", markup=False)
            return
        self.app.notify(line, markup=False)
        self.show_tab(self.tab, keep=True)

    def set_harness(self, name: str) -> None:
        self.hunt_write(lambda: data.set_harness(name))

    # The two slow actions say they are running on the hint line, until their modal opens: the
    # catalog takes a second or two (`claude --help`), doctor up to minutes.

    def draw_busy(self, frame: str) -> None:
        self.query_one("#settings-keys", Label).update(Text(f"{frame} {self.busy_text}" if frame else KEYS_HINT))

    def pick_model(self, sm: data.StageModel) -> None:
        self.busy_text = f"asking {sm.harness} for its models"
        self.read_models(sm, self.busy.start("models"))

    @work(thread=True, group="models", exclusive=True)
    def read_models(self, sm: data.StageModel, token: int) -> None:
        """The catalog is the harness CLI's answer, so it is asked off the UI thread."""
        try:
            choices = data.harness_models(sm.harness)
            self.app.call_from_thread(self.show_models, sm, choices)
        except Exception as e:  # noqa: BLE001, a failed ask says why and never leaves the mark spinning
            self.app.call_from_thread(self.app.notify, f"the {sm.harness} catalog did not load: {e}",
                                      severity="error", markup=False)
        finally:
            self.busy.done_from_thread(self.app, "models", token)

    def show_models(self, sm: data.StageModel, choices: data.ModelChoices) -> None:
        if self.app.screen is not self:                  # closed while the catalog loaded
            return
        ids = list(dict.fromkeys([*choices.ids, *([sm.model] if sm.model else [])]))
        options = [("", "harness default"), *((i, i) for i in ids)]

        def picked(model: str | None) -> None:
            if model is not None and model != (sm.model or ""):
                self.hunt_write(lambda: data.set_stage_model(sm.stage, model or None))

        self.app.push_screen(Picker(f"{sm.stage} model on {sm.harness}", options, sm.model or "",
                                    choices.note, choices.open_ended), picked)

    def ask_parallel(self, stage: str, now: int) -> None:
        """`concurrency` of one fanned stage, or `global_concurrency` when `stage` is empty. The
        prompt only asks for a whole number: the minimum is `src.hunt.config`'s to refuse."""
        def parse(text: str) -> str:
            try:
                return str(int(text.strip()))
            except ValueError:
                raise ValueError(f"a whole number, got {text.strip()!r}") from None

        def entered(text: str | None) -> None:
            if text is not None and int(text) != now:
                n = int(text)
                self.hunt_write(lambda: data.set_stage_concurrency(stage, n) if stage
                                else data.set_global_concurrency(n))

        what = f"{stage}: harness processes in parallel" if stage else "every stage together: harness processes in parallel"
        self.app.push_screen(Prompt(what, "a whole number, 1 or more", parse, str(now)), entered)

    def run_doctor(self) -> None:
        self.busy_text = "hunt doctor is running: a smoke prompt per model, up to a few minutes"
        self.doctor(self.busy.start("doctor"))

    @work(thread=True, group="doctor", exclusive=True)
    def doctor(self, token: int) -> None:
        try:
            _rc, text = commands.capture(commands.hunt_argv("doctor"))
            self.app.call_from_thread(self.app.push_screen, OutputModal("hunt doctor", text or "doctor printed nothing"))
        except Exception as e:  # noqa: BLE001
            self.app.call_from_thread(self.app.notify, f"hunt doctor did not run: {e}", severity="error", markup=False)
        finally:
            self.busy.done_from_thread(self.app, "doctor", token)

    def ask_editor(self) -> None:
        def parse(text: str) -> str:
            settings.check_editor(text)
            return text.strip()

        def entered(command: str | None) -> None:
            if command:
                self.set("editor", command)

        self.app.push_screen(Prompt("editor command", "e.g. code -w, or nvim +1 {file}", parse,
                                    self.current.editor), entered)
