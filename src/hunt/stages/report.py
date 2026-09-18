"""Stage 8, report: `data/report.html` from `src.report.build_html` and the run's
`report.md` (what each stage did, the picks, the needs_human list). PR 3 story 6 grows the
markdown into the full section 7 report with build verdicts and usage."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ... import db
from ..ledger import Ledger, run_state
from .base import Context, StageResult


def html_path() -> Path:
    return db.DB_PATH.parent / "report.html"


def render_markdown(led: Ledger) -> str:
    st = led.state
    lines = [f"# Hunt {st['run_id']}", "",
             f"Harness {st.get('harness') or '-'}, started {st.get('started') or '-'}, state {run_state(st)}.", "",
             "## Stages", "", "| stage | state | units | summary |", "|---|---|---|---|"]
    needs: list[str] = []
    for s in st["stages"]:
        units = s.get("units") or []
        done = sum(1 for u in units if u.get("state") == "done")
        summ: dict[str, Any] = dict(s.get("summary") or {})
        needs += [str(x) for x in (summ.pop("needs_human", None) or [])]
        text = ", ".join(f"{k} {v}" for k, v in summ.items() if not isinstance(v, (list, dict)))
        note = f" ({s['note']})" if s.get("note") else ""
        lines.append(f"| {s['name']} | {s['state']}{note} | {done}/{len(units)} | {text} |")
    picks_file = led.run_dir / "picks.json"
    if picks_file.exists():
        picks = json.loads(picks_file.read_text(encoding="utf-8")).get("picks") or []
        lines += ["", "## Picks", ""]
        lines += [f"- #{p['id']} {p.get('company') or '?'}: {p.get('title') or ''} ({p.get('location') or 'location unknown'}, "
                  f"match {p.get('match') if p.get('match') is not None else '-'}{', dream' if p.get('dream') else ''})"
                  for p in picks] or ["- none"]
    lines += ["", "## Needs a human", ""]
    lines += [f"- {n}" for n in needs] or ["- nothing"]
    return "\n".join(lines) + "\n"


def run(ctx: Context) -> StageResult:
    from ... import report as report_mod

    out = html_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report_mod.build_html(db.connect()), encoding="utf-8")
    md = ctx.run_dir / "report.md"
    md.write_text(render_markdown(ctx.ledger), encoding="utf-8")
    if not out.exists() or not md.exists():
        return StageResult({}, "report files missing")
    return StageResult({"html": str(out), "md": md.name})
