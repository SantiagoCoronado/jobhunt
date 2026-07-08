"""Adzuna aggregator API (Mexico + 12 countries). Free app_id + app_key.
GET https://api.adzuna.com/v1/api/jobs/{country}/search/{page}
Docs: https://developer.adzuna.com  (keys go in .env, see .env.example)
"""
from __future__ import annotations

from . import get_json
from ..config import get_secret
from ..models import Job, strip_html

_CCY = {"mx": "MXN", "us": "USD", "gb": "GBP", "ca": "CAD", "au": "AUD"}


def fetch(cfg: dict) -> list[Job]:
    app_id = get_secret("ADZUNA_APP_ID")
    app_key = get_secret("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        print("  ! adzuna: set ADZUNA_APP_ID and ADZUNA_APP_KEY in .env (see .env.example)")
        return []

    country = (cfg.get("country") or "mx").lower()
    per_page = cfg.get("results_per_page", 50)
    pages = cfg.get("pages", 2)
    queries = cfg.get("queries") or [""]
    where = cfg.get("where")

    jobs: list[Job] = []
    for what in queries:
        for page in range(1, pages + 1):
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
            params = {
                "app_id": app_id,
                "app_key": app_key,
                "results_per_page": per_page,
                "content-type": "application/json",
            }
            if what:
                params["what"] = what
            if where:
                params["where"] = where
            try:
                data = get_json(url, params=params)
            except Exception as e:  # noqa: BLE001, skip a bad page, keep the rest
                print(f"    · adzuna '{what}' p{page} failed: {e}")
                break
            results = data.get("results", [])
            if not results:
                break
            for j in results:
                loc = (j.get("location") or {}).get("display_name", "")
                jobs.append(Job(
                    source="adzuna",
                    external_id=str(j.get("id")),
                    url=j.get("redirect_url", ""),
                    company=(j.get("company") or {}).get("display_name", ""),
                    title=j.get("title", ""),
                    location=loc,
                    remote="remote" in (j.get("title", "") + " " + loc).lower(),
                    description=strip_html(j.get("description", "")),
                    salary_min=int(j["salary_min"]) if j.get("salary_min") else None,
                    salary_max=int(j["salary_max"]) if j.get("salary_max") else None,
                    currency=_CCY.get(country),
                    posted_at=j.get("created"),
                    tags=[t for t in [(j.get("category") or {}).get("label")] if t],
                    raw={},
                ))
    return jobs
