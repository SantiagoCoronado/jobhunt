"""The sign that a load is running. Every load is a worker already (the UI never blocks); what
was missing is something on screen that says so.

Two signs, both held back `SHOW_AFTER` seconds so a load that answers fast never flashes one:
a FIRST load puts Textual's animated indicator on the widgets it fills (`widget.loading`), a
RELOAD keeps the old rows on screen and spins a small mark instead (the footer note of a
section, the hint line of the settings modal), so a table never blanks under the cursor.

A load is a key and a token. The token is what makes `done` safe to call from a `finally`: an
exclusive worker that was superseded still runs to its end, and its `done` must not clear the
indicator the newer load now owns. Nothing can be left spinning: `done` always clears, and a
host that goes away stops its timers with it.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from textual.app import App
from textual.timer import Timer
from textual.widget import Widget

SHOW_AFTER = 0.2                  # seconds before any sign appears
FRAME_SECONDS = 0.12
FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


@dataclass
class _Load:
    token: int
    timer: Timer
    widgets: tuple[Widget, ...]
    shown: bool = False
    spinning: bool = False


@dataclass
class Busy:
    host: Widget                                  # a screen: owns the timers
    draw: Callable[[str], None]                   # called with the mark's frame, "" when nothing spins
    loads: dict[str, _Load] = field(default_factory=dict)
    seen: set[str] = field(default_factory=set)
    token: int = 0
    frame: int = 0
    ticker: Timer | None = None

    def start(self, key: str, *widgets: Widget) -> int:
        """UI thread. Until a load under `key` has come back, a load shows the indicator on
        `widgets`; every later one (or a load with no widget to cover) the spinning mark. "Come
        back", not "started": a first load that a second one supersedes is still the first thing
        the reader waits for. Returns the token for `done`."""
        self._clear(key)
        self.token += 1
        token = self.token
        first = key not in self.seen and bool(widgets)
        timer = self.host.set_timer(SHOW_AFTER, lambda: self._show(key, token, first))
        self.loads[key] = _Load(token, timer, widgets)
        return token

    def _show(self, key: str, token: int, first: bool) -> None:
        load = self.loads.get(key)
        if load is None or load.token != token:
            return
        if first:
            load.shown = True
            for w in load.widgets:
                w.loading = True
        else:
            load.spinning = True
            if self.ticker is None:
                self.ticker = self.host.set_interval(FRAME_SECONDS, self._tick)
            self._tick()

    def _tick(self) -> None:
        self.frame = (self.frame + 1) % len(FRAMES)
        self.draw(FRAMES[self.frame])

    def _clear(self, key: str) -> None:
        load = self.loads.pop(key, None)
        if load is None:
            return
        load.timer.stop()
        for w in load.widgets:
            if w.loading:
                w.loading = False
        if not any(other.spinning for other in self.loads.values()):
            if self.ticker is not None:
                self.ticker.stop()
                self.ticker = None
            if load.spinning:
                self.draw("")

    def done(self, key: str, token: int) -> None:
        """UI thread. A token that is no longer the key's latest belongs to a superseded load."""
        load = self.loads.get(key)
        if load is not None and load.token == token:
            self.seen.add(key)
            self._clear(key)

    def done_from_thread(self, app: App, key: str, token: int) -> None:
        """For a thread worker's `finally`. The app may be gone by then (a quit mid-load)."""
        try:
            app.call_from_thread(self.done, key, token)
        except RuntimeError:
            pass

    @property
    def active(self) -> bool:
        return bool(self.loads)

    def running(self, key: str) -> bool:
        return key in self.loads
