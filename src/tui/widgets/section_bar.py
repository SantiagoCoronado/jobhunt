"""The top bar: `1 board  2 shortlist ...` with the active section highlighted, date on the right."""
from __future__ import annotations

from rich.text import Text
from textual.widgets import Static


class SectionBar(Static):
    DEFAULT_CSS = """
    SectionBar { height: 1; background: $surface; color: $foreground; padding: 0 1; }
    """

    def __init__(self, active: str) -> None:
        super().__init__()
        self.active = active

    def render(self) -> Text:
        from ..app import SECTIONS  # local import: app imports the screens that import this bar

        t = Text()
        for i, (mode, label) in enumerate(SECTIONS, start=1):
            style = "reverse bold" if mode == self.active else ""
            t.append(f" {i} {label} ", style=style)
            t.append(" ")
        right = f"{self.app.title} · {self.app.today.isoformat()}"  # type: ignore[attr-defined]
        width = self.size.width or 100
        pad = max(1, width - 2 - len(t.plain) - len(right))
        t.append(" " * pad)
        t.append(right, style="dim")
        return t
