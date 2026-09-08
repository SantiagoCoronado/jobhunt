"""Torre opportunities search (public JSON, no key). Strong remote-LATAM coverage.
POST https://search.torre.co/opportunities/_search/
Grey-zone: undocumented public endpoint. cfg.queries: role search terms.

Eligibility capture: the SAME search response already carries a `timezones` band
(e.g. ["GMT+00:00","GMT+03:00"]), a `locations` country list (often empty when the
role is timezone-gated rather than country-gated), and an `opportunity` agreement
type (employee/contractor/flexible...). No per-job fetch needed. See
`eligibility_header` / bug: job 18645 (Constructor, Spain/UK-only via timezone) was
scored 84 and tailored before anyone saw `timezones` was Europe-only.
"""
from __future__ import annotations

import re

from . import post_json
from ..config import load_profile
from ..models import Job, strip_html

_GMT_RE = re.compile(r"^GMT([+-])(\d{2}):(\d{2})$")


def _gmt_offset_hours(tz: str) -> float | None:
    """'GMT+03:00' -> 3.0, 'GMT-06:00' -> -6.0. None if unparseable."""
    m = _GMT_RE.match((tz or "").strip())
    if not m:
        return None
    sign, hh, mm = m.groups()
    val = int(hh) + int(mm) / 60
    return -val if sign == "-" else val


_GMT_LOOSE = re.compile(r"GMT\s*([+-])\s*(\d{1,2})(?::?(\d{2}))?", re.I)


def home_offset_hours() -> float | None:
    """The home GMT offset written in the profile's `timezones` ("hybrid must be Lisbon
    (GMT+00:00)", "(GMT-6)"); None when no offset is written, and then no band excludes."""
    try:
        prof = load_profile()
    except FileNotFoundError:
        return None
    m = _GMT_LOOSE.search(" ".join(str(t) for t in (prof.get("timezones") or [])))
    if not m:
        return None
    sign, hh, mm = m.groups()
    val = int(hh) + int(mm or 0) / 60
    return -val if sign == "-" else val


def timezone_band_excludes(timezones: list[str] | None, offset_hours: float | None = None) -> bool:
    """True when a defined timezone band does NOT cover `offset_hours` (default: the home
    offset from the profile's `timezones`; none written = never excluded). A job with no
    timezone restriction (empty/None) is never 'excluded': absence of a band means it isn't
    timezone-gated."""
    if offset_hours is None:
        offset_hours = home_offset_hours()
    if offset_hours is None:
        return False
    parsed = [o for o in (_gmt_offset_hours(t) for t in (timezones or [])) if o is not None]
    if not parsed:
        return False
    return not (min(parsed) <= offset_hours <= max(parsed))


def _timezone_phrase(timezones: list[str]) -> str:
    valid = [t for t in timezones if isinstance(t, str) and t.strip()]
    if not valid:
        return ""
    if len(valid) == 1:
        return f"timezone {valid[0]}"
    def _sort_key(t: str) -> float:
        offset = _gmt_offset_hours(t)
        return offset if offset is not None else 0.0
    ordered = sorted(valid, key=_sort_key)
    if len(valid) == 2:
        return f"timezone {ordered[0]} to {ordered[-1]}"
    return "timezones: " + ", ".join(ordered)


def eligibility_header(*, remote: bool, timezones: list[str] | None,
                        locations: list[str] | None, opportunity: str | None) -> str:
    """One-line 'Eligibility: ...' header, PREPENDED to the description so triage
    and the matcher both see it (triage snippets the first 300 chars)."""
    bits = ["remote" if remote else "on-site"]
    tz_bit = _timezone_phrase(timezones or [])
    if tz_bit:
        bits.append(tz_bit)
    locs = [x for x in (locations or []) if isinstance(x, str) and x.strip()]
    if locs:
        bits.append("countries: " + ", ".join(locs))
    if opportunity:
        bits.append(f"agreement: {opportunity}")
    return "Eligibility: " + ", ".join(bits) + "."


_HEADER_RE = re.compile(r"^Eligibility:.*?\.\s*")


