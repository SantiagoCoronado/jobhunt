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

from .config import ROOT, load_profile, safe_profile, shortlist_threshold
from . import geo
from .db import connect
from .dream import dream_shortlist_threshold, is_dream
from .models import normalize_text, now_iso

PENDING = ROOT / "data" / "pending_match.json"
SCORES = ROOT / "data" / "scores.json"
MATCH_DIR = ROOT / "data" / "match"   # chunked scaled-scoring handoff (see export --chunk)


def _profile_skills() -> list[str]:
    p = load_profile()
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


def _score_bucket(score: int | None) -> int:
    """Pseudo-bucket for an ALREADY scored row, so --rescore keeps priority ordering."""
    if score is None:
        return -1
    return 3 if score >= 85 else 2 if score >= 75 else 1 if score >= 65 else 0


# Locations that clearly REQUIRE sitting somewhere outside the candidate's home region
# (profile `header_location`, resolved through config/geo.yaml). Applied only when the posting
# is not flagged remote; see profile.yaml location_rule (the authority).
_LOCATION_RES: tuple | None = None


def _location_res() -> tuple:
    """(ok_re, locked_out_re) for the home region, built once per process. No resolvable home
    (an old profile without header_location, or a fixture with none): nothing is locked out."""
    global _LOCATION_RES
    if _LOCATION_RES is None:
        prof = safe_profile()
        home = geo.home(prof)
        ok = geo._word_re(geo.home_words(home))
        locked = geo._word_re(geo.locked_out_words(home)) if home else None
        _LOCATION_RES = (ok, locked)
    return _LOCATION_RES


def _location_plausible(row) -> bool:
    """Cheap prefilter for the tightened location rule: drop only the clearly locked-out.

    Keeps anything flagged remote (a remote req headquartered elsewhere may still hire from
    home; the matcher and a live check decide), anything naming the home region or a region
    containing it, or a remote word, and blanks. The stored `location` string is NOT
    authoritative, so this only removes on-site rows that name a city, state or country the
    candidate will not relocate to.
    """
    loc = (row["location"] or "").strip().lower()
    if not loc:
        return True
    ok, locked = _location_res()
    if ok.search(loc):
        return True
    if row["remote"]:
        return True
    return locked is None or not locked.search(loc)


def export(limit: int, min_bucket: int | None = None, chunk: int | None = None,
           rescore: bool = False, eligible_only: bool = False) -> None:
    """Write the scoring queue. Rows are triage survivors (kept, unscored, discovered).

    Ordered by triage fit bucket (best first), then keyword prescore. Two modes:
      - default: top `limit` into data/pending_match.json (the /jh-match single-batch flow).
      - `chunk`: split into data/match/chunk_NNN.json for a fanned-out scoring workflow;
        `min_bucket` filters to survivors at/above that bucket (e.g. 3 = strong only).

    `rescore` also pulls ALREADY scored `shortlisted` rows back into the queue, for when a
    scoring input changed (e.g. profile.yaml location_rule) and old scores are stale. Their
    priority bucket is derived from the existing match_score. `eligible_only` drops rows whose
    location clearly requires relocating outside the home region (see `_location_plausible`).

    Dream-company rows (the dream_companies table) always survive `eligible_only`, sort
    ahead of everything else, and carry `dream: true`.
    """
    skills = _profile_skills()
    conn = connect()
    # cross-source dedupe: the deterministic representative per canonical_key
    # (ATS source preferred, then lowest id; see db.canonical_jobs)
    rows = list(conn.execute(
        "SELECT * FROM canonical_jobs WHERE match_score IS NULL AND status='discovered'"
    ).fetchall())
    stale: set[int] = set()
    if rescore:
        prev = conn.execute(
            "SELECT * FROM canonical_jobs WHERE match_score IS NOT NULL AND status='shortlisted'"
        ).fetchall()
        stale = {r["id"] for r in prev}
        rows += list(prev)

    if eligible_only:
        rows = [r for r in rows if is_dream(r["company"]) or _location_plausible(r)]

    items = []
    for r in rows:
        blob = f"{r['title']} {r['title']} {r['description']}"  # title double-weighted
        bucket = (_score_bucket(r["match_score"]) if r["id"] in stale
                  else _triage_bucket(r["match_verdict"]))
        items.append((r, _keyword_score(blob, skills), bucket, is_dream(r["company"])))
    if min_bucket is not None:
        # A dream row with NO triage bucket yet (-1) still rides along: it never waits
        # behind a bucket gate it has not been through. So does a dream row under --rescore:
        # its bucket comes from the OLD score on the general 85/75/65 ladder, while dream rows
        # shortlist at the lower dream threshold, so a bucket gate would drop exactly the rows
        # the rescore exists to re-evaluate. A dream row that triage DID bucket obeys the gate
        # like everyone else (2026-09-02: the old unconditional pass let 665 dream rows, 533 of
        # them bucket 0-2, into a bucket-3 export).
        items = [it for it in items
                 if it[2] >= min_bucket or (it[3] and (it[2] < 0 or it[0]["id"] in stale))]
    items.sort(key=lambda x: (x[3], x[2], x[1]), reverse=True)  # dream, bucket, prescore

    cap = limit if (limit and limit > 0) else None

    def rec(r, ks, bucket, dream):
        # salary_* carry the posted band when a source published one. They are NOT
        # normalised: sources mix periods (annual/monthly/hourly) and currencies, so the
        # matcher must annualise before comparing against the comp floor in profile.yaml.
        # Omitted entirely when the source published nothing, so an absent band never
        # reads as a zero.
        out = {
            "id": r["id"], "company": r["company"], "title": r["title"],
            "location": r["location"], "url": r["url"],
            "keyword_prescore": ks, "triage_bucket": bucket,
            "description": (r["description"] or "")[:3000],
        }
        if r["salary_min"] is not None or r["salary_max"] is not None:
            out["salary_min"] = r["salary_min"]
            out["salary_max"] = r["salary_max"]
            out["salary_currency"] = r["currency"]
        if dream:
            out["dream"] = True   # profile.yaml dream_rule applies (matcher reads it)
        return out

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
        print(f"  buckets: strong={by[3]} good={by[2]} plausible={by[1]} weak={by[0]} none={by[-1]}"
              f"  dream={sum(1 for it in sel if it[3])}")
        return

    sel = items[:cap] if cap else items
    out = [rec(*it) for it in sel]
    PENDING.parent.mkdir(exist_ok=True)
    PENDING.write_text(json.dumps(out, indent=2))
    print(f"Exported {len(out)} jobs -> {PENDING}  (dream={sum(1 for it in sel if it[3])})")
    print("Now run /jh-match in Claude Code to score them.")


