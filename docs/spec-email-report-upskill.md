# Spec: Gmail signal sync, HTML report, upskill analysis

Three features ported (in spirit, not code) from MadsLorentzen/ai-job-search, redesigned to fit
this repo's architecture: SQLite is canonical, deterministic Python computes, the LLM only
classifies and interprets, every status write goes through `db.set_status` / `db.touch_contact`,
and all generated text obeys the zero em-dash and writing-voice rules.

Status: Phase 1 SHIPPED 2026-07-24 (`src/report.py`, stats compute/print split,
`/jh-report`, `tests/test_report.py`; verified on the real DB and rendered in a browser).
Phase 2 SHIPPED 2026-07-24 (`src/gmail_pull.py`, `/jh-gmail-sync`, `/jh-followups`
refactor, `/jh-hunt` inbox-pull + report steps, CLAUDE.md Track paragraph,
`tests/test_gmail_pull.py`). One deviation from 2c/2d as written: a rejection
conflicting with a forward move goes to the ambiguous pile rather than "keep the most
advanced" (email order is not reliable enough to auto-pick a winner).
Phase 3 SHIPPED 2026-07-24 (`src/gaps.py`, `config/skills_lexicon.yaml`, `/jh-upskill`,
`/jh-prep` weak-spots fold-in, `tests/test_gaps.py`; smoke-run on the real DB: 692 jobs
scanned).
Phase 4 SHIPPED 2026-07-24 with phases 2-3 (CLAUDE.md Track + Learn entries, `/jh-hunt`
inbox pull + report steps, `/jh-review` report regeneration + quarterly upskill pointer;
full suite green at every phase).

---

## Design principles (apply to all three)

1. **Skill proposes, script applies.** Same shape as `/jh-notion-sync`: the skill (LLM) gathers
   and classifies, writes a JSON proposal file under `data/`, then a Python module validates and
   applies with a dry-run default. The LLM never writes to the DB directly.
2. **Single write path.** All status changes route through `db.set_status` (events logged,
   folders moved, follow-ups scheduled). No new write paths.
3. **`data/` is the only landing zone for runtime artifacts.** It is already gitignored; nothing
   personal or email-derived gets committed.
4. **Reuse before adding.** The report reuses `src/stats.py` logic; upskill reuses
   `config/profile.yaml` and `match_verdict`; gmail sync reuses the `notion_pull` validation
   pattern (never downgrade, never touch `backlog` holds).
5. **Counts next to every rate.** Same honesty rule as `/jh-review`: n=4 is an anecdote.

---

## Phase 1: HTML report (`python -m src.report` + thin `/jh-report` skill)

The offline dashboard. Fully deterministic, zero LLM tokens, re-runnable any time.

### 1a. Refactor `src/stats.py` into compute + print layers

Current functions compute and `print()` in one body. Split each into a data function returning
plain dicts/lists and a printer consuming it:

- `funnel_data(conn) -> dict` (totals, by_stage, responded, segments by band/family/source)
- `calibration_data(conn) -> dict`
- `latency_data(conn) -> dict` (n, median, min, max, plus the raw day values for a histogram)
- `comp_data(conn, min_score) -> dict`
- `drops` stays print-only (it is an audit sample, not a chart)

CLI output must not change: existing printers call the new data functions. This is the only
refactor in the whole spec; everything else is additive.

### 1b. `src/report.py`

`python -m src.report [--out data/report.html] [--open]`

Sections, all computed from the DB via the 1a data functions plus a few direct queries:

1. **Stat cards**: open pipeline count (non-terminal), applications, response rate,
   median applied-to-response days, interviews reached, offers.
2. **Funnel**: applied -> responded -> screen -> interview -> offer, horizontal bars.
3. **Response rate by score band, title family, and source**: grouped bars with n labels.
   This is the calibration story in visual form.
4. **Status distribution** of the whole DB (discovered through terminal), so triage and
   discovery volume are visible.
5. **Comp table**: the `comp_data` segments, with the existing monthly-vs-annual caveat
   printed verbatim.
