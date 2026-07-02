"""Himalayas remote-jobs API, free, no key. Remote-only, often includes annual salary.
GET https://himalayas.app/jobs/api?limit=100
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html


def _int(v):
    try:
        return int(v) if v else None
    except (ValueError, TypeError):
        return None


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    data = get_json("https://himalayas.app/jobs/api", params={"limit": cfg.get("limit", 100)})
    for j in data.get("jobs", []):
        locs = j.get("locationRestrictions") or []
        jobs.append(Job(
            source="himalayas",
            external_id=str(j.get("guid") or j.get("id")),
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
    return jobs
