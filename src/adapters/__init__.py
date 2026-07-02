"""Source adapters. Each module exposes `fetch(cfg: dict) -> list[Job]`.

Only free, official, ToS-safe endpoints live here (public ATS boards + sanctioned
aggregator APIs/RSS). The optional `jobspy_gap` adapter is the one grey-zone
exception and ships disabled.
"""
from __future__ import annotations

import time
import requests

UA = "jobhunt/0.1 (personal job search; +https://github.com/)"
_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": UA, "Accept": "application/json"})


def get_json(url: str, *, params: dict | None = None, timeout: int = 20, retries: int = 2):
    """GET JSON with light retry. Returns parsed body or raises on final failure."""
    last = None
    for attempt in range(retries + 1):
        try:
            r = _SESSION.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001, surface to per-source handler
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise last


def get_text(url: str, *, timeout: int = 20):
    r = _SESSION.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text
