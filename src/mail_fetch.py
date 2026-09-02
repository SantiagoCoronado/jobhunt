"""Portable multi-account inbox pull for /jh-gmail-sync (docs/spec-mail-fetch.md, Phase A).

Reads every IMAP mailbox listed in .env (MAIL_ACCOUNTS=...), read-only by protocol
(EXAMINE + BODY.PEEK, never STORE/COPY/EXPUNGE/APPEND), finds mail about the open
applications with one server-side search per job, confirms every candidate locally
with word-boundary matching, cuts noise no model needs to see, collapses threads,
ranks and caps them, and writes two files under data/:

    mail_inbox.json      accounts, tune lines, legend, one row per thread (headers +
                         lead only, no bodies)
    mail_snippets.jsonl  one cleaned snippet per thread; only `show` reads it

The default run prints the account summary, `tune:` lines, the legend and page 1 of
the manifest. The model classifies from that and asks `show <id>` for the few lines
it cannot settle. Python narrows; it never decides a status (hints carry a `?`).

    python -m src.mail_fetch [--account L ...] [--since YYYY-MM-DD] [--max-days 120]
                             [--status ...] [--limit-per-job 3] [--snippet-chars 800]
                             [--scan-all] [--full] [--keep-noise] [--page-size 80]
    python -m src.mail_fetch manifest [--page N] [--page-size 80]
    python -m src.mail_fetch show <id> [<id> ...]        (25 ids max)
"""
from __future__ import annotations

import argparse
import email
import email.header
import email.utils
import html
import imaplib
import json
import re
import sqlite3
import sys
import unicodedata
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from email.message import Message as EmailMessage
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urlsplit

from .config import CONFIG_DIR, ROOT, get_secret, load_yaml
from .db import STATUSES, connect

DATA_DIR = ROOT / "data"
INBOX_PATH = DATA_DIR / "mail_inbox.json"
SNIPPETS_PATH = DATA_DIR / "mail_snippets.jsonl"
STATE_PATH = DATA_DIR / "mail_state.json"
HINTS_PATH = CONFIG_DIR / "mail_hints.yaml"

OPEN_STATUSES = ("applied", "screen", "interview", "offer")
WINDOW_PAD_DAYS = 2
RECEIPT_GRACE_DAYS = 3
FALLBACK_THREAD_GAP_DAYS = 7
DEMOTE_DOMAIN_THRESHOLD = 5      # distinct sender domains before a name key is demoted
ZERO_CANDIDATE_SWEEPS = 3        # DAYS with 0 candidates before the aliases tune line (one count per day)
TUNE_LINES_MAX = 5               # per category per run; the rest is summarized
THREAD_TERMINAL_SIGNALS = frozenset({"rejection"})   # only these let a seen id silence its whole thread
SHOW_MAX_IDS = 25
HEADER_FIELDS = ("FROM TO SUBJECT DATE MESSAGE-ID IN-REPLY-TO REFERENCES "
                 "LIST-UNSUBSCRIBE PRECEDENCE AUTO-SUBMITTED")
FETCH_BATCH = 200

# Hosts that never identify the company (job boards + ATS). A url on one of these
# yields no domain key; the ATS slug (when present) becomes a name key instead.
ATS_HOSTS = (
    "greenhouse.io", "lever.co", "ashbyhq.com", "myworkdayjobs.com", "workday.com",
    "smartrecruiters.com", "teamtailor.com", "pinpointhq.com", "rippling.com",
    "bamboohr.com", "personio.de", "personio.com", "workable.com", "jobvite.com",
    "icims.com", "recruitee.com", "breezy.hr", "getonbrd.com", "remoteok.com",
    "weworkremotely.com", "torre.ai", "torre.co", "themuse.com", "findwork.dev",
    "adzuna.com", "adzuna.com.mx", "careerjet.com", "careerjet.com.mx", "linkedin.com",
    "indeed.com", "glassdoor.com", "ycombinator.com", "consider.com", "posthog.com",
    "wellfound.com", "hackernews.com", "ycombinator.com",
)
# Senders whose From line never names the company; matched on the body instead.
RELAY_DOMAINS = frozenset({
    "greenhouse-mail.io", "greenhouse.io", "lever.co", "hire.lever.co", "ashbyhq.com",
    "smartrecruiters.com", "myworkday.com", "workday.com", "workable.com",
    "workablemail.com", "bamboohr.com", "jobvite.com", "icims.com", "teamtailor.com",
    "pinpointhq.com", "rippling.com", "breezy.hr", "recruitee.com", "personio.de",
    "hackerrank.com", "hackereval.com", "codility.com", "coderbyte.com", "calendly.com",
    "goodtime.io",
})
# Job-alert senders: always cut (unless the message matched by domain/slug/alias/body).
ALERT_DOMAINS = frozenset({
    "indeed.com", "glassdoor.com", "ziprecruiter.com", "jobalerts.com", "e.linkedin.com",
    "jobs-noreply.linkedin.com", "getonbrd.com", "remoteok.com", "weworkremotely.com",
})
# Carry recruiter messages too: cut only when the subject looks like an alert.
SOFT_ALERT_DOMAINS = frozenset({"linkedin.com", "wellfound.com", "hired.com"})
ALERT_SUBJECT_RE = re.compile(
    r"jobs? for you|new jobs?|who'?s viewed|recommended for you|job alert|"
    r"trabajos? (para ti|nuevos?)|empleos? (para ti|nuevos?)", re.I)
FREEMAIL = frozenset({
    "gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com", "yahoo.com",
    "icloud.com", "me.com", "proton.me", "protonmail.com", "gmx.com", "aol.com",
})
NOREPLY_RE = re.compile(
    r"(^|[.\-_])(no-?reply|do-?not-?reply|notifications?|mailer-daemon|bounce|updates?|newsletters?|news|"
    r"marketing|digest|billing|welcome|alerts?)\d*($|[.\-_@+])", re.I)
ECHO_SUBJECT_RE = re.compile(r"^(accepted|declined|tentative|updated invitation|aceptad[oa]|rechazad[oa]):", re.I)
REPLY_PREFIX_RE = re.compile(r"^\s*((re|fwd?|fw|rv|aw|sv)\s*:\s*)+", re.I)
EXTERNAL_PREFIX_RE = re.compile(r"^\s*\[(external|externo|ext)\]\s*", re.I)
SUFFIX_RE = re.compile(
    r"\b(inc|incorporated|llc|ltd|limited|gmbh|s\.?a\.?(?: de c\.?v\.?)?|sa de cv|corp|corporation|co|"
    r"company|plc|s\.?l\.?|s\.?r\.?l\.?|holdings?|group|labs|technologies|technology|tech)\b\.?", re.I)
STRONG_KINDS = frozenset({"domain", "slug", "alias", "body", "relay"})
GENERIC_SLUGS = frozenset({"jobs", "careers", "job", "en", "es", "embed", "apply", "boards", "o", "postings", ""})


# ----------------------------------------------------------------------------- config

@dataclass
class MailAccount:
    label: str
    user: str
    password: str | None
    host: str = "imap.gmail.com"
    port: int = 993
    folders: list[str] = field(default_factory=lambda: ["INBOX"])
    aliases: list[str] = field(default_factory=list)
    reply_as: str | None = None


