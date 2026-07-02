---
description: Score newly discovered jobs against your profile
allowed-tools: Read, Write, Bash
---

Score the pending jobs against my profile.

1. First export the queue: run `python -m src.match export --limit 40` with Bash.
2. Delegate scoring to the **job-matcher** subagent (it reads `config/profile.yaml` and
   `data/pending_match.json`, writes `data/scores.json`, and ingests the scores).
3. Show me a table of the top matches (score, title, company, recommendation, why) and how
   many were shortlisted.

Be calibrated, I want the ~10-20% genuinely worth tailoring for, not a wall of 90s.
