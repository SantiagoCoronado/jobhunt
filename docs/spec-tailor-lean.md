# Spec: lean tailor (`src/tailor_bundle.py`, `src/tailor_build.py`, resume-tailor protocol)

Status: draft for review, 2026-09-02. Follows the audit in `docs/token-efficiency.md`.
One PR per phase (A, B, C). Nothing here changes what the tailor is allowed to write:
Fable still writes every word, only reframes master-resume facts, obeys
`docs/writing-voice.md`, zero em-dashes, and the deliverable names stay
`<FirstLast>Resume.{yaml,docx,pdf}`, `CoverLetter.{md,docx,pdf}`, `match_report.md`,
`answers.md`.

## Problem

A resume-tailor run today (measured over 12 agents on Aug 24 to Sep 2):

| | Today |
|---|---|
| API calls per application | 30 to 70 |
| Context per call | 12k at the start, 66k median, 86k at the end |
| Context tokens per application | 1M to 4.5M |
| Calls spent reading inputs | 5 to 7 (voice, profile, master, dossier, JD, answers.yaml, folder listing) |
| Calls spent in the render, audit, tweak loop | 15 to 25 (`render_docx`, `--audit`, `python3 - <<PYEOF` patches, repeat) |
| Calls spent writing the three deliverables | 3 to 4 |

The writing is under 10% of the calls. Everything else is plumbing that re-reads the whole
context each time: the agent discovers the page geometry by trial (render, read the
estimate, trim, render again) and reads a 51 kB answer bank for 7 approved entries. Five
tailors in flight is also what hit the plan rate limit on 2026-09-02.

## Goal

An application costs about 5 API calls and under 0.4M context tokens, with the same
output quality, verified by `scripts/token_audit.py` on three real jobs before and after.

Target protocol per application:

1. **Read** one file, `data/tailor/<id>/inputs.md` (every input, in a fixed order).
2. **Write** one file, `applications/pending/<company>-<id>/draft.md` (all deliverables
   in fenced sections).
3. **Bash** `python -m src.tailor_build <folder>`: split, check, render, audit, export,
   print a verdict of at most 12 lines, exit 1 if the agent must fix something.
4. At most one fix round: **Edit** the offending file, **Bash** `tailor_build` again.
5. Reply in at most 80 words.

## Non-goals

- Changing the house design, the renderer's estimator, or the fit levels.
- Batching several jobs into one agent. Quality per letter drops and a rate-limit kill
  loses two applications instead of one.
- Auto-submitting anything. Human clicks submit, unchanged.
- Rewriting the matcher, researcher or discover stages (already cheap).
- Prompt-cache engineering across agents (moving shared inputs into the agent system
  prompt). Worth maybe 100k tokens per hunt; revisit after A and B are measured.

## Design principles

1. **Geometry goes in the prompt, not in a loop.** The renderer already knows how many
   characters fit on a line and how many lines fit on the page. Tell the agent up front
   and ask for full-width lines on the first draft; the audit then confirms instead of
   iterating.
2. **One read, one write, one build.** Every tool call re-reads the context. Bundling and
   splitting are deterministic, so scripts do them.
3. **Scripts decide, the model writes.** Em-dash scan, word counts, relocation-line
   presence, answers marker, page count, PDF export: all deterministic, all in one
   command with one compact verdict. The model never runs `python3 - <<PYEOF` to inspect.
4. **Never paraphrase profile rules.** `dream_rule`, `relocation_line`, `location_rule`
   and the comp block reach the agent verbatim from `config/profile.yaml`, inside the
   bundle. No summary of them lives in the agent file (same rule as the matcher).
5. **Truthfulness unchanged.** The bundle includes the master resume verbatim; the
   verdict never suggests content, only geometry (cut N chars, extend N chars, merge).
6. **Files are the interface between agents.** Every stage reads a bundle from disk and
   writes files plus a JSON verdict to disk. No agent depends on another agent's chat
   reply, so a reviewer, a second tailor, or a Workflow script can be slotted in later
   without touching the agents that already exist (see "Extension points").

## Phase A: the two scripts (`src/tailor_bundle.py`, `src/tailor_build.py`, tests)

### A1. `python -m src.tailor_bundle <job_id> [--company NAME] [--dossier PATH] [--out DIR]`