def mail_accounts(getenv: Callable[[str], str | None] | None = None) -> list[MailAccount]:
    """Parse the MAIL_* block. A blank USER/PASS yields password=None (reported as skipped)."""
    get = getenv or (lambda k: get_secret(k))
    raw = (get("MAIL_ACCOUNTS") or "").strip()
    out: list[MailAccount] = []
    for label in [x.strip().lower() for x in raw.split(",") if x.strip()]:
        if not re.fullmatch(r"[a-z0-9_]+", label):
            raise ValueError(f"MAIL_ACCOUNTS label {label!r}: use [a-z0-9_] only")
        key = label.upper()
        user = (get(f"MAIL_{key}_USER") or "").strip()
        password = (get(f"MAIL_{key}_PASS") or "").replace(" ", "").strip()
        host_raw = (get(f"MAIL_{key}_HOST") or "imap.gmail.com").strip()
        host, _, port_s = host_raw.partition(":")
        port = int(port_s) if port_s else 993
        folders = [f.strip() for f in (get(f"MAIL_{key}_FOLDERS") or "INBOX").split(",") if f.strip()]
        aliases = [a.strip().lower() for a in (get(f"MAIL_{key}_ALIASES") or "").split(",") if a.strip()]
        reply_as = (get(f"MAIL_{key}_REPLY_AS") or "").strip() or None
        out.append(MailAccount(label, user, password if (user and password) else None,
                               host, port, folders or ["INBOX"], aliases, reply_as))
    return out


@dataclass
class Hints:
    hints: dict[str, list[tuple[str, re.Pattern[str]]]]   # category -> [(lang, regex)]
    receipts: list[re.Pattern[str]]
    weak_names: set[str]
    ignore_senders: set[str]
    aliases: dict[str, dict[str, list[str]]]              # normalized company -> {names, domains}


def load_hints(path: Path = HINTS_PATH) -> Hints:
    raw = load_yaml(str(path)) if path.exists() else {}
    hints: dict[str, list[tuple[str, re.Pattern[str]]]] = defaultdict(list)
    for lang, cats in (raw.get("hints") or {}).items():
        for cat, pats in (cats or {}).items():
            for p in pats or []:
                hints[cat].append((lang, re.compile(p, re.I)))
    receipts = [re.compile(p, re.I) for p in raw.get("receipts") or []]
    weak = {normalize_company(n) for n in raw.get("weak_names") or []}
    ignore = {str(s).strip().lower() for s in raw.get("ignore_senders") or []}
    aliases: dict[str, dict[str, list[str]]] = {}
    for company, spec in (raw.get("aliases") or {}).items():
        spec = spec or {}
        aliases[normalize_company(company)] = {
            "names": [normalize_company(n) for n in spec.get("names") or []],
            "domains": [str(d).strip().lower() for d in spec.get("domains") or []],
        }
    return Hints(dict(hints), receipts, weak, ignore, aliases)


# ----------------------------------------------------------------------------- job keys

def _fold(text: str) -> str:
    """Lowercase, accents stripped, so 'Wízeline' and 'wizeline' compare equal."""
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)).lower()


def normalize_company(name: str | None) -> str:
    s = _fold(name or "")
    s = re.sub(r"[^\w\s&.-]", " ", s)
    prev = None
    while prev != s:               # strip stacked suffixes: "Acme Labs Inc." -> "acme"
        prev = s
        s = SUFFIX_RE.sub(" ", s).strip()
        s = re.sub(r"[\s.,-]+$", "", s)
    s = re.sub(r"[.\-_]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def registered_domain(host: str) -> str:
    """Rough registered domain: last two labels, three for ccTLD second levels."""
    parts = host.lower().strip(".").split(".")
    if len(parts) >= 3 and parts[-2] in {"com", "co", "org", "net", "gov", "edu", "ac"} and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else host.lower()


def _is_ats_host(host: str) -> bool:
    return any(host == h or host.endswith("." + h) for h in ATS_HOSTS)


def domain_from_url(url: str | None) -> str | None:
    if not url:
        return None
    host = (urlsplit(url).hostname or "").lower()
    if not host or _is_ats_host(host):
        return None
    return registered_domain(host)


_SLUG_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^(?:boards|job-boards)\.greenhouse\.io$"), "path0"),
    (re.compile(r"^jobs\.lever\.co$"), "path0"),
    (re.compile(r"^jobs\.ashbyhq\.com$"), "path0"),
    (re.compile(r"^apply\.workable\.com$"), "path0"),
    (re.compile(r"^jobs\.smartrecruiters\.com$"), "path0"),
    (re.compile(r"^ats\.rippling\.com$"), "path0"),
    (re.compile(r"^([a-z0-9-]+)\.(?:teamtailor\.com|pinpointhq\.com|bamboohr\.com|recruitee\.com|breezy\.hr)$"), "host"),
    (re.compile(r"^([a-z0-9-]+)\.wd\d+\.myworkdayjobs\.com$"), "host"),
    (re.compile(r"^([a-z0-9-]+)\.jobs\.personio\.(?:de|com)$"), "host"),
]


def slug_from_url(url: str | None) -> str | None:
    """The company's own spelling on its ATS board: 'framework-computer' -> 'framework computer'."""
    if not url:
        return None
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    segs = [s for s in parts.path.split("/") if s]
    for pat, kind in _SLUG_PATTERNS:
        m = pat.match(host)
        if not m:
            continue
        slug = m.group(1) if kind == "host" else (segs[0] if segs else "")
        slug = slug.lower()
        if slug in GENERIC_SLUGS or re.fullmatch(r"[0-9a-f-]{8,}", slug):
            return None
        return re.sub(r"[-_]+", " ", slug).strip() or None
    return None


