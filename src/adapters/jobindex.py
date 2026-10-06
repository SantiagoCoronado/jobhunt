"""Jobindex (Denmark), the per-search RSS feed each search page advertises, no key.
GET https://www.jobindex.dk/jobsoegning.rss?q=...
One page per query: robots.txt disallows `page=` on /jobsoegning, so depth comes from more
queries. Verified 2026-10-06, docs/sources-europe.md.

cfg keys:
  queries: list[str]  -> one feed each (targeting, from config/sources.local.yaml)
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from . import get_text
from ..models import Job, strip_html

URL = "https://www.jobindex.dk/jobsoegning.rss"
_AREA = re.compile(r'class="jix_robotjob--area"[^>]*>(.*?)</span>', re.S | re.I)
_ALT = re.compile(r'<img[^>]*\balt="([^"]+)"', re.I)
_ID = re.compile(r"(\d+)\s*$")


def _split_title(raw_title: str, description: str) -> tuple[str, str]:
    """Items read "Role, Company". The company is the logo's alt text when the ad has one
    (a company name may hold a comma), else whatever follows the last comma."""
    alt = _ALT.search(description)
    if alt:
        company = strip_html(alt.group(1))
        if company and raw_title.endswith(", " + company):
            return raw_title[: -len(company) - 2].strip(), company
    role, sep, company = raw_title.rpartition(", ")
    return (role.strip(), company.strip()) if sep else (raw_title.strip(), "")


def parse(xml_text: str) -> list[Job]:
    root = ET.fromstring(xml_text)
    jobs: list[Job] = []
    for item in root.iter("item"):
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or link).strip()
        desc = item.findtext("description") or ""
        title, company = _split_title(strip_html(item.findtext("title") or ""), desc)
        area = _AREA.search(desc)
        location = strip_html(area.group(1)) if area else ""
        ident = _ID.search(guid)
        jobs.append(Job(
            source="jobindex",
            external_id=ident.group(1) if ident else guid,
            url=link,
            company=company,
            title=title,
            location=f"{location}, Denmark" if location else "Denmark",
            remote=any(w in location.lower() for w in ("remote", "hjemmefra", "fjern")),
            description=strip_html(desc),
            posted_at=item.findtext("pubDate"),
            tags=[c.text.strip() for c in item.findall("category") if c.text][:4],
            raw={},
        ))
    return jobs


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    seen: set[str] = set()
    for q in cfg.get("queries") or []:
        try:
            batch = parse(get_text(URL, params={"q": q}))
        except Exception as e:  # noqa: BLE001
            print(f"    . jobindex '{q}' failed: {e}")
            continue
        for job in batch:
            if job.external_id not in seen:
                seen.add(job.external_id)
                jobs.append(job)
    return jobs
