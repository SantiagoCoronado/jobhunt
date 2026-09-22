# Spec: hunt orchestrator (`src/hunt/`, harness adapters)

Status: draft for review, 2026-09-07 (Santiago + Fable). Lands before the TUI resumes
(`docs/spec-tui.md` story 3 of PR 3 is where that work paused). Section 10 amends the TUI spec.

## 1. Why

`/jh-hunt` is a page of prose that the interactive Claude session reads and follows. Every
fan-out (triage, match, research, tailor) is the main session launching sub-agents by hand and
waiting. Nothing records what already finished, so a session that dies, hits the plan rate limit
or gets interrupted starts the hunt over or guesses where it was. The main session is also the
largest token line left after Notion went (`docs/token-efficiency.md`: 16.9M of 25.9M on
2026-09-02), because every step's output lands in its context and is re-read on every later call.

Two constraints shape the fix:

1. **No harness bias.** The only thing the user should choose is the intelligence of the model
   behind each stage. The pipeline must run the same on Claude Code, Codex, OpenCode, pi or
   Antigravity, and on whatever comes next, without a second implementation.
2. **The TUI is where the hunt will be driven from.** `docs/spec-tui.md` deferred "harness
   execution" to Later because shelling an interactive agent out of Textual is a terminal
   ownership problem. A headless orchestrator with a ledger and log files is the piece that
   makes that integration boring.

## 2. What the harnesses offer today (surveyed 2026-09-07)

Installed here: `claude` 2.1.261, `codex` 0.153.4, `opencode` 1.18.29, `pi` 0.85.1, `agy`
(Antigravity), `gemini`. Every one has a headless print mode with a model flag and a way to
restrict tools. Their fan-out primitives differ:

| Harness | Headless | Native agent roles | Fan-out primitive | Deterministic script |
|---|---|---|---|---|
| Claude Code | `claude -p --bare --output-format json --json-schema --allowedTools --system-prompt` | `.claude/agents/*.md` | Agent tool, Workflow tool (JS script, 16 concurrent, resumable within a session) | yes (Workflow) |
| pi | `pi -p --mode json --system-prompt --tools --provider --model` | `.pi/agents/*.md` (extension) | `pi-subagents` extension: `SubagentWorkflow` runs Claude Workflow scripts unchanged, `--subagents-workflow-file` headless | yes (extension) |
| Codex | `codex exec --json --output-schema -o --sandbox -m` | `.codex/agents/*.toml` | MultiAgentV2: `spawn_agent`, `spawn_agents_on_csv`, `max_threads` 6, model in the loop | no |
| OpenCode | `opencode run --format json --agent -m provider/model` | `.opencode/agents/*.md` | Task tool, `@agent`, model in the loop | no |
| Antigravity | `agy -p --output-format json --json-schema --agent --model --effort` | `agy agents` | async subagents in the TUI, `subagent_info` in stream events | no |
| Gemini CLI | `gemini -p -m --approval-mode` | `.gemini/agents/*.md` | subagents, parallel still experimental | no |