@dataclass
class JobKeys:
    job_id: int
    company: str
    title: str
    status: str
    applied_at: str | None
    window: str                                   # ISO date; hits must be >= this
    names: list[tuple[str, str]]                  # (normalized key, kind: name|slug|alias)
    domains: list[str]
    weak: bool = False                            # single-token name in weak_names
    demoted: bool = False                         # auto-demoted this run
    name_re: dict[str, re.Pattern[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for key, _ in self.names:
            self.name_re[key] = re.compile(r"(?<![\w])" + re.escape(key) + r"(?![\w])", re.I)

    @property
    def is_weak(self) -> bool:
        return self.weak or self.demoted


def _iso_date(value: str | None) -> str | None:
    return value[:10] if value and len(value) >= 10 else None


def window_start(row: sqlite3.Row | dict) -> str:
    dates = [d for d in (_iso_date(row["applied_at"]), _iso_date(row["last_contact_at"])) if d]
    base = max(dates) if dates else (_iso_date(row["first_seen"]) or date.today().isoformat())
    return (date.fromisoformat(base) - timedelta(days=WINDOW_PAD_DAYS)).isoformat()


def job_keys(row: sqlite3.Row | dict, hints: Hints) -> JobKeys:
    company = normalize_company(row["company"])
    names: list[tuple[str, str]] = []
    if company:
        names.append((company, "name"))
    slug = slug_from_url(row["url"])
    if slug and slug != company:
        names.append((slug, "slug"))
    domains: list[str] = []
    d = domain_from_url(row["url"])
    if d:
        domains.append(d)
    alias = hints.aliases.get(company)
    if alias:
        names += [(n, "alias") for n in alias["names"] if n and n != company]
        domains += [x for x in alias["domains"] if x not in domains]
    weak = bool(company) and len(company.split()) == 1 and company in hints.weak_names
    return JobKeys(int(row["id"]), row["company"] or "", row["title"] or "", row["status"],
                   _iso_date(row["applied_at"]), window_start(row), names, domains, weak)


def open_jobs(conn: sqlite3.Connection, statuses: Iterable[str], hints: Hints) -> list[JobKeys]:
    marks = ",".join("?" * len(tuple(statuses)))
    rows = conn.execute(
        f"SELECT id, company, title, url, status, applied_at, last_contact_at, first_seen "
        f"FROM jobs WHERE status IN ({marks}) ORDER BY id", tuple(statuses)).fetchall()
    return [job_keys(r, hints) for r in rows]


# ----------------------------------------------------------------------------- IMAP

class ImapClient(Protocol):
    def capability(self) -> tuple[str, list[Any]]: ...
    def login(self, user: str, password: str) -> Any: ...
    def select(self, mailbox: str = ..., readonly: bool = ...) -> Any: ...
    def uid(self, command: str, *args: Any) -> tuple[str, list[Any]]: ...
    def logout(self) -> Any: ...


ClientFactory = Callable[[str, int], ImapClient]


def _default_client(host: str, port: int) -> ImapClient:
    return imaplib.IMAP4_SSL(host, port)


def imap_date(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%d-%b-%Y").lstrip("0")


def _imap_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _ascii(s: str) -> str | None:
    folded = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return folded if folded.isascii() else None


def search_args(job: JobKeys, gmail: bool) -> tuple[str, ...] | None:
    """Args for client.uid('SEARCH', None, *args). None when no key is searchable."""
    keys = [k for k in ([n for n, _ in job.names] + job.domains) if _ascii(k)]
    if not keys:
        return None
    if gmail:
        # Gmail's index is word-based, so `from:<domain>` is exact and cheap; the standard
        # branch below has only substring TEXT, so it searches the domain as text instead.
        # Recall differs slightly by backend on purpose; local confirmation equalizes it.
        terms = []
        for n, _ in job.names:
            if _ascii(n):
                terms.append(f'"{n}"' if " " in n else n)
        terms += [f"from:{d}" for d in job.domains if _ascii(d)]
        q = "(" + " OR ".join(terms) + ") after:" + job.window.replace("-", "/")   # explicit group: after: binds to all
        return ("X-GM-RAW", _imap_quote(q))
    crit = f"TEXT {_imap_quote(keys[-1])}"
    for k in reversed(keys[:-1]):          # IMAP OR is prefix-binary: OR a OR b c
        crit = f"OR TEXT {_imap_quote(k)} {crit}"
    return (f"SINCE {imap_date(job.window)} {crit}",)


def _uids(data: list[Any]) -> list[int]:
    out: list[int] = []
    for chunk in data:
        if isinstance(chunk, bytes) and chunk.strip():
            out += [int(x) for x in chunk.split()]
    return out


def _parse_fetch(data: list[Any]) -> dict[int, bytes]:
    """imaplib FETCH payloads: [(b'1 (UID 5 BODY[...] {n}', b'raw'), b')', ...] -> {5: raw}."""
    out: dict[int, bytes] = {}
    for item in data:
        if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], bytes):
            m = re.search(rb"UID (\d+)", item[0] if isinstance(item[0], bytes) else b"")
            if m:
                out[int(m.group(1))] = item[1]
    return out


def _fetch_batches(client: ImapClient, uids: list[int], what: str) -> dict[int, bytes]:
    out: dict[int, bytes] = {}
    for i in range(0, len(uids), FETCH_BATCH):
        batch = uids[i:i + FETCH_BATCH]
        _, data = client.uid("FETCH", ",".join(str(u) for u in batch), f"(UID {what})")
        out.update(_parse_fetch(data))
    return out


# ----------------------------------------------------------------------------- messages

@dataclass(eq=False)          # identity semantics: hashable, `in` never compares field by field
class Message:
    uid: int
    account: str
    folder: str
    from_name: str
    from_addr: str
    from_domain: str
    to: str
    subject: str
    date: str
    message_id: str
    in_reply_to: str
    references: list[str]
    list_unsubscribe: bool
    precedence: str
    auto_submitted: str
    # filled in later
    matches: dict[int, list[str]] = field(default_factory=dict)     # job_id -> match_on kinds
    body: str | None = None
    thread_key: str = ""
    thread_len: int = 1
    hints: list[str] = field(default_factory=list)
    lead: str = ""
    snippet: str = ""
    accounts_seen: list[str] = field(default_factory=list)

    @property
    def thread_root(self) -> str:
        return self.references[0] if self.references else (self.in_reply_to or self.message_id)

    @property
    def is_relay(self) -> bool:
        return _domain_in(self.from_domain, RELAY_DOMAINS)

    @property
    def is_noreply(self) -> bool:
        return bool(NOREPLY_RE.search(self.from_addr.split("@")[0])) or self.is_relay

    @property
    def strong_kinds(self) -> set[str]:
        return {k for kinds in self.matches.values() for k in kinds if k in STRONG_KINDS}


def _decode(value: str | None) -> str:
    if not value:
        return ""
    try:
        text = str(email.header.make_header(email.header.decode_header(value)))
    except Exception:  # noqa: BLE001 - malformed encoded-word; keep the raw header
        text = value
    return re.sub(r"\s+", " ", text.replace("—", ", ")).strip()


def _strip_id(value: str | None) -> str:
    return (value or "").strip().strip("<>").strip()


def _msg_date(msg: EmailMessage, fallback: str | None) -> str:
    raw = msg.get("Date")
    if raw:
        try:
            dt = email.utils.parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt.astimezone(UTC).date().isoformat()
        except (TypeError, ValueError):
            pass
    return fallback or date.today().isoformat()


def parse_headers(raw: bytes, uid: int, account: str, folder: str, internaldate: str | None = None) -> Message:
    msg = email.message_from_bytes(raw)
    name, addr = email.utils.parseaddr(_decode(msg.get("From")))
    addr = addr.lower()
    domain = addr.rsplit("@", 1)[-1] if "@" in addr else ""
    subject = EXTERNAL_PREFIX_RE.sub("", _decode(msg.get("Subject")))
    refs = [_strip_id(r) for r in (msg.get("References") or "").split() if _strip_id(r)]
    return Message(
        uid=uid, account=account, folder=folder, from_name=name.strip(), from_addr=addr,
        from_domain=domain, to=_decode(msg.get("To")).lower(), subject=subject,
        date=_msg_date(msg, internaldate), message_id=_strip_id(msg.get("Message-ID")),
        in_reply_to=_strip_id(msg.get("In-Reply-To")), references=refs,
        list_unsubscribe=bool(msg.get("List-Unsubscribe")),
        precedence=(msg.get("Precedence") or "").strip().lower(),
        auto_submitted=(msg.get("Auto-Submitted") or "").strip().lower(),
    )


# ----------------------------------------------------------------------------- body text

def extract_text(raw: bytes) -> str:
    """Prefer text/plain; fall back to tag-stripped text/html."""
    msg = email.message_from_bytes(raw)
    plain: list[str] = []
    htmls: list[str] = []
    parts = msg.walk() if msg.is_multipart() else [msg]
    for part in parts:
        ctype = part.get_content_type()
        if ctype not in ("text/plain", "text/html") or part.get("Content-Disposition", "").startswith("attachment"):
            continue
        payload = part.get_payload(decode=True)
        if not isinstance(payload, bytes):
            continue
        charset = part.get_content_charset() or "utf-8"
        try:
            text = payload.decode(charset, errors="replace")
        except LookupError:
            text = payload.decode("utf-8", errors="replace")
        (plain if ctype == "text/plain" else htmls).append(text)
    if plain:
        text = "\n".join(plain)
        if re.search(r"</?(p|br|div|span|a|td|table)\b", text, re.I):   # HTML shipped as text/plain
            text = html_to_text(text)
        return text
    if htmls:
        return html_to_text("\n".join(htmls))
    return ""


def html_to_text(src: str) -> str:
    s = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", src)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>|</li>|</h\d>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s).replace("\u2014", ", ")


_QUOTE_START_RE = re.compile(
    r"^(On .{0,200}wrote:|El .{0,200}escribi[óo]:|-{2,}\s*Original Message\s*-{2,}|"
    r"De:\s.*|From:\s.*|Enviado:\s.*|Sent:\s.*)$", re.I | re.M)
_SIG_START_RE = re.compile(r"^(--\s*$|__+\s*$|Sent from my|Enviado desde mi|Get Outlook for)", re.I | re.M)
_FOOTER_RE = re.compile(
    r"^.*(unsubscribe|darse de baja|cancelar (la )?suscripci[óo]n|manage (your )?(email )?preferences|"
    r"privacy policy|pol[íi]tica de privacidad|confidential(ity)? notice|this email was sent to|"
    r"view (this )?(email )?in (your )?browser|all rights reserved|©).*$", re.I | re.M)
_URL_RE = re.compile(r"https?://([^\s/<>\"')]+)[^\s<>\"')]*", re.I)
_SALUTATION_RE = re.compile(
    r"^\s*(hi|hello|hey|dear|good (morning|afternoon|evening)|hola|estimad[oa]s?|buen[oa]s (d[íi]as|tardes))\b"
    r"[^\n.!?]{0,60}[,!.:]?\s*", re.I)
_THANKS_RE = re.compile(r"^\s*(thank(s| you)( so much| very much)? for [^.!?\n]{0,120}[.!?]|gracias por [^.!?\n]{0,120}[.!?])\s*", re.I)


def clean_text(text: str, limit: int = 800) -> str:
    s = text.replace("\r\n", "\n").replace("\r", "\n").replace("—", ", ")
    s = re.sub(r"^\s*>.*$", "", s, flags=re.M)                # quoted lines
    m = _QUOTE_START_RE.search(s)
    if m and m.start() > 0:
        s = s[:m.start()]
    m = _SIG_START_RE.search(s)
    if m and m.start() > 40:
        s = s[:m.start()]
    s = _FOOTER_RE.sub("", s)
    s = _URL_RE.sub(lambda mm: mm.group(1), s)
    s = re.sub(r"([-_=*~])\1{3,}", " ", s)                      # ----- separators
    s = re.sub(r"[ \t ​‌͏]+", " ", s)
    s = re.sub(r"\s*\n\s*", " ", s)
    s = re.sub(r"\s{2,}", " ", s).strip()
    if limit and len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0] + "..."
    return s or "(no text)"


