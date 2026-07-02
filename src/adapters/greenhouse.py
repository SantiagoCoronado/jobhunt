"""Greenhouse public job board API, no key, sanctioned.
GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    for token in cfg.get("tokens", []):
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
        try:
            data = get_json(url, params={"content": "true"})
        except Exception as e:  # noqa: BLE001, skip a bad token, keep the rest
            print(f"    · greenhouse token '{token}' failed: {e}")
            continue
        company = token.replace("-", " ").title()
        for j in data.get("jobs", []):
            loc = (j.get("location") or {}).get("name", "")
            jobs.append(Job(
                source="greenhouse",
                external_id=str(j["id"]),
                url=j.get("absolute_url", ""),
                company=company,
                title=j.get("title", ""),
                location=loc,
                remote="remote" in loc.lower(),
                description=strip_html(j.get("content", "")),
                posted_at=j.get("updated_at"),
                raw=j,
            ))
    return jobs
