"""python -m src.init: copies every example to its real name once, never overwrites, never
copies the identity example, makes the data dirs, is idempotent."""
from __future__ import annotations

import shutil
from pathlib import Path

from src import init
from src.config import ROOT


def _tree(tmp_path: Path) -> Path:
    for ex in init.EXAMPLES:
        (tmp_path / ex).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / ex, tmp_path / ex)
    (tmp_path / "config" / "identity.local.example.yaml").write_text("patterns: [x]\n")
    return tmp_path


def test_real_name_handles_both_spellings():
    assert init.real_name("config/profile.example.yaml") == "config/profile.yaml"
    assert init.real_name("config/sources.local.example.yaml") == "config/sources.local.yaml"
    assert init.real_name(".env.example") == ".env"


def test_run_copies_once_keeps_edits_and_skips_identity(tmp_path, capsys):
    root = _tree(tmp_path)
    assert init.run(root) == 0
    out = capsys.readouterr().out
    assert "created  config/profile.yaml" in out and "created  .env" in out
    assert "skipped  config/identity.local.example.yaml" in out
    assert not (root / "config" / "identity.local.yaml").exists()
    for d in init.DATA_DIRS:
        assert (root / d).is_dir(), d
    (root / "config" / "profile.yaml").write_text("name: Mine\n")
    assert init.run(root) == 0
    text = (root / "config" / "profile.yaml").read_text()
    assert text.startswith("name: Mine\n")            # the user's line is kept ...
    assert "candidate_line: Mine" in text            # ... and the missing prompt keys are appended
    assert "kept     config/profile.yaml" in capsys.readouterr().out


def test_check_reports_without_writing(tmp_path, capsys):
    root = _tree(tmp_path)
    assert init.run(root, check=True) == 1
    assert "missing  config/profile.yaml" in capsys.readouterr().out
    assert not (root / "config" / "profile.yaml").exists()
    init.run(root)
    assert init.run(root, check=True) == 0


def test_missing_example_is_reported_not_fatal(tmp_path, capsys):
    root = _tree(tmp_path)
    (root / "resume" / "answers.example.yaml").unlink()
    assert init.run(root) == 0
    assert "no example on disk: resume/answers.example.yaml" in capsys.readouterr().out


def test_shipped_examples_all_exist():
    assert init.plan(ROOT)["missing_example"] == []