# ----------------------------------------------------------------------------- matching

def _domain_words(domain: str) -> str:
    """'mail.frame-work.co.uk' -> 'mail frame work co uk', for word-boundary name matching."""
    return re.sub(r"[.\-_]+", " ", _fold(domain)).strip()


def _domain_in(domain: str, pool: Iterable[str]) -> bool:
    return any(domain == d or domain.endswith("." + d) for d in pool)


def _in_window(job: JobKeys, msg: Message) -> bool:
    return msg.date >= job.window


def confirm_headers(msg: Message, jobs: list[JobKeys], own: set[str] | frozenset[str] = frozenset()) -> None:
    """Word-boundary confirmation on From (domain, display name) and Subject.
    Subject matches only for freemail/relay senders and the user's own addresses;
    a named corporate sender matches on its own domain and display name."""
    relay = msg.is_relay
    subject_ok = msg.from_domain in FREEMAIL or relay or not msg.from_domain or msg.from_addr in own
    for job in jobs:
        if not _in_window(job, msg):
            continue
        kinds: list[str] = []
        if msg.from_domain and _domain_in(msg.from_domain, job.domains):
            kinds.append("domain")
        # A recruiter mailing from the company's own domain is a domain hit even when the
        # job url sits on an ATS board (no domain key) and the subject never names the
        # company: alejandro@wizeline.com about "We Would Like to Invite you" is Wizeline.
        # For a weak-named company (google, linear, ...) the inferred hit stays WEAK
        # (`domain_words`, not in STRONG_KINDS): cloud.google.com billing mail must not
        # become a protected strong match that outranks recruiters and dodges the alert cut.
        elif msg.from_domain and any(job.name_re[key].search(_domain_words(msg.from_domain))
                                     for key, _ in job.names):
            kinds.append("domain_words" if job.is_weak else "domain")
        for key, kind in job.names:
            rx = job.name_re[key]
            if rx.search(_fold(msg.from_name)) or rx.search(_fold(msg.from_addr.split("@")[0].replace(".", " "))):
                kinds.append("slug" if kind == "slug" else "alias" if kind == "alias" else "name_from")
            elif subject_ok and rx.search(_fold(msg.subject)):
                kinds.append("slug" if kind == "slug" else "alias" if kind == "alias" else "name_subject")
        if kinds and relay and any(k.startswith("name_") for k in kinds):
            kinds.append("relay")          # an ATS relay only ever mails candidates: the name is the company
        if kinds:
            msg.matches[job.job_id] = sorted(set(kinds))


def confirm_body(msg: Message, jobs: list[JobKeys]) -> None:
    text = _fold(msg.body or "")
    if not text:
        return
    for job in jobs:
        if not _in_window(job, msg) or job.job_id in msg.matches:
            continue
        if any(job.name_re[key].search(text) for key, _ in job.names):
            msg.matches[job.job_id] = ["body"]


def strength(msg: Message, jobs_by_id: dict[int, JobKeys]) -> str:
    if msg.strong_kinds:
        return "strong"
    for jid, kinds in msg.matches.items():
        job = jobs_by_id.get(jid)
        if job and not job.is_weak and any(k.startswith("name_") for k in kinds):
            return "strong"
    return "weak"


