"""Stage ②a: bridge between SQLite and the Claude Code matcher.

Because your engine is Claude Code (not a local model), scoring works like this:
  1. `python -m src.match export`  -> writes data/pending_match.json (keyword-prescored,
     top-N unscored jobs) for the LLM to judge.
  2. The /match command (or job-matcher subagent) reads that file, scores each job
     against config/profile.yaml, and writes data/scores.json.
  3. `python -m src.match ingest`  -> writes scores back into the DB and shortlists winners.

Keyword prescore is only a cheap prioritizer so the LLM judges the most promising first.
"""
from __future__ import annotations

import argparse
import json

from .config import load_yaml, ROOT
from .db import connect
from .models import normalize_text, now_iso

PENDING = ROOT / "data" / "pending_match.json"
SCORES = ROOT / "data" / "scores.json"


def _profile_skills() -> list[str]:
    p = load_yaml("profile.yaml")
    skills = (p.get("must_have_skills") or []) + (p.get("nice_to_have_skills") or [])
    return [normalize_text(s) for s in skills if s]


def _keyword_score(text: str, skills: list[str]) -> int:
    t = normalize_text(text)
    hits = sum(1 for s in skills if s and s in t)
    return int(100 * hits / max(len(skills), 1))


def export(limit: int) -> None:
    skills = _profile_skills()
    conn = connect()
    # cross-source dedupe: one row per canonical_key, prefer the lowest id
    rows = conn.execute(
        """
        SELECT * FROM jobs
        WHERE match_score IS NULL AND status='discovered'
        GROUP BY canonical_key
        """
    ).fetchall()

    scored = []
    for r in rows:
        blob = f"{r['title']} {r['title']} {r['description']}"  # title double-weighted
        scored.append((r, _keyword_score(blob, skills)))
    scored.sort(key=lambda x: x[1], reverse=True)

    out = [{
        "id": r["id"],
        "company": r["company"],
        "title": r["title"],
        "location": r["location"],
        "url": r["url"],
        "keyword_prescore": ks,
        "description": (r["description"] or "")[:3000],
    } for r, ks in scored[:limit]]

    PENDING.parent.mkdir(exist_ok=True)
    PENDING.write_text(json.dumps(out, indent=2))
    print(f"Exported {len(out)} jobs -> {PENDING}")
    print("Now run the /match command in Claude Code to score them.")


def ingest(shortlist_threshold: int) -> None:
    if not SCORES.exists():
        raise SystemExit(f"No scores file at {SCORES}. Run /match in Claude Code first.")
    data = json.loads(SCORES.read_text())
    conn = connect()
    now = now_iso()
    n = short = 0
    for s in data:
        score = int(s.get("score", 0))
        verdict = json.dumps({k: s[k] for k in s if k not in ("id",)})
        new_status = "shortlisted" if score >= shortlist_threshold else "discovered"
        conn.execute(
            "UPDATE jobs SET match_score=?, match_verdict=?, status=CASE WHEN status='discovered' THEN ? ELSE status END WHERE id=?",
            (score, verdict, new_status, s["id"]),
        )
        n += 1
        if score >= shortlist_threshold:
            short += 1
    conn.commit()
    print(f"Ingested {n} scores; {short} shortlisted (>= {shortlist_threshold}). Updated {now}.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export"); e.add_argument("--limit", type=int, default=40)
    i = sub.add_parser("ingest"); i.add_argument("--threshold", type=int, default=70)
    args = ap.parse_args()
    if args.cmd == "export":
        export(args.limit)
    else:
        ingest(args.threshold)
