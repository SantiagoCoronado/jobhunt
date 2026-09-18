"""Left pane: the hot statuses with their counts, then a dimmed `all` (spec decisions 10, 14)."""
from __future__ import annotations

from rich.text import Text
from textual.binding import Binding
from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from ..presets import ALL, HOT


class StatusList(OptionList):
    DEFAULT_CSS = """
    StatusList { width: 22; height: 1fr; border: none; border-right: solid $panel; padding: 0; }
    """
    BINDINGS = [
        Binding("j", "cursor_down", "down", show=False),
        Binding("k", "cursor_up", "up", show=False),
    ]

    class Picked(Message):
        """The highlighted status changed; the screen filters the table by it."""

        def __init__(self, status: str) -> None:
            super().__init__()
            self.status = status

    def __init__(self, statuses: tuple[str, ...] = (*HOT, ALL), id: str | None = None) -> None:
        self.statuses = statuses
        super().__init__(*(Option(self._prompt(s, None), id=s) for s in statuses), id=id)

    @staticmethod
    def _prompt(status: str, count: int | None) -> Text:
        n = "" if count is None else str(count)
        return Text(f"{status:<13}{n:>6}", style="dim" if status == ALL else "")

    def on_mount(self) -> None:
        self.highlighted = 0

    def set_counts(self, counts: dict[str, int]) -> None:
        for s in self.statuses:
            self.replace_option_prompt(s, self._prompt(s, counts.get(s, 0)))

    @property
    def status(self) -> str | None:
        opt = self.highlighted_option
        return opt.id if opt else None

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        event.stop()
        if event.option.id:
            self.post_message(self.Picked(event.option.id))
