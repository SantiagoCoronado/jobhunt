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
| 2 | User file pattern | Tracked `<name>.example.<ext>` (infix) next to an ignored real file: `profile.example.yaml`, `master_resume.example.yaml`. The existing `config/notify.yaml.example` is renamed `notify.example.yaml`; `.env.example` is the one suffix form and stays. `python -m src.init` maps both forms and copies every example to its real name when the real one is missing, never overwrites. One exception: `config/identity.local.example.yaml` is documentation only and `init` never copies it; the user writes `identity.local.yaml` by hand when they want the guard's identity rule, because the example carries Alex Example's values and copying it would make the guard match the shipped example files and fixtures. | One convention (infix keeps editor highlighting), no home-directory relocation. |
| 3 | What is user data | `config/profile.yaml`, `config/sources.local.yaml`, `config/identity.local.yaml`, `config/notify.yaml`, `resume/master_resume.yaml`, `resume/answers.yaml`, `resume/originals/`, `research/companies/`, `research/upskill/`, `applications/`, `interviews/`, `data/`, `.env`. Everything else is the product, including `research/aliases.yaml` (a company slug table every user would otherwise rebuild). | Anything derived from one person's career or one person's targeting. |
| 4 | Sources split | `config/sources.yaml` stays tracked and carries adapter mechanics only: endpoints, rate limits, `enabled:`, field mappings. Everything that is targeting leaves it: ATS token lists, `dreamsheet`, Adzuna `countries`, Careerjet `locale_code` and `location`, Torre `countries`, every per-source keyword and query list. Those live in `config/sources.local.yaml` (ignored; the tracked example carries every targeting key **commented out** with Alex Example's Lisbon and EU values as the illustration, so an unedited clone searches nowhere rather than a fake person's country, and `discover` prints one hint naming the file when no source has targeting keys), deep-merged on top per source block at load time: lists replace, scalars override, unknown sources are added. `title_filter.include` is product data with a profile-derived extension, not a pure derivation: the tracked `sources.yaml` keeps the generic-engineering base list (`engineer`, `developer`, `programmer`, `architect`, `software`, `swe` and the rest of the current block, which `CLAUDE.md` records as calibrated 2026-08-27 to keep every row that ever reached shortlisted), and `config.sources()` appends every word from `profile.target_titles` and `role_families[].titles`; `sources.local.yaml` may extend it further. The family-specific comments and entries leave the tracked list. `tests/test_adapters.py:232` stays as the gate, and PR 2 story 3 re-runs the filter over the DB and proves that no row that ever reached `shortlisted` is dropped before the old list is touched. A source whose targeting keys are absent prints a hint and yields nothing, the way a keyed source without a key already does; no adapter keeps a country or locale default in code (`adzuna.py` `mx`, `careerjet.py` `es_MX` and `Mexico` go). | The adapter config is product; where to search and for what is targeting, and a stranger must never inherit someone else's country. |
| 5 | Deliverable names | The author's literal name stem becomes `<FirstLast>Resume.*`, derived from `profile.name` by `config.resume_basename()`. `CoverLetter.*` stays. `tailor_build`, `tailor_bundle`, `export_pdf.sh`, the tailor prompt and the tests read the helper. Normalization: NFKD fold to ASCII, drop everything but letters and digits, join the name parts in order, append `Resume`; an empty result falls back to `Resume` (`Zoë O'Brien-Smith` gives `ZoeOBrienSmithResume`). An optional `resume_basename:` profile key overrides the stem (same normalization, `Resume` appended once) for a shorter form of a long name (added in review of PR #21). Exposed as `python -m src.config resume-basename` for `export_pdf.sh`. Existing folders keep their old file names; `reconcile` reports them, never renames. | A file name with the author's name in it is the most visible leak. |
| 6 | Profile-driven prompts | Every personal fact in a prompt becomes a slot filled from `profile.yaml` at assembly time (the orchestrator's decision 7 already assembles prompts in Python). New profile keys: `candidate_line`, `role_families`, `work_authorization`, `header_location`. Nothing in `prompts/agents/`, `.claude/agents/` or `.claude/commands/` names a person, a city or a visa after this. Two render modes: the orchestrator inlines the values into each unit prompt under the ignored run folder; the committed native agent files never embed profile values, they tell the agent which `profile.yaml` keys to read (the matcher and the researcher already read the profile, the tailor gets it in the bundle). The tracked tree is therefore identical for every user and `init` never rewrites a tracked file. | The rubric text "Santiago, founder-engineer, Mexico City, TN-visa eligible" is exactly what a second user must not inherit. |
| 7 | Code constants | `tailor_build`'s relocation header check, its city and region lists, `match.py`'s LATAM and Mexico regexes, `render_docx`'s visa item, `torre.py`'s timezone, `stats.py`'s `FAMILIES` regexes (built from `role_families`, so `title_family` and `/jh-review` bucket by the user's families), `report.py`'s LatAm note, `answers_export`'s wording and `pick.py`'s docstring read from the profile (`header_location`, `locations`, `timezones`, `work_authorization`) or a new tracked `config/geo.yaml` (city to region table, product data). | Location logic is product; which region is home is profile. |
| 8 | Tests | No test reads a real user file. `tests/fixtures/` gets a full fake person (`profile.yaml`, `master_resume.yaml`, `answers.yaml`) and tests point `config.CONFIG_DIR` and the resume paths there. The example files and the fixtures are the same content, generated from one source so they cannot drift. | CI has no user files, and a stranger's `pytest` must pass on a fresh clone. |
| 9 | Guard test | `tests/test_no_user_data.py` fails if any tracked path under `config/`, `resume/`, `research/`, `applications/`, `interviews/` is not a `*.example.*` file, `.env.example`, a `README.md`, `.gitkeep`, or on an explicit product allowlist (`sources.yaml`, `skills_lexicon.yaml`, `mail_hints.yaml`, `hunt.toml`, `tui.toml`, `geo.yaml`, `research/aliases.yaml`); if any tracked text file outside `docs/` matches an identity pattern; and if any line under `docs/` matches one except a dated attribution. One generic rule is always on (added in the PR #21 review): no address at a personal mail provider and no phone-number-shaped string in product text (`src/`, `scripts/`, `config/`, `.claude/`, `.github/`, `CLAUDE.md`, `README.md`), placeholder local parts excepted. The identity patterns (name, both emails, phone, the old deliverable basename, the attribution regex) are read from the ignored `config/identity.local.yaml` (example tracked as `identity.local.example.yaml` with Alex Example's values, never copied by `init`), never written in the test, so the guard cannot match itself and cannot publish what it protects; when the file is absent the identity rule is skipped with a notice and only the path rule runs, which keeps a stranger's CI green. The identity rule is therefore opt-in: a fresh clone runs the path rule only, and the release checklist, which runs the guard with the author's file present, is the run that matters. | The rule that keeps the next contributor from committing their resume. |
| 10 | Docs | `CLAUDE.md`, `README.md`, the agent files and the commands lose the author's name entirely. Specs under `docs/` keep dated attributions; measured numbers stay. Literal product names in specs are converted: the author's resume stem becomes `<FirstLast>Resume.yaml` in `docs/spec-tailor-lean.md`, the author's memory path in `docs/token-efficiency.md` becomes `<project memory dir>`, so the guard's docs rule (decision 9) passes on attributions alone. `docs/writing-voice.md` stays as product guidance. The memory directory is per machine and never in the repo. | Specs are history and useful to a reader; a name in a rule is a leak, a name in a dated decision is provenance. |
| 11 | Licence | MIT. `LICENSE` at the root, copyright the author. | Permissive, the default for a personal tool people fork. |
| 12 | README | Rewritten for a stranger: what it is, the human-on-submit rule, five-minute setup (`init`, fill the three files, pick a harness with `hunt doctor`), the pipeline table, the token-cost expectations, how to add a source, how to add a harness. | Today's README assumes the author's machine. |
| 13 | Release checklist | Executed once, in order, in section 7. Secrets scan on the clean tree, name and email grep, fresh repo, one commit, CI green, branch protection, then the private rename. | A checklist because it happens once and cannot be undone. |

Routine calls made without a question: `init` prints what it copied and what it skipped; examples
carry a fake person named "Alex Example" with a plausible mid-level full-stack profile so every
stage runs end to end on a clone; the `dreamsheet` adapter stays in the tree, configured only
from `sources.local.yaml`, documented as optional; zero em-dashes in anything generated.

## 3. File classification

| Path | Public repo | Note |
|---|---|---|
| `config/profile.example.yaml` | tracked | full fake profile, every key documented inline |
| `config/profile.yaml` | ignored | the user's |
| `config/sources.yaml` | tracked | adapter mechanics and the generic-engineering `title_filter` base only; no tokens, countries, locales, queries or dreamsheet block |
| `config/sources.local.example.yaml` | tracked | token lists, dreamsheet block, countries, locales, query lists for Alex Example |
| `config/sources.local.yaml` | ignored | deep-merged on top |
| `config/identity.local.example.yaml` | tracked | the guard's pattern file, Alex Example values, documentation only, `init` skips it |
| `config/identity.local.yaml` | ignored | the author's name, emails, phone, old basename, written by hand |
| `config/notify.example.yaml` | tracked | renamed from `notify.yaml.example` |
| `config/skills_lexicon.yaml`, `config/mail_hints.yaml`, `config/hunt.toml`, `config/tui.toml`, `config/geo.yaml`, `research/aliases.yaml` | tracked | product data |
| `resume/master_resume.example.yaml`, `resume/answers.example.yaml` | tracked | Alex Example |
| `resume/master_resume.yaml`, `resume/answers.yaml`, `resume/originals/` | ignored | |
| `research/README.md` | tracked | |
| `research/companies/`, `research/upskill/` | ignored | dossiers and learning plans are the user's |
| `applications/.gitkeep`, `interviews/.gitkeep` | tracked | folders exist on clone |
| `applications/`, `interviews/`, `data/` | ignored (already) | |
| `prompts/agents/*.md`, generated native agent files | tracked | slots point at profile keys, no values embedded, identical for every user |
| `.env.example` | tracked (exists) | |

`.gitignore` after the change (the new lines):

```
config/profile.yaml
config/sources.local.yaml
config/identity.local.yaml
resume/master_resume.yaml
resume/answers.yaml
resume/originals/
research/companies/
research/upskill/
```

In the private repo these files are removed from the index with `git rm --cached` and stay on
disk. Before that command runs, `scripts/backup_user_data.sh` copies every path in decision 3 to
a directory outside the repo (`~/jobhunt-user-data/<date>/`), prints a per-path file count taken
on disk with `find` (never `git ls-files`, since `data/`, `applications/` and `interviews/` were
never tracked and are the paths with no copy anywhere else) and a checksum list, and the story is
not done until every per-path count matches the source tree and the three untracked paths show
non-zero counts for the author.
Keeping that directory under a private git repo is recommended in the docs, not required by the
product.

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
  relocation_regions: [europe]         # config/geo.yaml region names relocation_line covers ([] = home only)
  relocation_header: open to relocation within Europe   # "<header_location> (<this>)" on such a row
header_location: Lisbon, Portugal      # what the tailored resume header must say
```

`relocation_regions` and `relocation_header` were added while building PR 3: the tailor build,
the star pick and the tailor prompt need to know WHERE the relocation line applies (the author's
is a TN visa, valid in three countries) and what the header says then; both used to be
constants. `config.profile()` validates the four keys, `python -m src.config check` reports a
malformed or missing one, `python -m src.config candidate` prints the block a prompt opens
with (candidate line, lettered families with strengths and notes, work-authorization summary),
and `python -m src.geo "<location>" --scope <region ...>` shows what a location resolves to.
`role_families[]` also accepts an optional `match` phrase list (what `src.stats` buckets a
title by, on top of its title words; the first family is the catch-all) and a one-line `note`
the prompts carry with the family.

Existing keys (`target_titles`, `locations`, `timezones`, `comp`, `location_rule`,
`dealbreakers`, `dream_*`, `relocation_line`, `notes`) keep their meaning. `config.profile()`
validates the new keys with defaults so an old profile still loads, and `init` appends the
missing keys to an existing profile with defaults derived from its own keys (the name, the
target titles), under a dated comment, never touching a line the user wrote.

## 5. Prompt slots

| Prompt | Today | After |
|---|---|---|
| triager (from `jh-triage.md`) | "Candidate: Santiago, founder-engineer, Mexico City, bilingual ES/EN, TN-visa eligible" and four hand-written families | `{candidate_line}` and `{role_families}` rendered as the lettered list, `strength` deciding the "bucket good ones 2-3" line |
| job-matcher | the same four families and "he rates C and D as his two strongest" | same slots; pronoun-free wording ("the candidate") |
| resume-tailor | five mentions of the author, the file name, the header rule | `{resume_basename}`, `{header_location}`, `{work_authorization.summary}`, "the candidate" |
| company-researcher | four mentions, "Santiago will use" | "the candidate" |
| inbox-classifier (from `jh-gmail-sync.md`) | account labels and the author's addresses in examples | `{mail_accounts}` from `.env` labels |
| `/jh-upskill`, `/jh-tailor`, `/jh-triage`, `/jh-gmail-sync` command files | one mention each | none |

Two render modes for the same role file. Headless: the orchestrator's prompt assembler
(`docs/spec-hunt-orchestrator.md` section 4) inlines the values into `data/hunt/<run>/prompts/`,
which is ignored. Interactive: `sync-agents` renders the native agent files with each slot
replaced by an instruction to read the named keys from `config/profile.yaml` (the bundle already
carries the profile for the tailor). No committed file ever contains a profile value, so `init`
never touches a tracked file and no user's tree goes dirty; `sync-agents --check` in CI asserts
the committed renders match the role files.

## 6. Code changes by file

| File | Change |
|---|---|
| `src/config.py` | `profile()` with validation and defaults for the new keys; `resume_basename()` with the decision 5 normalization and a `python -m src.config resume-basename` entry point; `sources()` doing the `sources.local.yaml` deep merge and the `title_filter` default |
| `src/init.py` | copy examples, migrate an existing profile, print a summary; never writes a tracked file; idempotent |
| `src/discover.py` | reads `config.sources()` |
| `src/tailor_build.py` | `ALLOWED_FILES`, `REQUIRED_FILES`, the YAML path and the header check from `resume_basename()` and `header_location`; city and region lists from `config/geo.yaml` |
| `src/tailor_bundle.py` | existing-draft path from `resume_basename()`; "Santiago's own judgment" becomes "the user's own judgment" |
| `src/match.py` | `--eligible-only` regexes built from the home region (`header_location`, else `locations`) and `geo.yaml`; a bare non-remote "United States" row is now locked out for a profile whose home is elsewhere, which the location rule always said |
| `src/render_docx.py` | header item from `work_authorization.header_item` instead of sniffing "tn visa" |
| `src/adapters/torre.py` | the home GMT offset parsed from `profile.timezones` (none written = no band excludes); `countries` from the local sources file |
| `src/adapters/adzuna.py`, `src/adapters/careerjet.py` | the `mx`, `es_MX` and `Mexico` defaults removed; missing targeting keys print a hint and yield nothing |
| `src/stats.py`, `src/report.py` | `stats.families()` built from `role_families` (first family = catch-all, the rest match on `match` phrases or title words); the monthly-figure note is worded without a region |
| `scripts/backup_user_data.sh` | decision 3 paths to `~/jobhunt-user-data/<date>/`, count and checksums |
| `config/notify.yaml.example` | renamed `notify.example.yaml` |
| `src/answers_export.py`, `src/pick.py` | wording |
| `scripts/export_pdf.sh` | file pattern from `python -m src.config resume-basename` |
| `tests/` | fixtures for the fake person; `test_tailor_bundle`, `test_tailor_build`, `test_adapters`, `test_pick`, `test_mail_fetch`, `test_render_cover_letter`, `test_answers_export`, `test_data_quality`, `test_intelligence` stop reading real files or asserting the author's families and cities |
| `tests/test_no_user_data.py` | the guard from decision 9 |
| `.gitignore` | section 3 |
| `CLAUDE.md`, `README.md`, `.claude/agents/*.md`, `.claude/commands/*.md`, `docs/*.md` | name pass per decision 10 |

## 7. Release checklist (run once, in this order)

1. All phases below merged; orchestrator and TUI landed; `pytest` green on a clone with no
   user files (`git clone` into a temp dir, `python -m src.init`, `pytest`).
2. `python -m src.init` output reviewed: every example copies, every stage runs on Alex Example
   through `python -m src.hunt run --dry-run`.
3. Build the clean tree away from the working directory: `git clone --depth 1` the private repo
   into a temp dir (a clone carries tracked files only), `rm -rf .git` there. Every later step
   runs in that directory, never in the author's checkout.
4. Secrets and identity scan in the clean tree: `gitleaks detect --no-git`, then a grep for the
   author's name, both email addresses, the phone number, the Google Sheet id, every token in
   `sources.local.yaml`, and the old deliverable basename. Zero hits except dated attributions
   under `docs/`. Run the guard test there too.
5. Create the public repo empty, no template. In the clean tree: `git init`, one commit
   "jobhunt: initial public release", push. Enable CI, protect `main`, require the checks.
6. Rename this repository `jobhunt-private`, keep it private, add a README line pointing at the
   public one. Move local development to a clone of the public repo; copy the ignored user files
   into it by hand once.
7. Tag `v0.1.0` on the public repo after the first green CI.

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
   `resume/master_resume.example.yaml`, `resume/answers.example.yaml` for Alex Example;
   `config/notify.yaml.example` renamed; `tests/fixtures/` generated from the same
   content by one script (`scripts/gen_fixtures.py`) and a test that they match.
2. **Backup, gitignore and index**: `scripts/backup_user_data.sh` run and verified first (the
   count check in section 3); then the section 3 lines, `git rm --cached` for every newly
   ignored path, `applications/.gitkeep` and `interviews/.gitkeep`.
3. **`config.sources()`** with the local deep merge and the `title_filter` default; `discover`
   reads it; every targeting key (tokens, dreamsheet, countries, locales, query lists,
   the family-specific `title_filter` entries) leaves `sources.yaml` for the author's
   `sources.local.yaml`; the base list plus profile-derived words replaces the hand list only
   after a run over the DB proves every ever-shortlisted row still passes; the adzuna and
   careerjet code defaults removed; the example ships its targeting keys commented out and
   `discover` hints when none are set; tests.
4. **`resume_basename()`** and its use in `tailor_build`, `tailor_bundle`, `export_pdf.sh`,
   the tailor prompt; `reconcile` reports legacy file names; tests.
5. **`python -m src.init`**: copy, migrate, summary; test on a temp tree.
6. **Tests off real files**: every test in the section 6 list on fixtures; CI is green with the
   user files absent, which after story 2 is simply what a checkout contains.
7. **Guard test**: `tests/test_no_user_data.py` with `config/identity.local.example.yaml`
   (documentation, skipped by `init`) and the author's hand-written `identity.local.yaml`; the
   test file itself contains no identity string; a test proves the identity rule is skipped
   with a notice when the file is absent and that `init` leaves it absent.

### PR 3: `feat/profile-driven-prompts`

1. **Profile keys**: `candidate_line`, `role_families`, `work_authorization`,
   `header_location`; `config.profile()` validation and defaults; `init` migration; the
   author's real profile updated. (Landed 2026-09-07 with `relocation_regions` and
   `relocation_header` added to `work_authorization`, see section 4.)
2. **Code constants**: `geo.yaml`; `tailor_build`, `match`, `render_docx`, `torre`, `stats`,
   `report`, `answers_export`, `pick` per section 6; `test_intelligence` on fixture families;
   tests.
3. **Agent and command files**: slots per section 5 in `.claude/agents/*.md` and
   `.claude/commands/*.md`, rendered as read-these-profile-keys instructions, never values (these become `prompts/agents/` in `feat/hunt-core`, which starts
   from this state); the tailor and matcher run once on a real job to confirm no regression in
   the verdict and the letter. (Landed 2026-09-07: the matcher rescored two shortlisted rows
   within 2 points of their stored verdicts; the tailor built a dream row green at 98% fill
   with `header_location (relocation_header)` in the header, `relocation_line` verbatim in the
   letter and the `header_item` deduplicated against the header.)
4. **Docs pass**: `CLAUDE.md`, `README.md` (structure only, the stranger rewrite is phase 4),
   `docs/*.md` per decision 10.

### PR 4: `release/public` (after the orchestrator and the TUI)

1. **LICENSE** (MIT) and the README rewrite from decision 12.
2. **Clone test**: a CI job that clones, runs `init`, runs `pytest` and `hunt run --dry-run`
   on Alex Example.
3. **Checklist**: section 7, executed and ticked in the PR description; the tag.