Only Claude Code and pi (through an extension that copies Claude's script format) have a
deterministic orchestration script. Everywhere else the model decides what to spawn. Building the
hunt on any of those primitives ties it to that harness and, worse, to that harness's version.

The common denominator is a **process**: every harness can run one prompt, with one system
prompt, one model, a tool allowlist, and print a JSON envelope. So the orchestrator fans out at the
process level, and a harness is a small adapter that knows how to build that command line and read
that envelope. The Claude Workflow tool, the pi extension and Codex MultiAgentV2 are not used.

## 3. Decisions (settled 2026-09-07, do not re-open without a reason)

| # | Decision | Choice | Why |
|---|----------|--------|-----|
| 1 | Where orchestration lives | Python, `src/hunt/`. One state machine, one run ledger on disk, one process per unit of model work. | Harness-neutral, resumable across sessions, runnable from a terminal, from `ai_pass.sh` and from the TUI runner. Same venv as everything else. |
| 2 | Scope | The whole hunt: discover, triage, match, inbox pull, pick, research, tailor, report. | One ledger for one hunt. Deterministic stages are cheap to include and make `status` honest. |
| 3 | Fan-out | Process level: one harness process per triage chunk, match chunk, dossier, tailor, and one for inbox classification. Never a harness's own subagent or workflow feature. | Identical behaviour on every harness, the orchestrator verifies files not agent chatter, and retries are one process again. |
| 4 | Judge of done | Python. A unit is done when its output file exists and passes the stage's coverage check. Agent text is logged, never parsed for decisions. | The agent's reply is the least reliable artefact it produces. |
| 5 | Harness adapters | A tiny class per harness: build argv, run, parse the envelope into `Usage`. Ship and smoke-test claude (reference), codex, opencode, pi, agy. gemini via the generic `command` template only. | Five installed here. Anything else is a `[harness.<name>]` block with a command template. |
| 6 | Model selection | No tiers, no model ids shipped in the repo. Each stage's `model` in `config/hunt.toml` is chosen from the harness's **live catalog** (`hunt models`), or left unset to take the harness default. Claude is the one known exception: its CLI has no catalog, so for claude the pre-run check is a 10-token smoke prompt per distinct configured model (the same call `doctor` makes), which is what turns a retired alias into a minute-zero failure instead of a mid-hunt one. Rolling aliases are preferred where the harness has them (`fable`, `opus`, `sonnet`, `haiku` on claude; `~anthropic/claude-fable-latest` on pi and opencode). Every configured model is validated against the live catalog before a run starts; a model the harness no longer lists fails the run at minute zero with the current list printed, never mid-hunt. | Models change under us; a pinned id in a committed file is a crash waiting for a deprecation. The user should see what is actually available today and pick from that. Mixing harnesses per stage stays a config edit. |
| 7 | Prompts | Harness-neutral role files in `prompts/agents/<role>.md` (system prompt body plus a small frontmatter: tools, output contract). `python -m src.hunt sync-agents` generates every harness's native agent file from them; the generated files are committed and a test asserts they are in sync. | Interactive `/jh-tailor`-style use on any harness keeps working, the text lives once. `.claude/agents/*.md` stops being the source. |
| 8 | Ledger | `data/hunt/<run_id>/` with `state.json` (stages, units, verdicts, usage), `events.jsonl` (append-only), `logs/<stage>/<unit>.log` (harness stdout+stderr streamed), and the unit outputs the stages already write under `data/triage`, `data/match`, `data/tailor`. `run_id` is `YYYYMMDD-HHMM`. | Files a TUI can tail and a human can `cat`. SQLite stays the job data, never the run log. |
| 9 | Resume | `hunt run --resume latest` re-enters the state machine: finished units are skipped by ledger verdict, unit outputs still on disk are re-verified not re-run, failed units run again, the stage cursor continues. On resume a fanned stage takes its unit list from the ledger and **never calls `export` again**: `triage.export` and `match.export` delete every `chunk_*`, `out_*` and `scores_*` file before writing (`src/triage.py:55`, `src/match.py:183`), so a re-export would erase the outputs the resume is there to keep. `data/triage/` and `data/match/` are single global directories, not per run; their chunk files are part of a live run's inputs, the lockfile is what keeps anything else from re-exporting while a run is live, and `state.json` records the chunk list with sizes so a mismatch on resume is detected and reported rather than silently re-planned. A new `hunt run` without `--resume` starts a new run id and never touches an older run's folder. | Cross-session, cross-harness, no dependency on any harness's session store. |
| 10 | Concurrency | Per-stage cap in `hunt.toml` (triage 8, match 4, research 4, tailor 3, inbox 1) under a global cap (8). One attempt counter per unit: `retries = N` in `hunt.toml` means at most `1 + N` attempts, and every failure kind (timeout, non-zero exit, bad or short output file) consumes one. A rate-limit signal (harness `is_error` with 429-like text, or non-zero exit inside 10 s) is a **wait, not an attempt**: the unit sleeps 30 s, then 60 s, then 120 s and tries again without touching the counter; after the third consecutive backoff the attempt is marked failed and consumes one retry. Worst case for triage is therefore 3 attempts, each preceded by at most 3 waits. | Four Fable tailors in flight hit the plan limit on 2026-09-02. |
| 11 | Timeouts | Per stage: triage 5 min, match 10, research 15, tailor 15, inbox 10. A killed unit is one failed attempt under the same `retries` counter as decision 10, not an extra retry. | Antigravity headless is known to hang in a non-TTY (issue 318); a hang must never hold the hunt. |
| 12 | Interactivity | None inside a run. Questions the prose flow used to ask (role or company mismatch in the inbox pull, aggregator employer unresolved at pick) become `needs_human` items in the report; the run continues around them. | The hunt never blocks; the human reviews at the end, as with every other draft. |
| 13 | DB writes | Only Python writes the DB, through the existing entry points (`triage.ingest`, `match.ingest`, `gmail_pull --apply`, `set_status`). Agents write files. | One write path per table, already the house rule. |
| 14 | `/jh-hunt` after | A thin skill: `python -m src.hunt run` in the background, `hunt status` while it runs, `hunt report` at the end. No Agent calls, no Workflow, no file reads. | The main session becomes a viewer, which is where its 17M went. |
| 15 | `ai_pass.sh` after | Calls `python -m src.hunt run --to match --harness <default>` instead of `claude -p "run /jh-triage then /jh-match"`. | The scheduled pass gets the ledger, retries and coverage checks for free. |
| 16 | Token accounting | Each adapter parses its envelope into `Usage(input, output, cache_read, cache_create, cost_usd)` where the harness reports it, nulls where it does not. `hunt report` sums per stage. `scripts/token_audit.py --hunt <run>` reads the ledger instead of Claude session JSONL. | The audit stops depending on one harness's transcript format. |
| 17 | Multiplexer panes | Not used by the hunt. Logs plus `hunt status` are the view; the TUI run screen tails the same logs (section 10). | Panes are a multiplexer feature, the orchestrator must not depend on one. |
| 18 | Quality gates | Deterministic only: coverage checks per stage, `tailor_build` verdict with one fix round, dossier `researched:` line. No critic agents. | Token discipline. A critic is a later stage if calibration data says it is needed. |

Routine calls made without a question: the ledger is JSON not SQLite; unit logs are plain text;
`hunt.toml` is committed; the run folder is git-ignored under `data/`; zero em-dashes in anything
the orchestrator prints or writes.

## 4. Architecture

```
python -m src.hunt run
        │
        ▼
  src/hunt/run.py            state machine over the stage registry
        │  for each stage, in order
        ▼
  src/hunt/stages/<stage>.py  plan() -> [Unit], verify(unit) -> Verdict, ingest()
        │  units that need a model
        ▼
  src/hunt/pool.py            bounded thread pool, per-stage cap, retries, backoff, timeouts
        │  one subprocess per unit
        ▼
  src/hunt/harness/<name>.py  argv(prompt, system, model, tools, schema) + parse(envelope)
        │
        ▼
  <harness> -p ...            reads its inputs, writes its output file, exits
        │
        ▼
  ledger.py                   state.json, events.jsonl, logs/, usage
```

A **stage** is deterministic (a Python callable) or fanned (a planner that yields units, a unit
verifier, an ingest step). A **unit** is one prompt with a fixed output path. The orchestrator
never reads a unit's stdout for a decision; it reads the output file.

### Stage registry

| # | Stage | Kind | Units | Output | Verify | Ingest |
|---|---|---|---|---|---|---|
| 1 | discover | python | 1 (`src.discover.main`, then `src.maintain`) | `runs` rows | at least one source ok, list FAILED sources | none |
| 2 | triage | fanned, `stages.triage.model` | one per `data/triage/chunk_NNN.json` (100 rows) | `data/triage/out_NNN.json` | every input id present once, `keep` bool, `bucket` 0..3 | `triage.ingest()` |
| 3 | match | fanned, `stages.match.model` | one per `data/match/chunk_NNN.json` (`--min-bucket 3 --chunk 60 --limit 0`; a second pass `--min-bucket 2` when the first is under the stage budget; pass 1 is ingested **before** pass 2 exports, because `match.export` wipes `scores_*.json`, so the stage is export, run, ingest, then export, run, ingest again, each pass its own unit group in the ledger) | `data/match/scores_NNN.json` | every input id scored, score 0..100, verdict JSON well formed | `match.ingest(scores_dir=...)` after each pass |
| 4 | inbox | fanned, `stages.inbox.model` | 1 (manifest from `src.mail_fetch run`, printed into the prompt; `Bash` limited to `python -m src.mail_fetch show`) | `data/gmail_pull.json` | validates through `gmail_pull` dry run; `sweep` stamp matches | `gmail_pull --apply`; lines the classifier marked `needs_human` go to the report |
| 5 | pick | python | 1 (`src.pick --json`) | `picks.json` in the run folder | 5 picks or fewer with the reason; aggregator rows without a resolvable employer become `needs_human` and the next spare is taken | none |
| 6 | research | fanned, `stages.research.model`, needs `web` | one per pick whose `research get` says missing or stale | `research/companies/<slug>.md` | file exists, ends with `researched: YYYY-MM-DD` of today, has a Sources section, zero em-dashes | none |
| 7 | tailor | fanned, `stages.tailor.model` | one per pick, after `tailor_bundle` (with `--company`/`--dossier` for aggregator rows) | `<folder>/draft.md`, then `build.json` from `tailor_build` | `build.json` verdict PASS, page count 1, fill in range; on FAIL one more unit run with the verdict in the prompt | none |
| 8 | report | python | 1 (`src.report`, then the run summary) | `data/report.html`, `data/hunt/<run>/report.md` | file exists | none |

Stage order is fixed. `--from`, `--to`, `--only` and `--skip` select a contiguous or single set;
`inbox` is skipped with a note when no mail account is configured. Triage is skipped when the
unscored pile is under `triage.min_pile` (200). Pick stops the run early, with a report, when it
returns no picks.

### Unit prompt

Every unit prompt is assembled from three parts, in this order, and written to
`data/hunt/<run>/prompts/<stage>/<unit>.md` so a failed unit can be re-run by hand on any harness:

1. the role file body from `prompts/agents/<role>.md` (system prompt for harnesses that take one,
   prepended to the user prompt for those that do not);
2. the stage's fixed task line naming the input file, the output file and the contract (the same
   two-line shape the lean tailor already uses);
