"""Every test reads the invented candidate in tests/fixtures/, never a real user's files.

`src.config.USER_FILES` is the one table the loaders resolve through (profile, notify, local
sources, master resume, answers). Pointing it at the fixtures here means the suite passes on a
clone that has no user files at all, which is what CI is (docs/spec-open-source.md decision 8).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from tui_fakes import tmp_db  # noqa: F401  (the TUI pilot fixture, see tui_fakes.py)

from src import adapters, config, db, dream, match, render_docx, stats

FIXTURES = Path(__file__).resolve().parent / "fixtures"

_FIXTURE_FILES = {
    "profile": "profile.yaml",
    "notify": "notify.yaml",              # absent on purpose: the loaders fall back to defaults
    "sources_local": "sources.local.yaml",
    "master_resume": "master_resume.yaml",
    "answers": "answers.yaml",
}


# The invented candidate's dream list. It lives in the dream_companies table now
# (docs/spec-pre-release.md decision 9), so the suite seeds src.dream's per-process cache with
# it instead of a database; a test of the table itself calls dream.reset_cache() and reads the
# temp DB at db.DB_PATH.
DREAM_FIXTURE = [{"name": "Example Robotics", "match": ["example robotics", "examplerobotics"]}]


@pytest.fixture(autouse=True)
def _user_files_from_fixtures(monkeypatch, tmp_path):
    for key, name in _FIXTURE_FILES.items():
        monkeypatch.setitem(config.USER_FILES, key, FIXTURES / name)
    # Anything that resolves db.DB_PATH at call time (src.dream after a reset, src.tui.data)
    # lands in this test's temp dir, never in the real data/jobs.db.
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "jobs.db")
    # .env holds real secrets: no test reads it, and the one-line editor writes a temp copy.
    monkeypatch.setattr(config, "ENV_PATH", tmp_path / ".env")
    monkeypatch.setattr(config, "_ENV_CACHE", None)
    dream.reset_cache()
    monkeypatch.setattr(dream, "_COMPANIES", [dream.normalize(d) for d in DREAM_FIXTURE])
    # The shared title gate caches a value derived from those files, so a test that touches
    # an adapter would otherwise leave the previous profile's gate behind for the next one.
    adapters._TITLE_FILTER = None
    match._LOCATION_RES = None            # home-region prefilter regexes, from the profile
    stats._FAMILIES = None                # role-family regexes, from the profile
    render_docx._HEADER_ITEM = None       # the header work-status item, from the profile
    yield
    dream.reset_cache()
    adapters._TITLE_FILTER = None
    match._LOCATION_RES = None
    stats._FAMILIES = None
    render_docx._HEADER_ITEM = None


AGENT_CLIS = frozenset({"claude", "codex", "opencode", "pi", "agy", "gemini"})
_RealPopen = subprocess.Popen


class _NoAgentPopen(_RealPopen):
    """No test may start a real agent CLI. On 2026-09-18 a test that expected `hunt run` to be
    refused started a real hunt once the last fanned stage landed: `match.export` ran on the
    real DB and four Opus units scored real jobs before anyone noticed. A fake harness is a
    Python script; anything whose program is an agent binary is a test bug, so it raises."""

    def __init__(self, args, *a, **kw):
        program = args if isinstance(args, str) else (args[0] if args else "")
        if Path(str(program)).name in AGENT_CLIS:
            raise AssertionError(f"a test tried to start the real agent CLI {program!r}; use a fake harness")
        super().__init__(args, *a, **kw)


@pytest.fixture(autouse=True)
def _no_real_agent_cli(monkeypatch, request):
    if request.node.get_closest_marker("harness_smoke"):   # opt-in, see tests/test_hunt_harness_smoke.py
        return
    monkeypatch.setattr(subprocess, "Popen", _NoAgentPopen)
