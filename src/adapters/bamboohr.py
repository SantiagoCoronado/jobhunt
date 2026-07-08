"""BambooHR public careers list (JSON, no key). Native reimpl of the jobber pattern.
GET https://{company}.bamboohr.com/careers/list  -> {"result": [...]}
cfg.companies: BambooHR subdomains. The list endpoint has no description text.
"""
from __future__ import annotations

from . import get_json
from ..models import Job


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    for company in cfg.get("companies", []):
        url = f"https://{company}.bamboohr.com/careers/list"
        try:
            data = get_json(url)
        except Exception as e:  # noqa: BLE001, skip a bad company, keep the rest
            print(f"    · bamboohr '{company}' failed: {e}")
            continue
        display = company.replace("-", " ").title()
        for j in (data.get("result") or []):
            loc = j.get("location") or {}
            loc_str = ", ".join(
                x for x in [loc.get("city"), loc.get("state"), loc.get("addressCountry")] if x
            )
            jid = str(j.get("id"))
            remote = str(j.get("isRemote") or "").lower() in ("yes", "true", "1") \
                or "remote" in loc_str.lower()
            jobs.append(Job(
                source="bamboohr",
                external_id=f"{company}:{jid}",
                url=f"https://{company}.bamboohr.com/careers/{jid}",
                company=display,
                title=j.get("jobOpeningName", ""),
                location=loc_str or (j.get("locationType") or ""),
                remote=remote,
                description="",  # not in the list endpoint; detail needs a second call
                tags=[t for t in [j.get("departmentLabel")] if t],
                raw={},
            ))
    return jobs