3. the reply cap: "Reply with one line. Your reply is not read; the output file is."

The role files are today's `.claude/agents/{job-matcher,company-researcher,resume-tailor}.md`
bodies plus two new ones extracted from the commands: `triager` (the rubric in
`.claude/commands/jh-triage.md`) and `inbox-classifier` (the legend rules in
`.claude/commands/jh-gmail-sync.md`).

## 5. Harness adapters (`src/hunt/harness/`)

```python
@dataclass
class Invocation:
    prompt: str            # user prompt (task line + contract)
    system: str            # role body
    model: str | None      # from hunt.toml, validated against the live catalog; None = harness default
    tools: set[str]        # {"read", "write", "edit", "bash", "web"}; bash is "python only"
    schema: dict | None    # JSON schema when the unit returns structured text (inbox)
    cwd: Path
    timeout_s: int

@dataclass
class Usage:
    input: int | None; output: int | None; cache_read: int | None
    cache_create: int | None; cost_usd: float | None

class Harness(Protocol):
    name: str
    capabilities: set[str]                 # what tools it can grant, e.g. {"read","write","bash","web"}
    def argv(self, inv: Invocation) -> list[str]: ...
    def parse(self, stdout: str, stderr: str, rc: int) -> tuple[Usage, str | None]:  # usage, error
        ...
```

