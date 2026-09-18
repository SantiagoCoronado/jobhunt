"""`python -m src.hunt ...` (spec section 8).

    run      [--harness NAME] [--from STAGE] [--to STAGE] [--only STAGE] [--skip STAGE ...]
             [--resume RUN|latest] [--dry-run] [--quiet]
    status   [RUN|latest]
    report   [RUN|latest]
    runs
    models   [--harness NAME] [--grep TEXT]
    doctor   [--harness NAME]
    sync-agents [--check]

Exit codes: 0 ok; 1 nothing to show (no run yet); 2 a failed stage, a bad config or a command
this build does not carry yet; 3 the pick stage found nothing to tailor. Every line printed is
plain text the TUI can tail. Zero em-dashes.
"""
from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from . import config as hunt_config
from . import ledger
from .config import STAGES

def select_stages(from_: str | None = None, to: str | None = None, only: str | None = None,
                  skip: Sequence[str] = ()) -> list[str]:
    """The contiguous slice of the fixed stage order a run covers. `--only` is one stage,
    `--from/--to` a range (inclusive), `--skip` removes stages from whatever is selected."""
    for name in [from_, to, only, *skip]:
        if name is not None and name not in STAGES:
            raise ValueError(f"unknown stage '{name}' (known: {', '.join(STAGES)})")
    if only and (from_ or to):
        raise ValueError("--only cannot be combined with --from or --to")
    if only:
        chosen = [only]
    else:
        start = STAGES.index(from_) if from_ else 0
        end = STAGES.index(to) if to else len(STAGES) - 1
        if start > end:
            raise ValueError(f"--from {from_} comes after --to {to} in the stage order")
        chosen = list(STAGES[start:end + 1])
    return [s for s in chosen if s not in set(skip)]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m src.hunt", description="The hunt orchestrator.")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="run the hunt, or a slice of its stages")
    run.add_argument("--harness", help="harness for this run (default: hunt.toml [harness].default)")
    run.add_argument("--from", dest="from_", choices=STAGES, metavar="STAGE")
    run.add_argument("--to", choices=STAGES, metavar="STAGE")
    run.add_argument("--only", choices=STAGES, metavar="STAGE")
    run.add_argument("--skip", action="append", default=[], choices=STAGES, metavar="STAGE")
    run.add_argument("--resume", metavar="RUN", help="re-enter a run: RUN id or `latest`")
    run.add_argument("--dry-run", action="store_true", help="plan, write prompts, run nothing")
    run.add_argument("--quiet", action="store_true")

    for name, help_ in (("status", "render a run's ledger as a tree"), ("report", "write and print report.md")):
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("run", nargs="?", default="latest", metavar="RUN")

    sub.add_parser("runs", help="list run folders with state and started time")
    models = sub.add_parser("models", help="the harness's live model catalog")
    models.add_argument("--harness")
    models.add_argument("--grep")
    doctor = sub.add_parser("doctor", help="check the harness, the catalog and every stage's model")
    doctor.add_argument("--harness")
    sync = sub.add_parser("sync-agents", help="generate every harness's native agent files")
    sync.add_argument("--check", action="store_true")
    return p


# commands this build does not carry yet and where they land (docs/spec-hunt-orchestrator.md section 12)
_LANDS_IN = {"report": "PR 3, feat/hunt-fanout story 6"}


def _not_yet(cmd: str) -> int:
    print(f"hunt {cmd}: lands in {_LANDS_IN[cmd]} (docs/spec-hunt-orchestrator.md section 12)", file=sys.stderr)
    return 2


def cmd_runs() -> int:
    runs = ledger.list_runs(ledger.HUNT_DIR)
    if not runs:
        print(f"no runs yet under {ledger.HUNT_DIR}")
        return 0
    print(ledger.format_runs(runs))
    return 0


def cmd_status(run: str) -> int:
    path = ledger.resolve(run, ledger.HUNT_DIR)
    if path is None:
        what = "no runs yet" if run in ("latest", "") else f"no run '{run}'"
        print(f"{what} under {ledger.HUNT_DIR}")
        return 1
    try:
        state = ledger.load_state(path)
    except (FileNotFoundError, ValueError) as e:
        print(f"{path.name}: unreadable ledger ({e})")
        return 2
    print(ledger.render_status(state, path))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    try:
        cfg = hunt_config.load()
        stages = select_stages(args.from_, args.to, args.only, args.skip)
    except ValueError as e:
        print(f"hunt run: {e}", file=sys.stderr)
        return 2
    harness = args.harness or cfg.harness
    if args.dry_run:
        print(f"dry run: {len(stages)} stage(s) on {harness}, config {cfg.source or 'defaults'}")
        for name in stages:
            s = cfg.stage(name)
            if s.fanned:
                model = s.model or "harness default"
                print(f"  {name:<9} fanned  {s.harness or harness}  {model}  "
                      f"x{s.concurrency} {s.timeout_s}s {s.attempts} attempts")
            else:
                print(f"  {name:<9} python")
        print("units are planned by the stage modules (later stories); nothing ran")
        return 0
    from . import run as run_mod

    def say(line: str) -> None:
        if not args.quiet or line.startswith("run ") or " failed" in line or "hunt run:" in line:
            print(line, flush=True)
    return run_mod.run(cfg, stages, harness, emit=say, resume=args.resume)


def cmd_models(harness_name: str | None, grep: str | None) -> int:
    from . import doctor as doctor_mod
    from . import harness as harness_mod
    try:
        cfg = hunt_config.load()
        h = harness_mod.get(harness_name or cfg.harness)
    except ValueError as e:
        print(f"hunt models: {e}", file=sys.stderr)
        return 2
    models, reason = doctor_mod.catalog(h)
    aliases = h.aliases() if hasattr(h, "aliases") else None
    print(doctor_mod.render_models(h.name, models, reason, grep, aliases))
    return 0


def cmd_doctor(harness_name: str | None) -> int:
    from . import doctor as doctor_mod
    try:
        cfg = hunt_config.load()
    except ValueError as e:
        print(f"hunt doctor: {e}", file=sys.stderr)
        return 2
    checks, rc = doctor_mod.doctor(cfg, harness_name)
    print(doctor_mod.render(harness_name or cfg.harness, checks, rc))
    return rc


def cmd_sync_agents(check: bool) -> int:
    from . import prompts
    try:
        cfg = hunt_config.load()
        changed, same = prompts.sync(cfg, check=check)
    except ValueError as e:
        print(f"hunt sync-agents: {e}", file=sys.stderr)
        return 2
    if check:
        if changed:
            print("out of sync (run `python -m src.hunt sync-agents`): " + ", ".join(changed))
            return 1
        print(f"agents in sync ({len(same)} files)")
        return 0
    for rel in changed:
        print(f"wrote    {rel}")
    print(f"{len(changed)} written, {len(same)} unchanged")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "runs":
        return cmd_runs()
    if args.cmd == "status":
        return cmd_status(args.run)
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "models":
        return cmd_models(args.harness, args.grep)
    if args.cmd == "doctor":
        return cmd_doctor(args.harness)
    if args.cmd == "sync-agents":
        return cmd_sync_agents(args.check)
    return _not_yet(args.cmd)


if __name__ == "__main__":
    sys.exit(main())
