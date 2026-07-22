"""Normalized Job model shared by every source adapter.

Kept dependency-free (stdlib dataclasses) so `discover` runs on a bare Python.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, UTC
from typing import Any


_WS = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_HTML_TAG = re.compile(r"<[^>]+>")


def normalize_text(s: str | None) -> str:
    """Lowercase, strip punctuation/whitespace, used for fuzzy dedupe keys."""
    if not s:
        return ""
    s = _NON_ALNUM.sub(" ", s.lower())
    return _WS.sub(" ", s).strip()


def strip_html(s: str | None) -> str:
    if not s:
        return ""
    import html
    return _WS.sub(" ", html.unescape(_HTML_TAG.sub(" ", s))).strip()


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def iso_date(s) -> str | None:
    """Best-effort normalization of a source's posted-at into ISO-8601 UTC.

    Sources emit epoch seconds, ISO with/without Z, and RFC-2822 (RSS). One
    TEXT column with mixed formats makes date sorting unreliable, so coerce
    here. Unparseable values pass through unchanged: never destroy data.
    """
    if not s:
        return None
    s = str(s).strip()
    if s.isdigit() and len(s) in (10, 13):  # epoch seconds / milliseconds
        return datetime.fromtimestamp(int(s[:10]), tz=UTC).isoformat()
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(s)
        except (ValueError, TypeError):
            return s
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat()


@dataclass
class Job:
    # identity
    source: str                      # "greenhouse", "lever", "remoteok", ...
    external_id: str                 # id unique *within* that source
    url: str                         # apply / posting URL
    company: str
    title: str
    # detail
    location: str = ""
    remote: bool = False
    description: str = ""             # plain text (HTML stripped)
    salary_min: int | None = None
    salary_max: int | None = None
    currency: str | None = None
    posted_at: str | None = None     # ISO8601 if known
    tags: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def canonical_key(self) -> str:
        """Cross-source dedupe key: same role on Greenhouse + RemoteOK collapses."""
        basis = f"{normalize_text(self.company)}|{normalize_text(self.title)}"
        return hashlib.sha1(basis.encode()).hexdigest()[:16]

    def to_row(self) -> dict[str, Any]:
        d = asdict(self)
        d["tags"] = ",".join(str(t) for t in self.tags)
        d.pop("raw", None)
        d["remote"] = int(self.remote)
        d["posted_at"] = iso_date(self.posted_at)
        d["canonical_key"] = self.canonical_key
        return d
