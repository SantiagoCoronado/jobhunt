"""The four prompt keys (docs/spec-open-source.md section 4): `config.profile()` validates
them with defaults so an older profile still loads, `families_text` / `candidate_text` render
the block prompts inline, and `src.init` appends the missing keys to an existing profile."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import src.config as config
from src import init

OLD_PROFILE = """\
name: "Old Timer"
target_titles:
  - "Backend Engineer"
  - "Platform Engineer"
must_have_skills: [go, kubernetes, postgres]
shortlist_threshold: 70
"""


# ---- profile() ----

def test_fixture_profile_carries_all_four_keys_validated():
    prof = config.profile()
    assert prof["candidate_line"].startswith("Alex, full-stack engineer")
    keys = [f["key"] for f in prof["role_families"]]
    assert keys == ["A", "B"]
    assert prof["role_families"][1]["strength"] == "strongest"
    assert prof["work_authorization"] == {"summary": "EU citizen, no sponsorship needed in the EU",
                                          "header_item": "EU Work Authorization",
                                          "relocation_regions": ["europe"],
                                          "relocation_header": "open to relocation within Europe"}
    assert prof["header_location"] == "Lisbon, Portugal"
    assert prof["name"] == "Alex Example"           # other keys pass through


def test_old_profile_gets_derived_defaults():
    raw = yaml.safe_load(OLD_PROFILE)
    assert config.missing_profile_keys(raw) == list(config.PROFILE_KEYS)
    prof = config.profile(raw)
    assert prof["candidate_line"] == "Old Timer"
    assert prof["role_families"] == [{"key": "A", "name": "target roles",
                                      "titles": ["Backend Engineer", "Platform Engineer"],
                                      "skills": ["go", "kubernetes", "postgres"], "strength": "core"}]
    assert prof["work_authorization"] == {"summary": "", "header_item": "", "relocation_header": "",
                                          "relocation_regions": []}
    assert prof["header_location"] == ""


def test_profile_without_titles_has_no_families():
    prof = config.profile({"name": "Nobody"})
    assert prof["role_families"] == []
    assert config.families_text(prof) == ""
    assert config.candidate_text(prof) == "Candidate: Nobody"


def test_strength_defaults_to_core_and_whitespace_is_folded():
    prof = config.profile({"name": "X", "candidate_line": "  two\n  lines ",
                           "role_families": [{"key": "Z", "name": "ops", "titles": ["SRE"]}],
                           "work_authorization": {"summary": " a\n b ", "header_item": None}})
    assert prof["candidate_line"] == "two lines"
    assert prof["role_families"][0]["strength"] == "core"
    assert prof["role_families"][0]["skills"] == []
    assert prof["work_authorization"] == {"summary": "a b", "header_item": "", "relocation_header": "",
                                          "relocation_regions": []}


def test_relocation_regions_are_lowercased_and_extra_keys_pass_through():
    prof = config.profile({"name": "X", "work_authorization": {
        "summary": "s", "relocation_regions": [" United States ", "Canada"], "relocation_header": " open  to ",
        "note": "kept"}})
    wa = prof["work_authorization"]
    assert wa["relocation_regions"] == ["united states", "canada"]
    assert wa["relocation_header"] == "open to" and wa["note"] == "kept"
    fam = config.profile({"name": "X", "role_families": [{"key": "A", "titles": ["T"], "match": [" ui ", "react"],
                                                          "note": "one\n line"}]})["role_families"][0]
    assert fam["match"] == ["ui", "react"] and fam["note"] == "one line"


@pytest.mark.parametrize("bad, needle", [
    ({"role_families": "A"}, "must be a list"),
    ({"role_families": [{"name": "x", "titles": ["T"]}]}, "needs a `key`"),
    ({"role_families": [{"key": "A", "titles": ["T"]}, {"key": "A", "titles": ["U"]}]}, "appears twice"),
    ({"role_families": [{"key": "A", "titles": ["T"], "strength": "great"}]}, "strength must be one of"),
    ({"role_families": [{"key": "A", "titles": []}]}, "non-empty `titles`"),
    ({"role_families": [{"key": "A", "titles": ["T"], "skills": "python"}]}, "skills must be a list"),
    ({"work_authorization": "TN"}, "work_authorization must be a mapping"),
    ({"work_authorization": {"summary": ["x"]}}, "work_authorization.summary must be a string"),
    ({"work_authorization": {"relocation_regions": "europe"}}, "relocation_regions must be a list"),
    ({"work_authorization": {"relocation_regions": ["europ"]}}, "names no region in config/geo.yaml: europ"),
    ({"role_families": [{"key": "A", "titles": ["T"], "match": "front end"}]}, "match must be a list of phrases"),
    ({"role_families": [{"key": "A", "titles": ["T"], "match": [""]}]}, "match must be a list of phrases"),
    ({"role_families": [{"key": "A", "titles": ["T"]}, {"key": "B", "titles": ["Remote Role"]}]}, "no title word to match on"),
    ({"work_authorization": {"relocation_header": 1}}, "relocation_header must be a string"),
    ({"candidate_line": ["x"]}, "candidate_line must be a string"),
    ({"header_location": 3}, "header_location must be a string"),
])
def test_malformed_keys_name_the_key(bad, needle):
    with pytest.raises(ValueError, match=needle):
        config.profile({"name": "X", **bad})


# ---- rendering ----

def test_families_text_is_the_lettered_list_with_strength_lines():
    text = config.families_text()
    lines = text.splitlines()
    assert lines[0] == "2 role families, ALL in-scope:"
    assert lines[1] == "(A) hands-on full-stack engineering (Full-Stack Engineer, Software Engineer, Product Engineer; TypeScript, React, Node, Postgres)"
    assert lines[2].startswith("(B) frontend engineering (Frontend Engineer, UI Engineer; ")
    assert lines[3] == "B is the candidate's STRONGEST position: bucket good ones 2-3."
    assert "—" not in text


def test_families_text_carries_notes_and_adjacent_line():
    prof = config.profile({"name": "X", "role_families": [
        {"key": "A", "name": "core", "titles": ["Tester"], "strength": "strongest", "note": "one line"},
        {"key": "B", "name": "side", "titles": ["Uploader"], "strength": "adjacent"},
        {"key": "C", "name": "side2", "titles": ["Validator"], "strength": "strongest"},
    ]})
    text = config.families_text(prof)
    assert "    one line" in text.splitlines()
    assert "A and C are the candidate's STRONGEST positions: bucket good ones 2-3." in text
    assert "B is adjacent: in scope, weighted below the core families." in text


def test_candidate_text_opens_with_the_line_and_ends_with_work_auth(capsys):
    text = config.candidate_text()
    assert text.splitlines()[0] == "Candidate: Alex, full-stack engineer, Lisbon, bilingual PT/EN, EU work authorization."
    assert text.splitlines()[-1] == "Work authorization: EU citizen, no sponsorship needed in the EU"
    assert config.main(["candidate"]) == 0
    assert capsys.readouterr().out.strip() == text


def test_check_command_reports_missing_and_malformed(tmp_path, monkeypatch, capsys):
    path = tmp_path / "profile.yaml"
    path.write_text(OLD_PROFILE)
    monkeypatch.setitem(config.USER_FILES, "profile", path)
    assert config.main(["check"]) == 1
    out = capsys.readouterr().out
    assert "missing  candidate_line" in out and "profile keys incomplete" in out
    path.write_text(OLD_PROFILE + "role_families: nope\n")
    assert config.main(["check"]) == 1
    assert "role_families must be a list" in capsys.readouterr().out


# ---- init migration ----

def _root(tmp_path: Path, profile_text: str | None = OLD_PROFILE) -> Path:
    for ex in init.EXAMPLES:
        (tmp_path / ex).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / ex).write_bytes((config.ROOT / ex).read_bytes())
    if profile_text is not None:
        (tmp_path / "config" / "profile.yaml").write_text(profile_text)
    return tmp_path


def test_init_appends_missing_keys_once_and_keeps_every_written_line(tmp_path, capsys):
    root = _root(tmp_path)
    assert init.plan(root)["migrate"] == list(config.PROFILE_KEYS)
    assert init.run(root, check=True) == 1
    assert "missing  config/profile.yaml: candidate_line" in capsys.readouterr().out
    assert init.run(root) == 0
    out = capsys.readouterr().out
    assert "migrated config/profile.yaml: appended candidate_line, role_families, work_authorization, header_location" in out
    text = (root / "config" / "profile.yaml").read_text()
    assert text.startswith(OLD_PROFILE)                        # nothing above the block changed
    assert "# ---- added by `python -m src.init` on " in text
    raw = yaml.safe_load(text)
    assert config.missing_profile_keys(raw) == []
    prof = config.profile(raw)
    assert prof["candidate_line"] == "Old Timer"
    assert prof["role_families"][0]["titles"] == ["Backend Engineer", "Platform Engineer"]
    assert prof["header_location"] == ""
    # idempotent: a second run appends nothing and the check passes
    assert init.run(root) == 0
    assert "migrated" not in capsys.readouterr().out
    assert (root / "config" / "profile.yaml").read_text() == text
    assert init.run(root, check=True) == 0


def test_init_appends_only_the_keys_that_are_missing(tmp_path, capsys):
    root = _root(tmp_path, OLD_PROFILE + "header_location: Porto, Portugal\n")
    assert init.plan(root)["migrate"] == ["candidate_line", "role_families", "work_authorization"]
    init.run(root)
    raw = yaml.safe_load((root / "config" / "profile.yaml").read_text())
    assert raw["header_location"] == "Porto, Portugal"
    assert set(config.PROFILE_KEYS) <= set(raw)


def test_fresh_copy_of_the_example_needs_no_migration(tmp_path, capsys):
    root = _root(tmp_path, profile_text=None)
    assert init.plan(root)["migrate"] == []
    init.run(root)
    assert "migrated" not in capsys.readouterr().out
    raw = yaml.safe_load((root / "config" / "profile.yaml").read_text())
    assert config.missing_profile_keys(raw) == []
    assert init.run(root, check=True) == 0


def test_migration_block_is_valid_yaml_with_dated_comment():
    block = init.migration_block(yaml.safe_load(OLD_PROFILE), list(config.PROFILE_KEYS), today="2026-09-07")
    assert "on 2026-09-07:" in block
    parsed = yaml.safe_load(block)
    assert list(parsed) == list(config.PROFILE_KEYS)
    assert parsed["work_authorization"] == {"summary": "", "header_item": "", "relocation_header": "",
                                            "relocation_regions": []}
    for key in config.PROFILE_KEYS:
        assert f"# {key}: " in block