Reference command lines (verified against `--help` on 2026-09-07; the adapter test pins them):

| Harness | argv |
|---|---|
| claude | `claude -p [--bare] --output-format json --no-session-persistence --strict-mcp-config --permission-mode acceptEdits --permission-prompts none --model {model} --system-prompt {system} --tools Read,Write,Edit,Bash[,WebSearch,WebFetch] --allowedTools Read Write Edit "Bash(python:*)" "Bash(.venv/bin/python:*)" [WebSearch WebFetch] [--json-schema {schema}]` with the prompt on stdin. Landed 2026-09-18 (PR 2 story 3, verified on 2.1.276): the prompt cannot be a trailing argument because `--allowedTools` and `--tools` are variadic; `--tools` restricts the built-in set and `--allowedTools` pre-approves it; `--permission-prompts none` denies instead of hanging; `--bare` is passed only when `ANTHROPIC_API_KEY` is set, because bare mode never reads the OAuth login and fails with `terminal_reason: api_error`, "Not logged in" |
| codex | `codex exec --json -o {last_msg} [-m {model}] --sandbox {workspace-write or read-only} [--output-schema {file}] --ephemeral --skip-git-repo-check -` with `{system + prompt}` on stdin. Landed 2026-09-21 (PR 4 story 1, 0.153.4): a prompt argument with a closed stdin still prints "Reading additional input from stdin"; the sandbox is the only grant, read-only when the unit writes nothing; seen on a failed call only, the install was not logged in |
| opencode | `opencode run --format json [-m {provider/model}] --agent {role} {prompt}` (the generated agent file carries tools, permissions AND the role body; `--agent` is what applies them, so the prompt is the task alone). Landed 2026-09-21 (PR 4 story 2, 1.18.29, real calls): `Invocation` gained `role`; no schema flag, the schema rides in the prompt; usage is summed over one `step_finish` per step |
| pi | `pi -p --mode json --no-session --no-context-files --no-skills --no-prompt-templates --no-approve [--model {provider/id}] --system-prompt {system} (--tools read,write,edit,bash or --no-tools)` with the prompt on stdin. Landed 2026-09-21 (PR 4 story 3, 0.85.1, real calls): an argument starting with `@` is a file and one starting with `-` an option; `--model` takes `provider/id`, so no `--provider` |
| agy | `agy --output-format json [--model {model}] [--mode accept-edits] [--json-schema {schema}] --print-timeout {timeout}s --print={system + prompt}`; shell stays auto-denied unless `permissions.allow` in `~/.gemini/antigravity-cli/settings.json` covers `python`; `doctor` checks that and sign-in before it spends a call. Landed 2026-09-21 (PR 4 story 4, 1.1.27, signed out): `-p` takes the prompt as its value, so the line first written here exits 2; no `--agent`, the `agent.md` layout could not be confirmed; a signed-out headless call waits past `--print-timeout`; envelope `{status, response, error?, structured_output?, usage}` captured on 2026-09-22 |
| generic | `[harness.<name>] command = "..."` template with `{model} {system_file} {prompt_file} {schema_file}` placeholders (plus `{prompt}` and `{system}` as text, landed 2026-09-21: most CLIs take the prompt as an argument, not a file), `envelope = "json" | "text"` and `capabilities = [...]`; usage is null on `text`. Per-harness detail: `docs/hunt-harnesses.md` |

