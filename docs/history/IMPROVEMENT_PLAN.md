# jobhunt Improvement Plan

> The author's record, kept for the numbers.

Full backlog from the July 2026 project review, organized into implementable phases.
Each item states WHAT to do, WHY it matters, and HOW to do it (files, acceptance criteria).
Phases are ordered by leverage: fix the broken funnel first, then the automated loop,
then data quality, then foundations, then the intelligence layer.

Status legend: `[ ]` todo, `[~]` in progress, `[x]` done.

---

## Findings snapshot (evidence the plan is built on)

Measured against `data/jobs.db` and the working tree on 2026-07-16:

- 12,238 jobs discovered in 10 days across 17 sources. Discovery is healthy.
- 37 folders in `applications/applied/` but only 2 rows with `status='applied'`.
  27 of those folder IDs are still `shortlisted` in the DB.
- 0 rows have ever had `next_followup_at` set. `last_contact_at` has zero writers.
- 1,106 duplicate company+title groups (Careerjet stores one Corning role 21 times).
- DB is 72MB, almost all of it full descriptions, including 4,056 `irrelevant` rows
  that will never be read again. No expiry: `last_seen` is written, never read.
- `research/companies/99minutos.md` and `99minutos-com.md` are byte-identical
  (slug drift between `/jh-research <name>` and `<id>` entry points).
- `/jh-hunt` uses `match export --limit 40` (keyword prescore), bypassing the
  triage/bucket system entirely.
- The 08:00 digest email runs before any scoring happens, so it never contains
  the jobs it just discovered.
- No tests, no linter config, unpinned requirements, no schema migration path.

---

## Phase 0: Quick hygiene (half a day)

Cheap, zero-risk cleanups. Do these first, in one commit.

- [x] **0.1 Remove junk from repo root.**
  Delete `scratchpad_chunk004.txt`, remove `.DS_Store`, add both patterns to `.gitignore`.

- [x] **0.2 De-dupe the 99minutos dossiers.**
  Keep `research/companies/99minutos.md`, delete `99minutos-com.md`.
  (Root-cause fix for slug drift is 3.6; this just removes the existing dupe.)

- [x] **0.3 Backfill drifted statuses.**
  One-off script (or manual SQL) that flips the 27 jobs whose folders live in
  `applications/applied/` but whose DB status is still `shortlisted` to `applied`,
  setting `applied_at` from the folder's mtime as a best guess.
  Acceptance: `SELECT COUNT(*) FROM jobs WHERE status='applied'` matches reality.

- [x] **0.4 Pin requirements.**
  `pip freeze` the working versions into `requirements.txt` (or split into
  `requirements.in` + pinned `requirements.txt`).

---

## Phase 1: Tracking-layer integrity (1-2 days)

The CRM is currently fiction: statuses drift, follow-ups never fire. This phase
makes state transitions cheap and automatic so the data stays honest.

- [x] **1.1 `set-status` CLI helper.**
  WHAT: `python -m src.query set-status <id> <status> [--note "..."]`.
  WHY: today the ONLY status write path is the Flask viewer UI. Agents and
  commands (`/jh-followups` says "close out ghosted roles") have no way to act.
  HOW: add subcommand in `src/query.py`; validate against `db.STATUSES`;
  when flipping to `applied`, stamp `applied_at` and auto-set
  `next_followup_at = applied_at + followup_days` (see 1.3).

- [x] **1.2 `reconcile` script: folders <-> DB, both directions.**
  WHAT: `python -m src.reconcile` (or `scripts/reconcile.py`) that:
  - folder in `applications/applied/` + DB status earlier than `applied` -> flip DB.
  - DB status `rejected|ghosted|withdrawn` + folder still in `applied|pending` -> move to `other/`.
  - Prints a diff first; `--apply` to execute.
  WHY: filing is manual per CLAUDE.md, so drift is structural. This makes drift
  self-healing instead of forbidden.
  HOW: parse the trailing `-<id>` from folder names; folders without a numeric id
  (e.g. `backblaze-ai-enablement-director`) are reported as unmatched for manual mapping.
  Wire it into `/jh-notion-sync` and `/jh-hunt` as a first step so it runs routinely.