Writes `data/tailor/<id>/inputs.md` (git-ignored under `data/`) and prints one line:
`wrote data/tailor/41573/inputs.md (38.2 kB, ~9.6k tokens): dream=true dossier=nvidia.md answers=7 approved`.

Sections, in this fixed order, each under an H1 with a one-line purpose so the agent
never has to guess what a block is:

1. `# 1. Voice rules` : `docs/writing-voice.md` verbatim.
2. `# 2. Profile` : `config/profile.yaml` verbatim (13 kB; the agent needs `dream_rule`,
   `relocation_line`, `location_rule`, `comp`, target titles and skills, and a trimmed
   copy would drift).
3. `# 3. Master resume` : `resume/master_resume.yaml` verbatim (single source of truth).
4. `# 4. Page geometry` : generated from `src/render_docx.py` constants at bundle time, so
   it can never go stale (see B2 for the text). Includes the line budget computed for
   this master resume's fixed sections (contact, summary, skills, education, additional).
5. `# 5. Job` : `src.query job <id>` output (title, company, location, url, salary,
   `dream: true` when `src.dream.is_dream`, the Curated block from the dream-sheet twin
   when one exists, full description). If the description is empty (Workday rows), say so
   in one line and point at the dossier's Target role section.
6. `# 6. Company dossier` : `research/companies/<slug>.md` verbatim when it exists
   (`--dossier` overrides the path for aggregator rows such as `quill.md`), else one
   line "no dossier; do not invent company facts".
7. `# 7. answers.md (pre-rendered)` : the exact text `src.answers_export` would write,
   with its TAILOR block. The agent copies it into `draft.md` with the why-company block
   replaced; nothing else in it may change.
8. `# 8. Existing draft` : when `applications/*/<company>-<id>/<FirstLast>Resume.yaml`
   already exists, include it verbatim so a refresh edits instead of restarting.
9. `# 9. Review comments` : when `<folder>/review.json` exists (written by a reviewer
   agent, schema below), its unresolved items rendered as a numbered list with file,
   anchor and comment, so a fix round addresses them by number. Absent otherwise.

Size: 35 to 50 kB, 9k to 13k tokens. That is the whole input, read once.

`--company` reuses the `answers_export` override for aggregator rows. `--out` is for
tests. The bundle never contains anything under `data/mail_*` or `interviews/`.

### A2. `python -m src.tailor_build <folder> [--json] [--no-pdf] [--keep-draft]`

One command, in this order, stopping at the first hard failure:

1. **Split.** If `<folder>/draft.md` exists, split it on lines matching
   `=== FILE: <name> ===` into the named files (allowed names only:
   `<FirstLast>Resume.yaml`, `CoverLetter.md`, `match_report.md`, `answers.md`).
   Overwrite the targets, delete `draft.md` unless `--keep-draft`. A missing required
   file (`<FirstLast>Resume.yaml`, `CoverLetter.md`, `match_report.md`) is a hard
   failure naming the file.
2. **Text checks** over every `.md` and `.yaml` in the folder: em-dash count (any is a
   failure, with file:line), `<!-- TAILOR` marker left in `answers.md` (failure),
   CoverLetter.md shape (line 1 is the full name, line 2 the contact line, a `Re:` line,
   no Markdown `#`, `**`, backticks; body word count 220 to 280, header lines excluded),
   YAML parses and has `cv.sections` with the five known sections.
3. **Dream checks** when the job is a dream row (folder name resolves to a job id, then
   `src.dream.is_dream`): if the resume header location contains "open to US relocation"
   the letter must contain `profile.relocation_line` verbatim as its own sentence, and
   vice versa; a mismatch is a failure that quotes the expected sentence. A Berlin/London
   style row (location not in the US and not Mexico) must carry a visa note instead; the
   build only checks that the TN line is absent there.
4. **Resume render**: `render_docx --fit auto`, capture fit level and fill %. Over 100% at
   level 3 is a failure. Under 90% is a warning.
5. **Audit**: `audit_line_fill` at the chosen level; each finding is one verdict line in
   the renderer's own words ("[experience/2/1] 2 lines, last line 31% full: cut ~28 chars
   or extend ~62"). More than 3 findings is a failure; 1 to 3 is a warning the agent may
   fix in the one allowed round.
