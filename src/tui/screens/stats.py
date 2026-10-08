"""Section 4, stats (pre-release spec decision 15): "is my search working, and where is it
leaking?" on one screen, drawn in-process from one `data.stats()` snapshot. One column in the
scroll pane: the header, the tiles, the funnel, score vs reply, the sources. No drill-down, no
subprocess; `r` reads the snapshot again."""
from __future__ import annotations

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Static
from textual.worker import get_current_worker

from .. import data
from ..widgets.stats_view import render
from .base import SectionScreen


class StatsScreen(SectionScreen):
    DEFAULT_CSS = """
    StatsScreen #stats-scroll { height: 1fr; padding: 1 1 0 1; }
    """
    BINDINGS = [
        Binding("r", "refresh", "again", tooltip="read the numbers again"),
        Binding("j", "scroll(1)", "down", show=False),
        Binding("k", "scroll(-1)", "up", show=False),
        Binding("g", "scroll(0)", "top", show=False),
    ]

    def __init__(self) -> None:
        super().__init__("stats")

    def body(self) -> ComposeResult:
        with VerticalScroll(id="stats-scroll"):
            yield Static(Text(""), id="stats-text")

    def on_mount(self) -> None:
        self.query_one("#stats-scroll").focus()

    def on_screen_resume(self) -> None:
        """Every time the section comes up, the first included: a hunt may have moved the numbers
        meanwhile (ScreenResume comes twice on the first show; a load on its way is the load)."""
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
        self.load_stats(self.busy.start("stats", self.query_one("#stats-text")))

    @work(thread=True, group="stats", exclusive=True)
    def load_stats(self, token: int) -> None:
        worker = get_current_worker()
        try:
            shown = render(data.stats())
            if not worker.is_cancelled:
                self.app.call_from_thread(self.query_one("#stats-text", Static).update, shown)
        except Exception as e:  # noqa: BLE001, a load that fails says why and never leaves the indicator on
            self.load_failed("stats", e)
        finally:
            self.busy.done_from_thread(self.app, "stats", token)
