"""Section 7: the config files, read-only, one tab each (spec decision 13). `e` opens the file
in the configured editor; `,` is where the TUI's own settings are changed. No forms over YAML:
`profile.yaml` is the single authority for scoring and is edited as the file it is."""
from __future__ import annotations

import subprocess
from pathlib import Path

from rich.syntax import Syntax
from rich.text import Text
from textual import work
from textual.app import ComposeResult, SuspendNotSupported
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Static

from .. import commands, data, settings
from .base import SectionScreen


class ConfigScreen(SectionScreen):
    POLL_SECONDS = 2.0   # how often the shown file's mtime is checked

    DEFAULT_CSS = """
    ConfigScreen #config-tabs { height: 1; padding: 0 1; }
    ConfigScreen #config-path { height: 1; padding: 0 1; color: $text-muted; }
    ConfigScreen #config-scroll { height: 1fr; padding: 0 1; }
    """
    BINDINGS = [
        Binding("tab", "tab(1)", "next", tooltip="next file"),
        Binding("shift+tab", "tab(-1)", "previous file", show=False),
        Binding("l", "tab(1)", "next file", show=False),
        Binding("h", "tab(-1)", "previous file", show=False),
        Binding("right", "tab(1)", "next file", show=False),
        Binding("left", "tab(-1)", "previous file", show=False),
        Binding("e", "edit", "edit", tooltip="edit in the configured editor"),
        Binding("r", "refresh", "read again", show=False),
        Binding("j", "scroll(1)", "down", show=False),
        Binding("k", "scroll(-1)", "up", show=False),
        Binding("g", "scroll(0)", "top", show=False),
    ]

    def __init__(self) -> None:
        super().__init__("settings")
        self.files: list[data.ConfigFile] = []
        self.index = 0
        self.shown: Text | Syntax = Text("")     # what the pane holds now
        self.seen: dict[Path, float] = {}        # each file's mtime when it was last drawn

    def body(self) -> ComposeResult:
        yield Static(id="config-tabs")
        yield Static(id="config-path")
        with VerticalScroll(id="config-scroll"):
            yield Static(id="config-text")

    def on_mount(self) -> None:
        self.query_one("#config-scroll").focus()
        self.set_interval(self.POLL_SECONDS, self.poll)

    @staticmethod
    def mtime(path: Path) -> float:
        try:
            return path.stat().st_mtime
        except OSError:
            return 0.0

    def poll(self) -> None:
        """The view follows the file: a window editor saves while the TUI is up, and nothing
        else would say so. One stat per tick, and only while this section is on top."""
        if self.app.screen is self and self.files:
            f = self.current
            if self.mtime(f.path) != self.seen.get(f.path, 0.0):
                self.after_edit(f)

    def on_screen_resume(self) -> None:
        """Back from the settings modal or another section: the file may have been written."""
        self.reload()

    def action_refresh(self) -> None:
        self.reload()

    def reload(self) -> None:
        self.files = data.config_files()
        self.index = min(self.index, len(self.files) - 1)
        self.draw()
        self.seen = {f.path: self.mtime(f.path) for f in self.files}

    @property
    def current(self) -> data.ConfigFile:
        return self.files[self.index]

    def action_tab(self, step: int) -> None:
        self.index = (self.index + step) % len(self.files)
        self.draw()
        self.query_one("#config-scroll", VerticalScroll).scroll_home(animate=False)

    def action_scroll(self, step: int) -> None:
        pane = self.query_one("#config-scroll", VerticalScroll)
        if step == 0:
            pane.scroll_home(animate=False)
        else:
            pane.scroll_relative(y=step * 3, animate=False)

    def draw(self) -> None:
        bar = Text()
        for i, f in enumerate(self.files):
            bar.append(f" {f.name} ", style="reverse bold" if i == self.index else "")
            bar.append("  ")
        self.query_one("#config-tabs", Static).update(bar)
        f = self.current
        self.query_one("#config-path", Static).update(
            Text(f"{f.path}  ·  {f.role}  ·  read-only, e edits  ·  , settings"))
        try:
            text = data.read_config(f)
        except ValueError as e:
            body: Text | Syntax = Text(str(e), style="red")
        else:
            # Syntax lexes the text, it never parses markup: a `[bold]` in a YAML value stays as typed
            body = Syntax(text, f.lexer, theme="ansi_dark", line_numbers=True, word_wrap=True,
                          background_color=self.app.current_theme.background or "default") if text else Text(
                f"{f.name} does not exist yet ({'python -m src.init makes it' if f.lexer == 'yaml' else 'defaults apply'}); e creates it",
                style="dim")
        self.shown = body
        self.query_one("#config-text", Static).update(body)

    def action_edit(self) -> None:
        f = self.current
        try:
            argv = settings.editor_argv(self.app.settings.editor, f.path)  # type: ignore[attr-defined]
            name = Path(argv[0]).name                # as typed: the resolved file may be named otherwise
            window = commands.is_window_editor(argv)
            argv = commands.resolve_editor(argv)     # before the terminal is given away for nothing
        except ValueError as e:
            self.toast(str(e), "error")
            return
        if window or commands.is_window_editor(argv):   # its own window: the TUI stays up beside it
            try:
                proc = commands.launch_editor(argv)
            except OSError as e:
                self.toast(f"{name} did not start: {e}", "error")
                return
            self.toast(f"{f.name} is open in {name}; this view follows the file as you save")
            self.wait_for_editor(proc, f, name)
            return
        try:
            with self.app.suspend():                 # a terminal editor needs the terminal back
                rc = commands.run_editor(argv)
                commands.flush_terminal_input()      # its late terminal replies are not keys
            self.app.deafen()  # type: ignore[attr-defined]   # nor what still trickles in after the flush
        except SuspendNotSupported:                  # headless, or a terminal that cannot: a GUI editor still works
            rc = commands.run_editor(argv)
        if rc != 0:
            self.toast(f"{argv[0]} exited {rc}" if rc > 0 else f"{argv[0]} did not start", "warning")
        self.after_edit(f)

    @work(thread=True, group="editor")
    def wait_for_editor(self, proc: subprocess.Popen[bytes], f: data.ConfigFile, name: str) -> None:
        """Reaps the detached editor and takes its last save. With `-w` that is when the tab
        closes; without it the launcher exits at once and the poll does the following."""
        rc = proc.wait()
        try:
            if rc != 0:
                self.app.call_from_thread(self.toast, f"{name} exited {rc}", "warning")
            self.app.call_from_thread(self.after_edit, f)
        except RuntimeError:                         # the app closed meanwhile; the editor lives on
            pass

    def after_edit(self, f: data.ConfigFile) -> None:
        if f.path == settings.TUI_TOML:              # the TUI's own file: take the edit now
            self.app.apply_settings(settings.load())  # type: ignore[attr-defined]
            for line in self.app.settings.warnings:  # type: ignore[attr-defined]
                self.toast(f"config/tui.toml: {line}", "warning")
        self.reload()
