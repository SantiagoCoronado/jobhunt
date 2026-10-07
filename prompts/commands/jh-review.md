---
description: 'Monthly feedback loop: measure conversion, audit triage, propose profile/rubric tweaks'
tools: [read, bash, glob]
---

Review how the job hunt is actually converting and propose evidence-based tuning.
Numbers come from deterministic SQL, never estimate them yourself.

1. **Collect the numbers** with Bash:
   - `python -m src.stats funnel`        (conversion by stage, score band, title family, source)
   - `python -m src.stats calibration`   (do 90s convert better than 75s?)
   - `python -m src.stats latency`       (applied -> first response, from the event log)
   - `python -m src.stats drops --sample 15`  (triage false-drop audit)
   - `python -m src.stats comp --min-score 70` (salary landscape of good matches)
   - `python -m src.stats hunts --last 5`  (the last hunt runs: units, retries, failures and
     usage per stage, from the ledgers; a stage that grew or started retrying is drift)
   - `python -m src.report`  (regenerates `data/report.html`, the visual companion to
     these numbers; mention its path in the report)

2. **Audit the drop sample**: read each sampled drop's company+title+reason. Any that a
   human would clearly have kept is a false drop; name it and say which rubric line
   failed. The triage rubric lives in `prompts/agents/triager.md`.

2b. **Quarterly**: check the newest `research/upskill/*-plan.md`. If it is 3+ months
   old (or absent), suggest running `/jh-upskill`; if newer, note whether the market
   gaps it names have shifted given the current funnel.

3. **Mine the debriefs**: scan `interviews/*/debrief-*.md` (if any). Recurring themes:
   questions seen 3+ times (answer-bank candidates), answers repeatedly marked weak
   (rehearsal list), companies/round-types where I underperform.

4. **Interpret honestly**, with counts next to every rate (n=4 is an anecdote, not a
   trend): which score bands / title families / sources actually get responses; whether
   the matcher's 90s outperform its 70s (if not, the rubric is miscalibrated); whether
   any source produces applications but never responses.

5. **Propose concrete edits, as diffs I approve**, never self-applied:
   - `config/profile.yaml` (weights, titles, dealbreakers, threshold)
   - `prompts/agents/job-matcher.md` rubric lines
   - `prompts/agents/triager.md` rubric lines
   Each proposal: the evidence line it rests on, the exact edit, the expected effect.

6. **Report**: one screen: funnel headline, calibration verdict, top 3 proposed edits,
   false drops found, comp takeaway. Zero em-dashes.
