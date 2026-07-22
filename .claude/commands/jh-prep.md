---
description: Interview prep brief for a job in screen/interview stage. Usage: /jh-prep <job_id> [round]
allowed-tools: Read, Write, Bash, Glob, WebSearch, WebFetch
---

Build me an interview prep brief for job **$ARGUMENTS**.

1. **Load**: `python -m src.query job <id>` with Bash; the dossier via
   `python -m src.research get <id>` (if `stale: True`, refresh the time-sensitive
   facts first, /jh-research flow, before citing news); the tailored resume + cover
   letter in `applications/*/<company>-<id>/`; `resume/master_resume.yaml`;
   `resume/answers.yaml` (non-draft entries).

2. **Mine past learning**:
   - Earlier rounds at THIS company: `interviews/<company>-<id>/debrief-*.md`, their
     "before the next round" sections are the priority list.
   - Similar roles elsewhere: scan `interviews/*/debrief-*.md` for debriefs whose job
     shares the title family; collect questions that appeared more than once.

3. **Write** `applications/<bucket>/<company>-<id>/prep-<round-or-date>.md`:
   - **Likely questions**: from the JD's requirements, the recurring questions found in
     step 2, and this round's format. For each: the angle to take, in one line.
   - **My stories**: 4-6 STAR-shaped stories mapped to the JD's top requirements, built
     ONLY from `master_resume.yaml` facts (cite which experience each comes from).
   - **Weak spots**: gaps the matcher flagged (`match_verdict`) and weak answers from
     past debriefs, each with a prepared honest response, never a fabricated one.
   - **Questions to ask them**: 5-6 specific ones grounded in the dossier (product,
     team, roadmap), not generic filler.
   - **Company snapshot**: 5 lines from the dossier: what they do, stage/funding,
     recent news, why-me hook, comp intel if any (include `python -m src.stats comp`
     context when salary talk is likely).

4. Log it: `python -m src.query event <id> note --note "prep brief written for <round>"`.
   Report the brief's path and the single most important thing to rehearse.

Never fabricate experience. Zero em-dashes. The brief is for MY eyes; keep it blunt.
