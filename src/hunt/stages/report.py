"""Stage 8, report: `data/report.html` from `src.report.build_html` and the run's
`report.md` (spec section 7). The stage writes it near the end of a run, so its own row
still says running there; `python -m src.hunt report` renders it again from the finished
ledger, and is how a failed run (whose report stage never ran) gets its report."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ... import db
from ... import research as research_mod
from ...config import ROOT
from ..ledger import Ledger, add_usage, run_state
from .base import Context, StageResult


def html_path() -> Path:
    return db.DB_PATH.parent / "report.html"


_HIDDEN = {"needs_human", "builds", "chunk_rows"}           # rendered in their own sections, or not at all


def _n(value: Any) -> str:
    if value is None:
        return "-"
    return f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"


def _rel(path: Any) -> str:
    try:
        return str(Path(str(path)).resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def _picks(led: Ledger, builds: dict[str, Any]) -> list[str]:
    picks_file = led.run_dir / "picks.json"
    if not picks_file.exists():
        return []
    picks = json.loads(picks_file.read_text(encoding="utf-8")).get("picks") or []
    lines = ["", "## Picks", ""]
    for p in picks:
        score = p.get("match") if p.get("match") is not None else "-"
        lines.append(f"- #{p['id']} {p.get('company') or '?'}: {p.get('title') or ''} ({p.get('location') or 'location unknown'}, "
                     f"match {score}{', dream' if p.get('dream') else ''})")
        info = research_mod.dossier_info(p.get("company") or "")
        state = "missing" if not info["exists"] else f"researched {info['researched']}{', stale' if info['stale'] else ''}"
        lines.append(f"  - dossier: {_rel(info['path'])} ({state})")
        build = builds.get(f"job_{p['id']}")
        if build:
            lines.append(f"  - application: {_rel(build.get('folder') or '-')} ({'build PASS' if build.get('ok') else 'build FAIL'})")
            lines += [f"  - {ln}" for ln in build.get("lines") or []]
        else:
            lines.append("  - application: not tailored in this run")
        if p.get("dream"):
            lines.append(f"  - visa path: {p.get('visa_path') or 'not stated by the matcher'}")
            if build:
                lines.append(f"  - relocation line in the letter: {'present' if build.get('relocation_line') else 'absent'}")
    return lines + ([] if picks else ["- none"])


def _usage(st: dict[str, Any]) -> list[str]:
    lines = ["", "## Usage", "", "| stage | units | attempts | input | output | cache read | cache write | cost usd |",
             "|---|---|---|---|---|---|---|---|"]
    total: dict[str, Any] | None = None
    attempts_all = units_all = 0
    for s in st["stages"]:
        units = [u for u in s.get("units") or [] if u.get("harness")]          # model units only
        if not units:
            continue
        use: dict[str, Any] | None = None
        for u in units:
            use = add_usage(use, u.get("usage"))
        total = add_usage(total, use)
        attempts = sum(int(u.get("attempts") or 0) for u in units)
        attempts_all += attempts
        units_all += len(units)
        use = use or {}
        lines.append(f"| {s['name']} | {len(units)} | {attempts} | {_n(use.get('input'))} | {_n(use.get('output'))} | "
                     f"{_n(use.get('cache_read'))} | {_n(use.get('cache_create'))} | {_n(use.get('cost_usd'))} |")
    if total is None and not units_all:
        return lines[:3] + ["No model unit ran."]
    total = total or {}
    lines.append(f"| total | {units_all} | {attempts_all} | {_n(total.get('input'))} | {_n(total.get('output'))} | "
                 f"{_n(total.get('cache_read'))} | {_n(total.get('cache_create'))} | {_n(total.get('cost_usd'))} |")
    return lines


def render_markdown(led: Ledger) -> str:
    """report.md (spec section 7): what each stage did, the picks with their dossier and
    application paths and each build's RESUME and LETTER lines, the visa path and relocation
    line for dream rows, the needs_human list, usage per stage. Renders any ledger, finished
    or not, which is what `hunt report` does after a failed run."""
    st = led.state
    lines = [f"# Hunt {st['run_id']}", "",
             f"Harness {st.get('harness') or '-'}, started {st.get('started') or '-'}, "
             f"ended {st.get('ended') or '-'}, state {run_state(st)}.", "",
             "## Stages", "", "| stage | state | units | summary |", "|---|---|---|---|"]
    needs: list[str] = []
    details: list[str] = []
    builds: dict[str, Any] = {}
    for s in st["stages"]:
        units = s.get("units") or []
        done = sum(1 for u in units if u.get("state") == "done")
        summ: dict[str, Any] = dict(s.get("summary") or {})
        needs += [str(x) for x in (summ.get("needs_human") or [])]
        if s["name"] == "tailor":
            builds = dict(summ.get("builds") or {})
        text = ", ".join(f"{k} {v}" for k, v in summ.items() if not isinstance(v, (list, dict)) and v is not None)
        note = f" ({s['note']})" if s.get("note") else ""
        lines.append(f"| {s['name']} | {s['state']}{note} | {done}/{len(units)} | {text} |")
        for k, v in summ.items():
            if isinstance(v, list) and v and k not in _HIDDEN:
                details.append(f"- {s['name']} {k}: {'; '.join(str(x) for x in v)}")
        details += [f"- {s['name']} unit {u['id']} failed after {u.get('attempts', 0)} attempt(s): {u.get('verdict')}"
                    for u in units if u.get("state") == "failed"]
    if details:
        lines += ["", "## Details", "", *details]
    lines += _picks(led, builds)
    lines += ["", "## Needs a human", ""]
    lines += [f"- {n}" for n in needs] or ["- nothing"]
    lines += _usage(st)
    return "\n".join(lines).replace("\u2014", ", ") + "\n"


def write_markdown(led: Ledger) -> Path:
    md = led.run_dir / "report.md"
    md.write_text(render_markdown(led), encoding="utf-8")
    return md


def run(ctx: Context) -> StageResult:
    from ... import report as report_mod

    out = html_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report_mod.build_html(db.connect()), encoding="utf-8")
    md = write_markdown(ctx.ledger)
    if not out.exists() or not md.exists():
        return StageResult({}, "report files missing")
    return StageResult({"html": str(out), "md": md.name})