6. **Follow-ups due**: rows where `next_followup_at <= today`, soonest first.
7. **Applications table**: one row per application (company, title, source, score, status,
   applied_at, last_contact_at, next follow-up, days since applied), client-side sort and a
   status/family/source filter in plain vanilla JS.
8. **Source health**: from the `runs` table (already written by discover for exactly this
   purpose), per source: last run, pulled/new over the last 5 runs, and a "possibly dead"
   flag when recent runs all pulled 0 or failed. Today a dead source is invisible.

Constraints:

- Single self-contained file: inline CSS, inline SVG charts, inline JS. Zero external
  requests (no CDN, no fonts, no images). Works from `file://` offline.
- Light and dark via `prefers-color-scheme`.
- Zero em-dashes anywhere in the generated HTML.
- Default output `data/report.html` (gitignored by the existing `data/` rule).
- `--open` runs `open` on the file (macOS).
- At implementation time, load the `dataviz` skill before writing chart code (palette,
  axis, and legend rules).

### 1c. `/jh-report` skill (thin)

`.claude/commands/jh-report.md`: run the script with Bash, `--open` it, then relay the stat-card
headline numbers as text. No LLM-authored analysis inside the HTML; interpretation stays in
`/jh-review`, which gains one line telling it the report exists.

### 1d. Tests (`tests/test_report.py` + additions to existing stats tests)

- Seed a tmp DB (reuse the fixture style of `test_intelligence.py`), assert the HTML contains
  the expected counts and section anchors.
- Assert no external references: regex for `http` in `src=`/`href=` attributes, allow `file://`
  and anchors only.
- Assert zero U+2014 in output.
- Assert `stats` CLI output unchanged after the refactor (golden-ish string checks on a seeded DB).

### Acceptance

`python -m src.report --open` on the real DB renders a correct dashboard offline; all tests pass;
`python -m src.stats funnel` output is byte-identical to before the refactor.

---

## Phase 2: Gmail signal sync (`/jh-gmail-sync` + `src/gmail_pull.py`)

Reads Gmail (via the claude.ai Gmail connector, read-only) for status signals on open
applications, proposes changes as a batch with the source email cited, and applies only after
human approval, through the same validation gauntlet as `notion_pull`.

### 2a. Scope of "open application"

Jobs with `status IN ('applied','screen','interview')`, plus `offer` (for follow-up traffic).
Terminal, backlog, and pre-application statuses are never searched.

### 2b. The skill: `.claude/commands/jh-gmail-sync.md`

`allowed-tools`: Bash, Write, and ONLY the read-side Gmail tools (`search_threads`,
`get_thread`, `get_message`). No label/draft tools: this skill never modifies the mailbox and
never sends anything.

Flow:

1. `python -m src.query crm` (Bash) to get open applications with id, company, applied_at,
   last_contact_at, url.
2. Per application, search Gmail: company name as a quoted phrase plus, when the job `url`
   yields a company domain, `from:(@domain)`. Window: `after:` the later of `applied_at` and
   `last_contact_at`, minus 2 days of slack. Cap at 10 threads per application.
3. Classify each hit into exactly one signal (taxonomy in 2c) or `ambiguous`.
4. Write `data/gmail_pull.json`: a list of
   `{job_id, signal, proposed_status|null, contact_date, evidence: {from, subject, date, message_id}}`.
   Evidence carries headers only, never body text (bodies stay in Gmail; `data/` is gitignored
   but the DB event log is long-lived and email bodies do not belong in it).
5. Run `python -m src.gmail_pull data/gmail_pull.json` (dry run), show the proposed batch to
   Santiago with one line per change (`#id company: applied -> screen, per "subject" from x@y
   on date`), plus the ambiguous pile.
6. Only after explicit approval, re-run with `--apply`. Report what changed.

### 2c. Signal taxonomy and mapping

