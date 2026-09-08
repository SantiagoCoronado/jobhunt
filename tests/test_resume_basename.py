"""config.resume_basename(): the deliverable stem derived from profile.name, its CLI, the
bundle's legacy lookup and reconcile's legacy report (docs/spec-open-source.md decision 5)."""
from __future__ import annotations

import pytest

from src import config, reconcile, tailor_bundle


@pytest.mark.parametrize("name,stem", [
    ("Alex Example", "AlexExampleResume"),
    ("Zoë O'Brien-Smith", "ZoeOBrienSmithResume"),
    ("Maria Fernanda Lopez Garcia", "MariaFernandaLopezGarciaResume"),
    ("Cher", "CherResume"),
    ("José María Álvarez-Núñez", "JoseMariaAlvarezNunezResume"),
    ("", "Resume"),
    ("   ", "Resume"),
    ("李雷", "Resume"),
])
def test_resume_basename_normalization(name, stem):
    assert config.resume_basename(name) == stem


def test_resume_basename_defaults_to_the_profile_name_and_survives_no_profile(tmp_path, monkeypatch):
    assert config.resume_basename() == "AlexExampleResume"   # the fixture profile
    monkeypatch.setitem(config.USER_FILES, "profile", tmp_path / "absent.yaml")
    assert config.resume_basename() == "Resume"


def test_profile_override_wins_and_is_normalized(tmp_path, monkeypatch):
    prof = tmp_path / "profile.yaml"
    monkeypatch.setitem(config.USER_FILES, "profile", prof)
    prof.write_text('name: "Maria Fernanda Lopez Garcia"\nresume_basename: "Maria Lopez"\n')
    assert config.resume_basename() == "MariaLopezResume"
    prof.write_text('name: "Alex Example"\nresume_basename: "Zoë-Resume"\n')
    assert config.resume_basename() == "ZoeResume"
    prof.write_text('name: "Alex Example"\nresume_basename: ""\n')
    assert config.resume_basename() == "AlexExampleResume"
    assert config.resume_basename("Explicit Name") == "ExplicitNameResume"   # an explicit name ignores the profile


def test_cli_prints_the_stem(capsys):
    assert config.main(["resume-basename"]) == 0
    assert capsys.readouterr().out.strip() == "AlexExampleResume"


def test_existing_resume_prefers_current_then_legacy_name(tmp_path):
    folder = tmp_path / "acme-1"
    folder.mkdir()
    assert tailor_bundle.existing_resume(folder) == folder / "AlexExampleResume.yaml"   # absent, current
    (folder / "OldNameResume.yaml").write_text("cv: {}\n")
    assert tailor_bundle.existing_resume(folder) == folder / "OldNameResume.yaml"
    (folder / "AlexExampleResume.yaml").write_text("cv: {}\n")
    assert tailor_bundle.existing_resume(folder) == folder / "AlexExampleResume.yaml"


def test_reconcile_reports_legacy_names_never_renames(tmp_path):
    apps = tmp_path / "applications"
    for b in ("applied", "pending", "other"):
        (apps / b).mkdir(parents=True)
    old = apps / "applied" / "acme-1"
    old.mkdir()
    (old / "OldNameResume.yaml").write_text("cv: {}\n")
    new = apps / "pending" / "beta-2"
    new.mkdir()
    (new / "AlexExampleResume.yaml").write_text("cv: {}\n")
    names = reconcile.legacy_resume_names(reconcile.scan(apps))
    assert names == ["applied/acme-1/OldNameResume.yaml"]
    assert (old / "OldNameResume.yaml").exists()
