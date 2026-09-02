"""Secretlab's in-house careers API (the list secretlab.co/pages/careers renders).
GET https://beans.secretlab.co/index.php/api/2019-08/en/career_openings/openings/
Rows carry job_title, department_name, office_location, position_type,
required_experience and updated_at; there is no per-opening detail endpoint,
so the description is assembled from those fields. Each opening's page is the
careers page anchored at `#id-<id>`. Dream company (profile.yaml), no key.
"""
from __future__ import annotations

from . import get_json, remote_from_text, require_id
from ..models import Job, strip_html

API = "https://beans.secretlab.co/index.php/api/2019-08/en/career_openings/openings/"
PAGE = "https://secretlab.co/pages/careers"


def fetch(cfg: dict) -> list[Job]:
    try:
        data = get_json(API, headers={"User-Agent": "Mozilla/5.0", "Origin": "https://secretlab.co"})
    except Exception as e:  # noqa: BLE001, the source prints and yields nothing
        print(f"    · secretlab failed: {e}")
        return []
    jobs: list[Job] = []
    for o in data.get("data", []):
        try:
            ext = require_id(o, "id")
        except KeyError as e:
            print(f"    · secretlab skipped a row: {e}")
            continue
        title = strip_html(o.get("job_title"))
        loc = o.get("office_location") or ""
        bits = [f"Department: {o['department_name']}" if o.get("department_name") else "",
                f"Position type: {o['position_type']}" if o.get("position_type") else "",
                f"Required experience: {o['required_experience']}" if o.get("required_experience") else "",
                f"Office: {loc}" if loc else ""]
        jobs.append(Job(
            source="secretlab",
            external_id=ext,
            url=f"{PAGE}#id-{ext}",
            company=cfg.get("name") or "Secretlab",
            title=title,
            location=loc,
            remote=remote_from_text(loc, title),
            description="\n".join(b for b in bits if b),
            posted_at=o.get("updated_at"),
            tags=[t for t in (o.get("department_name"),) if t],
            raw={},
        ))
    return jobs