def auto_demote(msgs: list[Message], jobs: list[JobKeys]) -> list[str]:
    """A company writes from one or two domains; a dictionary word shows up from many."""
    tune: list[str] = []
    for job in jobs:
        single = [k for k, kind in job.names if kind == "name" and len(k.split()) == 1]
        if not single or job.weak:
            continue
        domains = {m.from_domain for m in msgs
                   if any(k.startswith("name_") for k in m.matches.get(job.job_id, []))
                   and not _domain_in(m.from_domain, job.domains)}
        if len(domains) > DEMOTE_DOMAIN_THRESHOLD:
            job.demoted = True
            tune.append(
                f'tune: "{job.company}" matched mail from {len(domains)} sender domains, treated as weak '
                f"this run.\n      Make it permanent: add {single[0]} to weak_names in config/mail_hints.yaml")
    return tune


# ----------------------------------------------------------------------------- noise cuts

@dataclass
class Cuts:
    seen: dict[str, str]                  # id -> signal it was classified as
    ignore_senders: set[str]
    own: set[str]
    receipts: list[re.Pattern[str]]
    jobs_by_id: dict[int, JobKeys]
    enabled: bool = True


def _receipt_shaped(subject: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(p.search(subject) for p in patterns)


def cut_reason(msg: Message, cuts: Cuts) -> str | None:
    """Return the noise category that removes this message, or None to keep it.
    The `seen` cut is not here: it is applied per thread group in collapse_threads, so it
    can drop a seen message together with everything OLDER in its thread while letting a
    newer reply through."""
    if not cuts.enabled:
        return None
    if msg.from_addr in cuts.ignore_senders or _domain_in(msg.from_domain, cuts.ignore_senders):
        return "ignored"
    if msg.from_addr in cuts.own:
        return "own"
    if msg.auto_submitted.startswith(("auto-replied", "auto-generated")):
        return "autoreply"
    protected = bool(msg.strong_kinds)
    if not protected:
        if _domain_in(msg.from_domain, ALERT_DOMAINS):
            return "alerts"
        if _domain_in(msg.from_domain, SOFT_ALERT_DOMAINS) and ALERT_SUBJECT_RE.search(msg.subject):
            return "alerts"
        if msg.list_unsubscribe and msg.precedence in ("bulk", "list"):
            return "alerts"
    if ECHO_SUBJECT_RE.match(msg.subject):
        return "echoes"
    if _receipt_shaped(msg.subject, cuts.receipts) and not msg.in_reply_to and not msg.references:
        for jid in msg.matches:
            job = cuts.jobs_by_id.get(jid)
            if job and job.applied_at and abs((date.fromisoformat(msg.date) - date.fromisoformat(job.applied_at)).days) <= RECEIPT_GRACE_DAYS:
                return "receipts"
    return None


def seen_signal(entry: object) -> str:
    """State `seen` values are {"signal", "at"} (or a bare signal string from older files)."""
    if isinstance(entry, dict):
        return str(entry.get("signal") or "ignore")
    return str(entry or "ignore")


def load_seen(conn: sqlite3.Connection | None, state: dict, full: bool) -> dict[str, str]:
    """id -> signal. Events rows without a signal count as `reply` (message-only suppression)."""
    if full:
        return {}
    seen = {str(k): seen_signal(v) for k, v in (state.get("seen") or {}).items()}
    if conn is not None:
        for (payload,) in conn.execute("SELECT payload FROM events WHERE kind='email_signal'"):
            try:
                ev = json.loads(payload or "{}")
            except json.JSONDecodeError:
                continue
            for k in ("message_id", "thread_id"):
                v = _strip_id(ev.get(k))
                if v:
                    seen.setdefault(v, str(ev.get("signal") or "reply"))
    return seen


def prune_seen(state: dict, before: str) -> int:
    """Drop seen entries recorded before `before` (ISO date). Undated entries stay. Returns count."""
    seen = state.get("seen") or {}
    stale = [k for k, v in seen.items() if isinstance(v, dict) and str(v.get("at") or "9999") < before]
    for k in stale:
        del seen[k]
    return len(stale)


# ----------------------------------------------------------------------------- threads

def _norm_subject(s: str) -> str:
    return re.sub(r"\s+", " ", REPLY_PREFIX_RE.sub("", _fold(s))).strip()


def collapse_threads(msgs: list[Message], seen: dict[str, str] | None = None) -> tuple[list[Message], int]:
    """One survivor per thread (the newest), thread_len recorded. Fallback key for mail
    without References: subject + sender domain, never across a 7-day gap.

    `seen` (id -> signal) is applied per group here, not per message: a seen message
    silences itself and everything OLDER in its thread (the model already judged that
    state), a seen REJECTION silences the whole thread, and anything newer than a
    non-terminal seen message still surfaces (recruiters reply on the receipt thread).
    Returns (survivors, number of messages dropped as seen)."""
    seen = seen or {}
    groups: dict[str, list[Message]] = defaultdict(list)
    fallback: list[Message] = []
    for m in msgs:
        if m.references or m.in_reply_to:
            groups[m.thread_root].append(m)
        else:
            fallback.append(m)
    rooted = {m for m in fallback if m.message_id and m.message_id in groups}   # the thread's first message
    for m in rooted:
        groups[m.message_id].append(m)
    fallback = sorted((m for m in fallback if m not in rooted), key=lambda m: m.date)
    open_groups: dict[str, list[Message]] = {}
    for m in fallback:
        base = f"{_norm_subject(m.subject)}|{m.from_domain}"
        grp = open_groups.get(base)
        if grp and (date.fromisoformat(m.date) - date.fromisoformat(grp[0].date)).days <= FALLBACK_THREAD_GAP_DAYS:
            grp.append(m)
        else:
            key = f"{base}|{m.date}"
            open_groups[base] = groups[key] = [m]
    out: list[Message] = []
    dropped = 0
    for key, grp in groups.items():
        grp.sort(key=lambda m: (m.date, m.uid))
        ids = {m.message_id for m in grp if m.message_id} | {key}
        if any(seen.get(i) in THREAD_TERMINAL_SIGNALS for i in ids):
            dropped += len(grp)
            continue
        last_seen = max((i for i, m in enumerate(grp) if m.message_id and m.message_id in seen), default=-1)
        if last_seen >= 0:
            dropped += last_seen + 1
            grp = grp[last_seen + 1:]
            if not grp:
                continue
        newest = grp[-1]
        newest.thread_len = len(grp)
        newest.thread_key = key if (newest.references or newest.in_reply_to) else newest.message_id or key
        for m in grp[:-1]:                                      # a job seen anywhere in the thread counts
            for jid, kinds in m.matches.items():
                newest.matches.setdefault(jid, kinds)
        out.append(newest)
    return out, dropped


def rank_key(msg: Message, jobs_by_id: dict[int, JobKeys]) -> tuple:
    return (0 if msg.strong_kinds else 1,
            0 if not msg.is_noreply else 1,
            0 if msg.hints and msg.hints != ["human?"] else 1,
            0 if strength(msg, jobs_by_id) == "strong" else 1,
            msg.date and "".join(chr(255 - ord(c)) for c in msg.date))   # newest first


def cap_per_job(msgs: list[Message], limit: int) -> tuple[list[Message], dict[int, int]]:
    counts: dict[int, int] = defaultdict(int)
    capped: dict[int, int] = defaultdict(int)
    kept: list[Message] = []
    for m in msgs:
        if limit <= 0 or any(counts[j] < limit for j in m.matches):
            kept.append(m)
            for j in m.matches:
                counts[j] += 1
        else:
            for j in m.matches:
                capped[j] += 1
    return kept, dict(capped)


# ----------------------------------------------------------------------------- hints + lead

def tag_hints(msg: Message, hints: Hints) -> None:
    text = msg.snippet if msg.snippet != "(no text)" else ""
    tags: list[str] = []
    first_pos: int | None = None
    for cat, pats in hints.hints.items():
        for _lang, rx in pats:
            hit = rx.search(text)
            if hit:
                tags.append(cat + "?")
                if first_pos is None or hit.start() < first_pos:
                    first_pos = hit.start()
                break
            if rx.search(msg.subject):
                tags.append(cat + "?")
                break
    if _receipt_shaped(msg.subject, hints.receipts):
        tags.append("receipt?")
    if not tags and not msg.is_noreply:
        tags.append("human?")
    msg.hints = list(dict.fromkeys(tags))
    msg.lead = make_lead(text, first_pos)


def body_has_signal(msg: Message, hints: Hints) -> bool:
    """True when a reject/schedule/assessment/offer hint fires in the body text."""
    text = clean_text(msg.body or "", 4000)
    return any(rx.search(text) for cat, pats in hints.hints.items() if cat != "receipt" for _l, rx in pats)


def make_lead(text: str, pos: int | None, width: int = 140) -> str:
    if not text:
        return "(no text)"
    if pos is not None:
        start = max(0, pos - width // 3)
        start = text.rfind(" ", 0, start) + 1 if start else 0
        end = min(len(text), start + width)
        end = text.rfind(" ", start, end) if end < len(text) and " " in text[start:end] else end
        return ("..." if start else "") + text[start:end].strip() + ("..." if end < len(text) else "")
    s = _SALUTATION_RE.sub("", text, count=1)
    s = _THANKS_RE.sub("", s, count=1)
    s = s.strip() or text
    if len(s) <= 120:
        return s
    cut = s[:120].rsplit(" ", 1)[0]
    return cut + "..."


# ----------------------------------------------------------------------------- state

def load_state(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            pass
    return {"accounts": {}, "seen": {}, "zero_candidates": {}}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=1, sort_keys=True))


# ----------------------------------------------------------------------------- the sweep

@dataclass
class AccountReport:
    label: str
    user: str
    host: str
    folders: list[str]
    status: str
    candidates: int = 0
    threads: int = 0
    noise: dict[str, int] = field(default_factory=dict)


@dataclass
class SweepResult:
    generated_at: str
    since: str
    open_jobs: int
    accounts: list[AccountReport]
    tune: list[str]
    legend: list[dict]
    threads: list[dict]
    snippets: dict[int, str]


def _gmail(client: ImapClient) -> bool:
    try:
        _, caps = client.capability()
    except Exception:  # noqa: BLE001 - capability is optional; fall back to standard SEARCH
        return False
    blob = b" ".join(c if isinstance(c, bytes) else str(c).encode() for c in caps)
    return b"X-GM-EXT-1" in blob.upper()


def _scan_folder(client: ImapClient, account: MailAccount, folder: str, jobs: list[JobKeys],
                 horizon: str, scan_all: bool, per_job_hits: dict[int, int]) -> list[Message]:
    client.select(folder, readonly=True)
    gmail = _gmail(client)
    uids: set[int] = set()
    if scan_all:
        _, data = client.uid("SEARCH", None, f"SINCE {imap_date(horizon)}")
        uids.update(_uids(data))
    else:
        for job in jobs:
            args = search_args(job, gmail)
            if not args:
                continue
            _, data = client.uid("SEARCH", None, *args)
            found = _uids(data)
            per_job_hits[job.job_id] += len(found)
            uids.update(found)
    ordered = sorted(uids)
    raw = _fetch_batches(client, ordered, f"BODY.PEEK[HEADER.FIELDS ({HEADER_FIELDS})]")
    return [parse_headers(raw[u], u, account.label, folder) for u in ordered if u in raw]


def _fetch_bodies(client: ImapClient, msgs: list[Message]) -> None:
    """UIDs are per folder, so reselect each message's folder (read-only) before fetching.
    Without this, a fetch after the folder loop runs against whichever folder was selected
    last and every other folder's bodies come back empty."""
    need = [m for m in msgs if m.body is None]
    by_folder: dict[str, list[Message]] = defaultdict(list)
    for m in need:
        by_folder[m.folder].append(m)
    for folder, group in by_folder.items():
        client.select(folder, readonly=True)
        raw = _fetch_batches(client, [m.uid for m in group], "BODY.PEEK[]")
        for m in group:
            m.body = extract_text(raw[m.uid]) if m.uid in raw else ""


def sweep(conn: sqlite3.Connection | None, accounts: list[MailAccount], hints: Hints, *,
          jobs: list[JobKeys] | None = None, state_path: Path = STATE_PATH,
          client_factory: ClientFactory = _default_client, since: str | None = None,
          max_days: int = 120, statuses: Iterable[str] = OPEN_STATUSES, limit_per_job: int = 3,
          snippet_chars: int = 800, scan_all: bool = False, full: bool = False,
          keep_noise: bool = False, today: date | None = None,
          all_labels: Iterable[str] | None = None) -> SweepResult:
    """`all_labels`: every credentialed account the user has configured, even ones left out
    of this run by --account. The zero-candidate tune line only fires once ALL of them have
    reported no mail for a job; a partial sweep must not blame the company for the other
    mailbox's silence."""
    today = today or date.today()
    labels_all = set(all_labels) if all_labels is not None else {a.label for a in accounts if a.password}
    if jobs is None:
        if conn is None:
            raise ValueError("sweep needs a db connection or an explicit jobs list")
        jobs = open_jobs(conn, tuple(statuses), hints)
    jobs_by_id = {j.job_id: j for j in jobs}
    state = load_state(state_path)
    prune_seen(state, (today - timedelta(days=max_days)).isoformat())
    seen = load_seen(conn, state, full)
    own = {a.user.lower() for a in accounts if a.user} | {al for a in accounts for al in a.aliases}
    cuts = Cuts(seen, hints.ignore_senders, own, hints.receipts, jobs_by_id, enabled=not keep_noise)

    horizon = since or (min((j.window for j in jobs), default=today.isoformat()))
    floor = (today - timedelta(days=max_days)).isoformat()
    floor_note = None
    if not since and horizon < floor:
        floor_note = f"note: horizon floored to {floor} by --max-days {max_days} (earliest window {horizon})"
        horizon = floor
        for jb in jobs:
            if jb.window < floor:
                jb.window = floor

    reports: list[AccountReport] = []
    survivors: list[Message] = []
    hits_by_acct: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    tune: list[str] = [floor_note] if floor_note else []
    by_mid: dict[str, Message] = {}

    for acct in accounts:
        rep = AccountReport(acct.label, acct.user, acct.host, list(acct.folders), "ok")
        reports.append(rep)
        if acct.password is None:
            key = acct.label.upper()
            missing = f"MAIL_{key}_USER" if not acct.user else f"MAIL_{key}_PASS"
            rep.status = f"skipped: {missing} not set"
            continue
        noise: dict[str, int] = defaultdict(int)
        acct_msgs: list[Message] = []
        try:
            client = client_factory(acct.host, acct.port)
            client.login(acct.user, acct.password)
        except Exception as e:  # noqa: BLE001 - one bad account never breaks the sweep
            rep.status = f"error: {type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}".rstrip(": ")
            continue
        try:
            for folder in acct.folders:
                try:
                    msgs = _scan_folder(client, acct, folder, jobs, horizon, scan_all, hits_by_acct[acct.label])
                except Exception as e:  # noqa: BLE001 - a missing folder is reported, not fatal
                    rep.status = f"error: {folder}: {type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}"
                    continue
                rep.candidates += len(msgs)
                for m in msgs:
                    confirm_headers(m, jobs, own)
                relay = [m for m in msgs if not m.matches and m.is_relay]
                if relay:
                    _fetch_bodies(client, relay)
                    for m in relay:
                        confirm_body(m, jobs)
                acct_msgs += [m for m in msgs if m.matches]
            tune += auto_demote(acct_msgs, jobs)
            kept: list[Message] = []
            receipt_shaped = [m for m in acct_msgs if cut_reason(m, cuts) == "receipts"]
            if receipt_shaped:                      # a rejection template can wear a receipt subject
                _fetch_bodies(client, receipt_shaped)
            for m in acct_msgs:
                if m.message_id and m.message_id in by_mid:           # cross-account duplicate
                    by_mid[m.message_id].accounts_seen.append(acct.label)
                    continue
                # a seen message skips the other cuts: collapse_threads counts it as seen
                # and uses it to silence what is older in its thread
                reason = None if (m.message_id and m.message_id in seen) else cut_reason(m, cuts)
                if reason == "receipts" and body_has_signal(m, hints):
                    reason = None
                if reason:
                    noise[reason] += 1
                    continue
                m.accounts_seen = [acct.label]
                if m.message_id:
                    by_mid[m.message_id] = m
                kept.append(m)
            before = len(kept)
            kept, seen_dropped = collapse_threads(kept, seen)
            if seen_dropped:
                noise["seen"] = seen_dropped
            if before - seen_dropped > len(kept):
                noise["collapsed"] = before - seen_dropped - len(kept)
            _fetch_bodies(client, kept)
            for m in kept:
                m.snippet = clean_text(m.body or "", snippet_chars) if snippet_chars else "(no text)"
                tag_hints(m, hints)
            survivors += kept
            rep.threads = len(kept)
        finally:
            try:
                client.logout()
            except Exception:  # noqa: BLE001 - logout failures are irrelevant to a read-only run
                pass
        rep.noise = dict(noise)

    survivors.sort(key=lambda m: rank_key(m, jobs_by_id))
    survivors, capped = cap_per_job(survivors, limit_per_job)

    # tune 2: a name key whose every thread was already classified as noise
    for job in jobs:
        hits = [m for m in by_mid.values() if job.job_id in m.matches]
        if len(hits) >= 3 and all(seen.get(m.thread_root, seen.get(m.message_id)) in
                                  ("ignore", "ambiguous", "receipt") for m in hits) and job.domains:
            tune.append(
                f'tune: "{job.company}" only ever matched mail you never classified as a signal.\n'
                f"      If you are a customer, not a candidate: add {job.domains[0]} to ignore_senders "
                f"in config/mail_hints.yaml")
    # tune 3: an open job that never produces a candidate in ANY configured mailbox.
    # Counters are per account so `--account personal` cannot blame the company for
    # mail that lands on the other address.
    raw_zero = state.get("zero_candidates") or {}
    zero: dict[str, dict[str, int]] = {str(a): {str(j): int(n) for j, n in (v or {}).items()}
                                       for a, v in raw_zero.items() if isinstance(v, dict)}
    swept_ok = {r.label for r in reports if r.status == "ok"} if not scan_all else set()
    job_ids = {str(j.job_id) for j in jobs}
    prev_accounts = state.get("accounts") or {}
    for label in swept_ok:
        counts = zero.setdefault(label, {})
        # a re-run on the same day is not new evidence: the counter moves once per day
        new_day = str((prev_accounts.get(label) or {}).get("swept_at") or "")[:10] != today.isoformat()
        for job in jobs:
            key = str(job.job_id)
            if hits_by_acct[label].get(job.job_id):
                counts[key] = 0
            elif new_day:
                counts[key] = counts.get(key, 0) + 1
    if swept_ok and labels_all and labels_all <= set(zero):
        silent = [(job, min(zero[label].get(str(job.job_id), 0) for label in labels_all)) for job in jobs]
        silent = [(job, n) for job, n in silent if n >= ZERO_CANDIDATE_SWEEPS]
        for job, n in silent[:TUNE_LINES_MAX]:
            tune.append(
                f"tune: job {job.job_id} ({job.company}, {job.title}) produced 0 candidates on {n} "
                f"sweep days across every mailbox.\n      If they wrote from another name or domain: "
                f"add it under aliases in config/mail_hints.yaml, or run with --keep-noise to see what was cut")
        if len(silent) > TUNE_LINES_MAX:
            tune.append(f"tune: {len(silent) - TUNE_LINES_MAX} more jobs with no candidates on "
                        f"{ZERO_CANDIDATE_SWEEPS}+ sweep days; ids: "
                        + ", ".join(str(j.job_id) for j, _ in silent[TUNE_LINES_MAX:]))
    state["zero_candidates"] = {a: {k: v for k, v in c.items() if k in job_ids} for a, c in zero.items()}
    state.setdefault("accounts", {})
    for r in reports:
        if r.status == "ok":
            state["accounts"][r.label] = {"swept_at": datetime.combine(today, datetime.now(UTC).time(), UTC)
                                          .isoformat(timespec="seconds")}
    save_state(state_path, state)

    threads_out: list[dict] = []
    snippets: dict[int, str] = {}
    per_job_threads: dict[int, int] = defaultdict(int)
    for i, m in enumerate(survivors, start=1):
        for jid in m.matches:
            per_job_threads[jid] += 1
        threads_out.append({
            "id": i, "account": m.account, "accounts_seen": m.accounts_seen,
            "job_ids": sorted(m.matches), "match_on": sorted({k for ks in m.matches.values() for k in ks}),
            "strength": strength(m, jobs_by_id), "hints": m.hints,
            "thread_id": m.thread_root, "thread_len": m.thread_len,
            "from": f"{m.from_name} <{m.from_addr}>" if m.from_name else m.from_addr,
            "from_domain": m.from_domain, "to": m.to, "subject": m.subject, "date": m.date,
            "message_id": m.message_id, "lead": m.lead,
        })
        snippets[i] = m.snippet
    legend = [{"job_id": j.job_id, "company": j.company, "title": j.title, "status": j.status,
               "applied_at": j.applied_at, "threads": per_job_threads[j.job_id],
               "capped": capped.get(j.job_id, 0)}
              for j in jobs if per_job_threads[j.job_id] or capped.get(j.job_id)]
    return SweepResult(datetime.now(UTC).isoformat(timespec="seconds"), horizon, len(jobs),
                       reports, tune, legend, threads_out, snippets)


# ----------------------------------------------------------------------------- output

def write_result(res: SweepResult, inbox_path: Path = INBOX_PATH, snippets_path: Path = SNIPPETS_PATH) -> None:
    inbox_path.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "generated_at": res.generated_at, "since": res.since, "open_jobs": res.open_jobs,
        "accounts": [a.__dict__ for a in res.accounts], "tune": res.tune,
        "legend": res.legend, "threads": res.threads,
    }
    inbox_path.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    with open(snippets_path, "w") as f:
        for i, snip in res.snippets.items():
            f.write(json.dumps({"id": i, "snippet": snip}, ensure_ascii=False) + "\n")


