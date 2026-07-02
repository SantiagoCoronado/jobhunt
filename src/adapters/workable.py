"""Workable public widget API, no auth. EXPERIMENTAL: schema varies by account.
GET https://apply.workable.com/api/v1/widget/accounts/{account}
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    for account in cfg.get("accounts", []):
        url = f"https://apply.workable.com/api/v1/widget/accounts/{account}"
        try:
            data = get_json(url, params={"details": "true"})
        except Exception:
            continue
        items = data.get("jobs") or data.get("results") or []
        for j in items:
            loc = " ".join(str(x) for x in [j.get("city"), j.get("country")] if x)
            jobs.append(Job(
                source="workable",
                external_id=str(j.get("shortcode") or j.get("id")),
                url=j.get("url") or j.get("application_url", ""),
                company=account.replace("-", " ").title(),
                title=j.get("title", ""),
                location=loc or j.get("location", ""),
                remote=bool(j.get("remote")) or "remote" in loc.lower(),
                description=strip_html(j.get("description", "")),
                posted_at=j.get("published_on") or j.get("created_at"),
                raw=j,
            ))
    return jobs