6. **Page count**: after `--pdf`, count pages in the PDF (PyPDF if importable, else
   `pdfinfo`, else skip with a note). Two pages is a failure even when the estimator said
   99%.
7. **Cover letter**: `render_cover_letter`, then `scripts/export_pdf.sh <folder>`.
8. **Verdict**, at most 12 lines, for example:

```
BUILD applications/pending/nvidia-41573  (dream row)
RESUME  fit level 2, 97% fill, 1 page (pdf)        OK
AUDIT   1 block: [projects/1/2] 2 lines, last 44% full: cut ~30 chars or extend ~55   WARN
LETTER  273 words, plain text, relocation line present   OK
ANSWERS 7 approved, why-company filled              OK
EMDASH  0                                            OK
FILES   <FirstLast>Resume.{yaml,docx,pdf} CoverLetter.{md,docx,pdf} match_report.md answers.md
RESULT  OK with 1 warning (exit 0)
```

Exit codes: 0 green or warnings only, 1 the agent must fix (each FAIL line says what,
including a resume YAML that does not parse), 2 environment problem (LibreOffice missing).
The "outside the US" test in step 3 is a keyword heuristic on the job's location string
(`OUTSIDE_COUNTRIES` / `OUTSIDE_CITIES` in `tailor_build.py`, weighed per location part against
the US/MX/CA markers in `TN_COUNTRY_MARKERS`, which win); a location it
does not recognise is treated as TN territory, and a missing pypdf downgrades the page count
to a printed warning rather than a silent pass. `--json` prints the same as
one object for tests and for `/jh-hunt`'s report.

Two more things the build always does, for other agents rather than for the tailor:

- Writes the verdict object to `<folder>/build.json` (timestamp, fit level, fill, pages,
  letter words, audit findings, failures, warnings, file list). Anything that wants to know
  the state of an application reads this file; nobody re-runs the build to find out.
- Reads `<folder>/review.json` when present and adds a `REVIEW` verdict line: how many
  items are open, and each open item's id, file and first 80 characters. Open items are a
  warning, not a failure, so a build never blocks on a reviewer; the tailor's fix round is
  what addresses them, and `draft.md` may carry a `=== FILE: review_response.md ===`
  section listing item ids with what changed. The build marks an item resolved when the
  response names it.

### A3. Tests (hermetic, no LibreOffice)

`tests/test_tailor_bundle.py`: section order and headings; `dream: true` and the Curated
block appear for a dream row; empty Workday description yields the pointer line;
`--company` flows into answers; nothing from `data/mail_*` can appear (assert on a
fixture tree); size line printed.

`tests/test_tailor_build.py`: split writes exactly the allowed files and rejects an
unknown name; em-dash in any file fails with file:line; TAILOR marker fails; letter with
Markdown fails; 219 and 281 word bodies fail, 220 and 280 pass; dream mismatch fails and
quotes `relocation_line`; over-100%-at-level-3 fails; audit findings become verdict lines;
`--no-pdf` skips steps 6 and 7; `--json` shape; exit codes. Fixtures: a small valid
resume YAML plus the master resume already in the repo.

## Phase B: the agent and the skills

### B1. `.claude/agents/resume-tailor.md` rewrite

Keep: model pin `fable`, the core principles, the dream-company rules, the final
truthfulness pass. Replace the STEPS section with the protocol:

1. Read `data/tailor/<id>/inputs.md` once. Do not read any other file. If the bundle is
   missing, run `python -m src.tailor_bundle <id>` once and read it.
2. Write `applications/pending/<company>-<id>/draft.md` in one Write call, containing
   the four deliverables under `=== FILE: ... ===` separators, resume first. Write to the
   geometry (B2) on this first draft.
3. Run `python -m src.tailor_build <folder>` once.
4. If it exits 1, fix exactly what the FAIL and WARN lines name using Edit on the split
   file (never `python3 - <<PYEOF`), run `tailor_build` once more, then stop regardless.
5. Reply in at most 80 words: fill %, fit level, page count, letter words, hook used, 2 to
   3 honest gaps, relocation decision for dream rows, anything to confirm before applying.

