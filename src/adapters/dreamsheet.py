"""The hand-curated dream-company sheet, read from a local markdown table.

The Google Sheet is private (its CSV export answers 401), so the `/jh-discover`
skill reads it through the Drive tool and saves the returned markdown table to
`cfg.path` (default `data/dream_sheet.md`). This adapter parses that file. No
network, no key; when the file is missing it prints a hint and yields nothing.

Expected columns (header row, any order, case-insensitive): Priority, Company,
Role, Location, Work auth, Why it fits, Apply URL, Status, First seen, Notes.
Only Company + Role + Apply URL are required. Rows whose Status says "skip" or
"applied" are still imported (the pipeline tracks status itself); the sheet's
own judgment lands in the description as a "Curated:" block so the matcher and
the tailor can read it.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..config import ROOT
from ..dream import dream_name
from ..models import Job

DEFAULT_PATH = "data/dream_sheet.md"
_REQUIRED = ("company", "role", "apply url")


def _cells(line: str) -> list[str]:
    body = line.strip().strip("|")
    return [c.strip().replace("\\_", "_").replace("\\~", "~").replace("\\.", ".")
            for c in body.split("|")]


def _is_rule(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-+:?", c) or c == "" for c in cells)


def parse_table(text: str) -> list[dict]:
    """Markdown pipe table -> [{lowercase header: value}], header row auto-detected."""
    rows: list[dict] = []
    header: list[str] | None = None
    for line in text.splitlines():
        if "|" not in line:
            continue
        cells = _cells(line)
        if _is_rule(cells) or not any(cells):
            continue
        low = [c.lower() for c in cells]
        if header is None:
            if all(req in low for req in _REQUIRED):
                header = low
            continue
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, cells, strict=False)))
    return rows


def _curated(row: dict) -> str:
    keep = ("priority", "work auth", "why it fits", "status", "notes", "first seen")
    lines = [f"{k.title()}: {row[k]}" for k in keep if row.get(k)]
    return "Curated (dream sheet):\n" + "\n".join(lines)


def fetch(cfg: dict) -> list[Job]:
    path = Path(cfg.get("path") or DEFAULT_PATH)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        print(f"    · dreamsheet: no {path} yet; refresh it from the sheet "
              f"(see /jh-discover) and re-run")
        return []
    jobs: list[Job] = []
    for row in parse_table(path.read_text()):
        url = row.get("apply url", "")
        title = row.get("role", "")
        company = row.get("company", "")
        if not (url and title and company):
            continue
        loc = row.get("location", "")
        jobs.append(Job(
            source="dreamsheet",
            external_id=url,
            url=url,
            company=dream_name(company) or company,
            title=title,
            location=loc,
            remote="remote" in loc.lower(),
            description=_curated(row),
            posted_at=row.get("first seen") or None,
            tags=[t for t in (row.get("priority"),) if t],
            raw={},
        ))
    return jobs
