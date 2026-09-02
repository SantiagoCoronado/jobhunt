"""Findwork.dev remote/tech jobs API. Free bearer token (account signup).
GET https://findwork.dev/api/jobs/   header: Authorization: Token <FINDWORK_TOKEN>
Docs: https://findwork.dev/developers/  (token in .env, see .env.example)
"""
from __future__ import annotations

import time

import requests

from . import get_json
from ..config import get_secret
from ..models import Job, strip_html

# findwork.dev doesn't publish a documented rate limit, but a full sweep (one
# request per search term x page) trips 429s if fired back to back. QUERY_DELAY
# spaces requests out; MAX_429_RETRIES + _backoff_wait retry a rate-limited page
# a few times (honoring Retry-After when the API sends one) before giving up on
# just that page, so one 429 doesn't cost the rest of the source.
QUERY_DELAY = 1.0
MAX_429_RETRIES = 3


def _backoff_wait(attempt: int, resp: requests.Response | None) -> float:
    if resp is not None and resp.headers.get("Retry-After"):
        try:
            return min(float(resp.headers["Retry-After"]), 30.0)
        except ValueError:
            pass
    return min(2.0 * (2**attempt), 30.0)  # 2s, 4s, 8s ...


def _get_with_retry(url: str, params: dict, headers: dict):
    """get_json with its own 429 loop (retries=0 so we control backoff/attempts)."""
    for attempt in range(MAX_429_RETRIES):
        try:
            return get_json(url, params=params, headers=headers, retries=0)
        except requests.RequestException as e:
            resp = getattr(e, "response", None)
            if resp is None or resp.status_code != 429 or attempt == MAX_429_RETRIES - 1:
                raise
            wait = _backoff_wait(attempt, resp)
            print(f"    · findwork rate-limited, retrying in {wait:.0f}s "
                  f"(attempt {attempt + 1}/{MAX_429_RETRIES})")
            time.sleep(wait)
    raise AssertionError("unreachable: loop always returns or raises")


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
    for i, term in enumerate(searches):
        if i:
            time.sleep(QUERY_DELAY)  # polite gap between search queries
        for page in range(1, pages + 1):
            params: dict = {"page": page}
            if term:
                params["search"] = term
            if remote_only:
                params["remote"] = "true"
            try:
                data = _get_with_retry("https://findwork.dev/api/jobs/", params, headers)
            except Exception as e:  # noqa: BLE001, skip a bad page, keep the rest
                if "401" in str(e):  # bad/expired token: stop, don't spam every term/page
                    print("  ! findwork: FINDWORK_TOKEN rejected (Invalid token). Re-copy your "
                          "API key from findwork.dev/developers (it is normally ~40 chars).")
                    return jobs
                if "404" in str(e):  # ran past the last page for this term: end of results
                    break
                if "429" in str(e):  # still rate-limited after MAX_429_RETRIES: skip this query
                    print(f"    · findwork '{term}' p{page} still rate-limited after "
                          f"{MAX_429_RETRIES} attempts, skipping rest of this query")
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
