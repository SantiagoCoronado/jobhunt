"""Adzuna aggregator API (13 country sites). Free app_id + app_key.
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

    # `countries:` (a list) supersedes the older single `country:`; the home country for
    # local roles, the US site for USD-priced remote roles that hire abroad. Adzuna
    # allows ~250 calls/day, so keep countries x queries x pages under that.
    countries = cfg.get("countries") or ([cfg["country"]] if cfg.get("country") else [])
    if not countries:
        raise ValueError("adzuna: set `countries:` in config/sources.local.yaml (no default country)")
    per_page = cfg.get("results_per_page", 50)
    pages = cfg.get("pages", 2)
    base_queries = cfg.get("queries") or [""]
    per_country_queries = cfg.get("country_queries") or {}
    where_by_country = cfg.get("where_by_country") or {}
    default_where = cfg.get("where")

    jobs: list[Job] = []
    for raw_country in countries:
        country = str(raw_country).lower()
        queries = per_country_queries.get(country) or base_queries
        where = where_by_country.get(country, default_where)
        for what in queries:
            jobs.extend(_search(country, what, where, app_id, app_key, per_page, pages))
    return jobs


def _search(country, what, where, app_id, app_key, per_page, pages) -> list[Job]:
    """One country x one search term, paged. Split out when `countries:` landed."""
    jobs: list[Job] = []

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

    for j in paginate(fetch_page, pages, label=f"adzuna {country} '{what}'"):
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
