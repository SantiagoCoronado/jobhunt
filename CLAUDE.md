# jobhunt, project guide for Claude Code

A DIY, $0 job-search copilot. Engine = Claude Code. Deterministic plumbing = Python.

## Pipeline
1. **Discover** (`/jh-discover` → `src/discover.py`), pull free ATS APIs + aggregators → SQLite (`data/jobs.db`).
   Sources live in `config/sources.yaml` (one block per adapter in `src/adapters/`, each a
   `fetch(cfg) -> list[Job]`), which is tracked and holds adapter MECHANICS only: endpoints,
   page sizes, `enabled:`, field mappings. The user's TARGETING (ATS tokens, countries,
   locales, query lists, the dreamsheet file id, extra title words) lives in the git-ignored
   `config/sources.local.yaml`. Read the merged view with `src.config.sources()`, never
   `load_yaml("sources.yaml")`; `missing_targeting` skips an enabled source whose targeting
   is absent, with a hint. Keyed sources read `.env` (copy `.env.example`) via
   `src.config.get_secret`; a source with no key prints a hint and yields nothing (never breaks the run).
   Opt-in sources are gated by `enabled:` in the tracked file (see `docs/new-sources.md`).
   A shared `title_filter:` gates off-family titles centrally in `src/discover.py`
   (word-boundary match; calibrated 2026-08-27 to keep every row that ever reached shortlisted).
   `config.sources()` builds its `include` list from the tracked generic-engineering base plus
   words derived from the profile's `target_titles` / `role_families` (`config.title_words`)
   plus `title_filter.include_extra` in the local file; a source can opt out of the gate
   (hackernews does). Never filter by location there.
2. **Triage** (optional but recommended when the discovered pile is large; `/jh-triage` →
   `src/triage.py`). Coarse Haiku junk-cut BEFORE the expensive matcher: `export --chunk` → fan Haiku
   sub-agents (keep/drop vs the profile dealbreakers, keep-on-doubt) → `ingest`. Drops become
   `status='irrelevant'` (out of every future stage); keepers get a 0-3 fit bucket in `match_verdict`.
   Drives ~80 agents (100-row chunks, 8k-row pile) via a Workflow for a full sweep. See `docs/scaling-scoring.md`.
3. **Match** (`/jh-match` → `job-matcher` agent), score jobs vs `config/profile.yaml`. Default
   `export --limit N` scores the top N by fit bucket then keyword prescore. To score at scale,
   `export --min-bucket 3 --chunk 60 --limit 0` → fan `job-matcher` over `data/match/chunk_*.json`
   (each writes `scores_NNN.json`) → `ingest --dir data/match`.
4. **Research** (optional; `/jh-research <company|id>` → `company-researcher` agent, runs on Sonnet),
   cited company dossier into `research/companies/<slug>.md`. `/jh-tailor` auto-weaves it into the cover letter.
5. **Tailor** (`/jh-tailor <id>` → `resume-tailor` agent), per-job resume + cover letter into `applications/`.
6. **Track** (`src/crm/viewer.py` local UI, being replaced by a Textual TUI: `docs/spec-tui.md`).
   Notion is gone since 2026-09-04 (pull script and command deleted; its MCP push had cost
   25M to 65M context tokens per hunt, `docs/token-efficiency.md`). The hunt picks its 5 targets with
   `python -m src.pick` (star rule, dream slots, skips companies already in play).
   `/jh-gmail-sync` reads every mailbox in `.env` (`MAIL_ACCOUNTS`, app passwords; STRICTLY
   read-only, IMAP EXAMINE + PEEK) via `python -m src.mail_fetch`, which prints a legend + a
   one-line-per-thread manifest; the model classifies THAT (`show <id>` for unsettled lines,
   never reads `data/mail_*`, never `query crm`/`query job` in that step), writes
   `data/gmail_pull.json`, then `python -m src.gmail_pull` validates and applies; since
   2026-09-04 the dry run is followed by `--apply` without a chat approval, the applier's
   guardrails are the gate (forward-only moves, never ghosted/withdrawn, `offer` only with full evidence and never
   accept/decline, evidence headers + signal only, bodies never enter the DB, applied ids recorded as seen). Gmail MCP is the
   fallback only when no account is configured. Setup + tuning: `docs/mail-setup.md`.
   `/jh-report` (`python -m src.report`) renders `data/report.html`, the offline dashboard.
