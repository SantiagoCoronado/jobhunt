# Spec: portable multi-account inbox pull (`src/mail_fetch.py`)

Status: v2. ALL PHASES SHIPPED. Phase A SHIPPED 2026-09-01 (`src/mail_fetch.py`, `config/mail_hints.yaml`, `tests/test_mail_fetch.py`, PR #9). Phase B SHIPPED 2026-09-01 (`/jh-gmail-sync` rewritten around the manifest, `gmail_pull` evidence gains account + thread_id, `ignore` signal, `--apply` records seen ids; `/jh-followups` reply-from-the-right-mailbox rule; `/jh-hunt` steps 2 and 4, PR #10).
Phase C SHIPPED 2026-09-01 (`docs/mail-setup.md`, `.env.example` block, CLAUDE.md Track
paragraph, pointer in the email spec, hint redirected, PR #11). Phase D SHIPPED 2026-09-01
(both real accounts swept; fixes forced by real mail: per-folder body fetch, company name
matched against the sender's own domain, seen applied per thread group with older
siblings, folded touches recorded, HTML in text/plain, zero-candidate counter per day;
measured budget in A6). v1 reviewed by a Fable sub-agent the same day;
its findings (job legend, hint-centered leads, receipt-cut gating, name stoplist, id format,
thread exclusion, file split, Outlook correction, honest budget) are folded in below,
together with the owner's server-side-search idea (A3). The reviewer's conditional Haiku
relevance pass was declined by the owner: one model, one context, no second agent.

## Problem

`/jh-gmail-sync` reads the inbox through the Gmail MCP connector, which is bound to exactly one
Google account per Claude Code login. Anyone who applies from a second address (a dedicated
"applications" mailbox is common) gets a sweep that looks clean while recruiters are writing to
the other account. On this repo's own pipeline the connected account saw 1 live thread while
the unconnected one held 5 (verified 2026-08-10, again 2026-09-01: Caylent, Wizeline,
HackerEval, Cosuno were all invisible). A clean sweep is currently not evidence of anything.

The fix has to work for any user of a public clone, so it cannot depend on a connector, a
specific MCP server, or a Google Cloud project. And it has to be cheap in model tokens: the
MCP path today hands the model whole threads (2k to 8k tokens each, HTML included).

## Goal

Move the mailbox read into the deterministic Python layer, where discovery sources already
live. Any number of accounts, any IMAP provider, credentials in `.env`, read-only by protocol,
and the LLM keeps doing exactly one job: classifying candidate messages into signals from a
compact manifest. The applier (`src/gmail_pull.py`) and its guardrails do not change shape.

## Non-goals

- Gmail API / OAuth. It needs a Cloud project, a consent screen, and an "unverified app"
  warning per user. A possible later adapter behind the same output files, not built now.
- Sending, drafting, labeling, marking read. The fetcher never writes to a mailbox.
- A daemon or IMAP IDLE. This is a pull that runs when the sync runs.
- Exchange/EWS, Outlook.com, or any non-IMAP-with-password provider. Users on those set up
  forwarding into a supported mailbox (docs).
- Classifying in Python. Keyword rules for "rejected" vs "next step" are exactly the brittle
  thing the LLM step exists to avoid. Python narrows the pile; Claude reads it. Regex hints
  carry a question mark and are never applied.

## Design principles

1. **Same shape as discovery.** One `.env` block per account, `get_secret` reads it, an account
   with no password prints a hint and yields nothing, the run never breaks on one bad account.
2. **Read-only at the protocol layer.** Folders open with `EXAMINE` (`select(readonly=True)`),
   every fetch is `BODY.PEEK`, and no `STORE`, `COPY`, `EXPUNGE`, or `APPEND` is ever issued.
   The skill's "strictly read-only" rule becomes a property of the tool.
3. **`data/` is the only landing zone.** Snippets are bodies. They live in
   `data/mail_snippets.jsonl` (gitignored, overwritten per run) and nowhere else. Nothing
   body-derived reaches `gmail_pull.json`, the DB, or a report.
4. **The applier's contract does not move.** Same `gmail_pull.json` schema plus two additive
   evidence fields (`account`, `thread_id`); same guardrails.
5. **Provider-agnostic input.** The skill reads the printed manifest. IMAP today, an OAuth
   adapter later, the Gmail MCP as a fallback: invisible to classification.
6. **Tokens are the scarce resource, not bandwidth.** Everything decidable without a model is
   decided in Python. The model sees a legend plus one line per surviving thread and pulls
   text only for lines it cannot settle. The cheap path must be the only easy path (A5, B1).
7. **Counts next to every claim.** The budget in A6 is stated per email and per sweep with
   the fixed costs included, and the run prints its own line counts so the estimate can be
   checked against reality.

---

## Phase A: the fetcher (`src/mail_fetch.py` + `tests/test_mail_fetch.py`)

### A1. Configuration

`.env` (block added to `.env.example`):

```
# Inbox pull for /jh-gmail-sync. One label per mailbox you apply from, comma separated.
# Each label needs MAIL_<LABEL>_USER and MAIL_<LABEL>_PASS (an app password, never your
# login password). See docs/mail-setup.md for where to mint one per provider.
MAIL_ACCOUNTS=personal,apps
MAIL_PERSONAL_USER=
MAIL_PERSONAL_PASS=
MAIL_APPS_USER=
MAIL_APPS_PASS=
# Optional per label. HOST may carry :port (default imap.gmail.com:993, implicit TLS).
# FOLDERS is a comma list; Gmail users should add [Gmail]/Spam, first-contact ATS mail
# lands there more often than expected. ALIASES are extra From addresses that are you.
# MAIL_APPS_HOST=imap.gmail.com
# MAIL_APPS_FOLDERS=INBOX,[Gmail]/Spam
# MAIL_APPS_ALIASES=me@mydomain.com
# MAIL_APPS_REPLY_AS=   # only for a forwarding target: the address replies must go out from
```

- Labels `[a-z0-9_]+`, uppercased for env keys. `MAIL_ACCOUNTS` absent or empty means not
  configured: print the setup hint, write output files with zero accounts, exit 0.
- `PASS` stripped of internal spaces (Gmail shows app passwords in groups of four).
- Default folder `INBOX`. `[Gmail]/All Mail` is a documented option (larger, includes sent
  mail; own-reply exclusion in A3.6 handles that).
- Real environment variables override `.env`, like every other secret.
- `mail_accounts() -> list[MailAccount]` (dataclass: label, user, password, host, port,
  folders, aliases, reply_as). Blank USER or PASS yields `password=None`, reported as
  skipped rather than dropped.

`config/mail_hints.yaml` (committed, user-editable, per-language blocks):

```yaml
hints:            # regex lists; a hit tags the thread, it never decides anything
  en:
    reject: ["unfortunately", "other candidates", "not (be )?moving forward", "decided to (pursue|proceed with)", "not selected"]
    schedule: ["calendly", "schedule", "availability", "zoom", "google meet", "interview"]
    assessment: ["assessment", "take-home", "coding challenge", "hackerrank", "codility", "hackereval"]
    offer: ["offer letter", "pleased to offer", "compensation package"]
  es:
    reject: ["lamentamos", "otros candidatos", "no continuar", "no seguir adelante"]
    schedule: ["entrevista", "agendar", "disponibilidad"]
    assessment: ["prueba t[ée]cnica", "evaluaci[óo]n"]
receipts:         # receipt-shaped subjects, en + es; see A3.6 for the gate
  - "application (was )?received"
  - "thank(s| you) for (applying|your application)"
  - "we('ve| have) received your"
  - "gracias por (tu|su) (postulaci[óo]n|aplicaci[óo]n)"
weak_names:       # single-token company names that collide with ordinary mail
  [google, socket, tailor, handle, landing, linear, kraken, mercury, dropbox, warp, ramp,
   clara, consider, primero, resend, openai]
ignore_senders:   # addresses or domains never matched (companies you are a customer of)
  []
aliases:          # company -> extra names and domains used in mail
  "Framework Computer": {names: ["Framework"], domains: ["frame.work"]}
  "Handle": {domains: ["usehandle.ai"]}
```

`RELAY_DOMAINS` (ATS and scheduling senders whose From never names the company) and
`ALERT_DOMAINS` (job-alert senders) are module constants; the yaml is what users edit.

### A2. What to look for: open applications and their match keys

Rows with `status IN ('applied','screen','interview','offer')`. Per job:

- **window start** = later of `applied_at` and `last_contact_at`, minus 2 days; `first_seen`
  when neither exists. A message is a hit for job J only if dated at or after J's window.
- **name keys**: the company name lowercased with corporate suffixes stripped (`inc`, `llc`,
  `ltd`, `gmbh`, `s.a. de c.v.`, `sa de cv`, `corp`, `co`, punctuation), plus the ATS slug
  from `url` (`job-boards.greenhouse.io/clara`, `jobs.ashbyhq.com/openai`,
  `jobs.lever.co/acme`), plus `aliases.names` from the yaml. Local match is a word-boundary
  regex of the whole key.
- **domain keys**: the registered domain of `url` unless the host is an ATS or board
  (greenhouse, lever, ashby, workday, smartrecruiters, teamtailor, pinpoint, rippling,
  bamboohr, personio, workable, jobvite, icims, recruitee, breezy, getonbrd, remoteok,
  weworkremotely, torre, themuse, findwork, adzuna, careerjet, linkedin, indeed, glassdoor);
  `boards.` and `jobs.` prefixes collapse; plus `aliases.domains`.
- **strength**: domain hits and slug hits are `strong`. A name hit is `strong` when the name
  has 2+ tokens and is not in `weak_names`; every single-token name in `weak_names` is
  `weak`; a single-token name not in the list is `strong` unless auto-demoted (next
  bullet). No length heuristic. Weak hits are kept but ranked last (A3.7) and flagged in
  the manifest.
- **auto-demotion**: a company you applied to writes from one or two sender domains; a
  dictionary word or product name shows up from many. After candidate generation, a
  single-token name key whose candidates come from more than 5 distinct sender domains
  inside its window is treated as `weak` for this run, and the run prints a `tune:` line
  (A5) telling the user how to make it permanent. The yaml stays the manual override.
- **subject matching** applies only when the sender domain is freemail or a relay; a named
  corporate sender matches on display name and domain only.

The fetch horizon is the earliest window start across open rows, floored by `--max-days`
(default 120, prints a note when it bites); `--since` overrides both.

### A3. Fetch strategy per account and folder

**A3.1 Connect.** `IMAP4_SSL(host, port)`, `login`, `select(folder, readonly=True)`. Any
exception becomes `status: "error: <class>: <first line>"` for that account/folder and the
run continues. Passwords never appear in errors or logs.

**A3.2 Candidate generation, server-side (default).** For each job, one `UID SEARCH` scoped
to its window:

```
SINCE <window> (OR (OR FROM "<key>" SUBJECT "<key>") TEXT "<key>")   # repeated per key, OR-chained
```

Keys are the job's name keys and domain keys. When the server's CAPABILITY response
advertises `X-GM-EXT-1` (Gmail and Workspace, detected by capability, never by hostname,
since Workspace custom domains hit the same servers) use `X-GM-RAW` instead, which gives
word-level matching through Gmail's own index:
`"<name>" OR from:<domain> OR <slug> after:<YYYY/MM/DD>`. Standard `SEARCH` is substring
and case-insensitive, so on other servers expect more candidates; local confirmation (A3.4)
makes the result identical, only the header-fetch count differs. Union the UIDs across jobs,
remembering which jobs each UID came from. This replaces a 60-day header pull with under a
hundred small round trips and makes the per-job window a server-side fact.

`--scan-all` is the fallback for servers where `TEXT` search is unusable (no full-text
index, or capped): pull `HEADER.FIELDS` for every UID `SINCE <horizon>` and match locally.
Same downstream pipeline either way.

Also, per job whose `applied_at` or latest status event is newer than the account's
`swept_at` (in `data/mail_state.json`), the search runs regardless of anything cached, so
an assessment invite that arrived before the row was marked applied is caught on the next
sweep without `--full`.

**A3.3 Header pass.** For the union: `BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE
MESSAGE-ID IN-REPLY-TO REFERENCES LIST-UNSUBSCRIBE PRECEDENCE AUTO-SUBMITTED)]` in batches
of 200. Decode RFC 2047, normalize whitespace, replace U+2014 with `, ` in every subject
(the zero em-dash rule, applied at the source so nothing downstream can copy one), parse
`Date` to ISO `YYYY-MM-DD` UTC with `INTERNALDATE` as the fallback for malformed headers.

**A3.4 Local confirmation.** IMAP `SEARCH` is substring and case-insensitive ("Clara"
matches "declaration"), so every candidate is re-checked locally with the word-boundary
regex on From display name, From domain, Subject (subject only per the A2 rule). Record
`match_on` (`domain`, `slug`, `name_from`, `name_subject`, `alias`) and strength. A
candidate that fails local confirmation and is not from a relay domain is discarded.

**A3.5 Relay pass.** Candidates from `RELAY_DOMAINS` (greenhouse-mail.io, greenhouse.io,
lever.co, hire.lever.co, ashbyhq.com, smartrecruiters.com, myworkday.com, workday.com,
workable.com, workablemail.com, bamboohr.com, jobvite.com, icims.com, teamtailor.com,
pinpointhq.com, rippling.com, breezy.hr, recruitee.com, personio.de, hackerrank.com,
hackereval.com, codility.com, coderbyte.com, calendly.com, goodtime.io) that failed header
confirmation get their body fetched and name-matched on the cleaned text. `match_on: body`.
Honest cost note: on a first run this is potentially hundreds of body fetches (every ATS
receipt of an active applier); bandwidth only, nothing is stored unless matched.

**A3.6 Exclusions and noise cuts** (zero tokens; every cut is a category the skill ignores
by rule, so no outcome changes). Order matters:

1. *Already processed*: thread root or message id present in `events` (`email_signal`
   evidence, RFC 822 Message-ID with angle brackets stripped) or in the `seen` list of
   `data/mail_state.json` (B2 appends every id of an applied batch there, ambiguous ones
   included). Legacy events carrying Gmail API hex ids never match; that is fine.
2. *Ignored senders*: `ignore_senders` from the yaml, exact address or domain.
3. *Own mail*: From is any `MAIL_*_USER` or `MAIL_*_ALIASES` address. Keeps All Mail and
   Sent-copy providers from making the user's "Tuesday works" the newest message.
4. *Auto-replies*: `Auto-Submitted: auto-replied|auto-generated`. Out-of-office answers to
   a nudge otherwise hide the recruiter's real reply and look like a human touch.
5. *Alerts*: sender domain in `ALERT_DOMAINS` (indeed.com, glassdoor.com, ziprecruiter.com,
   jobalerts.*, and the alert subdomains of linkedin.com), or `List-Unsubscribe` together
   with `Precedence: bulk|list`. Exceptions: linkedin.com, wellfound.com, hired.com are cut
   only when the subject matches an alert pattern (`jobs for you`, `new jobs`, `who's
   viewed`, `recommended`) because they also carry recruiter messages; and NO header-based
   cut applies to a message matched by domain, slug, alias, or relay body. A message from
   the company's own domain always earns its manifest line.
6. *Calendar echoes*: subject starts with `Accepted:`, `Declined:`, `Tentative:`, or
   `Updated invitation:`. `Invitation:` and `Canceled event:` stay.
7. *Receipts*: subject matches the `receipts` regexes AND the message is the first in its
   thread AND it is dated within 3 days of the job's `applied_at`. Anything receipt-shaped
   arriving later is kept and tagged `receipt?`, because Greenhouse and Lever rejection
   templates reuse "Thank you for your application" subjects from no-reply senders.

Counts per category print in the account summary (`noise: seen 12, own 3, autoreply 1,
alerts 9, echoes 2, receipts 14, collapsed 31`). `--keep-noise` disables cuts 2 to 7 for
debugging a missed email.

**A3.7 Thread collapse, rank, cap.** Thread key = root of `References`, else
`In-Reply-To`, else normalized subject + sender domain + the role title or ATS req id when
the subject carries one, and never across messages more than 7 days apart (so four open
OpenAI rows with identical receipt subjects do not merge). Keep the newest message per
thread after cuts 3 and 4, record `thread_len`. Rank threads per job: domain/slug/alias/
relay-body matches, then human (non-noreply) senders, then hinted, then weak, then by date.
Cap at `--limit-per-job` (default 3 threads) after ranking, so a product notification never
pushes a recruiter reply out of the file. The legend shows the capped count per job.

**A3.8 Snippet.** For every surviving thread's newest message: `BODY.PEEK[]`, prefer
`text/plain`, else strip tags from `text/html`, decode with `errors="replace"`, then clean:
quoted tails (`On ... wrote:`, `>` lines, `De: ... Enviado:` blocks), signatures (from the
first `--`, `Sent from`, `Enviado desde`), unsubscribe and legal footers, tracking URLs
collapsed to their domain, `[EXTERNAL]`-style prefixes, U+2014 to `, `, whitespace. Cap at
`--snippet-chars` (default 800). HTML-only mail that cleans to nothing gets `(no text)`.
`--snippet-chars 0` is headers-only mode.

**A3.9 Hints and lead.** Run the `hints` regexes over subject + cleaned snippet; tag zero or
more of `reject?`, `schedule?`, `assessment?`, `offer?`, `receipt?`, plus `human?` when the
sender is not a no-reply address and nothing else fired. The **lead** is a window of about
140 characters centered on the first hint hit, so the line carries the decision sentence
("...we have decided to move forward with other candidates. We appreciate...") instead of
the greeting. With no hit, the lead is the first 120 characters after skipping the
salutation line and a leading "thank you for" sentence. This is what makes "settle from the
line" true; without it every line needs a `show`.

**A3.10 Finish.** `logout()`. Update `data/mail_state.json`: `swept_at` per account.

The IMAP client is injected (`fetch_account(account, jobs, *, client_factory=...)`), and
`fetch(...)` takes `conn` and `state_path`, so tests use a fake with canned RFC 822 messages,
a `tmp_path` DB and state file, and never open a socket or touch `data/`.

### A4. Output: two files, split on purpose

`data/mail_inbox.json` holds accounts, legend, and per-thread metadata. No snippets:

```json
{
  "generated_at": "2026-09-01T18:02:11Z", "since": "2026-07-04", "open_jobs": 91,
  "accounts": [
    {"label": "apps", "user": "you@example.com", "host": "imap.gmail.com", "folders": ["INBOX", "[Gmail]/Spam"],
     "status": "ok", "candidates": 212, "threads": 27,
     "noise": {"seen": 12, "own": 3, "autoreply": 1, "alerts": 9, "echoes": 2, "receipts": 14, "collapsed": 31}},
    {"label": "personal", "user": "", "host": "imap.gmail.com", "folders": ["INBOX"],
     "status": "skipped: MAIL_PERSONAL_PASS not set", "candidates": 0, "threads": 0, "noise": {}}
  ],
  "legend": [
    {"job_id": 412, "company": "Wizeline", "title": "Senior Full Stack Engineer", "status": "screen",
     "applied_at": "2026-08-20", "threads": 1, "capped": 0}
  ],
  "threads": [
    {"id": 7, "account": "apps", "accounts_seen": ["apps"], "job_ids": [412],
     "match_on": ["domain", "name_subject"], "strength": "strong", "hints": ["schedule?"],
     "thread_id": "CAF+abc@mail.gmail.com", "thread_len": 3,
     "from": "Alejandro Ruiz <alejandro@wizeline.com>", "to": "you@example.com",
     "subject": "Wizeline | We Would Like to Invite you to a Zoom Interview",
     "date": "2026-09-01", "message_id": "CAF+abc@mail.gmail.com",
     "lead": "...I will be in charge of your selection process. I would like to invite you to a Zoom interview; could you share your availability..."}
  ]
}
```

`data/mail_snippets.jsonl` holds one `{"id": 7, "snippet": "..."}` per line. Only `show`
reads it. A stray Read of the manifest file costs a few thousand tokens; the snippet file is
the only place bodies live.

Ids are small integers stable within one run. Cross-account duplicates dedupe on
`message_id`, first account wins, both labels in `accounts_seen`. `message_id` and
`thread_id` are RFC 822 values with angle brackets stripped; this is the form the applier
stores and the exclusion in A3.6 compares.

### A5. CLI and printed output

```
python -m src.mail_fetch [--account LABEL ...] [--since YYYY-MM-DD] [--max-days 120]
                         [--status applied screen interview offer] [--limit-per-job 3]
                         [--snippet-chars 800] [--scan-all] [--full] [--keep-noise]
                         [--page-size 80]
python -m src.mail_fetch manifest [--page N] [--page-size 80]
python -m src.mail_fetch show <id> [<id> ...]        # max 25 ids per call, no --all
```

The default run prints, in order: one summary line per account/folder with the noise
counts; zero or more `tune:` lines; the legend (one line per job with at least one thread:
`412  Wizeline  Senior Full Stack Engineer  screen  applied 2026-08-20  threads 1`); page 1
of the manifest; and a footer `N more lines, run: python -m src.mail_fetch manifest --page
2` when it overflows. No snippet is ever printed unasked.

**`tune:` lines** are how a user learns the yaml knobs exist, at the moment the symptom
appears, with the exact edit. The fetcher never edits the yaml itself (committed config;
silent edits would drift across clones). Three triggers:

```
tune: "Google" matched 41 threads from 9 sender domains, treated as weak this run.
      Make it permanent: add google to weak_names in config/mail_hints.yaml
tune: "Kraken" only ever matched mail from kraken.com notifications you never classified.
      If you are a customer, not a candidate: add kraken.com to ignore_senders in config/mail_hints.yaml
tune: job 3077 (OpenAI, Software Engineer) produced 0 candidates in 3 consecutive sweeps.
      If they wrote from another name or domain: add it under aliases in config/mail_hints.yaml,
      or run with --keep-noise to see what was cut
```

The second fires when every thread a name key ever matched was ignored or left ambiguous
in past batches (from the `seen` list and events). The third needs a per-job sweep counter
in `data/mail_state.json`. All three are one line each and cost nothing when silent.

Manifest line format (about 200 characters, sorted by rank then date, so the tail of a long
manifest is the least valuable):

```
 id  acct  job   date        from                  hints        subject | lead
  7  apps  412   2026-09-01  wizeline.com          schedule?    Wizeline | We Would Like to Invite you to a Zoom Interview | ...invite you to a Zoom interview; could you share your availability...
 12  apps  388   2026-08-29  cosuno.com            reject?      Your application at Cosuno - Senior Full Stack Developer | ...decided to move forward with other candidates whose experience more closely...
 15  apps  401   2026-08-31  hackereval.com        assessment?  You're invited to your coding challenge | ...invited to a coding challenge on HackerEval. You have 7 days to complete...
 19  apps  3077  2026-08-27  Ana Ruiz (gmail.com)  human? weak  Quick question | ...saw your profile and wanted to ask whether you are open to...
```

`from` shows the domain, or the display name plus `(freemail)` for freemail senders. Several
job ids print comma-separated; several hints space-separated; `weak` appears as a flag.
`show` prints, per id: a header line (id, account, job ids, from, date, subject) and the
cleaned snippet.

Page size 80 keeps a page under Claude Code's Bash output cap (about 30k characters) with
the legend included. Exit 0 in every configured-or-not case; exit 1 only on a bad flag or
an unwritable output path.

### A6. Token budget, honest version

Per-line and per-snippet numbers below use 3.4 characters per token, which is what mixed
ids, dates, domains, and prose tokenize at. "Input" is what the orchestrating model reads;
"output" is what it writes, which costs several times more per token and includes its
reasoning.

**Per email that survives to the manifest:**

| path | input | output | total |
|---|---|---|---|
| settled from the line, no proposal (receipt, ack, noise the cuts missed) | 60 | 30 | about 90 |
| settled from the line, proposal written (rejection, invite, touch) | 60 + 40 dry-run line | 80 proposal + 50 reasoning | about 230 |
| needs `show`, then proposal | 60 + 250 snippet + 40 | 80 + 70 | about 500 |
| `offer?` line (always shown, always a proposal) | 350 | 150 | about 500 |

Roughly a third of surviving lines need `show` once leads are hint-centered (mostly `human?`
lines with no hint and weak matches). Blended: **about 250 tokens per surviving email**, of
which about 90 are output tokens. For comparison, the Gmail MCP path reads a whole thread
per email at 2k to 8k input tokens, so this is 10x to 30x cheaper per email, and emails cut
by A3.6 cost zero.

**Fixed per sweep:** skill prompt about 900; four Bash calls (run, show, dry run, apply) at
about 150 framing each; account summary and legend 200 to 1,400 depending on how many jobs
have threads; dry-run header and totals about 100. Call it **2k to 3k**.

**Per sweep:**

| case | surviving lines | model tokens |
|---|---|---|
| steady state (weekly, watermark and seen-list in effect) | 15 to 30 | 6k to 10k |
| first run on this pipeline (91 open rows, 59 days) | about 100 to 130 | 25k to 35k |
| first run narrowed with `--status screen interview offer` first, then `applied` | two runs, same lines total | same total, split across two sessions |

Two consequences the spec commits to: the 5k figure from v1 is withdrawn; and the run prints
`threads` per account so every sweep can be checked against this table. If steady state
lands above 15k, the cuts or the ranking are wrong, not the model.

**Measured 2026-09-01 (Phase D, two Gmail accounts, All Mail + Spam, 91 open rows, mail
back to 2026-07-04):**

| | first run | second run, same day, after `--apply` |
|---|---|---|
| candidates (server-side search hits) | 168 | 107 |
| cut before the model: receipts / ignored / own / echoes / collapsed / seen | 38 / 10 / 6 / 4 / 10 / 0 | 32 / 10 / 4 / 0 / 1 / 32 |
| manifest lines | 53 | 2 |
| printout (summary + legend + manifest), chars | 19.8k (about 5.8k tokens) | 4.6k with 9 tune lines, about 1.3k tokens |
| `show` calls / ids | 1 / 8 (about 1.3k tokens) | 0 |
| proposals written | 53 (about 4k output tokens) | 0 |
| orchestrator total, all-in | about 12k to 13k | about 2k |
| wall clock | 98 s | 75 s |

The first run came in well under the 25k to 35k projection because the receipt cut and
the per-job search removed most of the pile before the model saw a line; the projection
had assumed 100 to 130 surviving lines and reality was 53. The batch moved 21 statuses
(2 to screen, 19 rejected) and 6 touches that the Gmail-MCP sweep had never seen.

### A7. Tests (`tests/test_mail_fetch.py`, hermetic)

- Config: labels, uppercase mapping, space-stripped password, `host:port`, folder list,
  aliases, defaults, blank password reported as skipped, real env overriding `.env`.
- Keys: suffix stripping, slug extraction from Greenhouse/Ashby/Lever URLs, ATS hosts
  yielding no domain, `boards.`/`jobs.` collapse, yaml aliases merged, strength rule on a
  table of real names (Clara weak, OpenAI weak via list, Wizeline strong, Framework Computer
  strong).
- Server-side search: the fake records the SEARCH strings; assert per-job `SINCE`, the
  OR-chain, `X-GM-RAW` on Gmail hosts, `--scan-all` falling back to a horizon-wide header
  pull, and the `swept_at` re-search for a job marked applied after the last sweep.
- Local confirmation: "Clara" candidate from "declaration" discarded; display-name hit;
  subject hit only for freemail/relay senders; per-job window enforced on hits.
- Auto-demotion: a single-token name with candidates from 6 sender domains is `weak` for
  the run and emits the `tune:` line; from 2 domains it stays strong; a yaml entry wins
  either way. The other two `tune:` triggers on a positive and a negative each.
- Capability detection: the fake advertising `X-GM-EXT-1` gets `X-GM-RAW` searches; a
  fake without it gets standard `SEARCH`; the hostname is never consulted.
- Relay pass: greenhouse-mail.io message with the company only in the body is matched; a
  non-relay non-matching message is never body-fetched (assert on the fake's call log).
- Exclusions and cuts, each on a positive and a near-miss: seen thread root, ignored sender,
  own alias, auto-reply, LinkedIn alert vs LinkedIn recruiter message, ATS invite with
  `List-Unsubscribe` survives, `Invitation:` stays while `Accepted:` goes, day-1 receipt cut
  while a day-9 "Thank you for your application" is kept with `receipt?`.
- Collapse: newest kept, `thread_len`, fallback key includes role title and the 7-day gap,
  own reply removed before picking newest.
- Rank and cap: a domain-matched recruiter reply survives a cap of 3 against five product
  notifications; legend shows the capped count.
- Snippet cleaning: multipart prefers plain, html fallback, quoted-printable and base64,
  charset fallback, quoted tail and signature removal (en and es), URL collapse, em-dash
  normalization, `(no text)`, 800 cap.
- Hints and lead: table of subjects and bodies per language; lead centered on the hit; lead
  skips salutation when no hit.
- Output: file split (no `snippet` key in `mail_inbox.json`), ids stable, cross-account
  dedupe, `message_id` and `thread_id` bracket-stripped, manifest paging and footer, `show`
  refuses 26 ids, account error row alongside a working account,
  no-accounts path writes valid files and exits 0.
- Read-only: `select` called with `readonly=True`; every FETCH string contains `PEEK`; the
  fake raises on any `STORE`, `COPY`, `EXPUNGE`, `APPEND`.

---

## Phase B: wiring (skills + applier)

### B1. `/jh-gmail-sync` (`.claude/commands/jh-gmail-sync.md`)

Name unchanged (referenced from hunt, followups, CLAUDE.md, memory). `allowed-tools: Bash,
Write` plus the three Gmail read tools for the fallback only. No Read tool; the skill never
needs it.

1. Run `python -m src.mail_fetch` with Bash. Show me the account summary lines and every
   `tune:` line verbatim (they are the user's only prompt to edit `config/mail_hints.yaml`).
   Say which mailboxes the sweep covered, and say it when that is zero.
2. If at least one account/folder is `status: ok`, the printed legend and manifest are the
   whole input. NEVER run `python -m src.query crm` or `python -m src.query job` in this
   skill (90k and 3.5k tokens respectively on a mature DB; the legend is the job context).
   NEVER `cat`, `Read`, `grep`, `jq`, or `python -c` over anything under `data/mail_`.
   Do NOT search Gmail through MCP tools when an account is ok.
3. If no account is configured and the Gmail MCP tools are available, fall back to the
   current per-application search, capped at 10 threads per application, and take
   `message_id` from the RFC 822 header the message exposes, brackets stripped, so the
   exclusion in A3.6 keeps working. If neither, say so and stop.
4. Work page by page. A manifest over 80 lines prints a footer; finish page 1 (classify,
   `show`, write proposals) before fetching page 2. Never spawn a sub-agent for this step;
   the manifest is sized to be read directly.
5. Classify from the manifest line when the lead itself contains the decision sentence. A
   hint alone is never enough. For every unsettled line, and for every `offer?` line
   regardless, call `python -m src.mail_fetch show <ids>` ONCE with all the ids (25 max per
   call), then classify from the snippets. `weak` lines propose only touches or ambiguous
   unless the text names the role. Signals unchanged: rejection / invite / assessment /
   offer / human reply / receipt / ambiguous. Never propose ghosted, withdrawn, or an offer
   decision.
6. Write `data/gmail_pull.json` in the same schema; `evidence` gains `account` and
   `thread_id`. Evidence stays headers only; snippets are read, never copied.
7. Dry run, wait for my explicit approval, apply. Unchanged.

### B2. `src/gmail_pull.py`

- `_headers()` whitelists `account` and `thread_id` alongside from/subject/date/message_id;
  `_note()` gains `[<account>]` when present.
- `--apply` records the `message_id` and `thread_id` of every proposal the plan accepted
  (changes, touches, ambiguous, ignored; never out-of-scope or otherwise skipped ones) in
  `data/mail_state.json` under `seen`, as `{"signal", "at"}`. State path injectable for
  tests. Entries older than `--max-days` are pruned at the next sweep.
- Seen semantics (fixed in PR #10 review): a seen id silences only that message. It
  silences the rest of its thread only when its signal is terminal (`rejection`).
  Recruiters reply on the receipt thread constantly, so an ignored receipt must never hide
  the interview invite that lands on it. The `email_signal` event payload carries the
  signal for the same reason.
- Everything else stands: forward-only, no ghosted/withdrawn/offer decisions, backlog holds,
  evidence required for rejected/offer. Tests added to `tests/test_gmail_pull.py`.

### B3. `/jh-followups`

Step 1 inherits the change. Step 3 gains: a nudge goes out from the account that received
the thread (`evidence.account` on the latest `email_signal` event; `MAIL_<LABEL>_REPLY_AS`
overrides it for a forwarding target). The Gmail MCP draft tool only reaches the connected
account, so when the account differs, write the draft to `data/followups/<company>-<id>.md`
and tell me which mailbox to paste it into. That file is never handed to any send tool.
Relay reply addresses (Greenhouse `bf-j-...`, Lever, Ashby) make this mandatory.

### B4. `/jh-hunt`

Step 4: "If mail_fetch reports no configured accounts and the Gmail tools are unavailable,
note it and continue"; add the B1 step 2 prohibition on `query crm` / `query job` inside the
inbox pull. Step 2's pile check: make the `python -c` COUNT the only option, since
`query crm` is a 90k-token call on this DB.

---

## Phase C: docs and repo surface

- `docs/mail-setup.md`: per provider. Gmail and Google Workspace: 2-Step Verification, then
  an app password; note the admin can disable IMAP or app passwords. iCloud: app-specific
  password. Fastmail, Zoho, Yahoo: app password pages and IMAP hosts. **Outlook.com,
  Hotmail, Live, and Microsoft 365: Basic Auth for IMAP was removed (consumer in 2024,
  tenants in 2022 to 2023), app passwords do not work for third-party IMAP; use a forwarding
  rule into a supported mailbox** and set `MAIL_<LABEL>_REPLY_AS` so nudges go out from the
  right address. The `.env` block, folder choice (`[Gmail]/Spam` recommended), the
  `mail_hints.yaml` knobs in a **tuning section organized by symptom**, not by key:
  "product notifications show up as weak lines" (weak_names), "a company I know wrote to me
  is missing" (aliases, `--keep-noise`), "mail from a company I am a customer of keeps
  appearing" (ignore_senders), "recruiters write to me in another language" (a new hints
  block), each with a two-line yaml example and the `tune:` line that points at it; and a
  security paragraph: an app password grants full mailbox access even though this tool only
  reads, keep `.env` local, prefer a dedicated applications mailbox, revoke when done.
- `.env.example`: the A1 block, in the file's existing comment style.
- `config/mail_hints.yaml`: shipped with the A1 defaults.
- `CLAUDE.md` Track paragraph: one sentence that the inbox pull is `python -m src.mail_fetch`
  over every account in `.env`, the model reads the printed manifest and `show`, never the
  files, Gmail MCP is the fallback, snippets never leave `data/`.
- `docs/spec-email-report-upskill.md` Phase 2 header: pointer to this spec.
- Memory `two-gmail-accounts`: rewrite once shipped; the blind spot is closed, the
  reply-from-the-right-account rule stays.

---

## Phase D: verification on the real pipeline

1. Configure both real accounts in `.env` with `INBOX,[Gmail]/Spam`, run the fetcher, confirm
   both report `ok`, and confirm the threads seen through Kairos on 2026-09-01 (Caylent
   talent interview, Wizeline Zoom invite, HackerEval challenge, the skill-assessment
   follow-up, Cosuno reply) plus Backblaze on the personal account are in the manifest with
   the right job ids and sensible leads.
2. Record the printed counts (candidates, threads, noise per category, manifest lines) and
   the sweep's actual token use against the A6 table. Adjust the table, not the claim.
3. Run `/jh-gmail-sync` end to end: classification page by page, dry run, apply after
   approval. Confirm `python -m src.query crm` reflects the moves and each
   `email_signal` event carries `account` and `thread_id`.
4. Second run the same day: manifest should be near zero lines (seen list + swept_at).
5. Full suite green: `ruff`, `mypy`, `pytest`.

---

## Decisions taken (flag if you disagree)

- **IMAP with app passwords over the Gmail API**, for portability; OAuth later behind the
  same files if demand appears.
- **Server-side search as the candidate generator, local confirmation after.** Cheaper
  in bandwidth and code, per-job windows for free; it does not change the token bill, the
  manifest does. `--scan-all` kept for weak servers.
- **No UID watermark.** Per-job windows, the seen list, and the `swept_at` re-search cover
  what the watermark did, without its id-format and late-applied failure modes.
- **Two output files.** The manifest file is safe to glance at; the snippet file is bodies.
- **Hints stay, with hint-centered leads.** Cheap in Python, and with the lead window they
  actually reduce `show` calls. A hint never decides; the skill text says so twice.
- **No sub-agent pass.** The reviewer proposed a Haiku relevance pass for large manifests;
  declined. The manifest is paged and ranked so the orchestrator reads it directly, and a
  large first run is a one-time cost.
- **Skill keeps the `jh-gmail-sync` name.**
- **Budget stated as 6k to 10k steady, 25k to 35k first run.** The earlier 5k figure was
  optimistic by about 2x and did not count the fixed costs.

- **Shortlisted rows are not swept** (decided 2026-09-01). This DB has 535 shortlisted rows
  against 91 open applications, most single-word names; sweeping them multiplies search
  volume by six, and the applier discards proposals on rows before `applied` anyway.
  Inbound recruiter contact before an application would need its own transition
  (shortlisted to screen) and belongs to a separate `--inbound` mode if ever wanted.
- **`weak_names` is seeded by the tool, not by reading docs** (decided 2026-09-01). A short
  default list ships; auto-demotion (A2) plus `tune:` lines (A5) surface the right edit
  when the symptom appears; the skill relays those lines; the docs are organized by symptom.
- **The Gmail search branch stays, detected by capability** (decided 2026-09-01). Word-level
  matching cuts candidate counts on the most common provider; correctness never depends on
  it because local confirmation runs on every server.

## Open questions

None at v2. Anything found during Phase A goes here with a date.