def ingest(threshold: int | None = None, scores_dir: str | None = None) -> None:
    """Write scores back. Dream-company rows shortlist at `dream_shortlist_threshold`
    (profile.yaml) instead of `shortlist_threshold`; an explicit --threshold applies to both."""
    shortlist = threshold if threshold is not None else shortlist_threshold()
    dream_cut = threshold if threshold is not None else dream_shortlist_threshold()
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
    n = short = missing = dream_short = 0
    for s in data:
        score = int(s.get("score", 0))
        verdict = json.dumps({k: s[k] for k in s if k not in ("id",)})
        co = conn.execute("SELECT company FROM jobs WHERE id=?", (s.get("id"),)).fetchone()
        dream = bool(co) and is_dream(co["company"])
        cut = dream_cut if dream else shortlist
        new_status = "shortlisted" if score >= cut else "discovered"
        # The score was judged on the canonical representative; propagate it to
        # every still-unscored duplicate of the same role so dupes never
        # re-enter the export queue as fresh work.
        # 'shortlisted' is included so a re-scored row (export --rescore) can fall back to
        # 'discovered' when the new score misses the cutoff. Human-progressed and terminal
        # statuses are never touched.
        cur = conn.execute(
            "UPDATE jobs SET match_score=?, match_verdict=?, "
            "status=CASE WHEN status IN ('discovered','shortlisted') THEN ? ELSE status END "
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
        if score >= cut:
            short += 1
            dream_short += int(dream)
    conn.commit()
    tail = f"; {missing} skipped (unknown id)" if missing else ""
    dtail = f", {dream_short} of them dream-company rows (>= {dream_cut})" if dream_short else ""
    print(f"Ingested {n} scores; {short} shortlisted (>= {shortlist}{dtail}){tail}. Updated {now}.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--limit", type=int, default=40)   # 0 = no cap (use with --chunk)
    e.add_argument("--min-bucket", type=int, default=None, dest="min_bucket")
    e.add_argument("--chunk", type=int, default=None)
    e.add_argument("--rescore", action="store_true",
                   help="also re-queue already-scored 'shortlisted' rows (use when a scoring "
                        "input changed, e.g. profile.yaml location_rule)")
    e.add_argument("--eligible-only", action="store_true", dest="eligible_only",
                   help="drop rows whose location clearly requires relocating outside the home region")
    i = sub.add_parser("ingest")
    i.add_argument("--threshold", type=int, default=None,
                   help="override profile.yaml shortlist_threshold (default 70)")
    i.add_argument("--dir", default=None, dest="scores_dir")  # merge data/match/scores_*.json
    args = ap.parse_args()
    if args.cmd == "export":
        export(args.limit, args.min_bucket, args.chunk, args.rescore, args.eligible_only)
    else:
        ingest(args.threshold, args.scores_dir)
