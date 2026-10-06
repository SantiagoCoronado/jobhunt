"""JobTech JobSearch (Arbetsförmedlingen, the Swedish Public Employment Service), no key.
GET https://jobsearch.api.jobtechdev.se/search?q=...&limit=...&offset=...
Official open-data API; the ads are licensed CC0 (the API's own OpenAPI `info.license`).
Verified 2026-10-06, docs/sources-europe.md.

cfg keys:
  queries: list[str]  -> free-text searches (targeting, from config/sources.local.yaml)
  limit:   int        -> hits per request (the API allows up to 100)
  pages:   int        -> requests per query
"""
from __future__ import annotations

from . import get_json
from ..models import Job

URL = "https://jobsearch.api.jobtechdev.se/search"
_HOME_COUNTRY = {"", "sverige", "sweden"}


def _label(v) -> str:
    return str((v or {}).get("label") or "") if isinstance(v, dict) else ""


def _location(addr: dict) -> str:
    place = addr.get("city") or addr.get("municipality") or addr.get("region") or ""
    country = str(addr.get("country") or "")
    country = "Sweden" if country.strip().lower() in _HOME_COUNTRY else country
    return ", ".join(p for p in (place, country) if p)


def to_job(hit: dict) -> Job:
    desc = hit.get("description") or {}
    model = _label(hit.get("workplace_model")).lower()
    headline = str(hit.get("headline") or "").strip()
    return Job(
        source="jobtech",
        external_id=str(hit.get("id")),
        url=str(hit.get("webpage_url") or ""),
        company=str((hit.get("employer") or {}).get("name") or ""),
        title=headline,
        location=_location(hit.get("workplace_address") or {}),
        remote="distans" in model or "remote" in model or "remote" in headline.lower(),
        description=str(desc.get("text") or "").strip(),
        posted_at=hit.get("publication_date"),
        tags=[t for t in (_label(hit.get("occupation")), _label(hit.get("employment_type"))) if t],
        raw={},
    )


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    seen: set[str] = set()
    limit = int(cfg.get("limit", 100))
    for q in cfg.get("queries") or []:
        for page in range(int(cfg.get("pages", 2))):
            try:
                data = get_json(URL, params={"q": q, "limit": limit, "offset": page * limit})
            except Exception as e:  # noqa: BLE001
                print(f"    . jobtech '{q}' page {page + 1} failed: {e}")
                break
            hits = data.get("hits") or []
            for hit in hits:
                if hit.get("removed") or str(hit.get("id")) in seen:
                    continue
                seen.add(str(hit.get("id")))
                jobs.append(to_job(hit))
            if len(hits) < limit:
                break
    return jobs
