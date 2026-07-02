"""Arbeitnow job-board API, free, no key. Has a boolean remote flag.
GET https://www.arbeitnow.com/api/job-board-api?page=1
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    pages = cfg.get("pages", 3)
    remote_only = cfg.get("remote_only", True)
    for p in range(1, pages + 1):
        try:
            data = get_json("https://www.arbeitnow.com/api/job-board-api", params={"page": p})
        except Exception as e:  # noqa: BLE001
            print(f"    . arbeitnow page {p} failed: {e}")
            continue
        items = data.get("data", [])
        if not items:
            break
        for j in items:
            remote = bool(j.get("remote"))
            if remote_only and not remote:
                continue
            jobs.append(Job(
                source="arbeitnow",
                external_id=str(j.get("slug")),
                url=j.get("url", ""),
                company=j.get("company_name", ""),
                title=j.get("title", ""),
                location=(j.get("location") or ("Remote" if remote else "")),
                remote=remote,
                description=strip_html(j.get("description", "")),
                posted_at=str(j.get("created_at") or ""),
                tags=(j.get("tags") or [])[:6],
                raw={},
            ))
    return jobs