def load_result(inbox_path: Path = INBOX_PATH) -> dict:
    if not inbox_path.exists():
        raise SystemExit(f"{inbox_path} not found; run `python -m src.mail_fetch` first")
    return json.loads(inbox_path.read_text())


def load_snippets(snippets_path: Path = SNIPPETS_PATH) -> dict[int, str]:
    out: dict[int, str] = {}
    if snippets_path.exists():
        for line in snippets_path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                out[int(row["id"])] = row["snippet"]
    return out


def format_summary(doc: dict) -> list[str]:
    lines = []
    for a in doc["accounts"]:
        noise = a.get("noise") or {}
        noise_s = ", ".join(f"{k} {v}" for k, v in noise.items() if v) or "none"
        folders = ",".join(a.get("folders") or [])
        lines.append(f"{a['label']:<10} {a.get('user') or '(no user)':<32} {folders:<24} {a['status']}"
                     + (f"  candidates {a['candidates']}  threads {a['threads']}  noise: {noise_s}"
                        if a["status"] == "ok" else ""))
    lines += doc.get("tune") or []
    return lines


def format_legend(doc: dict) -> list[str]:
    lines = []
    for j in doc.get("legend") or []:
        capped = f"  capped {j['capped']}" if j.get("capped") else ""
        lines.append(f"{j['job_id']:>6}  {j['company'][:22]:<22} {j['title'][:38]:<38} {j['status']:<10}"
                     f" applied {j.get('applied_at') or '?':<10} threads {j['threads']}{capped}")
    return lines


