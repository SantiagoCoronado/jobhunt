"""PostHog "Cool tech jobs" board (https://posthog.com/cool-tech-jobs).

Curated list of dev-tool companies with engineer-friendly cultures (PostHog,
Supabase, Zapier, Resend, Mintlify, SigNoz, ...). The page itself is a Gatsby
shell whose page-data is empty: every listing is client-fetched from the public,
unauthenticated Strapi API that backs it, which is what we call here. Small
board (~150 live roles across ~10 companies), so two requests cover it.

Overlaps by design with our Ashby tokens for the same companies; `canonical_key`
collapses the duplicates. The extra value is the companies we do NOT track
directly plus the culture curation.

cfg keys (all optional):
  pages:       int       -> max pages to walk (default 3; Strapi caps pageSize at 100)
  page_size:   int       -> rows per page (default 100)
  departments: list[str] -> keep only these departments, case-insensitive substring
                            match (default [] = keep everything). Values are free
                            text on this board ("Engineering", "Data + Growth", and
                            some company names), so match loosely or not at all.
  remote_only: bool      -> drop non-remote rows (default false)
"""
from __future__ import annotations

from ..models import Job, strip_html
from . import get_json, paginate, remote_from_text, require_id

API = "https://better-animal-d658c56969.strapiapp.com/api/jobs"


def _keep(dept: str, wanted: list[str]) -> bool:
    if not wanted:
        return True
    d = dept.lower()
    return any(w.lower() in d for w in wanted)


def fetch(cfg: dict) -> list[Job]:
    page_size = int(cfg.get("page_size", 100))
    departments = cfg.get("departments") or []
    remote_only = bool(cfg.get("remote_only"))

    def page(n: int) -> list[dict]:
        params = {
            "pagination[page]": n,
            "pagination[pageSize]": page_size,
            "populate": "company",
            "sort[0]": "postedDate:desc",
        }
        return (get_json(API, params=params) or {}).get("data") or []

    jobs: list[Job] = []
    for row in paginate(page, int(cfg.get("pages", 3)), label="posthog"):
        a = row.get("attributes") or {}
        company = ((a.get("company") or {}).get("data") or {}).get("attributes") or {}
        dept = a.get("department") or ""
        if not _keep(dept, departments):
            continue

        location = (a.get("location") or "").strip()
        is_remote = a.get("isRemote")
        remote = bool(is_remote) if is_remote is not None else remote_from_text(location)
        remote = remote or bool(company.get("remoteOnly"))
        if remote_only and not remote:
            continue

        url = a.get("url") or company.get("jobBoardURL") or company.get("url") or ""
        try:
            external_id = require_id(row, "id")
        except KeyError:
            continue

        jobs.append(Job(
            source="posthog",
            external_id=external_id,
            url=url,
            company=company.get("name", ""),
            title=a.get("title", ""),
            location=location or ("Remote" if remote else ""),
            remote=remote,
            description=strip_html(a.get("description") or company.get("description") or ""),
            posted_at=a.get("postedDate") or a.get("publishedAt"),
            tags=[t for t in (dept,) if t][:5],
            raw={},
        ))
    return jobs
