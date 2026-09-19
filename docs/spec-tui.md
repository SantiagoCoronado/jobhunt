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
| 4 | Sections | 1 board, 2 shortlist, 3 follow-ups, 4 apps, 5 stats (placeholder only), 6 run, 7 settings | Sections 1 to 3 are presets on one shared three-pane screen. |
| 5 | Claude Code | The TUI runs no model itself. LLM stages run through the hunt orchestrator (`docs/spec-hunt-orchestrator.md`): `python -m src.hunt run --only <stage>` or a full `run`, as a subprocess exactly like a Python stage, stdout tailed in the log pane. The harness behind it is chosen in `config/hunt.toml`, never in the TUI code. Copy-to-clipboard of the slash command stays as the secondary verb. (Amended 2026-09-07; before that, v1 was copy-only and harness execution was deferred.) | Shelling an interactive agent out of Textual is a terminal-ownership rabbit hole; a headless orchestrator with log files is not. |
| 6 | Phone access | Lost, accepted. `textual serve` is the one-line escape hatch later. | The hunt stopped pushing to Notion on 2026-09-02 anyway. |
| 7 | Process | Spec first, review in a separate session, one PR per phase, several commits per PR (one story each). | House workflow. |
| 8 | Multiplexer integration | None. Standalone `python -m src.tui`, opened in any terminal or tmux pane by hand. | A multiplexer plugin would buy one keybinding and an auto-start; it over-complicates v1 (Santiago, 2026-09-19). |
| 9 | Navigation | Sections 1 to 3 share one three-pane screen (status list, jobs table, detail pane). Sections 4 to 7 are their own screens. | Board, shortlist and follow-ups are the same rows with different filters. |
| 10 | Board shape | Three-pane. Eleven kanban columns do not fit a terminal. | The status list is the counts strip turned vertical. |
| 11 | Stars | Computed, never stored: a row is starred iff `src.pick` would choose it right now (up to 5, dream slots respected, companies in play skipped). Gone the moment a row leaves `shortlisted`. | What the TUI shows starred is what a hunt would tailor. |
| 12 | Runner scope | The stage list is the `src.hunt` registry (discover, triage, match, inbox, pick, research, tailor, report, plus the full hunt) and the extra Python stages (reconcile, stats). `enter` runs any of them as a subprocess with a streamed log; `c` still copies the slash command. A run list shows `data/hunt/*/state.json` with state and started time; selecting a run shows its stages and units and tails the selected unit's log. Per-job copy from the detail pane. Multi-select and a key that copies every starred role. | One process at a time keeps SQLite writes serialized, and the orchestrator's lockfile enforces it for hunts. |
| 13 | Settings | `config/tui.toml`, committed. Tabbed modal opened with `,`: tabs `theme`, `sections`, `harness`, `follow-ups`, `editor`, a list, `enter` applies, `esc` closes. The `harness` tab edits `config/hunt.toml` (`harness.default` and one model per stage, picked from the harness's live catalog via `hunt models`), not `tui.toml`, and offers a `doctor` action. Plus a read-only view of `profile.yaml`, `sources.yaml`, `hunt.toml`, `tui.toml` with open-in-`$EDITOR`. No YAML editing through forms. | `profile.yaml` is the single authority for scoring and `hunt.toml` for how a hunt runs; open them in the editor rather than build forms. |
| 14 | Cold rows | `discovered` hidden behind a dimmed `all` entry that loads lazily with search. `irrelevant` and `expired` never shown (`stats drops` audits them). | 26k discovered, 10k irrelevant, 7k expired. |
| 15 | Multi-select | `space` toggles, `v` selects all visible, `esc` clears. Bulk verbs: status change, backlog, copy commands. `C` copies one `/jh-tailor <id>` per line for every starred row. | Multi-line paste into a Claude Code prompt runs in order; `/jh-tailor` weaves the dossier in when one exists. |
| 16 | Detail pane | Header (title, company, location, source, dream flag, salary when present), status line (score, status, dates, folder bucket), dossier path when one exists, verdict (strengths and missing skills from `match_verdict`), notes, last 5 events, description scrolling. | Events are the only memory of what happened when. |
| 17 | Status keys | `s` opens a picker with a type-to-filter box, `enter` applies through `set_status` (folder moves with it). `b` is the one direct key (backlog: frequent and reversible). Any move that leaves `applied` or later asks for a one-key confirm. | Direct letters for terminal statuses are how a row gets fat-fingered into rejected. |
| 18 | Search | `/` searches title, company and notes inside the current filter. In the `all` view a `d:` prefix also searches descriptions. | The common path stays instant. |
| 19 | Apps section | Every folder under `applications/{pending,applied,other}` joined to its DB row: bucket, company, title, DB status, files present, build verdict when `build.json` exists, drift flag when bucket and status disagree. Pending first. `o` opens posting and Finder folder together, `p` opens the resume PDF, `s` status picker, `R` runs reconcile. | Pending rows are the ones waiting on a human click. |
| 20 | Live refresh | Poll the `jobs.db` mtime every 2 s, reload the current view on change, `r` forces it. `db.connect` gains `busy_timeout=5000` and `journal_mode=WAL`. | A hunt in another pane must show up without a keypress and must not hand the TUI "database is locked". |
| 21 | Keybindings | Single keys, focus-based modes (while an input has focus, letters type; `esc` returns focus to the table). `?` opens a help overlay grouped by section. The footer always shows the bindings that apply right now, drawn from the same binding table so it cannot drift. No prefix key. Avoid `ctrl+b` (the tmux prefix). | The TUI is a leaf, not a multiplexer: nothing underneath it needs the keys. |

Routine calls made without a question: notes edit the whole field in a text modal (events keep
history); `f` takes a date or `+N`; `t` records contact, `T` records contact and bumps the
follow-up; mouse enabled; stats placeholder shows the plain output of `stats funnel`.

## 3. Layout

Sections 1 to 3 (board shown; shortlist pins `shortlisted` with the star column leading;
follow-ups pins `applied · screen · interview`, sorts by follow-up date, overdue in red):

```
 1 board  2 shortlist  3 follow-ups  4 apps  5 stats  6 run  7 settings          jobhunt · 2026-09-04
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

Global: `1`..`7` sections, `?` help, `,` settings, `r` refresh, `q` quit, `esc` home
(focus back to the table, selection cleared, any modal closed).

Jobs table (sections 1 to 3): `j`/`k`/arrows move, `g`/`G` top/bottom, `enter` detail overlay
(narrow) or focus detail (wide), `space` select, `v` select all visible, `s` status picker,
`b` backlog, `n` notes, `f` follow-up date, `t` touch, `T` touch and bump, `o` open posting,
`O` open folder (or dossier when no folder), `c` copy `/jh-tailor <id>` (selection when any),
`C` copy every starred role, `/` search, `tab` cycle status list / table / detail.
Sort (added 2026-09-19): `>` / `<` sort by the next / previous column (score, company, title,
loc, fup), `-` flips ascending and descending, `=` returns to the section's own sort; a click
on a column header sorts by it and a second click flips. The sorted header carries `▲` or `▼`.
The order is made in SQL (`data.rows(..., sort)`, whitelisted columns, empty values last in
both directions), so search, the `all` cap and live refresh keep it.

Apps (4): `j`/`k`, `o` posting + Finder, `p` resume PDF, `s` status, `R` reconcile (the dry
run first; one `y` applies it when there is something it can fix, and what only a human can
settle stays in the toast).

Run (6): `j`/`k` pick a stage, `enter` run (Python stage) or `c` copy (LLM stage),
`ctrl+c` inside the log pane cancels the running stage.

Status picker: type to filter, `↑`/`↓`, `enter` apply, `esc` cancel; confirm prompt `y` when
leaving `applied` or later.

## 5. Modules

```
src/tui/
  __init__.py
  __main__.py        python -m src.tui
  app.py             App, section switching, global bindings, refresh timer
  data.py            the ONLY module that opens SQLite; pure functions returning dataclasses
  presets.py         board / shortlist / follow-ups filter + sort definitions
  commands.py        slash-command strings, `src.hunt` argv builders, clipboard
  settings.py        config/tui.toml load/save, defaults, kanagawa theme
  screens/
    jobs.py          three-pane screen (sections 1 to 3)
    apps.py          section 4
    stats.py         section 5 placeholder
    run.py           section 6
    config_view.py   read-only config + open in editor
  widgets/
    status_list.py   left pane
    jobs_table.py    middle pane (DataTable subclass)
    detail.py        right pane
    modals.py        status picker, notes editor, follow-up prompt, confirm, help, settings
tests/test_tui_data.py, tests/test_tui_app.py (Textual pilot, headless)
config/tui.toml
```

`data.py` contract (all synchronous, called from Textual workers):

- `counts() -> dict[status, int]` (hot statuses only, `all` = discovered count)
- `rows(preset, status, query) -> list[JobRow]` (never `irrelevant`/`expired`; `discovered` only for the `all` view, capped and searchable)
- `detail(id) -> JobDetail` (row + parsed verdict + events + dossier path via `research.path` + folder via `reconcile`)
- `stars() -> set[int]` (delegates to `pick`)
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
command = "$EDITOR"
```

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

As built (2026-09-19): `pick.pick` takes the caller's connection and applications tree, so
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

## 9. Later (not scheduled)

Unit-level rows in the runner (one row per unit with attempts and usage). Stats widgets over
`stats.py` (funnel, calibration, latency, comp, source health).
`textual serve` for phone access. (Harness execution moved into scope on 2026-09-07 through
`docs/spec-hunt-orchestrator.md`.)
