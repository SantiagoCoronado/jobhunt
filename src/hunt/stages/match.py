"""Stage 3, match: `src.match.export --min-bucket --chunk` under the stage's unit budget, one
unit per chunk on the stage's model, per-unit verify (every input id scored once, `score` an
int 0..100, `reasons` a string), then `src.match.ingest(scores_dir=...)`.

Two passes, each its own unit group in the ledger (`p1_chunk_NNN`, `p2_chunk_NNN`): pass 1 at
`min_bucket`, and when it left room under `budget_units`, pass 2 at `second_pass_min_bucket`.
Pass 1 is ingested BEFORE pass 2 exports, because `match.export` wipes every `scores_*.json`.
For the same reason a resume never exports a pass whose units are already in the ledger, and
pass 2 is not planned while pass 1 has a failed unit (its export would erase the evidence).

A unit that runs out of attempts has its scores file moved aside so ingest never reads it;
the verified chunks are ingested either way. Em-dashes in a `reasons` string are replaced
here (a comma) rather than costing a whole chunk another run on the matcher's model.
Dream-company rows get their own summary keys and their own line in the run output.
"""
from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import Any

from ... import match as match_mod
from ...dream import is_dream
from .base import Context, StageResult
from .fan import Planned, chunks_changed, failed_verdict, fan_out, rel

NAME = "match"
EM_DASH = "\u2014"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_scores(chunk: Path, out: Path) -> str | None:
    """Coverage check for one chunk (registry row 3). None when the scores file passes."""
    want = [r["id"] for r in _load(chunk)]
    if not out.exists():
        return f"no output file {out.name}"
    try:
        data = _load(out)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return f"{out.name} is not valid JSON: {e}"[:200]
    if not isinstance(data, list) or not all(isinstance(d, dict) for d in data):
        return f"{out.name} must be a JSON array of objects"
    got = [d.get("id") for d in data]
    missing = [i for i in want if i not in set(got)]
    if missing:
        return (f"short file: {len(set(got) & set(want))} of {len(want)} ids scored, missing "
                f"{', '.join(str(i) for i in missing[:5])}{' ...' if len(missing) > 5 else ''}")
    extra = sorted({i for i in got if i not in set(want)}, key=str)
    if extra:
        return f"ids that are not in {chunk.name}: {', '.join(str(i) for i in extra[:5])}"
    if len(got) != len(set(got)):
        return f"an id appears twice in {out.name}"
    for d in data:
        score = d.get("score")
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
            return f"id {d.get('id')}: score must be an integer 0..100, got {score!r}"
        if not isinstance(d.get("reasons"), str):
            return f"id {d.get('id')}: reasons must be a string"
    return None