| Signal | Proposed action |
|---|---|
| rejection | status -> `rejected` |
| interview invite / scheduling link | advance one stage: `applied` -> `screen`, `screen` -> `interview`; already `interview` -> contact touch only |
| assessment / take-home link | status -> `screen` (if currently `applied`), else touch |
| offer letter / verbal-offer recap | status -> `offer` |
| human reply, no stage change (recruiter ack, "we'll get back to you") | `touch_contact` with the email date, no status change |
| automated application receipt | ignore (not even a touch; it says nothing about a human) |
| anything unclear, or a signal conflicting with current status | `ambiguous`: listed for manual handling, never guessed |

Never proposed by this tool, ever: `ghosted`, `withdrawn`, `backlog`, or accepting/declining an
offer. Those are human judgments; the funnel's silence bucket must stay human-curated.

### 2d. The applier: `src/gmail_pull.py`

Modeled line-for-line on the `notion_pull` contract:

- Dry run by default, `--apply` to write, per-change diff output either way.
- Validation: job_id must exist and be in scope (2a); proposed status must be a forward move in
  the stage order `applied < screen < interview < offer` (rejected allowed from any open stage);
  never downgrade; never touch `backlog`; reject duplicate proposals for one job (keep the most
  advanced, note the rest).
- Writes go through `db.set_status` (which logs the `status_change` event; pass
  `note="email: <subject> (<from>, <date>)"`) and `db.touch_contact` for touches. Additionally
  `log_event(kind='email_signal', payload=evidence-headers)` for every applied change so
  `/jh-review` can later measure how much of the funnel Gmail caught.
- A `rejected` or `offer` proposal is applied only when evidence includes subject AND sender.

### 2e. Pipeline wiring

- `/jh-hunt`: new step between Match and Sync + star, "Inbox pull": run the gmail-sync flow
  (dry run, present the proposed batch inline, apply on approval, skip cleanly if the Gmail
  connector is absent). Rationale: the hunt already pulls Notion edits before starring for
  exactly this reason; email is the earlier, more authoritative source of the same truth. A
  company that rejected or advanced by email this week must be reflected before the top 5 are
  starred and tailored.
- `/jh-followups`: REFACTOR, not just a pointer. It already carries Gmail read tools and does
  its own inline reply-checking (its steps 2-3), applying `set-status` directly with none of
  the never-downgrade validation. Two independent email-classification paths with different
  rules is how statuses drift. Its steps 2-3 become "run the /jh-gmail-sync flow first"; the
  skill keeps what is uniquely its own: deciding who deserves a nudge, drafting it
  (`create_draft` stays HERE, gmail-sync stays read-only), `touch --bump` after drafting, and
  the 3-week ghosted closeout.
- `/jh-notion-sync`: unchanged (its phase 1 pull already reconciles; gmail sync runs before it,
  inside `/jh-hunt` or when both are used in one sitting).
- CLAUDE.md: one paragraph under Track/Learn describing the skill and the read-only guarantee.

### 2f. Tests (`tests/test_gmail_pull.py`)

Fixture-driven, no network: JSON proposals against a seeded DB. Cases: forward move applied;
downgrade blocked; backlog untouched; unknown job id rejected; contact-only touch sets
`last_contact_at` and logs the event; terminal proposal without full evidence rejected;
dry run writes nothing; duplicate proposals collapsed.

### Risks and mitigations

- **Company-name false positives** (e.g. a company named "Landing"): domain-scoped `from:` is
  the primary query when a domain is derivable; bare-name matches classify conservatively and
  fall to `ambiguous` unless the thread clearly references the role.
- **Connector absence in headless runs**: the skill degrades to a clear "Gmail connector not
  available" message; nothing else in the pipeline depends on it.
- **Privacy**: headers only in JSON and events; `data/` gitignored; skill has no write access
  to Gmail.

### Acceptance

A dry run on the real mailbox proposes a sensible batch with zero false status changes after
human review; `--apply` moves statuses through `set_status` with events logged; all fixture
tests pass.

---

## Phase 3: Upskill analysis (`/jh-upskill [job_id]` + `python -m src.gaps`)

Gap analysis between the profile and the market actually being applied to, with one twist the
source repo does not have: the first question is always "is this a real skill gap, or a
profile-vocabulary gap?" (a skill Santiago has that `profile.yaml` does not list). Vocabulary
gaps become proposed `profile.yaml` diffs, mirroring `/jh-review`; only real gaps get a
learning plan.

