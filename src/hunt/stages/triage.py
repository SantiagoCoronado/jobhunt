"""Stage 2, triage: `src.triage.export` into 100-row chunks, one unit per chunk on the
stage's model, per-unit coverage verify (every input id exactly once, `keep` a real bool,
`bucket` 0..3 on keepers; a short file is a failed attempt and the pool runs it again), then
`src.triage.ingest`. Skipped when the untriaged pile is under `min_pile`.

A unit that runs out of attempts has its out file moved aside (`out_NNN.json.failed`), so
ingest, which coerces anything that is not a clear keep into a drop, never sees a file that
did not pass. The verified chunks are ingested even when another chunk failed: the work is
kept, the stage is failed, and `--resume` runs only the failed chunks.
"""
from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import Any

from ... import config as app_config
from ... import triage as triage_mod
from .base import Context, StageResult
from .fan import Planned, failed_verdict, fan_out, rel

NAME = "triage"


def pile() -> int:
    """The rows `triage.export` would write: untriaged, unscored, discovered, one per role."""
    row = triage_mod.connect().execute(
        "SELECT COUNT(*) FROM canonical_jobs WHERE status='discovered' AND match_score IS NULL "
        "AND match_verdict IS NULL").fetchone()
    return int(row[0])


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_out(chunk: Path, out: Path) -> str | None:
    """Coverage check for one chunk (registry row 2). None when the out file passes."""
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
        return (f"short file: {len(set(got) & set(want))} of {len(want)} ids, missing "
                f"{', '.join(str(i) for i in missing[:5])}{' ...' if len(missing) > 5 else ''}")
    extra = sorted({i for i in got if i not in set(want)}, key=str)
    if extra:
        return f"ids that are not in {chunk.name}: {', '.join(str(i) for i in extra[:5])}"
    if len(got) != len(set(got)):
        return f"an id appears twice in {out.name}"
    for d in data:
        if not isinstance(d.get("keep"), bool):
            return f"id {d.get('id')}: keep must be true or false, got {d.get('keep')!r}"
        bucket = d.get("bucket")
        ok = isinstance(bucket, int) and not isinstance(bucket, bool) and 0 <= bucket <= 3
        if not ok and (d["keep"] or bucket is not None):          # a drop may leave the bucket out
            return f"id {d.get('id')}: bucket must be 0..3, got {bucket!r}"
    return None


def _out_for(chunk: Path) -> Path:
    return chunk.with_name(chunk.name.replace("chunk_", "out_", 1))


def plan(ctx: Context, chunks: list[Path]) -> list[Planned]:
    candidate = app_config.candidate_text()
    planned = []
    for chunk in chunks:
        out = _out_for(chunk)
        rows = len(_load(chunk))
        task = (f"{candidate}\n\n"
                f"Task: triage the {rows} jobs in `{rel(chunk, ctx.cwd)}` and write `{rel(out, ctx.cwd)}`.\n"
                f"Contract: a JSON array with every input id exactly once, `keep` true or false, a `reason` "
                f"of 8 words or fewer, `bucket` 0 to 3.")
        planned.append(Planned(chunk.stem, rel(chunk, ctx.cwd), rel(out, ctx.cwd), task,
                               lambda c=chunk, o=out: verify_out(c, o)))   # type: ignore[misc]
    return planned


def tally(outs: list[Path]) -> dict[str, int]:
    kept = dropped = 0
    buckets = [0, 0, 0, 0]
    for out in outs:
        for d in _load(out):
            if d["keep"]:
                kept += 1
                buckets[d["bucket"]] += 1
            else:
                dropped += 1
    return {"kept": kept, "dropped": dropped, **{f"b{i}": buckets[i] for i in (3, 2, 1, 0)}}


def run(ctx: Context) -> StageResult:
    from . import REGISTRY

    scfg = ctx.cfg.stage(NAME)
    resumed = bool(ctx.ledger.stage(NAME)["units"])
    if not resumed:                                   # decision 9: a resume never exports again
        n = pile()
        if n < scfg.option("min_pile"):
            return StageResult({"pile": n}, skipped=f"pile {n} is under min_pile {scfg.option('min_pile')}")
        with open(ctx.stage_log(NAME, "export"), "a", encoding="utf-8") as log, contextlib.redirect_stdout(log):
            triage_mod.export(scfg.option("chunk"), None)
    chunks = sorted(triage_mod.TRIAGE_DIR.glob("chunk_*.json"))
    if not chunks:
        return StageResult({"pile": 0}, skipped="nothing to triage")
    planned = plan(ctx, chunks)
    ctx.ledger.set_summary(NAME, units=len(planned), rows=sum(len(_load(c)) for c in chunks),
                           chunk_rows={c.stem: len(_load(c)) for c in chunks})
    outcomes = fan_out(ctx, REGISTRY[NAME], planned)
    for o in outcomes:
        out = _out_for(triage_mod.TRIAGE_DIR / f"{o.id}.json")
        if o.state == "failed" and out.exists():
            out.replace(out.with_name(out.name + ".failed"))
    good = [_out_for(c) for c in chunks if ctx.ledger.unit(NAME, c.stem)["state"] == "done"]
    summary: dict[str, Any] = {"failed_units": len(chunks) - len(good), **tally(good)}
    if good:
        with open(ctx.stage_log(NAME, "ingest"), "a", encoding="utf-8") as log, contextlib.redirect_stdout(log):
            triage_mod.ingest()
    return StageResult(summary, failed_verdict(NAME, outcomes, len(chunks)))
