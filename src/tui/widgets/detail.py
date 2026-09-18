"""Right pane: everything about the highlighted job (spec decision 16), scrolling."""
from __future__ import annotations

from pathlib import Path

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Static

from ..data import Event, JobDetail

NONE = "·"
RULE = "─" * 34
ROOT = Path(__file__).resolve().parents[3]


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def _salary(d: JobDetail) -> str:
    lo, hi = d.salary_min, d.salary_max
    if not lo and not hi:
        return ""
    span = f"{lo:,} to {hi:,}" if lo and hi and lo != hi else f"{(lo or hi):,}"
    return f"{d.currency} {span}".strip()


def event_line(e: Event) -> str:
    day = e.ts[:10]
    p = e.payload
    if e.kind == "status_change":
        what = f"{p.get('from') or NONE} -> {p.get('to') or NONE}"
    elif e.kind == "contact":
        what = f"contact {p.get('date') or ''}".rstrip() + (" (follow-up bumped)" if p.get("bumped") else "")
    else:
        what = f"{e.kind}: {p.get('note') or p.get('raw') or ''}".rstrip(": ")
    return f"{day} {what}"


def render_detail(d: JobDetail) -> Text:
    r = d.row
    t = Text()

    def section(name: str) -> None:
        t.append(f"{RULE}\n", style="dim")
        t.append(f"{name}\n", style="bold")

    t.append(f"#{r.id} {r.company}\n", style="bold")
    t.append(f"{r.title}\n")
    head = [r.location or NONE, r.source, f"dream: {'yes' if r.dream else 'no'}"]
    if d.remote:
        head.append("remote")
    if _salary(d):
        head.append(_salary(d))
    t.append(" · ".join(head) + "\n", style="dim")

    score = NONE if r.score is None else str(r.score)
    t.append(f"score {score} · {r.status} · seen {(d.first_seen or NONE)[:10]}\n")
    # Two spaces between the pairs, as in the mockup: `·` already means "none" on this line.
    t.append(f"applied {r.applied_at or NONE}  fup {r.followup or NONE}  "
             f"contact {d.last_contact_at or NONE}  folder {d.bucket + '/' if d.bucket else NONE}\n")
    if d.dossier:
        t.append(f"dossier {_rel(d.dossier)}\n")

    section("verdict")
    v = d.verdict
    if v.empty:
        t.append(" not scored yet\n", style="dim")
    elif v.raw:
        t.append(f" {v.raw}\n")
    else:
        bucket = f" (bucket {v.bucket})" if v.bucket is not None else ""
        t.append(f" {v.recommendation or NONE}{bucket}\n")
        if v.reasons:
            t.append(f" {v.reasons}\n")
        if v.strengths:
            t.append(f" strengths: {', '.join(v.strengths)}\n")
        t.append(f" missing: {', '.join(v.missing_skills) or 'none'}\n")

    section("notes")
    t.append(f"{d.notes}\n" if d.notes else " none\n", style="" if d.notes else "dim")

    section("events")
    if d.events:
        for e in d.events:
            t.append(f" {event_line(e)}\n")
    else:
        t.append(" none\n", style="dim")

    section("description")
    t.append(d.description or " none stored", style="" if d.description else "dim")
    return t


class DetailPane(VerticalScroll):
    DEFAULT_CSS = """
    DetailPane { width: 48; height: 1fr; border-left: solid $panel; padding: 0 1; }
    DetailPane.overlay { width: 100%; border-left: none; }
    """
    BINDINGS = [
        Binding("j", "scroll_down", "down", show=False),
        Binding("k", "scroll_up", "up", show=False),
        Binding("g", "scroll_home", "top", show=False),
        Binding("G", "scroll_end", "bottom", show=False),
    ]

    def __init__(self, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(id=id, classes=classes)
        self.job_id: int | None = None

    def compose(self) -> ComposeResult:
        yield Static("", id="detail-body")

    def show(self, d: JobDetail | None) -> None:
        self.job_id = d.row.id if d else None
        self.query_one("#detail-body", Static).update(render_detail(d) if d else Text(""))
        self.scroll_home(animate=False)

    @property
    def text(self) -> str:
        """What the pane is showing, as plain text."""
        content = self.query_one("#detail-body", Static).content
        return content.plain if isinstance(content, Text) else str(content)
