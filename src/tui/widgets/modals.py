"""Modal screens. Every one closes on `esc` (spec: esc is home)."""
from __future__ import annotations

from collections.abc import Callable, Sequence

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Input, Label, OptionList, Static, TextArea
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


class Picker(ModalScreen[str | None]):
    """The status picker's shape for any short list: type to filter, arrows, `enter`. Dismisses
    with the option's id. With `open_ended`, typed text that matches nothing is itself the
    answer (a full model id the list does not carry)."""

    DEFAULT_CSS = """
    Picker { align: center middle; }
    Picker #picker { width: 60; height: auto; border: round $primary; background: $surface; padding: 0 1; }
    Picker OptionList { height: auto; max-height: 14; border: none; }
    Picker Input { border: none; height: 1; padding: 0; }
    Picker #picker-note { color: $text-muted; }
    """
    BINDINGS = [
        Binding("escape", "dismiss(None)", "cancel"),
        Binding("up", "move(-1)", "up", show=False),
        Binding("down", "move(1)", "down", show=False),
    ]

    def __init__(self, title: str, options: Sequence[tuple[str, str]], current: str = "",
                 note: str = "", open_ended: bool = False) -> None:
        super().__init__()
        self.heading = title
        self.options = list(options)             # (id, label)
        self.current = current
        self.note = note
        self.open_ended = open_ended

    def compose(self) -> ComposeResult:
        with Vertical(id="picker"):
            yield Label(Text(self.heading, style="bold"))
            yield Input(placeholder="type to filter" + (", or a full name" if self.open_ended else ""),
                        id="picker-filter")
            yield OptionList(id="picker-list")
            if self.note:
                yield Label(Text(self.note), id="picker-note")

    def on_mount(self) -> None:
        self.refill("")
        self.query_one(Input).focus()

    def matches(self, term: str) -> list[tuple[str, str]]:
        term = term.strip().lower()
        starts = [o for o in self.options if o[1].lower().startswith(term)]
        return starts + [o for o in self.options if term in o[1].lower() and o not in starts]

    def refill(self, term: str) -> None:
        ol = self.query_one(OptionList)
        ol.clear_options()
        found = self.matches(term)
        ol.add_options(Option(Text(label, style="bold" if oid == self.current else ""), id=oid or "-")
                       for oid, label in found)
        ids = [oid for oid, _label in found]
        if found:
            ol.highlighted = ids.index(self.current) if not term.strip() and self.current in ids else 0

    def on_input_changed(self, event: Input.Changed) -> None:
        self.refill(event.value)

    def action_move(self, step: int) -> None:
        ol = self.query_one(OptionList)
        if ol.option_count:
            ol.highlighted = ((ol.highlighted or 0) + step) % ol.option_count

    def answer(self, option_id: str | None) -> str:
        return "" if option_id == "-" else (option_id or "")      # "-" stands in for the empty id

    def on_input_submitted(self, event: Input.Submitted) -> None:
        opt = self.query_one(OptionList).highlighted_option
        if opt is not None:
            self.dismiss(self.answer(opt.id))
        elif self.open_ended and event.value.strip():
            self.dismiss(event.value.strip())

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(self.answer(event.option.id))


class OutputModal(ModalScreen[None]):
    """A command's printed report (`hunt doctor`), scrollable. Plain text, never markup."""

    DEFAULT_CSS = """
    OutputModal { align: center middle; }
    OutputModal #output-box { width: 90%; max-width: 120; height: auto; max-height: 90%;
                              border: round $primary; background: $surface; padding: 0 1; }
    OutputModal #output-scroll { height: auto; max-height: 100%; }
    """
    BINDINGS = [
        Binding("escape", "dismiss", "close"),
        Binding("enter", "dismiss", "close", show=False),
        Binding("q", "dismiss", "close", show=False),
    ]

    def __init__(self, title: str, text: str) -> None:
        super().__init__()
        self.heading = title
        self.text = text

    def compose(self) -> ComposeResult:
        with Vertical(id="output-box"):
            yield Label(Text.assemble((self.heading, "bold"), "  esc close"))
            with VerticalScroll(id="output-scroll"):
                yield Static(Text(self.text), id="output-text")


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


