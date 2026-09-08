---
description: Skill-gap analysis vs the market being applied to; learning plan for real gaps, profile diffs for vocabulary gaps. Usage: /jh-upskill [job_id]
argument-hint: "[job_id]"
allowed-tools: Read, Write, Bash, WebSearch, WebFetch
---

Analyze my skill gaps **$ARGUMENTS** (fleet mode when no job id is given).

The first question for every gap is always: is this a REAL skill gap, or a
PROFILE-VOCABULARY gap (a skill I have that `config/profile.yaml` does not list)?
Vocabulary gaps become proposed profile diffs; only real gaps get a learning plan.

1. **Extract the numbers** with Bash: `python -m src.gaps --json` (fleet) or
   `python -m src.gaps --job <id> --json`. Never estimate counts yourself; the
   ranked terms, job counts, and responded rates come from this output only.

2. **Load the evidence base**: `config/profile.yaml` AND `resume/master_resume.yaml`.

3. **Classify each top gap term** (work down the matcher_missing list first, it is
   LLM-judged; use description_gaps as the secondary sweep):
   - **vocabulary gap**: defensible evidence exists in the master resume -> propose a
     `config/profile.yaml` addition as a diff I approve, citing the master-resume
     line it rests on. Same contract as /jh-review: never self-applied.
   - **real gap**: no defensible evidence -> candidate for the learning plan.
   - **noise**: irrelevant to my four title families -> discard with one line saying why.

4. **For the top 5 real gaps**: WebSearch 2-3 current resources each, free first
   (official docs, courses, build-a-thing projects), with an honest hours estimate
   and a "provable by" milestone (a repo, a cert, a demo). A gap counts as closed
   only when it is interview-defensible, not when a video was watched.

5. **Write the output**:
   - Fleet mode: `research/upskill/<YYYY-MM>-plan.md` (committed, like dossiers):
     gap table with counts next to every rate, the vocabulary-gap diffs, the
     learning plan, Sources section with citations.
   - Per-job mode: `applications/<bucket>/<company>-<id>/upskill.md` (find the
     folder with Glob `applications/*/<company>-<id>`; it is gitignored with the
     rest of applications/): that JD's gaps, honest bridge lines for each, and
     what to rehearse. `/jh-prep` folds this file into its Weak spots section.

6. **Report** one screen: top 3 real gaps with counts, top 3 vocabulary diffs,
   the single highest-leverage thing to learn next and why (evidence line).

HARD RULE (CLAUDE.md): the learning plan NEVER feeds resume or answer-bank
content. A skill enters `master_resume.yaml` only after the candidate actually
learns it and can prove it, by their own hand. Voice rules per `docs/writing-voice.md`;
zero em-dashes; small n is an anecdote, print the n.
