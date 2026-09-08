"""Self-contained offline HTML dashboard over the pipeline DB.

  python -m src.report [--out data/report.html] [--open]

Fully deterministic: SQL + src.stats compute everything, no LLM anywhere.
The output is ONE file: inline CSS, inline SVG charts, inline vanilla JS,
zero external requests, works from file:// with no network. Regenerate any
time; data/ is gitignored so the report never lands in the repo.
"""
from __future__ import annotations

import argparse
import html
import json
import sqlite3
import subprocess
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from statistics import median

from .db import DB_PATH, STATUSES, connect
from .stats import comp_data, funnel_data, latency_data

STAGE_ORDER = ["applied", "screen", "interview", "offer"]
OPEN_PIPELINE = ("shortlisted", "applied", "screen", "interview", "offer")


def esc(v) -> str:
    # Postings carry em-dashes in titles/companies; the zero em-dash rule covers
    # the whole generated page, so normalize external text to a plain hyphen.
    return html.escape(str(v if v is not None else "").replace("—", "-"))


# ---------------------------------------------------------------- data pulls

def reached_stages(conn: sqlite3.Connection) -> dict[str, int]:
    """How many jobs ever REACHED each stage (funnel semantics, not current status).

    A job reached stage X if the event log has a status_change to X or later,
    or its current status is X or later. Later implies earlier (you cannot
    interview without having applied), so one max per job fills the prefix.
    """
    idx = {s: i for i, s in enumerate(STAGE_ORDER)}
    best: dict[int, int] = {}
    for r in conn.execute("SELECT job_id, payload FROM events WHERE kind='status_change'"):
        try:
            to = json.loads(r["payload"] or "{}").get("to")
        except json.JSONDecodeError:
            continue
        if to in idx:
            best[r["job_id"]] = max(best.get(r["job_id"], -1), idx[to])
    for r in conn.execute("SELECT id, status, applied_at FROM jobs"):
        if r["status"] in idx:
            best[r["id"]] = max(best.get(r["id"], -1), idx[r["status"]])
        elif r["applied_at"] and r["id"] not in best:
            best[r["id"]] = 0  # applied at some point, later status is off-track
    counts = dict.fromkeys(STAGE_ORDER, 0)
    for top in best.values():
        for i in range(top + 1):
            counts[STAGE_ORDER[i]] += 1
    return counts


def status_distribution(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    got = dict(conn.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status").fetchall())
    return [(s, got[s]) for s in STATUSES if got.get(s)]


def followups_due(conn: sqlite3.Connection, today: date) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT id, company, title, status, next_followup_at, last_contact_at "
        "FROM jobs WHERE status IN ('applied','screen','interview') "
        "AND next_followup_at IS NOT NULL AND next_followup_at <= ? "
        "ORDER BY next_followup_at", (today.isoformat(),),
    ).fetchall()


def application_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT id, company, title, source, match_score, status, applied_at, "
        "last_contact_at, next_followup_at FROM jobs "
        "WHERE applied_at IS NOT NULL "
        "OR status IN ('applied','screen','interview','offer') "
        "ORDER BY applied_at IS NULL, applied_at DESC, id DESC",
    ).fetchall()


def source_health(conn: sqlite3.Connection, window: int = 5) -> list[dict]:
    """Last `window` runs per source; flag sources whose recent runs all came
    up empty or failed (>= 2 runs so one bad night is not a verdict)."""
    per: dict[str, list[sqlite3.Row]] = {}
    for r in conn.execute("SELECT ts, source, pulled, new, ok FROM runs ORDER BY id DESC"):
        bucket = per.setdefault(r["source"], [])
        if len(bucket) < window:
            bucket.append(r)
    out = []
    for src in sorted(per):
        runs = per[src]
        dead = len(runs) >= 2 and all(r["pulled"] == 0 or not r["ok"] for r in runs)
        out.append({"source": src, "last": (runs[0]["ts"] or "")[:10], "runs": len(runs),
                    "pulled": sum(r["pulled"] for r in runs),
                    "new": sum(r["new"] for r in runs), "dead": dead})
    return out


# ---------------------------------------------------------------- SVG charts