`web` is a capability: only harnesses that grant a web tool can run `research`. The stage falls
back to the first configured harness with `web` and logs the substitution. As landed
(2026-09-21) only claude, opencode with `OPENCODE_ENABLE_EXA`, and a template that declares it
claim `web`: codex and agy could not be verified headless, so they do not.

### Live model catalog

Each adapter implements `models() -> list[Model] | None` by asking the harness, never from a
table in the repo (checked 2026-09-07):

| Harness | Source of truth | Notes |
|---|---|---|
| claude | no list command. `models()` returns `None`; the adapter parses the alias examples out of `claude --help` for display only (no list in the repo) and accepts any full id. Pre-run validation for claude is the smoke prompt: one 10-token call per distinct configured model, failing the run if the CLI rejects the model | the known exception to catalog validation; aliases resolve to the latest model, so they are still the safest choice |
| codex | `codex debug models` (JSON catalog, `slug` per entry) | 11 entries today, includes `-latest` slugs |
| opencode | `opencode models` (`provider/model`, one per line) | 405 entries today; `openrouter/~anthropic/claude-fable-latest`-style rolling ids exist |
| pi | `pi --list-models` (provider, model, context, thinking) | `~provider/model-latest` rolling ids |
| agy | `agy models` | needs a sign-in first; `doctor` reports "sign in" instead of failing |
| gemini, generic | none | `models()` returns `None`; the configured model is passed through unvalidated and `doctor` says so |

`hunt models [--harness NAME] [--grep TEXT]` prints the live catalog. `doctor` prints the
binary, version, catalog size or the reason it could not be read, whether every stage's configured
model is in the catalog, a 10-token smoke prompt result and whether the tool grants worked, so a
broken adapter or a retired model is found before a hunt, not during one.

## 6. Configuration (`config/hunt.toml`, committed)

