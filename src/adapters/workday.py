"""Workday CxS public job search (POST JSON, no key). Unlocks large enterprises.
POST https://{tenant}.wd{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
cfg.sites: list of {tenant, wd, site, name?, search?}. The list endpoint has no
description text (a per-job detail call would be needed for that).
"""
from __future__ import annotations

from . import post_json
from ..models import Job


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    per_page = cfg.get("limit", 20)
    max_pages = cfg.get("pages", 3)
    for site in cfg.get("sites", []):
        tenant = site.get("tenant")
        wd = site.get("wd", 5)
        board = site.get("site")
        if not tenant or not board:
            continue
        host = f"https://{tenant}.wd{wd}.myworkdayjobs.com"
        url = f"{host}/wday/cxs/{tenant}/{board}/jobs"
        display = (site.get("name") or tenant).replace("-", " ").title()
        for page in range(max_pages):
            body = {
                "appliedFacets": {},
                "limit": per_page,
                "offset": page * per_page,
                "searchText": site.get("search", ""),
            }
            try:
                data = post_json(url, json=body, headers={"Accept": "application/json"})
            except Exception as e:  # noqa: BLE001, skip a bad site, keep the rest
                print(f"    · workday '{tenant}' p{page} failed: {e}")
                break
            postings = data.get("jobPostings", [])
            if not postings:
                break
            for j in postings:
                path = j.get("externalPath", "")
                locs = j.get("locationsText", "")
                jobs.append(Job(
                    source="workday",
                    external_id=f"{tenant}:{path}",
                    url=f"{host}/en-US/{board}{path}",
                    company=display,
                    title=j.get("title", ""),
                    location=locs,
                    remote="remote" in (locs + " " + j.get("title", "")).lower(),
                    description="",
                    posted_at=None,  # only a relative "Posted 30+ Days Ago" string is given
                    tags=(j.get("bulletFields") or [])[:3],
                    raw={},
                ))
    return jobs