def bar_chart(rows: Sequence[tuple[str, float, str, str]], max_val: float,
              label_w: int = 150) -> str:
    """Horizontal single-series bars. rows: (label, value, tip_text, hover_text).

    Mark spec: bar 20px thick, 4px rounded data-end, square at the baseline,
    value label at the tip in ink (never on every gridline; there is no grid).
    """
    if not rows:
        return '<p class="empty">No data yet.</p>'
    row_h, bar_h, width = 30, 20, 680
    plot_x, plot_w = label_w + 10, width - label_w - 10 - 120
    height = row_h * len(rows)
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" '
             f'style="width:100%;max-width:{width}px;height:auto">']
    for i, (label, value, tip, hover) in enumerate(rows):
        y = i * row_h + (row_h - bar_h) // 2
        cy = i * row_h + row_h // 2 + 4
        w = 0 if max_val <= 0 else plot_w * value / max_val
        parts.append(f'<text x="{label_w}" y="{cy}" text-anchor="end" '
                     f'class="axis">{esc(label)}</text>')
        if w >= 1:
            r = min(4, w / 2)
            d = (f"M{plot_x},{y} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} "
                 f"v{bar_h - 2 * r} a{r},{r} 0 0 1 {-r},{r} h{-(w - r):.1f} z")
            parts.append(f'<path d="{d}" class="bar"><title>{esc(hover)}</title></path>')
        parts.append(f'<text x="{plot_x + w + 6:.1f}" y="{cy}" class="tip">{esc(tip)}</text>')
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------- sections

def _cards(fd: dict, lat_days: list[int], open_count: int) -> str:
    total, responded = fd["total"], fd["responded"]
    rate = f"{100 * responded // total}%" if total else "0%"
    med = f"{median(lat_days):.0f}d" if lat_days else "n/a"
    interviews = fd["by_stage"]["interview"] + fd["by_stage"]["offer"]
    cards = [
        ("Applications", str(total), "ever applied"),
        ("Response rate", rate, f"{responded} responded"),
        ("Median response", med, f"n={len(lat_days)}"),
        ("In interviews", str(interviews), "current"),
        ("Offers", str(fd["by_stage"]["offer"]), "current"),
        ("Open pipeline", str(open_count), "shortlisted through offer"),
    ]
    tiles = "".join(
        f'<div class="card"><div class="card-label">{esc(label)}</div>'
        f'<div class="card-value">{esc(value)}</div>'
        f'<div class="card-sub">{esc(sub)}</div></div>' for label, value, sub in cards)
    return f'<div class="cards">{tiles}</div>'


def _funnel_section(conn: sqlite3.Connection, fd: dict) -> str:
    reached = reached_stages(conn)
    rows = [("applied", reached["applied"], str(reached["applied"]),
             f"{reached['applied']} applications")]
    rows.append(("responded", fd["responded"], str(fd["responded"]),
                 f"{fd['responded']} got any reply (a rejection counts)"))
    for s in STAGE_ORDER[1:]:
        rows.append((s, reached[s], str(reached[s]), f"{reached[s]} reached {s}"))
    mx = max((v for _, v, _, _ in rows), default=0)
    return bar_chart(rows, mx)


def _rate_charts(fd: dict) -> str:
    out = []
    for label, rows in fd["segments"].items():
        bars = []
        for key, n, resp in rows:
            pct = 100 * resp // n if n else 0
            bars.append((key, pct, f"{resp}/{n} ({pct}%)",
                         f"{key}: {n} applied, {resp} responded"))
        out.append(f"<h3>Response rate by {esc(label)}</h3>"
                   + bar_chart(bars, 100))
    return "".join(out)


def _status_section(conn: sqlite3.Connection) -> str:
    dist = status_distribution(conn)
    mx = max((c for _, c in dist), default=0)
    return bar_chart([(s, c, str(c), f"{c} jobs currently {s}") for s, c in dist], mx)


def _comp_section(conn: sqlite3.Connection, min_score: int = 70) -> str:
    d = comp_data(conn, min_score)
    if not d["n_rows"]:
        return '<p class="empty">No salary data at score floor 70.</p>'
    rows = "".join(
        f"<tr><td>{esc(s['currency'])}</td><td>{esc(s['family'])}</td>"
        f"<td>{'yes' if s['remote'] else 'no'}</td><td class='num'>{s['n']}</td>"
        f"<td class='num'>{s['median']:,}</td><td class='num'>{s['min']:,}</td>"
        f"<td class='num'>{s['max']:,}</td></tr>" for s in d["segments"])
    return (f"<p>Salary data on {d['n_rows']} deduped roles scoring 70+ "
            "(value = max of range, else min).</p>"
            "<p class='note'>NOTE: units are as-posted; some boards post "
            "MONTHLY figures, so a '5,000 USD' cluster is a monthly rate, not annual. "
            "Sanity-check before negotiating.</p>"
            "<table><thead><tr><th>ccy</th><th>family</th><th>remote</th>"
            "<th class='num'>n</th><th class='num'>median</th><th class='num'>min</th>"
            f"<th class='num'>max</th></tr></thead><tbody>{rows}</tbody></table>")