```toml
[harness]
default = "claude"                # any [harness.<name>] below or a shipped adapter
global_concurrency = 8

# Models: pick from `python -m src.hunt models`, the live catalog of the harness.
# Leave `model` out to take the harness default. Rolling aliases are the safest choice.
# A model the harness no longer lists stops the run before it starts.

[stages.triage]
model = "haiku"                   # claude rolling alias; `hunt models` shows the alternatives
concurrency = 8
timeout_s = 300
retries = 2
min_pile = 200                    # skip the stage under this many unscored canonical rows
chunk = 100

[stages.match]
model = "opus"                    # calibration continuity with the existing shortlist
concurrency = 4
timeout_s = 600
retries = 2
chunk = 60
min_bucket = 3
second_pass_min_bucket = 2        # 0 disables the second pass
budget_units = 12                 # stop planning match units past this many per run

[stages.inbox]
model = "sonnet"
concurrency = 1
timeout_s = 600
retries = 1

[stages.research]
model = "sonnet"
concurrency = 4
timeout_s = 900
retries = 1
# harness = "claude"              # per-stage override; must grant "web"

[stages.tailor]
model = "fable"                   # the tailor stays on the strongest writer available
concurrency = 3
timeout_s = 900
retries = 1                       # the one fix round; a second failure is reported, not retried

[pick]
n = 5
dream_slots = 2
```

`profile.yaml` keeps every scoring and dream rule. `hunt.toml` only says how to run, never what
counts as a fit. The TUI settings modal's `harness` tab edits `harness.default` and each stage's
`model`, picking from the live catalog; `config/tui.toml` drops its own `harness.template`
(section 10). The shipped file names claude aliases because claude is the reference harness; on
another harness `doctor` lists what to change them to.

## 7. Ledger (`data/hunt/<run_id>/`)

```
state.json
  run_id, started, harness, config snapshot (hunt.toml as loaded),
  stages: [{name, state: pending|running|done|failed|skipped, started, ended,
            units: [{id, input, output, attempts, state, verdict, usage, harness, model, log}],
            summary: {...stage specific: kept/dropped, shortlisted, picks, needs_human}}]
events.jsonl      one line per transition: {ts, stage, unit, from, to, note}
prompts/<stage>/<unit>.md
logs/<stage>/<unit>.log
picks.json
report.md
```

`state.json` is rewritten atomically (write to `.tmp`, rename) after every transition so a crash
leaves a readable ledger. `hunt status [run]` renders it as a tree with counts and the last log
line per running unit. `hunt report [run]` writes and prints `report.md`: what each stage did,
the 5 picks with dossier and application paths, each build's RESUME and LETTER verdict lines,
`visa_path` and the relocation line for dream rows, the `needs_human` list, and usage per stage.

## 8. CLI

```
python -m src.hunt run      [--harness NAME] [--from STAGE] [--to STAGE] [--only STAGE]
                            [--skip STAGE ...] [--ids ID,ID,...] [--resume RUN|latest]
                            [--dry-run] [--quiet]
python -m src.hunt status   [RUN|latest]
python -m src.hunt report   [RUN|latest]
python -m src.hunt runs     # list run folders with state and started time
python -m src.hunt models   [--harness NAME] [--grep TEXT]   # live catalog, never a table in the repo
python -m src.hunt doctor   [--harness NAME]
python -m src.hunt sync-agents [--check]
```

`--dry-run` plans every stage, writes the prompts, runs nothing and prints the unit list with the
harness and model each would use. `run` prints one line per transition to stdout (the TUI tails
the same lines) and exits 0 when every non-skipped stage is done, 2 when any stage failed, 3 when
the pick stage found nothing to tailor. A lockfile (`data/hunt/.lock`, mkdir-atomic like
`ai_pass.sh`) refuses a second concurrent run.