Total: 4 to 6 calls. The tailor never runs `render_docx` directly, never reads
`resume/answers.yaml`, never lists folders.

### B2. The geometry block (generated by `tailor_bundle` from `render_docx` constants)

Numbers come from the module at bundle time; the text below is the template with
today's values, so a renderer change can never leave the agent writing to a stale grid.

```
Page: letter, 0.7in side margins, content width 511pt (bullets indent to 475pt).
Body text 9.0pt Arial at fit levels 0-2 (8.5pt at level 3, the last resort).
A full bullet line holds about 110 characters (116 at level 3); a full summary or skills
line about 105 (110 at level 3).
Write to the grid: every bullet is either ONE full line (95 to 110 chars) or TWO full lines
(205 to 220 chars). Never 1.3 lines. Summary: 2 full lines (200 to 210 chars). Skills:
each label line 95 to 105 chars. Merge a short bullet into a sibling rather than leave it.
Budget: with this master resume's header, summary, skills and education, about 40 body
lines remain at level 1 for experience + projects, and each entry costs 2 lines of
company/title overhead before its bullets. 3 experience entries with 7 bullets and 4
projects with 6 bullets, all full-width, lands at 95-99% at level 1. If you need level 3
to fit, cut a bullet instead.
```

### B3. `/jh-tailor` and `/jh-hunt` step 7

`jh-tailor.md`: step 1 becomes `python -m src.tailor_bundle <id>` (it prints the dossier
state and dream flag, so `src.research get` and `src.query job` are no longer run by the
orchestrator); step 2b is folded into the bundle (answers pre-rendered); step 3 spawns
the agent with a two-line prompt: the job id, the folder, dream yes/no, and the reply cap.
Step 4's summary comes from the agent's 80 words plus the `tailor_build --json` verdict,
which the orchestrator runs once more only if the agent's reply lacks the fill line.

`jh-hunt.md` step 7: the orchestrator runs `tailor_bundle` for the 5 picks in one Bash
call, spawns the 5 tailors in one message, and includes each verdict's RESUME and LETTER
lines in the final report.

### B3b. What B actually changed (landed 2026-09-02)

- `resume-tailor.md` gained the `Edit` tool (the fix round edits the split file; no
  `python3 - <<PYEOF`), the four-call protocol, and the "outside the TN countries" dream case.
- `/jh-tailor` is three steps: bundle, delegate with a two-line prompt, summarize from the
  reply (or `tailor_build --json`).
- `/jh-hunt` step 7 bundles the 5 picks in one Bash call and spawns the 5 tailors in one
  message; step 8 reports the RESUME and LETTER verdict lines and the token audit totals.
- `src.pick` skips dream rows located outside the TN countries (Steven.com London style),
  per Santiago's 2026-09-02 call that the dream waiver is US-on-TN only. Test: `tests/test_pick.py`.

### B4. Measurement gate (acceptance for merging B)

Run three real tailors under the new protocol and `python scripts/token_audit.py --latest`:

| Metric | Gate |
|---|---|
| API calls per tailor | at most 7 |
| Context tokens per tailor | at most 0.4M |
| Verdict | all three exit 0, one page verified by PDF |
| Quality | Santiago reads the three letters and resumes and finds no regression against the Sep 2 drafts |

### B4 result (2026-09-02, three real jobs, measured with `scripts/token_audit.py`)

