"""Stage 5, pick: `src.pick.pick()` under `[pick]` in hunt.toml, written to `picks.json` in
the run folder. An aggregator row (flagged by pick) becomes a `needs_human` item and the next
spare takes its slot (decision 12). No picks at all stops the run after the report."""
from __future__ import annotations

import json
from pathlib import Path

from .base import Context, StageResult


def write_chosen(run_dir: Path, picks: list[dict]) -> Path:
    """`hunt run --ids`: the rows a human chose stand in for this stage, in the same file and
    shape, so research, tailor and the report read them as they read a hunt's own picks."""
    path = run_dir / "picks.json"
    path.write_text(json.dumps({"picks": picks, "flagged": [], "skipped": [], "spares": [], "source": "ids"},
                               indent=1) + "\n", encoding="utf-8")
    return path


def run(ctx: Context) -> StageResult:
    from ... import pick as pick_mod

    n = ctx.cfg.pick_n
    picks, skipped, spares = pick_mod.pick(n, ctx.cfg.pick_dream_slots)
    final: list[dict] = []
    flagged: list[dict] = []
    rest: list[dict] = []
    for p in [*picks, *spares]:
        if len(final) >= n:
            rest.append(p)
        elif p.get("flag"):
            flagged.append(p)
        else:
            final.append(p)
    (ctx.run_dir / "picks.json").write_text(
        json.dumps({"picks": final, "flagged": flagged, "skipped": skipped, "spares": rest}, indent=1) + "\n",
        encoding="utf-8")
    needs_human = [f"pick: #{p['id']} {p.get('company') or '?'}, {p['flag']}" for p in flagged]
    summary = {"picks": len(final), "flagged": len(flagged), "skipped": len(skipped), "spares": len(rest)}
    return StageResult(summary, None, needs_human, stop=not final)