def _from_col(t: dict) -> str:
    dom = t.get("from_domain") or ""
    if dom in FREEMAIL:
        name = t["from"].split("<")[0].strip() or dom
        return f"{name} (freemail)"[:22]
    return dom[:22]


def format_manifest(doc: dict, page: int = 1, page_size: int = 80) -> list[str]:
    threads = doc.get("threads") or []
    total = len(threads)
    start, end = (page - 1) * page_size, page * page_size
    rows = threads[start:end]
    lines = [f"{'id':>4}  {'acct':<8} {'job':<12} {'date':<10}  {'from':<22} {'hints':<22} subject | lead"]
    for t in rows:
        hints = " ".join(t.get("hints") or [])
        if t.get("strength") == "weak":
            hints = (hints + " weak").strip()
        jobs = ",".join(str(j) for j in t["job_ids"])
        lines.append(f"{t['id']:>4}  {t['account']:<8} {jobs:<12} {t['date']:<10}  {_from_col(t):<22} "
                     f"{hints[:22]:<22} {t['subject']} | {t['lead']}")
    if not rows:
        lines.append("(no threads)")
    if end < total:
        lines.append(f"{total - end} more lines, run: python -m src.mail_fetch manifest --page {page + 1}")
    return lines


def format_show(doc: dict, snippets: dict[int, str], ids: list[int]) -> list[str]:
    by_id = {t["id"]: t for t in doc.get("threads") or []}
    lines: list[str] = []
    for i in ids:
        t = by_id.get(i)
        if not t:
            lines.append(f"[{i}] unknown id")
            continue
        jobs = ",".join(str(j) for j in t["job_ids"])
        lines.append(f"[{i}] {t['account']} job {jobs} | {t['from']} | {t['date']} | {t['subject']}")
        lines.append(snippets.get(i, "(no text)"))
        lines.append("")
    return lines


