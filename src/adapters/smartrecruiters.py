"""SmartRecruiters public postings API, free, no key, per company.
GET https://api.smartrecruiters.com/v1/companies/{company}/postings?limit=100
Note: the list endpoint has no job description, so matching leans on title + location.
"""
from __future__ import annotations

from . import get_json
from ..models import Job


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    for company in cfg.get("companies", []):
        try:
            data = get_json(
                f"https://api.smartrecruiters.com/v1/companies/{company}/postings",
                params={"limit": 100},
            )
        except Exception as e:  # noqa: BLE001
            print(f"    . smartrecruiters '{company}' failed: {e}")
            continue
        for p in data.get("content", []):
            loc = p.get("location") or {}
            parts = [loc.get("city"), loc.get("region"), loc.get("country")]
            locstr = ", ".join(x for x in parts if x)
            if loc.get("remote"):
                locstr = (locstr + " (remote)").strip()
            jobs.append(Job(
                source="smartrecruiters",
                external_id=str(p.get("id")),
                url=f"https://jobs.smartrecruiters.com/{company}/{p.get('id')}",
                company=(p.get("company") or {}).get("name", company),
                title=p.get("name", ""),
                location=locstr,
                remote=bool(loc.get("remote")),
                description="",
                posted_at=p.get("releasedDate"),
                raw={},
            ))
    return jobs
