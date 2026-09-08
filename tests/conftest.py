"""Every test reads the invented candidate in tests/fixtures/, never a real user's files.

`src.config.USER_FILES` is the one table the loaders resolve through (profile, notify, local
sources, master resume, answers). Pointing it at the fixtures here means the suite passes on a
clone that has no user files at all, which is what CI is (docs/spec-open-source.md decision 8).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src import adapters, config, dream, match, render_docx, stats

FIXTURES = Path(__file__).resolve().parent / "fixtures"

_FIXTURE_FILES = {
    "profile": "profile.yaml",
    "notify": "notify.yaml",              # absent on purpose: the loaders fall back to defaults
    "sources_local": "sources.local.yaml",
    "master_resume": "master_resume.yaml",
    "answers": "answers.yaml",
}


@pytest.fixture(autouse=True)
def _user_files_from_fixtures(monkeypatch):
    for key, name in _FIXTURE_FILES.items():
        monkeypatch.setitem(config.USER_FILES, key, FIXTURES / name)
    dream.reset_cache()
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
