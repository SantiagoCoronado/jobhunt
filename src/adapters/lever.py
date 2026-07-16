"""Lever postings API, read-only, no auth.
GET https://api.lever.co/v0/postings/{company}?mode=json
"""
from __future__ import annotations

from datetime import datetime, UTC

from . import get_json
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    for company in cfg.get("companies", []):
        url = f"https://api.lever.co/v0/postings/{company}"
        try:
            data = get_json(url, params={"mode": "json"})
        except Exception as e:  # noqa: BLE001, skip a bad company, keep the rest
            print(f"    · lever company '{company}' failed: {e}")
            continue
        for j in data:
            cats = j.get("categories") or {}
            loc = cats.get("location", "")
            workplace = (j.get("workplaceType") or "").lower()
            posted = None
            if j.get("createdAt"):
                posted = datetime.fromtimestamp(j["createdAt"] / 1000, UTC).isoformat()
            jobs.append(Job(
                source="lever",
                external_id=str(j["id"]),
                url=j.get("hostedUrl", ""),
                company=company.replace("-", " ").title(),
                title=j.get("text", ""),
                location=loc,
                remote=workplace == "remote" or "remote" in loc.lower(),
                description=strip_html(j.get("descriptionPlain") or j.get("description", "")),
                posted_at=posted,
                tags=[t for t in [cats.get("team"), cats.get("commitment")] if t],
                raw=j,
            ))
    return jobs
