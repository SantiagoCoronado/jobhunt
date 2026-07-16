"""Stage ①.5: coarse Haiku triage between discover and match.

The keyword prescore in src/match.py is a dumb substring counter, so we only ever
feed the expensive matcher the top-N jobs and leave thousands unscored. This stage
is a cheap junk cut: a Haiku sub-agent judges each job keep/drop against the profile
dealbreakers, so the real matcher can then run over ALL survivors instead of a top-N.

Mirrors src/match.py's export -> agent -> ingest handoff:
  1. `python -m src.triage export [--chunk 200] [--limit N]` -> data/triage/chunk_*.json
     (untriaged 'discovered' jobs, deduped by canonical_key, minimal fields only).
  2. Haiku sub-agents read each chunk_NNN.json and write out_NNN.json =
     [{id, keep, reason, bucket}] (see the triage prompt / rubric).
  3. `python -m src.triage ingest` -> drops non-keepers (status='irrelevant', so they
     leave every future export/match/triage) and marks keepers so they skip re-triage
     yet still flow on to /jh-match.

Keep-on-doubt: only drop clearly off-field roles or explicit dealbreaker violations.
"""
from __future__ import annotations

import argparse
import json

from .config import ROOT
from .db import connect
from .models import now_iso

TRIAGE_DIR = ROOT / "data" / "triage"


def _is_keep(v) -> bool:
    """Coerce an agent's keep value (bool / string / int) to a real bool."""
    return v in (True, "true", "True", "yes", 1, "1")


def export(chunk: int, limit: int | None) -> None:
    conn = connect()
    # Untriaged, undiscarded, unscored jobs, one per canonical_key. Order by the hash
    # so chunks are a representative cross-source mix (good for a sanity-check batch);
    # for a full sweep order is irrelevant since everything gets judged.
    rows = conn.execute(
        """
        SELECT id, company, title, location, remote, description
        FROM canonical_jobs
        WHERE status='discovered' AND match_score IS NULL AND match_verdict IS NULL
        ORDER BY canonical_key
        """
    ).fetchall()
    if limit:
        rows = rows[:limit]

    TRIAGE_DIR.mkdir(parents=True, exist_ok=True)
    for old in list(TRIAGE_DIR.glob("chunk_*.json")) + list(TRIAGE_DIR.glob("out_*.json")):
        old.unlink()

    recs = [{
        "id": r["id"],
        "company": r["company"],
        "title": r["title"],
        "location": r["location"] or ("Remote" if r["remote"] else ""),
        "snippet": (r["description"] or "")[:300],
    } for r in rows]

    n = 0
    for i in range(0, len(recs), chunk):
        (TRIAGE_DIR / f"chunk_{n:03d}.json").write_text(
            json.dumps(recs[i:i + chunk], indent=2, ensure_ascii=False))
        n += 1

    print(f"Exported {len(recs)} jobs -> {n} chunk(s) of <= {chunk} in {TRIAGE_DIR}")
    print("Now run one Haiku triage sub-agent per chunk_NNN.json (-> out_NNN.json), "
          "then: python -m src.triage ingest")


def ingest() -> None:
    outs = sorted(TRIAGE_DIR.glob("out_*.json"))
    if not outs:
        raise SystemExit(f"No out_*.json in {TRIAGE_DIR}. Run the triage sub-agents first.")
    conn = connect()
    now = now_iso()
    kept = dropped = missing = 0
    for f in outs:
        try:
            data = json.loads(f.read_text())
        except Exception as e:  # noqa: BLE001, one bad file shouldn't sink the batch
            print(f"  ! skip {f.name}: {e}")
            continue
        for d in data:
            row = conn.execute(
                "SELECT canonical_key FROM jobs WHERE id=?", (d.get("id"),)).fetchone()
            if not row:
                missing += 1
                continue
            ck = row["canonical_key"]
            verdict = json.dumps({
                "triage": "keep" if _is_keep(d.get("keep")) else "drop",
                "reason": (d.get("reason") or "")[:120],
                "bucket": d.get("bucket"),
            })
            if _is_keep(d.get("keep")):
                # Mark keeper (verdict set, score still NULL) so re-runs skip it, yet it
                # still satisfies match export's `match_score IS NULL AND status='discovered'`.
                conn.execute(
                    "UPDATE jobs SET match_verdict=? "
                    "WHERE canonical_key=? AND status='discovered' AND match_score IS NULL",
                    (verdict, ck))
                kept += 1
            else:
                conn.execute(
                    "UPDATE jobs SET status='irrelevant', match_verdict=? "
                    "WHERE canonical_key=? AND status='discovered'",
                    (verdict, ck))
                dropped += 1
    conn.commit()
    tail = f" {missing} unknown ids." if missing else ""
    print(f"Triage ingest ({now}): {kept} kept, {dropped} dropped (status='irrelevant').{tail}")
    print("Next: python -m src.match export --limit <big>  then /jh-match over the survivors.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--chunk", type=int, default=200)
    e.add_argument("--limit", type=int, default=None)
    sub.add_parser("ingest")
    args = ap.parse_args()
    if args.cmd == "export":
        export(args.chunk, args.limit)
    else:
        ingest()
