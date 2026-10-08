"""The stats screen's drawing (pre-release spec decision 15): pure functions from a
`data.StatsSnapshot` to Rich text, one column, no app needed to test them.

Top to bottom: the header (last discover and its age, the last hunt), the tiles, the funnel on
two scales, score vs reply, the sources table. A bar that is zero names the step that fills it,
so the day-1 screen (found rows, nothing else) reads as a list of next steps, not a broken chart.
"""
from __future__ import annotations

from collections.abc import Sequence

from rich.text import Text

from ..data import (CALIBRATION_FROM, FIRST_APPLIED, FUNNEL, SMALL_BAND, STALE_DISCOVER,
                    SOURCE_WINDOW, StatsSnapshot)
from ..sections import number

BAR_WIDTH = 40                 # the funnel's full bar
RATE_WIDTH = 20                # score vs reply: a full bar is a 100% reply rate
EIGHTHS = " ▏▎▍▌▋▊▉"
FULL = "█"
GAP = "   "                    # between the header's two halves
TILE_GAP = "  "
LABEL_WIDTH = 12
COUNT_WIDTH = 8
WARN = "yellow"
BAD = "red"
NONE = "-"


def bar(value: float, scale: float, width: int = BAR_WIDTH) -> str:
    """`value` against `scale` in eighth blocks. Anything above zero draws at least one eighth,
    so a small count never reads as nothing; zero (or no scale) is the empty string."""
    if value <= 0 or scale <= 0:
        return ""
    eighths = max(1, round(min(value / scale, 1.0) * width * 8))
    full, rest = divmod(eighths, 8)
    return FULL * full + (EIGHTHS[rest] if rest else "")


def tile(label: str, value: str, note: str = "") -> Text:
    """One number with its name, the way the tiles row reads: `applications 121`."""
    t = Text(f"{label} ")
    t.append(value, style="bold")
    if note:
        t.append(f" {note}", style="dim")
    return t


def table(headers: Sequence[str], rows: Sequence[Sequence[str | Text]], right: frozenset[int] = frozenset()) -> Text:
    """Plain columns two spaces apart, the header dim; a column in `right` is right-aligned. A
    cell may be Text to carry its own style (the dead flag)."""
    cells = [[c if isinstance(c, Text) else Text(c) for c in row] for row in rows]
    widths = [max([len(h), *(len(r[i]) for r in cells)]) for i, h in enumerate(headers)]

    def line(row: Sequence[Text], style: str = "") -> Text:
        out = Text(style=style)
        for i, (cell, w) in enumerate(zip(row, widths, strict=True)):
            if i:
                out.append("  ")
            pad = " " * (w - len(cell))
            out.append_text(Text(pad) + cell if i in right else cell + Text(pad))
        out.rstrip()
        return out

    t = Text()
    t.append_text(line([Text(h) for h in headers], "dim"))
    for row in cells:
        t.append("\n")
        t.append_text(line(row))
    return t


def pct(part: int, whole: int) -> str:
    return f"{round(100 * part / whole)}%" if whole else NONE


def tokens(n: int | None) -> str:
    """Context tokens the way the hunt report reads them: 850k, 3.2M; a dash for none."""
    if n is None:
        return NONE
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n // 1_000}k"
    return str(n)


def cost(usd: float | None) -> str:
    return NONE if usd is None else f"${usd:.2f}"


def _days(n: int) -> str:
    return "today" if n == 0 else "1 day ago" if n == 1 else f"{n} days ago"


def zero_hint(step: str) -> str:
    """What fills an empty bar, naming the section that does it."""
    run, board = number("run"), number("board")
    if step == "found":
        return f"run discover in section {run}"
    if step in ("scored", "shortlisted"):
        return f"run match in section {run}"
    if step == "applied":
        return f"tailor in section {run}, apply by hand, then s in section {board}"
    return f"run inbox in section {run}, or s in section {board}"


def header(s: StatsSnapshot) -> Text:
    t = Text()
    age = s.discover_age
    if s.last_discover is None or age is None:
        t.append(f"no discover yet: run discover in section {number('run')}", style=WARN)
    else:
        t.append(f"last discover {s.last_discover}, {_days(age)}", style=WARN if age > STALE_DISCOVER else "")
    t.append(GAP)
    h = s.hunt
    if h is None:
        t.append("no hunt yet", style="dim")
        return t
    t.append(f"last hunt {h.run_id}: ")
    t.append(h.state, style=BAD if h.state in ("failed", "unreadable") else "")
    t.append(f", {h.units} unit{'' if h.units == 1 else 's'}")
    if h.failed:
        t.append(f", {h.failed} failed", style=BAD)
    t.append(f", context {tokens(h.context)}, cost {cost(h.cost_usd)}")
    return t