# ----------------------------------------------------------------------------- CLI

def _hint_no_accounts() -> str:
    return ("no mail accounts configured: set MAIL_ACCOUNTS (and MAIL_<LABEL>_USER / _PASS) in .env, "
            "see docs/mail-setup.md")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read-only inbox pull for /jh-gmail-sync")
    sub = ap.add_subparsers(dest="cmd")
    run = sub.add_parser("run", help="sweep every configured account (default)")
    run.add_argument("--account", action="append", help="only these labels")
    run.add_argument("--since", help="YYYY-MM-DD, overrides the per-job horizon")
    run.add_argument("--max-days", type=int, default=120)
    run.add_argument("--status", nargs="+", default=list(OPEN_STATUSES), choices=STATUSES, metavar="STATUS",
                     help=f"pipeline statuses to sweep (default: {' '.join(OPEN_STATUSES)})")
    run.add_argument("--limit-per-job", type=int, default=3)
    run.add_argument("--snippet-chars", type=int, default=800)
    run.add_argument("--scan-all", action="store_true", help="horizon-wide header pull instead of per-job search")
    run.add_argument("--full", action="store_true", help="ignore the seen list and past evidence")
    run.add_argument("--keep-noise", action="store_true", help="disable the noise cuts (debugging)")
    run.add_argument("--page-size", type=int, default=80)
    man = sub.add_parser("manifest", help="print the manifest from the last run")
    man.add_argument("--page", type=int, default=1)
    man.add_argument("--page-size", type=int, default=80)
    show = sub.add_parser("show", help="print cleaned snippets for the given ids")
    show.add_argument("ids", nargs="+", type=int)

    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv[0].startswith("-"):
        argv = ["run", *argv]
    args = ap.parse_args(argv)

    if args.cmd == "manifest":
        doc = load_result(INBOX_PATH)
        print("\n".join(format_legend(doc)))
        print("\n".join(format_manifest(doc, args.page, args.page_size)))
        return 0
    if args.cmd == "show":
        if len(args.ids) > SHOW_MAX_IDS:
            print(f"show: at most {SHOW_MAX_IDS} ids per call (got {len(args.ids)})")
            return 1
        print("\n".join(format_show(load_result(INBOX_PATH), load_snippets(SNIPPETS_PATH), args.ids)))
        return 0

    configured = mail_accounts()
    accounts = configured
    if args.account:
        wanted = {a.lower() for a in args.account}
        accounts = [a for a in configured if a.label in wanted]
    hints = load_hints()
    conn = connect()
    if not accounts:
        print(_hint_no_accounts())
    res = sweep(conn, accounts, hints, state_path=STATE_PATH, client_factory=_default_client,
                since=args.since, max_days=args.max_days, statuses=args.status,
                limit_per_job=args.limit_per_job, snippet_chars=args.snippet_chars,
                scan_all=args.scan_all, full=args.full, keep_noise=args.keep_noise,
                all_labels=[a.label for a in configured if a.password])
    write_result(res, INBOX_PATH, SNIPPETS_PATH)
    doc = load_result(INBOX_PATH)
    print("\n".join(format_summary(doc)))
    if doc["legend"]:
        print()
        print("\n".join(format_legend(doc)))
    print()
    print("\n".join(format_manifest(doc, 1, args.page_size)))
    print(f"\nwrote {INBOX_PATH} ({len(doc['threads'])} threads) and {SNIPPETS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
