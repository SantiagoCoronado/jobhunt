---
description: Full job-hunt pipeline end to end under the hunt orchestrator: discover, triage, match, inbox pull, pick the top 5 shortlisted, research + tailor those 5, report. Usage: /jh-hunt
allowed-tools: Bash
---

Run my whole job hunt. The orchestrator (`python -m src.hunt`, `docs/spec-hunt-orchestrator.md`)
does the work: one process per unit of model work on the harness and models in
`config/hunt.toml`, a ledger under `data/hunt/<run>/`, retries, coverage checks and the DB
writes. You are the viewer: do not start agents yourself, do not read the hunt's files;
every token you spend here is one the hunt did not need. Use `.venv/bin/python` if plain `python` is not on PATH.

1. **Start it**: run `python -m src.hunt run` with your shell tool, in the background if your
   shell tool can (a hunt runs for many minutes). If the last run stopped early (a failed stage, Ctrl+C, a dead session),
   continue it with `python -m src.hunt run --resume latest` instead of starting a new one:
   finished units are skipped and nothing is exported or scored twice. "another hunt holds
   the lock" means one is already running; go to step 2.

2. **Watch it**: `python -m src.hunt status latest`, at most once every two minutes, and relay
   the tree: the stage that is running, units done of total, any unit on a retry and why.
   Do not tail logs or open the ledger yourself; `status` shows the last log line of every
   running unit.

3. **Report**: when the background command exits, run `python -m src.hunt report latest` and
   present what it prints: what each stage did, the 5 picks with their dossier and application
   paths, each build's RESUME and LETTER lines, the visa path and relocation line on dream
   rows, the `needs_human` list and the usage table. Lead with `needs_human`: those are the
   questions the run could not ask (an inbox line naming another role or company, an
   aggregator row with no resolvable employer, a build that failed its fix round).
   Exit 0 is a finished hunt, 3 means the pick found nothing to tailor, 2 means a stage
   failed: say which one from the report and offer `--resume latest`.

`python -m src.hunt doctor` checks the harness, every stage's model and the tool grants
before a hunt; `python -m src.hunt run --only <stage>` or `--from A --to B` runs a slice.

Guardrails, enforced by the orchestrator and restated for you: only `shortlisted` jobs are
picked, researched and tailored; only Python writes the DB; human-progressed statuses are never
overwritten; resume and company facts are never fabricated; zero em-dashes anywhere. The outputs
are DRAFTS to review; nothing is ever submitted, a human clicks submit. SQLite is canonical.
