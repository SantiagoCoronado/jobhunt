"""Personio public job feed (XML, no key). Big in EU startups.
GET https://{company}.jobs.personio.de/xml?language=en
Root <workzag-jobs> -> <position> nodes. cfg.companies: Personio subdomains.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from . import get_text
from ..models import Job, strip_html


def _t(node, tag: str) -> str:
    el = node.find(tag)
    return (el.text or "").strip() if el is not None and el.text else ""


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    for company in cfg.get("companies", []):
        raw = None
        last: Exception | None = None
        for host in (f"https://{company}.jobs.personio.de/xml",
                     f"https://{company}.jobs.personio.com/xml"):
            try:
                raw = get_text(host, params={"language": "en"})
                break
            except Exception as e:  # noqa: BLE001
                last = e
        if raw is None:
            print(f"    · personio '{company}' failed: {last}")
            continue
        try:
            root = ET.fromstring(raw)
        except Exception as e:  # noqa: BLE001
            print(f"    · personio '{company}' bad XML: {e}")
            continue
        display = company.replace("-", " ").title()
        for pos in root.findall(".//position"):
            pid = _t(pos, "id")
            if not pid:
                continue
            office = _t(pos, "office")
            title = _t(pos, "name")
            parts: list[str] = []
            for jd in pos.findall(".//jobDescription"):
                parts.append(_t(jd, "name"))
                parts.append(_t(jd, "value"))
            jobs.append(Job(
                source="personio",
                external_id=f"{company}:{pid}",
                url=f"https://{company}.jobs.personio.de/job/{pid}",
                company=display,
                title=title,
                location=office,
                remote="remote" in (office + " " + title).lower(),
                description=strip_html(" ".join(p for p in parts if p)),
                posted_at=_t(pos, "createdAt") or None,
                tags=[t for t in [_t(pos, "recruitingCategory"), _t(pos, "department")] if t],
                raw={},
            ))
    return jobs
