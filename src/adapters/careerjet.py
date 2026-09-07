"""Careerjet affiliate job search (locale and location from config/sources.local.yaml). Needs a partner affid.
GET http://public.api.careerjet.net/search   (a Referer header is required)
NOTE: the legacy public endpoint now serves only pre-existing legacy affiliates; new
partners must use the v4 API (https://www.careerjet.com/partners/api).
cfg.keywords: search terms. cfg.pages: how deep to page each term (the response
reports `pages`, and a single MX keyword like "developer" spans ~25 pages of 50).
"""
from __future__ import annotations

import hashlib

from . import get_json
from ..config import get_secret
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    affid = get_secret("CAREERJET_AFFID")
    if not affid:
        print("  ! careerjet: set CAREERJET_AFFID in .env (see .env.example)")
        return []

    locale = cfg.get("locale_code")
    location = cfg.get("location")
    if not locale or not location:
        raise ValueError("careerjet: set `locale_code:` and `location:` in config/sources.local.yaml (no defaults)")
    pagesize = cfg.get("pagesize", 50)
    max_pages = cfg.get("pages", 1)
    keywords = cfg.get("keywords") or [""]
    headers = {"Referer": "https://github.com/ (jobhunt personal search)"}

    jobs: list[Job] = []
    for kw in keywords:
        jobs.extend(_keyword(kw, locale, location, pagesize, max_pages, affid, headers))
    return jobs


def _keyword(kw, locale, location, pagesize, max_pages, affid, headers) -> list[Job]:
    out: list[Job] = []
    for page in range(1, max_pages + 1):
        params = {
            "locale_code": locale, "location": location, "keywords": kw,
            "affid": affid, "pagesize": pagesize, "page": page,
            "user_ip": "127.0.0.1", "user_agent": "jobhunt/0.1",
        }
        try:
            data = get_json("http://public.api.careerjet.net/search",
                            params=params, headers=headers)
        except Exception as e:  # noqa: BLE001, skip a bad page, keep the rest
            print(f"    · careerjet '{kw}' p{page} failed: {e}")
            break
        if data.get("type") != "JOBS":
            print(f"    · careerjet '{kw}' p{page}: {data.get('error') or data.get('type')}")
            break
        batch = data.get("jobs", [])
        if not batch:
            break
        for j in batch:
            url = j.get("url", "")
            locs = j.get("locations", location)
            out.append(Job(
                source="careerjet",
                external_id=hashlib.sha1(url.encode()).hexdigest()[:16],
                url=url,
                company=j.get("company", ""),
                title=j.get("title", ""),
                location=locs,
                remote="remote" in (j.get("title", "") + " " + locs).lower(),
                description=strip_html(j.get("description", "")),
                posted_at=j.get("date"),
                raw={},
            ))
        if page >= (data.get("pages") or max_pages):
            break
    return out