- [x] **1.3 Auto follow-up dates.**
  WHAT: whenever status becomes `applied`, set `next_followup_at = applied_at + N days`
  (default 7, config key `followup_days` in `config/notify.yaml`).
  After a follow-up is sent, `/jh-followups` bumps it another N days.
  WHY: `next_followup_at` has NEVER been set on any row; `/jh-followups` has never
  had anything to find.
  HOW: implement in the `set-status` helper (1.1) and in the viewer's update route
  (`src/crm/viewer.py`), so both write paths behave identically.

- [x] **1.4 Make `last_contact_at` real (or kill it).**
  WHAT: `/jh-followups` writes `last_contact_at` when it finds a reply in Gmail or
  drafts a nudge; expose via `python -m src.query touch <id> [--date ...]`.
  WHY: the column is read by the followups query but written by nothing, so the
  agent re-derives contact state from Gmail on every run and can re-nudge someone
  who already replied.
  HOW: extend `.claude/commands/jh-followups.md` to call the helper after inspecting
  threads; grant it the Bash permission for `python -m src.query`.

- [x] **1.5 Record submissions from the CLI flow.**
  WHAT: document + support the transition "human submitted the application":
  `python -m src.query set-status <id> applied` also moves the folder
  `pending/ -> applied/`.
  WHY: today that transition exists only in the viewer UI; the hunt/tailor flow
  gives you a pending folder and then loses track.
  Acceptance for the phase: `/jh-followups` returns a non-empty, correct due list;
  folder locations and DB statuses agree for every application.

---

## Phase 2: Fix the automated daily loop (1-2 days)

The scheduled path exists but is mis-ordered and skips the smart parts.

- [x] **2.1 `/jh-hunt` must use triage + bucket-ordered scoring.**
  WHAT: insert a triage step when the unscored discovered pile is large
  (threshold ~200), then score with `export --min-bucket 3 --chunk 60 --limit 0`
  fan-out instead of the current `export --limit 40`.
  WHY: the bare `--limit 40` keyword prescore is exactly the trap
  `docs/scaling-scoring.md` documents; the flagship command re-introduces it.
  HOW: edit `.claude/commands/jh-hunt.md`; make the triage step conditional on
  `SELECT COUNT(*) FROM jobs WHERE status='discovered' AND match_score IS NULL`.

- [x] **2.2 Honest daily digest.**
  WHAT: either (a) schedule a headless triage+match pass before `notify` in
  `run.sh`, or (b) relabel the digest "scored since last run" and add a second
  section "discovered today, not yet scored: N".
  WHY: the 08:00 email currently advertises freshness it does not have; today's
  discoveries are invisible until a human scores them.
  HOW: (b) is a small `src/notify.py` change and honest immediately; (a) is the
  real fix once headless scoring is trusted. Do (b) now, (a) after 2.3.

- [x] **2.3 Scheduled read-only AI pass.**
  WHAT: a scheduled headless Claude run (launchd on macOS, mirroring
  `mac/install-schedule.sh`) that executes triage + match + notion-sync +
  followups-draft. Nothing in this set submits anything.
  WHY: "human on the submit button" only requires a human at the apply step;
  scoring and sync are the stages that back up on busy days.
  HOW: `claude -p "/jh-triage then /jh-match then /jh-notion-sync"` style runner
  script with a lockfile so it never overlaps the interactive session; log to
  `data/logs/`. Keep tailor/apply strictly manual.
  DONE 2026-07-16: `scripts/ai_pass.sh` (discover -> headless claude triage+match ->
  digest, guard + lockfile, logs in data/logs/). MCP-dependent stages (notion-sync,
  followups) stay interactive: claude.ai connectors are not available headless.
  Install with `./mac/install-schedule.sh --ai` (mutually exclusive with the plain
  daily job so discover never runs twice). NOT auto-installed; run it when ready.

