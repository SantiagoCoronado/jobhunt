# jobhunt, project guide for Claude Code

A DIY, $0 job-search copilot. Engine = Claude Code. Deterministic plumbing = Python.

## Pipeline
1. **Discover** (`/jh-discover` → `src/discover.py`), pull free ATS APIs + aggregators → SQLite (`data/jobs.db`).
   Sources live in `config/sources.yaml` (one block per adapter in `src/adapters/`, each a
   `fetch(cfg) -> list[Job]`), which is tracked and holds adapter MECHANICS only: endpoints,
   page sizes, `enabled:`, field mappings. The user's TARGETING (ATS tokens, countries,
   locales, query lists, extra title words) lives in the git-ignored
   `config/sources.local.yaml`. Read the merged view with `src.config.sources()`, never
   `load_yaml("sources.yaml")`; `missing_targeting` skips an enabled source whose targeting
   is absent, with a hint. Keyed sources read `.env` (copy `.env.example`) via
   `src.config.get_secret`; a source with no key prints a hint and yields nothing (never breaks the run).
   Opt-in sources are gated by `enabled:` in the tracked file (see `docs/history/new-sources.md`).
   A shared `title_filter:` gates off-family titles centrally in `src/discover.py`
   (word-boundary match; calibrated 2026-08-27 to keep every row that ever reached shortlisted).
   `config.sources()` builds its `include` list from the tracked generic-engineering base plus
   words derived from the profile's `target_titles` / `role_families` (`config.title_words`)
   plus `title_filter.include_extra` in the local file; a source can opt out of the gate
   (hackernews does). Never filter by location there.
   Sources are region-gated (decision 10 of `docs/spec-pre-release.md`): every block in
   `sources.yaml` declares `regions:` (`config/geo.yaml` names or `global`); `config.sources()`
   turns off a source whose regions miss `config.coverage(profile)` (locations, header_location,
   `work_authorization.relocation_regions`), an `enabled:` in the local file forces it either way,
   and discover prints one `off by region` line per skipped source. The European boards
   (jobtech, jobindex, berlinstartupjobs) and the ones verified but not wired are in `docs/sources-europe.md`.
2. **Triage** (optional but recommended when the discovered pile is large; `/jh-triage` →
   `python -m src.hunt run --only triage` over `src/triage.py`). Coarse junk-cut BEFORE the expensive
   matcher: `export --chunk` → one `triager` process per chunk (keep/drop vs the profile dealbreakers,
   keep-on-doubt) → `ingest`. Drops become `status='irrelevant'` (out of every future stage); keepers
   get a 0-3 fit bucket in `match_verdict`. See `docs/scaling-scoring.md`.
3. **Match** (`/jh-match` → `python -m src.hunt run --only match`, one `job-matcher` process per
   chunk), score jobs vs `config/profile.yaml`: `export --min-bucket N --chunk 60` → `scores_NNN.json`
   per chunk → `ingest --dir data/match`. The commands are viewers of the orchestrator (decision 5,
   `docs/spec-pre-release.md`); no command fans out agents itself.
4. **Research** (optional; `/jh-research <company|id>` → `company-researcher` agent, runs on Sonnet),
   cited company dossier into `research/companies/<slug>.md`. `/jh-tailor` auto-weaves it into the cover letter.