def strip_eligibility_header(description: str) -> str:
    """Undo a previously-prepended header, so a backfill re-run doesn't stack them."""
    return _HEADER_RE.sub("", description or "", count=1)


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
                timezones = [x for x in (j.get("timezones") or []) if isinstance(x, str)]
                opportunity = j.get("opportunity") or ""
                header = eligibility_header(remote=bool(j.get("remote")), timezones=timezones,
                                             locations=locs, opportunity=opportunity)
                comp = (j.get("compensation") or {}).get("data") or {}
                jobs.append(Job(
                    source="torre",
                    external_id=oid,
                    url=f"https://torre.co/jobs/{oid}",
                    company=company,
                    title=j.get("objective", ""),
                    location=", ".join(locs) or ("Remote" if j.get("remote") else ""),
                    remote=bool(j.get("remote")),
                    description=(header + " " + strip_html(j.get("tagline", ""))).strip(),
                    salary_min=int(comp["minAmount"]) if comp.get("minAmount") else None,
                    salary_max=int(comp["maxAmount"]) if comp.get("maxAmount") else None,
                    currency=comp.get("currency"),
                    posted_at=j.get("created"),
                    tags=[s.get("name") for s in (j.get("skills") or [])[:5] if s.get("name")],
                    raw={},
                ))
    return jobs


def backfill_eligibility(pages: int = 6) -> None:
    """One-off: refresh the eligibility header on existing Torre rows.

    No per-job endpoint exists (confirmed: search.torre.co ignores an `id` filter
    and returns unrelated results), so this re-runs the SAME search queries the
    adapter uses, walking a few more pages than a normal fetch, and updates any
    row whose external_id shows up in the fresh results. Rows that no longer
    surface in search (fell off the ranking) are left untouched and reported as
    not-refreshed; their status/data otherwise stays exactly as-is (this never
    changes `status`).
    """
    from ..config import sources
    from ..db import connect

    cfg = sources().get("torre") or {}
    queries = cfg.get("queries") or ["software engineer"]
    size = min(cfg.get("size", 20), 30)
    remote_only = cfg.get("remote", True)

    conn = connect()
    rows = conn.execute(
        "SELECT id, company, title, external_id, description FROM jobs "
        "WHERE source='torre' AND status IN ('discovered','shortlisted','backlog')"
    ).fetchall()
    wanted = {r["external_id"]: dict(r) for r in rows if r["external_id"]}
    print(f"Torre rows eligible for backfill: {len(wanted)}")

    found: dict[str, dict] = {}
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
                print(f"    · torre backfill '{term}' p{page} failed: {e}")
                break
            results = data.get("results", [])
            if not results:
                break
            for j in results:
                oid = str(j.get("id") or "")
                if oid in wanted and oid not in found:
                    found[oid] = j

    refreshed = 0
    home_offset = home_offset_hours()
    excluded: list[tuple] = []
    for oid, j in found.items():
        row = wanted[oid]
        locs = [x for x in (j.get("locations") or []) if isinstance(x, str)]
        timezones = [x for x in (j.get("timezones") or []) if isinstance(x, str)]
        opportunity = j.get("opportunity") or ""
        remote = bool(j.get("remote"))
        header = eligibility_header(remote=remote, timezones=timezones,
                                     locations=locs, opportunity=opportunity)
        base_desc = strip_eligibility_header(row["description"] or "")
        new_desc = (header + " " + base_desc).strip()
        new_loc = ", ".join(locs) or ("Remote" if remote else "")
        conn.execute("UPDATE jobs SET description=?, location=? WHERE id=?",
                     (new_desc, new_loc, row["id"]))
        refreshed += 1
        if timezone_band_excludes(timezones, home_offset):
            excluded.append((row["id"], row["company"], row["title"], timezones))
    conn.commit()

    print(f"Refreshed {refreshed}/{len(wanted)} Torre rows with a live eligibility header "
          f"({len(wanted) - refreshed} not found in a fresh search, left untouched).")
    if home_offset is None:
        print("No GMT offset in profile.yaml timezones: timezone bands not checked.")
    else:
        print(f"{len(excluded)} refreshed row(s) have a timezone band that excludes the home offset "
              f"GMT{home_offset:+g} (profile timezones):")
    for jid, company, title, tzs in excluded:
        print(f"  id={jid} {company!r} - {title!r} timezones={tzs}")


if __name__ == "__main__":
    backfill_eligibility()
