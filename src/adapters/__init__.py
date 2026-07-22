"""Source adapters. Each module exposes `fetch(cfg: dict) -> list[Job]`.

Only free, official, ToS-safe endpoints live here (public ATS boards + sanctioned
aggregator APIs/RSS). The optional `jobspy_gap` adapter is the one grey-zone
exception and ships disabled.

Shared HTTP layer: one session, a per-host politeness delay, and retries that
only fire when a retry can help (429/5xx/timeouts). A 404 or 401 fails fast.
"""
from __future__ import annotations

import threading
import time
from urllib.parse import urlsplit

import requests

UA = "jobhunt/0.1 (personal job search; +https://github.com/)"
_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": UA, "Accept": "application/json"})

# Minimum spacing between requests to the SAME host, shared across threads
# (softserve fans a ThreadPoolExecutor over one host's vacancy pages).
HOST_MIN_INTERVAL = 0.4
_last_hit: dict[str, float] = {}
_throttle_lock = threading.Lock()

RETRY_STATUSES = {429, 500, 502, 503, 504}


def _throttle(url: str) -> None:
    host = urlsplit(url).netloc
    with _throttle_lock:
        # Reserve the next free slot for this host BEFORE sleeping, so
        # concurrent threads queue up instead of firing together.
        now = time.monotonic()
        slot = max(now, _last_hit.get(host, now - HOST_MIN_INTERVAL) + HOST_MIN_INTERVAL)
        _last_hit[host] = slot
    if slot > now:
        time.sleep(slot - now)


def _retryable(exc: requests.RequestException) -> bool:
    if isinstance(exc, (requests.ConnectionError, requests.Timeout)):
        return True
    resp = getattr(exc, "response", None)
    return resp is not None and resp.status_code in RETRY_STATUSES


def _request(method: str, url: str, *, retries: int = 2, **kwargs) -> requests.Response:
    """Session request with per-host throttle; retries ONLY 429/5xx/timeouts.
    Other 4xx (404, 401, 403) raise immediately: retrying can't fix them."""
    for attempt in range(retries + 1):
        _throttle(url)
        try:
            r = _SESSION.request(method, url, **kwargs)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            if not _retryable(e) or attempt == retries:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise AssertionError("unreachable: loop always returns or raises")


def get_json(url: str, *, params: dict | None = None, headers: dict | None = None,
             auth=None, timeout: int = 20, retries: int = 2):
    """GET JSON. `headers`/`auth` are per-request extras for keyed sources
    (Bearer/Basic); the shared session only sets a User-Agent."""
    return _request("GET", url, params=params, headers=headers, auth=auth,
                    timeout=timeout, retries=retries).json()


def post_json(url: str, *, json: dict | None = None, params: dict | None = None,
              headers: dict | None = None, auth=None, timeout: int = 20, retries: int = 2):
    """POST JSON with the same retry policy (Workday CxS, Torre search)."""
    return _request("POST", url, json=json, params=params, headers=headers,
                    auth=auth, timeout=timeout, retries=retries).json()


def get_text(url: str, *, params: dict | None = None, headers: dict | None = None,
             auth=None, timeout: int = 20, retries: int = 2) -> str:
    """GET text/HTML/XML with the same retry policy as get_json (it used to have
    none, and it is the sole fetch path for sitemap/RSS sources like softserve)."""
    return _request("GET", url, params=params, headers=headers, auth=auth,
                    timeout=timeout, retries=retries).text


# ---- shared normalization helpers (use these in every adapter) ----

def int_or_none(x) -> int | None:
    """Salary coercion without the copy-pasted `int(x) if x else None` pitfall.
    0 deliberately collapses to None: sources emit 0 for 'unspecified'."""
    try:
        return int(float(x)) if x not in (None, "", 0) else None
    except (TypeError, ValueError):
        return None


def remote_from_text(*parts: str | None) -> bool:
    """The 'remote' heuristic every adapter reimplemented: any part mentions it."""
    return "remote" in " ".join(p for p in parts if p).lower()


def require_id(obj: dict, *keys: str) -> str:
    """First non-empty id-ish field, as str. Raises KeyError instead of returning
    the literal 'None', which would poison UNIQUE(source, external_id)."""
    for k in keys:
        v = obj.get(k)
        if v not in (None, ""):
            return str(v)
    raise KeyError(f"no usable id in any of {keys}")


def paginate(fetch_page, max_pages: int, *, label: str = "") -> list:
    """Run fetch_page(page_number) for 1..max_pages, collecting list results.
    Stops on the first empty page; a failing page skips the rest of THAT loop
    but keeps what was already fetched (the standard adapter pattern)."""
    out: list = []
    for page in range(1, max_pages + 1):
        try:
            batch = fetch_page(page)
        except Exception as e:  # noqa: BLE001, per-page skip is the adapter contract
            print(f"    · {label or 'page'} p{page} failed: {e}")
            break
        if not batch:
            break
        out.extend(batch)
    return out
