"""Hacker News "Ask HN: Who is hiring?", via the official Algolia HN Search API.

  GET https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring
  GET https://hn.algolia.com/api/v1/search?tags=comment,story_<id>&hitsPerPage=100

Was hnrss.org/whoishiring/jobs.jsonfeed, which started serving HTTP 502 (measured
2026-08-27) and only ever exposed the current month. Algolia is HN's own public
search API, has no key, pages properly, and can walk several months back, so the
source went from ~20 rows a run to the full ~400 ads per thread.

Each comment is a freeform ad; company/title are best-effort parsed from line 1
(the "Company | Role | Location | ..." convention most posters follow).
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html

ALGOLIA = "https://hn.algolia.com/api/v1"
HITS_PER_PAGE = 100


def _threads(months: int) -> list[str]:
    """Newest `months` "Who is hiring?" story ids (the whoishiring bot posts three
    threads a month; only the hiring one is wanted)."""
    data = get_json(f"{ALGOLIA}/search_by_date",
                    params={"tags": "story,author_whoishiring", "hitsPerPage": months * 4})
    ids = []
    for h in data.get("hits", []):
        if "who is hiring" in (h.get("title") or "").lower():
            ids.append(str(h.get("objectID")))
        if len(ids) >= months:
            break
    return ids


def fetch(cfg: dict) -> list[Job]:
    months = cfg.get("months", 2)
    max_pages = cfg.get("pages", 6)
    try:
        threads = _threads(months)
    except Exception as e:  # noqa: BLE001, no thread list means no rows, not a crash
        print(f"    · hackernews thread lookup failed: {e}")
        return []

    jobs: list[Job] = []
    for tid in threads:
        for page in range(max_pages):
            try:
                data = get_json(f"{ALGOLIA}/search",
                                params={"tags": f"comment,story_{tid}",
                                        "hitsPerPage": HITS_PER_PAGE, "page": page})
            except Exception as e:  # noqa: BLE001, keep earlier pages
                print(f"    · hackernews thread {tid} p{page} failed: {e}")
                break
            hits = data.get("hits", [])
            if not hits:
                break
            for h in hits:
                if h.get("parent_id") and str(h["parent_id"]) != tid:
                    continue  # a reply to an ad, not an ad
                text = strip_html(h.get("comment_text") or "")
                if not text:
                    continue
                first = text.split("|")[0].strip()[:120]
                cid = str(h.get("objectID"))
                jobs.append(Job(
                    source="hackernews",
                    external_id=f"https://news.ycombinator.com/item?id={cid}",
                    url=f"https://news.ycombinator.com/item?id={cid}",
                    company="HN: Who is Hiring",
                    title=first or "HN posting",
                    location="",
                    remote="remote" in text.lower(),
                    description=text,
                    posted_at=h.get("created_at"),
                    raw={},
                ))
            if page + 1 >= (data.get("nbPages") or 1):
                break
    return jobs