7. **Learn** (the intelligence layer). `/jh-upskill [id]`: gap analysis via `python -m src.gaps`
   (matcher missing_skills + lexicon scan vs `config/skills_lexicon.yaml`); vocabulary gaps become
   proposed profile.yaml diffs, real gaps a learning plan in `research/upskill/`; learning plans
   NEVER feed resume content. `/jh-prep <id>`: interview prep brief from dossier +
   past debriefs. `/jh-debrief <id>`: digest an interview transcript (dropped at
   `interviews/<company>-<id>/<date>-<round>.md`, git-ignored, NEVER committed) into a debrief +
   answer-bank drafts. `/jh-review`: monthly conversion/calibration report over `python -m
   src.stats {funnel|calibration|latency|drops|comp}`; proposes profile/rubric edits as diffs.
   `resume/answers.yaml` is the answer bank: `draft: true` entries await human review; answers
   only ever contain master-resume facts. Every status change / contact / debrief lands in the
   `events` table (written by `db.set_status`/`touch_contact`/`log_event`).

`/jh-hunt` runs the whole loop end to end: discover, triage (Haiku, 100-row chunks), match,
inbox pull, pick the top 5 shortlisted (`src.pick`), research those 5, then tailor those 5.

**Token discipline** (audit 2026-09-02, `docs/token-efficiency.md`): measure any hunt with
`python scripts/token_audit.py --latest` (per agent, per tool, per phase; `--all` for one row per
session). Rules that fell out of it: no Notion in the hunt; subagents reply in one line or under
120 words; `python -m src.answers_export <id>` replaces reading `resume/answers.yaml`; the tailor
runs render/audit at most twice; triage chunks are 100 rows (Haiku truncates a 200-row JSON
write); never `python -m src.query crm` inside an orchestrated step.

**Dream companies** (set 2026-09-01): `dream_companies` + `dream_rule` + `relocation_line` +
`dream_shortlist_threshold` in `config/profile.yaml` are the single authority; `src/dream.py`
computes `is_dream(company)` from them (never stored, so editing the list never goes stale).
For those companies the location rule and comp floors are waived, the title gate is skipped,
match export sorts them first with `dream: true`, ingest shortlists them at the lower cutoff,
`/jh-hunt` reserves up to 2 of the 5 stars for them, and the tailor adds the relocation line
when US presence is required. ITAR / US-person / citizens-only / clearance stay hard blocks.
The hand-curated sheet (`dreamsheet` in `config/sources.local.yaml`, private Google Sheet) is read
by `/jh-discover` through the Drive tool into `data/dream_sheet.md`, which the adapter parses;
a dream company with no usable board is sheet rows and outreach only.

Applications are filed by status: `applications/{applied,pending,other}/<company>-<id>/`. New
`/jh-tailor` drafts land in `pending/`; move a folder to `applied/` once submitted, `other/` for
rejected/ghosted/withdrawn. `scripts/export_pdf.sh` searches these nested folders.
`python -m src.reconcile` keeps folders and DB statuses agreeing (folder names carry `-<id>`).

## Data model
Everything lives in one SQLite table `jobs` (see `src/db.py`). `status` column IS the CRM
pipeline: discovered → shortlisted → applied → screen → interview → offer, with terminal
outcomes rejected/ghosted/withdrawn and a deliberate `backlog` hold. `db.STATUSES` is the single
authority on this vocabulary; `declined` is NOT a status (use `withdrawn`).
`irrelevant` is a terminal triage-drop (off-field / dealbreaker), excluded from match/export/triage.
Triage keepers store their fit bucket in `match_verdict` until real scoring overwrites it.
SQLite is canonical.

