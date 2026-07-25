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


def funnel_data(conn: sqlite3.Connection) -> dict:
    """Everything funnel() prints, as data. Also consumed by src/report.py."""
    apps = _applications(conn)
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

    segments: dict[str, list[tuple[str, int, int]]] = {}
    for label, keyfn in (("score band", lambda r: _band(r["match_score"])),
                         ("title family", lambda r: title_family(r["title"])),
                         ("source", lambda r: r["source"])):
        seg: dict[str, list] = {}
        for r in apps:
            seg.setdefault(keyfn(r), []).append(_outcome(r["status"]))
        segments[label] = [
            (k, len(seg[k]), sum(1 for o in seg[k] if o == "responded"))
            for k in sorted(seg)
        ]
    return {"total": total, "responded": responded,
            "by_stage": by_stage, "segments": segments}


def funnel(conn: sqlite3.Connection) -> None:
    d = funnel_data(conn)
    if not d["total"]:
        print("No applications yet.")
        return
    total = d["total"]
    print(f"Applications: {total}")
    print(f"  responded (screen+ or rejected): {d['responded']}  ({100 * d['responded'] // total}%)")
    for k, v in d["by_stage"].items():
        if v:
            print(f"  {k:10s} {v}")
    for label, rows in d["segments"].items():
        print(f"\nBy {label}:")
        for k, n, resp in rows:
            print(f"  {k:12s} applied={n:3d}  responded={resp}  ({100 * resp // n}%)")


def calibration_data(conn: sqlite3.Connection) -> dict:
    """Score band vs outcome counts, in fixed band order."""
    apps = _applications(conn)
    seg: dict[str, dict[str, int]] = {}
    for r in apps:
        b = seg.setdefault(_band(r["match_score"]), {"responded": 0, "silence": 0})
        b["responded" if _outcome(r["status"]) == "responded" else "silence"] += 1
    bands = [(band, seg[band]["responded"], seg[band]["silence"])
             for band in ("90+", "80-89", "70-79", "<70", "unscored") if band in seg]
    return {"total": len(apps), "bands": bands}


def calibration(conn: sqlite3.Connection) -> None:
    d = calibration_data(conn)
    if not d["total"]:
        print("No applications yet.")
        return
    print("Score band vs outcome (does a 90 convert better than a 75?):")
    for band, responded, silence in d["bands"]:
        n = responded + silence
        print(f"  {band:9s} n={n:3d}  responded={responded}  rate={100 * responded // n}%")
    print("\nSmall n means weak evidence; interpret rates with counts in view.")


def comp_data(conn: sqlite3.Connection, min_score: int = 0) -> dict:
    """Salary segments over deduped roles at the score floor."""
    rows = conn.execute(
        "SELECT title, currency, salary_min, salary_max, remote FROM canonical_jobs "
        "WHERE (salary_min IS NOT NULL OR salary_max IS NOT NULL) "
        "AND COALESCE(match_score, 0) >= ?", (min_score,),
    ).fetchall()
    seg: dict[tuple, list[int]] = {}
    for r in rows:
        key = (r["currency"] or "?", title_family(r["title"]), bool(r["remote"]))
        # `or` is safe: int_or_none collapses 0 to None at ingest, so a stored
        # salary is always truthy (invariant from src/adapters/__init__.py).
        val = r["salary_max"] or r["salary_min"]
        seg.setdefault(key, []).append(val)
    segments = [
        {"currency": ccy, "family": fam, "remote": remote, "n": len(vals),
         "median": round(median(vals)), "min": min(vals), "max": max(vals)}
        for (ccy, fam, remote), vals in sorted(seg.items())
    ]
    return {"n_rows": len(rows), "segments": segments}


def comp(conn: sqlite3.Connection, min_score: int = 0) -> None:
    d = comp_data(conn, min_score)
    if not d["n_rows"]:
        print("No salary data at that score floor.")
        return
    print(f"Salary data on {d['n_rows']} deduped roles (value = max of range, else min).")
    print("NOTE: units are as-posted; several LatAm boards post MONTHLY figures, so a")
    print("'5,000 USD' cluster is monthly rate, not annual. Sanity-check before negotiating.")
    print(f"  {'ccy':4s} {'fam':3s} {'remote':6s} {'n':>4s} {'median':>10s} {'min':>10s} {'max':>10s}")
    for s in d["segments"]:
        print(f"  {s['currency']:4s} {s['family']:3s} {str(s['remote']):6s} {s['n']:4d} "
              f"{s['median']:>10,} {s['min']:>10,} {s['max']:>10,}")


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


def latency_data(conn: sqlite3.Connection) -> dict:
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
    return {"days": [r["days"] for r in rows]}


def latency(conn: sqlite3.Connection) -> None:
    days = latency_data(conn)["days"]
    if not days:
        print("No applied -> response pairs in the event log yet.")
        return
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
