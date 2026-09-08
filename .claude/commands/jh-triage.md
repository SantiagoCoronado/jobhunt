---
description: Coarse Haiku junk-cut of discovered jobs before the expensive matcher
allowed-tools: Bash, Task, Write, Read
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

   RUBRIC (keep-on-doubt: this is a junk cut, NOT the final judge; when in any doubt, KEEP):
   Open the rubric with the candidate block: run `python -m src.config candidate` ONCE with Bash
   before spawning and paste its output verbatim here (it renders `candidate_line`, the lettered
   `role_families` with their titles and skills, the strongest families, and the
   `work_authorization` summary from `config/profile.yaml`; never restate them by hand).
   Every listed family is IN scope; bucket good fits in the families it marks STRONGEST 2-3.
   Director/Lead/Manager/Strategist titles are IN scope.
   DROP (keep=false) ONLY if clearly one of: (1) OFF-FIELD (not software/AI/data/ML/frontend/internal
   -tools engineering AND not an AI deployment/solutions/enablement/strategy or technical
   product/program role): nurse,
   accountant, non-technical sales/account executive, customer success, recruiter/HR, marketing,
   finance, legal, admin, mechanical/civil/chemical/electrical/manufacturing engineering, retail;
   (2) requires an active security clearance OR citizenship of a specific country the candidate
   block does not claim; (3) base salary EXPLICITLY listed
   and, ONCE ANNUALIZED, clearly below `comp.min_usd_latam_scope` in `config/profile.yaml`.
   Annualize first: a USD figure under 20,000 is a MONTHLY rate, multiply by 12 (a "5,000-7,000
   USD" getonbrd row is 60k-84k/yr, not 5k-7k/yr). Never drop a monthly rate as if it were annual.
   NEVER drop for location, city, on-site, hybrid, remote, or country. Location is judged later with
   the full JD. Give each KEPT job a bucket 0-3 (0 weak, 1 plausible, 2 good, 3 strong fit).
   DREAM COMPANIES: a row carrying `"dream": true` is at one of `dream_companies` in
   `config/profile.yaml` (its `dream_rule` is the authority). For those rows rule (3) (pay) does
   NOT apply and location never did; rules (1) off-field and (2) clearance / citizens-only /
   export-control ("US person", ITAR) still drop. When in doubt on a dream row, keep it and
   bucket honestly.

3. Verify every chunk has a complete out file (ids match its chunk), re-running any that fell short.

4. Ingest: `python -m src.triage ingest`  (drops become `status='irrelevant'`; keepers are marked and
   still flow to `/jh-match`). Report kept vs dropped and the bucket split.

Next: `/jh-match` scores the survivors, now ordered by fit bucket (best first). For a deep scaled
pass, `python -m src.match export --min-bucket 3 --chunk 60 --limit 0`, fan the **job-matcher** over
`data/match/chunk_*.json` (write `data/match/scores_NNN.json` each), then
`python -m src.match ingest --dir data/match` (shortlist cutoff comes from profile.yaml
`shortlist_threshold`).
