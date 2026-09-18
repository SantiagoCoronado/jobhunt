"""Stage 7, tailor: `src.tailor_bundle` per pick, one unit per pick on the stage's model (the
strongest writer configured), and `src.tailor_build` as the judge. The unit follows its role
protocol (read the bundle, write `draft.md`, run the build); verify runs the build AGAIN in
Python, so the verdict the ledger records is the orchestrator's, never the agent's word for it.

A build that fails gets the one fix round (`retries = 1`): the next attempt's prompt carries
the build's FAIL lines and says to fix exactly those on the split files. A second failure is
reported with its verdict lines, not retried (decision 18). Each build's metrics (fit, fill,
pages, letter words, the RESUME and LETTER lines) go into the stage summary for the report.

A unit that wrote nothing passes no build: verify refuses a folder with no file newer than
the plan, so a refresh of an older application cannot pass on the old files.
"""
from __future__ import annotations

import contextlib
import json
import re
from pathlib import Path
from typing import Any

from ... import tailor_build, tailor_bundle
from .base import Context, StageResult
from .fan import Planned, failed_verdict, fan_out, rel
from .research import load_picks

NAME = "tailor"
_BOOKKEEPING = {"build.json", "state.json"}
_FILL = re.compile(r"fit level (\d), (\d+)% fill")


def bundle(job_id: int, company: str, log: Path) -> tuple[Path, Path]:
    """(inputs.md, application folder) for one pick; `tailor_bundle` output goes to the log."""
    with open(log, "a", encoding="utf-8") as f, contextlib.redirect_stdout(f):
        tailor_bundle.main([str(job_id)])
    return tailor_bundle.TAILOR_DIR / str(job_id) / "inputs.md", tailor_bundle.application_folder(job_id, company)


def build(folder: Path) -> dict[str, Any]:
    return tailor_build.build(folder).to_dict()


def _mtimes(folder: Path) -> dict[str, float]:
    if not folder.is_dir():
        return {}
    return {p.name: p.stat().st_mtime_ns for p in folder.iterdir() if p.is_file() and p.name not in _BOOKKEEPING}


def verify_build(folder: Path, before: dict[str, float]) -> str | None:
    """Run the build and judge it (registry row 7). None when it passes on one page."""
    if _mtimes(folder) == before:
        return f"the unit wrote nothing in {folder.name}"
    try:
        doc = build(folder)
    except tailor_build.EnvError as e:
        return f"build environment: {e}"[:250]
    if not doc["ok"]:
        return "build FAIL: " + " | ".join(str(f) for f in doc["failures"])[:400]
    pages = doc["metrics"].get("pages")
    if pages not in (None, 1):
        return f"build passed but the resume is {pages} pages"
    return None


def fix_task(folder: Path, cwd: Path, first_task: str) -> str | None:
    """The fix round's task lines, from the build the failed attempt left behind; None (run
    the first prompt again) when the attempt died before any build."""
    path = folder / "build.json"
    if not path.exists():
        return None
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("ok"):
        return None
    lines = "\n".join(f"  {ln}" for ln in doc.get("verdict") or [])
    return (f"{first_task.rstrip()}\n\n"
            f"FIX ROUND. Your draft is already split into files in `{rel(folder, cwd)}` and the build failed:\n{lines}\n"
            f"Do not write a new draft.md. Fix exactly the FAIL lines with Edit on the file each one names, run "
            f"`.venv/bin/python -m src.tailor_build {rel(folder, cwd)}` once, and stop whatever it prints.")


def metrics(folder: Path) -> dict[str, Any]:
    path = folder / "build.json"
    if not path.exists():
        return {"ok": False, "lines": ["no build.json"]}
    doc = json.loads(path.read_text(encoding="utf-8"))
    lines = [str(ln) for ln in doc.get("verdict") or []]
    out: dict[str, Any] = {"ok": bool(doc.get("ok")), "folder": doc.get("folder"),
                           "pages": doc["metrics"].get("pages"), "letter_words": doc["metrics"].get("letter_words"),
                           "warnings": len(doc.get("warnings") or []),
                           "relocation_line": bool(doc["metrics"].get("relocation_line")),
                           "lines": [ln for ln in lines if ln.startswith(("RESUME", "LETTER", "FAIL"))]}
    m = next((m for m in map(_FILL.search, lines) if m), None)
    if m:
        out.update(fit_level=int(m.group(1)), fill_pct=int(m.group(2)))
    return out


def run(ctx: Context) -> StageResult:
    from . import REGISTRY

    picks = load_picks(ctx.run_dir)
    if picks is None:
        return StageResult({}, "no picks.json in this run; tailor needs the pick stage (`--from pick`)")
    if not picks:
        return StageResult({"picks": 0}, skipped="no picks")
    done_before = {u["id"] for u in ctx.ledger.stage(NAME)["units"] if u["state"] == "done"}
    planned: list[Planned] = []
    folders: dict[str, Path] = {}
    for p in picks:
        uid = f"job_{p['id']}"
        if uid in done_before:                        # a resume: the bundle would only restamp the folder
            folders[uid] = tailor_bundle.application_folder(p["id"], p.get("company") or "")
            planned.append(Planned(uid, None, None, "", lambda: None))
            continue
        inputs, folder = bundle(p["id"], p.get("company") or "", ctx.stage_log(NAME, "bundle"))
        folders[uid] = folder
        before = _mtimes(folder)
        task = (f"Task: tailor job #{p['id']}, {p.get('title') or 'untitled'} at {p.get('company') or '?'}. The bundle "
                f"is `{rel(inputs, ctx.cwd)}`; write `{rel(folder / 'draft.md', ctx.cwd)}` and run the build on "
                f"`{rel(folder, ctx.cwd)}`.\n"
                f"Contract: your protocol as written. The orchestrator runs `tailor_build` again after you and that "
                f"verdict is the one that counts: PASS, one page.")
        planned.append(Planned(uid, rel(inputs, ctx.cwd), rel(folder, ctx.cwd), task,
                               lambda f=folder, b=before: verify_build(f, b),          # type: ignore[misc]
                               retry_task=lambda verdict, f=folder, t=task: fix_task(f, ctx.cwd, t)))  # type: ignore[misc]
    outcomes = fan_out(ctx, REGISTRY[NAME], planned)
    builds = {uid: metrics(folder) for uid, folder in folders.items()}
    passed = sum(1 for b in builds.values() if b["ok"])
    summary = {"picks": len(picks), "passed": passed, "failed_units": len(picks) - passed, "builds": builds}
    needs = [f"tailor: {uid} did not pass its build after the fix round: {'; '.join(b['lines'][-2:])}"
             for uid, b in builds.items() if not b["ok"]]
    return StageResult(summary, failed_verdict(NAME, outcomes, len(planned)), needs)
