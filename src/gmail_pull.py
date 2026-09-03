"""Apply inbox-derived status signals to the local DB.

Phase 2 of docs/spec-email-report-upskill.md, input side replaced by
docs/spec-mail-fetch.md (Phase B). The /jh-gmail-sync skill reads the manifest
printed by `python -m src.mail_fetch` (or the Gmail MCP as a fallback) and
classifies signals; THIS script is the only thing that touches the DB, on
notion_pull's contract: dry run by default, per-change diff either way, never
downgrade, every write through the single write path (db.set_status /
db.touch_contact).

  python -m src.gmail_pull data/gmail_pull.json          # diff only
  python -m src.gmail_pull data/gmail_pull.json --apply  # execute

Input: JSON array, one object per proposal, in one of two forms.

Manifest form (the normal path, after `python -m src.mail_fetch`):
  {"manifest_id": <line id from the printed manifest>,
   "sweep": "<the `sweep:` stamp the fetcher printed>",
   "signal": "rejection|interview_invite|assessment|offer|reply|ambiguous|ignore",
   "proposed_status": "screen|interview|offer|rejected" | null,
   "job_id": <int, only when the line lists several jobs>}
  `resolve_manifest` copies the evidence headers, the job id and the contact date from
  that line in data/mail_inbox.json. A `sweep` that does not match the manifest on disk
  stops the run; any other per-line problem skips that proposal and reports it.

Explicit form (the Gmail MCP fallback, or a hand-written proposal):
  {"job_id": <int>,
   "signal": ...,
   "proposed_status": ...,
   "contact_date": "YYYY-MM-DD",
   "evidence": {"from": ..., "subject": ..., "date": ..., "message_id": ...,
                "thread_id": ..., "account": ...}}

`ignore` (receipts, product mail the cuts missed) writes nothing to the DB; it
exists so --apply can record the thread as seen and it never re-enters a sweep.

Rules (spec 2c/2d):
- Scope: jobs currently applied/screen/interview/offer. Anything else
  (terminal, a backlog hold, pre-application) is skipped and reported.
- proposed_status must move FORWARD in applied < screen < interview < offer.
  A non-forward proposal degrades to a contact touch; nothing ever downgrades.
- rejected is allowed from any in-scope stage; rejected and offer proposals
  need evidence carrying both subject and sender, or they are skipped.
- Conflicting proposals for one job: forward targets collapse to the most
  advanced; a rejection conflicting with a forward move goes to the ambiguous
  pile instead (email order is not reliable enough to auto-pick a winner).
- Every applied change also logs an events row kind='email_signal' whose
  payload is the evidence HEADERS only (from, subject, date, message_id,
  thread_id, account). Email bodies never enter the DB.
- --apply also records the message_id / thread_id of every proposal the plan
  accepted (changes, touches, ambiguous, ignored; NOT out-of-scope or otherwise
  skipped ones) in data/mail_state.json `seen`, with the signal and the date.
  mail_fetch then drops that message; only a `rejection` silences its whole
  thread, so an ignored receipt never hides the reply that lands on it.
- ghosted / withdrawn / offer decisions are human calls; this tool never
  proposes them and rejects them if handed one.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

from .db import connect, log_event, set_status, touch_contact
from .mail_fetch import INBOX_PATH, STATE_PATH, load_state, save_state
from .reconcile import sync_folder

STAGE_RANK = {"applied": 0, "screen": 1, "interview": 2, "offer": 3}
ALLOWED_TARGETS = {"screen", "interview", "offer", "rejected"}
EVIDENCE_REQUIRED = {"rejected", "offer"}
IGNORE_SIGNALS = {"ignore", "receipt"}
HEADER_KEYS = ("from", "subject", "date", "message_id", "thread_id", "account")


def _note(evidence: dict) -> str:
    acct = f" [{evidence['account']}]" if evidence.get("account") else ""
    return (f"email: {evidence.get('subject', '?')} "
            f"({evidence.get('from', '?')}, {evidence.get('date', '?')}){acct}")


def _strip_id(value: object) -> str:
    return str(value or "").strip().strip("<>").strip()


def _headers(evidence: dict) -> dict:
    out = {k: evidence[k] for k in HEADER_KEYS if evidence.get(k)}
    for k in ("message_id", "thread_id"):
        if k in out:
            out[k] = _strip_id(out[k])
    return out


def record_seen(batch: list[dict], state_path: Path = STATE_PATH, today: str | None = None) -> int:
    """Remember the ids of every accepted proposal (`plan()["seen_batch"]`) with their
    signal and date, so mail_fetch never re-surfaces the message. Returns the count."""
    state = load_state(state_path)
    seen: dict[str, dict] = state.setdefault("seen", {})
    at = today or date.today().isoformat()
    n = 0
    for p in batch:
        ev = p.get("evidence") or {}
        signal = str(p.get("signal") or ("ignore" if not p.get("proposed_status") else "reply"))
        for key in ("message_id", "thread_id"):
            v = _strip_id(ev.get(key))
            if v and v not in seen:
                seen[v] = {"signal": signal, "at": at}
                n += 1
    save_state(state_path, state)
    return n


def _same_sweep(a: str, b: str) -> bool:
    """Same instant, not the same string: a copied stamp may say Z for +00:00 or carry spaces."""
    a, b = a.strip(), b.strip()
    if a == b:
        return True
    try:
        return (datetime.fromisoformat(a.replace("Z", "+00:00"))
                == datetime.fromisoformat(b.replace("Z", "+00:00")))
    except ValueError:
        return False


def resolve_manifest(proposals: list[dict], inbox_path: Path = INBOX_PATH) -> list[dict]:
    """Fill a proposal from its manifest line.

    The /jh-gmail-sync skill classifies the printed manifest, which carries no message
    or thread ids (and must not be read from disk by the model). A proposal may
    therefore cite ``"manifest_id": <line id>``; the evidence headers (from, subject,
    date, message_id, thread_id, account), a missing ``job_id`` and a missing
    ``contact_date`` are copied here from ``data/mail_inbox.json``. Headers only;
    snippets never leave the archive. Explicit fields in the proposal win.

    A stale or missing ``sweep`` stamp stops the run (every id would be off). A per-line
    problem (unknown id, a multi-job line with no ``job_id``, a ``job_id`` the line never
    matched) marks that proposal ``_skip`` with the reason; ``plan`` reports it under
    Skipped and the rest of the batch still lands."""
    if not any("manifest_id" in p for p in proposals):
        return proposals
    try:
        doc = json.loads(Path(inbox_path).read_text())
        threads = {t["id"]: t for t in doc.get("threads") or []}
        generated_at = str(doc.get("generated_at") or "")
    except (OSError, ValueError):
        threads, generated_at = {}, ""
    out: list[dict] = []
    for p in proposals:
        mid = p.get("manifest_id")
        if mid is None:
            out.append(p)
            continue
        # Manifest ids are numbered per sweep and shift between sweeps, so a proposal must name
        # the sweep it classified; a stale or missing stamp refuses rather than hitting another
        # thread's job with another thread's evidence.
        sweep = str(p.get("sweep") or "").strip()
        if not sweep or not _same_sweep(sweep, generated_at):
            raise SystemExit(f"proposal for manifest_id {mid} names sweep {sweep or '(none)'} but the manifest "
                             f"on disk is {generated_at or '(none)'}; fix the stamp in the proposals file if the "
                             "ids came from this manifest, otherwise re-run python -m src.mail_fetch and "
                             "reclassify (ids are renumbered per sweep)")
        try:
            key = int(str(mid).strip())
        except ValueError:
            out.append({**p, "_skip": f"manifest_id {mid!r} is not a manifest line number, skipped"})
            continue
        t = threads.get(key)
        if not t:
            out.append({**p, "_skip": f"manifest_id {mid} is not in {inbox_path}, skipped"})
            continue
        ev = {k: t.get(k) for k in HEADER_KEYS if t.get(k)}
        ev.update(p.get("evidence") or {})
        q = {**p, "evidence": ev}
        jobs = t.get("job_ids") or []
        if q.get("job_id") is None:
            if len(jobs) != 1:
                out.append({**q, "_skip": f"manifest_id {mid} maps to {len(jobs)} jobs, set job_id explicitly, skipped"})
                continue
            q["job_id"] = jobs[0]
        else:
            # The manifest stores job ids as ints; a proposal may carry "6984" (the explicit path
            # gets SQLite's INTEGER affinity for free, this comparison does not).
            try:
                q["job_id"] = int(str(q["job_id"]).strip())
            except ValueError:
                out.append({**q, "_skip": f"job_id {q['job_id']!r} on manifest_id {mid} is not a job id, skipped"})
                continue
            if jobs and q["job_id"] not in jobs:
                # An explicit job_id must be one the cited thread actually matched, or the evidence
                # headers above would be filed against an unrelated job.
                out.append({**q, "_skip": f"job_id {q['job_id']} is not on manifest_id {mid} (matches {jobs}), skipped"})
                continue
        if q.get("proposed_status") is not None or q.get("signal") not in IGNORE_SIGNALS:
            if q.get("contact_date") is None:      # an explicit null must still take the thread date
                q["contact_date"] = t.get("date")
        out.append(q)
    return out


def _resolve_conflicts(proposals: list[dict]) -> tuple[list[dict], list[dict]]:
    """Collapse duplicate status proposals per job.

    Identical targets collapse to one; forward targets keep the most advanced;
    rejected + a forward target is a genuine conflict -> ambiguous.
    Returns (kept, conflicted)."""
    by_job: dict[int, list[dict]] = {}
    for p in proposals:
        by_job.setdefault(p["job_id"], []).append(p)
    kept: list[dict] = []
    conflicted: list[dict] = []
    for plist in by_job.values():
        targets = {p["proposed_status"] for p in plist}
        if len(targets) == 1:
            kept.append(plist[0])
        elif "rejected" in targets:
            conflicted.extend(plist)
        else:
            kept.append(max(plist, key=lambda p: STAGE_RANK[p["proposed_status"]]))
    return kept, conflicted


def plan(conn: sqlite3.Connection, proposals: list[dict]) -> dict:
    changes: list[dict] = []
    touches: dict[int, dict] = {}
    touch_evidence: list[dict] = []        # every accepted touch, folded or superseded included
    ambiguous: list[dict] = []
    skipped: list[str] = []
    ignored: list[dict] = []

    def to_touch(p: dict, job: sqlite3.Row) -> None:
        when = p.get("contact_date") or (p.get("evidence") or {}).get("date")
        if not when:
            skipped.append(f"#{job['id']} {job['company']}: touch with no date, skipped")
            return
        touch_evidence.append({"signal": p.get("signal") or "reply", "evidence": p.get("evidence") or {}})
        prev = touches.get(job["id"])
        if prev is None or when > prev["contact_date"]:
            touches[job["id"]] = {"id": job["id"], "company": job["company"],
                                  "title": job["title"], "contact_date": when,
                                  "signal": p.get("signal") or "reply",
                                  "evidence": p.get("evidence") or {}}

    status_props: list[dict] = []
    for p in proposals:
        if p.get("_skip"):                 # resolve_manifest could not fill this line
            skipped.append(p["_skip"])
            continue
        job = conn.execute("SELECT id, company, title, status FROM jobs WHERE id=?",
                           (p.get("job_id"),)).fetchone()
        if job is None:
            skipped.append(f"#{p.get('job_id')}: no such job")
            continue
        if job["status"] not in STAGE_RANK:
            why = "deliberate backlog hold" if job["status"] == "backlog" else job["status"]
            skipped.append(f"#{job['id']} {job['company']}: out of scope ({why})")
            continue
        p = {**p, "_job": job}
        if p.get("signal") in IGNORE_SIGNALS:
            ignored.append(p)              # recorded as seen on --apply, never touches the DB
        elif p.get("signal") == "ambiguous" or (
                not p.get("proposed_status") and not p.get("contact_date")
                and not (p.get("evidence") or {}).get("date")):
            ambiguous.append(p)
        elif target := p.get("proposed_status"):
            # invalid targets must fall out HERE, before conflict resolution
            # ranks proposals by stage order (unknown statuses have no rank)
            if target not in ALLOWED_TARGETS:
                skipped.append(f"#{job['id']} {job['company']}: '{target}' is never "
                               "email-proposable (human call), skipped")
            else:
                status_props.append(p)
        else:
            to_touch(p, job)

    status_props, conflicted = _resolve_conflicts(status_props)
    ambiguous.extend(conflicted)

    for p in status_props:
        job, target = p["_job"], p["proposed_status"]
        evidence = p.get("evidence") or {}
        if target in EVIDENCE_REQUIRED and not (evidence.get("subject") and evidence.get("from")):
            skipped.append(f"#{job['id']} {job['company']}: '{target}' needs evidence "
                           "with subject AND sender, skipped")
            continue
        if target != "rejected" and STAGE_RANK[target] <= STAGE_RANK[job["status"]]:
            to_touch(p, job)   # already there or beyond; the email is still contact
            continue
        changes.append({"id": job["id"], "company": job["company"], "title": job["title"],
                        "from_status": job["status"], "to_status": target,
                        "contact_date": p.get("contact_date") or evidence.get("date"),
                        "signal": p.get("signal") or target, "evidence": evidence})

    change_ids = {c["id"] for c in changes}
    kept_touches = [t for t in touches.values() if t["id"] not in change_ids]
    # what --apply records as seen: everything the plan accepted, nothing it refused
    seen_batch = ([{"signal": c["signal"], "evidence": c["evidence"]} for c in changes]
                  + touch_evidence
                  + [{"signal": "ambiguous", "evidence": a.get("evidence") or {}} for a in ambiguous]
                  + [{"signal": "ignore", "evidence": i.get("evidence") or {}} for i in ignored])
    return {"changes": changes, "touches": kept_touches, "ambiguous": ambiguous,
            "skipped": skipped, "ignored": ignored, "seen_batch": seen_batch}


def apply_changes(conn: sqlite3.Connection, p: dict) -> list[str]:
    log: list[str] = []
    for c in p["changes"]:
        set_status(conn, c["id"], c["to_status"], note=_note(c["evidence"]))
        if c.get("contact_date"):
            # a reply IS contact; direct column update to avoid a second
            # contact event on top of status_change + email_signal
            conn.execute("UPDATE jobs SET last_contact_at=? WHERE id=?",
                         (c["contact_date"][:10], c["id"]))
        log_event(conn, c["id"], "email_signal", {**_headers(c["evidence"]), "signal": c["signal"]})
    for t in p["touches"]:
        touch_contact(conn, t["id"], contact_date=t["contact_date"][:10])
        log_event(conn, t["id"], "email_signal", {**_headers(t["evidence"]), "signal": t["signal"]})
    conn.commit()
    for c in p["changes"]:
        moved = sync_folder(c["id"], c["to_status"])
        if moved:
            log.append(moved)
    return log


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply Gmail status signals to the local DB")
    ap.add_argument("proposals_json", help="JSON array written by /jh-gmail-sync")
    ap.add_argument("--apply", action="store_true", help="execute the proposed changes")
    args = ap.parse_args()

    proposals = resolve_manifest(json.loads(Path(args.proposals_json).read_text()))
    conn = connect()
    p = plan(conn, proposals)

    if p["changes"]:
        print(f"Status changes ({len(p['changes'])}):")
        for c in p["changes"]:
            print(f"  #{c['id']} {c['company']} - {c['title']}: "
                  f"{c['from_status']} -> {c['to_status']}, per {_note(c['evidence'])}")
    if p["touches"]:
        print(f"Contact touches ({len(p['touches'])}):")
        for t in p["touches"]:
            print(f"  #{t['id']} {t['company']} - {t['title']}: "
                  f"last_contact_at -> {t['contact_date']}")
    if p["ambiguous"]:
        print(f"Ambiguous, handle manually ({len(p['ambiguous'])}):")
        for a in p["ambiguous"]:
            ev = a.get("evidence") or {}
            print(f"  #{a['job_id']}: {ev.get('subject', '(no subject)')} "
                  f"from {ev.get('from', '?')}")
    if p["skipped"]:
        print(f"Skipped ({len(p['skipped'])}):")
        for s in p["skipped"]:
            print(f"  {s}")
    if p["ignored"]:
        print(f"Ignored, recorded as seen on --apply ({len(p['ignored'])}).")
    if not any(v for k, v in p.items() if k not in ("ignored", "seen_batch")):
        print("Inbox and DB agree.")

    if not args.apply:
        print("\nDry run. Re-run with --apply to execute.")
        return

    for line in apply_changes(conn, p):
        print(line)
    seen = record_seen(p["seen_batch"])
    print(f"\nApplied {len(p['changes'])} status changes, {len(p['touches'])} touches; "
          f"{seen} ids recorded as seen.")


if __name__ == "__main__":
    main()
