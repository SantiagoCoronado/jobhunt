"""Stage ②a: bridge between SQLite and the Claude Code matcher.

Because your engine is Claude Code (not a local model), scoring works like this:
  1. `python -m src.match export`  -> writes data/pending_match.json (keyword-prescored,
     top-N unscored jobs) for the LLM to judge.
  2. The /jh-match command (or job-matcher subagent) reads that file, scores each job
     against config/profile.yaml, and writes data/scores.json.
  3. `python -m src.match ingest`  -> writes scores back into the DB and shortlists winners.

Keyword prescore is only a cheap prioritizer so the LLM judges the most promising first.
"""
from __future__ import annotations

import argparse
import json

from pathlib import Path

from .config import load_yaml, shortlist_threshold, ROOT
from .db import connect
from .models import normalize_text, now_iso

PENDING = ROOT / "data" / "pending_match.json"
SCORES = ROOT / "data" / "scores.json"
MATCH_DIR = ROOT / "data" / "match"   # chunked scaled-scoring handoff (see export --chunk)


def _profile_skills() -> list[str]:
    p = load_yaml("profile.yaml")
    skills = (p.get("must_have_skills") or []) + (p.get("nice_to_have_skills") or [])
    return [normalize_text(s) for s in skills if s]


def _keyword_score(text: str, skills: list[str]) -> int:
    t = normalize_text(text)
    hits = sum(1 for s in skills if s and s in t)
    return int(100 * hits / max(len(skills), 1))


def _triage_bucket(verdict: str | None) -> int:
    """Pull the coarse Haiku triage fit bucket (0-3) out of match_verdict; -1 if none."""
    if not verdict:
        return -1
    try:
        b = json.loads(verdict).get("bucket")
        return b if isinstance(b, int) else -1
    except Exception:  # noqa: BLE001
        return -1


def export(limit: int, min_bucket: int | None = None, chunk: int | None = None) -> None:
    """Write the scoring queue. Rows are triage survivors (kept, unscored, discovered).

    Ordered by triage fit bucket (best first), then keyword prescore. Two modes:
      - default: top `limit` into data/pending_match.json (the /jh-match single-batch flow).
      - `chunk`: split into data/match/chunk_NNN.json for a fanned-out scoring workflow;
        `min_bucket` filters to survivors at/above that bucket (e.g. 3 = strong only).
    """
    skills = _profile_skills()
    conn = connect()
    # cross-source dedupe: the deterministic representative per canonical_key
    # (ATS source preferred, then lowest id; see db.canonical_jobs)
    rows = conn.execute(
        "SELECT * FROM canonical_jobs WHERE match_score IS NULL AND status='discovered'"
    ).fetchall()

    items = []
    for r in rows:
        blob = f"{r['title']} {r['title']} {r['description']}"  # title double-weighted
        items.append((r, _keyword_score(blob, skills), _triage_bucket(r["match_verdict"])))
    if min_bucket is not None:
        items = [it for it in items if it[2] >= min_bucket]
    items.sort(key=lambda x: (x[2], x[1]), reverse=True)  # bucket first, then prescore

    cap = limit if (limit and limit > 0) else None

    def rec(r, ks, bucket):
        return {
            "id": r["id"], "company": r["company"], "title": r["title"],
            "location": r["location"], "url": r["url"],
            "keyword_prescore": ks, "triage_bucket": bucket,
            "description": (r["description"] or "")[:3000],
        }

    if chunk:
        MATCH_DIR.mkdir(parents=True, exist_ok=True)
        for old in list(MATCH_DIR.glob("chunk_*.json")) + list(MATCH_DIR.glob("scores_*.json")):
            old.unlink()
        sel = items[:cap] if cap else items
        n = 0
        for i in range(0, len(sel), chunk):
            part = [rec(*it) for it in sel[i:i + chunk]]
            (MATCH_DIR / f"chunk_{n:03d}.json").write_text(
                json.dumps(part, indent=2, ensure_ascii=False))
            n += 1
        by = {b: sum(1 for it in sel if it[2] == b) for b in (3, 2, 1, 0, -1)}
        print(f"Exported {len(sel)} jobs -> {n} chunk(s) of <= {chunk} in {MATCH_DIR}")
        print(f"  buckets: strong={by[3]} good={by[2]} plausible={by[1]} weak={by[0]} none={by[-1]}")
        return

    out = [rec(*it) for it in (items[:cap] if cap else items)]
    PENDING.parent.mkdir(exist_ok=True)
    PENDING.write_text(json.dumps(out, indent=2))
    print(f"Exported {len(out)} jobs -> {PENDING}")
    print("Now run /jh-match in Claude Code to score them.")


def ingest(threshold: int | None = None, scores_dir: str | None = None) -> None:
    shortlist = threshold if threshold is not None else shortlist_threshold()
    if scores_dir:
        files = sorted(Path(scores_dir).glob("scores_*.json"))
        if not files:
            raise SystemExit(f"No scores_*.json in {scores_dir}. Run the scoring workflow first.")
        data = []
        for f in files:
            try:
                data += json.loads(f.read_text())
            except Exception as e:  # noqa: BLE001, one bad file shouldn't sink the batch
                print(f"  ! skip {f.name}: {e}")
    else:
        if not SCORES.exists():
            raise SystemExit(f"No scores file at {SCORES}. Run /jh-match in Claude Code first.")
        data = json.loads(SCORES.read_text())
    conn = connect()
    now = now_iso()
    n = short = missing = 0
    for s in data:
        score = int(s.get("score", 0))
        verdict = json.dumps({k: s[k] for k in s if k not in ("id",)})
        new_status = "shortlisted" if score >= shortlist else "discovered"
        # The score was judged on the canonical representative; propagate it to
        # every still-unscored duplicate of the same role so dupes never
        # re-enter the export queue as fresh work.
        cur = conn.execute(
            "UPDATE jobs SET match_score=?, match_verdict=?, "
            "status=CASE WHEN status='discovered' THEN ? ELSE status END "
            "WHERE (id=? OR (match_score IS NULL AND status='discovered')) "
            "AND canonical_key=(SELECT canonical_key FROM jobs WHERE id=?)",
            (score, verdict, new_status, s["id"], s["id"]),
        )
        if cur.rowcount == 0:
            # Unknown id (deleted row, or the scorer hallucinated one): a silent
            # no-op here would report success while writing nothing.
            missing += 1
            print(f"  ! skip score for unknown job id {s.get('id')!r}")
            continue
        n += 1
        if score >= shortlist:
            short += 1
    conn.commit()
    tail = f"; {missing} skipped (unknown id)" if missing else ""
    print(f"Ingested {n} scores; {short} shortlisted (>= {shortlist}){tail}. Updated {now}.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--limit", type=int, default=40)   # 0 = no cap (use with --chunk)
    e.add_argument("--min-bucket", type=int, default=None, dest="min_bucket")
    e.add_argument("--chunk", type=int, default=None)
    i = sub.add_parser("ingest")
    i.add_argument("--threshold", type=int, default=None,
                   help="override profile.yaml shortlist_threshold (default 70)")
    i.add_argument("--dir", default=None, dest="scores_dir")  # merge data/match/scores_*.json
    args = ap.parse_args()
    if args.cmd == "export":
        export(args.limit, args.min_bucket, args.chunk)
    else:
        ingest(args.threshold, args.scores_dir)
