"""Section 5, a placeholder (spec decision 4): the plain output of `python -m src.stats funnel`.
Real widgets over `stats.py` (funnel, calibration, latency, comp, source health) come later."""
from __future__ import annotations

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Label, Static

from .. import commands
from .base import SectionScreen

STATS_ARGV = ("src.stats", "funnel")
NOTE = ("python -m src.stats funnel, as printed. Real widgets (funnel, calibration, latency, comp, "
        "source health) come later; /jh-review reads the rest today.")


class StatsScreen(SectionScreen):
    DEFAULT_CSS = """
    StatsScreen #stats-note { height: auto; padding: 0 1; color: $text-muted; }
    StatsScreen #stats-scroll { height: 1fr; padding: 0 1; }
    """
    BINDINGS = [
        Binding("r", "refresh", "again", tooltip="run the command again"),
        Binding("j", "scroll(1)", "down", show=False),
        Binding("k", "scroll(-1)", "up", show=False),
        Binding("g", "scroll(0)", "top", show=False),
    ]

    def __init__(self) -> None:
        super().__init__("stats")

    def body(self) -> ComposeResult:
        yield Label(Text(NOTE), id="stats-note")
        with VerticalScroll(id="stats-scroll"):
            yield Static(Text("running python -m src.stats funnel ...", style="dim"), id="stats-text")

    def on_mount(self) -> None:
        self.query_one("#stats-scroll").focus()

    def on_screen_resume(self) -> None:
        """Every time the section comes up, the first included: one run of the command each
        (ScreenResume comes twice on the first show; a run already on its way is the run)."""
        if not self.busy.running("stats"):
            self.reload()

    def action_refresh(self) -> None:
        self.reload()

    def action_scroll(self, step: int) -> None:
        pane = self.query_one("#stats-scroll", VerticalScroll)
        if step == 0:
            pane.scroll_home(animate=False)
        else:
            pane.scroll_relative(y=step * 3, animate=False)

    def reload(self) -> None:
        self.load_stats(self.busy.start("stats", self.query_one("#stats-scroll")))

    @work(thread=True, group="stats", exclusive=True)
    def load_stats(self, token: int) -> None:
        try:
            rc, text = commands.capture(commands.module_argv(*STATS_ARGV), timeout=60)
            shown = text or "stats printed nothing"
            if rc != 0:
                shown = f"python -m src.stats funnel: exit {rc}\n\n{shown}"
            # the funnel names companies and sources from scraped postings: text, never markup
            self.app.call_from_thread(self.query_one("#stats-text", Static).update, Text(shown))
        except Exception as e:  # noqa: BLE001
            self.load_failed("stats", e)
        finally:
            self.busy.done_from_thread(self.app, "stats", token)
