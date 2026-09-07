"""config helpers: notify_setting / followup_days fall back sanely."""
import pytest

import src.config as config


def test_notify_setting_missing_file_uses_default(monkeypatch, tmp_path):
    monkeypatch.setitem(config.USER_FILES, "notify", tmp_path / "notify.yaml")
    assert config.notify_setting("followup_days", 7) == 7
    assert config.followup_days() == 7


def test_followup_days_reads_config(monkeypatch, tmp_path):
    (tmp_path / "notify.yaml").write_text("followup_days: 10\n")
    monkeypatch.setitem(config.USER_FILES, "notify", tmp_path / "notify.yaml")
    assert config.followup_days() == 10


def test_followup_days_rejects_garbage(monkeypatch, tmp_path):
    (tmp_path / "notify.yaml").write_text("followup_days: soon\n")
    monkeypatch.setitem(config.USER_FILES, "notify", tmp_path / "notify.yaml")
    with pytest.raises(ValueError, match="notify.yaml"):
        config.followup_days()


def test_shortlist_threshold_single_source(monkeypatch, tmp_path):
    monkeypatch.setitem(config.USER_FILES, "profile", tmp_path / "profile.yaml")
    assert config.shortlist_threshold() == 70  # no profile.yaml: safe default
    (tmp_path / "profile.yaml").write_text("shortlist_threshold: 75\n")
    assert config.shortlist_threshold() == 75
