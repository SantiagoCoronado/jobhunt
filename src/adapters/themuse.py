"""The Muse public jobs API. Works anon (500/hr); optional key raises the limit.
GET https://www.themuse.com/api/public/jobs?page=&category=&location=
Docs: https://www.themuse.com/developers/api/v2  (THEMUSE_API_KEY optional, .env)
"""
from __future__ import annotations

from . import get_json
from ..config import get_secret
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    pages = cfg.get("pages", 3)
    categories = cfg.get("categories") or [None]
    locations = cfg.get("locations") or cfg.get("location")
    if isinstance(locations, str):
        locations = [locations]
    level = cfg.get("level")
    api_key = get_secret("THEMUSE_API_KEY")

    jobs: list[Job] = []
    for cat in categories:
        for page in range(1, pages + 1):
            params: dict = {"page": page}
            if cat:
                params["category"] = cat
            if locations:
                params["location"] = locations  # requests repeats the key per value
            if level:
                params["level"] = level
            if api_key:
                params["api_key"] = api_key
            try:
                data = get_json("https://www.themuse.com/api/public/jobs", params=params)
            except Exception as e:  # noqa: BLE001, skip a bad page, keep the rest
                print(f"    · themuse cat={cat} p{page} failed: {e}")
                break
            results = data.get("results", [])
            if not results:
                break
            for j in results:
                locs = [(l or {}).get("name", "") for l in (j.get("locations") or [])]
                loc = ", ".join(l for l in locs if l)
                remote = any("remote" in l.lower() or "flexible" in l.lower() for l in locs)
                jobs.append(Job(
                    source="themuse",
                    external_id=str(j.get("id")),
                    url=(j.get("refs") or {}).get("landing_page", ""),
                    company=(j.get("company") or {}).get("name", ""),
                    title=j.get("name", ""),
                    location=loc,
                    remote=remote,
                    description=strip_html(j.get("contents", "")),
                    posted_at=j.get("publication_date"),
                    tags=[(l or {}).get("name") for l in (j.get("levels") or []) if (l or {}).get("name")],
                    raw={},
                ))
    return jobs