### 3a. Deterministic extractor: `src/gaps.py`

`python -m src.gaps [--min-score 70] [--job <id>] [--json]`

- **Fleet mode** (default): over `canonical_jobs` with `match_score >= min-score` OR status in
  (`shortlisted`,`applied`,`screen`,`interview`,`offer`), scan descriptions for tech-term
  hits against a curated lexicon file (`config/skills_lexicon.yaml`: term, aliases, category).
  Subtract everything in `profile.yaml` `must_have_skills` + `nice_to_have_skills`
  (case-insensitive, alias-aware). Output ranked rows: term, jobs mentioning it, example job
  ids, and (when those jobs were applied to) the responded rate of jobs carrying the term.
- **Per-job mode** (`--job <id>`): the same subtraction against one description; feeds the
  interview-prep use case ("what will they grill me on that I have not got").
- **`missing_skills` aggregation, the primary signal**: the job-matcher already emits
  `missing_skills: [...]` and `reasons` in every `match_verdict` (verified against
  `.claude/agents/job-matcher.md`; the field is `missing_skills`, there is no `gaps` field).
  Fleet mode aggregates `missing_skills` across the selected jobs into the same ranked
  output (term, count, example ids, responded rate). This is an LLM-judged gap list and
  beats raw lexicon counting; the lexicon scan complements it by covering unscored
  descriptions and terms the matcher did not single out.
- `--json` for the skill to consume; human-readable table otherwise.

The lexicon starts small (~80 terms: languages, frameworks, infra, AI stack, data) and grows by
hand; a term the lexicon lacks is simply not counted, and the skill's LLM pass covers novel
terms qualitatively.

### 3b. The skill: `.claude/commands/jh-upskill.md`

`allowed-tools`: Read, Write, Bash, WebSearch, WebFetch.

Flow (fleet mode):

1. `python -m src.gaps --json` (Bash).
2. Read `config/profile.yaml` AND `resume/master_resume.yaml`. Classify each top gap term:
   - **vocabulary gap**: evidence exists in the master resume -> propose a `profile.yaml`
     addition as a diff (never self-applied, same contract as `/jh-review`).
   - **real gap**: no defensible evidence -> candidate for the learning plan.
   - **noise**: lexicon hit irrelevant to the four title families -> discard with one line.
3. For the top 5 real gaps: WebSearch 2-3 current, free-first resources each (docs, courses,
   projects), with an hours estimate and a "provable by" milestone (a repo, a cert, a demo),
   because a gap is only closed when it is interview-defensible.
4. Write `research/upskill/<YYYY-MM>-plan.md` (committed, like company dossiers): gap table
   with counts, the vocabulary-gap diffs, the learning plan, sources cited. Voice rules and
   zero em-dashes apply.
5. Report a one-screen summary.

Per-job mode (`/jh-upskill <id>`): same but scoped to one posting. Output lands at
`applications/<bucket>/<company>-<id>/upskill.md` (next to the prep briefs, gitignored with
the rest of `applications/*/`). `/jh-prep` step 3 ("Weak spots", which already reads
`match_verdict`) gains: "if `upskill.md` exists in the application folder, fold its real-gap
list into the weak spots with the prepared honest response for each."

Hard rule carried over from CLAUDE.md: the learning plan NEVER feeds resume or answer-bank
content. A skill enters `master_resume.yaml` only after it is actually learned and provable,
by hand, by Santiago.

### 3c. Tests (`tests/test_gaps.py`)

Seeded DB + tiny fixture lexicon: known description produces expected ranked terms; profile
subtraction removes listed skills and aliases; `--job` mode scopes to one row; `--json` shape
is stable; jobs below the score floor and irrelevant/expired rows are excluded.

### Acceptance

`python -m src.gaps` on the real DB produces a plausible ranked table in under a second;
the skill produces a plan whose every vocabulary-gap claim cites a master-resume line; tests pass.

---

## Phase 4: Integration, docs, and review-loop closure

