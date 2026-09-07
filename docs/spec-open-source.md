# Spec: open-source release (user data out of the repo, profile-driven prompts)

Status: draft for review, 2026-09-07 (Santiago + Fable). Lands before `feat/hunt-core`
(`docs/spec-hunt-orchestrator.md` PR 2), because that PR creates `prompts/agents/` and the
prompts must be written profile-driven from the start. The public release itself is the last
phase and happens after the orchestrator and the TUI land.

## 1. Why

The repo is going public. Today it is one person's hunt: the master resume, the answer bank,
117 company dossiers, the original CVs, the profile with dream companies and visa status, and
the Greenhouse token list are all tracked, and the code, prompts, tests and docs name that person,
their city and their visa in about forty places. A stranger who clones it gets someone else's
career, and cannot run it without editing source.

Two facts shape the plan:

1. **Git history keeps everything.** Adding a path to `.gitignore` does not remove it from past
   commits. A public push of this repository publishes every version of every tracked file.
   The release therefore starts a **new public repository from a clean tree**; this one stays
   private as the archive.
2. **Personal data is not only in data files.** The triage rubric, the matcher, the tailor and
   the researcher prompts, `tailor_build`'s header check, `render_docx`'s visa line, the Torre
   adapter's timezone, the deliverable file names and the docs all carry the author. Those
   become template slots filled from `config/profile.yaml`.

## 2. Decisions (settled 2026-09-07, do not re-open without a reason)

