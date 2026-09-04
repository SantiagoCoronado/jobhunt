# Token efficiency of `/jh-hunt`

Audit of 2026-09-02. Tool: `scripts/token_audit.py` (reads the Claude Code session JSONL under
`~/.claude/projects/-Users-santiagocoronado-jobhunt/`, plus each in-process subagent transcript
under `<session>/subagents/`, dedupes the repeated usage blocks, and reports per agent, per
tool, per phase). Run `python scripts/token_audit.py --latest` after any hunt; `--all` prints one
row per session.

"Context tokens" below means everything the model read across all API calls (input + cache
read + cache create). That is what a long agentic run pays for: each call re-reads the whole
conversation, so cost is roughly (context size) x (number of calls).

## Where the tokens went (last four full hunts, corrected numbers)

| Hunt | Context read | Main session | Notion work | Tailors | Researchers | Matchers |
|---|---|---|---|---|---|---|
| Aug 24 | 110M | 81M (Notion done inline, 311 calls) | inside main | 18M (15 agents) | 8M (13) | 2M (7) |
| Aug 27 | 97M | 23M | 55M (17 general-purpose agents, two Notion pushes at 22M + 9M) | 8M (12) | 3M (5) | 3M (6) |
| Aug 31 | 50M | 12M | 26M (5 general-purpose agents, one Notion sync at 22M) | 8M (5) | 4M (6) | 0 |
| Sep 1 | 78M | 60M (Notion + Chrome inline, 215 calls at ~280k each) | inside main | 7M (6) | 5M (6) | 6M (11) |

Findings, in order of size:

1. **Notion push over MCP was the single largest line item every time**, 25M to 65M per hunt.
   The push updated one page per `notion-update-page` call (65 to 187 calls) after dumping the
   whole CRM (`query crm`) and several 40 kB `query-data-sources` results into context, so every
   later call re-read a 300k to 390k context. Two hunts did it inside the main session, which
   is worse: the main context stayed bloated for every later phase too.
   Decision (Santiago, 2026-09-02): Notion is out of the hunt. `python -m src.pick` replaces the
   star step from SQLite. `/jh-notion-sync` remains an optional standalone.
2. **Main-session bloat.** Average context per main-session call ran 140k to 280k. Sources:
   MCP results left in context (Notion queries, Chrome `computer` screenshots at 60 to 110 kB
   each), `query crm` dumps, reading whole files (`answers.yaml` 51 kB, `sources.yaml`), and
   verbose subagent reports. Fix: subagents reply in one line or under 120 words; the
   orchestrator never runs `query crm`; Chrome stays out of the hunt.
3. **Resume-tailor agents** cost 1M to 4.5M each (30 to 70 calls). The render, audit, python
   heredoc loop ran 5 to 10 times per agent, and each agent read the full answer bank.
   Fixes: `src/answers_export.py` emits `answers.md` deterministically (7 approved entries,
   `{company}` filled, drafts listed, only the why-company block left for the model);
   the tailor prompt caps render/audit at two rounds; inputs are named explicitly so the
   agent reads each once.
4. **Gmail over MCP** cost 3M to 7M per sweep (45 to 64 `search_threads` calls). Already
   replaced by `python -m src.mail_fetch` (IMAP, one printed manifest). This run's sweep of two
   mailboxes was two Bash calls. Gap fixed today: the printed manifest carries no message ids,
   so `gmail_pull` now accepts `manifest_id` and copies the evidence headers itself.
5. **Triage** is cheap (Haiku, ~80k tokens per 200-row chunk) but a 200-row chunk truncates:
   Haiku wrote 130 to 145 rows of 200 in 3 of 12 chunks and 79 of 94 in a gap chunk. Default
   chunk is now 100 rows; verify coverage and gap-fill before ingest.
6. **Dream rows flooded the match export.** `match export --min-bucket 3` let every dream row
   through regardless of bucket (665 rows, 533 of them bucket 0 to 2, mostly off-family NVIDIA
   and Binance titles). Fixed in `src/match.py`: a dream row bypasses the gate only while untriaged, or under
   `--rescore` (its bucket then comes from the old score on the general ladder, below the
   dream shortlist threshold); a dream row triage bucketed obeys the gate.
   Export went from 743 rows (13 matcher agents) to 218 (4 agents).
7. **Matchers and researchers are fine**: 0.1M to 0.8M per agent. Keep Opus for the matcher
   (calibration continuity) and Sonnet for research.

## Model routing used on 2026-09-02

| Stage | Model | Why |
|---|---|---|
| Triage (14 chunks) | Haiku 4.5 | keep/drop with a fixed rubric; ~80k tokens per 200 rows |
| Match (4 chunks) | Opus 5 | calibration must match the existing shortlist, scored under Opus |
| Research (6 dossiers) | Sonnet 5 | web fetch + summarize, capped at 8 fetches each |
| Tailor (6 applications) | Fable 5.1 | pinned; writes the resume YAML and letter |
| Orchestrator | Fable 5.1 | main session; keeps every subagent reply short |

## This run (2026-09-02), measured

| Metric | This run | Baseline (last four hunts) |
|---|---|---|
| Context tokens read, total | 25.9M | 50M to 110M |
| API calls | 314 | 411 to 915 |
| Main session | 16.9M over 98 calls | 12M to 81M |
| Triage (14 Haiku agents) | 3.1M | n/a (Workflow-driven before) |
| Match (4 Opus agents, 218 jobs) | 1.4M | 2M to 6M |
| Research (6 Sonnet agents) | 1.9M | 3M to 8M |
| Tailor (6 applications, 10 agent runs incl. 4 resumes) | 2.6M recorded | 7M to 18M |
| Notion | 0 | 25M to 65M |

Caveats: the session hit the plan's rate limit with four tailors in flight, so their
transcripts are partial and the tailor line undercounts; the audit itself added roughly
50k tokens of exploratory Bash output to the main session (re-read on every later call),
which a normal hunt will not carry. Even so the run came in at a quarter to half of the
baseline, and the main session is now the biggest line, which is the next thing to trim
(shorter skill expansions, fewer status turns).

## Lean tailor, measured (Phase B, 2026-09-02)

Three real applications under the read-once, write-once, build-once protocol
(`docs/spec-tailor-lean.md`): 3 to 4 API calls and 45k to 165k context tokens each, against
30 to 70 calls and 1M to 4.5M before. No fix rounds: the page-geometry block in the bundle
got every first draft to 91 to 92% at fit level 0 with a clean audit and one verified page.

## Rules going forward

- No Notion, no Chrome, no `query crm` inside `/jh-hunt`.
- Every subagent prompt ends with an explicit reply cap and a "read each input once" list.
- Deterministic scripts for anything a script can do: `src.pick`, `src.answers_export`,
  `src.mail_fetch` + `gmail_pull manifest_id`, `src.report`.
- Triage chunks of 100; verify coverage before ingest.
- Tailor render/audit at most twice; trim real content instead of iterating.
- Run `python scripts/token_audit.py --latest` at the end of a hunt and paste the totals into
  the report so drift is visible next time.
