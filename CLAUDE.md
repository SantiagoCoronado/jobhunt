# jobhunt, project guide for Claude Code

A DIY, $0 job-search copilot. Engine = Claude Code. Deterministic plumbing = Python.

## Pipeline
1. **Discover** (`/jh-discover` → `src/discover.py`), pull free ATS APIs + aggregators → SQLite (`data/jobs.db`).
   Sources live in `config/sources.yaml` (one block per adapter in `src/adapters/`, each a
   `fetch(cfg) -> list[Job]`). Keyed sources read `.env` (copy `.env.example`) via
   `src.config.get_secret`; a source with no key prints a hint and yields nothing (never breaks the run).
   Active new sources: Adzuna (MX, keyed), The Muse, Findwork (keyed), Torre (remote-LATAM). Opt-in via
   `enabled:`: Careerjet, Personio, BambooHR, Workday, Consider, YC (see `docs/new-sources.md`).
2. **Triage** (optional but recommended when the discovered pile is large; `/jh-triage` →
   `src/triage.py`). Coarse Haiku junk-cut BEFORE the expensive matcher: `export --chunk` → fan Haiku
   sub-agents (keep/drop vs the profile dealbreakers, keep-on-doubt) → `ingest`. Drops become
   `status='irrelevant'` (out of every future stage); keepers get a 0-3 fit bucket in `match_verdict`.
   Drives ~40 agents via a Workflow for a full sweep. See `docs/scaling-scoring.md`.
3. **Match** (`/jh-match` → `job-matcher` agent), score jobs vs `config/profile.yaml`. Default
   `export --limit N` scores the top N by fit bucket then keyword prescore. To score at scale,
   `export --min-bucket 3 --chunk 60 --limit 0` → fan `job-matcher` over `data/match/chunk_*.json`
   (each writes `scores_NNN.json`) → `ingest --dir data/match`.
4. **Research** (optional; `/jh-research <company|id>` → `company-researcher` agent, runs on Sonnet),
   cited company dossier into `research/companies/<slug>.md`. `/jh-tailor` auto-weaves it into the cover letter.
5. **Tailor** (`/jh-tailor <id>` → `resume-tailor` agent), per-job resume + cover letter into `applications/`.
6. **Track** (`src/crm/viewer.py` local UI, or `/jh-notion-sync`), application status + follow-ups.

`/jh-hunt` runs the whole loop end to end: discover, match, sync + star the top 5 shortlisted,
research those 5, then tailor those 5.

Applications are filed by status: `applications/{applied,pending,other}/<company>-<id>/`. New
`/jh-tailor` drafts land in `pending/`; move a folder to `applied/` once submitted, `other/` for
rejected/ghosted/withdrawn. `scripts/export_pdf.sh` searches these nested folders.
`python -m src.reconcile` keeps folders and DB statuses agreeing (folder names carry `-<id>`).

## Data model
Everything lives in one SQLite table `jobs` (see `src/db.py`). `status` column IS the CRM
pipeline: discovered → shortlisted → applied → screen → interview → offer, with terminal
outcomes rejected/ghosted/withdrawn and a deliberate `backlog` hold. `db.STATUSES` is the single
authority on this vocabulary; `declined` is NOT a status (it is Notion's phone-side label for
`withdrawn`, mapped on sync).
`irrelevant` is a terminal triage-drop (off-field / dealbreaker), excluded from match/export/triage.
Triage keepers store their fit bucket in `match_verdict` until real scoring overwrites it.
SQLite is canonical; Notion is a convenience mirror.

## Hard rules (enforce these in every AI step)
- **Never fabricate** resume content. Only reframe what's in `resume/master_resume.yaml`.
- **Never auto-submit** applications or drive logged-in LinkedIn/Indeed. Human clicks submit.
- Discovery uses only free, ToS-safe sources. `jobspy` (Indeed/LinkedIn scraping) stays off
  unless the user explicitly enables it and accepts the risk.
- Keep resumes ATS-clean: single column, standard headings, no tables/images, acronym+full form.
- **Zero em-dashes** (Unicode U+2014) in ANY generated text (resumes, cover letters, notes, reports). Canonical rule. Use commas/colons/periods.

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
- Reference look: `resume/originals/CV Santiago Coronado - English latest.docx`.
- RenderCV `engineeringresumes` is legacy, use only if explicitly asked. Known bug: setting
  `design.page.*_margin` crashes its Typst template.

## Commands
All skills are `jh-` prefixed. `/jh-hunt` (full pipeline), `/jh-discover` `/jh-match`
`/jh-research <company|id>` `/jh-tailor <id>` `/jh-followups` `/jh-notion-sync`, see `.claude/commands/`.
Helper queries: `python -m src.query {job <id>|crm|followups}`, `python -m src.research {path "<company>"|get <id>}`.
Status transitions: `python -m src.query set-status <id> <status> [--note ...] [--followup YYYY-MM-DD]`
(single write path: validates, stamps `applied_at`, auto-schedules the follow-up, moves the
application folder to its bucket). Record contact: `python -m src.query touch <id> [--bump]`.
Folder/DB drift check: `python -m src.reconcile [--apply]`. Tests: `.venv/bin/python -m pytest tests/`.
DB maintenance (auto-runs after discover): `python -m src.maintain [--vacuum]`, expires postings
that vanished from an actively-checked source, prunes irrelevant/expired descriptions.
Cross-source dedup: query the `canonical_jobs` view (one deterministic row per role, ATS source
preferred), never bare `GROUP BY canonical_key`.
Notion pull (reverse sync, used by `/jh-notion-sync` phase 1): export Notion rows to
`data/notion_pull.json`, then `python -m src.notion_pull data/notion_pull.json [--apply] [--create-missing]`
(maps Notion `declined`/`Not Found` -> `withdrawn`, never downgrades, keeps `backlog` holds).
Company dossiers (`research/companies/<slug>.md`) are committed, reusable, cited; obey the
never-fabricate and zero-em-dash rules like any generated text.