## Hard rules (enforce these in every AI step)
- **Never fabricate** resume content. Only reframe what's in `resume/master_resume.yaml`.
- **Never auto-submit** applications or drive logged-in LinkedIn/Indeed. Human clicks submit.
- Discovery uses only free, ToS-safe sources. `jobspy` (Indeed/LinkedIn scraping) stays off
  unless the user explicitly enables it and accepts the risk.
- Keep resumes ATS-clean: single column, standard headings, no tables/images, acronym+full form.
- **Zero em-dashes** (Unicode U+2014) in ANY generated text (resumes, cover letters, notes, reports). Canonical rule. Use commas/colons/periods.
- **Voice rules for all application text** (answers, cover letters, outreach): `docs/writing-voice.md`.
  No "not X, it's Y" reversals, no kicker endings, no invented percentages, no intensifiers. Plain
  engineer-in-a-form voice. Every tailor/answer agent must read that file first.

## Resume rendering
Canonical renderer (docx, house design):

```
python -m src.render_docx <resume.yaml> [--pdf] [--fit auto|0|1|2|3]
```

- Emits .docx replicating the reference design: Arial, navy `#1F3864` accents, underlined CAPS
  section headers, 0.38in/0.7in margins, right-tab dates, compact spacing.
- `--fit auto` (default) picks the loosest spacing level that fits ONE page and prints page fill.
  If even level 3 overflows, trim bullets; do not compress further. Target 90-100% fill.
- `--pdf` converts via LibreOffice (`soffice`) when installed; otherwise export from Word.
- `--audit` flags paragraphs whose last line is <70% full (trailing white space). Fix by cutting
  or extending REAL content per the reported char counts; never pad with filler.
- Reference look: the user's own original CV under `resume/originals/` (git-ignored).
- RenderCV `engineeringresumes` is legacy, use only if explicitly asked. Known bug: setting
  `design.page.*_margin` crashes its Typst template.

## Commands
All commands are `jh-` prefixed; see `.claude/commands/`.
Helper queries: `python -m src.query {job <id>|crm|followups}`; hand-enter a board-less role with `python -m src.query add --company C --title T ...` (reuses a same company+title row when one exists; the only insert path outside discovery), `python -m src.research {path "<company>"|get <id>}`.
Status transitions: `python -m src.query set-status <id> <status> [--note ...] [--followup YYYY-MM-DD]`
(single write path: validates, stamps `applied_at`, auto-schedules the follow-up, moves the
application folder to its bucket). Record contact: `python -m src.query touch <id> [--bump]`.
Lean tailor (spec `docs/spec-tailor-lean.md`, Phase A landed 2026-09-02): `python -m src.tailor_bundle <id>`
writes the one input file the tailor reads (`data/tailor/<id>/inputs.md`, voice + profile + master +
generated page geometry + job + dossier + answers); `python -m src.tailor_build <folder>` splits `draft.md`,
checks, renders, audits, exports PDFs, verifies the page count and prints a verdict (exit 1 = fix it),
writing `build.json` + `state.json` in the folder. The resume-tailor agent, `/jh-tailor` and `/jh-hunt`
step 7 run on them (Phase B, measured at 3 to 4 calls and under 0.2M tokens per application).
Folder/DB drift check: `python -m src.reconcile [--apply]`. Tests: `.venv/bin/python -m pytest tests/`.
DB maintenance (auto-runs after discover): `python -m src.maintain [--vacuum]`, expires postings
that vanished from an actively-checked source, prunes irrelevant/expired descriptions.
Cross-source dedup: query the `canonical_jobs` view (one deterministic row per role, ATS source
preferred), never bare `GROUP BY canonical_key`.
Company dossiers (`research/companies/<slug>.md`) are committed, reusable, cited; obey the
never-fabricate and zero-em-dash rules like any generated text.
