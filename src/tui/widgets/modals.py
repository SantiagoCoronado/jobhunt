"""Modal screens. Every one closes on `esc` (spec: esc is home)."""
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, OptionList
from textual.widgets.option_list import Option

from ..data import JobDetail
from ..presets import HOT
from .detail import DetailPane


class DetailOverlay(ModalScreen[None]):
    """The detail pane full-width, for a terminal too narrow to keep it beside the table."""

    DEFAULT_CSS = """
    DetailOverlay { align: center middle; }
    DetailOverlay DetailPane { width: 90%; height: 90%; border: round $primary; background: $surface; }
    """
    BINDINGS = [
        Binding("escape", "dismiss", "close"),
        Binding("enter", "dismiss", "close", show=False),
        Binding("q", "dismiss", "close", show=False),
    ]

    def __init__(self, detail: JobDetail) -> None:
        super().__init__()
        self.detail = detail

    def compose(self) -> ComposeResult:
        yield DetailPane(id="detail-overlay", classes="overlay")

    def on_mount(self) -> None:
        pane = self.query_one(DetailPane)
        pane.show(self.detail)
        pane.focus()


class StatusPicker(ModalScreen[str | None]):
    """Type to filter, arrows to move, `enter` applies. Dismisses with the status, or None."""

    DEFAULT_CSS = """
    StatusPicker { align: center middle; }
    StatusPicker #picker { width: 40; height: auto; border: round $primary; background: $surface; padding: 0 1; }
    StatusPicker OptionList { height: auto; max-height: 12; border: none; }
    StatusPicker Input { border: none; height: 1; padding: 0; }
    """
    BINDINGS = [
        Binding("escape", "dismiss(None)", "cancel"),
        Binding("up", "move(-1)", "up", show=False),
        Binding("down", "move(1)", "down", show=False),
    ]

    def __init__(self, title: str, current: str) -> None:
        super().__init__()
        self.heading = title
        self.current = current

    def compose(self) -> ComposeResult:
        with Vertical(id="picker"):
            yield Label(Text(self.heading, style="bold"))
            yield Input(placeholder="type to filter", id="picker-filter")
            yield OptionList(id="picker-list")

    def on_mount(self) -> None:
        self.refill("")
        self.query_one(Input).focus()

    @staticmethod
    def matches(term: str) -> list[str]:
        """Prefix matches first, then anything containing the term, each in pipeline order."""
        term = term.strip().lower()
        starts = [s for s in HOT if s.startswith(term)]
        return starts + [s for s in HOT if term in s and s not in starts]

    def refill(self, term: str) -> None:
        ol = self.query_one(OptionList)
        ol.clear_options()
        found = self.matches(term)
        ol.add_options(Option(Text(s, style="dim" if s == self.current else ""), id=s) for s in found)
        if found:
            ol.highlighted = found.index(self.current) if not term.strip() and self.current in found else 0

    def on_input_changed(self, event: Input.Changed) -> None:
        self.refill(event.value)

    def action_move(self, step: int) -> None:
        ol = self.query_one(OptionList)
        if ol.option_count:
            ol.highlighted = ((ol.highlighted or 0) + step) % ol.option_count

    def on_input_submitted(self, event: Input.Submitted) -> None:
        opt = self.query_one(OptionList).highlighted_option
        self.dismiss(opt.id if opt else None)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option.id)


class Confirm(ModalScreen[bool]):
    """One key: `y` goes ahead, anything else backs out."""

    DEFAULT_CSS = """
    Confirm { align: center middle; }
    Confirm Label { width: auto; max-width: 70; border: round $warning; background: $surface; padding: 0 2; }
    """

    def __init__(self, question: str) -> None:
        super().__init__()
        self.question = question

    def compose(self) -> ComposeResult:
        yield Label(Text.assemble(self.question, "  ", ("y", "bold"), " confirm · any other key cancels"))

    def on_key(self, event) -> None:
        event.stop()
        self.dismiss(event.key == "y")
