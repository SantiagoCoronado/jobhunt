---
description: 'Digest an interview transcript into a debrief, prep notes, and answer-bank updates. Usage: /jh-debrief <job_id> [transcript_path]'
tools: [read, write, bash, glob]
---

Digest my interview for job **$ARGUMENTS** into durable learning.

Transcript convention: I record the interview (checking consent/legality is MY job,
not yours; treat the transcript as lawfully obtained input) and drop the text at
`interviews/<company>-<id>/<YYYY-MM-DD>-<round>.md` (e.g. `2026-07-20-screen.md`).

1. **Load context**: `python -m src.query job <id>` with Bash; the transcript (the
   path if given, else the newest `interviews/*-<id>/*.md` that has no matching
   `debrief-*` file); the tailored materials in `applications/*/<company>-<id>/`;
   the dossier via `python -m src.research get <id>`.

2. **Extract** from the transcript:
   - Every question asked, as a list (paraphrase long ones).
   - How each of my answers landed: strong / adequate / weak, with one line on why
     (rambled, missed the point, great story, etc.). Be honest; flattery wastes the loop.
   - Factual commitments I made ("can start in August", "comfortable with X").
   - What the interviewer revealed: team, stack, process, comp hints, next steps.
   - Signals and red flags, both directions.

3. **Write the debrief** to `interviews/<company>-<id>/debrief-<date>.md`: the
   extraction above plus a "before the next round" section (weak answers to rehearse,
   questions I should ask next time, facts to verify). Summarize the interviewer's
   words; do NOT quote them at length.

4. **Update the answer bank** (`resume/answers.yaml`): for questions not already
   covered, add an entry with `draft: true` and a proposed answer built from what I
   actually said (improved phrasing is fine, new claims are not; ground everything in
   `resume/master_resume.yaml`). For existing entries where my live answer landed
   better than the bank's, propose the improvement the same way. I review drafts;
   you never flip draft to false.

5. **Record it**: `python -m src.query event <id> debrief --note "<round>: <one-line outcome>"`,
   `python -m src.query touch <id> --date <interview-date>`, and if the round moved the
   pipeline (e.g. invited onward, or rejected), `python -m src.query set-status <id> <status>`.

6. **Report**: 5-line summary: how it went, the 2 weakest answers, the strongest moment,
   next step and its date.

Privacy guardrails: `interviews/` is git-ignored and must stay local; transcripts hold
other people's words and possibly confidential company information. Never copy transcript
content into committed files (dossiers, answers.yaml keep only MY answers and public
facts). Zero em-dashes in everything you write.
