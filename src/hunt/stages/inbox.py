"""Stage 4, inbox: `src.mail_fetch run` (read-only IMAP sweep), the whole printed manifest in
the prompt, one unit on the stage's model whose tools are read plus python-only bash (for
`python -m src.mail_fetch show`), and a JSON schema for its reply. The unit has no write
tool: the reply IS the proposals, and the orchestrator writes `data/gmail_pull.json`.

Verify is the applier's own dry run (`gmail_pull.resolve_manifest` + `plan`): a stale sweep
stamp, a reply that is not the schema, or a manifest line with no proposal fails the attempt.
Ingest is the apply (decision 13: the applier is the only thing that writes the DB, and its
guardrails are the gate). Whatever needs the candidate goes to `needs_human` (decision 12):
lines the classifier marked, the applier's ambiguous pile and the lines it skipped.

Skipped cleanly when no mail account is configured, and when the sweep finds no thread.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from typing import Any

from ... import gmail_pull, mail_fetch
from ..harness import Result
from .base import Context, StageResult
from .fan import Planned, failed_verdict, fan_out, rel

NAME = "inbox"
UNIT = "inbox"
SIGNALS = ("rejection", "interview_invite", "assessment", "offer", "reply", "ignore", "ambiguous")
SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False, "required": ["proposals"],
    "properties": {"proposals": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["manifest_id", "sweep", "signal", "proposed_status"],
        "properties": {
            "manifest_id": {"type": "integer"}, "sweep": {"type": "string"},
            "signal": {"type": "string", "enum": list(SIGNALS)},
            "proposed_status": {"type": ["string", "null"], "enum": [*sorted(gmail_pull.ALLOWED_TARGETS), None]},
            "job_id": {"type": "integer"}, "needs_human": {"type": "string"},
        }}}},
}


def proposals_path() -> Path:
    return mail_fetch.DATA_DIR / "gmail_pull.json"


def fetch() -> str:
    """One sweep, the whole manifest on one page; what it prints is what the unit reads."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        mail_fetch.main(["run", "--page-size", "100000"])
    return buf.getvalue()


def _proposals(res: Result) -> list[dict[str, Any]] | None:
    data = res.structured
    if data is None and res.text:
        text = res.text.strip()
        if text.startswith("```"):
            text = text.strip("`").removeprefix("json").strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None
    rows = data.get("proposals") if isinstance(data, dict) else data
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        return None
    return rows


def write_reply(res: Result) -> None:
    """The reply becomes the proposals file; a reply that is not the schema leaves none, so
    verify fails the attempt and an older file is never mistaken for this run's."""
    path = proposals_path()
    path.unlink(missing_ok=True)
    rows = _proposals(res)
    if rows is not None:
        path.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def dry_run(conn: Any = None) -> tuple[dict[str, Any] | None, list[dict[str, Any]], str | None]:
    """(plan, proposals, why it failed). The applier's validation, nothing written. Verify
    calls it on a pool thread, so it opens its own connection there (SQLite's are per thread)."""
    path = proposals_path()
    if not path.exists():
        return None, [], "the reply was not the proposals object the schema describes"
    rows = json.loads(path.read_text(encoding="utf-8"))
    threads = {t["id"] for t in mail_fetch.load_result(mail_fetch.INBOX_PATH).get("threads") or []}
    cited = {r.get("manifest_id") for r in rows}
    missing = sorted(threads - cited)
    if missing:
        return None, rows, (f"{len(missing)} of {len(threads)} manifest lines have no proposal: "
                            f"{', '.join(str(i) for i in missing[:8])}{' ...' if len(missing) > 8 else ''}")
    try:
        resolved = gmail_pull.resolve_manifest([{k: v for k, v in r.items() if k != "needs_human"} for r in rows],
                                               mail_fetch.INBOX_PATH)
    except SystemExit as e:
        return None, rows, str(e)[:250]
    return gmail_pull.plan(conn if conn is not None else gmail_pull.connect(), resolved), rows, None


def run(ctx: Context) -> StageResult:
    from . import REGISTRY

    accounts = [a for a in mail_fetch.mail_accounts() if a.password]
    if not accounts:
        return StageResult({}, skipped="no mail account configured (docs/mail-setup.md)")
    units = ctx.ledger.stage(NAME)["units"]
    classified = bool(units) and units[0]["state"] == "done"      # a resume after the unit: same sweep, no new fetch
    manifest = "" if classified else fetch()
    with open(ctx.stage_log(NAME, "fetch"), "a", encoding="utf-8") as log:
        log.write(manifest)
    doc = mail_fetch.load_result(mail_fetch.INBOX_PATH)
    threads = len(doc.get("threads") or [])
    ctx.ledger.set_summary(NAME, accounts=len(accounts), threads=threads)
    failed_boxes = [f"inbox: mailbox {a['label']} {a['status']}" for a in doc.get("accounts") or [] if a.get("status") != "ok"]
    if not threads:
        return StageResult({}, needs_human=failed_boxes, skipped="no new mail on the open applications")
    out = proposals_path()
    task = (f"{manifest.rstrip()}\n\n"
            f"Task: classify every line of the manifest above, {threads} in all, sweep `{doc.get('generated_at')}`. "
            f"Your reply is the output (`{rel(out, ctx.cwd)}` is written from it).\n"
            f"Contract: {{\"proposals\": [...]}}, one proposal per manifest line, every line id present, the sweep "
            f"stamp on each, `signal` one of {', '.join(SIGNALS)}.")
    unit = Planned(UNIT, rel(mail_fetch.INBOX_PATH, ctx.cwd), rel(out, ctx.cwd), task,
                   lambda: dry_run()[2], SCHEMA, write_reply)
    outcomes = fan_out(ctx, REGISTRY[NAME], [unit])
    verdict = failed_verdict(NAME, outcomes, 1)
    if verdict:
        return StageResult({}, verdict, failed_boxes)
    conn = gmail_pull.connect()
    plan, rows, why = dry_run(conn)
    if plan is None:                                   # a resume whose proposals file is gone
        return StageResult({}, why, failed_boxes)
    with open(ctx.stage_log(NAME, "apply"), "a", encoding="utf-8") as log:
        for c in plan["changes"]:
            log.write(f"#{c['id']} {c['company']}: {c['from_status']} -> {c['to_status']}\n")
        for t in plan["touches"]:
            log.write(f"#{t['id']} {t['company']}: last_contact_at -> {t['contact_date']}\n")
        for line in gmail_pull.apply_changes(conn, plan):
            log.write(line + "\n")
        seen = gmail_pull.record_seen(plan["seen_batch"], mail_fetch.STATE_PATH)
        log.write(f"{seen} ids recorded as seen\n")
    needs = list(failed_boxes)
    needs += [f"inbox: line {r.get('manifest_id')}: {r['needs_human']}" for r in rows if r.get("needs_human")]
    needs += [f"inbox: #{a.get('job_id')} ambiguous, {(a.get('evidence') or {}).get('subject', '(no subject)')} "
              f"from {(a.get('evidence') or {}).get('from', '?')}" for a in plan["ambiguous"]]
    needs += [f"inbox: {s}" for s in plan["skipped"]]
    summary = {"proposals": len(rows), "changes": len(plan["changes"]), "touches": len(plan["touches"]),
               "ambiguous": len(plan["ambiguous"]), "ignored": len(plan["ignored"]), "skipped": len(plan["skipped"]),
               "moves": [f"#{c['id']} {c['company']}: {c['from_status']} -> {c['to_status']}" for c in plan["changes"]]}
    return StageResult(summary, None, needs)