def _followups_section(conn: sqlite3.Connection, today: date) -> str:
    due = followups_due(conn, today)
    if not due:
        return '<p class="empty">Nothing due. Clean slate.</p>'
    rows = "".join(
        f"<tr><td>{r['id']}</td><td>{esc(r['company'])}</td><td>{esc(r['title'])}</td>"
        f"<td>{esc(r['status'])}</td><td>{esc(r['next_followup_at'])}</td>"
        f"<td>{esc(r['last_contact_at'] or 'never')}</td></tr>" for r in due)
    return ("<table><thead><tr><th>id</th><th>company</th><th>role</th><th>status</th>"
            f"<th>due</th><th>last contact</th></tr></thead><tbody>{rows}</tbody></table>")


def _applications_section(conn: sqlite3.Connection, today: date) -> str:
    apps = application_rows(conn)
    if not apps:
        return '<p class="empty">No applications yet.</p>'
    statuses = sorted({r["status"] for r in apps})
    options = "".join(f'<option value="{esc(s)}">{esc(s)}</option>' for s in statuses)
    body = []
    for r in apps:
        days = ""
        if r["applied_at"]:
            try:
                days = str((today - date.fromisoformat(r["applied_at"][:10])).days)
            except ValueError:
                pass
        body.append(
            f"<tr><td>{r['id']}</td><td>{esc(r['company'])}</td><td>{esc(r['title'])}</td>"
            f"<td>{esc(r['source'])}</td><td class='num'>{esc(r['match_score'])}</td>"
            f"<td>{esc(r['status'])}</td><td>{esc(r['applied_at'])}</td>"
            f"<td>{esc(r['last_contact_at'])}</td><td>{esc(r['next_followup_at'])}</td>"
            f"<td class='num'>{days}</td></tr>")
    heads = ["id", "company", "role", "source", "score", "status", "applied",
             "last contact", "follow-up", "days"]
    ths = "".join(f'<th data-col="{i}">{esc(h)}</th>' for i, h in enumerate(heads))
    return (
        '<div class="filters"><input id="q" type="search" placeholder="filter text">'
        f'<select id="st"><option value="">all statuses</option>{options}</select></div>'
        f'<table id="apps"><thead><tr>{ths}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table>')


def _sources_section(conn: sqlite3.Connection) -> str:
    health = source_health(conn)
    if not health:
        return '<p class="empty">No discover runs recorded yet.</p>'
    rows = "".join(
        f"<tr><td>{esc(h['source'])}</td><td>{esc(h['last'])}</td>"
        f"<td class='num'>{h['runs']}</td><td class='num'>{h['pulled']}</td>"
        f"<td class='num'>{h['new']}</td>"
        f"<td>{'&#9888; possibly dead' if h['dead'] else 'ok'}</td></tr>"
        for h in health)
    return ("<p>Per source, over its last 5 discover runs. A source whose recent runs "
            "all pulled 0 (or failed) is silently dead: check its adapter or key.</p>"
            "<table><thead><tr><th>source</th><th>last run</th><th class='num'>runs</th>"
            "<th class='num'>pulled</th><th class='num'>new</th><th>health</th></tr>"
            f"</thead><tbody>{rows}</tbody></table>")


# ---------------------------------------------------------------- page

CSS = """
:root {
  color-scheme: light;
  --page: #f9f9f7; --surface: #fcfcfb;
  --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
  --hairline: #e1e0d9; --border: rgba(11,11,11,0.10);
  --series: #2a78d6; --warn: #d03b3b;
}
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --page: #0d0d0d; --surface: #1a1a19;
    --ink: #ffffff; --ink-2: #c3c2b7; --muted: #898781;
    --hairline: #2c2c2a; --border: rgba(255,255,255,0.10);
    --series: #3987e5; --warn: #e66767;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--page); color: var(--ink);
  font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 960px; margin: 0 auto; padding: 24px 16px 64px; }
h1 { font-size: 22px; margin: 0 0 4px; }
h2 { font-size: 16px; margin: 0 0 12px; }
h3 { font-size: 13px; color: var(--ink-2); margin: 16px 0 4px; font-weight: 600; }
.stamp { color: var(--muted); margin-bottom: 24px; }
section { background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 16px; margin-bottom: 16px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px; margin-bottom: 16px; }
.card { background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 12px 14px; }
.card-label { color: var(--ink-2); font-size: 12px; }
.card-value { font-size: 28px; font-weight: 600; }
.card-sub { color: var(--muted); font-size: 12px; }
svg { display: block; }
svg .bar { fill: var(--series); }
svg .axis { fill: var(--ink-2); font-size: 12px; }
svg .tip { fill: var(--ink); font-size: 12px; font-variant-numeric: tabular-nums; }
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; padding: 5px 10px 5px 0; border-bottom: 1px solid var(--hairline);
  font-variant-numeric: tabular-nums; }
th { color: var(--ink-2); font-weight: 600; cursor: pointer; user-select: none; }
td.num, th.num { text-align: right; }
.note, .empty { color: var(--muted); }
.filters { display: flex; gap: 8px; margin-bottom: 10px; }
.filters input, .filters select { background: var(--page); color: var(--ink);
  border: 1px solid var(--border); border-radius: 6px; padding: 5px 8px; font: inherit; }
.overflow { overflow-x: auto; }
"""