5. **Tailor** (`/jh-tailor <id>` → `resume-tailor` agent), per-job resume + cover letter into `applications/`.
6. **Track** (`python -m src.tui`, or the one-word launcher `jobhunt` = `bin/jobhunt` symlinked by
   `scripts/install_launcher.sh [name]`; a Textual TUI, spec `docs/spec-tui.md`; the Flask viewer is gone since
   2026-09-18). Board and follow-ups share one three-pane screen (the shortlist section is gone since 2026-09-20; status list, jobs table,
   detail; the board's status list ends with `dream list`, the rows at a dream company, where `a` adds a
   company and `x` removes one through `data.add_dream` / `remove_dream`); the rows `src.pick` would choose arrive pre-selected (`data.picks()`, computed, never
   stored, feeds `c` and the runner only), `space`/`v` select by hand for bulk status (the marks are the app's,
   `src/tui/selection.py`, shared by every section), `c` copies `/jh-tailor` lines; section 3 lists `applications/` beside the DB
   (`data.apps()`, `R` = reconcile through `reconcile.apply`); section 4 prints `stats funnel`; section 5 is the
   runner (`data.stages()` = the full hunt, the `src.hunt` registry, reconcile, stats; `enter` spawns the stage
   through `commands.spawn`, one at a time, `tailor` and `research` on the marked rows through `hunt run --ids`, `ctrl+c` = SIGTERM so `--resume` works, `R` resumes a run; runs and
   units come from `data.hunt_runs()` / `hunt_status()` over the ledgers); section 6 shows the config files
   read-only (`e` = the editor template in `config/tui.toml`); `,` is the settings modal (`src/tui/settings.py`
   loads and rewrites `config/tui.toml`, never raises; its harness tab writes `config/hunt.toml` only through
   `src.hunt.config.set_default_harness` / `set_stage_model`, a comment-keeping one-line edit). Every load shows through `src/tui/loading.py` (`Busy`: indicator on a slow first load, footer mark on a reload, cleared in a `finally`). `src/tui/data.py` is the ONLY TUI module that opens SQLite and every write goes through
   `db.set_status` / `touch_contact` / `log_event` plus `reconcile.sync_folder`, as `src.query` does.
   Pilot tests opt into the `tmp_db` fixture (`tests/tui_fakes.py`, `pytestmark = pytest.mark.usefixtures("tmp_db")`), which patches
   `db.DB_PATH`, `reconcile.APPS_DIR`, `research.COMPANIES_DIR`, `settings.TUI_TOML`, `hunt.config.HUNT_TOML`, `ledger.HUNT_DIR`,
   `commands.launch`, `commands.pbcopy` and `commands.capture` (a captured command is a child process and would read the real DB).
   Notion is gone since 2026-09-04 (pull script and command deleted; its MCP push had cost
   25M to 65M context tokens per hunt, `docs/history/token-efficiency.md`). The hunt picks its 5 targets with
   `python -m src.pick` (star rule, dream slots, skips companies already in play).
   `/jh-gmail-sync` reads every mailbox in `.env` (`MAIL_ACCOUNTS`, app passwords; STRICTLY
   read-only, IMAP EXAMINE + PEEK) via `python -m src.mail_fetch`, which prints a legend + a
   one-line-per-thread manifest (the session runs it with `--summary`); the `inbox-classifier`
   agent classifies THAT (`manifest --page N`, `show <id>` for unsettled lines, never reads
   `data/mail_*`, never `query crm`/`query job` in that step) and replies the proposals, the
   session writes `data/gmail_pull.json`, then `python -m src.gmail_pull` validates and applies; since
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
   src.stats {funnel|calibration|latency|drops|comp|hunts}` (`hunts` reads the run ledgers, never the DB:
   units, retries, failures, usage per stage per run); proposes profile/rubric edits as diffs.
   `resume/answers.yaml` is the answer bank: `draft: true` entries await human review; answers
   only ever contain master-resume facts. Every status change / contact / debrief lands in the
   `events` table (written by `db.set_status`/`touch_contact`/`log_event`).

`/jh-hunt` runs the whole loop end to end under the hunt orchestrator (`python -m src.hunt`,
spec `docs/spec-hunt-orchestrator.md`): discover, triage, match, inbox, pick the top 5
shortlisted (`src.pick`), research those 5, tailor those 5, report. The skill is a viewer:
`hunt run` in the background, `hunt status latest` while it runs, `hunt report latest` at the
end; no Agent calls, no Workflow. The orchestrator fans out at the PROCESS level (one harness
process per triage chunk, match chunk, dossier, tailor, one for the inbox), so it never uses
a harness's own subagent or workflow feature. Python judges done: a unit is done when its
output file passes the stage's check (coverage of every id, the applier's dry run, the dossier
`researched:` line, `tailor_build` run again), never because the agent said so. Only Python
writes the DB. `config/hunt.toml` says how to run (harness, per-stage model from the live
catalog, caps, timeouts, retries); `config/profile.yaml` still says what counts as a fit.
The ledger is `data/hunt/<run_id>/` (`state.json`, `events.jsonl`, `prompts/`, `logs/`,
`picks.json`, `report.md`); questions a run cannot ask become `needs_human` lines in the report.

**Token discipline** (audit 2026-09-02, `docs/history/token-efficiency.md`): measure any hunt with
`python scripts/token_audit.py --latest` (per agent, per tool, per phase; `--all` for one row per
session; `--hunt RUN|latest` reads the run's ledger instead: per stage, per harness, biggest
units). Rules that fell out of it: no Notion in the hunt; subagents reply in one line or under
120 words; `python -m src.answers_export <id>` replaces reading `resume/answers.yaml`; the tailor
runs render/audit at most twice; triage chunks are 100 rows (Haiku truncates a 200-row JSON
write); never `python -m src.query crm` inside an orchestrated step.

**Dream companies** (set 2026-09-01; the list moved to the DB 2026-10-06, `docs/spec-pre-release.md`
decision 9): the LIST is the `dream_companies` table in `data/jobs.db` (name, match aliases, careers
URL, note, added_at), edited with `python -m src.query dream {list|add|rm}` or the TUI's Dream tab;
the RULES `dream_rule` + `relocation_line` + `dream_shortlist_threshold` stay in `config/profile.yaml`.
`python -m src.init` moves an older profile's `dream_companies:` list into the table once (commented
out under a dated note; until then that list still counts). `src/dream.py` computes `is_dream(company)`
from the table, cached per process (never stored on a job row, so editing the list never goes stale).
For those companies the location rule and comp floors are waived, the title gate is skipped,
match export sorts them first with `dream: true`, ingest shortlists them at the lower cutoff,
`/jh-hunt` reserves up to 2 of the 5 stars for them, and the tailor adds the relocation line
and the `relocation_header` note when the role requires presence inside
`work_authorization.relocation_regions` (plus home; `config/geo.yaml` resolves the location),
a plain visa note outside them, neither for remote-from-home. Export-control ("US person",
ITAR), citizens-only and clearance requirements stay hard blocks.
A dream company with no usable board is hand-entered rows (`python -m src.query add`) and outreach only.

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
All commands are `jh-` prefixed and live ONCE in `prompts/commands/<name>.md` (frontmatter: description,
argument-hint, tools in the command vocabulary; the body in harness-neutral words); `.claude/commands/`,
`.opencode/commands/`, `.gemini/commands/` (toml), `.pi/prompts/` and the `## Commands` list in `AGENTS.md`
(codex, agy) are renders of them (`docs/hunt-harnesses.md`, "Commands on every harness").
Agent system prompts live ONCE in `prompts/agents/<role>.md` (frontmatter: tools, output contract);
`python -m src.hunt sync-agents` regenerates every harness's native files from both (`.claude/agents`,
`.opencode/agents`, `.pi/agents`, `.gemini/agents`, `.codex/agents`, the command renders; a file carries a stage's model only
when that stage runs on that file's harness), and CI runs `sync-agents --check`. Never edit a generated agent or command file.
Harnesses (`docs/hunt-harnesses.md`): adapters claude, codex, opencode, pi, agy in `src/hunt/harness/`, anything
else a `[harness.<name>]` command template in `config/hunt.toml`; an adapter refuses a tool it cannot grant,
and only opencode reads its generated file at run time (`--agent`). Real-CLI smoke: `HUNT_SMOKE=1 pytest -m harness_smoke`.
Hunt orchestrator: `python -m src.hunt run [--from S] [--to S] [--only S] [--skip S] [--ids ID,ID] [--harness H]`
(`--ids` = research/tailor rows a human chose instead of the pick stage, `src.pick.chosen`)
(exit 0 done, 2 a stage failed, 3 nothing to tailor), `run --resume RUN|latest` (done units
skipped, outputs on disk verified again, never a second export; a dead run's lock is taken
over), `status [RUN]`, `report [RUN]`, `runs`, `models`, `doctor`. Nothing is scheduled from the tree:
`docs/scheduling.md` is one paragraph (cron or launchd running `hunt run --to match` then the digest). Stage code is `src/hunt/stages/<stage>.py` over the
shared `fan.py`. Tests must use a fake harness: `tests/conftest.py` refuses to start a real
agent CLI, and a bare `hunt run` in a test IS a hunt (patch `connect` and the data dirs of
every module a stage touches, as `tests/test_hunt_*.py` do).
Helper queries: `python -m src.query {job <id>|crm|followups}`; hand-enter a board-less role with `python -m src.query add --company C --title T ...` (reuses a same company+title row when one exists; the only insert path outside discovery), `python -m src.research {path "<company>"|get <id>}`.
Status transitions: `python -m src.query set-status <id> <status> [--note ...] [--followup YYYY-MM-DD]`
(single write path: validates, stamps `applied_at`, auto-schedules the follow-up, moves the
application folder to its bucket). Record contact: `python -m src.query touch <id> [--bump]`.
Lean tailor (spec `docs/spec-tailor-lean.md`, Phase A landed 2026-09-02): `python -m src.tailor_bundle <id>`
writes the one input file the tailor reads (`data/tailor/<id>/inputs.md`, voice + profile + master +
generated page geometry + job + dossier + answers); `python -m src.tailor_build <folder>` splits `draft.md`,
checks, renders, audits, exports PDFs, verifies the page count and prints a verdict (exit 1 = fix it),
writing `build.json` + `state.json` in the folder. The resume-tailor agent, `/jh-tailor` and the hunt's
tailor stage (`src/hunt/stages/tailor.py`) run on them (Phase B, measured at 3 to 4 calls and under 0.2M tokens per application).
Folder/DB drift check: `python -m src.reconcile [--apply]`. Tests: `.venv/bin/python -m pytest tests/`.
DB maintenance (auto-runs after discover): `python -m src.maintain [--vacuum]`, expires postings
that vanished from an actively-checked source, prunes irrelevant/expired descriptions.
Cross-source dedup: query the `canonical_jobs` view (one deterministic row per role, ATS source
preferred), never bare `GROUP BY canonical_key`.
Company dossiers (`research/companies/<slug>.md`) are committed, reusable, cited; obey the
never-fabricate and zero-em-dash rules like any generated text.
