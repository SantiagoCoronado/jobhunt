---
description: Tailor resume + cover letter for a job. Usage: /jh-tailor <job_id>
argument-hint: <job_id>
allowed-tools: Read, Write, Bash
---

Tailor my application for job id **$ARGUMENTS**.

1. Load the job: run `python -m src.query job $ARGUMENTS` with Bash.
2. Check for a company dossier: run `python -m src.research get $ARGUMENTS` with Bash. If it
   reports `exists: True`, pass that dossier file to the subagent so the cover letter can weave in
   the most resonant, company-specific hook. If it does not exist, proceed without it and suggest
   running `/jh-research $ARGUMENTS` first for a sharper letter (non-blocking).
3. Delegate to the **resume-tailor** subagent with that job, `resume/master_resume.yaml`,
   `config/profile.yaml`, and the company dossier if present. It writes the tailored resume, cover
   letter, and match report into `applications/pending/<company>-$ARGUMENTS/`, then renders the one-page
   .docx (house design) via
   `python -m src.render_docx applications/pending/<company>-$ARGUMENTS/tailored_resume.yaml --pdf`.
4. Summarize: the fit, the ATS keywords woven in, the company hook used (if a dossier was
   present), and, honestly, any requirement I'm missing that I should be ready to speak to.

Never fabricate experience. Only reframe what's actually in my master resume. After it's done, remind
me this is a DRAFT to review before I submit anything myself.