- [x] **2.4 Source health monitoring.**
  WHAT: a `runs` table (`source, ts, fetched, inserted, ok, error`) written by
  `src/discover.py` per source per run; digest flags any enabled source with 0
  fetched for 3+ consecutive runs.
  WHY: adapter failures are currently a `print` and gone; a dead source is
  indistinguishable from a quiet one for weeks.
  HOW: small schema addition (needs migrations, 5.4, or `CREATE TABLE IF NOT
  EXISTS` for now); render a "source health" line in `notify.py`.

- [x] **2.5 One starring rule for Notion.**
  WHAT: unify `/jh-notion-sync` (stars top 10 by match) and `/jh-hunt` (stars
  exactly 5 shortlisted). Pick: star = "top 5 shortlisted by match score", shared.
  WHY: the star is the phone action queue; it currently flip-flops by entry point.
  HOW: edit both command files to reference the same rule text.
  DONE 2026-07-16: sync now stars top 5 shortlisted, same as hunt.

- [x] **2.6 Two-way Notion sync (pull before push).** (added 2026-07-16, shipped same day)
  WHAT: Notion is where statuses get updated from the phone; those edits now flow
  back. `src/notion_pull.py` takes a JSON export of the Notion rows and applies a
  conservative diff: URL-first matching (tracking params stripped, identifying
  params kept), `declined`/`Not Found` -> `withdrawn`, no pipeline downgrades,
  `backlog` holds preserved, explicit follow-up dates survive terminal statuses
  (reapply reminders). `/jh-notion-sync` is now pull-then-push.
  Initial pull applied 35 changes (real statuses: 32 applied, 2 screen, 4 rejected,
  9 withdrawn) and all 10 unlinked application folders were renamed to carry their
  DB ids.

---

## Phase 3: Data quality (2-3 days)

- [x] **3.1 Deterministic cross-source dedup.**
  WHAT: replace bare `GROUP BY canonical_key` in `src/match.py:67`,
  `src/triage.py:47`, `src/notify.py` with a deterministic representative:
  prefer ATS sources (greenhouse/lever/ashby/recruitee/workable) over
  aggregators, tie-break `MIN(id)`.
  WHY: SQLite returns an arbitrary row per group, so WHICH duplicate's
  description gets scored is undefined and can change between runs; the row
  judged may not be the row shown.
  HOW: a `rank` CASE expression or a `canonical_jobs` SQL view all consumers use.

- [x] **3.2 Job expiry.**
  WHAT: nightly pass (in `src/discover.py` post-run): jobs with
  `last_seen < now - 14 days` and status in (`discovered`) get `status='expired'`
  (new terminal status). Never expire anything shortlisted or later.
  WHY: closed postings live forever as `discovered`, polluting triage/match and
  the pile counts.
  HOW: add `expired` to `db.STATUSES`; exclude it everywhere `irrelevant` is
  excluded; add to Notion select mapping (4.1).

- [x] **3.3 Description pruning (the 72MB fix).**
  WHAT: null out `description` on rows that are `irrelevant` or `expired` for
  30+ days; then `VACUUM`.
  WHY: descriptions are ~56MB of the 72MB file; 4,056 irrelevant rows keep full
  text forever for no reader.
  HOW: same nightly pass as 3.2. Keep company/title/url/scores for audit.

