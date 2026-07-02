"""Jobicy remote-jobs API, free, no key. Includes annual salary (USD) when known.
GET https://jobicy.com/api/v2/remote-jobs?count=100&tag=python
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html


def _int(v):
    try:
        return int(v) if v not in (None, "", 0, "0") else None
    except (ValueError, TypeError):
        return None


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    count = cfg.get("count", 100)
    tags = cfg.get("tags") or [None]
    for tag in tags:
        params = {"count": count}
        if tag:
            params["tag"] = tag
        try:
            data = get_json("https://jobicy.com/api/v2/remote-jobs", params=params)
        except Exception as e:  # noqa: BLE001
            print(f"    . jobicy tag '{tag}' failed: {e}")
            continue
        for j in data.get("jobs", []):
            jobs.append(Job(
                source="jobicy",
                external_id=str(j.get("id")),
                url=j.get("url", ""),
                company=j.get("companyName", ""),
                title=j.get("jobTitle", ""),
                location=j.get("jobGeo", "Remote"),
                remote=True,
                description=strip_html(j.get("jobExcerpt") or j.get("jobDescription", "")),
                salary_min=_int(j.get("annualSalaryMin")),
                salary_max=_int(j.get("annualSalaryMax")),
                currency=(j.get("salaryCurrency") or None),
                posted_at=j.get("pubDate"),
                tags=(j.get("jobIndustry") or [])[:5],
                raw={},
            ))
    return jobs
