"""The settings modal (spec decision 13): `,` opens it, `tab` walks the tabs, `enter` applies the
highlighted line and saves, `esc` closes. One list per tab, every line a value to choose."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, OptionList, Static
from textual.widgets.option_list import Option

from .. import settings
from ..settings import Settings
from .modals import Prompt

TABS: tuple[tuple[str, str], ...] = (
    ("theme", "theme"), ("sections", "sections"), ("harness", "harness"),
    ("followups", "follow-ups"), ("editor", "editor"),
)
FOLLOWUP_DAYS: tuple[int, ...] = (3, 5, 7, 10, 14)
CHECK = " ✓"
CUSTOM = "custom"


@dataclass(frozen=True)
class Line:
    """One line of a tab. A heading has no `pick`; a choice carries what `enter` does with it."""
    label: Text
    key: str = ""                                    # option id, unique inside the tab
    pick: Callable[[], None] | None = None
    chosen: bool = False


def heading(text: str) -> Line:
    return Line(Text(text, style="dim"))


class SettingsModal(ModalScreen[None]):
    DEFAULT_CSS = """
    SettingsModal { align: center middle; }
    SettingsModal #settings-box { width: 64; height: auto; max-height: 90%; border: round $primary;
                                  background: $surface; padding: 0 1; }
    SettingsModal #settings-tabs { height: 1; margin-bottom: 1; }
    SettingsModal OptionList { height: auto; max-height: 22; border: none; background: $surface; }
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

    @property
    def current(self) -> Settings:
        return self.app.settings  # type: ignore[attr-defined]

    def compose(self) -> ComposeResult:
        with Vertical(id="settings-box"):
            yield Label(Text("settings", style="bold"))
            yield Static(id="settings-tabs")
            yield OptionList(id="settings-list")
            yield Label("↑↓ select   tab section          ↵ apply   esc close", id="settings-keys")

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
        return [heading("config/hunt.toml: the harness and one model per stage")]

    def followup_lines(self) -> list[Line]:
        days = sorted({*FOLLOWUP_DAYS, self.current.followup_days})
        styles = list(dict.fromkeys([*settings.OVERDUE_STYLES, self.current.overdue_style]))
        return [
            heading("days the follow-up prompt suggests (display only; notify.yaml schedules)"),
            *(self.choice(f"+{n}", "followup_days", n) for n in days),
            heading("overdue follow-ups"),
            *(self.choice(Text.assemble("  ", (s, s)), "overdue_style", s) for s in styles),
        ]

    def editor_lines(self) -> list[Line]:
        known = list(dict.fromkeys([*settings.EDITORS, self.current.editor]))
        return [
            heading("opens a config file (e in section 7)"),
            *(self.choice(cmd, "editor", cmd) for cmd in known),
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

    def ask_editor(self) -> None:
        def parse(text: str) -> str:
            settings.check_editor(text)
            return text.strip()

        def entered(command: str | None) -> None:
            if command:
                self.set("editor", command)

        self.app.push_screen(Prompt("editor command", "e.g. code -w, or nvim +1 {file}", parse,
                                    self.current.editor), entered)
