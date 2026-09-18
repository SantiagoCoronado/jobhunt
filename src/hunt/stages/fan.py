"""What every fanned stage shares (spec section 4, "Unit prompt"): a stage plans `Planned`
units, `fan_out` writes each unit's prompt to `prompts/<stage>/<unit>.md` (role body, task
lines, reply cap) so a failed unit can be re-run by hand on any harness, records the units in
the ledger with the harness and model that will run them, and hands them to the pool.

Units the ledger already holds as done are skipped, which is what `--resume` relies on. The
agent's reply is never read here; a unit is done when its `verify` says so (decision 4).
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .. import prompts
from ..harness import Invocation
from ..pool import Outcome, UnitSpec
from .base import Context, Stage

REPLY_CAP = "Reply with one line. Your reply is not read; the output file is."


@dataclass(frozen=True)
class Planned:
    id: str
    input: str | None                     # shown in the ledger, relative to the repo when inside it
    output: str | None
    task: str                             # the task lines: input file, output file, contract
    verify: Callable[[], str | None]      # None when the output passes, else why it did not
    schema: dict[str, Any] | None = None


def rel(path: Path, cwd: Path) -> str:
    """A path as the prompt and the ledger name it: relative to the working directory when
    it is inside it (what an agent started there can open), absolute otherwise."""
    try:
        return str(path.resolve().relative_to(cwd.resolve()))
    except ValueError:
        return str(path)


def fan_out(ctx: Context, stage: Stage, planned: Sequence[Planned]) -> list[Outcome]:
    """Run the planned units of one stage; one Outcome per unit that ran (done units already
    in the ledger are not run again and yield no Outcome)."""
    assert stage.role is not None
    name = stage.name
    scfg = ctx.cfg.stage(name)
    hname = scfg.harness or ctx.harness
    harness = ctx.get_harness(hname)
    role = prompts.load_roles()[stage.role]
    known = {u["id"]: u for u in ctx.ledger.stage(name)["units"]}
    fresh = [p for p in planned if p.id not in known]
    if fresh:
        ctx.ledger.add_units(name, [{"id": p.id, "input": p.input, "output": p.output, "harness": hname,
                                     "model": scfg.model} for p in fresh])
    specs: list[UnitSpec] = []
    prompt_dir = ctx.run_dir / "prompts" / name
    prompt_dir.mkdir(parents=True, exist_ok=True)
    for p in planned:
        if known.get(p.id, {}).get("state") == "done":
            continue
        user = f"{p.task.rstrip()}\n{REPLY_CAP}\n"
        (prompt_dir / f"{p.id}.md").write_text(f"{role.body.rstrip()}\n\n{user}", encoding="utf-8")
        inv = Invocation(prompt=user, system=role.body, model=scfg.model, tools=stage.tools, cwd=ctx.cwd,
                         timeout_s=scfg.timeout_s, schema=p.schema)
        specs.append(UnitSpec(name, p.id, inv, p.verify))
    return ctx.pool(harness).run_stage(name, specs, scfg.concurrency, scfg.attempts)


def failed_verdict(stage: str, outcomes: Sequence[Outcome], total: int) -> str | None:
    """The stage verdict when any unit ran out of attempts: how many, and the first reason."""
    failed = [o for o in outcomes if o.state == "failed"]
    if not failed:
        return None
    first = failed[0]
    return (f"{len(failed)} of {total} {stage} unit(s) failed after their retries, first {first.id}: "
            f"{first.verdict}; `hunt run --resume` runs only those again")[:300]
