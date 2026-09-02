"""Teamtailor public JSON Feed, no key, per company.
GET https://{slug}.teamtailor.com/jobs.json  (JSON Feed 1.x; each item carries a
schema.org JobPosting under `_jobposting` with the location and org name).
cfg.companies: list of slugs, optional cfg.names: {slug: "Display Name"}.
"""
from __future__ import annotations

from . import get_json, remote_from_text, require_id
from ..models import Job, strip_html


def _location(posting: dict) -> str:
    parts = []
    for place in posting.get("jobLocation") or []:
        addr = (place or {}).get("address") or {}
        bits = [addr.get("addressLocality"), addr.get("addressRegion"), addr.get("addressCountry")]
        s = ", ".join(b for b in bits if b)
        if s and s not in parts:
            parts.append(s)
    if posting.get("jobLocationType") == "TELECOMMUTE":
        parts.append("Remote")
    return " / ".join(parts)


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    names = cfg.get("names") or {}
    for slug in cfg.get("companies", []):
        url = f"https://{slug}.teamtailor.com/jobs.json"
        try:
            data = get_json(url)
        except Exception as e:  # noqa: BLE001, skip a bad slug, keep the rest
            print(f"    · teamtailor '{slug}' failed: {e}")
            continue
        for item in data.get("items", []):
            posting = item.get("_jobposting") or {}
            org = (posting.get("hiringOrganization") or {}).get("name")
            company = names.get(slug) or org or slug.replace("-", " ").title()
            loc = _location(posting)
            title = item.get("title") or posting.get("title") or ""
            try:
                ext = require_id(item, "id", "url")
            except KeyError as e:
                print(f"    · teamtailor '{slug}' skipped a row: {e}")
                continue
            jobs.append(Job(
                source="teamtailor",
                external_id=f"{slug}:{ext}",
                url=item.get("url", ""),
                company=company,
                title=title,
                location=loc,
                remote=remote_from_text(loc, title),
                description=strip_html(item.get("content_html") or posting.get("description")),
                posted_at=item.get("date_published") or posting.get("datePosted"),
                raw={},
            ))
    return jobs
