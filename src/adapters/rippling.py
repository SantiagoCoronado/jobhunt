"""Rippling ATS public job board API, no key, per company.
GET https://api.rippling.com/platform/api/ats/v1/board/{slug}/jobs
The list carries name, department, workLocation and the posting URL; no
description text (a per-job detail call would be needed for that).
cfg.companies: list of board slugs; optional cfg.names: {slug: "Display Name"}.
"""
from __future__ import annotations

from . import get_json, remote_from_text, require_id
from ..models import Job


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    names = cfg.get("names") or {}
    for slug in cfg.get("companies", []):
        url = f"https://api.rippling.com/platform/api/ats/v1/board/{slug}/jobs"
        try:
            data = get_json(url, headers={"User-Agent": "Mozilla/5.0"})
        except Exception as e:  # noqa: BLE001, skip a bad slug, keep the rest
            print(f"    · rippling '{slug}' failed: {e}")
            continue
        company = names.get(slug) or slug.replace("-", " ").title()
        for j in data if isinstance(data, list) else data.get("items", []):
            try:
                ext = require_id(j, "uuid", "id", "url")
            except KeyError as e:
                print(f"    · rippling '{slug}' skipped a row: {e}")
                continue
            loc = (j.get("workLocation") or {}).get("label", "") or ""
            title = (j.get("name") or "").strip()
            dept = (j.get("department") or {}).get("label")
            jobs.append(Job(
                source="rippling",
                external_id=f"{slug}:{ext}",
                url=j.get("url") or f"https://ats.rippling.com/{slug}/jobs/{ext}",
                company=company,
                title=title,
                location=loc,
                remote=remote_from_text(loc, title),
                description="",
                posted_at=None,
                tags=[dept] if dept else [],
                raw={},
            ))
    return jobs
