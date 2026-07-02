"""RemoteOK API, free JSON. NOTE: index 0 is a legal/metadata object (skip it).
Attribution required: link back to the RemoteOK URL (no redirects).
GET https://remoteok.com/api
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    data = get_json("https://remoteok.com/api")
    jobs: list[Job] = []
    for j in data[1:]:  # skip legal notice at index 0
        if not isinstance(j, dict) or not j.get("id"):
            continue
        jobs.append(Job(
            source="remoteok",
            external_id=str(j["id"]),
            url=j.get("url", ""),
            company=j.get("company", ""),
            title=j.get("position", ""),
            location=j.get("location", "Remote"),
            remote=True,
            description=strip_html(j.get("description", "")),
            salary_min=j.get("salary_min") or None,
            salary_max=j.get("salary_max") or None,
            currency="USD" if j.get("salary_min") else None,
            posted_at=j.get("date"),
            tags=j.get("tags", []) or [],
            raw=j,
        ))
    return jobs
