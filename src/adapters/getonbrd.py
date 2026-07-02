"""Get on Board (LatAm / Chile) public REST API, no key.
GET https://www.getonbrd.com/api/v0/search/jobs?query=...&per_page=...
Docs: https://www.getonbrd.com/api-doc.html
"""
from __future__ import annotations

from . import get_json
from ..models import Job, strip_html


def _name(v) -> str:
    """GoB fields can be a str or a nested {data:{attributes:{name}}} object."""
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        return (v.get("name") or v.get("label")
                or _name(v.get("attributes")) or _name(v.get("data")) or "")
    return ""


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    for query in cfg.get("queries", ["remote"]):
        try:
            data = get_json(
                "https://www.getonbrd.com/api/v0/search/jobs",
                params={"query": query, "per_page": cfg.get("per_page", 50), "expand[]": "company"},
            )
        except Exception as e:  # noqa: BLE001, skip a bad query, keep the rest
            print(f"    · getonbrd query '{query}' failed: {e}")
            continue
        for item in data.get("data", []):
            a = item.get("attributes", {})
            jobs.append(Job(
                source="getonbrd",
                external_id=str(item.get("id")),
                url=f"https://www.getonbrd.com/jobs/{a.get('slug', item.get('id'))}",
                company=_name(a.get("company")) or _name(a.get("company_name")),
                title=a.get("title", ""),
                location=_name(a.get("modality")) or ("Remote" if a.get("remote") else ""),
                remote=bool(a.get("remote")),
                description=strip_html(a.get("description", "")),
                salary_min=a.get("min_salary") if isinstance(a.get("min_salary"), int) else None,
                salary_max=a.get("max_salary") if isinstance(a.get("max_salary"), int) else None,
                currency="USD" if isinstance(a.get("min_salary"), int) else None,
                posted_at=str(a.get("published_at")) if a.get("published_at") else None,
                tags=[t for t in [_name(a.get("seniority")), _name(a.get("category"))] if t],
                raw={},
            ))
    return jobs
