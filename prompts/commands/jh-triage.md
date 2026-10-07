---
description: Coarse Haiku junk-cut of discovered jobs before the expensive matcher
tools: [bash, agent, write, read]
---

Cheaply triage newly discovered jobs so the real matcher (`/jh-match`) only spends tokens on
plausibly-relevant roles. Haiku does a keep/drop junk cut against the profile dealbreakers; drops
land at `status='irrelevant'` (gone from every future stage) and keepers carry a 0-3 fit bucket
that later orders scoring. Run this after `/jh-discover` when the discovered pile is large.

1. Export the queue into chunks:
   `python -m src.triage export --chunk 100`
   (untriaged `discovered` jobs, deduped by `canonical_key`, into `data/triage/chunk_NNN.json`).
   Note the chunk count.

2. For EACH `chunk_NNN.json`, delegate to a **Haiku** sub-agent (model: haiku) that reads the chunk,
   applies the RUBRIC below, and writes `data/triage/out_NNN.json` as
   `[{"id": <int>, "keep": true|false, "reason": "<=8 words", "bucket": 0-3}]` with every input id
   exactly once. Run them in parallel. For a large sweep (more than ~10 chunks), drive them with a
   **Workflow** so they fan out under a concurrency cap and are resumable; hardcode the chunk count
   in the script (passing it via `args` has been unreliable).

   RUBRIC: the rubric is the body of `prompts/agents/triager.md` (the same system prompt the
   hunt orchestrator gives the triage units; `.claude/agents/triager.md` is generated from it).
   Read that file ONCE, and open every sub-agent prompt with the candidate block: run
   `python -m src.config candidate` ONCE with Bash before spawning and paste its output verbatim
   (it renders `candidate_line`, the lettered `role_families` with their titles and skills, the
   strongest families, and the `work_authorization` summary from `config/profile.yaml`; never
   restate them by hand), then the rubric, then the chunk and output file names.

3. Verify every chunk has a complete out file (ids match its chunk), re-running any that fell short.

4. Ingest: `python -m src.triage ingest`  (drops become `status='irrelevant'`; keepers are marked and
   still flow to `/jh-match`). Report kept vs dropped and the bucket split.

Next: `/jh-match` scores the survivors, now ordered by fit bucket (best first). For a deep scaled
pass, `python -m src.match export --min-bucket 3 --chunk 60 --limit 0`, fan the **job-matcher** over
`data/match/chunk_*.json` (write `data/match/scores_NNN.json` each), then
`python -m src.match ingest --dir data/match` (shortlist cutoff comes from profile.yaml
`shortlist_threshold`).

For a batch, `python -m src.hunt run --only triage` runs this stage under the hunt orchestrator (ledger, retries, coverage checks, `--resume`); this prose flow is for a single interactive use.
