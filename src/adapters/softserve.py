"""SoftServe careers (career.softserveinc.com) adapter.

SoftServe's own public careers board. We use only the ToS-safe path: the SEO
sitemap (`sitemap/vacancy.xml`, crawler-sanctioned) enumerates every vacancy,
and each vacancy page carries JSON-LD schema.org/JobPosting, the same structured
data Google Jobs consumes. We never touch SoftServe's robots-disallowed
`*/query` search API.

cfg keys (all optional):
  countries: list[str]  -> keep only vacancies whose applicant country matches
  limit:     int        -> cap number of sitemap URLs fetched (testing)
  workers:   int        -> page-fetch concurrency (default 6)
"""
from __future__ import annotations

import html
import json
import re
from concurrent.futures import ThreadPoolExecutor

from ..models import Job, strip_html
from . import get_text

BASE = "https://career.softserveinc.com"
SITEMAP = f"{BASE}/sitemap/vacancy.xml"

_LOC = re.compile(r"<loc>([^<]+)</loc>")
_LD = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S)
_ID = re.compile(r"-(\d+)/?$")


def _country(posting: dict) -> str:
    alr = posting.get("applicantLocationRequirements")
    if isinstance(alr, dict):
        return alr.get("name") or ""
    if isinstance(alr, list):
        return ", ".join(x.get("name", "") for x in alr if isinstance(x, dict))
    return ""


def _city(posting: dict) -> str:
    jl = posting.get("jobLocation")
    if isinstance(jl, list):
        jl = jl[0] if jl else None
    if isinstance(jl, dict):
        addr = jl.get("address") or {}
        if isinstance(addr, dict):
            return " ".join(
                b for b in (addr.get("addressLocality"), addr.get("addressRegion")) if b
            )
    return ""


def _parse_vacancy(url: str) -> Job | None:
    page = get_text(url, timeout=20)
    posting = None
    for block in _LD.findall(page):
        try:
            data = json.loads(block.strip())
        except Exception:  # noqa: BLE001
            continue
        t = data.get("@type")
        if t == "JobPosting" or (isinstance(t, list) and "JobPosting" in t):
            posting = data
            break
    if not posting:
        return None
    title = (posting.get("title") or "").strip()
    if not title:
        return None

    m = _ID.search(url)
    ext = m.group(1) if m else url
    remote = str(posting.get("jobLocationType") or "").upper() == "TELECOMMUTE"
    country = _country(posting)
    loc = ", ".join(b for b in (_city(posting), country) if b)
    if remote:
        loc = f"Remote ({loc})" if loc else "Remote"

    return Job(
        source="softserve",
        external_id=str(ext),
        url=url.split("?")[0],
        company="SoftServe",
        title=title,
        location=loc,
        remote=remote,
        description=strip_html(html.unescape(posting.get("description") or "")),
        posted_at=posting.get("datePosted"),
        raw={"country": country},
    )


def _safe(url: str) -> Job | None:
    try:
        return _parse_vacancy(url)
    except Exception:  # noqa: BLE001, one bad page shouldn't drop the batch
        return None


def fetch(cfg: dict) -> list[Job]:
    countries = [c.lower() for c in (cfg.get("countries") or [])]
    limit = cfg.get("limit")
    workers = int(cfg.get("workers", 6))
    try:
        xml = get_text(SITEMAP, timeout=30)
    except Exception as e:  # noqa: BLE001
        print(f"    softserve: sitemap fetch failed: {e}")
        return []
    urls = _LOC.findall(xml)
    if limit:
        urls = urls[: int(limit)]

    jobs: list[Job] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for job in ex.map(_safe, urls):
            if job is None:
                continue
            if countries:
                c = (job.raw.get("country") or "").lower()
                if not any(k in c for k in countries):
                    continue
            jobs.append(job)
    return jobs
