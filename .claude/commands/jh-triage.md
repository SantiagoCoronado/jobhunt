---
description: Coarse Haiku junk-cut of discovered jobs before the expensive matcher
allowed-tools: Bash, Task, Write, Read
---

Cheaply triage newly discovered jobs so the real matcher (`/jh-match`) only spends tokens on
plausibly-relevant roles. Haiku does a keep/drop junk cut against the profile dealbreakers; drops
land at `status='irrelevant'` (gone from every future stage) and keepers carry a 0-3 fit bucket
that later orders scoring. Run this after `/jh-discover` when the discovered pile is large.

1. Export the queue into chunks:
   `python -m src.triage export --chunk 200`
   (untriaged `discovered` jobs, deduped by `canonical_key`, into `data/triage/chunk_NNN.json`).
   Note the chunk count.

2. For EACH `chunk_NNN.json`, delegate to a **Haiku** sub-agent (model: haiku) that reads the chunk,
   applies the RUBRIC below, and writes `data/triage/out_NNN.json` as
   `[{"id": <int>, "keep": true|false, "reason": "<=8 words", "bucket": 0-3}]` with every input id
   exactly once. Run them in parallel. For a large sweep (more than ~10 chunks), drive them with a
   **Workflow** so they fan out under a concurrency cap and are resumable; hardcode the chunk count
   in the script (passing it via `args` has been unreliable).

   RUBRIC (keep-on-doubt: this is a junk cut, NOT the final judge; when in any doubt, KEEP):
   Candidate: Santiago, founder-engineer, Mexico City, bilingual ES/EN, TN-visa eligible for US work.
   Four role families, ALL in-scope: (A) hands-on AI / full-stack engineering (Applied AI / AI /
   Forward-Deployed / Founding / Full-Stack / Software Engineer; Python, JS/TS, React, Node, LLMs,
   RAG, AI agents, AWS, SQL); (B) AI deployment / enablement / strategy (Deployment Strategist,
   Solutions Architect/Engineer, AI Enablement/Transformation/Adoption Lead/Director/Manager, Applied
   AI Strategist, GTM engineer, technical PM/PgM for AI); (C) frontend engineering (Frontend / UI /
   React / Web Engineer; React, TypeScript, Electron); (D) internal tooling / internal platforms
   (Internal Tools, Developer Experience/Productivity, Business Systems, Workflow Automation
   Engineer). C and D are his two STRONGEST positions, bucket good ones 2-3.
   Director/Lead/Manager/Strategist titles are IN scope.
   DROP (keep=false) ONLY if clearly one of: (1) OFF-FIELD (not software/AI/data/ML/frontend/internal
   -tools engineering AND not an AI deployment/solutions/enablement/strategy or technical
   product/program role): nurse,
   accountant, non-technical sales/account executive, customer success, recruiter/HR, marketing,
   finance, legal, admin, mechanical/civil/chemical/electrical/manufacturing engineering, retail;
   (2) requires an active security clearance OR US-citizens-only; (3) base salary EXPLICITLY listed
   and clearly below 65,000 USD.
   NEVER drop for location, city, on-site, hybrid, remote, or country. Location is judged later with
   the full JD. Give each KEPT job a bucket 0-3 (0 weak, 1 plausible, 2 good, 3 strong fit).

3. Verify every chunk has a complete out file (ids match its chunk), re-running any that fell short.

4. Ingest: `python -m src.triage ingest`  (drops become `status='irrelevant'`; keepers are marked and
   still flow to `/jh-match`). Report kept vs dropped and the bucket split.

Next: `/jh-match` scores the survivors, now ordered by fit bucket (best first). For a deep scaled
pass, `python -m src.match export --min-bucket 3 --chunk 60 --limit 0`, fan the **job-matcher** over
`data/match/chunk_*.json` (write `data/match/scores_NNN.json` each), then
`python -m src.match ingest --dir data/match` (shortlist cutoff comes from profile.yaml
`shortlist_threshold`).
