"""Section 4: every application folder beside its DB row (spec decision 19)."""
from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.worker import get_current_worker

from .. import commands, data
from ..widgets.apps_table import AppsTable
from ..widgets.modals import Confirm, StatusPicker
from .base import SectionScreen


class AppsScreen(SectionScreen):
    BINDINGS = [
        Binding("r", "refresh", "refresh"),
        Binding("o", "open", "open posting + folder"),
        Binding("p", "pdf", "resume PDF"),
        Binding("s", "status", "status"),
        Binding("R", "reconcile", "reconcile"),
    ]

    def __init__(self) -> None:
        super().__init__("apps")

    def body(self) -> ComposeResult:
        yield AppsTable(id="apps-table")

    def on_mount(self) -> None:
        self.query_one(AppsTable).focus()
        self.reload()

    def on_screen_resume(self) -> None:
        """Back from another section or a modal: a hunt may have tailored a folder meanwhile."""
        self.reload()

    def action_refresh(self) -> None:
        self.reload()

    def reload(self) -> None:
        self.load_apps()

    @work(thread=True, group="apps", exclusive=True)
    def load_apps(self) -> None:
        worker = get_current_worker()
        apps = data.apps()
        if not worker.is_cancelled:
            self.app.call_from_thread(self.query_one(AppsTable).load, apps)

    def current(self) -> data.AppRow | None:
        return self.query_one(AppsTable).current

    # Open: the posting and the folder together (what submitting by hand needs), or the PDF.

    def action_open(self) -> None:
        a = self.current()
        if a is None:
            return
        lines = []
        for op in (lambda: commands.open_posting(a.url), lambda: commands.open_path(a.folder)):
            try:
                lines.append(op())
            except (ValueError, OSError) as e:
                lines.append(str(e))
        self.toast(" · ".join(lines))

    def action_pdf(self) -> None:
        a = self.current()
        if a is None:
            return
        try:
            if a.resume_pdf is None:
                raise ValueError(f"{a.folder.name} has no resume PDF yet")
            self.toast(commands.open_path(a.resume_pdf))
        except (ValueError, OSError) as e:
            self.toast(str(e), "warning")

    # Status: the same picker, confirm and write path as the jobs table; the folder moves with it.

    def action_status(self) -> None:
        a = self.current()
        if a is None:
            return
        if a.job_id is None or not a.status:
            self.toast(f"{a.folder.name}: {a.drift}", "warning")
            return
        job_id, status_now, name = a.job_id, a.status, f"#{a.job_id} {a.company}"

        def picked(status: str | None) -> None:
            if not status or status == status_now:
                return
            if not data.needs_confirm(status_now, status):
                self.write(lambda: data.set_status(job_id, status))
                return

            def answered(yes: bool | None) -> None:
                if yes:
                    self.write(lambda: data.set_status(job_id, status))

            self.app.push_screen(Confirm(f"{name}: leave {status_now} for {status}?"), answered)

        self.app.push_screen(StatusPicker(name, status_now), picked)

    # Reconcile: the dry run first; `y` applies it when there is something it can fix.

    def action_reconcile(self) -> None:
        self.plan_reconcile()

    @work(thread=True, group="reconcile", exclusive=True)
    def plan_reconcile(self) -> None:
        plan = data.reconcile_plan()
        if not plan.fixes:
            line = " · ".join([plan.line, *plan.unmatched])
            self.app.call_from_thread(self.toast, line, "warning" if plan.unmatched else "information")
            return

        def answered(yes: bool | None) -> None:
            if yes:
                self.write(data.reconcile_apply)

        self.app.call_from_thread(self.app.push_screen, Confirm(f"{plan.line}. apply?"), answered)
