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


def get_json(url: str, *, params: dict | None = None, headers: dict | None = None,
             auth=None, timeout: int = 20, retries: int = 2):
    """GET JSON with light retry. Returns parsed body or raises on final failure.

    `headers`/`auth` are per-request extras for keyed sources (Bearer/Basic);
    the shared session only sets a User-Agent, so callers pass credentials here.
    """
    last = None
    for attempt in range(retries + 1):
        try:
            r = _SESSION.get(url, params=params, headers=headers, auth=auth, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001, surface to per-source handler
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise last


def post_json(url: str, *, json: dict | None = None, params: dict | None = None,
              headers: dict | None = None, auth=None, timeout: int = 20, retries: int = 2):
    """POST JSON with light retry (Workday CxS, Torre search). Returns parsed body."""
    last = None
    for attempt in range(retries + 1):
        try:
            r = _SESSION.post(url, json=json, params=params, headers=headers,
                              auth=auth, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001, surface to per-source handler
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise last


def get_text(url: str, *, params: dict | None = None, headers: dict | None = None,
             auth=None, timeout: int = 20):
    r = _SESSION.get(url, params=params, headers=headers, auth=auth, timeout=timeout)
    r.raise_for_status()
    return r.text
