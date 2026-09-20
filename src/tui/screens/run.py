"""The runner (spec decision 12): a stage list, the app's selection, a run list with the
selected run's units, and a log pane. `enter` runs the highlighted stage as a subprocess, one at
a time, its output streamed; `tailor` and `research` run on the selection (`hunt run --ids`). A
run shows its `hunt status` tree, a unit the tail of its log."""
from __future__ import annotations

import subprocess
from collections import deque

from rich.text import Text
from textual import events, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Label, Log, OptionList
from textual.widgets.option_list import Option

from .. import commands, data
from ..sections import number
from ..widgets.jobs_table import MARK, PICK_STYLE, clip
from .base import SectionScreen

KEPT_LINES = 5000
STATE_STYLE = {"done": "green", "failed": "red", "running": "yellow", "unreadable": "red",
               "pending": "dim", "skipped": "dim"}
OPENS_REPORT = ("report", data.HUNT)      # a clean exit of these opens data/report.html
IGNORES = " · ignores selection"          # on every stage that does not run on the marked rows
NOTE_WIDTH = 50                           # what is left of the left column after mark and name
NO_SELECTION = "selection-empty"


class RunList(OptionList):
    BINDINGS = [
        Binding("j", "cursor_down", "down", show=False),
        Binding("k", "cursor_up", "up", show=False),
    ]

    def fill(self, options: list[Option]) -> None:
        """Replace the lines, keeping the highlight on the same id when it is still listed."""
        was = self.highlighted_option.id if self.highlighted_option else None
        self.clear_options()
        self.add_options(options)
        ids = [o.id for o in options]
        if options:
            self.highlighted = ids.index(was) if was in ids else 0


