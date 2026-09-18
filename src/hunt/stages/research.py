"""Stage 6, research: one unit per pick whose dossier `src.research.dossier_info` says is
missing or stale, on a harness that grants `web` (the stage's own, else the first configured
one that does; the substitution is logged). Verify: the dossier exists, carries today's
`researched: YYYY-MM-DD` line and a Sources section, and has zero em-dashes. No ingest: the
dossier is the output, and the tailor stage reads it through `tailor_bundle`.

Picks come from `picks.json` in the run folder (the pick stage wrote it).
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from ... import research as research_mod
from .base import Context, StageResult
from .fan import NoCapableHarness, Planned, failed_verdict, fan_out, rel

NAME = "research"
_SOURCES = re.compile(r"^#+\s*(\d+\.\s*)?\**sources\b", re.I | re.M)
_RESEARCHED = re.compile(r"researched:\s*(\d{4}-\d{2}-\d{2})")


def load_picks(run_dir: Path) -> list[dict[str, Any]] | None:
    path = run_dir / "picks.json"
    if not path.exists():
        return None
    return list(json.loads(path.read_text(encoding="utf-8")).get("picks") or [])


def verify_dossier(path: Path, today: str) -> str | None:
    if not path.exists():
        return f"no dossier at {path.name}"
    text = path.read_text(encoding="utf-8", errors="replace")
    stamps = _RESEARCHED.findall(text)
    if not stamps:
        return f"{path.name} has no `researched: YYYY-MM-DD` line"
    if today not in stamps:
        return f"{path.name} says researched {stamps[-1]}, not today ({today}): the dossier was not refreshed"
    if not _SOURCES.search(text):
        return f"{path.name} has no Sources section"
    dashes = text.count("\u2014")
    if dashes:
        return f"{path.name} has {dashes} em-dash(es); the rule is zero"
    return None


def run(ctx: Context) -> StageResult:
    from . import REGISTRY

    picks = load_picks(ctx.run_dir)
    if picks is None:
        return StageResult({}, "no picks.json in this run; research needs the pick stage (`--from pick`)")
    today = date.today().isoformat()
    planned: list[Planned] = []
    fresh: list[str] = []
    for p in picks:
        company = p.get("company") or ""
        slug = research_mod.company_slug(company)
        if not slug or any(u.id == slug for u in planned):
            continue
        info = research_mod.dossier_info(company)
        if info["exists"] and not info["stale"] and not _planned_before(ctx, slug):
            fresh.append(slug)
            continue
        path: Path = info["path"]
        why = "refresh the stale dossier" if info["exists"] else "write the dossier"
        task = (f"Task: research {company} and {why} at `{rel(path, ctx.cwd)}`. Today is {today}. The role that "
                f"prompted this is job #{p['id']}, {p.get('title') or 'untitled'}; "
                f"`python -m src.query job {p['id']}` prints its description.\n"
                f"Contract: every section of your dossier format, a Sources section, the line "
                f"`researched: {today}`, zero em-dashes.")
        planned.append(Planned(slug, f"job #{p['id']}", rel(path, ctx.cwd), task,
                               lambda path=path: verify_dossier(path, today)))   # type: ignore[misc]
    summary: dict[str, Any] = {"picks": len(picks), "fresh": len(fresh), "units": len(planned)}
    if not planned:
        return StageResult(summary, skipped="every pick has a fresh dossier" if picks else "no picks")
    try:
        outcomes = fan_out(ctx, REGISTRY[NAME], planned)
    except NoCapableHarness as e:
        return StageResult(summary, str(e))
    done = [u for u in ctx.ledger.stage(NAME)["units"] if u["state"] == "done"]
    summary.update(written=len(done), failed_units=len(planned) - len(done), harness=done[0]["harness"] if done else None)
    return StageResult(summary, failed_verdict(NAME, outcomes, len(planned)))


def _planned_before(ctx: Context, slug: str) -> bool:
    """On a resume a dossier this run already wrote is fresh; keep its unit in the plan so the
    ledger's done verdict, not the file's date, is what skips it."""
    return any(u["id"] == slug for u in ctx.ledger.stage(NAME)["units"])
