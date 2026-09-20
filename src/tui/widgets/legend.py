"""The legend under the status list: what the mark and the colours at the start of a row mean.
Drawn from the constants the table draws with, so a change of mark or colour cannot leave it
behind. `?` lists keys; this lists marks."""
from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from ..presets import ALL, OVERDUE_STYLE, PICKS_LEAD, PRESETS
from .jobs_table import DREAM_TAG, MARK, NONE, PICK_STYLE

SAMPLE_DATE = "2026-01-01"


def entries(preset: str, overdue_style: str = OVERDUE_STYLE) -> list[tuple[Text, str]]:
    """(sample, meaning) per line, only what the section can show: no pick line where no pick is
    ever listed, no `all` line where the left pane has no `all`."""
    listed = PRESETS[preset].entries
    out = [(Text(MARK), "marked by hand")]
    if PICKS_LEAD in listed:
        out.append((Text(MARK, style=PICK_STYLE), "hunt pick"))
    out.append((Text(SAMPLE_DATE, style=overdue_style), "overdue"))
    out.append((Text(DREAM_TAG.strip()), "dream list"))
    if ALL in listed:
        out.append((Text(ALL, style="dim"), "discovered rows"))
    out.append((Text(NONE, style="dim"), "no value"))
    return out


class Legend(Static):
    """Bottom-aligned in whatever height the status list leaves: on a short terminal the legend
    loses lines from the top, the status list never loses one to it."""

    DEFAULT_CSS = """
    Legend { height: 1fr; padding: 0 1; content-align: left bottom; color: $text-muted; }
    """

    def __init__(self, preset: str, id: str | None = None) -> None:
        super().__init__(id=id)
        self.preset = preset
        self.overdue_style = OVERDUE_STYLE

    def show(self, overdue_style: str) -> None:
        self.overdue_style = overdue_style
        self.update(self.text())

    def text(self) -> Text:
        t = Text()
        for i, (sample, meaning) in enumerate(entries(self.preset, self.overdue_style)):
            t.append("\n" if i else "")
            t.append_text(sample)
            t.append(f" {meaning}", style="dim")
        return t

    def on_mount(self) -> None:
        self.update(self.text())