Measured on the code as merged (fill warning under 95%, geometry budget at fit level 0, the
fill warning is the agent's one fix round). The audit excludes the rate-limit placeholder
lines that an earlier version of the script counted as API calls (`<synthetic>` model, zero
usage), which is why these figures are lower than the ones first posted on the PR.

| Job | First pass | Fix round | Total | Build |
|---|---|---|---|---|
| MongoDB 24703, Solutions Architect, Mexico City | 4 calls, 165k | 6 calls, 237k | 10 calls, 402k | fit 0, 99%, 1 page, audit clean, 238-word letter |
| Riot Games 40698, dream, LA on-site | 2 calls + deterministic build, 47k | 6 calls, 217k | 8 calls, 264k | fit 0, 98%, 1 page, relocation line present |
| CINC Systems 34063, US remote | 2 calls + deterministic build, 45k | 5 calls, 166k | 7 calls, 211k | fit 0, 99%, 1 page, 270-word letter |

MongoDB also had one rate-limited attempt that read the bundle and died (1 call, 13k), not
counted above. The first passes were made before the fill change and landed at 91 to 92%,
which the code as merged flags, so every job took the fix round; the fix-round column is what
that round costs.

Gate reading: CINC passes both gates (7 calls, 211k). Riot passes the token gate and takes 8
calls. MongoDB is over both by a hair (10 calls, 402k against 7 and 0.4M). Recorded as a
deviation, not rounded away: the stated gate assumed the fix round would be rare, and the
geometry change (budget at level 0, spend all of it) is what should make it rare. The next
hunt's audit decides whether the gate moves to 10 calls and 0.45M or first drafts now land
full and the original numbers hold. Against the 30 to 70 calls and 1M to 4.5M baseline every
job is 5x to 20x cheaper either way.

Riot and CINC hit the plan rate limit between their Write and their Bash step on the first
pass, so the orchestrator ran `tailor_build` on their drafts (protocol step 3, zero tokens);
both passed first time, which is the geometry block working. Letters read in the plain voice
with one dossier hook each and named gaps. The renderer also stopped printing "TN Visa
Eligible" twice when the relocation header already says "TN eligible". Santiago's read of the
three drafts: good; the fill change came out of it.

## Phase C: pre-fitted family variants (after B is measured)

Four base resumes under `resume/variants/`: `fde-ai-deployment.yaml`, `frontend.yaml`,
`internal-tools.yaml`, `fullstack-ai.yaml`. Each is written once by Fable from the master,
built with `tailor_build` to 95 to 100% at level 1, and reviewed by Santiago before it
lands. `tailor_bundle` picks the variant by a small title keyword map in `config/profile.yaml`
(`tailor_variants:`; `--variant` overrides) and puts it in section 8 as the starting draft;
the agent then changes the summary and at most 5 bullets. Output shrinks from a 7 kB YAML
to a handful of edited lines, and the fit is stable because the base already fits.

Deferred on purpose: it needs Santiago's review time, and A + B should land and be
measured first so the variant gain is visible on its own.

## Extension points (multi-agent, later)

Every stage of the hunt, existing or future, follows one contract so an orchestrator
(the main session today, a Workflow script or a routine later) can fan agents over it
without reading anything but small JSON files:

| Stage | Deterministic pre-step | Agent (model) | Agent writes | Deterministic post-step / verdict |
|---|---|---|---|---|
| Triage | `src.triage export` -> `chunk_NNN.json` | general-purpose (Haiku) | `out_NNN.json` | `src.triage ingest`; coverage check |
| Match | `src.match export` -> `chunk_NNN.json` | job-matcher (Opus) | `scores_NNN.json` | `src.match ingest` |
| Research | `src.research get` | company-researcher (Sonnet) | `research/companies/<slug>.md` | `src.research get` (stale flag) |
| Tailor | `src.tailor_bundle` -> `inputs.md` | resume-tailor (Fable) | `draft.md` | `src.tailor_build` -> `build.json` |
| Review (new, Phase D) | `src.tailor_bundle` + `build.json` | cv-reviewer (Opus or Sonnet) | `review.json`, `review.md` | `src.tailor_build` (REVIEW line) |
| Fix (Tailor again) | `src.tailor_bundle` (section 9 filled) | resume-tailor (Fable) | `draft.md` with `review_response.md` | `src.tailor_build` |

Rules that make this pluggable:

- An agent takes exactly one argument in its prompt: a job id or a folder. Everything
  else it needs is in the bundle. Adding a stage never changes an existing agent's prompt.
- An agent's reply is at most 80 words and is never parsed. State lives in the files.
- Verdict JSON is the same shape everywhere: `{"stage", "job_id", "ok", "failures": [],
  "warnings": [], "metrics": {}, "files": [], "at"}`. `tailor_build --json` is the first
  producer; triage and match ingest gain the same shape in a follow-up.
- Reviewers never edit deliverables. They write comments; the tailor applies them. That
  keeps the never-fabricate boundary in one agent.

`review.json` schema (a reviewer writes it, the bundle renders it, the build tracks it):

```json
{"reviewer": "cv-reviewer", "at": "2026-09-03T15:02:00Z",
 "items": [
   {"id": 1, "file": "<FirstLast>Resume.yaml", "anchor": "experience/0/highlights/2",
    "severity": "must" , "comment": "Claims a metric not in the master resume; drop or reword.",
    "resolved": false},
   {"id": 2, "file": "CoverLetter.md", "anchor": "paragraph 2",
    "severity": "should", "comment": "Hook repeats the dossier fact twice; keep one.",
    "resolved": false}
 ]}
```

`severity` is `must` (the build turns an unresolved must into a failure only when
`--strict-review` is passed, which the orchestrator does after a fix round), `should`, or
`nit`. `anchor` is free text for letters and a YAML path for the resume. `review.md` is
the same content for a human to read in Finder.

Per-application state, so any orchestrator can ask "what is next" cheaply:
`<folder>/state.json` = `{"job_id", "stages": {"bundled": ts, "drafted": ts, "built": ts,
"reviewed": ts, "fixed": ts}, "last_verdict_ok": bool}`. `tailor_bundle` and
`tailor_build` update it; a reviewer stage updates `reviewed`. `src.pick` skips a company
whose folder exists today; later it can also skip folders whose state says "reviewed and
ok", which is the hook for a "ready to submit" queue.

Workflow sketch for the day this is wanted (not built now):

```js
const picks = await bash('python -m src.pick --json')
await parallel(picks.map(p => () =>
  agent(`Tailor job ${p.id}`, {label: `tailor:${p.id}`, schema: VERDICT})
    .then(() => agent(`Review folder ${p.folder}`, {label: `review:${p.id}`, schema: VERDICT}))
    .then(() => agent(`Fix job ${p.id} from review.json`, {label: `fix:${p.id}`, schema: VERDICT}))))
```

Each `agent()` call is the same two-line prompt the main session uses today, so moving
from in-session orchestration to a Workflow is a script change, not an agent change.

## Phase D (later): `cv-reviewer` agent

Reads the bundle (sections 1 to 3 give it the voice rules and the master resume, the
truth source) plus the built `<FirstLast>Resume.yaml`, `CoverLetter.md` and
`build.json`. Checks: every resume claim traces to the master resume; voice rules; the
hook is one company fact, not a paragraph of them; the honest gaps in `match_report.md`
match what the resume actually shows; ATS terms present where the JD demands them.
Writes `review.json` and `review.md`. Never touches the deliverables. Not built until B is
measured; the spec only reserves its files and its place in the table.

## Token budget, honest version

Per application under B, estimated from today's file sizes:

| Call | Context read | Output |
|---|---|---|
| 1 Read bundle | 3k system + 1k prompt + 11k bundle = 15k | 0.2k |
| 2 Write draft.md | 15k + 0.5k | 5k (yaml 2k, letter 0.5k, report 1.5k, answers 1k) |
| 3 Bash tailor_build | 21k | 0.2k |
| 4 Edit fix (when needed) | 22k | 0.3k |
| 5 Bash tailor_build | 22k | 0.1k |
| 6 Reply | 23k | 0.1k |
| Total | about 120k | about 6k |

Against the measured 1M to 4.5M that is 10x to 30x, so the 0.4M gate in B4 leaves room
for a bundle twice this size and a second fix round. Five tailors in parallel then read
about 0.6M total, versus the 8M to 18M per hunt in the audit.

## Rollout

1. PR A: scripts + tests. No behaviour change for the current agent (it may keep running
   `render_docx` until B lands).
2. PR B: agent + skills + the measurement gate in the PR description.
3. PR C: variants, one at a time, each reviewed.
4. PR D (whenever wanted): the reviewer agent and `--strict-review`; no changes to A or B
   are needed for it because the files and the REVIEW line already exist.

## Open questions for review

1. Should `draft.md` be replaced by four Write calls (simpler agent instructions, 3 more
   calls per tailor, about +60k context)? The spec picks the single file.
2. Should the bundle include `config/profile.yaml` whole (13 kB, no drift) or only the
   keys the tailor uses (about 4 kB, needs a maintained key list)? The spec picks whole.
3. Page count via PyPDF adds a dependency; `pdfinfo` is not installed by default on macOS.
   The spec tries PyPDF, then `pdfinfo`, then the estimator with a note. Acceptable?
