"""Hacker News "Who is hiring", monthly thread via hnrss JSON feed.
GET https://hnrss.org/whoishiring/jobs.jsonfeed
Each comment is a freeform ad; company/title are best-effort parsed from line 1.
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    data = get_json("https://hnrss.org/whoishiring/jobs.jsonfeed")
    jobs: list[Job] = []
    for it in data.get("items", []):
        text = strip_html(it.get("content_html", ""))
        first = text.split("|")[0].strip()[:120] if text else "HN posting"
        jobs.append(Job(
            source="hackernews",
            external_id=str(it.get("id", it.get("url"))),
            url=it.get("url", ""),
            company="HN: Who is Hiring",
            title=first,
            location="",
            remote="remote" in text.lower(),
            description=text,
            posted_at=it.get("date_published"),
            raw={},
        ))
    return jobs