class NotesEditor(ModalScreen[str | None]):
    """The whole notes field in a text area. `ctrl+s` saves, `esc` drops the edit."""

    DEFAULT_CSS = """
    NotesEditor { align: center middle; }
    NotesEditor #notes-box { width: 80%; height: 70%; border: round $primary; background: $surface; padding: 0 1; }
    NotesEditor TextArea { height: 1fr; border: none; }
    """
    BINDINGS = [
        Binding("ctrl+s", "save", "save", priority=True),
        Binding("escape", "dismiss(None)", "cancel"),
    ]

    def __init__(self, title: str, text: str) -> None:
        super().__init__()
        self.heading = title
        self.text = text

    def compose(self) -> ComposeResult:
        with Vertical(id="notes-box"):
            yield Label(Text.assemble((self.heading, "bold"), "  ctrl+s save · esc cancel"))
            yield TextArea(self.text, id="notes-text", soft_wrap=True, show_line_numbers=False)

    def on_mount(self) -> None:
        area = self.query_one(TextArea)
        area.focus()
        area.move_cursor(area.document.end)

    def action_save(self) -> None:
        self.dismiss(self.query_one(TextArea).text)


class Prompt(ModalScreen[str | None]):
    """One line of input. `parse` turns it into the value to dismiss with; when it raises
    ValueError the message shows under the box and the prompt stays open."""

    DEFAULT_CSS = """
    Prompt { align: center middle; }
    Prompt #prompt-box { width: 56; height: auto; border: round $primary; background: $surface; padding: 0 1; }
    Prompt Input { border: none; height: 1; padding: 0; }
    Prompt #prompt-error { color: $error; }
    """
    BINDINGS = [Binding("escape", "dismiss(None)", "cancel")]

    def __init__(self, title: str, hint: str, parse: Callable[[str], str], value: str = "",
                 password: bool = False) -> None:
        super().__init__()
        self.heading = title
        self.hint = hint
        self.parse = parse
        self.value = value
        self.password = password                     # a secret: typed as dots, never prefilled

    def compose(self) -> ComposeResult:
        with Vertical(id="prompt-box"):
            yield Label(Text(self.heading, style="bold"))
            yield Input(value=self.value, placeholder=self.hint, id="prompt-input", password=self.password)
            yield Label("", id="prompt-error")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            self.dismiss(self.parse(event.value))
        except ValueError as e:
            self.query_one("#prompt-error", Label).update(Text(str(e)))   # echoes typed text: no markup


KEY_NAMES = {"slash": "/", "question_mark": "?", "escape": "esc", "space": "space", "comma": ","}
HelpGroup = tuple[str, Sequence[Binding]]


def key_name(binding: Binding) -> str:
    return binding.key_display or KEY_NAMES.get(binding.key, binding.key)


def long_text(binding: Binding) -> str:
    """What `?` says about a key. A binding the footer shows keeps a one or two word
    `description` there and carries its long form in `tooltip`; both live on the one Binding,
    so the footer and the overlay still cannot drift (spec decision 21)."""
    return binding.tooltip or binding.description


def help_text(groups: Sequence[HelpGroup]) -> Text:
    """One block per group, one line per binding, straight from the BINDINGS tables the app
    runs on: the footer reads the same tables, so neither can describe a key that is not bound."""
    t = Text()
    for title, bindings in groups:
        t.append(f"{title}\n", style="bold")
        for b in bindings:
            t.append(f"  {key_name(b):<8}", style="bold cyan")
            t.append(f"{long_text(b)}\n")
        t.append("\n")
    t.rstrip()
    return t


class HelpOverlay(ModalScreen[None]):
    DEFAULT_CSS = """
    HelpOverlay { align: center middle; }
    HelpOverlay #help-box { width: 60; max-height: 90%; border: round $primary; background: $surface; padding: 0 2; }
    """
    BINDINGS = [
        Binding("escape", "dismiss", "close"),
        Binding("question_mark", "dismiss", "close", show=False),
        Binding("q", "dismiss", "close", show=False),
    ]

    def __init__(self, groups: Sequence[HelpGroup]) -> None:
        super().__init__()
        self.groups = groups

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="help-box"):
            yield Static(help_text(self.groups), id="help-text")
