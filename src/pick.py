"""Pick the N shortlisted jobs to research and tailor next (the old Notion "star" step).

Deterministic version of the /jh-hunt star rule, run against SQLite (canonical):
  * `shortlisted` rows only;
  * first up to `--dream-slots` (default 2) go to the highest-match rows at a dream company
    (profile.yaml `dream_companies`), one per company;
  * the remaining slots go to the highest-match rows overall, one per company;
  * a company that already has an application folder (applications/{applied,pending,other})
    or a human-progressed row is skipped, so the hunt never re-tailors a live application;
  * a dream row located outside the TN countries (Berlin, London, Singapore ...) is listed under
    skipped: the dream waiver is US-on-TN only (Santiago, 2026-09-02), so it never takes a slot;
  * aggregator rows (Jobgether, HN "Who is Hiring") are listed but flagged, since the real
    employer needs a look before research.
Ties keep the newer posting. Nothing is written; the picks are printed one per line so the
orchestrator reads ~10 lines instead of the whole shortlist.

Usage:  python -m src.pick [--n 5] [--dream-slots 2] [--show 20]
"""
from __future__ import annotations

import argparse
import json

from .config import ROOT
from .db import connect
from .dream import is_dream
from .tailor_build import outside_tn_countries

PROGRESSED = ("applied", "screen", "interview", "offer", "rejected", "ghosted", "withdrawn")
AGGREGATORS = ("jobgether", "hn: who is hiring", "who is hiring")


def _norm(company: str) -> str:
    return " ".join((company or "").lower().replace(",", " ").replace(".", " ").split())


def pick(n: int = 5, dream_slots: int = 2) -> tuple[list[dict], list[dict]]:
    conn = connect()
    busy: set[str] = set()
    for r in conn.execute(f"SELECT company FROM jobs WHERE status IN ({','.join('?' * len(PROGRESSED))})", PROGRESSED):
        busy.add(_norm(r["company"]))
    busy_ids: set[int] = set()
    for p in (ROOT / "applications").glob("*/*-*"):
        tail = p.name.rsplit("-", 1)[-1]
        if tail.isdigit():
            busy_ids.add(int(tail))
    for r in conn.execute("SELECT id, company FROM jobs"):
        if r["id"] in busy_ids:
            busy.add(_norm(r["company"]))

    rows = conn.execute(
        "SELECT id, company, title, location, match_score, match_verdict, first_seen "
        "FROM jobs WHERE status='shortlisted' AND match_score IS NOT NULL "
        "ORDER BY match_score DESC, first_seen DESC"
    ).fetchall()
    picks: list[dict] = []
    skipped: list[dict] = []
    taken: set[str] = set()

    def consider(r, dream: bool) -> bool:
        key = _norm(r["company"])
        if key in taken:
            return False
        try:
            v = json.loads(r["match_verdict"] or "{}")
        except ValueError:
            v = {}
        rec = {
            "id": r["id"], "company": r["company"], "title": r["title"], "location": r["location"],
            "match": r["match_score"], "dream": dream, "recommendation": v.get("recommendation"),
            "location_ok": v.get("location_ok"), "visa_path": v.get("visa_path"),
        }
        if key in busy:
            rec["why"] = "company already has an application"
            skipped.append(rec)
            taken.add(key)
            return False
        if dream and outside_tn_countries(r["location"]):
            rec["why"] = "dream row outside the TN countries (no EU/UK/APAC relocation)"
            skipped.append(rec)
            taken.add(key)
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
        if len(picks) >= n:
            break
        if is_dream(r["company"]) and _norm(r["company"]) in taken:
            continue
        consider(r, is_dream(r["company"]))
    return picks[:n], skipped


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--dream-slots", type=int, default=2)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    picks, skipped = pick(a.n, a.dream_slots)
    if a.json:
        print(json.dumps({"picks": picks, "skipped": skipped}, indent=1))
        return 0
    print(f"picks ({len(picks)}):")
    for p in picks:
        flag = f"  [{p['flag']}]" if p.get("flag") else ""
        print(f"  {'D' if p['dream'] else ' '} {p['id']:>6} {p['match']:>3} {p['company'][:24]:<24} "
              f"{p['title'][:52]:<52} {(p['location'] or '')[:22]:<22} {p.get('recommendation') or '':<10} "
              f"loc_ok={p.get('location_ok')!s:<5} {(p.get('visa_path') or '')[:50]}{flag}")
    if skipped:
        print(f"skipped ({len(skipped)}): "
              + ", ".join(f"{s['company']} #{s['id']} ({s['match']}, {s['why'].split(' (')[0]})" for s in skipped[:12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
