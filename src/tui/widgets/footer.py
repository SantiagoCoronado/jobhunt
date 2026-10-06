"""The footer every section shares: Textual's key strip, with room for one note ahead of it."""
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Label


class SectionFooter(Footer):
    """`note` is a short state line ("3 selected") drawn before the keys, so it survives a
    terminal too narrow for all of them. The keys still come from the binding tables."""

    DEFAULT_CSS = """
    SectionFooter #footer-note { width: auto; height: 1; padding: 0 1; margin-right: 1;
                                 color: $footer-key-foreground; text-style: bold; }
    """
    note: reactive[str] = reactive("", recompose=True)
    _rebuild_queued = False

    def bindings_changed(self, screen: Screen) -> None:
        """Textual's Footer queues one full recompose per bindings signal, and a screen coming
        up sends a burst of them (mount, every focus move, the mode switch): a dozen rebuilds of
        every key, each restyled, before the first paint. One rebuild per burst is the same strip."""
        self._bindings_ready = True
        if not screen.app.app_focus or self._rebuild_queued:
            return
        if self.is_attached and screen is self.screen:
            self._rebuild_queued = True
            self.call_after_refresh(self._rebuild)

    async def _rebuild(self) -> None:
        self._rebuild_queued = False
        await self.recompose()

    def compose(self) -> ComposeResult:
        if self.note:
            yield Label(Text(self.note), id="footer-note")
        yield from super().compose()