def _no_dash(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace(f" {EM_DASH} ", ", ").replace(EM_DASH, ", ")
    if isinstance(value, list):
        return [_no_dash(v) for v in value]
    if isinstance(value, dict):
        return {k: _no_dash(v) for k, v in value.items()}
    return value


def scrub(out: Path) -> None:
    """On the parsed data: a JSON writer may have escaped the dash, so the raw text can hide it."""
    data = _load(out)
    clean = _no_dash(data)
    if clean != data:
        out.write_text(json.dumps(clean, indent=1, ensure_ascii=False), encoding="utf-8")


def _chunk_of(unit_id: str) -> Path:
    return match_mod.MATCH_DIR / f"{unit_id.split('_', 1)[1]}.json"


def _scores_for(chunk: Path) -> Path:
    return chunk.with_name(chunk.name.replace("chunk_", "scores_", 1))


def plan(ctx: Context, pass_no: int, chunks: list[Path]) -> list[Planned]:
    planned = []
    for chunk in chunks:
        out = _scores_for(chunk)
        task = (f"Task: score the {len(_load(chunk))} jobs in `{rel(chunk, ctx.cwd)}` against `config/profile.yaml` "
                f"and write `{rel(out, ctx.cwd)}`.\n"
                f"Contract: a JSON array, one object per input id, every id exactly once, `score` an integer 0 to "
                f"100, the fields of your output format. Do not run `src.match ingest` and do not print a table: "
                f"the orchestrator ingests the file.")
        planned.append(Planned(f"p{pass_no}_{chunk.stem}", rel(chunk, ctx.cwd), rel(out, ctx.cwd), task,
                               lambda c=chunk, o=out: verify_scores(c, o)))   # type: ignore[misc]
    return planned


def _export(ctx: Context, pass_no: int, min_bucket: int, max_units: int, chunk: int) -> None:
    with open(ctx.stage_log(NAME, f"export_p{pass_no}"), "a", encoding="utf-8") as log, contextlib.redirect_stdout(log):
        match_mod.export(max_units * chunk, min_bucket, chunk)


def _run_pass(ctx: Context, pass_no: int, totals: dict[str, Any]) -> tuple[int, str | None]:
    """Fan one pass out over the chunk files on disk, ingest what verified. Returns the
    number of units in the pass and the verdict when any of them failed."""
    from . import REGISTRY

    chunks = sorted(match_mod.MATCH_DIR.glob("chunk_*.json"))
    if not chunks:
        return 0, None
    planned = plan(ctx, pass_no, chunks)
    rows = {p.id: len(_load(_chunk_of(p.id))) for p in planned}
    known = dict(ctx.ledger.stage(NAME)["summary"].get("chunk_rows") or {})
    recorded = {k: v for k, v in known.items() if k.startswith(f"p{pass_no}_")}
    if recorded:                                      # a resume: these files are the pass's inputs
        changed = chunks_changed(recorded, rows, "data/match")
        if changed:
            return len(recorded), changed
    ctx.ledger.set_summary(NAME, chunk_rows={**known, **rows})
    outcomes = fan_out(ctx, REGISTRY[NAME], planned)
    for o in outcomes:
        out = _scores_for(_chunk_of(o.id))
        if o.state == "failed" and out.exists():
            out.replace(out.with_name(out.name + ".failed"))
    good = [_scores_for(_chunk_of(p.id)) for p in planned if ctx.ledger.unit(NAME, p.id)["state"] == "done"]
    if good:
        for out in good:
            scrub(out)
        with open(ctx.stage_log(NAME, f"ingest_p{pass_no}"), "a", encoding="utf-8") as log, contextlib.redirect_stdout(log):
            match_mod.ingest(scores_dir=str(match_mod.MATCH_DIR))
        _tally(good, totals)
    totals["failed_units"] += len(planned) - len(good)
    return len(planned), failed_verdict(NAME, outcomes, len(planned))


def _tally(outs: list[Path], totals: dict[str, Any]) -> None:
    """What the pass did, read back from the DB after ingest (ingest owns the cutoffs)."""
    conn = match_mod.connect()
    for out in outs:
        for d in _load(out):
            row = conn.execute("SELECT company, status, match_score FROM jobs WHERE id=?", (d["id"],)).fetchone()
            if row is None:
                continue
            short = row["status"] == "shortlisted"
            totals["scored"] += 1
            totals["shortlisted"] += int(short)
            if is_dream(row["company"]):
                totals["dream_scored"] += 1
                totals["dream_shortlisted"] += int(short)
                totals["dream_rows"].append(f"#{d['id']} {row['company']} {row['match_score']}"
                                            f"{' shortlisted' if short else ''}")


def run(ctx: Context) -> StageResult:
    scfg = ctx.cfg.stage(NAME)
    chunk, budget = scfg.option("chunk"), scfg.option("budget_units")
    second = scfg.option("second_pass_min_bucket")
    units = [u["id"] for u in ctx.ledger.stage(NAME)["units"]]
    in_p2 = any(u.startswith("p2_") for u in units)
    totals: dict[str, Any] = {"scored": 0, "shortlisted": 0, "dream_scored": 0, "dream_shortlisted": 0,
                              "failed_units": 0, "dream_rows": []}
    if budget <= 0:
        return StageResult({}, skipped="budget_units is 0")
    n1 = sum(1 for u in units if u.startswith("p1_"))
    verdict = None
    if in_p2:                                         # a resume inside pass 2: pass 1 was ingested, its files are gone
        totals.update(ctx.ledger.stage(NAME)["summary"].get("pass1_totals") or {})
    else:
        if not units:                                 # decision 9: a resume never exports again
            _export(ctx, 1, scfg.option("min_bucket"), budget, chunk)
        n1, verdict = _run_pass(ctx, 1, totals)
        ctx.ledger.set_summary(NAME, pass1_totals={k: (list(v) if isinstance(v, list) else v) for k, v in totals.items()})
    n2 = 0
    if verdict is None and (in_p2 or (second > 0 and second < scfg.option("min_bucket") and n1 < budget)):
        if not in_p2:
            _export(ctx, 2, second, budget - n1, chunk)
        n2, verdict = _run_pass(ctx, 2, totals)
    dream_rows = totals.pop("dream_rows")
    summary = {"units": n1 + n2, "pass1_units": n1, "pass2_units": n2, **totals}
    if dream_rows:
        summary["dream_rows"] = dream_rows
        ctx.emit(f"match dream: {totals['dream_scored']} scored, {totals['dream_shortlisted']} shortlisted: "
                 f"{'; '.join(dream_rows)}")
    if not n1 and not n2:
        return StageResult(summary, skipped="nothing to score")
    return StageResult(summary, verdict)
