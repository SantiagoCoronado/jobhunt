"""Stage ①: pull every enabled source -> normalize -> upsert into SQLite.

Run:  python -m src.discover
Config: config/sources.yaml  (which ATS tokens / aggregators to pull)
"""
from __future__ import annotations

import importlib

from .adapters import keep_title
from .config import load_yaml
from .db import connect
from .models import now_iso

# adapter module name -> friendly label
ADAPTERS = [
    # ATS boards
    "greenhouse", "lever", "ashby", "workable",
    "personio", "bamboohr", "workday", "softserve",
    # Aggregators
    "remoteok", "remotive", "weworkremotely", "hackernews", "getonbrd",
    "jobicy", "arbeitnow", "himalayas", "recruitee", "smartrecruiters",
    "adzuna", "themuse", "findwork", "careerjet", "torre", "posthog",
    "consider", "workatastartup",
]


def main() -> None:
    sources = load_yaml("sources.yaml")
    conn = connect()
    now = now_iso()
    total_new = total_seen = total_dropped = 0

    for name in ADAPTERS:
        cfg = sources.get(name) or {}
        if not cfg.get("enabled"):
            continue
        try:
            mod = importlib.import_module(f".adapters.{name}", package="src")
            jobs = mod.fetch(cfg)
        except Exception as e:  # noqa: BLE001, one bad source shouldn't kill the run
            print(f"  ! {name:15s} FAILED: {e}")
            _record_run(conn, now, name, ok=False, error=str(e)[:300])
            continue

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

    print(f"\nDone. {total_new} new jobs added, {total_seen} already known, "
          f"{total_dropped} dropped by the role-family title gate.")

    from .maintain import run as maintain
    m = maintain(conn)
    print(f"Maintenance: {m['expired']} expired, {m['pruned']} descriptions pruned"
          f"{', VACUUMed' if m['vacuumed'] else ''}.")
    print("Next:  python -m src.match export   then run /jh-match in Claude Code.")


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
