"""The footer every section shares: Textual's key strip, with room for one note ahead of it."""
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Footer, Label


class SectionFooter(Footer):
    """`note` is a short state line ("3 selected") drawn before the keys, so it survives a
    terminal too narrow for all of them. The keys still come from the binding tables."""

    DEFAULT_CSS = """
    SectionFooter #footer-note { width: auto; height: 1; padding: 0 1; margin-right: 1;
                                 color: $footer-key-foreground; text-style: bold; }
    """
    note: reactive[str] = reactive("", recompose=True)

    def compose(self) -> ComposeResult:
        if self.note:
            yield Label(Text(self.note), id="footer-note")
        yield from super().compose()
