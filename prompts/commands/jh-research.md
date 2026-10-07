---
description: 'Research a company into a reusable, cited dossier. Usage: /jh-research <company | job_id>'
argument-hint: <company | job_id>
tools: [read, write, bash, web]
---

Research the company for **$ARGUMENTS** and write a reusable dossier.

1. Resolve the target:
   - If **$ARGUMENTS** is a numeric job id, run `python -m src.query job $ARGUMENTS` with Bash to
     get the company name and the job description (extra grounding for what they value).
   - Otherwise treat **$ARGUMENTS** as a company name directly.
   - Get the dossier path with `python -m src.research path "<company>"` (for a job id,
     `python -m src.research get <id>` also prints `exists`/`researched`/`stale`). If it exists
     and `stale: False`, reuse it rather than starting over; if `stale: True`, refresh it in
     place (keep the file, update facts and the `researched:` date line). Always end the dossier
     with a `researched: YYYY-MM-DD` line; that line is what makes staleness deterministic.
2. Delegate to the **company-researcher** subagent with the company name, the job description (if
   from a job id), `config/profile.yaml`, and `resume/master_resume.yaml`. It writes the dossier
   to `research/companies/<company-slug>.md` (all four areas: mission & product, culture & voice,
   recent news, engineering & AI), with cited Sources and zero em-dashes.
3. Report where the dossier landed and summarize this company's Core narrative and the single
   strongest hook for my application.

The dossier is comprehensive, but cover letters and answers should lean into the company's
specific narrative, not checklist every section. This is a DRAFT to review. Once it exists,
`/jh-tailor <id>` will automatically weave it into the cover letter. Never fabricate company facts.

For a batch, `python -m src.hunt run --only research` runs this stage under the hunt orchestrator (ledger, retries, coverage checks, `--resume`); this prose flow is for a single interactive use.