`--ids 3625,9118` (added 2026-09-20, PRA-111) runs research and tailor on rows a human chose,
in the order given: `--only research`, `--only tailor`, `--from research --to tailor` (the
report may follow). The ids stand in for the pick stage: `src.pick.chosen` builds the same
records `pick` writes and the run starts with them in its `picks.json` (`"source": "ids"`), so
the stages and the report read them as they read a hunt's picks, and `--resume` keeps them
because the file is the run's. Refused by name before a ledger exists: an id that is not a row,
a row that is not `shortlisted`, a dream row outside the relocation regions (the block `pick`
applies; export-control rows never reach `shortlisted`, the matcher's hard block), a range that
holds a stage that does not read picks (`pick` and everything before it), and `--ids` with
`--resume`. The star rule does not apply: no slot count, no dream slots, no one-per-company, no
in-play or cooldown skip, an unscored row is fine. The human chose. The TUI's runner is the
caller: `enter` on `tailor` or `research` passes the rows marked in the jobs sections.

## 9. Interactive use after this lands

- `/jh-hunt`: step 1 `python -m src.hunt run` with `run_in_background`; step 2 poll
  `python -m src.hunt status latest` at most every two minutes and relay the tree; step 3
  `python -m src.hunt report latest` and present it. The skill's `allowed-tools` becomes
  `Bash` only.
- `/jh-triage`, `/jh-match`, `/jh-research`, `/jh-tailor`, `/jh-gmail-sync` keep their prose flow
  for a single interactive use, and each gains one line: "for a batch, `python -m src.hunt run
  --only <stage>`". Their agent bodies come from `prompts/agents/` via `sync-agents`.

## 10. TUI integration (amends `docs/spec-tui.md`)

The following replaces the "copy the slash command" model for LLM stages. Applied to the TUI spec
as a diff in the same PR as this document:

- Decision 5 (Claude Code): v1 of the TUI still runs no model itself. It runs `python -m src.hunt
  run --only <stage>` or a full `run` as a subprocess, exactly like a Python stage, and tails its
  stdout in the log pane. Copy-to-clipboard stays as the secondary verb.
- Decision 12 (Runner scope): the stage list comes from the `src.hunt` registry (both kinds) plus
  the extra Python stages (reconcile, stats). `enter` runs any of them. One process at a time.
- Decision 13 (Settings): the `harness` tab edits `config/hunt.toml` (`harness.default`, one
  model per stage picked from the live catalog), not `tui.toml`. `tui.toml` loses `[harness]`.
- Section 6 (Settings file): drop the `[harness]` block.
- PR 5 stories 4 to 6 become: 4 **Harness settings** (tab over `hunt.toml`, `doctor` button);
  5 **Runner data** (stage registry from `src.hunt`, run list from `data/hunt/*/state.json`,
  `data.hunt_runs()` and `data.hunt_status(run)`); 6 **Runner screen** (stage list, run list,
  log pane tailing `logs/` for the selected unit, `enter` runs, `ctrl+c` cancels by killing the
  subprocess which the orchestrator handles by marking running units failed so `--resume` picks
  them up).
- Section 9 (Later): remove "Harness execution"; add "unit-level view in the runner (one row per
  unit with attempts and usage)".

## 11. Non-goals

Using any harness's subagent, workflow, or session-resume feature. Model-in-the-loop
orchestration. Critic agents. Running two hunts at once. Editing `profile.yaml` from the
orchestrator. A daemon: every command is a process that exits.

## 12. Phases, PRs and stories

One PR per phase, one commit per story, stories land in the listed order. Every story keeps
`ruff`, `mypy` and `pytest` green (`set -o pipefail` before claiming green). Zero em-dashes in
any text the orchestrator prints or writes. Spec review happens in a separate session before
PR 2 starts.

### PR 1: `docs/spec-hunt`

1. This document.
2. The `docs/spec-tui.md` amendments from section 10.

### PR 2: `feat/hunt-core`

1. **Skeleton**: `src/hunt/{__init__,__main__,cli,config,ledger}.py`; `config/hunt.toml` with
   the claude aliases per stage; `hunt runs` and `hunt status` over an empty folder; tests for
   config defaults, missing model (harness default), unknown stage.
2. **Ledger**: `state.json` atomic writes, `events.jsonl`, transitions, `status` tree renderer;
   tests replay a synthetic run and assert every transition is recoverable.
3. **Harness base + claude adapter**: `Invocation`, `Usage`, the `Harness` protocol, the claude
   argv and envelope parser; tests pin argv per tool set and parse a captured envelope.
4. **Pool**: bounded thread pool with per-stage and global caps, timeouts, retries, backoff on
   rate-limit signals, streamed logs; tests use a fake harness that sleeps, fails, and times out.
5. **Deterministic stages**: discover (with maintain), pick, report in the registry; `hunt run
   --only discover` works end to end; tests use a temp DB.
6. **Models and doctor**: `models()` on the adapter protocol, `hunt models`, run-start
   validation of every stage's model against the live catalog; `doctor` with binary, version,
   catalog, per-stage model check, one smoke prompt, tool grant check; tests with a fake harness
   on PATH whose catalog drops a model between two calls.
7. **Prompts**: `prompts/agents/{triager,job-matcher,company-researcher,resume-tailor,
   inbox-classifier}.md` extracted from the agent and command files, frontmatter with `tools`
   and `output`; `sync-agents` generates `.claude/agents/*.md`; `sync-agents --check` in CI;
   test asserts the generated files match.

### PR 3: `feat/hunt-fanout`

1. **Triage stage**: planner over `triage.export`, per-unit coverage verify (every id once,
   re-run short chunks), `triage.ingest`; summary kept/dropped/buckets; test with a fake harness
   that writes a short file once.
2. **Match stage**: planner over `match.export --min-bucket --chunk --limit 0`, verify, ingest,
   optional second pass, dream rows reported on their own line; tests.
3. **Inbox stage**: manifest into the prompt, `show` allowed, JSON schema for the proposals,
   dry run as verify, `--apply`, `needs_human` collection; skipped cleanly with no accounts;
   tests on the `gmail_pull` fixtures.
4. **Research stage**: `research get` staleness, `web` capability routing, dossier verify; tests.
5. **Tailor stage**: `tailor_bundle` per pick, unit, `tailor_build` verdict as verify, one fix
   round with the verdict in the prompt, `build.json` metrics into the ledger; tests on the
   `tailor_build` fixtures.
6. **Report**: `report.md` renderer with the section 7 contents; `hunt report`; test on a
   synthetic ledger.
7. **Resume**: `--resume`, re-verify outputs on disk, skip done units, the lockfile; tests kill
   a fake run mid-stage and resume it.
8. **Wire the skills**: `/jh-hunt` rewritten per section 9, `ai_pass.sh` calls `hunt run --to
   match`, CLAUDE.md Pipeline and Commands sections updated, `docs/token-efficiency.md` gains a
   "measured under the orchestrator" row after the first real hunt.

### PR 4: `feat/hunt-harnesses`

1. **codex adapter** with `--output-schema` and `-o`; smoke test behind a marker that skips when
   the binary is missing.
2. **opencode adapter** plus `sync-agents` output to `.opencode/agents/*.md`.
3. **pi adapter** plus `.pi/agents/*.md`.
4. **agy adapter** plus the permissions check in `doctor`; `.gemini/agents/*.md` and `.codex/agents/*.toml` from `sync-agents`.
5. **generic template harness** for anything else; docs page `docs/hunt-harnesses.md` with the
   exact command line per harness and how to add one.

### PR 5: `feat/hunt-audit`

1. **Usage in the ledger** rolled up per stage and per harness; `hunt report` usage table.
2. **`scripts/token_audit.py --hunt RUN`** reading the ledger; the Claude-JSONL mode stays for
   interactive sessions.
3. **`stats`**: `python -m src.stats hunts` over `data/hunt/*/state.json` (units, retries,
   failures, usage per stage per run) so drift is visible without opening a ledger.

## 13. Later (not scheduled)

A Workflow-script emitter for harnesses that run them (Claude, pi), as a pure optimisation of
process startups; a critic stage if calibration data asks for one; unit-level runner rows in the
TUI; `hunt run --watch` re-running discover on a schedule inside one process.

## 14. Resolved in review (2026-09-07)

- **No tier maps, no model ids in the repo** (Santiago): models change with time, so a
  committed id is a future crash. Each stage names a model picked from the harness's live
  catalog, or none for the harness default; validation happens before a run starts. Decision 6.
- **Generated native agent files are committed** for every shipped harness, so interactive use
  works after a clone with no setup. Decision 7.
- **`inbox` runs after `discover`**: no effect on function, quality or tokens either way, and
  after catches a reply that lands during a long discover.
