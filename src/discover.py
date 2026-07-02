"""Stage ①: pull every enabled source -> normalize -> upsert into SQLite.

Run:  python -m src.discover
Config: config/sources.yaml  (which ATS tokens / aggregators to pull)
"""
from __future__ import annotations

import importlib

from .config import load_yaml
from .db import connect
from .models import now_iso

# adapter module name -> friendly label
ADAPTERS = [
    "greenhouse", "lever", "ashby", "workable",
    "remoteok", "remotive", "weworkremotely", "hackernews", "getonbrd",
    "jobicy", "arbeitnow", "himalayas", "recruitee", "smartrecruiters",
]


def main() -> None:
    sources = load_yaml("sources.yaml")
    conn = connect()
    now = now_iso()
    total_new = total_seen = 0

    for name in ADAPTERS:
        cfg = sources.get(name) or {}
        if not cfg.get("enabled"):
            continue
        try:
            mod = importlib.import_module(f".adapters.{name}", package="src")
            jobs = mod.fetch(cfg)
        except Exception as e:  # noqa: BLE001, one bad source shouldn't kill the run
            print(f"  ! {name:15s} FAILED: {e}")
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
        conn.commit()
        total_new += new
        total_seen += seen
        print(f"  ✓ {name:15s} {new:4d} new  {seen:4d} seen  ({len(jobs)} pulled)")

    print(f"\nDone. {total_new} new jobs added, {total_seen} already known.")
    print("Next:  python -m src.match export   then run the /match command in Claude Code.")


def _upsert(conn, job, now) -> str:
    from .db import upsert_job

    return upsert_job(conn, job.to_row(), now)


if __name__ == "__main__":
    main()