JS = """
(function () {
  var q = document.getElementById('q'), st = document.getElementById('st'),
      table = document.getElementById('apps');
  if (!table) return;
  var body = table.tBodies[0];
  function applyFilter() {
    var text = (q.value || '').toLowerCase(), status = st.value;
    Array.prototype.forEach.call(body.rows, function (row) {
      var okText = !text || row.textContent.toLowerCase().indexOf(text) !== -1;
      var okStatus = !status || row.cells[5].textContent === status;
      row.style.display = okText && okStatus ? '' : 'none';
    });
  }
  q.addEventListener('input', applyFilter);
  st.addEventListener('change', applyFilter);
  var dir = {};
  table.tHead.addEventListener('click', function (e) {
    var th = e.target.closest('th');
    if (!th) return;
    var col = +th.dataset.col;
    dir[col] = -(dir[col] || -1);
    var rows = Array.prototype.slice.call(body.rows);
    rows.sort(function (a, b) {
      var x = a.cells[col].textContent, y = b.cells[col].textContent;
      var nx = parseFloat(x), ny = parseFloat(y);
      if (!isNaN(nx) && !isNaN(ny)) return (nx - ny) * dir[col];
      return x.localeCompare(y) * dir[col];
    });
    rows.forEach(function (r) { body.appendChild(r); });
  });
})();
"""


def build_html(conn: sqlite3.Connection, today: date | None = None) -> str:
    today = today or date.today()
    fd = funnel_data(conn)
    lat = latency_data(conn)["days"]
    open_count = conn.execute(
        f"SELECT COUNT(*) FROM jobs WHERE status IN ({','.join('?' * len(OPEN_PIPELINE))})",
        OPEN_PIPELINE).fetchone()[0]

    def section(sid: str, title: str, body: str) -> str:
        return (f'<section id="{sid}"><h2>{esc(title)}</h2>'
                f'<div class="overflow">{body}</div></section>')

    parts = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>jobhunt report</title>",
        "<link rel='icon' href='data:,'>",
        f"<style>{CSS}</style></head><body><main>",
        "<h1>Job hunt report</h1>",
        f"<p class='stamp'>Generated {today.isoformat()}. Offline snapshot; "
        "regenerate with <code>python -m src.report</code>.</p>",
        _cards(fd, lat, open_count),
        section("funnel", "Funnel", _funnel_section(conn, fd)
                if fd["total"] else '<p class="empty">No applications yet.</p>'),
        section("rates", "Where responses come from", _rate_charts(fd)
                if fd["total"] else '<p class="empty">No applications yet.</p>'),
        section("statuses", "Pipeline by status", _status_section(conn)),
        section("followups", "Follow-ups due", _followups_section(conn, today)),
        section("applications", "Applications", _applications_section(conn, today)),
        section("comp", "Compensation landscape", _comp_section(conn)),
        section("sources", "Source health", _sources_section(conn)),
        f"<script>{JS}</script></main></body></html>",
    ]
    page = "".join(parts)
    assert "—" not in page, "em-dash leaked into the report"
    return page


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DB_PATH.parent / "report.html"))
    ap.add_argument("--open", action="store_true", dest="open_it",
                    help="open the report in the default browser (macOS)")
    a = ap.parse_args()
    conn = connect()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(conn), encoding="utf-8")

    fd = funnel_data(conn)
    lat = latency_data(conn)["days"]
    total, responded = fd["total"], fd["responded"]
    rate = f"{100 * responded // total}%" if total else "0%"
    med = f"{median(lat):.0f}d" if lat else "n/a"
    print(f"Report: {out}")
    print(f"Applications: {total} | responded {responded} ({rate}) | "
          f"median response {med} | in interviews "
          f"{fd['by_stage']['interview'] + fd['by_stage']['offer']} | "
          f"offers {fd['by_stage']['offer']}")
    if a.open_it:
        subprocess.run(["open", str(out)], check=False)


if __name__ == "__main__":
    main()
