# Scaling the scorer: triage cascade + bucket-ordered scoring

## The problem
Discovery pulls thousands of jobs (8k+ unique after dedupe), but the LLM `job-matcher` is expensive,
so `match export --limit N` only ever fed it the top N by a dumb keyword prescore (substring hits).
Everything else stayed unscored, and a genuinely good role phrased without the exact skill keywords
got buried below the cutoff and never judged.

## The fix: a two-stage cascade
A cheap coarse pass shrinks the pile so the expensive pass can cover all of what survives.

### Stage 1: coarse triage (Haiku, ~$0 on the Claude Code plan) — `src/triage.py`, `/jh-triage`
Junk cut only. A Haiku sub-agent judges each job **keep/drop** against the profile dealbreakers,
biased hard toward keep (keep-on-doubt). Drops go to `status='irrelevant'` and leave every future
stage. Keepers get a **0-3 fit bucket** stored in `match_verdict` (0 weak … 3 strong).

- `python -m src.triage export --chunk 200` → `data/triage/chunk_NNN.json` (untriaged `discovered`
  jobs, deduped by `canonical_key`).
- Fan one Haiku sub-agent per chunk (a Workflow for a full sweep; ~40 agents under a concurrency
  cap, resumable). Each writes `data/triage/out_NNN.json` = `[{id, keep, reason, bucket}]`.
- `python -m src.triage ingest` → drops become `irrelevant`; keepers marked, still flow to match.

**Rubric = 3 hard drops only:** off-field role; clearance/US-citizens-only; salary listed and below
the floor. **Location is NOT a triage criterion** — a coarse pass cannot tell "on-site only" from
"HQ city listed but remote OK," and dropping on a bare city label nukes remote-friendly target roles
(this was found and fixed live: an early version dropped ~50 Anthropic/OpenAI SF/NYC engineering
roles on the word "San Francisco"). Location is judged in Stage 2 with the full JD.

### Stage 2: real scoring over survivors, best bucket first — `src/match.py`, `job-matcher`
`match export` now orders by triage bucket (desc) then keyword prescore, and takes `--min-bucket`
and `--chunk` for a fanned-out pass:

```
python -m src.match export --min-bucket 3 --chunk 60 --limit 0   # strong bucket -> data/match/chunk_*.json
# fan job-matcher (Sonnet) over each chunk -> data/match/scores_NNN.json
python -m src.match ingest --dir data/match       # merge all scores; cutoff = profile.yaml shortlist_threshold
```

The `job-matcher` rubric applies the location rule from `config/profile.yaml`'s `location_rule`
key, which is the single authority on location (this doc intentionally does not restate it).

## Reference numbers (2026-07-08 run)
Discovered 8,157 unique → triage kept 5,015 (62%), dropped 3,053 off-field. Strong bucket = 1,038
unique, scored on Sonnet → 324 shortlisted (>=70), well calibrated (36 at 90+, 741 below 60). Both
profile-flagged "ideal" roles (ElevenLabs Deployment Strategist, Backblaze AI Enablement Director
LATAM) surfaced at the top. Haiku sweep ~2.65M tokens; Sonnet scoring ~1.95M tokens.

## Gotchas
- Pass the chunk count into a Workflow by **hardcoding it in the script** — `args` did not reach the
  script reliably (a run fanned out over an empty list and finished in 67ms doing nothing).
- Haiku occasionally truncates a 200-item chunk (wrote 100/200 once); always verify each `out`/`scores`
  file covers every input id before ingest, and re-run any short chunk.
- Triage decisions apply across the whole `canonical_key` group, so `status='irrelevant'` /
  keeper-mark counts (row-level) run higher than the per-canonical decision counts.
