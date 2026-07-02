"""Ashby public posting API, no auth, includes compensation.
GET https://api.ashbyhq.com/posting-api/job-board/{client}?includeCompensation=true
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    for client in cfg.get("clients", []):
        url = f"https://api.ashbyhq.com/posting-api/job-board/{client}"
        try:
            data = get_json(url, params={"includeCompensation": "true"})
        except Exception as e:  # noqa: BLE001, skip a bad client, keep the rest
            print(f"    · ashby client '{client}' failed: {e}")
            continue
        for j in data.get("jobs", []):
            comp = j.get("compensation") or {}
            crange = (comp.get("compensationTierSummary") or "")
            jobs.append(Job(
                source="ashby",
                external_id=str(j.get("id")),
                url=j.get("applyUrl") or j.get("jobUrl", ""),
                company=client.replace("-", " ").title(),
                title=j.get("title", ""),
                location=j.get("location", ""),
                remote=bool(j.get("isRemote")),
                description=strip_html(j.get("descriptionHtml") or j.get("descriptionPlain", "")),
                posted_at=j.get("publishedAt"),
                tags=[t for t in [j.get("department"), j.get("team"), j.get("employmentType")] if t],
                raw={"compensation": crange, **{k: j[k] for k in list(j)[:0]}},
            ))
    return jobs
