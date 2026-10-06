# Spec: pre-release (onboarding, the harness installer, region-gated sources, the cuts)

Status: draft for review, 2026-09-24 (Santiago + Fable). Lands between the open-source PR 3
(`feat/profile-driven-prompts`, merged) and the public release (`release/public`, PR #34, open).
The release checklist in `docs/spec-open-source.md` section 7 runs again after this spec's last
phase, on the tree it leaves. Amended 2026-10-06: the stats screen (decision 15) joins as PR 6,
moved here from `docs/spec-tui.md` section 9; the full flow becomes PR 7.

## 1. Why

`docs/spec-open-source.md` made the repo safe to publish: no user data tracked, prompts
profile-driven, a fake candidate so a clone runs. It did not make the repo easy to *adopt*. On
2026-09-24, with the release PR open, Santiago paused it for four reasons:

1. A stranger still writes three YAML files by hand (`profile.yaml`, `master_resume.yaml`,
   `sources.local.yaml`) before anything useful happens. The master resume in particular is a
   deep schema nobody wants to type. People already have resumes, LinkedIn exports and old
   cover letters; the tool should read those and ask questions, not hand over a template.
2. Keys for the keyed boards and the mail app passwords live in `.env` with comments as the
   only guide.
3. The only end-to-end proof is on the author's machine, on the author's harness. Three
   harnesses (claude, codex, pi) and a second person (a friend, on their own CLI and resume)
   have to go from clone to a tailored application before the post goes up.
4. The tree still carries things built for one person: a Google Sheet read through a Drive MCP,
   a macOS launchd schedule, a CI review workflow that talks to Linear and Cursor, research
   reports about Mexico, and sources chosen for one search. A new user should find three kinds
   of things: what everyone uses, what they can switch on, and nothing that only ever worked
   for the author.

The reference for the install experience is `mattpocock/skills`: one command, it asks which
agents you use, and it installs only what your setup needs. The audience is anyone who runs an
agent CLI (the post goes to the Claude Code, Codex and general subreddits), so no harness is
the assumed one.

## 2. Decisions (settled 2026-09-24, do not re-open without a reason)

| # | Decision | Choice | Why |
|---|----------|--------|-----|
| 1 | Order | PR #34 (`release/public`) is merged now as it stands (LICENSE, the README, the clone job); it leaves the repo private. The phases below land after it; the README gets a final pass in the last phase; checklist steps 3 and 4 (clean tree, scans) run again on the final tree, then steps 5 to 7. | The three landed stories are useful today and safe; keeping a branch open across five more PRs only invites conflicts. |
| 2 | Distribution | `git clone` then one setup command, now. A pip/uvx package is a follow-up after the first round of feedback, not part of this spec. | The repo is the product: the user owns and edits every file, and the agent files, prompts and config have no home in site-packages. |
| 3 | Installer | `./setup.sh` becomes a thin wrapper around `python -m src.setup`: detect the agent CLIs on PATH, ask which the user runs (multi-select, `--harness a,b` and `--yes` for scripts), make the venv and install deps, run `init`, write the default harness into `config/hunt.toml`, run `hunt doctor` for each chosen harness, and end by naming the next step in that harness's own words (`/jh-setup` in claude or opencode, the prompt name in codex). It never renders per-user files: every harness's native files stay committed and identical for everyone (open-source decision 6). | The mattpocock flow, without dirtying a tracked file. |
| 4 | Front door on every harness | Every `/jh-*` command lives once in `prompts/commands/<name>.md` (harness-neutral wording: "your shell tool", never "Bash tool" or "Agent tool") and `sync-agents` renders it into each harness's native command format beside the agent files; CI checks the renders. Where a harness has a per-project command format it gets real commands; where it has none, `AGENTS.md` (codex, agy) lists the flows under `## Commands` with the exact text to say, and the installer offers to copy the prompt files into the harness's home-level prompts dir as an opt-in. The formats are verified per harness in the story that lands them, and a harness whose format could not be confirmed falls back to `AGENTS.md` and says so in `docs/hunt-harnesses.md`. | A codex user should type the same thing a claude user types. |
| 5 | Fan-out commands delegate | `/jh-triage`, `/jh-match` and `/jh-hunt` stop describing subagents or Workflows and run the orchestrator (`python -m src.hunt run --only triage`, `--only match`, the full run), watching `hunt status` while it works. `/jh-research`, `/jh-tailor`, `/jh-gmail-sync` keep their single-unit shape (bundle, one agent, build) but say "the <role> agent" and let the harness's native agent file supply it. | The orchestrator is already harness-neutral; a command that names a Claude-only fan-out feature cannot be ported. It also removes the last places a hunt could run inside the chat session (`docs/history/token-efficiency.md`). |
| 6 | Onboarding | `/jh-setup` is an interview run by the agent, backed by `python -m src.onboard` for everything deterministic. Intake: any number of documents (resumes, cover letters, a portfolio page saved as text, LinkedIn's profile PDF, LinkedIn's data-export zip) in PDF, docx, md, txt or csv; a public LinkedIn URL as an explicit opt-in with a warning (see decision 7). The helper extracts text (`pypdf`, `python-docx`, the zip's csv files) into `data/onboard/`; the agent reads each once and writes `resume/master_resume.yaml`, then interviews for the profile one section at a time, then proposes sources from the profile's regions and asks for the ATS tokens of companies the user follows (each verified live before it is written), then keys, then mail accounts (optional). Every write goes through the helper, which validates against the schema (`config check`, the resume loader) and never overwrites a file the user already edited without showing the diff and asking. Ends with `hunt doctor`, a first `discover`, and a summary of what was written where. | The three files are the whole barrier to entry. |
| 7 | Nothing invented, still | The master resume the interview writes contains only facts present in the user's documents or typed by the user in the interview; the agent lists, per role and per skill, which document it came from, and anything it could not place becomes a question, never a guess. The public LinkedIn fetch reads the public page only, never a logged-in session, and is off unless the user passes the URL; it is documented as fragile (login wall, terms). | The hard rule of the whole product applies to its own setup. |
| 8 | Keys | The interview lists the keyed sources relevant to the user's regions with each one's signup URL, takes the value or "skip", and writes `.env` through the helper (one-line edits that keep the comments). The TUI settings modal gets a Keys tab reading the catalog from `.env.example` (name, hint, URL), showing set or unset, editing through the same helper, never displaying a value. | Set once in the chat, change later in the app, no hand-editing. |
| 9 | Dream companies table | The dream list moves out of `config/profile.yaml` into a `dream_companies` table in `data/jobs.db` (name, match phrases, careers URL, note, added_at). `src.dream` reads it (cached per process); `python -m src.query dream {list|add|rm}` edits it; the TUI edits it (a Dream tab in the board's status list, `a` add, `x` remove); the interview fills it; `init` migrates an existing profile's list into the table once, under a dated note in the profile. `dream_rule`, the thresholds and `relocation_line` stay in the profile: they are rules, not data. Openings at a dream company with no board are hand-entered rows (`query add`), as today. | One authority, editable from the app, and the sheet is gone. |
| 10 | Region-gated sources | Every block in `config/sources.yaml` declares `regions:` (a list from `config/geo.yaml`'s region names, or `global`). `config.sources()` enables a source when its regions meet the profile's coverage: the regions of `profile.locations` resolved through `geo.yaml`, plus `work_authorization.relocation_regions`; `global` always. `sources.local.yaml` can force any source on or off with `enabled:`. `discover` prints one line per source skipped by region, naming the key that forces it. European sources are added after a verification pass (live request, terms check, yield), the way `docs/history/new-sources.md` was done; Santiago picks from the verified list; they ship in the tree and stay off for a profile that does not cover Europe. | The author's LatAm sources stay useful; a European user gets European boards; nobody inherits someone else's geography. |
| 11 | Cuts | Removed from the tree: the `dreamsheet` adapter and its Drive step in `/jh-discover` and `/jh-hunt`; `mac/`, `run.sh`, `scripts/ai_pass.sh` and the scheduling sections of the README (scheduling is one paragraph in `docs/`: run `hunt run` from cron or launchd, nothing shipped); the `sm.xml` line in `.gitignore`. `src.notify` stays (the digest is useful without a scheduler and is already opt-in). | Three things only the author's machine could run. `.github/workflows/claude-review.yml` stays (corrected 2026-10-06): it is the project's second-pass code reviewer, Cursor hands off to it with `@claude Claude gate: PRA-xxx`, and it runs on GitHub, not on the author's machine. |
| 12 | History docs | `docs/IMPROVEMENT_PLAN.md`, `docs/new-sources.md` and `docs/token-efficiency.md` move to `docs/history/` with a one-line header ("the author's record, kept for the numbers"); links in `CLAUDE.md` and the specs follow. Specs stay where they are with their dated attributions. | A stranger reads specs to understand the code; the reports are provenance. |
| 13 | Test matrix | Santiago runs the full flow (clone into a temp dir, `setup.sh`, `/jh-setup` on his own documents, a hunt to a tailored application) on claude, codex and pi. A friend runs it once on their own CLI and resume from the README alone and reports where they stopped. Each stop is a story in the last phase; the README's final pass comes after both. | Proof on three harnesses and two people before the post. |
| 14 | Onboarding token budget | The interview reads each extracted document once, writes each file once, and ends under 0.3M context tokens for a three-document intake; the helper prints per-document sizes so the agent can refuse a 40-page PDF politely and ask for the relevant pages. | `docs/history/token-efficiency.md` rules, applied to setup. |
| 15 | Stats screen (added 2026-10-06) | Section 4 of the TUI stops printing `stats funnel` and answers "is my search working, and where is it leaking?" on one screen, in-process from one `data.stats()` snapshot over the functions that already exist (`stats.funnel_data`, `calibration_data`, `latency_data`, `hunts_data`, `report.reached_stages`, `report.source_health`). One column in the scroll pane, `r` `j` `k` `g`, no drill-down, no subprocess, no new dependency. Top to bottom: **header**, the last discover (date and age, warning color past 7 days) and the last hunt (units, failed, context tokens, cost, a dash where the harness reports none); **tiles**, applications, reply rate labelled "any reply, rejections count", median days to first reply, waiting, in interviews, applied in the last 7 and 28 days; **funnel** bars, found, scored, shortlisted, applied, replied, screen, interview, offer, each with its count, on two scales (found, scored and shortlisted against found; applied onward against applied, so 121 applications never draw as a sliver under 49,727 found rows), a percent of the previous bar from applied on only, and a zero bar naming the step that fills it (`scored 0: run match in section 5`); **score vs reply**, reply rate per score band with n, a band under 5 dimmed, one line until 20 applications; **sources**, one row each with pulled and new over its last 5 runs, applied, replies, reply rate and the dead flag, dead first, then by applied. Cut: a weekly chart and comp (back to `docs/spec-tui.md` section 9). Reviewed by a contrarian agent the same day: it cut the sparkline, the two-column layout and "open pipeline" (that tile counted the shortlist), and added the empty state and the discover age; calibration stays, gated. | Strangers open the TUI next, and a section labelled "placeholder" reads as unfinished. Every tester's DB starts empty (the full-flow runs end at a tailored application, nobody applies), so the day-1 screen is the one designed first. The discover age is there because the author's own `runs` table stopped on 2026-09-07 and nothing on screen said so. |

Routine calls made without a question: the installer's harness list is `claude`, `codex`,
`opencode`, `pi`, `gemini`, `agy` (the shipped adapters plus the documented template);
`python -m src.setup --check` reports without writing; the interview runs in whatever
language the user writes in but writes the files in the language of the user's documents;
zero em-dashes in anything generated, including the files the interview writes.

## 3. The user's first hour

```
git clone https://github.com/<you>/jobhunt.git && cd jobhunt
./setup.sh
  which agent CLIs do you use?  [x] claude  [ ] codex  [x] pi   (found on PATH: claude, pi)
  venv, deps, init: 6 files from the examples
  default harness: claude (hunt.toml)      doctor claude: ok      doctor pi: ok
  next: open claude here and run /jh-setup
claude
> /jh-setup
  drop your documents (resumes, cover letters, LinkedIn "Save to PDF" or data export) ...
  ... master resume written: 4 roles, 3 projects, 22 skills, every one traced to a document
  ... profile: titles, families, locations, comp, dealbreakers, dream companies (5)
  ... sources for north_america + latam: 9 on, 3 need a key (adzuna, findwork, themuse)
  ... greenhouse tokens verified: 6 of 7 (one returned 0 jobs, kept as a note)
  ... .env: 2 keys set, 1 skipped;  mail: skipped
  ... doctor ok; discover: 1,214 rows;  run /jh-hunt when ready
```

## 4. Files

| Path | Change |
|---|---|
| `src/setup.py` | new: detect CLIs, ask, venv + deps (or reuse), `init`, `set_default_harness`, `doctor` per harness, the next-step line; `--harness`, `--yes`, `--check` |
| `setup.sh` | thin: python check, then `python -m src.setup "$@"` |
| `prompts/commands/*.md` | new: the one source per command; `.claude/commands/*.md` become renders |
| `src/hunt/prompts.py` | renders commands per harness beside agents; `NATIVE` grows a commands row per harness; `AGENTS.md` render for harnesses without a command format |
| `src/onboard.py` | new: `extract <files...>`, `check {resume|profile}`, `write {resume|profile|sources|env|dream} <json or file>`, `sources` (proposal from coverage), `verify-token <source> <token>`, `linkedin <url>` (opt-in fetch), `summary` |
| `prompts/commands/jh-setup.md` | new: the interview script, section by section, with the helper calls |
| `src/db.py` | `dream_companies` table + accessors; `query dream` |
| `src/dream.py` | reads the table; `init` migration from the profile list |
| `src/tui/` | Dream tab in the status list (`a`, `x`); Keys tab in the settings modal; `data.stats()` and the stats screen (section 4) |
| `src/config.py` | `sources()` region gate and coverage; `env` one-line editor (shared by onboarding and the Keys tab) |
| `config/sources.yaml` | `regions:` on every block; the verified European blocks |
| `config/geo.yaml` | region names the gate and the profile share; any region the EU sources need |
| `src/discover.py` | the skipped-by-region lines |
| removed | `src/adapters/dreamsheet.py`, `mac/`, `run.sh`, `scripts/ai_pass.sh` |
| moved | `docs/{IMPROVEMENT_PLAN,new-sources,token-efficiency}.md` to `docs/history/` |
| `README.md`, `CLAUDE.md`, `docs/hunt-harnesses.md` | the setup flow, the command table per harness, the region gate, the cuts |
| `tests/` | every new module on fixtures; the command renders checked like the agent renders; a golden interview transcript replayed against `src.onboard` with the fake documents (Alex Example's resume as PDF and docx, generated by `scripts/gen_fixtures.py`) |

## 5. Non-goals

A pip or uvx package (after feedback). A hosted or web version. Scraping a logged-in LinkedIn
or any job board. Rendering per-user native files. Multi-profile support. Rewriting the
private repo's history. Any change to what counts as a fit (`profile.yaml` semantics) or to
the hunt orchestrator's stages.

## 6. Phases, PRs and stories

One PR per phase, one commit per story, stories land in the listed order. Every story keeps
`ruff`, `mypy` and `pytest` green (`set -o pipefail` before claiming green) and the CI `clone`
job green. Zero em-dashes in any generated text. Linear mirrors this section: one parent issue
per PR, one sub-issue per story.

### PR 1: `docs/spec-pre-release`

1. This document.

### PR 2: `feat/cut-personal`

1. **Cuts**: decision 11, with every reference in `CLAUDE.md`, the README, the commands, the
   tests and the specs updated; the guard test and the clone job stay green.
2. **History docs**: decision 12.
3. **Dream companies table**: decision 9, the `db` accessors, `query dream`, `src.dream` on the
   table, the `init` migration (a profile with a list gets it moved and a dated note; a second
   run moves nothing), `tailor_bundle`, `match` and `pick` unchanged in behaviour; tests on a
   temp DB.
4. **Dream tab in the TUI**: add, remove, the board filters by it; pilot tests.

### PR 3: `feat/region-sources`

1. **Region gate**: decision 10 in `config.sources()`, `regions:` on every existing block
   (the LatAm ones `[latam]`, the aggregators `[global]`, the ATS families `[global]`, the
   EU ones already present `[europe]`), the `discover` lines, the forcing key, tests on the
   fixture profile (Lisbon covers `europe`, not `latam`).
2. **European sources, verified**: a research pass in the `docs/history/new-sources.md` form
   (live request, terms, yield, what the response carries) over the candidate boards, written
   to `docs/sources-europe.md`; Santiago picks which to wire. No code in this story.
3. **European sources, wired**: one adapter and one block per picked board, each with a
   fixture from a real response, off for a profile that does not cover Europe.

### PR 4: `feat/front-door`

1. **Commands as one source**: `prompts/commands/`, the claude render byte-identical to
   today's files (proved by the test before the old files are deleted), `sync-agents --check`
   covering them.
2. **Fan-out commands delegate**: decision 5; the `jh-hunt` skill is the same viewer it is
   today, `jh-triage` and `jh-match` become `hunt run --only` viewers.
3. **Renders per harness**: decision 4 for opencode, gemini, pi, codex, agy; each format
   verified against the CLI's own loader where one exists and recorded in
   `docs/hunt-harnesses.md`; `AGENTS.md` for the rest.
4. **Installer**: decision 3, `src/setup.py`, the thin `setup.sh`, `--check`; a test on a temp
   tree with fake binaries on PATH.

### PR 5: `feat/onboarding`

1. **Extraction and checks**: `src.onboard extract` (PDF, docx, md, txt, csv, the LinkedIn zip),
   `check resume`, `check profile`; fixtures: Alex Example's resume as PDF and docx generated
   by `scripts/gen_fixtures.py` so the fake person has documents to import.
2. **Writers**: `write {resume|profile|sources|env|dream}` with validation, the show-diff-and-ask
   rule for an existing file, the shared `.env` one-line editor.
3. **Sources and tokens**: `sources` (the proposal from coverage, with keyed ones marked and
   their URLs), `verify-token` (one live request per token, 200 and a non-empty board).
4. **The interview**: `prompts/commands/jh-setup.md`, section by section, every write through
   the helper, the provenance list, the token budget (decision 14); a golden transcript test
   that replays the helper calls the interview makes on the fixture documents.
5. **LinkedIn URL opt-in**: decision 7's fetch, the warning, a fixture of a public page.
6. **Keys tab**: decision 8 in the TUI settings modal; pilot tests.

### PR 6: `feat/tui-stats`

1. **Stats data**: `data.stats()` returns one frozen snapshot for decision 15, built from the
   existing functions plus the found and scored counts, the 7 and 28 day application counts and
   the last discover time; `data.py` stays the only TUI module that opens SQLite; tests on
   `tmp_db` for an empty DB, a day-1 DB (discovered rows only) and a seeded DB with events.
2. **Stats screen**: section 4 renders the snapshot in-process (pure renderers for the bar, the
   tile and the table, tested without the app), the zero-bar next steps, the small-n dimming,
   the 20-application gate; pilot tests replace the placeholder ones in `tests/test_tui_stats.py`;
   `docs/spec-tui.md` decision 4, `CLAUDE.md` and the README say what section 4 shows.

### PR 7: `test/full-flow`

1. **Three harnesses**: the decision 13 runs on claude, codex and pi, each recorded in
   `docs/history/full-flow-<date>.md` (what was typed, what stopped, tokens from the ledger);
   each stop fixed as its own commit in this PR.
2. **The friend's run**: their stops as stories here, or as issues if they need a phase.
3. **README final pass**: the setup flow as it really went, the command table per harness, the
   regions paragraph, the cuts gone from the text.

Then `docs/spec-open-source.md` section 7 steps 3 to 7 on the resulting `main`.
