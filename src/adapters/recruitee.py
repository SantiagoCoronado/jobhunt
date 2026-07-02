"""Recruitee public offers API, free, no key, per company. Includes descriptions.
GET https://{company}.recruitee.com/api/offers/
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    for company in cfg.get("companies", []):
        try:
            data = get_json(f"https://{company}.recruitee.com/api/offers/")
        except Exception as e:  # noqa: BLE001
            print(f"    . recruitee '{company}' failed: {e}")
            continue
        for o in data.get("offers", []):
            loc = ", ".join(x for x in [o.get("city"), o.get("country")] if x)
            jobs.append(Job(
                source="recruitee",
                external_id=str(o.get("id")),
                url=o.get("careers_url") or o.get("careers_apply_url", ""),
                company=company.replace("-", " ").title(),
                title=o.get("title", ""),
                location=loc or o.get("location") or ("Remote" if o.get("remote") else ""),
                remote=bool(o.get("remote")),
                description=strip_html(o.get("description", "")),
                posted_at=o.get("published_at"),
                tags=[t for t in [o.get("department"), o.get("employment_type")] if t],
                raw={},
            ))
    return jobs
