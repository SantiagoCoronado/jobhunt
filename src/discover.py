"""Stage ①: pull every enabled source -> normalize -> upsert into SQLite.

Run:  python -m src.discover
Config: config/sources.yaml  (which ATS tokens / aggregators to pull)

Every fetched row passes the shared role-family title gate (`title_filter:` in
sources.yaml, applied here so no adapter has to repeat it) before it is upserted.
Company boards return every open req they have, and roughly half of that is
nursing/manufacturing/sales that would otherwise cost a Haiku triage call each.
The gate reads TITLES only: location is the matcher's job (profile.location_rule).
Sources are region-gated before that (config.sources(), docs/spec-pre-release.md decision
10): a board whose `regions:` miss the profile's coverage is off, and discover prints one
line for it naming the `enabled:` key that forces it back on.
Dream companies (the dream_companies table, src.dream) skip the gate when
`title_filter.skip_dream_companies` is on: their boards are small and hand-picked.
"""
from __future__ import annotations

import importlib

from .adapters import keep_title
from .config import REGION_GATED, missing_targeting, region_skip_line, sources as load_sources
from .db import connect
from .dream import is_dream
from .models import now_iso

# adapter module name -> friendly label
ADAPTERS = [
    # ATS boards
    "greenhouse", "lever", "ashby", "workable",
    "personio", "bamboohr", "workday", "softserve", "teamtailor",
    "pinpoint", "rippling", "secretlab",
    # Aggregators
    "remoteok", "remotive", "weworkremotely", "hackernews", "getonbrd",
    "jobicy", "arbeitnow", "himalayas", "recruitee", "smartrecruiters",
    "adzuna", "themuse", "findwork", "careerjet", "torre", "posthog",
    "consider", "workatastartup",
    # European boards (docs/sources-europe.md), region-gated to their country
    "jobtech", "jobindex", "berlinstartupjobs",
]


def main() -> None:
    sources = load_sources()
    skip_dream = bool((sources.get("title_filter") or {}).get("skip_dream_companies", True))
    conn = connect()
    now = now_iso()
    total_new = total_seen = total_dropped = 0
    untargeted: list[str] = []

    for name in ADAPTERS:
        cfg = sources.get(name) or {}
        if not cfg.get("enabled"):
            if cfg.get(REGION_GATED):
                print(region_skip_line(name, cfg))
            continue
        missing = missing_targeting(name, cfg)
        if missing:
            untargeted.append(f"{name} ({', '.join(missing)})")
            continue
        try:
            mod = importlib.import_module(f".adapters.{name}", package="src")
            jobs = mod.fetch(cfg)
        except Exception as e:  # noqa: BLE001, one bad source shouldn't kill the run
            print(f"  ! {name:15s} FAILED: {e}")
            _record_run(conn, now, name, ok=False, error=str(e)[:300])
            continue

        pulled = len(jobs)
        jobs = [j for j in jobs
                if keep_title(cfg, j.title) or (skip_dream and is_dream(j.company))]
        dropped = pulled - len(jobs)

        new = seen = 0
        for job in jobs:
            status = None
            try:
                status = _upsert(conn, job, now)
            except Exception as e:  # noqa: BLE001
                print(f"    · skipped one {name} row: {e}")
                continue
            if status == "new":
                new += 1
            else:
                seen += 1
        _record_run(conn, now, name, pulled=len(jobs), new=new, seen=seen)
        conn.commit()
        total_new += new
        total_seen += seen
        total_dropped += dropped
        off_family = f"  [-{dropped} off-family]" if dropped else ""
        print(f"  ✓ {name:15s} {new:4d} new  {seen:4d} seen  "
              f"({len(jobs)} kept of {pulled} pulled){off_family}")

    if untargeted:
        print(f"  - skipped, no targeting in config/sources.local.yaml: {'; '.join(untargeted)}"
              "\n    (fill in the keys named above there, or let /jh-setup ask for them)")
    print(f"\nDone. {total_new} new jobs added, {total_seen} already known, "
          f"{total_dropped} dropped by the role-family title gate.")

    from .maintain import run as maintain
    m = maintain(conn)
    print(f"Maintenance: {m['expired']} expired, {m['pruned']} descriptions pruned"
          f"{', VACUUMed' if m['vacuumed'] else ''}.")
    print("Next:  /jh-hunt in your agent CLI runs the whole loop; /jh-triage then /jh-match score "
          "only (or `python -m src.hunt run --from triage --to match`).")


def _upsert(conn, job, now) -> str:
    from .db import upsert_job

    return upsert_job(conn, job.to_row(), now)


def _record_run(conn, now: str, source: str, *, pulled: int = 0, new: int = 0,
                seen: int = 0, ok: bool = True, error: str | None = None) -> None:
    """Health log per source per run; the digest flags sources that go quiet."""
    conn.execute(
        "INSERT INTO runs (ts, source, pulled, new, seen, ok, error) VALUES (?,?,?,?,?,?,?)",
        (now, source, pulled, new, seen, int(ok), error),
    )


if __name__ == "__main__":
    main()
