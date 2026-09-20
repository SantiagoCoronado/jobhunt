"""The top bar: `1 board  2 follow-ups ...` with the active section highlighted, date on the right.
A click on a tab is its number key."""
from __future__ import annotations

from rich.text import Text
from textual import events
from textual.widgets import Static

from ..sections import SECTIONS

PAD = 1      # the bar's horizontal padding: a click's x counts from the widget's edge, the text does not


def tabs() -> list[tuple[str, str, int, int]]:
    """(mode, text, start, end) per tab, in cells from the start of the bar's text. The one
    table both the drawing and the hit areas come from, so they cannot drift."""
    out, at = [], 0
    for i, (mode, label) in enumerate(SECTIONS, start=1):
        text = f" {i} {label} "
        out.append((mode, text, at, at + len(text)))
        at += len(text) + 1                      # one blank cell between tabs, part of neither
    return out


class SectionBar(Static):
    DEFAULT_CSS = """
    SectionBar { height: 1; background: $surface; color: $foreground; padding: 0 1; }
    """

    def __init__(self, active: str) -> None:
        super().__init__()
        self.active = active

    def render(self) -> Text:
        t = Text()
        for mode, text, _start, _end in tabs():
            t.append(text, style="reverse bold" if mode == self.active else "")
            t.append(" ")
        right = f"{self.app.title} · {self.app.today.isoformat()}"  # type: ignore[attr-defined]
        width = self.size.width or 100
        pad = max(1, width - 2 - len(t.plain) - len(right))
        t.append(" " * pad)
        t.append(right, style="dim")
        return t

    @staticmethod
    def mode_at(x: int) -> str | None:
        """The section whose label (number included) covers cell `x` of the widget."""
        return next((mode for mode, _text, start, end in tabs() if start <= x - PAD < end), None)

    def on_click(self, event: events.Click) -> None:
        mode = self.mode_at(event.x)
        if mode is not None:
            event.stop()
            self.app.action_section(mode)  # type: ignore[attr-defined]
