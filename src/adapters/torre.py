"""Torre opportunities search (public JSON, no key). Strong remote-LATAM coverage.
POST https://search.torre.co/opportunities/_search/
Grey-zone: undocumented public endpoint. cfg.queries: role search terms.
"""
from __future__ import annotations

from . import post_json
from ..models import Job, strip_html


def fetch(cfg: dict) -> list[Job]:
    queries = cfg.get("queries") or ["software engineer"]
    size = min(cfg.get("size", 20), 30)  # the endpoint 400s above ~30 per page
    pages = cfg.get("pages", 2)
    remote_only = cfg.get("remote", True)

    jobs: list[Job] = []
    seen: set[str] = set()
    for term in queries:
        body: dict = {"skill/role": {"text": term, "experience": "potential-to-develop"}}
        if remote_only:
            body["remote"] = {"term": True}
        for page in range(pages):
            offset = page * size
            url = (f"https://search.torre.co/opportunities/_search/"
                   f"?size={size}&aggregate=false&offset={offset}")
            try:
                data = post_json(url, json=body, headers={"Content-Type": "application/json"})
            except Exception as e:  # noqa: BLE001, skip a bad page, keep the rest
                print(f"    · torre '{term}' p{page} failed: {e}")
                break
            results = data.get("results", [])
            if not results:
                break
            for j in results:
                oid = str(j.get("id") or "")
                if not oid or oid in seen:
                    continue
                seen.add(oid)
                orgs = j.get("organizations") or []
                company = orgs[0].get("name", "") if orgs else ""
                locs = [x for x in (j.get("locations") or []) if isinstance(x, str)]
                comp = (j.get("compensation") or {}).get("data") or {}
                jobs.append(Job(
                    source="torre",
                    external_id=oid,
                    url=f"https://torre.co/jobs/{oid}",
                    company=company,
                    title=j.get("objective", ""),
                    location=", ".join(locs) or ("Remote" if j.get("remote") else ""),
                    remote=bool(j.get("remote")),
                    description=strip_html(j.get("tagline", "")),
                    salary_min=int(comp["minAmount"]) if comp.get("minAmount") else None,
                    salary_max=int(comp["maxAmount"]) if comp.get("maxAmount") else None,
                    currency=comp.get("currency"),
                    posted_at=j.get("created"),
                    tags=[s.get("name") for s in (j.get("skills") or [])[:5] if s.get("name")],
                    raw={},
                ))
    return jobs
