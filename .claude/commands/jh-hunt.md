---
description: Full job-hunt pipeline end to end: discover, match, sync + star top 5 shortlisted, research + tailor those 5. Usage: /jh-hunt
allowed-tools: Read, Write, Bash, WebSearch, WebFetch, mcp__claude_ai_Notion__notion-search, mcp__claude_ai_Notion__notion-query-data-sources, mcp__claude_ai_Notion__notion-create-database, mcp__claude_ai_Notion__notion-create-pages, mcp__claude_ai_Notion__notion-update-page
---

Run my whole job hunt end to end. Do the phases in order and give me a short report after each.
Use `.venv/bin/python` if plain `python` is not on PATH.

1. **Discover** (the `/jh-discover` flow): run `python -m src.discover`. Report how many new jobs landed.

2. **Match** (the `/jh-match` flow): run `python -m src.match export --limit 40`, delegate scoring to
   the **job-matcher** subagent (it reads `config/profile.yaml` + `data/pending_match.json`, writes
   `data/scores.json`), then ingest. Be calibrated. Report how many were shortlisted.

3. **Sync + star** (the `/jh-notion-sync` flow, with a top-5 star rule): mirror the pipeline to the
   "Job Hunt" Notion database (upsert each `python -m src.query crm` row, matching on Company+Role;
   do NOT clobber human-progressed `applied`/`screen`/`interview`/`offer`/`rejected`/`declined`
   statuses or curated notes). Keep the database view sorted by Match. Then **star EXACTLY the 5
   jobs whose Status is `shortlisted` with the highest Match** (set the ⭐ page icon on those 5,
   remove it from every other row so exactly those 5 are starred). These 5 can include shortlisted
   jobs from earlier sessions, not only ones from this discover run. Break ties in favor of the more
   AI-forward or better-located role. Report the 5 starred (company, role, match).

4. **Research the 5 starred**: for each of the 5, delegate to the **company-researcher** subagent
   (Sonnet) to write `research/companies/<slug>.md`. Resolve each path with
   `python -m src.research get <job_id>`; skip the research if a fresh dossier already exists.

5. **Tailor the 5 starred**: for each of the 5 (all `shortlisted`), run the `/jh-tailor` flow: load
   the job (`python -m src.query job <id>`), pass its company dossier from step 4, and delegate to
   the **resume-tailor** subagent to write `applications/pending/<company>-<id>/` (tailored resume, cover
   letter, match report) and render the one-page .docx. If a current application folder already
   exists for that job, refresh it rather than duplicating.

6. **Report**: the 5 starred jobs with their dossier paths and tailored application paths, the
   strongest hook and honest gaps for each, and anything I should confirm before applying.

Guardrails: only star, research, and tailor jobs with `shortlisted` status. Never fabricate resume
or company facts. Zero em-dashes anywhere. These outputs are DRAFTS to review; never auto-submit,
a human clicks submit. SQLite is canonical; Notion is the mirror.
