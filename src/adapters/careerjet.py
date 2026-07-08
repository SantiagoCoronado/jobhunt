"""Careerjet affiliate job search (Mexico via es_MX locale). Needs a partner affid.
GET http://public.api.careerjet.net/search   (a Referer header is required)
NOTE: the legacy public endpoint now serves only pre-existing legacy affiliates; new
partners must use the v4 API (https://www.careerjet.com/partners/api). Ships DISABLED
until a working affid is confirmed live. cfg.keywords: search terms.
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

    locale = cfg.get("locale_code", "es_MX")
    location = cfg.get("location", "Mexico")
    pagesize = cfg.get("pagesize", 50)
    keywords = cfg.get("keywords") or [""]
    headers = {"Referer": "https://github.com/ (jobhunt personal search)"}

    jobs: list[Job] = []
    for kw in keywords:
        params = {
            "locale_code": locale, "location": location, "keywords": kw,
            "affid": affid, "pagesize": pagesize, "page": 1,
            "user_ip": "127.0.0.1", "user_agent": "jobhunt/0.1",
        }
        try:
            data = get_json("http://public.api.careerjet.net/search", params=params, headers=headers)
        except Exception as e:  # noqa: BLE001, skip a bad query, keep the rest
            print(f"    · careerjet '{kw}' failed: {e}")
            continue
        if data.get("type") != "JOBS":
            print(f"    · careerjet '{kw}': {data.get('error') or data.get('type')}")
            continue
        for j in data.get("jobs", []):
            url = j.get("url", "")
            locs = j.get("locations", location)
            jobs.append(Job(
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
    return jobs