Small, mostly text. Full skill-edit inventory (every existing skill and agent was audited):

| Skill / agent | Change |
|---|---|
| `/jh-hunt` | Inbox pull step + report regeneration (item 3 below) |
| `/jh-followups` | Refactored: email classification delegated to gmail-sync (see 2e); keeps nudge drafting, bumps, ghosted closeout |
| `/jh-review` | Report regeneration in step 1; quarterly upskill pointer (item 2 below) |
| `/jh-prep` | Step 3 reads `upskill.md` from the application folder when present (see 3b) |
| `/jh-notion-sync` | Unchanged; gmail sync simply runs before it |
| `/jh-debrief` | Unchanged; it is the human-driven status path, gmail-sync's ambiguous pile refers to it |
| `/jh-discover`, `/jh-match`, `/jh-triage`, `/jh-research`, `/jh-tailor` | Unchanged; upskill output is deliberately kept OUT of tailoring (never-fabricate rule) |
| `job-matcher`, `company-researcher`, `resume-tailor` agents | Unchanged; upskill consumes `missing_skills` as-is |

1. CLAUDE.md: add the three commands to the pipeline section (report under Track, gmail-sync
   under Track, upskill under Learn), one line each.
2. `/jh-review` step 1 gains `python -m src.report` regeneration and, quarterly, a pointer to
   the latest upskill plan ("did the market gaps shift?").
3. `/jh-hunt` gains two steps (both cheap, neither changes the loop's guardrails):
   - **Inbox pull** between Match and Sync + star (see 2e): dry-run gmail sync, approve the
     batch, apply, so starring and tailoring run against email-fresh statuses. Skips cleanly
     when the connector is unavailable; the hunt never blocks on it.
   - **Report regeneration** in the final step: run `python -m src.report` and include the
     dashboard path plus the headline stat cards in the hunt's closing report. Deterministic
     and token-free, so there is no reason a hunt should end with a stale dashboard.
   Upskill deliberately stays OUT of `/jh-hunt`: it is a monthly reflection over the whole
   market, not a per-run step, and its WebSearch cost would slow every hunt for no per-run
   benefit. Its cadence hook lives in `/jh-review` (item 2).
4. `docs/` cross-links: this spec gets a "shipped" status note per phase as they land.
5. Full test suite green; `python -m src.reconcile` untouched by any of this (no new folder
   conventions were introduced).

---

## Sequencing and effort

| Phase | Depends on | Rough size | Why this order |
|---|---|---|---|
| 1 report | nothing | ~400 lines Python + HTML template, 1 test file | Pure, offline, zero risk; the stats refactor it forces benefits everything later |
| 2 gmail sync | phase 1's refactor not required, but ships after so the report can show email-caught events | ~250 lines Python + 1 skill, 1 test file | Highest ongoing value; needs the most careful validation, so it gets a proven pattern (notion_pull) to lean on |
| 3 upskill | nothing hard; reads match_verdict quality that improves as the pipeline runs | ~200 lines Python + 1 lexicon + 1 skill, 1 test file | Useful but not time-sensitive; benefits from more scored jobs in the DB |
| 4 integration | 1-3 | text only | Closure |

## Explicitly out of scope

- Sending or drafting any email (follow-up drafting already lives in `/jh-followups`).
- Writing anything to Gmail (labels included).
- Auto-applying status changes without the human approving the batch.
- A web-served dashboard (the report is a static file; `src/crm/viewer.py` remains the
  interactive UI).
- Salary benchmarking beyond the existing `stats comp` (the source repo's Danish salary tool
  has no free MX/LATAM equivalent worth wiring in).

## Defaults chosen (flag now if wrong)

1. Report lands at `data/report.html`, gitignored. Alternative: a committed `reports/` dir.
2. Gmail evidence stored as headers only (from, subject, date, message_id), never body text.
3. Upskill plans are committed under `research/upskill/`, like company dossiers.
4. The stage order for the never-downgrade rule is `applied < screen < interview < offer`,
   with `rejected` reachable from any open stage.
5. New config file `config/skills_lexicon.yaml` rather than growing `profile.yaml`.
