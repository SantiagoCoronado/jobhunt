"""We Work Remotely, sanctioned path is RSS (no JSON API). Needs `feedparser`.
Category feeds: https://weworkremotely.com/categories/{cat}.rss
e.g. remote-back-end-programming-jobs, remote-full-stack-programming-jobs
"""
from __future__ import annotations

import hashlib

from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    try:
        import feedparser
    except ImportError:
        print("  ! weworkremotely: `pip install feedparser` to enable RSS")
        return []

    jobs: list[Job] = []
    cats = cfg.get("categories") or ["remote-programming-jobs"]
    for cat in cats:
        feed = feedparser.parse(f"https://weworkremotely.com/categories/{cat}.rss")
        for e in feed.entries:
            title = e.get("title", "")
            company, _, role = title.partition(":")  # WWR uses "Company: Role"
            role = role.strip() or title
            jobs.append(Job(
                source="weworkremotely",
                external_id=hashlib.sha1(e.get("link", title).encode()).hexdigest()[:16],
                url=e.get("link", ""),
                company=company.strip(),
                title=role,
                location=e.get("region", "Remote"),
                remote=True,
                description=strip_html(e.get("summary", "")),
                posted_at=e.get("published"),
                raw={},
            ))
    return jobs
