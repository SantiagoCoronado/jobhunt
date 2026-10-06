"""Pick the N shortlisted jobs to research and tailor next (the "star" step).

Deterministic version of the /jh-hunt star rule, run against SQLite (canonical):
  * `shortlisted` rows only;
  * first up to `--dream-slots` (default 2) go to the highest-match rows at a dream company
    (profile.yaml `dream_companies`), one per company;
  * the remaining slots go to the highest-match rows overall, one per company;
  * a company with a live application (applied/screen/interview/offer, or a folder under
    applications/applied or applications/pending) or a `backlog` hold is skipped, so the hunt
    never re-tailors a live application or overrides a deliberate hold;
  * a company with a terminal outcome (rejected/ghosted/withdrawn) is skipped for
    `--cooldown-days` (default 90) after the outcome, dated by the NEWEST of application date,
    last contact, last logged event and first sighting, then released: a company that turned
    one role down is often the best source of the next one. A row with none of those dates is
    released, not held forever;
  * hand-shortlisted rows with no match score are listed under skipped ("not scored yet"), never
    picked blind and never silently dropped;
  * a dream row located outside the profile's relocation regions
    (`work_authorization.relocation_regions`, resolved through config/geo.yaml) is listed under
    skipped: the dream waiver covers relocation to those regions only (set 2026-09-02), so that
    ROW never takes a slot; the company's rows inside them stay eligible;
  * aggregator rows (Jobgether, HN "Who is Hiring") are listed but flagged, since the real
    employer needs a look before research.
Ties keep the newer posting. Two spares follow the picks so a flagged aggregator row can be
swapped without re-running. Nothing is written; the picks are printed one per line so the
orchestrator reads ~12 lines instead of the whole shortlist.

Usage:  python -m src.pick [--n 5] [--dream-slots 2] [--cooldown-days 90] [--spares 2] [--json]
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from .config import ROOT
from .db import connect
from .dream import is_dream
from .geo import outside_relocation_regions, relocation_scope

LIVE = ("applied", "screen", "interview", "offer")
HOLD = ("backlog",)
TERMINAL = ("rejected", "ghosted", "withdrawn")
COOLDOWN_DAYS = 90
SPARES = 2
AGGREGATORS = ("jobgether", "hn: who is hiring", "who is hiring")


def _norm(company: str) -> str:
    return " ".join((company or "").lower().replace(",", " ").replace(".", " ").split())


def busy_companies(conn, cooldown_days: int = COOLDOWN_DAYS, today: date | None = None,
                   apps_dir: Path | None = None) -> dict[str, str]:
    """{normalised company: reason} for every company the hunt must not pick right now."""
    apps = apps_dir or ROOT / "applications"
    busy: dict[str, str] = {}
    for r in conn.execute(f"SELECT company FROM jobs WHERE status IN ({','.join('?' * len(LIVE))})", LIVE):
        busy.setdefault(_norm(r["company"]), "company already has a live application")
    for r in conn.execute(f"SELECT company FROM jobs WHERE status IN ({','.join('?' * len(HOLD))})", HOLD):
        busy.setdefault(_norm(r["company"]), "company is on a backlog hold")
    cutoff = ((today or date.today()) - timedelta(days=cooldown_days)).isoformat()
    # The outcome date is the NEWEST of the dates a row carries: applied_at is stamped once on
    # the first flip to applied and never moves, so preferring it would date a September
    # rejection to a January application and release the company the next day.
    for r in conn.execute(
        "SELECT company, status, NULLIF(MAX(COALESCE(applied_at, ''), COALESCE(last_contact_at, ''), "
        "COALESCE((SELECT max(ts) FROM events e WHERE e.job_id = jobs.id), ''), COALESCE(first_seen, '')), '') AS at "
        f"FROM jobs WHERE status IN ({','.join('?' * len(TERMINAL))})", TERMINAL):
        when = (r["at"] or "")[:10]
        if when and when >= cutoff:   # no date at all: released, never held forever
            busy.setdefault(_norm(r["company"]), f"{r['status']} on {when}, within the {cooldown_days}-day cooldown")
    busy_ids: set[int] = set()
    for bucket in ("applied", "pending"):
        for p in (apps / bucket).glob("*-*"):
            tail = p.name.rsplit("-", 1)[-1]
            if tail.isdigit():
                busy_ids.add(int(tail))
    if busy_ids:
        for r in conn.execute("SELECT id, company FROM jobs"):
            if r["id"] in busy_ids:
                busy.setdefault(_norm(r["company"]), "company has an application folder in applied/ or pending/")
    return busy


def record(r, dream: bool) -> dict:
    """One pick as `picks.json` carries it, from a jobs row."""
    try:
        v = json.loads(r["match_verdict"] or "{}")
    except (ValueError, TypeError):
        v = {}
    if not isinstance(v, dict):
        v = {}
    return {
        "id": r["id"], "company": r["company"], "title": r["title"], "location": r["location"],
        "match": r["match_score"], "dream": dream, "recommendation": v.get("recommendation"),
        "location_ok": v.get("location_ok"), "visa_path": v.get("visa_path"),
    }


def chosen(ids: list[int], conn: sqlite3.Connection | None = None) -> tuple[list[dict], list[str]]:
    """(picks, refusals) for rows a human chose by id (`hunt run --ids`), in the order given.
    The star rule does not apply: no slots, no one-per-company, no in-play or cooldown skip, an
    unscored row is fine. What still holds: the row exists and is `shortlisted` (the matcher's
    hard blocks, export control among them, never reach that status), and a dream row outside
    the relocation regions stays out, as it does for `pick`. Any refusal means nothing runs."""
    conn = conn or connect()
    scope = relocation_scope()
    picks: list[dict] = []
    refused: list[str] = []
    for job_id in dict.fromkeys(ids):
        r = conn.execute("SELECT id, company, title, location, status, match_score, match_verdict "
                         "FROM jobs WHERE id=?", (job_id,)).fetchone()
        if r is None:
            refused.append(f"#{job_id} is not a row in the jobs table")
        elif r["status"] != "shortlisted":
            refused.append(f"#{job_id} {r['company'] or '?'} is {r['status']}, not shortlisted")
        elif is_dream(r["company"]) and outside_relocation_regions(r["location"], scope):
            refused.append(f"#{job_id} {r['company'] or '?'} is a dream row outside the relocation regions "
                           f"(work_authorization.relocation_regions)")
        else:
            picks.append(record(r, is_dream(r["company"])))
    return picks, refused


def pick(n: int = 5, dream_slots: int = 2, cooldown_days: int = COOLDOWN_DAYS,
         today: date | None = None, spares: int = SPARES, conn: sqlite3.Connection | None = None,
         apps_dir: Path | None = None) -> tuple[list[dict], list[dict], list[dict]]:
    """(picks, skipped, spares). Spares are the next candidates after the n picks. `conn` and
    `apps_dir` let a caller that owns its own connection and tree (the TUI) get the same answer
    a hunt would; the connection needs `sqlite3.Row` rows."""
    scope = relocation_scope()            # once, not once per dream row
    conn = conn or connect()
    busy = busy_companies(conn, cooldown_days, today, apps_dir)

    rows = conn.execute(
        "SELECT id, company, title, location, match_score, match_verdict, first_seen "
        "FROM jobs WHERE status='shortlisted' AND match_score IS NOT NULL "
        "ORDER BY match_score DESC, first_seen DESC"
    ).fetchall()
    picks: list[dict] = []
    skipped: list[dict] = []
    taken: set[str] = set()
    evaluated: set[int] = set()   # a row is judged once, whichever loop reaches it first
    for r in conn.execute("SELECT id, company, title, location FROM jobs WHERE status='shortlisted' AND match_score IS NULL"):
        skipped.append({"id": r["id"], "company": r["company"], "title": r["title"], "location": r["location"],
                        "match": None, "dream": is_dream(r["company"]), "why": "not scored yet, run the matcher"})

    def consider(r, dream: bool) -> bool:
        key = _norm(r["company"])
        if key in taken or r["id"] in evaluated:
            return False
        evaluated.add(r["id"])
        rec = record(r, dream)
        if key in busy:
            rec["why"] = busy[key]
            skipped.append(rec)
            taken.add(key)
            return False
        if dream and outside_relocation_regions(r["location"], scope):
            # Row-level skip: that req loses the slot, the company's reqs inside the regions stay eligible.
            rec["why"] = "dream row outside the relocation regions (work_authorization.relocation_regions)"
            skipped.append(rec)
            return False
        if any(a in key for a in AGGREGATORS):
            rec["flag"] = "aggregator row: confirm the real employer before research"
        picks.append(rec)
        taken.add(key)
        return True

    dream_rows = [r for r in rows if is_dream(r["company"])]
    got = 0
    for r in dream_rows:
        if got >= dream_slots:
            break
        if consider(r, True):
            got += 1
    for r in rows:
        if len(picks) >= n + spares:
            break
        consider(r, is_dream(r["company"]))
    return picks[:n], skipped, picks[n:n + spares]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--dream-slots", type=int, default=2)
    ap.add_argument("--cooldown-days", type=int, default=COOLDOWN_DAYS,
                    help="days a rejected/ghosted/withdrawn outcome keeps its company out of the picks")
    ap.add_argument("--spares", type=int, default=SPARES, help="extra candidates printed after the picks")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    picks, skipped, spares = pick(a.n, a.dream_slots, a.cooldown_days, spares=a.spares)
    if a.json:
        print(json.dumps({"picks": picks, "skipped": skipped, "spares": spares}, indent=1))
        return 0

    def line(p: dict) -> str:
        flag = f"  [{p['flag']}]" if p.get("flag") else ""
        return (f"  {'D' if p['dream'] else ' '} {p['id']:>6} {p['match'] or 0:>3} {(p['company'] or '')[:24]:<24} "
                f"{(p['title'] or '')[:52]:<52} {(p['location'] or '')[:22]:<22} {p.get('recommendation') or '':<10} "
                f"loc_ok={p.get('location_ok')!s:<5} {(p.get('visa_path') or '')[:50]}{flag}")

    print(f"picks ({len(picks)}):")
    for p in picks:
        print(line(p))
    if spares:
        print(f"spares ({len(spares)}), use in order if a pick is dropped:")
        for p in spares:
            print(line(p))
    held = sum(1 for why in busy_companies(connect(), a.cooldown_days).values() if "cooldown" in why)
    if skipped or held:
        print(f"skipped ({len(skipped)}"
              + (f", {held} compan{'y' if held == 1 else 'ies'} held by the {a.cooldown_days}-day cooldown" if held else "")
              + "): " + ", ".join(f"{s['company'] or '?'} #{s['id']} ({s['match']}, {s['why'].split(' (')[0]})" for s in skipped[:12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
