---
description: Tailor resume + cover letter for a job. Usage:/tailor <job_id>
argument-hint: <job_id>
allowed-tools: Read, Write, Bash
---

Tailor my application for job id **$ARGUMENTS**.

1. Load the job: run `python -m src.query job $ARGUMENTS` with Bash.
2. Delegate to the **resume-tailor** subagent with that job, `resume/master_resume.yaml`, and
   `config/profile.yaml`. It writes the tailored resume, cover letter, and match report into
   `applications/<company>-$ARGUMENTS/`.
3. Summarize: the fit, the ATS keywords woven in, and, honestly, any requirement I'm missing
   that I should be ready to speak to.

Never fabricate experience. Only reframe what's actually in my master resume. After it's done, remind
me this is a DRAFT to review before I submit anything myself.
