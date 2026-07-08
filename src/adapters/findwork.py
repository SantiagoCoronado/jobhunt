"""Findwork.dev remote/tech jobs API. Free bearer token (account signup).
GET https://findwork.dev/api/jobs/   header: Authorization: Token <FINDWORK_TOKEN>
Docs: https://findwork.dev/developers/  (token in .env, see .env.example)
"""
from __future__ import annotations

from . import get_json
from ..config import get_secret
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    token = get_secret("FINDWORK_TOKEN")
    if not token:
        print("  ! findwork: set FINDWORK_TOKEN in .env (see .env.example)")
        return []

    headers = {"Authorization": f"Token {token}"}
    searches = cfg.get("search") or [None]
    remote_only = cfg.get("remote", True)
    pages = cfg.get("pages", 1)

    jobs: list[Job] = []
    for term in searches:
        for page in range(1, pages + 1):
            params: dict = {"page": page}
            if term:
                params["search"] = term
            if remote_only:
                params["remote"] = "true"
            try:
                data = get_json("https://findwork.dev/api/jobs/", params=params, headers=headers)
            except Exception as e:  # noqa: BLE001, skip a bad page, keep the rest
                if "401" in str(e):  # bad/expired token: stop, don't spam every term/page
                    print("  ! findwork: FINDWORK_TOKEN rejected (Invalid token). Re-copy your "
                          "API key from findwork.dev/developers (it is normally ~40 chars).")
                    return jobs
                if "404" in str(e):  # ran past the last page for this term: end of results
                    break
                print(f"    · findwork '{term}' p{page} failed: {e}")
                break
            results = data.get("results", [])
            if not results:
                break
            for j in results:
                jobs.append(Job(
                    source="findwork",
                    external_id=str(j.get("id")),
                    url=j.get("url", ""),
                    company=j.get("company_name", ""),
                    title=j.get("role", ""),
                    location=j.get("location") or ("Remote" if j.get("remote") else ""),
                    remote=bool(j.get("remote")),
                    description=strip_html(j.get("text", "")),
                    posted_at=j.get("date_posted"),
                    tags=(j.get("keywords") or [])[:6],
                    raw={},
                ))
    return jobs
