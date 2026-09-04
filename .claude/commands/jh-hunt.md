---
description: Full job-hunt pipeline end to end: discover, triage, match, inbox pull, pick top 5 shortlisted, research + tailor those 5, refresh the report. Usage: /jh-hunt
allowed-tools: Read, Write, Bash, WebSearch, WebFetch
---

Run my whole job hunt end to end. Do the phases in order and give me a short report after each.
Use `.venv/bin/python` if plain `python` is not on PATH.

1. **Discover** (the `/jh-discover` flow): run `python -m src.discover` with the Bash tool
   **in the background** (run_in_background: true); a full sweep is hundreds of sequential HTTP
   calls and blows past the default 2-minute Bash timeout. Wait for it to finish, then report
   how many new jobs landed and flag any source marked FAILED.

2. **Triage if the pile is large**: count the unscored pile with
   `.venv/bin/python -c "from src.db import connect; print(connect().execute(\"SELECT COUNT(DISTINCT canonical_key) FROM jobs WHERE status='discovered' AND match_score IS NULL AND match_verdict IS NULL\").fetchone()[0])"`
   (never `python -m src.query crm` for this; on a mature DB that is a 90k-token dump).
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
   Dream-company rows (`dream: true`, from `dream_companies` in profile.yaml) sort first in
   every export and shortlist at `dream_shortlist_threshold`; report them as their own line.

4. **Inbox pull** (the `/jh-gmail-sync` flow): run `python -m src.mail_fetch`, classify
   the printed legend + manifest (use `show <id>` for unsettled lines; never read
   `data/mail_*`, never `query crm` or `query job` inside this step), write
   `data/gmail_pull.json` as `/jh-gmail-sync` step 5 says (one `{manifest_id, sweep, signal,
   proposed_status}` object per line, the `sweep` stamp copied from the fetcher's output; the
   applier fills the headers and ids from the manifest, so never write `evidence` yourself on
   this path), run the dry run, present the batch inline, and apply only after my approval. This runs BEFORE the pick so the top 5 are picked against email-fresh
   statuses (a company that rejected or advanced me this week must be reflected first).
   If mail_fetch reports no configured accounts and the Gmail tools are unavailable, note
   it and continue; the hunt never blocks on this step.

5. **Pick 5** (no Notion; dropped 2026-09-02, it was the single largest token sink of every
   hunt): run `python -m src.pick` with Bash. It prints the 5 `shortlisted` targets under the
   star rule: first up to 2 slots go to the highest-Match shortlisted rows with `dream: true`
   (one per company), then the remaining slots to the highest-Match shortlisted rows overall,
   one per company, skipping any company that already has an application folder or a
   human-progressed row. It also lists what it skipped and flags aggregator rows (Jobgether,
   HN "Who is Hiring") whose real employer you must confirm before research; drop a flagged
   row you cannot resolve and take the first spare (it prints two spares after the picks).
   Rows listed as "not scored yet" are hand-shortlisted and need `/jh-match` before a pick. These 5 can include shortlisted jobs from
   earlier sessions. Never `python -m src.query crm` here (a 90k-token dump on a mature DB).
   Report the 5 picked (company, role, match, dream or not).

6. **Research the 5 picked**: for each of the 5, delegate to the **company-researcher** subagent
   (Sonnet) to write `research/companies/<slug>.md`. Resolve each with
   `python -m src.research get <job_id>`; skip the research when it reports `stale: False`,
   refresh in place when `stale: True`.

7. **Tailor the 5 picked**: run `python -m src.tailor_bundle <id>` for all 5 in ONE Bash call
   (add `--company` / `--dossier` for aggregator rows); each prints its folder, dream flag and
   dossier state. Then spawn the 5 **resume-tailor** subagents in ONE message, each with
   `model: "fable"` and the two-line prompt: `Tailor job <id>. Bundle:
   data/tailor/<id>/inputs.md. Folder: <folder>. Dream: <yes/no>. Reply in at most 80 words.`
   Each agent reads its bundle once, writes `<folder>/draft.md` once, runs
   `python -m src.tailor_build <folder>` (at most one fix round) and replies in 80 words. Do
   NOT run `src.query job`, `src.research get` or `src.answers_export` here; the bundle did.
   An existing folder for the job is refreshed in place (the bundle carries the old draft).
   After the replies, run `python -m src.tailor_build <folder> --json` only for an agent whose
   reply lacks the fill line. Then `python scripts/token_audit.py --latest` and keep its
   per-agent lines for the report.

8. **Report**: run `python -m src.report` (regenerates `data/report.html`, free and
   deterministic; include its path and headline line), then the 5 picked jobs with their
   dossier paths and tailored application paths, each build's RESUME and LETTER verdict lines
   (from the agent reply or `build.json`), the strongest hook and honest gaps for each, anything
   I should confirm before applying, and the token audit totals (context tokens and API calls
   per stage, so drift is visible next time). For a dream-company job also state
   the matcher's `visa_path` and whether the cover letter carries the relocation line.

Guardrails: only pick, research, and tailor jobs with `shortlisted` status. Never overwrite
human-progressed statuses (`applied`/`screen`/`interview`/`offer`/`rejected`/`ghosted`/`withdrawn`)
or curated notes; record status changes only via `python -m src.query set-status`. Never fabricate
resume or company facts. Zero em-dashes anywhere. These outputs are DRAFTS to review; never
auto-submit, a human clicks submit. SQLite is canonical.
