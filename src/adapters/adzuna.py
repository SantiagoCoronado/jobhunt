"""Adzuna aggregator API (Mexico + 12 countries). Free app_id + app_key.
GET https://api.adzuna.com/v1/api/jobs/{country}/search/{page}
Docs: https://developer.adzuna.com  (keys go in .env, see .env.example)
"""
from __future__ import annotations

from . import get_json, int_or_none, paginate, remote_from_text, require_id
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
        def fetch_page(page: int, what=what):
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
            return get_json(url, params=params).get("results", [])

        for j in paginate(fetch_page, pages, label=f"adzuna '{what}'"):
            loc = (j.get("location") or {}).get("display_name", "")
            try:
                ext_id = require_id(j, "id", "redirect_url")
            except KeyError:
                continue  # a row with no identity can't be upserted safely
            jobs.append(Job(
                source="adzuna",
                external_id=ext_id,
                url=j.get("redirect_url", ""),
                company=(j.get("company") or {}).get("display_name", ""),
                title=j.get("title", ""),
                location=loc,
                remote=remote_from_text(j.get("title"), loc),
                description=strip_html(j.get("description", "")),
                salary_min=int_or_none(j.get("salary_min")),
                salary_max=int_or_none(j.get("salary_max")),
                currency=_CCY.get(country),
                posted_at=j.get("created"),
                tags=[t for t in [(j.get("category") or {}).get("label")] if t],
                raw={},
            ))
    return jobs
