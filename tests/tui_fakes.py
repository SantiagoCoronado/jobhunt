"""What every TUI pilot test shares: the temp DB and folders, the recorders that stand in for
the desktop (`open`, the clipboard), and the worker-settling helper.

A pilot test module opts in with `pytestmark = pytest.mark.usefixtures("tmp_db")`; the fixture
itself is registered in conftest.py so a test can also take it by name.
"""
import asyncio

import pytest

from src import db, reconcile, research
from src.hunt import config as hunt_config
from src.hunt import ledger as hunt_ledger
from src.tui import commands, settings


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """The app reads through src.tui.data, which resolves these at call time. Without this a
    pilot test would open the real jobs.db."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "jobs.db")
    monkeypatch.setattr(reconcile, "APPS_DIR", tmp_path / "applications")
    monkeypatch.setattr(research, "COMPANIES_DIR", tmp_path / "companies")
    OPENED.clear()
    monkeypatch.setattr(commands, "launch", OPENED.append)   # no test opens a browser or Finder
    COPIED.clear()
    monkeypatch.setattr(commands, "pbcopy", COPIED.append)   # nor writes the real clipboard
    monkeypatch.setattr(settings, "TUI_TOML", tmp_path / "config" / "tui.toml")   # nor the real settings
    monkeypatch.setattr(hunt_config, "HUNT_TOML", tmp_path / "config" / "hunt.toml")   # nor how the hunt runs
    monkeypatch.setattr(hunt_ledger, "HUNT_DIR", tmp_path / "hunt")                    # nor a real run's ledger
    return tmp_path


OPENED: list[str] = []
COPIED: list[str] = []


def _add(**cols) -> int:
    conn = db.connect(db.DB_PATH)
    n = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] + 1
    row = {"source": "t", "external_id": f"x{n}", "canonical_key": f"k{n}",
           "company": "Acme", "title": "Engineer", "status": "shortlisted", **cols}
    cur = conn.execute(f"INSERT INTO jobs ({','.join(row)}) VALUES ({','.join('?' for _ in row)})",
                       list(row.values()))
    conn.commit()
    conn.close()
    return int(cur.lastrowid or 0)


def _run(coro):
    return asyncio.run(coro)


async def _settle(app, pilot):
    """Wait for the workers. An exclusive worker that a newer one replaced counts as cancelled
    and `wait_for_complete` raises for it; that is the app working as designed, so wait again
    for the one that replaced it."""
    from textual.worker import WorkerCancelled

    for _ in range(5):
        try:
            await app.workers.wait_for_complete()
            break
        except WorkerCancelled:
            continue
    await pilot.pause()