- [x] **3.4 HTTP layer hardening.**
  WHAT: in `src/adapters/__init__.py`:
  - retry only on 429/5xx/timeouts (catch `requests.RequestException`, not `Exception`);
    fail fast on other 4xx.
  - give `get_text()` the same retry wrapper as `get_json` (it is SoftServe's only path).
  - per-host minimum delay (simple `time.monotonic` throttle keyed by netloc in the
    shared session); cap SoftServe's ThreadPoolExecutor politeness accordingly.
  WHY: today a 404 retries 3x with backoff for nothing, one blip kills a SoftServe
  run, and sitemap fan-out can hammer one host.

- [x] **3.5 Adapter shared helpers.**
  WHAT: extract into `src/adapters/__init__.py` (or `src/adapters/base.py`):
  `paginate(fetch_page, max_pages)`, `int_or_none(x)`, `remote_from_text(*parts)`,
  `require_id(obj, *keys)` (raises instead of producing external_id `"None"`).
  Migrate adapters opportunistically; new adapters must use them.
  WHY: the same pagination/skip/coercion logic is copy-pasted across ~24 files;
  `str(j.get("id"))` currently creates bogus `"None"` unique rows.

- [x] **3.6 Research slug normalization + freshness.**
  WHAT: in `src/research.py`:
  - `company_slug`: strip trailing domain tokens (`com|io|ai|co|net`) and corporate
    suffixes (`inc|llc|ltd|sa|de|cv`), collapse repeats; keep an alias map
    (`research/aliases.yaml`) for manual overrides.
  - `research get/path` returns `stale: true|false` parsed from the dossier's
    `researched:` line (fallback file mtime), TTL configurable (default 30 days).
  WHY: byte-identical duplicate dossiers waste full Sonnet research runs, and
  "looks fresh" is currently eyeballed non-determinism.
  HOW: update `jh-research.md`, `jh-hunt.md`, `jh-tailor.md` to branch on `stale`.

- [x] **3.7 Normalize `posted_at`.**
  WHAT: coerce every adapter's date to ISO-8601 UTC in `Job.to_row` (one place),
  parsing the handful of formats sources emit.
  WHY: mixed formats in one TEXT column make date filtering/sorting unreliable.

---

## Phase 4: Config and docs consistency (1 day)

- [x] **4.1 Single-source the status vocabulary.**
  WHAT: `db.STATUSES` is the only authority. Fix: `jh-hunt.md` and `CLAUDE.md`
  say `declined` (not a real status; the enum has `withdrawn`); the Notion select
  in `jh-notion-sync.md` is missing `ghosted`/`withdrawn`/`expired`.
  WHY: the phone CRM literally cannot represent a ghosted job today.

- [x] **4.2 One location matrix, in `profile.yaml` only.**
  WHAT: authoritative rule: remote anywhere / US on-site or hybrid (TN eligible)
  / Mexico City on-site / LATAM = OK; on-site outside US+MX = dealbreaker.
  Fix the current `profile.yaml` dealbreaker text ("on-site or hybrid outside
  Mexico City") which contradicts this, and make `job-matcher.md` cite the
  profile verbatim instead of paraphrasing.
  WHY: the same job legitimately scores 25 or 80 depending on which doc the
  agent anchors to.

- [x] **4.3 One shortlist threshold.**
  WHAT: a single config key (e.g. `profile.yaml: shortlist_threshold: 70`);
  `notify.yaml min_score`, `job-matcher.md`, `jh-triage.md` all read/cite it.
  WHY: the two 70s are coincidentally equal and independently maintained.

- [x] **4.4 README regeneration.**
  WHAT: fix stale unprefixed command names (`/match` -> `/jh-match` etc., also in
  `run.sh` epilogue), add Triage and Research rows to the pipeline table, list all
  three agents, list `triage.py`/`research.py`/`render_docx.py` in the layout.
  Drop or implement the promised "assisted form-fill / Playwright" row (see 6.4).
  WHY: copy-pasting any README command fails today; second-machine setup is the
  README's own stated use case.

- [x] **4.5 Clarify bucket vs score in `job-matcher.md`.**
  One line: "the triage bucket affects coverage ORDER only; it is not a scoring input."

---

## Phase 5: Engineering foundation (2-3 days, parallelizable with 3-4)

- [x] **5.1 Tests.**
  WHAT: `tests/` + pytest. Priority order:
  1. `models.canonical_key` / `normalize_text` (dedup correctness),
  2. `db.upsert_job` (insert vs refresh, uniqueness),
  3. per-adapter `fetch()` against recorded JSON/HTML fixtures (no network),
  4. `query.set-status` transitions + follow-up stamping (Phase 1 logic),
  5. slug normalization (3.6).
  WHY: 27 adapters and all dedup/render logic are currently untested; every
  refactor in Phase 3 is risky without this.

- [x] **5.2 Lint + types.**
  WHAT: `pyproject.toml` with ruff (the code already carries `# noqa: BLE001`
  expecting it) and mypy (codebase is already fully annotated).

- [x] **5.3 CI.**
  WHAT: `.github/workflows/ci.yml`: ruff + mypy + pytest on push/PR.

- [x] **5.4 Schema migrations.**
  WHAT: `PRAGMA user_version`-based runner in `src/db.py` (numbered migration
  list applied on connect).
  WHY: Phases 2-3 and 6 all add columns/tables; `CREATE TABLE IF NOT EXISTS`
  cannot alter an existing table.
  NOTE: do this BEFORE 2.4, 3.2, and 6.x schema changes; sequence it early.

- [x] **5.5 Viewer hardening (small).**
  WHAT: validate `status` against `db.STATUSES` and validate the follow-up date
  format in `src/crm/viewer.py` update route; escape quotes in `notify._esc`.

---

## Phase 6: Intelligence layer (the new capabilities)

This is where the system starts learning instead of just filtering. Order within
the phase follows the data dependency: capture events first, then the loops that
consume them.

- [x] **6.1 Event log + outcome capture.**
  WHAT: an `events` table: `(id, job_id, ts, kind, payload)` with kinds like
  `status_change`, `followup_sent`, `reply_received`, `interview_scheduled`,
  `debrief`. Every status transition (1.1) writes an event automatically.
  WHY: `status` alone loses history (you cannot compute "days from applied to
  first reply" from a single column). Every loop below reads this table.
  HOW: needs migrations (5.4). Backfill what's derivable from `applied_at`.

- [x] **6.2 Interview transcripts + `/jh-debrief <id>` (user-requested).**
  WHAT: record interviews, drop the transcript in
  `interviews/<company>-<id>/<date>-<round>.md` (e.g. `2026-07-20-screen.md`),
  then run `/jh-debrief <id>`. The command:
  1. Reads the transcript + the job row + the tailored materials + the dossier.
  2. Extracts: every question asked, how the answer landed (strong / weak /
     rambled), factual commitments made ("I said I could start in August"),
     interviewer signals, red flags, comp/process info revealed.
  3. Writes `interviews/<company>-<id>/debrief-<date>.md` with a
     prep-for-next-round section (weak answers to rehearse, questions to ask).
  4. Updates the answer bank (6.5): new questions encountered, improved phrasings
     of answers that landed well. NEVER invents experience; improved answers must
     still be grounded in `resume/master_resume.yaml`.
  5. Logs an `events` row (`kind='debrief'`) and updates
     `last_contact_at` / `next_followup_at`.
  PRIVACY / GUARDRAILS:
  - Recording consent is on the human: check local/state law and the company's
    policy before recording; when in doubt, take notes instead. The tooling
    treats the transcript as already-lawfully-obtained input.
  - `interviews/` goes in `.gitignore`. Transcripts contain other people's words
    and possibly confidential company info; they stay local, never committed,
    never pasted into dossiers (dossiers are committed and cite public sources only).
  - Debriefs may summarize; they must not quote interviewers at length.
  HOW: new command `.claude/commands/jh-debrief.md` + optionally a
  `debrief-analyst` agent; `src/query.py` helper to log the event. Transcription
  itself stays out of scope (use Voice Memos + any local transcriber; the
  pipeline starts at "a .md/.txt transcript exists").

- [x] **6.3 `/jh-prep <id>`: interview prep brief.**
  WHAT: when a job hits `screen`/`interview`, generate
  `applications/<...>/prep-<round>.md`: likely questions from the JD, your
  matching stories from `master_resume.yaml` (STAR-shaped, grounded), questions
  to ask them, recent company news from the dossier, and, crucially, everything
  `/jh-debrief` learned from earlier rounds at this company AND from similar
  roles elsewhere (common questions for this title family from the answer bank).
  WHY: the two ingredients (dossier + tailored resume) already exist; this is the
  natural next pipeline stage and consumes the 6.2 output.
  HOW: `.claude/commands/jh-prep.md`; refresh the dossier first if `stale` (3.6).

- [x] **6.4 Answer bank.**
  WHAT: `resume/answers.yaml`: canonical, human-approved answers to recurring
  application/interview questions (why-us template, visa/TN status, salary
  expectations, notice period, remote setup). `/jh-tailor` emits a per-job
  `answers.md` next to the cover letter with the relevant ones filled in;
  `/jh-debrief` proposes additions/edits (marked `draft: true` until the human
  approves them).
  WHY: removes the most tedious part of applying while keeping the human on
  submit; gives debrief learnings a durable home.
  GUARDRAIL: answers obey the never-fabricate rule; salary figures come from the
  human, never generated.

- [x] **6.5 `/jh-review`: the monthly feedback loop.**
  WHAT: a command that reads `events` + statuses and reports:
  - conversion by stage (applied -> reply -> screen -> interview -> offer),
    segmented by title family, score band, source, and remote/on-site;
  - triage/match calibration: score distribution of jobs that got replies vs
    ghosted (are the 90s actually converting better than the 75s?);
  - false-drop audit: sample of `irrelevant` triage drops for human spot-check
    (the docs record a near-miss where ~50 Anthropic/OpenAI roles were almost
    dropped; make that check systematic);
  - recurring interview themes from debriefs (questions seen 3+ times, answers
    consistently marked weak);
  - concrete proposed edits to `profile.yaml` / `job-matcher.md` rubric, as a
    diff the human approves or rejects. Nothing self-modifies.
  WHY: the project's thesis is that targeted applications convert better; this is
  the only mechanism that measures it and improves the targeting.
  HOW: `.claude/commands/jh-review.md` + `python -m src.query stats` helpers so
  the numbers are computed deterministically in SQL, not by the LLM.

- [x] **6.6 Salary intelligence (small, do anytime after 6.1).**
  WHAT: `python -m src.query comp`: salary_min/max distribution for matched title
  families, split MX vs US-remote, from data already being stored (Adzuna, Torre,
  RemoteOK emit salaries; nothing reads them today). Surface in `/jh-review` and
  before any negotiation.

- [ ] **6.7 (Deferred, decision 2026-07-16: NOT building now) Assisted form-fill.**
  The README promise was removed in Phase 4. Revisit only if the answer bank +
  manual flow proves too slow in practice; the answer bank (6.4) removes most of
  the pain already.
  The README promises "assisted form-fill optional / Playwright". Only worth
  building after 6.4 (the answer bank is the content source). Strictly
  fill-and-pause: Playwright pre-fills fields from `answers.md` + resume data,
  human reviews every field and clicks submit. Never auto-submit; never drive
  logged-in LinkedIn/Indeed. If not built by end of Phase 6, delete the README row.

---

## Sequencing summary

| Phase | Theme | Effort | Unblocks |
|-------|-------|--------|----------|
| 0 | Hygiene | 0.5d | everything (clean tree) |
| 1 | Tracking integrity | 1-2d | follow-ups, 6.1, honest funnel |
| 2 | Automated loop | 1-2d | daily value without babysitting |
| 5.4 | Migrations (pull early) | 0.5d | 2.4, 3.2, all of 6 |
| 3 | Data quality | 2-3d | trustworthy scoring at scale |
| 4 | Config/docs consistency | 1d | agents stop contradicting each other |
| 5 | Tests/CI/lint | 2-3d | safe refactors (parallel with 3-4) |
| 6 | Intelligence layer | 3-5d | the system learns |

Dependencies to respect:
- 5.4 (migrations) before 2.4, 3.2, 6.1.
- 1.1 (set-status) before 1.3, 1.4, 6.1.
- 6.1 (events) before 6.2/6.5; 6.2 before 6.3's cross-round features; 6.4 before 6.7.
- 3.6 (slug+staleness) before 6.3 (prep refreshes stale dossiers).

Everything in Phases 0-2 is independent enough to ship as one PR each; Phase 6
items are one PR per command.
