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
`/discover` `/match` `/tailor <id>` `/followups` `/notion-sync`, see `.claude/commands/`.
Helper queries: `python -m src.query {job <id>|crm|followups}`.
