# Spec: jobhunt TUI

Status: draft for review (grilled 2026-09-04, Santiago + Fable). Supersedes the Flask kanban
(`src/crm/viewer.py`) and closes the Notion chapter (PR 1 below deletes it).

## 1. Why

Notion was the phone-side CRM and the single largest token sink of every hunt
(`docs/token-efficiency.md`). It left the hunt on 2026-09-02. The Flask board that remained is a
read-mostly page with eleven kanban columns and no room for the description, the verdict or the
events log. The pipeline already has every write path it needs (`db.set_status`, `touch_contact`,
`log_event`, `reconcile.sync_folder`, `pick`, `stats`); what is missing is one place to live in
while running the hunt. That place is a terminal app, because the hunt itself runs in a terminal
(Claude Code in a terminal).

## 2. Decisions (settled in the grilling, do not re-open without a reason)

| # | Decision | Choice | Why |
|---|----------|--------|-----|
| 1 | Framework | Textual (Python), with `src/tui/data.py` as the only module touching SQLite so a ratatui front end could replace the view later | Same venv, imports the existing write paths, no second implementation of `set_status`. A fast TUI never blocks on I/O, stays alive between uses and draws only dirty cells; Textual gives the last one, the first two are architecture and apply regardless of language. No Rust or Go toolchain on the machine. |
| 2 | Notion | Full delete: `src/notion_pull.py`, its test, `/jh-notion-sync`, `query crm`, hints in run.sh, setup.sh, notify footer, docs wording. History docs keep past-tense mentions. Santiago disconnects the claude.ai Notion connector himself (it is not configured in the repo). | Half-killed code gets picked up by an agent one day. |
| 3 | What it replaces | The Flask viewer and the Flask dependency. `report.html` stays as the offline, shareable dashboard. | A TUI cannot be opened on a phone or sent to someone. |
| 4 | Sections | 1 board, 2 follow-ups, 3 apps, 4 stats (placeholder only), 5 run, 6 settings. (Amended 2026-09-20: the shortlist section, once `2`, is gone; it showed the board's `shortlisted` rows under a left pane with nothing to pick. The board's `shortlisted` view took over its one rule, the hunt's picks leading the list.) | Board and follow-ups are presets on one shared three-pane screen. |
| 5 | Claude Code | The TUI runs no model itself. LLM stages run through the hunt orchestrator (`docs/spec-hunt-orchestrator.md`): `python -m src.hunt run --only <stage>` or a full `run`, as a subprocess exactly like a Python stage, stdout tailed in the log pane. The harness behind it is chosen in `config/hunt.toml`, never in the TUI code. Copy-to-clipboard of the slash command stays as the secondary verb. (Amended 2026-09-07; before that, v1 was copy-only and harness execution was deferred.) | Shelling an interactive agent out of Textual is a terminal-ownership rabbit hole; a headless orchestrator with log files is not. |
| 6 | Phone access | Lost, accepted. `textual serve` is the one-line escape hatch later. | The hunt stopped pushing to Notion on 2026-09-02 anyway. |
| 7 | Process | Spec first, review in a separate session, one PR per phase, several commits per PR (one story each). | House workflow. |
| 8 | Multiplexer integration | None. Standalone `python -m src.tui`, opened in any terminal or tmux pane by hand. | A multiplexer plugin would buy one keybinding and an auto-start; it over-complicates v1 (Santiago, 2026-09-19). |
| 9 | Navigation | Board and follow-ups share one three-pane screen (status list, jobs table, detail pane). Apps, stats, run and settings are their own screens. | Board and follow-ups are the same rows with different filters. |
| 10 | Board shape | Three-pane. Eleven kanban columns do not fit a terminal. | The status list is the counts strip turned vertical. |
| 11 | Hunt picks (was: stars) | Computed, never stored: a row is a pick iff `src.pick` would choose it right now (up to 5, dream slots respected, companies in play skipped). Gone the moment a row leaves `shortlisted`. There is no star mark (amended 2026-09-19): a mark nobody can set by hand reads as broken, so the picks arrive as a pre-selection, the same `●` as a hand-made one, in yellow. `space` takes one off, `esc` takes them all off, `C` brings them back. The pre-selection feeds `c` and the runner only (the runner since 2026-09-20); `s` and `b` act on hand-made marks, so a stray `b` never backlogs five rows. | What the TUI shows pre-selected is what a hunt would tailor. |
| 12 | Runner scope | The stage list is the `src.hunt` registry (discover, triage, match, inbox, pick, research, tailor, report, plus the full hunt) and the extra Python stages (reconcile, stats). `enter` runs any of them as a subprocess with a streamed log; `c` still copies the slash command. A run list shows `data/hunt/*/state.json` with state and started time; selecting a run shows its stages and units and tails the selected unit's log. Per-job copy from the detail pane. Multi-select and a key that copies every starred role. (Amended 2026-09-20: the runner takes the selection. A `selection` block under the stage list shows the marked rows, `space` or `backspace` takes one off, `enter` on one lands on it in the board; `enter` on `tailor` or `research` runs `hunt run --only <stage> --ids ...` on exactly those rows, toasts and starts nothing when none is marked, and spends the selection only when the run exits 0. The full hunt and every other stage ignore the selection and say so.) | One process at a time keeps SQLite writes serialized, and the orchestrator's lockfile enforces it for hunts. |
| 13 | Settings | `config/tui.toml`, committed. Tabbed modal opened with `,`: tabs `theme`, `sections`, `harness`, `follow-ups`, `editor`, a list, `enter` applies, `esc` closes. The `harness` tab edits `config/hunt.toml` (`harness.default` and one model per stage, picked from the harness's live catalog via `hunt models`), not `tui.toml`, and offers a `doctor` action. Plus a read-only view of `profile.yaml`, `sources.yaml`, `hunt.toml`, `tui.toml` with open-in-`$EDITOR`. No YAML editing through forms. | `profile.yaml` is the single authority for scoring and `hunt.toml` for how a hunt runs; open them in the editor rather than build forms. |
| 14 | Cold rows | `discovered` hidden behind a dimmed `all` entry that loads lazily with search. `irrelevant` and `expired` never shown (`stats drops` audits them). | 26k discovered, 10k irrelevant, 7k expired. |
| 15 | Multi-select | The selection is the app's, not a table's (amended 2026-09-20, `src/tui/selection.py`): board and follow-ups draw the same marks, another filter or section never drops one, the footer of every section carries the count, and a hand-made mark goes only when its row leaves the statuses the TUI lists. `space` toggles, `v` selects all visible, `esc` clears. Bulk verbs: status change, backlog (hand-made marks only), copy commands (`c`: every marked row listed, pre-selected or hand-made, one `/jh-tailor <id>` per line, in table order). | Multi-line paste into a Claude Code prompt runs in order; `/jh-tailor` weaves the dossier in when one exists. |
| 16 | Detail pane | Header (title, company, location, source, dream flag, salary when present), status line (score, status, dates, folder bucket), dossier path when one exists, verdict (strengths and missing skills from `match_verdict`), notes, last 5 events, description scrolling. | Events are the only memory of what happened when. |
| 17 | Status keys | `s` opens a picker with a type-to-filter box, `enter` applies through `set_status` (folder moves with it). `b` is the one direct key (backlog: frequent and reversible). Any move that leaves `applied` or later asks for a one-key confirm. | Direct letters for terminal statuses are how a row gets fat-fingered into rejected. |
| 18 | Search | `/` searches title, company and notes inside the current filter. In the `all` view a `d:` prefix also searches descriptions. | The common path stays instant. |
| 19 | Apps section | Every folder under `applications/{pending,applied,other}` joined to its DB row: bucket, company, title, DB status, files present, build verdict when `build.json` exists, drift flag when bucket and status disagree. Pending first. `o` opens posting and Finder folder together, `p` opens the resume PDF, `s` status picker, `R` runs reconcile. | Pending rows are the ones waiting on a human click. |
| 20 | Live refresh | Poll the `jobs.db` mtime every 2 s, reload the current view on change, `r` forces it. `db.connect` gains `busy_timeout=5000` and `journal_mode=WAL`. | A hunt in another pane must show up without a keypress and must not hand the TUI "database is locked". |
| 21 | Keybindings | Single keys, focus-based modes (while an input has focus, letters type; `esc` returns focus to the table). `?` opens a help overlay grouped by section. The footer always shows the bindings that apply right now, drawn from the same binding table so it cannot drift. (Amended 2026-09-20: the footer carries only the keys a reader needs in front of them, a handful per section with one or two word labels; every other binding is `show=False` and lives under `?`, which lists all of them. A shown binding keeps its long form in `tooltip`, on the same `Binding`, and the overlay prints that.) No prefix key. Avoid `ctrl+b` (the tmux prefix). | The TUI is a leaf, not a multiplexer: nothing underneath it needs the keys. |

Routine calls made without a question: notes edit the whole field in a text modal (events keep
history); `f` takes a date or `+N`; `t` records contact, `T` records contact and bumps the
follow-up; mouse enabled; stats placeholder shows the plain output of `stats funnel`.

## 3. Layout

Board and follow-ups (board shown; its `shortlisted` view leads with the hunt's picks unless a
sort was chosen; follow-ups pins `applied · screen · interview`, sorts by follow-up date, overdue in red):

```
 1 board  2 follow-ups  3 apps  4 stats  5 run  6 settings                       jobhunt · 2026-09-04
──────────────────────────────────────────────────────────────────────────────────────────────────
 status         │ score co    company           title                       loc          fup      │ #3625 ElevenLabs
 ▸ shortlisted 622 │ ★ 94   ElevenLabs        Forward Deployed Engineer    Remote LATAM  ·        │ Forward Deployed Engineer
   applied     62 │ ★ 91   Framework Comp.   Software Engineer, Tools     US (dream)    ·        │ Remote LATAM · ashby · dream: no
   screen      11 │ ★ 90   Cursor            FDE, Mexico                  Mexico City   ·        │ score 94 · shortlisted 2026-09-01
   interview    2 │   88   Clara             Backend Engineer             CDMX          ·        │ applied  ·  fup  ·  folder pending/
   offer        0 │   86   Handle            FDE Mexico                   Mexico        ·        │ ─────────────────────────────────
   backlog     36 │   85   Cinc Systems      Senior Fullstack             Remote MX     ·        │ verdict
   rejected    31 │   84   Decagon           Solutions Engineer           Remote        ·        │  strengths: TS, React, Postgres…
   ghosted      0 │   83   Resend            Developer Experience Eng     Remote        ·        │  missing: Go, k8s
   withdrawn   74 │   82   Supabase          Support Engineer, LATAM      Remote        ·        │ ─────────────────────────────────
   all (dim)      │   81   Linear            Product Engineer             Remote US     ·        │ description (scroll ↓)
                  │   …                                                                          │  ElevenLabs is looking for…
──────────────────────────────────────────────────────────────────────────────────────────────────
 j/k move  space select  s status  n note  f follow-up  o open posting  O open folder  c copy cmd  / search  ? help
```

Under about 120 columns the detail pane collapses and `enter` opens it as an overlay.

Settings modal:

```
 settings
 theme   sections   harness   follow-ups   editor
 ────────────────────────────────────────────────
   nord
   gruvbox
   tokyo-night
 ▸ kanagawa ✓
   …
 ↑↓ select   tab section          ↵ apply   esc close
```

## 4. Keybindings

Global: `1`..`6` sections, `?` help, `,` settings, `r` refresh, `q` quit, `esc` home
(focus back to the table, selection cleared, any modal closed).

Jobs table (board and follow-ups): `j`/`k`/arrows move, `g`/`G` top/bottom, `enter` detail overlay
(narrow) or focus detail (wide), `space` select, `v` select all visible, `s` status picker,
`b` backlog, `n` notes, `f` follow-up date, `t` touch, `T` touch and bump, `o` open posting,
`O` open folder (or dossier when no folder), `c` copy `/jh-tailor <id>` (every marked row when any),
`C` select the hunt's picks again, `/` search, `tab` cycle status list / table / detail.
Sort (added 2026-09-19): `>` / `<` sort by the next / previous column (score, company, title,
loc, fup), `-` flips ascending and descending, `=` returns to the section's own sort; a click
on a column header sorts by it and a second click flips. The sorted header carries `▲` or `▼`.
The order is made in SQL (`data.rows(..., sort)`, whitelisted columns, empty values last in
both directions), so search, the `all` cap and live refresh keep it.

Apps (3): `j`/`k`, `o` posting + Finder, `p` resume PDF, `s` status, `R` reconcile (the dry
run first; one `y` applies it when there is something it can fix, and what only a human can
settle stays in the toast).

Run (5): `j`/`k` pick a stage, `enter` runs it (any stage, the full hunt included), `c` copies
the slash command (the shell line when there is none), `R` resumes the highlighted run, `o` opens
`report.html`, `tab` walks stages, runs, units and the log, `ctrl+c` stops the running stage
(SIGTERM; a second one kills the process group). `q` asks first while a stage is running.

Stats (4): `j`/`k`/`g` scroll, `r` runs the command again.

Config files (6): `tab` / `h` / `l` walk the files, `j`/`k`/`g` scroll, `e` opens the file in
the configured editor, `r` reads it again.

Settings modal (`,`): `tab` / `shift+tab` walk the tabs, `j`/`k`/arrows move, `enter` applies
and saves, `esc` closes.

Status picker: type to filter, `↑`/`↓`, `enter` apply, `esc` cancel; confirm prompt `y` when
leaving `applied` or later.

## 5. Modules

```
src/tui/
  __init__.py
  __main__.py        python -m src.tui
  app.py             App, section switching, global bindings, refresh timer
  data.py            the ONLY module that opens SQLite; pure functions returning dataclasses
  presets.py         board / follow-ups filter + sort definitions
  sections.py        the section table (key order) and `number(mode)`
  commands.py        slash-command strings, `src.hunt` argv builders, clipboard
  settings.py        config/tui.toml load/save, defaults, kanagawa theme
  screens/
    jobs.py          three-pane screen (board and follow-ups)
    apps.py          the apps section
    stats.py         the stats placeholder
    run.py           the runner
    config_view.py   read-only config + open in editor
  widgets/
    status_list.py   left pane
    jobs_table.py    middle pane (DataTable subclass)
    detail.py        right pane
    modals.py        status picker, notes editor, follow-up prompt, confirm, help, picker, output
    settings_modal.py  the tabbed settings modal
tests/test_tui_data.py, tests/test_tui_app.py (Textual pilot, headless), tests/tui_fakes.py (the
shared pilot fixture), one tests/test_tui_<area>.py per PR 5 area
config/tui.toml
```

`data.py` contract (all synchronous, called from Textual workers):

- `counts() -> dict[status, int]` (hot statuses only, `all` = discovered count)
- `rows(preset, status, query) -> list[JobRow]` (never `irrelevant`/`expired`; `discovered` only for the `all` view, capped and searchable)
- `detail(id) -> JobDetail` (row + parsed verdict + events + dossier path via `research.path` + folder via `reconcile`)
- `picks() -> list[int]` (delegates to `pick`, in pick order)
- `set_status(id, status, note, followup)`, `set_notes`, `set_followup`, `touch(id, bump)`: thin wrappers over `db` + `reconcile.sync_folder`
- `apps() -> list[AppRow]`, `db_mtime() -> float`

Every write goes through `db.set_status` / `touch_contact` / `log_event`, so the events table
and folder moves stay consistent with `python -m src.query`.

## 6. Settings (`config/tui.toml`)

```toml
[theme]
name = "kanagawa"           # any Textual built-in or "kanagawa" (custom)

[sections]
default = "board"           # section opened on launch
detail_pane = true          # false = always overlay

# No [harness] block: the harness and per-stage models live in config/hunt.toml
# (docs/spec-hunt-orchestrator.md section 6) and the settings modal edits that file.

[followups]
days = 7                    # display only; config.followup_days() stays the pipeline authority
overdue_style = "red"

[editor]
command = "$EDITOR"         # $VARS expand; {file} marks where the path goes (appended when absent)
```

Loading never raises: a value that does not pass falls back to its default and is toasted on
launch. The modal rewrites the whole file (values kept, hand-written comments not).

## 7. Non-goals for v1

Running LLM stages from the TUI. Phone access. Editing `profile.yaml` or `sources.yaml`
through forms. Kanban columns. Multiplexer plugins. Showing `irrelevant` or `expired` rows.

## 8. Phases, PRs and stories

One PR per phase, one commit per story, stories land in the listed order. Every story keeps
`ruff`, `mypy` and `pytest` green (`set -o pipefail` before claiming green). Zero em-dashes in
any text the TUI renders or writes.

### PR 1: `chore/kill-notion`

1. Delete `src/notion_pull.py` and `tests/test_notion_pull.py`; drop the `notion_pull` reference from `src/gmail_pull.py`'s docstring (the contract wording moves into gmail_pull itself).
2. Delete `.claude/commands/jh-notion-sync.md`; remove `query crm` from `src/query.py` (subparser, function, docstring).
3. Scrub hints: `run.sh`, `setup.sh`, the `notify.py` footer, `pick.py` docstring, `tests/test_pick.py` fixture labels.
4. Rewrite the Track section and Commands list in `CLAUDE.md`; rewrite README rows and the "local CRM instead of Notion" paragraph; leave `docs/token-efficiency.md` and `docs/IMPROVEMENT_PLAN.md` as history.
5. Memory: update the token-efficiency and improvement-plan notes so no memory recommends `/jh-notion-sync`.

### PR 2: `docs/spec-tui`

1. This document.

### PR 3: `feat/tui-core` (the one you live in)

1. **Skeleton**: pin `textual` in `requirements.txt`, add `src/tui/{__init__,__main__,app}.py` with the section bar, footer and `q`; `python -m src.tui` opens; one pilot test boots the app headless.
2. **SQLite settings**: `db.connect` sets `busy_timeout=5000` and `journal_mode=WAL`; test asserts both on a fresh DB.
3. **Data layer**: `data.py` with `counts`, `rows`, `detail`, `db_mtime` and the dataclasses; unit tests on a temp DB cover hot/cold filtering, verdict parsing, events order, dossier and folder resolution.
4. **Status list**: left pane with counts, hot statuses in `db.STATUSES` order, dimmed `all`; selecting one sets the table filter.
5. **Jobs table**: DataTable subclass, columns from the mockup, rows loaded in a worker, `j`/`k`/`g`/`G`, sort per preset, star column reserved (empty until PR 4).
6. **Detail pane**: header, status line, dossier line, verdict, notes, last 5 events, description; collapses under 120 columns; `enter` overlay.
7. **Presets**: `1` board, `2` shortlist, `3` follow-ups with their filters and sorts; overdue follow-ups styled red.
8. **Status picker**: modal with type-to-filter, `s` opens, `b` backlog direct, `y` confirm when leaving `applied` or later; writes through `data.set_status`, folder moves; pilot test drives a change and asserts the events row.
9. **Notes and dates**: `n` text modal, `f` date prompt accepting `YYYY-MM-DD`, `+N`, `t`; `t` touch, `T` touch and bump.
10. **Open**: `o` posting in the browser, `O` folder in Finder or dossier when no folder, via `open`.
11. **Search**: `/` over title, company, notes within the filter; `d:` prefix in the `all` view; `esc` clears.
12. **Live refresh**: 2 s mtime poll, reload on change preserving cursor and selection, `r` forces.
13. **Help and footer**: `?` overlay grouped by section, footer driven by the binding table, `esc` home semantics everywhere.
14. **Retire Flask**: delete `src/crm/`, `tests/test_viewer.py`, the Flask pin; update CLAUDE.md Track section and README to name `python -m src.tui`.

### PR 3b: `feat/tui-sort-launch` (added 2026-09-19, after Santiago tested PR 3; Linear PRA-104)

1. **Sort**: `>` `<` `-` `=` and header clicks order the jobs table by any data column, ascending or descending; the order is made in `data.rows`; arrow on the sorted header; cursor stays on the same job.
2. **Launcher**: `bin/jobhunt` opens the TUI from any directory; `scripts/install_launcher.sh [name]` symlinks it into `~/.local/bin` under `jobhunt` or any name, never over a foreign command; `--uninstall` removes it.

### PR 4: `feat/tui-stars-apps`

1. **Stars**: `data.stars()` over `pick`; star column filled; shortlist preset sorts stars first; test with a dream row and a company already in play.
2. **Multi-select**: `space`, `v`, `esc`; selection count in the footer; bulk status change through the picker with one confirm.
3. **Copy commands**: `commands.py` with the slash-command builder and clipboard (`pbcopy`, fallback to Textual's clipboard); `c` current or selection, `C` all starred, one per line; toast confirms what was copied.
4. **Apps data**: `data.apps()` scans the three buckets, joins by the `-<id>` suffix, reads `build.json` when present, flags drift the way `reconcile` does; tests on a temp tree.
5. **Apps screen**: table pending-first, `o` posting + Finder, `p` PDF, `s` picker, `R` reconcile with its output in a toast.

6. **Picks as a pre-selection** (added 2026-09-19 after Santiago tried the stars; decision 11 amended): no star mark; the rows `pick` would choose arrive pre-selected (`●`, yellow), `space` cycles a row, `esc` clears, `C` selects the picks again; `c` copies every marked row listed; `s` and `b` ignore the pre-selection; the footer names both counts.

As built (2026-09-19, stories 1 to 5; story 6 replaces the star and `C` described here): `pick.pick` takes the caller's connection and applications tree, so
`data.stars()` answers on the DB the TUI has open; the first column is two cells wide, the
selection mark `●` then the star; the shortlist leads with the stars only under its own sort;
`space` steps down after marking; a bulk verb spends its selection; `C` copies in pick order;
`reconcile.apply` is the one apply path for the CLI and the TUI.

### PR 5: `feat/tui-run-settings`

1. **Settings file**: `settings.py` loads `config/tui.toml` with defaults and writes it back; tests for missing file, unknown theme, bad template.
2. **Settings modal**: `,` opens the tabbed modal (theme, sections, harness, follow-ups, editor), `enter` applies and saves, `esc` closes.
3. **Themes**: register the kanagawa theme; the theme tab lists Textual built-ins plus kanagawa; applies live.
4. **Harness settings**: the `harness` tab reads and writes `config/hunt.toml` (`harness.default`, one model per stage chosen from the live `hunt models` list) through `src.hunt.config`, and runs `python -m src.hunt doctor` with its table in a modal.
5. **Runner data**: `data.stages()` from the `src.hunt` registry plus reconcile and stats, `data.hunt_runs()` and `data.hunt_status(run)` over `data/hunt/*/state.json`, last-run summary per source from the `runs` table.
6. **Runner screen**: stage list, run list, log pane tailing subprocess stdout or the selected unit's `logs/<stage>/<unit>.log`, one process at a time, `ctrl+c` kills the subprocess (the orchestrator marks running units failed so `--resume` picks them up), `report` opens the html afterwards.
7. **Stats placeholder**: section 5 renders `python -m src.stats funnel` output in a scrollable pane with a note that real widgets come later.
8. **Config view**: read-only tabs for `profile.yaml`, `sources.yaml`, `tui.toml`, `e` opens the file in the configured editor.

As built (2026-09-19): `settings.load` never raises, each bad value is its default plus one
warning; the "bad template" of story 1 is the editor command (`$VARS`, `{file}`, unset `$EDITOR`
is `vi`), since `tui.toml` lost its harness template on 2026-09-07. `followups.days` is the hint
in the `f` prompt. The modal lives in `widgets/settings_modal.py`, one list per tab, every line
a value. `src.hunt.config` gained `write` / `set_default_harness` / `set_stage_model`: a one-line
text edit that keeps every comment, validated by `parse` before an atomic replace; claude has
no live catalog, so its picker lists the `--help` aliases and takes a typed full id. The runner
also lists the selected run's units (the pane tails the highlighted one), resumes a run with `R`,
shows the last discover run per source before anything has run, and the app asks before `q`
takes a running stage down. Section 7 is the config view and adds `sources.local.yaml` and
`hunt.toml` to the three files the story names. Every command the TUI captures or spawns goes
through `commands.capture` / `spawn` / `run_editor`, which the pilot fixture fakes or the tests
replace with tiny Python scripts, so no test reads the real DB or starts an agent CLI.
Known cost: the harness tab and the modal write tracked files (`config/hunt.toml`,
`config/tui.toml`), so a changed model or theme shows up in `git status`, and
`tests/test_hunt_config.py::test_shipped_file_loads_with_the_spec_values` pins the shipped models.

### PR 5b: `feat/tui-polish` (added 2026-09-20, after Santiago used PR 5; Linear PRA-108)

Built in the order 6, 3, 8, then the rest; the numbers are the stories' own.

1. **Clickable section tabs**: a click on a tab's label is its number key; the hit areas come from the table the bar draws from (`section_bar.tabs()`, itself from `SECTIONS`).
2. **Runner stage notes**: `haiku on claude · 8 parallel` and a hunt line that names the global cap; the harness tab edits each fanned stage's `concurrency` and `global_concurrency` through the comment-keeping writer, which gained an integer form.
3. **The selection follows you into the runner**: the marks are held on the app, the runner shows them in a `selection` block and `enter` on `tailor` or `research` runs `hunt run --only <stage> --ids ...` on them (decisions 11, 12, 15; hunt spec section 8).
6. **Remove the shortlist section**: six sections; the board's `shortlisted` view leads with the hunt's picks under its own sort (decisions 4, 9).
4. **Footer**: board and follow-ups show `space select`, `/ search`, `s status`, `c copy`, `? help`; apps `o open`, `s status`, `R reconcile`; run `enter run`, `^c stop`, `R resume`; stats `r again`; config files `tab next`, `e edit`; `,` and `q` left the footer too. Nothing is cut at 120 columns with a selection note.
5. **No command palette**: `ENABLE_COMMAND_PALETTE = False`; the theme changes only in the settings modal, so `tui.toml` is its one record.
7. **Thin scrollbars**: one cell, set once in the app's CSS, colours from the theme; the jobs table's title column takes the table's slack (never under `TITLE_MIN`), so the horizontal bar goes where the columns fit.
8. **An editor round trip never quits the TUI**: `e` with nvim closed the app.
9. **The settings modal keeps one size**: a fixed box (29 rows, `max-height: 90%` on a short terminal) with the list scrolling inside; no edge moves on `tab`.
10. **Legend**: under the status list of board and follow-ups, drawn from the table's own constants (`widgets/legend.py`), only the lines the section can show, first to give way on a short terminal.
11. **Loading state**: `src/tui/loading.py`. A first load that takes over 0.2 s puts Textual's indicator on the widget it fills; a reload keeps the rows and spins a mark in the footer note; the model picker and `hunt doctor` say they are running on the modal's hint line; every load clears its sign in a `finally`, and a token keeps a superseded worker from clearing the newer load's.

As built, story 8: `e` builds the argv from the template (`settings.editor_argv`), suspends the
app (`App.suspend`: the driver leaves application mode and stops reading input), runs the editor
in the foreground on the real terminal (`commands.run_editor`), and resumes. An editor like nvim
asks the terminal questions on its way in and out (cursor style, colours, keyboard protocol); an
answer that arrives after the editor is gone waits in the terminal's input queue and the resumed
TUI read it as keys. The cursor-style answer is `ESC P 1 $ r 2 SP q ESC \`, and `q` quits, which
is what "nvim closes the TUI" was; nano asks nothing, so it never showed. Two guards, both in the
round trip and nowhere else: `commands.flush_terminal_input` (`tcflush(TCIFLUSH)` on the fd the
driver reads) runs after the editor exits and BEFORE `resume_application_mode`, and
`JobhuntApp.deafen` drops every input event for `DEAF_SECONDS` (0.3 s) after the resume, for
what trickles in later; a `q` typed after that quits as ever. `tests/test_tui_pty.py` (marker
`pty`, skipped where there is no pty) runs the real `run()` path in a child on a
pseudo-terminal, with a fake terminal editor that reads nothing while the test injects that
answer plus a bare `q`: the TUI must be alive afterwards and a later `q` must exit 0. With the
two guards removed the test fails on "the late reply was read as `q`".

After Santiago tried the branch (2026-09-20): nvim was fine, `code -w` and `cursor -w` did not
launch. Neither CLI was on PATH: a GUI editor's command lives inside its app bundle on macOS and
reaches PATH only through the editor's own "install shell command" action. `commands.find_program`
looks on PATH, then in the bundles under `/Applications` and `~/Applications` (globbed, a second
install is "Visual Studio Code 2.app"); `resolve_editor` runs before the terminal is given away,
an editor nothing can find is an error toast that says what to do, and the settings modal's editor
tab marks it `not installed`. The runner's selection block became a checklist the same day:
`space` takes a row off and puts it back (it stays listed, `○` and struck through), `x` clears,
the title counts what is on and off, the footer names the keys while the block has the focus, and
a run takes the marked rows in the block's order.

As built, the rest: decisions 4, 9, 11, 12, 15 and 21 carry their amendments inline. The
selection (story 3) outlives a filter as well as a section, which the story left open: the
footer counts it everywhere, so a bulk `s` or `b` acts on every hand-made mark, listed in the
current view or not. Section numbers in on-screen text come from `sections.number(mode)`, and
pilot tests press `_key(mode)`, so the next renumbering is one table. Story 11 measured section
3 before adding any indicator: the seconds were not the folder walk but `config.resume_basename()`
called once per folder, a full parse of `profile.yaml` each time (155 folders, 2.0 s); read once
per load it is 0.06 s, so no per-folder cache was needed. Textual posts `ScreenResume` twice on
a mode's first show, which started every section's first load twice; a load already on its way
is now the load. `hunt.toml` gained a minimum of 1 for `global_concurrency` (a cap of 0 let no
unit start).

## 9. Later (not scheduled)

Unit-level rows in the runner (one row per unit with attempts and usage). Stats widgets over
`stats.py` (funnel, calibration, latency, comp, source health).
`textual serve` for phone access. (Harness execution moved into scope on 2026-09-07 through
`docs/spec-hunt-orchestrator.md`.)
