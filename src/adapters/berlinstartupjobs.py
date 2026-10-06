"""Berlin Startup Jobs (Germany), the category RSS feed the site publishes, no key.
GET https://berlinstartupjobs.com/{category}/feed/?paged=N
robots.txt allows `/` for every agent; the board answers the project's own User-Agent and
throttles browser-looking ones. Verified 2026-10-06, docs/sources-europe.md.

cfg keys:
  categories: list[str]  -> feed categories (default [engineering])
  pages:      int        -> feed pages per category (about 12 items each; a 404 ends it)
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from . import get_text
from ..models import Job, strip_html

BASE = "https://berlinstartupjobs.com"
_ID = re.compile(r"[?&]p=(\d+)")


def parse(xml_text: str) -> list[Job]:
    root = ET.fromstring(xml_text)
    jobs: list[Job] = []
    for item in root.iter("item"):
        raw_title = strip_html(item.findtext("title") or "")
        role, sep, company = raw_title.rpartition(" // ")
        title, company = (role.strip(), company.strip()) if sep else (raw_title, "")
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or link).strip()
        ident = _ID.search(guid)
        jobs.append(Job(
            source="berlinstartupjobs",
            external_id=ident.group(1) if ident else guid,
            url=link,
            company=company,
            title=title,
            location="Berlin, Germany",
            remote="remote" in title.lower(),
            description=strip_html(item.findtext("description") or ""),
            posted_at=item.findtext("pubDate"),
            tags=[c.text.strip() for c in item.findall("category") if c.text][:4],
            raw={},
        ))
    return jobs


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    seen: set[str] = set()
    for cat in cfg.get("categories") or ["engineering"]:
        for page in range(1, int(cfg.get("pages", 3)) + 1):
            params = {"paged": page} if page > 1 else None
            try:
                batch = parse(get_text(f"{BASE}/{cat}/feed/", params=params))
            except Exception as e:  # noqa: BLE001
                if page == 1:
                    print(f"    . berlinstartupjobs '{cat}' failed: {e}")
                break                       # past the last page the feed 404s
            if not batch:
                break
            for job in batch:
                if job.external_id not in seen:
                    seen.add(job.external_id)
                    jobs.append(job)
    return jobs
