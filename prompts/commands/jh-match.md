---
description: Score newly discovered jobs against your profile, run by the hunt orchestrator
tools: [bash]
---

Score the pending jobs against my profile. The hunt orchestrator does the work (`python -m
src.hunt`, `docs/spec-hunt-orchestrator.md`): it exports the best-bucket rows into chunks, runs
one job-matcher process per chunk on the harness and model in `config/hunt.toml` (the rubric is
`prompts/agents/job-matcher.md`), checks that every scores file covers every id, retries the
short ones and ingests (the shortlist cutoff comes from `config/profile.yaml`). You are the
viewer: do not start agents, read chunks or write scores yourself. Use `.venv/bin/python` if
plain `python` is not on PATH.

1. **Start it**: run `python -m src.hunt run --only match` with your shell tool, in the
   background if your shell tool can (it runs for many minutes). If the last run stopped early,
   continue it with `python -m src.hunt run --resume latest` instead: finished chunks are
   skipped and nothing is exported or scored twice. "another hunt holds the lock" means a run
   is already going; go to step 2.

2. **Watch it**: `python -m src.hunt status latest`, at most once every two minutes, and relay
   the units done of total and any unit on a retry and why. Do not tail logs or open the ledger.

3. **Report**: when the command exits, run `python -m src.hunt report latest` and relay the
   match line: how many were scored and how many were shortlisted, and any failed chunk. Exit 2
   means a chunk failed: offer `python -m src.hunt run --resume latest`.

How many units one run plans is `budget_units` in `config/hunt.toml`; the floor bucket is
`min_bucket`. I want the ~10-20% genuinely worth tailoring for, not a wall of 90s: if the
shortlist looks inflated, say so and suggest `/jh-review`.
