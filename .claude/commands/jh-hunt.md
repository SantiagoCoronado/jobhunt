---
description: Full job-hunt pipeline end to end: discover, match, sync + star top 5 shortlisted, research + tailor those 5. Usage: /jh-hunt
allowed-tools: Read, Write, Bash, WebSearch, WebFetch, mcp__claude_ai_Notion__notion-search, mcp__claude_ai_Notion__notion-query-data-sources, mcp__claude_ai_Notion__notion-create-database, mcp__claude_ai_Notion__notion-create-pages, mcp__claude_ai_Notion__notion-update-page
---

Run my whole job hunt end to end. Do the phases in order and give me a short report after each.
Use `.venv/bin/python` if plain `python` is not on PATH.

1. **Discover** (the `/jh-discover` flow): run `python -m src.discover`. Report how many new jobs landed.

2. **Triage if the pile is large**: check the unscored pile with
   `python -m src.query crm` OR directly:
   `.venv/bin/python -c "from src.db import connect; print(connect().execute(\"SELECT COUNT(DISTINCT canonical_key) FROM jobs WHERE status='discovered' AND match_score IS NULL AND match_verdict IS NULL\").fetchone()[0])"`.
   If it is over ~200, run the full `/jh-triage` flow first (export chunks, fan Haiku
   sub-agents, ingest). Report kept vs dropped and the bucket split.

3. **Match** (the `/jh-match` flow), scaled when triage ran:
   - Triaged pile: `python -m src.match export --min-bucket 3 --chunk 60 --limit 0`, fan the
     **job-matcher** subagent over `data/match/chunk_*.json` (each writes `scores_NNN.json`),
     then `python -m src.match ingest --dir data/match` (cutoff from profile.yaml
     `shortlist_threshold`). If bucket-3 coverage
     leaves budget, repeat with `--min-bucket 2`.
   - Small untriaged pile: `python -m src.match export --limit 40`, one **job-matcher** pass
     (reads `config/profile.yaml` + `data/pending_match.json`, writes `data/scores.json`), ingest.
   Be calibrated. NEVER score with a bare keyword-prescore `--limit` when a triaged pile is
   waiting; the prescore buries well-phrased strong matches. Report how many were shortlisted.

4. **Sync + star** (the `/jh-notion-sync` flow, both phases): PULL Notion edits first
   (`python -m src.notion_pull data/notion_pull.json --apply` after exporting the decisive rows),
   then push the pipeline back (upsert `python -m src.query crm` rows; statuses map
   `withdrawn` -> `declined`, `backlog` -> `shortlisted`). Then **star EXACTLY the 5 jobs whose
   Status is `shortlisted` with the highest Match** (set the ⭐ page icon on those 5, remove it
   from every other row so exactly those 5 are starred). These 5 can include shortlisted jobs
   from earlier sessions, not only ones from this discover run. Break ties in favor of the more
   AI-forward or better-located role. Report the 5 starred (company, role, match).

5. **Research the 5 starred**: for each of the 5, delegate to the **company-researcher** subagent
   (Sonnet) to write `research/companies/<slug>.md`. Resolve each with
   `python -m src.research get <job_id>`; skip the research when it reports `stale: False`,
   refresh in place when `stale: True`.

6. **Tailor the 5 starred**: for each of the 5 (all `shortlisted`), run the `/jh-tailor` flow: load
   the job (`python -m src.query job <id>`), pass its company dossier from step 5, and delegate to
   the **resume-tailor** subagent to write `applications/pending/<company>-<id>/` (tailored resume, cover
   letter, match report) and render the one-page .docx. If a current application folder already
   exists for that job, refresh it rather than duplicating.

7. **Report**: the 5 starred jobs with their dossier paths and tailored application paths, the
   strongest hook and honest gaps for each, and anything I should confirm before applying.

Guardrails: only star, research, and tailor jobs with `shortlisted` status. Never overwrite
human-progressed statuses (`applied`/`screen`/`interview`/`offer`/`rejected`/`ghosted`/`withdrawn`)
or curated notes; record status changes only via `python -m src.query set-status`. Never fabricate
resume or company facts. Zero em-dashes anywhere. These outputs are DRAFTS to review; never
auto-submit, a human clicks submit. SQLite is canonical; Notion is the mirror.
