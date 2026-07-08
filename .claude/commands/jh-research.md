---
description: Research a company into a reusable, cited dossier. Usage: /jh-research <company | job_id>
argument-hint: <company | job_id>
allowed-tools: Read, Write, Bash, WebSearch, WebFetch
---

Research the company for **$ARGUMENTS** and write a reusable dossier.

1. Resolve the target:
   - If **$ARGUMENTS** is a numeric job id, run `python -m src.query job $ARGUMENTS` with Bash to
     get the company name and the job description (extra grounding for what they value).
   - Otherwise treat **$ARGUMENTS** as a company name directly.
   - Get the dossier path with `python -m src.research path "<company>"`. If it already exists and
     still looks fresh, reuse or refresh it rather than starting over. (Use `--refresh` intent in
     your request if I explicitly ask to rebuild stale news.)
2. Delegate to the **company-researcher** subagent with the company name, the job description (if
   from a job id), `config/profile.yaml`, and `resume/master_resume.yaml`. It writes the dossier
   to `research/companies/<company-slug>.md` (all four areas: mission & product, culture & voice,
   recent news, engineering & AI), with cited Sources and zero em-dashes.
3. Report where the dossier landed and summarize this company's Core narrative and the single
   strongest hook for my application.

The dossier is comprehensive, but cover letters and answers should lean into the company's
specific narrative, not checklist every section. This is a DRAFT to review. Once it exists,
`/jh-tailor <id>` will automatically weave it into the cover letter. Never fabricate company facts.
