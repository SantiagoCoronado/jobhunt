"""Pinpoint ATS public postings feed, no key, per company.
GET https://{subdomain}.pinpointhq.com/postings.json
Rows carry title, location, workplace_type (onsite/hybrid/remote), a posted
compensation band (min/max/currency/frequency), and full HTML sections.
cfg.companies: list of subdomains; optional cfg.names: {subdomain: "Display Name"}.
"""
from __future__ import annotations

from . import get_json, int_or_none, require_id
from ..models import Job, strip_html

_SECTIONS = ("description", "key_responsibilities", "skills_knowledge_expertise", "benefits")


def _location(p: dict) -> str:
    loc = p.get("location")
    name = loc.get("name", "") if isinstance(loc, dict) else (loc or "")
    kind = (p.get("workplace_type") or "").lower()
    if kind and kind != "onsite":
        name = f"{name} ({kind})".strip()
    return name


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    names = cfg.get("names") or {}
    for sub in cfg.get("companies", []):
        url = f"https://{sub}.pinpointhq.com/postings.json"
        try:
            data = get_json(url, headers={"User-Agent": "Mozilla/5.0"})
        except Exception as e:  # noqa: BLE001, skip a bad subdomain, keep the rest
            print(f"    · pinpoint '{sub}' failed: {e}")
            continue
        company = names.get(sub) or sub.replace("-", " ").title()
        for p in data.get("data", []):
            try:
                ext = require_id(p, "id", "url")
            except KeyError as e:
                print(f"    · pinpoint '{sub}' skipped a row: {e}")
                continue
            body = " ".join(strip_html(p.get(k)) for k in _SECTIONS if p.get(k))
            # Only an annual band is comparable to the profile's annual floor; hourly or
            # monthly figures are left out rather than mis-stated as annual.
            annual = (p.get("compensation_frequency") or "").lower() in ("year", "annual", "annually")
            jobs.append(Job(
                source="pinpoint",
                external_id=f"{sub}:{ext}",
                url=p.get("url") or f"https://{sub}.pinpointhq.com{p.get('path', '')}",
                company=company,
                title=p.get("title", ""),
                location=_location(p),
                remote=(p.get("workplace_type") or "").lower() == "remote",
                description=body,
                salary_min=int_or_none(p.get("compensation_minimum")) if annual else None,
                salary_max=int_or_none(p.get("compensation_maximum")) if annual else None,
                currency=(p.get("compensation_currency") or None) if annual else None,
                posted_at=None,  # the feed carries no created/updated date
                tags=[t for t in (p.get("employment_type_text"),) if t],
                raw={},
            ))
    return jobs
