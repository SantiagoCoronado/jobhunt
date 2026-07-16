"""config helpers: notify_setting / followup_days fall back sanely."""
import pytest

import src.config as config


def test_notify_setting_missing_file_uses_default(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
    assert config.notify_setting("followup_days", 7) == 7
    assert config.followup_days() == 7


def test_followup_days_reads_config(monkeypatch, tmp_path):
    (tmp_path / "notify.yaml").write_text("followup_days: 10\n")
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
    assert config.followup_days() == 10


def test_followup_days_rejects_garbage(monkeypatch, tmp_path):
    (tmp_path / "notify.yaml").write_text("followup_days: soon\n")
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
    with pytest.raises(ValueError, match="notify.yaml"):
        config.followup_days()
