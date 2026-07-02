"""Remotive API, free JSON. ToS: <=~4 calls/day, credit + link back.
GET https://remotive.com/api/remote-jobs?category=&search=&limit=
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    categories = cfg.get("categories") or [None]  # None => all
    for cat in categories:
        params = {"limit": cfg.get("limit", 100)}
        if cat:
            params["category"] = cat
        data = get_json("https://remotive.com/api/remote-jobs", params=params)
        for j in data.get("jobs", []):
            jobs.append(Job(
                source="remotive",
                external_id=str(j["id"]),
                url=j.get("url", ""),
                company=j.get("company_name", ""),
                title=j.get("title", ""),
                location=j.get("candidate_required_location", "Remote"),
                remote=True,
                description=strip_html(j.get("description", "")),
                posted_at=j.get("publication_date"),
                tags=j.get("tags", []) or [],
                raw=j,
            ))
    return jobs
