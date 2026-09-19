"""App shell: seven sections as Textual modes, a section bar, the footer, global keys."""
from __future__ import annotations

from datetime import date

from textual.app import App
from textual.binding import Binding
from textual.screen import Screen

from . import settings as settings_mod
from .presets import PRESETS
from .screens.apps import AppsScreen
from .screens.base import SectionScreen
from .screens.jobs import JobsScreen
from .screens.run import RunScreen
from .screens.stats import StatsScreen
from .widgets.detail import DetailPane
from .widgets.jobs_table import JobsTable
from .widgets.modals import Confirm, HelpGroup, HelpOverlay, NotesEditor, StatusPicker
from .widgets.settings_modal import SettingsModal
from .widgets.status_list import StatusList

# (mode, label). Order is the key order: `1` is the first entry.
SECTIONS: tuple[tuple[str, str], ...] = (
    ("board", "board"),
    ("shortlist", "shortlist"),
    ("followups", "follow-ups"),
    ("apps", "apps"),
    ("stats", "stats"),
    ("run", "run"),
    ("settings", "settings"),
)


def _screen(mode: str, label: str):
    def make() -> Screen:
        if mode in PRESETS:
            return JobsScreen(mode)
        if mode == "apps":
            return AppsScreen()
        if mode == "stats":
            return StatsScreen()
        if mode == "run":
            return RunScreen()
        return SectionScreen(mode, f"{label}: coming in a later story (docs/spec-tui.md)")
    return make


class JobhuntApp(App):
    TITLE = "jobhunt"
    MODES = {mode: _screen(mode, label) for mode, label in SECTIONS}
    # DEFAULT_MODE stays Textual's "_default" (a blank screen) and on_mount switches to
    # board. Naming board as DEFAULT_MODE crashed the real `run()` path: Textual runs
    # asyncio tasks eagerly there (not under run_test), so registering the first screen
    # composes it on the spot, and `_init_mode` registers a MODES screen BEFORE pushing
    # it on the mode's stack. The search Input's mount then asks for `app.screen` and
    # finds an empty stack ("No screens on stack"). Switching from "_default" keeps
    # that blank screen on top until board is fully on its own stack.
    BINDINGS = [
        *(Binding(str(i), f"section('{mode}')", label, show=False)
          for i, (mode, label) in enumerate(SECTIONS, start=1)),
        Binding("question_mark", "help", "help"),
        Binding("comma", "settings", "settings", key_display=","),
        Binding("escape", "home", "home: back to the table, search cleared, modal closed", show=False),
        Binding("q", "quit", "quit"),
    ]

    def __init__(self, today: date | None = None) -> None:
        super().__init__()
        self.today = today or date.today()
        self.settings = settings_mod.load()
        self.running = ""                      # the runner's live process, by name
        self.register_theme(settings_mod.KANAGAWA_THEME)
        self.theme = self.settings.theme

    def on_mount(self) -> None:
        self.switch_mode(self.settings.default_section)
        for line in self.settings.warnings:
            self.notify(f"config/tui.toml: {line}", severity="warning", markup=False, timeout=10)

    def apply_settings(self, new: settings_mod.Settings, save: bool = False) -> None:
        """The one place a setting changes. Screens read `app.settings` when they draw, and the
        section under the modal picks the change up in its `on_screen_resume`."""
        self.settings = new
        if new.theme != self.theme and new.theme in self.available_themes:
            self.theme = new.theme                      # live: every widget restyles on the spot
        if save:
            try:
                settings_mod.save(new)
            except OSError as e:
                self.notify(f"config/tui.toml not saved: {e}", severity="error", markup=False)

    def action_section(self, mode: str) -> None:
        if mode != self.current_mode:
            self.switch_mode(mode)

    async def action_quit(self) -> None:
        """A stray `q` must not take a forty-minute hunt down with it."""
        if not self.running:
            self.exit()
            return

        def answered(yes: bool | None) -> None:
            if yes:
                self.exit()

        self.push_screen(Confirm(f"{self.running} is still running: quit and stop it?"), answered)

    def action_home(self) -> None:
        """`esc` on a section with nothing to go home to. JobsScreen and every modal bind their
        own `escape`, which wins over this one."""

    @staticmethod
    def help_groups() -> list[HelpGroup]:
        owners = (
            ("everywhere", JobhuntApp), ("sections 1 to 3", JobsScreen), ("jobs table", JobsTable),
            ("status list", StatusList), ("detail pane", DetailPane), ("apps", AppsScreen), ("stats", StatsScreen), ("run", RunScreen),
            ("status picker", StatusPicker), ("notes editor", NotesEditor), ("settings", SettingsModal),
        )
        # Textual also accepts bare tuples in BINDINGS; this app only writes Binding objects.
        return [(title, [b for b in cls.BINDINGS if isinstance(b, Binding)]) for title, cls in owners]

    def action_settings(self) -> None:
        if not isinstance(self.screen, SettingsModal):
            self.push_screen(SettingsModal())

    def action_help(self) -> None:
        if not isinstance(self.screen, HelpOverlay):
            self.push_screen(HelpOverlay(self.help_groups()))
