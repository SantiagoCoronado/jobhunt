"""Per-application state file (spec: docs/spec-tailor-lean.md, "Extension points").

`<folder>/state.json` = {"job_id", "stages": {"bundled": ts, "drafted": ts, "built": ts,
"reviewed": ts, "fixed": ts}, "last_verdict_ok": bool}. Any orchestrator reads this to
know what is next instead of re-running a stage.
"""
from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path

STATE_FILE = "state.json"


def read_state(folder: Path) -> dict:
    p = Path(folder) / STATE_FILE
    if not p.exists():
        return {"job_id": None, "stages": {}, "last_verdict_ok": None}
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return {"job_id": None, "stages": {}, "last_verdict_ok": None}
    doc.setdefault("stages", {})
    doc.setdefault("last_verdict_ok", None)
    doc.setdefault("job_id", None)
    return doc


def update_state(folder: Path, stage: str, job_id: int | None = None, ok: bool | None = None) -> dict:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    doc = read_state(folder)
    if job_id is not None:
        doc["job_id"] = job_id
    doc["stages"][stage] = datetime.now(UTC).isoformat(timespec="seconds")
    if ok is not None:
        doc["last_verdict_ok"] = ok
    (folder / STATE_FILE).write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return doc
