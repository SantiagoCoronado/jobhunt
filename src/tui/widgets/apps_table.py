"""Section 4's table: one line per application folder, pending first."""
from __future__ import annotations

from rich.text import Text
from textual.binding import Binding
from textual.widgets import DataTable

from ..data import APP_FILES, AppRow
from .jobs_table import NONE, clip

# (key, label, width)
COLUMNS: tuple[tuple[str, str, int], ...] = (
    ("bucket", "bucket", 7),
    ("company", "company", 20),
    ("title", "title", 30),
    ("status", "status", 11),
    ("files", "files", 22),
    ("build", "build", 10),
    ("drift", "drift", 52),
)
BUILD_STYLE = {"ok": "green", "": ""}       # anything else (fail N, unreadable) is red
DRIFT_STYLE = "yellow"


class AppsTable(DataTable):
    DEFAULT_CSS = """
    AppsTable { width: 1fr; height: 1fr; }
    """
    BINDINGS = [
        Binding("j", "cursor_down", "down", show=False),
        Binding("k", "cursor_up", "up", show=False),
        Binding("g", "top", "top", show=False),
        Binding("G", "bottom", "bottom", show=False),
    ]

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id, cursor_type="row", zebra_stripes=False, cell_padding=1)
        self.apps: list[AppRow] = []

    def on_mount(self) -> None:
        for key, label, width in COLUMNS:
            self.add_column(label, key=key, width=width)

    @staticmethod
    def cells(a: AppRow) -> tuple[Text, ...]:
        """`Text` cells only: company and title come from scraped postings, the rest from
        folder names (see `JobsTable.cells`)."""
        widths = {key: w for key, _label, w in COLUMNS}
        files = Text(" ").join(Text(f) if f in a.files else Text(NONE * len(f), style="dim") for f in APP_FILES)
        return (
            Text(a.bucket),
            Text(clip(a.company, widths["company"])),
            Text(clip(a.title, widths["title"]) or NONE),
            Text(a.status or NONE),
            files,
            Text(a.build or NONE, style=BUILD_STYLE.get(a.build, "red")),
            Text(clip(a.drift, widths["drift"]), style=DRIFT_STYLE),
        )

    def load(self, apps: list[AppRow]) -> None:
        """The cursor stays on the same folder when it is still listed (a status change moves
        the folder to another bucket, not off the list), else on the same line."""
        was = self.current.folder.name if self.current else None
        was_line = self.cursor_row
        self.clear()
        self.apps = apps
        for a in apps:
            self.add_row(*self.cells(a), key=f"{a.bucket}/{a.folder.name}")
        if apps and was is not None:
            names = [a.folder.name for a in apps]
            self.move_cursor(row=names.index(was) if was in names else min(was_line, len(apps) - 1))

    @property
    def current(self) -> AppRow | None:
        return self.apps[self.cursor_row] if 0 <= self.cursor_row < len(self.apps) else None

    def action_top(self) -> None:
        if self.row_count:
            self.move_cursor(row=0)

    def action_bottom(self) -> None:
        if self.row_count:
            self.move_cursor(row=self.row_count - 1)
