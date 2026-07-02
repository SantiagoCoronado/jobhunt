# jobhunt, project guide for Claude Code

A DIY, $0 job-search copilot. Engine = Claude Code. Deterministic plumbing = Python.

## Pipeline
1. **Discover** (`src/discover.py`), pull free ATS APIs + aggregators → SQLite (`data/jobs.db`).
2. **Match** (`/match` → `job-matcher` agent), score jobs vs `config/profile.yaml`.
3. **Tailor** (`/tailor <id>` → `resume-tailor` agent), per-job resume + cover letter into `applications/`.
4. **Track** (`src/crm/viewer.py` local UI, or `/notion-sync`), application status + follow-ups.

## Data model
Everything lives in one SQLite table `jobs` (see `src/db.py`). `status` column IS the CRM
pipeline: discovered → shortlisted → applied → screen → interview → offer/rejected/ghosted.
SQLite is canonical; Notion is a convenience mirror.

## Hard rules (enforce these in every AI step)
- **Never fabricate** resume content. Only reframe what's in `resume/master_resume.yaml`.
- **Never auto-submit** applications or drive logged-in LinkedIn/Indeed. Human clicks submit.
- Discovery uses only free, ToS-safe sources. `jobspy` (Indeed/LinkedIn scraping) stays off
  unless the user explicitly enables it and accepts the risk.
- Keep resumes ATS-clean: single column, standard headings, no tables/images, acronym+full form.
- **Zero em-dashes** (Unicode U+2014) in ANY generated text (resumes, cover letters, notes, reports). Canonical rule. Use commas/colons/periods.

## Resume rendering
Theme is `engineeringresumes` (RenderCV, installed in `.venv`; keep it current, v2.3 had bugs).
To fit one page, compress with `text.font_size`/`leading` + `section_titles`/`entries`/`highlights`
spacing. Do NOT set `design.page.*_margin`, it crashes this theme's Typst template ("cannot
multiply dictionary with integer"). Working example: `applications/easyaudit-ai-393/tailored_resume.yaml`.

## Commands
`/discover` `/match` `/tailor <id>` `/followups` `/notion-sync`, see `.claude/commands/`.
Helper queries: `python -m src.query {job <id>|crm|followups}`.