def tiles(s: StatsSnapshot) -> Text:
    med = s.median_reply
    parts = [
        tile("applications", f"{s.applications:,}"),
        tile("any reply", NONE if s.reply_rate is None else f"{s.reply_rate}%", "(rejections count)"),
        tile("median reply", NONE if med is None else f"{med:.0f}d"),
        tile("waiting", f"{s.waiting:,}"),
        tile("in interviews", f"{s.interviewing:,}"),
        tile("applied 7d", f"{s.applied_7d:,}") + Text(" / 28d ") + Text(f"{s.applied_28d:,}", style="bold"),
    ]
    return Text(TILE_GAP).join(parts)


def funnel(s: StatsSnapshot) -> Text:
    """Found, scored and shortlisted against found; applied onward against applied, so a hundred
    applications never draw as a sliver under fifty thousand found rows. The percent is of the
    bar above, from replied on."""
    counts = dict(s.funnel)
    lines = []
    for i, step in enumerate(FUNNEL):
        n = counts[step]
        scale = counts[FUNNEL[0]] if i < FIRST_APPLIED else counts["applied"]
        prev = counts[FUNNEL[i - 1]] if i else 0
        t = Text(f"{step:<{LABEL_WIDTH}}{n:>{COUNT_WIDTH},}  ")
        rated = i > FIRST_APPLIED and prev > 0
        if n == 0 and (step in FUNNEL[:FIRST_APPLIED + 2] or not rated):
            t.append(zero_hint(step), style="dim")       # an empty step: say what fills it
        else:
            t.append(f"{bar(n, scale):<{BAR_WIDTH}}")
            if rated:
                t.append(f"  {pct(n, prev):>4}")
        t.rstrip()
        lines.append(t)
    lines.append(Text("found to shortlisted are drawn against found, applied on against applied; "
                      "a percent is of the bar above", style="dim"))
    return Text("\n").join(lines)


def score_vs_reply(s: StatsSnapshot) -> Text:
    """Reply rate per score band with its n; a band under SMALL_BAND is dimmed (weak evidence).
    One line until CALIBRATION_FROM applications: before that every band is noise."""
    label = f"{'score vs reply':<{LABEL_WIDTH + 5}}"
    if s.applications < CALIBRATION_FROM or not s.bands:
        return Text(label) + Text(f"shows from {CALIBRATION_FROM} applications ({s.applications} so far)", style="dim")
    lines = []
    for i, b in enumerate(s.bands):
        t = Text(label if i == 0 else " " * len(label))
        t.append(f"{b.band:<10}{bar(b.rate, 100, RATE_WIDTH):<{RATE_WIDTH}}  {b.rate:>3}%  n={b.n}",
                 style="dim" if b.n < SMALL_BAND else "")
        lines.append(t)
    if any(b.n < SMALL_BAND for b in s.bands):
        lines.append(Text(" " * len(label) + f"dimmed: under {SMALL_BAND} applications, weak evidence", style="dim"))
    return Text("\n").join(lines)


def sources(s: StatsSnapshot) -> Text:
    """One row per source, dead first. Before the first application the table is pulled and new
    (and the health flag, which is what a missing key looks like on day 1)."""
    if not s.sources:
        return Text(f"sources: no discover runs yet, run discover in section {number('run')}", style="dim")
    applied = s.applications > 0
    headers = ["source", "pulled", "new", *(("applied", "replies", "rate") if applied else ()), "health"]
    rows: list[list[str | Text]] = []
    for x in s.sources:
        health = Text("dead", style=BAD) if x.dead else Text("ok" if x.runs else NONE, style="" if x.runs else "dim")
        ran = (f"{x.pulled:,}", f"{x.new:,}") if x.runs else (NONE, NONE)
        extra = (f"{x.applied:,}", f"{x.replied:,}", NONE if x.rate is None else f"{x.rate}%") if applied else ()
        rows.append([x.source, *ran, *extra, health])
    right = frozenset(range(1, len(headers) - 1))
    note = Text(f"pulled and new over each source's last {SOURCE_WINDOW} discover runs; "
                "dead: every recent run came back empty or failed", style="dim")
    return table(headers, rows, right) + Text("\n") + note


def render(s: StatsSnapshot) -> Text:
    """The whole screen, top to bottom, a blank line between the parts."""
    return Text("\n\n").join([header(s), tiles(s), funnel(s), score_vs_reply(s), sources(s)])
