"""Deterministic pipeline analytics: the numbers behind /jh-review.

SQL computes everything; the LLM only interprets. Subcommands:

  python -m src.stats funnel        # conversion by stage, split by score band / family / source
  python -m src.stats calibration   # do high scores actually convert better?
  python -m src.stats comp          # salary distribution of scored roles (6.6)
  python -m src.stats drops [--sample N] [--seed S]   # triage false-drop audit sample
  python -m src.stats latency       # applied -> first-response days, from the event log

An "application" is any job that ever reached applied (applied_at set or a
status_change event to applied). "Responded" = reached screen or later, OR was
rejected (a rejection is a reply); ghosted/waiting are the silence bucket.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from statistics import median

from .db import connect

RESPONDED = ("screen", "interview", "offer")

# Title families per config/profile.yaml. Order matters: B's strategist/architect
# titles often contain "AI", so B is checked before A; C/D before A for the same
# reason ("React Engineer, AI tools" is a C).
FAMILIES = [
    ("B", re.compile(r"deployment|solutions? (architect|engineer)|enablement|strategist|"
                     r"forward.?deploy|field engineer|gtm|technical program|adoption", re.I)),
    ("C", re.compile(r"front.?end|\bui\b|react|web engineer|frontend", re.I)),
    ("D", re.compile(r"internal (tool|platform|application)|developer (experience|productivity)|"
                     r"business systems|workflow automation|devex", re.I)),
    ("A", re.compile(r".", re.I)),  # everything else: hands-on AI / full-stack
]


def title_family(title: str | None) -> str:
    for fam, rx in FAMILIES:
        if rx.search(title or ""):
            return fam
    return "A"


def _band(score) -> str:
    if score is None:
        return "unscored"
    if score >= 90:
        return "90+"
    if score >= 80:
        return "80-89"
    if score >= 70:
        return "70-79"
    return "<70"


def _applications(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM jobs WHERE applied_at IS NOT NULL "
        "OR status IN ('applied','screen','interview','offer')"
    ).fetchall()


def _outcome(status: str) -> str:
    if status in RESPONDED:
        return "responded"
    if status == "rejected":
        return "responded"      # a rejection is a reply
    if status in ("ghosted", "withdrawn"):
        return status
    return "waiting"            # applied, no signal yet


def funnel(conn: sqlite3.Connection) -> None:
    apps = _applications(conn)
    if not apps:
        print("No applications yet.")
        return
    total = len(apps)
    by_stage = {"screen": 0, "interview": 0, "offer": 0, "rejected": 0,
                "ghosted": 0, "withdrawn": 0, "waiting": 0, "other": 0}
    for r in apps:
        s = r["status"]
        if s in by_stage:
            by_stage[s] += 1
        elif s == "applied":
            by_stage["waiting"] += 1
        else:
            # e.g. moved to backlog with applied_at set; count it so the
            # breakdown always sums to the reported total.
            by_stage["other"] += 1
    responded = sum(1 for r in apps if _outcome(r["status"]) == "responded")
    print(f"Applications: {total}")
    print(f"  responded (screen+ or rejected): {responded}  ({100 * responded // total}%)")
    for k, v in by_stage.items():
        if v:
            print(f"  {k:10s} {v}")

    for label, keyfn in (("score band", lambda r: _band(r["match_score"])),
                         ("title family", lambda r: title_family(r["title"])),
                         ("source", lambda r: r["source"])):
        seg: dict[str, list] = {}
        for r in apps:
            seg.setdefault(keyfn(r), []).append(_outcome(r["status"]))
        print(f"\nBy {label}:")
        for k in sorted(seg):
            outs = seg[k]
            resp = sum(1 for o in outs if o == "responded")
            print(f"  {k:12s} applied={len(outs):3d}  responded={resp}  ({100 * resp // len(outs)}%)")


def calibration(conn: sqlite3.Connection) -> None:
    apps = _applications(conn)
    if not apps:
        print("No applications yet.")
        return
    print("Score band vs outcome (does a 90 convert better than a 75?):")
    seg: dict[str, dict[str, int]] = {}
    for r in apps:
        b = seg.setdefault(_band(r["match_score"]), {"responded": 0, "silence": 0})
        b["responded" if _outcome(r["status"]) == "responded" else "silence"] += 1
    for band in ("90+", "80-89", "70-79", "<70", "unscored"):
        if band in seg:
            d = seg[band]
            n = d["responded"] + d["silence"]
            print(f"  {band:9s} n={n:3d}  responded={d['responded']}  rate={100 * d['responded'] // n}%")
    print("\nSmall n means weak evidence; interpret rates with counts in view.")


def comp(conn: sqlite3.Connection, min_score: int = 0) -> None:
    rows = conn.execute(
        "SELECT title, currency, salary_min, salary_max, remote FROM canonical_jobs "
        "WHERE (salary_min IS NOT NULL OR salary_max IS NOT NULL) "
        "AND COALESCE(match_score, 0) >= ?", (min_score,),
    ).fetchall()
    if not rows:
        print("No salary data at that score floor.")
        return
    seg: dict[tuple, list[int]] = {}
    for r in rows:
        key = (r["currency"] or "?", title_family(r["title"]), bool(r["remote"]))
        # `or` is safe: int_or_none collapses 0 to None at ingest, so a stored
        # salary is always truthy (invariant from src/adapters/__init__.py).
        val = r["salary_max"] or r["salary_min"]
        seg.setdefault(key, []).append(val)
    print(f"Salary data on {len(rows)} deduped roles (value = max of range, else min).")
    print("NOTE: units are as-posted; several LatAm boards post MONTHLY figures, so a")
    print("'5,000 USD' cluster is monthly rate, not annual. Sanity-check before negotiating.")
    print(f"  {'ccy':4s} {'fam':3s} {'remote':6s} {'n':>4s} {'median':>10s} {'min':>10s} {'max':>10s}")
    for (ccy, fam, remote), vals in sorted(seg.items()):
        print(f"  {ccy:4s} {fam:3s} {str(remote):6s} {len(vals):4d} "
              f"{round(median(vals)):>10,} {min(vals):>10,} {max(vals):>10,}")


def drops(conn: sqlite3.Connection, sample: int = 15, seed: int | None = None) -> None:
    order = f"(id * {2654435761 + (seed or 0)}) % 9973" if seed is not None else "RANDOM()"
    rows = conn.execute(
        f"SELECT id, company, title, match_verdict FROM jobs "
        f"WHERE status='irrelevant' ORDER BY {order} LIMIT ?", (sample,),
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='irrelevant'").fetchone()[0]
    print(f"Triage false-drop audit: {sample} of {total} drops. "
          f"Any that look wrongly dropped -> tighten the triage rubric.")
    for r in rows:
        reason = ""
        try:
            reason = json.loads(r["match_verdict"] or "{}").get("reason", "")
        except json.JSONDecodeError:
            pass
        print(f"  #{r['id']} {r['company']} - {r['title']}  [{reason}]")


def latency(conn: sqlite3.Connection) -> None:
    # One row per APPLIED EVENT (not per job: a re-apply is its own cycle), and
    # the response must land before the next applied event of the same job so
    # cycles never cross. MIN() makes the pick well-defined; a bare column
    # under GROUP BY without an aggregate is implementation-defined in SQLite.
    rows = conn.execute(
        """
        SELECT a.id,
               MIN(CAST(julianday(r.ts) - julianday(a.ts) AS INTEGER)) AS days
        FROM events a
        JOIN events r ON r.job_id = a.job_id AND r.id > a.id
             AND r.kind = 'status_change'
             AND (r.payload LIKE '%"to": "screen"%' OR r.payload LIKE '%"to": "rejected"%'
                  OR r.payload LIKE '%"to": "interview"%')
             AND r.id < COALESCE((
                 SELECT MIN(na.id) FROM events na
                 WHERE na.job_id = a.job_id AND na.id > a.id
                   AND na.kind = 'status_change'
                   AND na.payload LIKE '%"to": "applied"%'), 9223372036854775807)
        WHERE a.kind = 'status_change' AND a.payload LIKE '%"to": "applied"%'
        GROUP BY a.id
        """
    ).fetchall()
    if not rows:
        print("No applied -> response pairs in the event log yet.")
        return
    days = [r["days"] for r in rows]
    print(f"Applied -> first response: n={len(days)}, median {median(days):.0f} days, "
          f"min {min(days)}, max {max(days)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("funnel")
    sub.add_parser("calibration")
    c = sub.add_parser("comp")
    c.add_argument("--min-score", type=int, default=0)
    d = sub.add_parser("drops")
    d.add_argument("--sample", type=int, default=15)
    d.add_argument("--seed", type=int, default=None)
    sub.add_parser("latency")
    a = ap.parse_args()
    conn = connect()
    if a.cmd == "funnel":
        funnel(conn)
    elif a.cmd == "calibration":
        calibration(conn)
    elif a.cmd == "comp":
        comp(conn, a.min_score)
    elif a.cmd == "drops":
        drops(conn, a.sample, a.seed)
    else:
        latency(conn)


if __name__ == "__main__":
    main()
