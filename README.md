# jobhunt

A job-search copilot you run on your own machine for $0 in software: free job APIs, a SQLite
CRM, a terminal UI, and an agent CLI you already pay for (Claude Code by default; Codex,
OpenCode, pi and Antigravity work too) doing the reading and the writing. It discovers roles,
throws out the junk, scores what is left against your profile, researches the company, and
drafts a tailored resume and cover letter per role. Then it stops.

**You click submit.** Nothing here submits an application, logs into LinkedIn or Indeed, or
sends mail on your behalf. Mass auto-apply converts at about the rate of cold applying and gets
accounts banned; ten to twenty tailored applications a week to roles that actually fit is the
thing this tool is built to make cheap.

Two rules every agent in the repo is held to:

- **Nothing is invented.** A tailored resume only reframes what is in your master resume.
  A cover letter only cites what the company dossier cites. Learning plans never feed a resume.
- **Discovery is free and ToS-safe.** Public ATS APIs and aggregators only. The Indeed/LinkedIn
  scraper (`jobspy`) ships off and stays off unless you turn it on and accept the risk.

## Five-minute setup

You need Python 3.11+, git, and one agent CLI on your PATH (`claude`, `codex`, `opencode`,
`pi` or `agy`), signed in.

```bash
git clone https://github.com/<you>/jobhunt.git && cd jobhunt
./setup.sh                        # venv, deps, then `python -m src.init`
source .venv/bin/activate
```

`python -m src.init` creates every user-owned file from its tracked example and never
overwrites one. The person in those files is invented ("Alex Example", full-stack, Lisbon), so
the whole pipeline runs end to end on a clone before you touch anything. Then make it yours:

1. `config/profile.yaml`: what a fit is. Target titles, must-have skills, locations and the
   location rule, comp floor, dealbreakers, dream companies, the one-line `candidate_line`
   and the `role_families` the prompts weight by. Every key is documented inline.
2. `resume/master_resume.yaml`: your whole career, true and complete. This is the only source
   the tailor may draw from. `resume/answers.yaml` is the answer bank for application forms.
3. `config/sources.local.yaml`: where to look. ATS tokens of companies you follow, countries
   and locales for the aggregators, query lists. Everything in it ships commented out, so an
   unedited clone searches nowhere rather than somewhere that belongs to someone else.

Then pick the harness and check it:

```bash
python -m src.hunt doctor                 # binary, sign-in, each stage's model, a smoke prompt, a read probe
python -m src.hunt models                 # the live catalog, to set per-stage models in config/hunt.toml
python -m src.init --check                # every user file present, every profile key set
```

`config/hunt.toml` says how the hunt runs (harness, per-stage model, concurrency, timeouts,
retries). `config/profile.yaml` says what counts. The two never overlap.

Optional: `.env` holds keys for the keyed sources (Adzuna, Findwork, Careerjet, The Muse) and
the app passwords for the read-only inbox pull (`docs/mail-setup.md`). A source with no key
prints a hint and yields nothing; it never breaks a run.

## The pipeline

| Stage | What happens | Run it |
|---|---|---|
| Discover | Free ATS APIs and aggregators into SQLite (`data/jobs.db`); a shared title gate keeps off-family reqs out; vanished postings expire | `python -m src.discover` |
| Triage | Cheap keep/drop against your dealbreakers, keepers get a 0 to 3 fit bucket; runs before the expensive matcher | `/jh-triage` |
| Match | Scores each keeper against the profile with a written verdict; shortlists above your threshold | `/jh-match` |
| Research | Cited company dossier in `research/companies/`, reused by every later step | `/jh-research <company or id>` |
| Tailor | One-page resume plus cover letter in `applications/pending/<company>-<id>/`, built, audited and page-counted by Python | `/jh-tailor <id>` |
| Apply | You read the draft, fix what you want, and submit | you |
| Track | Status pipeline, follow-up dates, inbox signals, funnel stats | `python -m src.tui`, `/jh-followups`, `/jh-gmail-sync` |
| Learn | Skill-gap analysis, interview prep briefs, interview debriefs, a monthly calibration review | `/jh-upskill`, `/jh-prep`, `/jh-debrief`, `/jh-review` |

The whole loop, end to end, is one command:

```bash
python -m src.hunt run                    # discover, triage, match, inbox, pick 5, research, tailor, report
python -m src.hunt status latest          # while it runs
python -m src.hunt report latest          # units, retries, tokens per stage, what needs a human
python -m src.hunt run --resume latest    # after a Ctrl+C or a crash: done units are skipped
python -m src.hunt run --dry-run          # the plan, no calls
```

