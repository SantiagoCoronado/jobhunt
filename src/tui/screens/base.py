"""SectionScreen: the frame every section shares (section bar on top, footer below)."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Static

from ..widgets.section_bar import SectionBar


class SectionScreen(Screen):
    """A section with a placeholder body. Real sections subclass and override `body`."""

    def __init__(self, mode: str, placeholder: str = "") -> None:
        super().__init__()
        self.mode = mode
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        yield SectionBar(self.mode)
        yield from self.body()
        yield Footer()

    def body(self) -> ComposeResult:
        yield Static(self.placeholder, id="placeholder")