| # | Decision | Choice | Why |
|---|----------|--------|-----|
| 1 | Public repo | A fresh repository seeded from a clean snapshot with one initial commit. The current repo is renamed `jobhunt-private` and kept as history. Development moves to the public repo after the release; the author's private files live on disk in the ignored paths. | History rewriting with `filter-repo` on a repo this size and this personal is more work and more risk than a clean seed. |
| 2 | User file pattern | Tracked `*.example.*` next to an ignored real file, the pattern `.env.example` already uses. `python -m src.init` copies every example to its real name when the real one is missing, never overwrites. | One convention, already known in the repo, no home-directory relocation. |
| 3 | What is user data | `config/profile.yaml`, `config/sources.local.yaml`, `config/notify.yaml`, `resume/master_resume.yaml`, `resume/answers.yaml`, `resume/originals/`, `research/companies/`, `research/upskill/`, `research/aliases.yaml`, `applications/`, `interviews/`, `data/`, `.env`. Everything else is the product. | Anything derived from one person's career or one person's targeting. |
| 4 | Sources split | `config/sources.yaml` stays tracked and generic (every adapter block, token lists empty, `dreamsheet` disabled). `config/sources.local.yaml` (ignored, example tracked) is deep-merged on top per source block at load time: lists replace, scalars override, unknown sources are added. | The adapter config is product; which companies' boards to poll is targeting. |
| 5 | Deliverable names | `SantiagoCoronadoResume.*` becomes `<FirstLast>Resume.*`, derived from `profile.name` by `config.resume_basename()`. `CoverLetter.*` stays. `tailor_build`, `tailor_bundle`, `export_pdf.sh`, the tailor prompt and the tests read the helper. Existing folders keep their old file names; `reconcile` reports them, never renames. | A file name with the author's name in it is the most visible leak. |
| 6 | Profile-driven prompts | Every personal fact in a prompt becomes a slot filled from `profile.yaml` at assembly time (the orchestrator's decision 7 already assembles prompts in Python). New profile keys: `candidate_line`, `role_families`, `work_authorization`, `header_location`. Nothing in `prompts/agents/`, `.claude/agents/` or `.claude/commands/` names a person, a city or a visa after this. | The rubric text "Santiago, founder-engineer, Mexico City, TN-visa eligible" is exactly what a second user must not inherit. |
| 7 | Code constants | `tailor_build`'s relocation header check, its city and region lists, `match.py`'s LATAM and Mexico regexes, `render_docx`'s visa item, `torre.py`'s timezone, `answers_export`'s wording and `pick.py`'s docstring read from the profile (`header_location`, `locations`, `timezones`, `work_authorization`) or a new tracked `config/geo.yaml` (city to region table, product data). | Location logic is product; which region is home is profile. |
| 8 | Tests | No test reads a real user file. `tests/fixtures/` gets a full fake person (`profile.yaml`, `master_resume.yaml`, `answers.yaml`) and tests point `config.CONFIG_DIR` and the resume paths there. The example files and the fixtures are the same content, generated from one source so they cannot drift. | CI has no user files, and a stranger's `pytest` must pass on a fresh clone. |
| 9 | Guard test | `tests/test_no_user_data.py` fails if any tracked path under `config/`, `resume/`, `research/`, `applications/`, `interviews/` is not an `*.example.*`, a `README.md`, `.gitkeep`, or on an explicit product allowlist (`sources.yaml`, `skills_lexicon.yaml`, `mail_hints.yaml`, `hunt.toml`, `tui.toml`, `geo.yaml`); and if any tracked text file outside `docs/` matches the author's name or email. | The rule that keeps the next contributor from committing their resume. |
| 10 | Docs | `CLAUDE.md`, `README.md`, the agent files and the commands lose the author's name entirely. Specs under `docs/` keep dated decisions but attribute them to "the author"; measured numbers stay. `docs/writing-voice.md` stays as product guidance. The memory directory is per machine and never in the repo. | Specs are history and useful to a reader; a name in a rule is a leak, a name in a dated decision is provenance. |
| 11 | Licence | MIT. `LICENSE` at the root, copyright the author. | Permissive, the default for a personal tool people fork. |
| 12 | README | Rewritten for a stranger: what it is, the human-on-submit rule, five-minute setup (`init`, fill the three files, pick a harness with `hunt doctor`), the pipeline table, the token-cost expectations, how to add a source, how to add a harness. | Today's README assumes the author's machine. |
| 13 | Release checklist | Executed once, in order, in section 7. Secrets scan on the clean tree, name and email grep, fresh repo, one commit, CI green, branch protection, then the private rename. | A checklist because it happens once and cannot be undone. |

Routine calls made without a question: `init` prints what it copied and what it skipped; examples
carry a fake person named "Alex Example" with a plausible mid-level full-stack profile so every
stage runs end to end on a clone; the `dreamsheet` adapter stays in the tree, disabled in the
tracked `sources.yaml`, documented as optional; zero em-dashes in anything generated.

## 3. File classification

| Path | Public repo | Note |
|---|---|---|
| `config/profile.example.yaml` | tracked | full fake profile, every key documented inline |
| `config/profile.yaml` | ignored | the user's |
| `config/sources.yaml` | tracked | generic adapter config, tokens empty, `dreamsheet: enabled: false` |
| `config/sources.local.example.yaml` | tracked | shows token lists and the dreamsheet block |
| `config/sources.local.yaml` | ignored | deep-merged on top |
| `config/notify.yaml.example` | tracked (exists) | |
| `config/skills_lexicon.yaml`, `config/mail_hints.yaml`, `config/hunt.toml`, `config/tui.toml`, `config/geo.yaml` | tracked | product data |
| `resume/master_resume.example.yaml`, `resume/answers.example.yaml` | tracked | Alex Example |
| `resume/master_resume.yaml`, `resume/answers.yaml`, `resume/originals/` | ignored | |
| `research/README.md`, `research/aliases.example.yaml` | tracked | |
| `research/companies/`, `research/upskill/`, `research/aliases.yaml` | ignored | dossiers are the user's research |
| `applications/.gitkeep`, `interviews/.gitkeep` | tracked | folders exist on clone |
| `applications/`, `interviews/`, `data/` | ignored (already) | |
| `prompts/agents/*.md`, generated native agent files | tracked | profile-driven, no person in them |
| `.env.example` | tracked (exists) | |

`.gitignore` after the change (the new lines):

```
config/profile.yaml
config/sources.local.yaml
resume/master_resume.yaml
resume/answers.yaml
resume/originals/
research/companies/
research/upskill/
research/aliases.yaml
```

In the private repo these files are removed from the index with `git rm --cached` and stay on
disk. The author may keep them under their own private git repo elsewhere; the product does not
depend on that.

## 4. Profile keys added

```yaml
name: Alex Example
candidate_line: >-                     # one sentence the triage and match prompts open with
  Alex, full-stack engineer, Lisbon, bilingual PT/EN, EU work authorization.
role_families:                         # ordered, the letters are what the prompts use
  - key: A
    name: hands-on full-stack engineering
    titles: [Full-Stack Engineer, Software Engineer, Product Engineer]
    skills: [TypeScript, React, Node, Postgres]
    strength: core
  - key: B
    name: frontend engineering
    titles: [Frontend Engineer, UI Engineer]
    skills: [React, TypeScript, Vite]
    strength: strongest                # strongest | core | adjacent; the prompts weight by this
work_authorization:                    # rendered in the resume header and told to the prompts
  summary: EU citizen, no sponsorship needed in the EU
  header_item: EU Work Authorization   # empty string = nothing in the header
header_location: Lisbon, Portugal      # what the tailored resume header must say
```

Existing keys (`target_titles`, `locations`, `timezones`, `comp`, `location_rule`,
`dealbreakers`, `dream_*`, `relocation_line`, `notes`) keep their meaning. `config.profile()`
validates the new keys with defaults so an old profile still loads, and `init` migrates the
author's real profile by appending the new keys with the current hardcoded values.

## 5. Prompt slots

| Prompt | Today | After |
|---|---|---|
| triager (from `jh-triage.md`) | "Candidate: Santiago, founder-engineer, Mexico City, bilingual ES/EN, TN-visa eligible" and four hand-written families | `{candidate_line}` and `{role_families}` rendered as the lettered list, `strength` deciding the "bucket good ones 2-3" line |
| job-matcher | the same four families and "he rates C and D as his two strongest" | same slots; pronoun-free wording ("the candidate") |
| resume-tailor | five mentions of the author, the file name, the header rule | `{resume_basename}`, `{header_location}`, `{work_authorization.summary}`, "the candidate" |
| company-researcher | four mentions, "Santiago will use" | "the candidate" |
| inbox-classifier (from `jh-gmail-sync.md`) | account labels and the author's addresses in examples | `{mail_accounts}` from `.env` labels |
| `/jh-upskill`, `/jh-tailor`, `/jh-triage`, `/jh-gmail-sync` command files | one mention each | none |

The orchestrator's prompt assembler (`docs/spec-hunt-orchestrator.md` section 4) fills the slots.
For interactive use, `sync-agents` fills them at generation time and the generated native agent
files are committed with the **example** profile's values; `init` regenerates them for the user's
profile after the copy, and the guard test checks that the committed ones match the example.

## 6. Code changes by file

| File | Change |
|---|---|
| `src/config.py` | `profile()` with validation and defaults for the new keys; `resume_basename()`; `sources()` doing the `sources.local.yaml` deep merge |
| `src/init.py` | copy examples, migrate an existing profile, regenerate native agent files, print a summary; idempotent |
| `src/discover.py` | reads `config.sources()` |
| `src/tailor_build.py` | `ALLOWED_FILES`, `REQUIRED_FILES`, the YAML path and the header check from `resume_basename()` and `header_location`; city and region lists from `config/geo.yaml` |
| `src/tailor_bundle.py` | existing-draft path from `resume_basename()`; "Santiago's own judgment" becomes "the user's own judgment" |
| `src/match.py` | region regexes built from `profile.locations` and `geo.yaml` |
| `src/render_docx.py` | header item from `work_authorization.header_item` instead of sniffing "tn visa" |
| `src/adapters/torre.py` | timezone from `profile.timezones` |
| `src/answers_export.py`, `src/pick.py` | wording |
| `scripts/export_pdf.sh` | file pattern from `python -m src.config resume-basename` |
| `tests/` | fixtures for the fake person; `test_tailor_bundle`, `test_tailor_build`, `test_adapters`, `test_pick`, `test_mail_fetch`, `test_render_cover_letter`, `test_answers_export`, `test_data_quality` stop reading real files or the author's name |
| `tests/test_no_user_data.py` | the guard from decision 9 |
| `.gitignore` | section 3 |
| `CLAUDE.md`, `README.md`, `.claude/agents/*.md`, `.claude/commands/*.md`, `docs/*.md` | name pass per decision 10 |

## 7. Release checklist (run once, in this order)

1. All phases below merged; orchestrator and TUI landed; `pytest` green on a clone with no
   user files (`git clone` into a temp dir, `python -m src.init`, `pytest`).
2. `python -m src.init` output reviewed: every example copies, every stage runs on Alex Example
   through `python -m src.hunt run --dry-run`.
3. Secrets and identity scan on the clean tree: `gitleaks detect --no-git`, then a grep for the
   author's name, both email addresses, the phone number, the Google Sheet id, every token in
   `sources.local.yaml`. Zero hits outside `docs/` provenance lines.
4. Create the public repo empty, no template. From the clean tree: `git init`, one commit
   "jobhunt: initial public release", push. Enable CI, protect `main`, require the checks.
5. Rename this repository `jobhunt-private`, keep it private, add a README line pointing at the
   public one. Move local development to a clone of the public repo; copy the ignored user files
   into it by hand once.
6. Tag `v0.1.0` on the public repo after the first green CI.

## 8. Non-goals

Multi-user support in one checkout. A hosted or web version. Relocating user files to a home
directory. Rewriting the private repo's history. Removing the author's dated decisions from the
specs.

## 9. Phases, PRs and stories

One PR per phase, one commit per story, stories land in the listed order. Every story keeps
`ruff`, `mypy` and `pytest` green (`set -o pipefail` before claiming green). Zero em-dashes in
any generated text. Phases 2 and 3 land **before** `feat/hunt-core`; phase 4 is the last thing
the project does before going public.

### PR 1: `docs/spec-open-source`

1. This document.

### PR 2: `feat/user-data-split`

1. **Examples**: `config/profile.example.yaml`, `config/sources.local.example.yaml`,
   `resume/master_resume.example.yaml`, `resume/answers.example.yaml`,
   `research/aliases.example.yaml` for Alex Example; `tests/fixtures/` generated from the same
   content by one script (`scripts/gen_fixtures.py`) and a test that they match.
2. **gitignore and index**: the section 3 lines; `git rm --cached` for every newly ignored path;
   `applications/.gitkeep` and `interviews/.gitkeep`.
3. **`config.sources()`** with the local deep merge; `discover` reads it; `sources.yaml` tokens
   emptied and `dreamsheet` disabled; the author's lists move to `sources.local.yaml`; tests.
4. **`resume_basename()`** and its use in `tailor_build`, `tailor_bundle`, `export_pdf.sh`,
   the tailor prompt; `reconcile` reports legacy file names; tests.
5. **`python -m src.init`**: copy, migrate, summary; test on a temp tree.
6. **Tests off real files**: every test in the section 6 list on fixtures; CI green with the user
   files absent (a CI step deletes them before `pytest` to prove it, until phase 4 makes that
   the natural state).
7. **Guard test**: `tests/test_no_user_data.py`.

### PR 3: `feat/profile-driven-prompts`

1. **Profile keys**: `candidate_line`, `role_families`, `work_authorization`,
   `header_location`; `config.profile()` validation and defaults; `init` migration; the
   author's real profile updated.
2. **Code constants**: `geo.yaml`; `tailor_build`, `match`, `render_docx`, `torre`,
   `answers_export`, `pick` per section 6; tests.
3. **Agent and command files**: slots per section 5 in `.claude/agents/*.md` and
   `.claude/commands/*.md` (these become `prompts/agents/` in `feat/hunt-core`, which starts
   from this state); the tailor and matcher run once on a real job to confirm no regression in
   the verdict and the letter.
4. **Docs pass**: `CLAUDE.md`, `README.md` (structure only, the stranger rewrite is phase 4),
   `docs/*.md` per decision 10.

### PR 4: `release/public` (after the orchestrator and the TUI)

1. **LICENSE** (MIT) and the README rewrite from decision 12.
2. **Clone test**: a CI job that clones, runs `init`, runs `pytest` and `hunt run --dry-run`
   on Alex Example.
3. **Checklist**: section 7, executed and ticked in the PR description; the tag.
