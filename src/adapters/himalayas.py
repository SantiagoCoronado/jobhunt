"""Himalayas remote-jobs API, free, no key. Remote-only, often includes annual salary.
GET https://himalayas.app/jobs/api?limit=100&offset=0

NOTE (measured 2026-08-27): `limit` is IGNORED, the endpoint always returns 20 rows.
Only `offset` moves the window, so one call saw 20 of the board and the source looked
dead (66 new rows in 14 days). `pages` walks the feed in PAGE_SIZE steps instead.
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html

PAGE_SIZE = 20  # server-side, not configurable: `limit` has no effect


def _int(v):
    try:
        return int(v) if v else None
    except (ValueError, TypeError):
        return None


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    seen: set[str] = set()
    pages = cfg.get("pages", 25)
    for page in range(pages):
        try:
            data = get_json("https://himalayas.app/jobs/api",
                            params={"limit": PAGE_SIZE, "offset": page * PAGE_SIZE})
        except Exception as e:  # noqa: BLE001, keep whatever earlier pages returned
            print(f"    · himalayas p{page} failed: {e}")
            break
        batch = data.get("jobs", [])
        if not batch:
            break
        fresh = 0
        for j in batch:
            ext = str(j.get("guid") or j.get("id") or "")
            if not ext or ext in seen:
                continue
            seen.add(ext)
            fresh += 1
            locs = j.get("locationRestrictions") or []
            jobs.append(Job(
                source="himalayas",
                external_id=ext,
                url=j.get("applicationLink") or j.get("url", ""),
                company=j.get("companyName", ""),
                title=j.get("title", ""),
                location=", ".join(locs) if locs else "Remote",
                remote=True,
                description=strip_html(j.get("description") or j.get("excerpt", "")),
                salary_min=_int(j.get("minSalary")),
                salary_max=_int(j.get("maxSalary")),
                currency="USD" if j.get("minSalary") else None,
                posted_at=str(j.get("pubDate") or ""),
                tags=(j.get("categories") or [])[:5],
                raw={},
            ))
        if not fresh:  # offset stopped moving: end of the feed
            break
    return jobs
