---
description: 'Tailor resume + cover letter for a job. Usage: /jh-tailor <job_id>'
argument-hint: <job_id>
tools: [read, write, bash]
---

Tailor my application for job id **$ARGUMENTS**.

1. **Bundle**: run `python -m src.tailor_bundle $ARGUMENTS` with Bash (`.venv/bin/python` if
   plain `python` is not on PATH). It writes `data/tailor/$ARGUMENTS/inputs.md` with every
   input the subagent needs (voice rules, profile, master resume, page geometry, the job with
   its dream flag, the dossier, the pre-rendered answers) and prints one line
   with the folder, the dream flag, the dossier name and whether it is stale. That line is all
   you need; do NOT run `src.query job`, `src.research get` or `src.answers_export` yourself.
   Aggregator rows (HN "Who is Hiring", Jobgether): add `--company <Employer>` and, when the
   dossier lives under another slug, `--dossier research/companies/<slug>.md`.
   If the line says `dossier=none`, suggest `/jh-research $ARGUMENTS` first (non-blocking).

2. **Delegate** to the **resume-tailor** subagent with `model: "fable"` (it is pinned to Fable
   in its definition; pass it explicitly too). The prompt is two lines:
   `Tailor job $ARGUMENTS. Bundle: data/tailor/$ARGUMENTS/inputs.md. Folder: <folder from step 1>.
   Dream: <yes/no>. Reply in at most 80 words.`
   The agent reads the bundle once, writes `<folder>/draft.md` once, runs
   `python -m src.tailor_build <folder>` once (plus at most one fix round), and replies.
   Deliverables: `<NameParts>Resume.{yaml,docx,pdf}` (stem from `profile.name`, printed in the bundle), `CoverLetter.{md,docx,pdf}`,
   `match_report.md`, `answers.md`, plus `build.json` and `state.json` for the record.

3. **Summarize** from the agent's reply. If it lacks the fill line, run
   `python -m src.tailor_build <folder> --json` once and take `metrics` from it. Report the fit
   level and fill, the page count, the hook used, the ATS keywords woven in, and, honestly, any
   requirement I am missing that I should be ready to speak to.

Never fabricate experience. Only reframe what is in my master resume. Remind me this is a DRAFT
to review before I submit anything myself.

For a batch, `python -m src.hunt run --only tailor` runs this stage under the hunt orchestrator (ledger, retries, coverage checks, `--resume`); this prose flow is for a single interactive use.