Each unit of model work (one triage chunk, one match chunk, one dossier, one tailor) is one
process of your agent CLI, run in parallel up to the caps in `hunt.toml`. Python decides when
a unit is done by checking its output file, never by trusting the agent. Only Python writes the
database. The run's ledger lives in `data/hunt/<run_id>/` (state, events, every prompt, every
log); a question a run cannot ask you becomes a `needs_human` line in its report.

The `/jh-*` slash commands are the same stages driven interactively from Claude Code, one at a
time, with you in the loop. `python -m src.tui` is the CRM: the board, follow-ups, the
application folders, the funnel, a runner that starts any stage or the full hunt with its log
beside it, and the config files. `scripts/install_launcher.sh` makes it one word (`jobhunt`).

Recording a submission moves the folder and schedules the follow-up in one write:

```bash
python -m src.query set-status 42 applied
```

## What it costs in tokens

Measured on the author's hunts (`docs/token-efficiency.md`), on a pile of a few thousand
discovered rows; your ledger prints your own numbers (`python -m src.hunt report`,
`python scripts/token_audit.py --hunt latest`):

- Triage: about 80k context tokens per 100-row chunk on the cheapest model.
- Match: 0.1M to 0.8M per 60-row chunk.
- Research: 0.1M to 0.8M per dossier, once per company, then reused.
- Tailor: 45k to 165k per application, 3 to 4 calls, because the agent reads one bundle,
  writes one draft, and Python builds it.

A full hunt that tailors five applications runs in the low tens of millions of context tokens,
almost all of it in the fanned-out units, so the model in each stage is the lever:
`hunt.toml` ships the cheapest model that does each job well (a small model for triage, a large
one for the writing). Pick the models from `python -m src.hunt models` on your harness.

## Adding a source

A source is one Python file in `src/adapters/` exposing `fetch(cfg) -> list[Job]` and one
block in `config/sources.yaml` with its mechanics (endpoint, page size, `enabled:`, field
mapping). Targeting for it (tokens, countries, queries) goes in `config/sources.local.yaml`,
which is deep-merged onto the tracked block at load time: lists replace, scalars override.
Read a small one first (`src/adapters/jobicy.py`) and the shared title gate at the bottom of
`sources.yaml`. Never filter by location in an adapter; `profile.yaml`'s `location_rule` is
the one authority and the matcher applies it. `docs/new-sources.md` is the research behind
the sources that ship and the ones that were rejected, with the reasons.

## Adding a harness

Any agent CLI that takes a prompt and prints a reply is a five-line command template in
`config/hunt.toml`, no Python:

```toml
[harness.gemini]
command = "gemini -m {model} --approval-mode auto_edit -o json -p {prompt}"
envelope = "json"
capabilities = ["read", "write", "edit", "bash", "web"]
```

`docs/hunt-harnesses.md` has the placeholders, the envelope rules, and what each shipped
adapter (claude, codex, opencode, pi, agy) runs. Write a Python adapter only when the CLI
needs what a template cannot express: a model catalog, an event stream to sum, native agent
files. Agent prompts live once in `prompts/agents/<role>.md`; `python -m src.hunt sync-agents`
renders each harness's native files from them, and CI checks they match.

## Your data stays yours

Everything derived from your career or your targeting is git-ignored and created by `init`
from a tracked `*.example.*`: the profile, the master resume, the answer bank, the local
sources file, `.env`, `data/`, `applications/`, `interviews/`, `research/companies/`.
A guard test refuses to track any of them. `scripts/backup_user_data.sh` copies the lot to
`~/jobhunt-user-data/<date>/` with counts and checksums; keeping that folder in a private repo
of your own is a good idea.

Optional: write `config/identity.local.yaml` (see the `.example`) with your name, addresses and
phone, and the guard also refuses any tracked file that mentions them.

## Development

```bash
.venv/bin/python -m pytest tests/       # the suite runs on a clone with no user files
ruff check src tests scripts && mypy    # CI runs all three, plus `sync-agents --check`
```

Tests never start a real agent CLI (`tests/conftest.py` refuses); a fake harness stands in.
The one exception is the opt-in smoke, `HUNT_SMOKE=1 pytest -m harness_smoke`, one 10-token
call per installed CLI. The specs under `docs/` are the design record: `spec-hunt-orchestrator.md`,
`spec-tui.md`, `spec-tailor-lean.md`, `spec-open-source.md`. `CLAUDE.md` is the project guide
the agents read.

## Ground rules, once more

- Never fabricate. Tailoring reframes; it does not add.
- Never auto-submit, never automate a logged-in job board.
- Free, sanctioned endpoints only.
- ATS-clean output: one column, standard headings, no tables or images, no white-text tricks.

MIT licensed (`LICENSE`). Not legal advice; respect each site's terms of service, and you are
responsible for how you use it.
