"""Stage 1, discover: `src.discover.main()` (every enabled, targeted source, then maintain)
with its output in the unit log. Verify: at least one source recorded an ok run since the
stage started; the failed ones are listed in the summary."""
from __future__ import annotations

import contextlib

from ... import db
from ...models import now_iso
from .base import Context, StageResult


def run(ctx: Context) -> StageResult:
    from ... import discover as discover_mod

    started = now_iso()
    with open(ctx.log_path("discover", "discover"), "a", encoding="utf-8") as log, contextlib.redirect_stdout(log):
        discover_mod.main()
    conn = db.connect()
    rows = conn.execute("SELECT source, ok, error, new, seen FROM runs WHERE ts >= ? ORDER BY id", (started,)).fetchall()
    ok = [r["source"] for r in rows if r["ok"]]
    failed = [r["source"] for r in rows if not r["ok"]]
    summary = {"sources_ok": len(ok), "sources_failed": len(failed), "new": sum(r["new"] for r in rows),
               "seen": sum(r["seen"] for r in rows), "failed": failed}
    if ok:
        return StageResult(summary)
    why = ", ".join(failed) if failed else "none enabled or targeted"
    return StageResult(summary, f"no source succeeded: {why}")