class RunScreen(SectionScreen):
    POLL_SECONDS = 2.0

    DEFAULT_CSS = """
    RunScreen #run-panes { height: 1fr; }
    RunScreen #run-left { width: 64; height: 1fr; border-right: solid $panel; }
    RunScreen .run-title { height: 1; padding: 0 1; color: $text-muted; text-style: bold; }
    RunScreen RunList, RunScreen RunList:focus { border: none; padding: 0; height: auto; max-height: 14; }
    RunScreen #run-runs { max-height: 8; }
    RunScreen #run-selection { max-height: 7; }
    RunScreen #run-units { height: 1fr; max-height: 100%; }
    RunScreen #run-right { width: 1fr; height: 1fr; }
    RunScreen Log { height: 1fr; padding: 0 1; }
    """
    BINDINGS = [
        Binding("enter", "run", "run the stage (tailor and research: on the selection)"),
        Binding("space", "drop", "take the row off the selection", show=False),
        Binding("backspace", "drop", "take the row off the selection", show=False),
        Binding("c", "copy", "copy the command"),
        Binding("R", "resume", "resume the run"),
        Binding("o", "report", "open report.html"),
        Binding("ctrl+c", "cancel", "stop the running stage", priority=True),
        Binding("r", "refresh", "refresh"),
        Binding("tab", "app.focus_next", "next list: stages, selection, runs, units, log", show=False),
    ]

    def __init__(self) -> None:
        super().__init__("run")
        self.stages: list[data.RunStage] = []
        self.status: data.HuntStatus | None = None       # the highlighted run
        self.proc: subprocess.Popen[str] | None = None
        self.proc_name = ""
        self.stop_asked = False
        self.lines: deque[str] = deque(maxlen=KEPT_LINES)
        self.view = "process"                            # process | run | unit
        self.shown = ""
        self.sources = ""
        self.ran_on: list[int] = []                      # the rows the live process was started on

    def body(self) -> ComposeResult:
        with Horizontal(id="run-panes"):
            with Vertical(id="run-left"):
                yield Label("stages", classes="run-title")
                yield RunList(id="run-stages")
                yield Label("selection", classes="run-title", id="run-selection-title")
                yield RunList(id="run-selection")
                yield Label("runs", classes="run-title")
                yield RunList(id="run-runs")
                yield Label("units", classes="run-title")
                yield RunList(id="run-units")
            with Vertical(id="run-right"):
                yield Label("log", classes="run-title", id="run-log-title")
                yield Log(id="run-log", auto_scroll=True)

    def on_mount(self) -> None:
        self.query_one("#run-stages", RunList).focus()
        self.reload()
        self.set_interval(self.POLL_SECONDS, self.poll)

    def on_unmount(self) -> None:
        if self.proc is not None:
            commands.stop(self.proc)

    def on_screen_resume(self) -> None:
        self.reload()
        self.draw_selection()

    def sync_selection(self) -> None:
        super().sync_selection()
        self.draw_selection()

    # The selection: the rows marked in the jobs sections, the same set `c` copies there.

    def draw_selection(self) -> None:
        rows = self.app.selection.marked_rows  # type: ignore[attr-defined]
        picked = self.app.selection.preselected  # type: ignore[attr-defined]
        self.query_one("#run-selection-title", Label).update(Text(f"selection ({len(rows)})"))
        jobs = f"sections {number('board')} and {number('followups')}"
        self.query_one("#run-selection", RunList).fill([
            Option(Text.assemble((f"{MARK} ", PICK_STYLE if r.id in picked else ""),
                                 clip(f"#{r.id} {r.company}, {r.title}", NOTE_WIDTH + 8)), id=str(r.id))
            for r in rows] or [Option(Text(f"  nothing marked: space marks a row in {jobs}", style="dim"),
                                      id=NO_SELECTION, disabled=True)])
        self.draw_stages()

    def action_drop(self) -> None:
        block = self.query_one("#run-selection", RunList)
        opt = block.highlighted_option
        if self.focused is block and opt is not None and opt.id and opt.id != NO_SELECTION:
            self.app.selection.drop(int(opt.id))  # type: ignore[attr-defined]

    def action_refresh(self) -> None:
        self.reload()

    def poll(self) -> None:
        if self.app.screen is self:
            self.refresh_runs()

    def reload(self) -> None:
        self.load_stages()
        self.refresh_runs()

    def refresh_runs(self) -> None:
        """The highlighted run is read here, on the UI thread: the worker must not touch a list
        that `fill()` may be rebuilding under it."""
        opt = self.query_one("#run-runs", RunList).highlighted_option
        self.load_runs(opt.id if opt else None)

    # Loading: the registry import, the ledgers and the runs table are all read off the UI thread.

    @work(thread=True, group="run-stages", exclusive=True)
    def load_stages(self) -> None:
        stages = data.stages()
        runs = data.source_runs()
        self.app.call_from_thread(self.show_stages, stages, runs)

    def show_stages(self, stages: list[data.RunStage], sources: list[data.SourceRun]) -> None:
        self.stages = stages
        self.draw_stages()
        lines = [f"  {r.source:<16} {'ok  ' if r.ok else 'FAIL'}  pulled {r.pulled:>5}  new {r.new:>5}  "
                 f"{r.ts[:16]}  {r.error}".rstrip() for r in sources]
        self.sources = "\n".join(["last discover run per source", *lines]) if lines else ""
        self.draw()

    def draw_stages(self) -> None:
        """The stage lines, with a mark beside the one that is running. `tailor` and `research`
        carry the count they would run on; while rows are marked every other line says it
        ignores them."""
        n = len(self.app.selection.marked)  # type: ignore[attr-defined]

        def note(s: data.RunStage) -> str:
            if s.takes_selection:
                return clip(f"{n} selected · {s.note}", NOTE_WIDTH)
            return clip(s.note, NOTE_WIDTH - len(IGNORES)) + IGNORES if n else s.note

        self.query_one("#run-stages", RunList).fill([
            Option(Text.assemble(("▶ " if self.proc and s.name == self.proc_name else "  ", "yellow"),
                                 f"{s.name:<10}", (note(s), "dim")), id=s.name) for s in self.stages])

    @work(thread=True, group="run-runs", exclusive=True)
    def load_runs(self, highlighted: str | None) -> None:
        runs = data.hunt_runs()
        wanted = highlighted if highlighted in {r.run_id for r in runs} else (runs[0].run_id if runs else None)
        status = data.hunt_status(wanted) if wanted else None
        self.app.call_from_thread(self.show_runs, runs, status)

    def show_runs(self, runs: list[data.HuntRun], status: data.HuntStatus | None) -> None:
        self.query_one("#run-runs", RunList).fill([
            Option(Text.assemble(f"{r.run_id}  ", (f"{r.state:<10}", STATE_STYLE.get(r.state, "")),
                                 (f" {r.started[11:16]} {r.harness}", "dim")), id=r.run_id) for r in runs])
        self.show_status(status)

    def show_status(self, status: data.HuntStatus | None) -> None:
        self.status = status
        units = status.units() if status else []
        self.query_one("#run-units", RunList).fill([
            Option(Text.assemble(f"{u.stage}/{u.id}  ", (u.state, STATE_STYLE.get(u.state, "")),
                                 (f"  x{u.attempts}" if u.attempts > 1 else "", "dim")), id=f"{u.stage}/{u.id}")
            for u in units])
        self.draw()

    @work(thread=True, group="run-status", exclusive=True)
    def load_status(self, run_id: str) -> None:
        status = data.hunt_status(run_id)
        self.app.call_from_thread(self.show_status, status)

    # The log pane follows the list that was touched last.

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        if not event.option_list.has_focus:              # a refill moved it, not the reader
            return
        which = event.option_list.id
        if which == "run-stages":
            self.view = "process"
        elif which == "run-runs":
            self.view = "run"
            if event.option.id and (self.status is None or self.status.run_id != event.option.id):
                self.load_status(event.option.id)
        elif which == "run-units":
            self.view = "unit"
        self.draw()

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        focused = self.focused
        view = {"run-stages": "process", "run-selection": "process", "run-runs": "run",
                "run-units": "unit"}.get(focused.id or "") if focused else None
        if view and view != self.view:
            self.view = view
            self.draw()

    def current_unit(self) -> data.HuntUnit | None:
        opt = self.query_one("#run-units", RunList).highlighted_option
        if opt is None or self.status is None:
            return None
        return next((u for u in self.status.units() if f"{u.stage}/{u.id}" == opt.id), None)

    def draw(self) -> None:
        title, text = "log", ""
        if self.view == "run" and self.status is not None:
            title = f"run {self.status.run_id}"
            text = self.status.error or self.status.tree
        elif self.view == "unit" and (unit := self.current_unit()) is not None:
            title = f"{unit.stage}/{unit.id}  {unit.state}" + (f"  {unit.verdict}" if unit.verdict else "")
            text = (data.tail(unit.log) if unit.log else "") or "no log yet"
        else:
            title = f"{self.proc_name}" + (" (running)" if self.proc else "") if self.proc_name else "log"
            text = "\n".join(self.lines) if self.lines else (
                "enter runs the highlighted stage; its output lands here.\n\n" + self.sources).rstrip()
        self.query_one("#run-log-title", Label).update(Text(title))
        if text != self.shown:
            self.shown = text
            log = self.query_one(Log)
            log.clear()
            log.write(text + "\n")

    # Run, one process at a time.

    def current_stage(self) -> data.RunStage | None:
        opt = self.query_one("#run-stages", RunList).highlighted_option
        return next((s for s in self.stages if opt is not None and s.name == opt.id), None)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        if event.option_list.id == "run-stages":
            self.action_run()
        elif event.option_list.id == "run-selection" and event.option.id not in (None, NO_SELECTION):
            self.app.show_job(int(event.option.id))  # type: ignore[attr-defined]

    def action_run(self) -> None:
        stage = self.current_stage()
        if stage is None or self.focused is not self.query_one("#run-stages", RunList):
            return
        ids = [r.id for r in self.app.selection.marked_rows] if stage.takes_selection else []  # type: ignore[attr-defined]
        if stage.takes_selection and not ids:            # never a run that can only fail
            self.toast(f"nothing selected: mark rows in sections {number('board')} and "
                       f"{number('followups')}, or run from pick", "warning")
            return
        self.start(stage.name, list(stage.argv_for(ids)), ids)

    def action_resume(self) -> None:
        if self.status is None:
            self.toast("no run to resume", "warning")
        elif self.status.state == "done":
            self.toast(f"run {self.status.run_id} is done; nothing to resume", "warning")
        else:
            self.start(f"resume {self.status.run_id}", commands.hunt_argv("run", "--resume", self.status.run_id))

    def start(self, name: str, argv: list[str], ids: list[int] | None = None) -> None:
        if self.proc is not None:
            self.toast(f"{self.proc_name} is still running (ctrl+c stops it); one process at a time", "warning")
            return
        try:
            proc = commands.spawn(argv)
        except OSError as e:
            self.toast(f"{name} did not start: {e}", "error")
            return
        self.proc, self.proc_name, self.stop_asked = proc, name, False
        self.ran_on = list(ids or [])
        self.app.running = name  # type: ignore[attr-defined]
        self.lines.clear()
        self.lines.append(f"$ {commands.shell_line(argv)}")
        self.view = "process"
        self.state_note = f"running {name}"
        self.draw_note()
        self.draw_stages()
        self.draw()
        self.pump(proc, name)

    @work(thread=True, group="run-proc")
    def pump(self, proc: subprocess.Popen[str], name: str) -> None:
        assert proc.stdout is not None
        try:
            for line in proc.stdout:
                self.app.call_from_thread(self.add_line, line.rstrip("\n"))
            rc = proc.wait()
            self.app.call_from_thread(self.finished, name, rc)
        except RuntimeError:               # the app closed under the pump; on_unmount stopped the process
            proc.wait()

    def add_line(self, line: str) -> None:
        self.lines.append(line)
        if self.view == "process":
            self.shown = "\n".join(self.lines)
            self.query_one(Log).write_line(line)

    def finished(self, name: str, rc: int) -> None:
        self.proc = None
        self.app.running = ""  # type: ignore[attr-defined]
        self.draw_stages()
        self.add_line(f"--- {name} {'stopped' if self.stop_asked else 'exited'} ({rc})")
        self.state_note = ""
        self.draw_note()
        self.toast(f"{name}: exit {rc}", "information" if rc == 0 else "warning")
        if rc == 0 and self.ran_on:                      # spent only by a run that went through
            self.app.selection.spend(self.ran_on)  # type: ignore[attr-defined]
        self.ran_on = []
        self.reload()
        if rc == 0 and name in OPENS_REPORT:
            self.action_report()

    def action_cancel(self) -> None:
        if self.proc is None:
            self.toast("nothing is running")
            return
        commands.stop(self.proc, hard=self.stop_asked)
        self.toast(f"killed {self.proc_name}" if self.stop_asked else
                   f"stopping {self.proc_name} (ctrl+c again kills it)", "warning")
        self.stop_asked = True

    def action_copy(self) -> None:
        stage = self.current_stage()
        if stage is None:
            return
        ids = [r.id for r in self.app.selection.marked_rows] if stage.takes_selection else []  # type: ignore[attr-defined]
        text = commands.shell_line(stage.argv_for(ids)) if ids else stage.copy_text
        commands.copy(text, self.app.copy_to_clipboard)
        self.toast(f"copied {text}")

    def action_report(self) -> None:
        path = data.report_path()              # asked now: the stage that just exited may have written it
        try:
            if not path.exists():
                raise ValueError("no data/report.html yet (run the report stage)")
            self.toast(commands.open_path(path))
        except (ValueError, OSError) as e:
            self.toast(str(e), "warning")
