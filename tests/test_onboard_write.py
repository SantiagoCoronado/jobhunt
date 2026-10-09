"""python -m src.onboard write (docs/spec-pre-release.md PR 5 story 2): every writer validates
first, the show-diff-and-ask rule for a hand-edited file, provenance on the master resume, and
the shared .env one-line editor. Every path is a temp copy; conftest points .env at a temp file."""
from __future__ import annotations

import io
import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml

from src import config, db, dream, onboard

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PDF = FIXTURES / "onboard" / "alex-example-resume.pdf"


@pytest.fixture
def tree(tmp_path, monkeypatch):
    """Fresh `src.init` copies of the user files in a temp dir, and one extracted document."""
    files = {"profile": "profile.yaml", "master_resume": "master_resume.yaml", "sources_local": "sources.local.yaml"}
    for key, name in files.items():
        shutil.copyfile(FIXTURES / name, tmp_path / name)
        monkeypatch.setitem(config.USER_FILES, key, tmp_path / name)
    monkeypatch.setattr(onboard, "ONBOARD_DIR", tmp_path / "onboard")
    onboard.extract([PDF])
    return tmp_path


def _resume_payload() -> dict:
    data = yaml.safe_load((FIXTURES / "master_resume.yaml").read_text())
    data.pop("design", None)
    data["provenance"] = [
        {"what": "summary", "from": ["alex-example-resume.pdf"]},
        {"what": "experience Ledgerly, Brightpath Studio, Universidade de Lisboa (student job)",
         "from": ["alex-example-resume.pdf"]},
        {"what": "projects Shelfmate (open-source reading tracker), Lisbon Transit Widget",
         "from": ["alex-example-resume.pdf"]},
        {"what": "education Universidade de Lisboa", "from": ["alex-example-resume.pdf"]},
        {"what": "skills Frontend, Backend & Cloud, Product & Collaboration", "from": ["alex-example-resume.pdf"]},
        {"what": "additional Languages, Work Authorization", "from": ["interview"]},
    ]
    return data


# ---- resume -----------------------------------------------------------------------------------

def test_write_resume_validates_traces_and_writes(tree):
    line = onboard.write("resume", _resume_payload())
    assert "written" in line and "3 roles, 2 projects" in line
    text = (tree / "master_resume.yaml").read_text()
    assert text.startswith("# MASTER RESUME, written by `python -m src.onboard`")
    assert "from: alex-example-resume.pdf, interview." in text
    data = yaml.safe_load(text)
    assert "provenance" not in data and onboard.resume_errors(data) == []
    prov = json.loads((tree / "onboard" / "provenance.json").read_text())
    assert prov[-1]["from"] == ["interview"]
    assert onboard.write("resume", _resume_payload()).lstrip().startswith("unchanged")


def test_every_entry_needs_a_source_and_a_known_document(tree):
    payload = _resume_payload()
    payload["provenance"][3]["what"] = "school"
    payload["provenance"][1]["what"] = "experience Ledgerly, Brightpath Studio"
    payload["provenance"][0]["from"] = ["my-memory.pdf"]
    with pytest.raises(onboard.Refused) as e:
        onboard.write("resume", payload)
    msg = str(e.value)
    assert "no provenance for education 'Universidade de Lisboa'" in msg
    assert "no provenance for experience 'Universidade de Lisboa (student job)'" in msg
    assert "cites my-memory.pdf, which is not an extracted document" in msg
    assert (tree / "master_resume.yaml").read_text() == (FIXTURES / "master_resume.yaml").read_text()
    with pytest.raises(onboard.Refused, match="`provenance` is required"):
        onboard.write("resume", {k: v for k, v in _resume_payload().items() if k != "provenance"})


def test_a_schema_problem_writes_nothing(tree):
    payload = _resume_payload()
    payload["cv"]["sections"]["experience"][0]["start_date"] = "spring"
    with pytest.raises(onboard.Refused, match="start_date must be YYYY-MM"):
        onboard.write("resume", payload)
    assert not (tree / "onboard" / "provenance.json").exists()


def test_a_hand_edited_file_shows_the_diff_and_waits_for_yes(tree, capsys):
    path = tree / "master_resume.yaml"
    path.write_text(path.read_text().replace("Alex Example", "Alex Q. Example"))     # the user edited it
    payload = json.dumps(_resume_payload())
    assert onboard.main(["write", "resume", payload]) == onboard.NEEDS_YES
    out = capsys.readouterr().out
    assert "--- a/" in out and "-  name: Alex Q. Example" in out and "+  name: Alex Example" in out
    assert "repeat the call with --yes" in out
    assert "Alex Q. Example" in path.read_text()                                      # untouched
    assert onboard.main(["write", "resume", payload, "--yes"]) == 0
    assert "Alex Q. Example" not in path.read_text()
    backups = list((tree / "onboard" / "backup").iterdir())
    assert len(backups) == 1 and "Alex Q. Example" in backups[0].read_text()


def test_what_the_helper_wrote_is_not_hand_edited(tree):
    onboard.write("resume", _resume_payload())
    payload = _resume_payload()
    payload["cv"]["sections"]["summary"] = ["Full-stack engineer, five years of TypeScript."]
    assert "written" in onboard.write("resume", payload)                              # no --yes needed


# ---- profile ----------------------------------------------------------------------------------

def test_write_profile_replaces_one_section_and_keeps_every_comment(tree):
    before = (tree / "profile.yaml").read_text()
    onboard.write("profile", {"target_titles": ["Platform Engineer", "Backend Engineer"], "seniority": "senior"})
    after = (tree / "profile.yaml").read_text()
    prof = yaml.safe_load(after)
    assert prof["target_titles"] == ["Platform Engineer", "Backend Engineer"] and prof["seniority"] == "senior"
    assert prof["name"] == "Alex Example" and prof["comp"]["min_usd"] == 60000
    kept = [ln for ln in before.splitlines() if ln.startswith("#")]
    assert all(ln in after for ln in kept)                    # every top-level comment is still there
    onboard.write("profile", {"resume_basename": "AlexE"})
    assert yaml.safe_load((tree / "profile.yaml").read_text())["resume_basename"] == "AlexE"


def test_write_profile_refuses_a_bad_value_an_unknown_key_and_the_dream_list(tree):
    before = (tree / "profile.yaml").read_text()
    with pytest.raises(onboard.Refused, match="strength must be one of"):
        onboard.write("profile", {"role_families": [{"key": "A", "titles": ["Engineer"], "strength": "best"}]})
    with pytest.raises(onboard.Refused, match="unknown profile key"):
        onboard.write("profile", {"favourite_colour": "blue"})
    with pytest.raises(onboard.Refused, match="use `write dream`"):
        onboard.write("profile", {"dream_companies": ["Example Robotics"]})
    with pytest.raises(onboard.Refused, match="em-dash"):
        onboard.write("profile", {"notes": "Strong frontend — and backend"})
    assert (tree / "profile.yaml").read_text() == before


def test_a_missing_profile_starts_from_the_example(tree):
    (tree / "profile.yaml").unlink()
    onboard.write("profile", {"name": "Sam Sample"})
    text = (tree / "profile.yaml").read_text()
    assert "# Your target profile." in text and yaml.safe_load(text)["name"] == "Sam Sample"


# ---- sources ----------------------------------------------------------------------------------

class _Board:
    status_code = 200

    @staticmethod
    def json():
        return {"jobs": [{"id": 1}]}


def test_write_sources_adds_blocks_the_merge_reads(tree, monkeypatch):
    monkeypatch.setattr(onboard, "_get", lambda url, params: _Board())    # story 3: tokens are verified first
    for token in ("examplecorp", "ledgerly"):
        assert onboard.verify_token("greenhouse", token)["ok"]
    onboard.write("sources", {"greenhouse": {"tokens": ["examplecorp"]}, "adzuna": {"countries": ["pt"],
                                                                                    "queries": ["frontend"]}})
    text = (tree / "sources.local.yaml").read_text()
    assert text.startswith("# Your targeting on top of config/sources.yaml.")
    merged = config.sources()
    assert merged["greenhouse"]["tokens"] == ["examplecorp"] and merged["adzuna"]["countries"] == ["pt"]
    onboard.write("sources", {"greenhouse": {"tokens": ["examplecorp", "ledgerly"]}})
    assert config.sources()["greenhouse"]["tokens"] == ["examplecorp", "ledgerly"]
    assert text.count("greenhouse:") == (tree / "sources.local.yaml").read_text().count("greenhouse:")


def test_write_sources_refuses_an_unknown_source(tree):
    with pytest.raises(onboard.Refused, match="unknown source 'linkedin'"):
        onboard.write("sources", {"linkedin": {"queries": ["x"]}})


# ---- .env -------------------------------------------------------------------------------------

def test_write_env_edits_one_line_each_and_never_prints_a_value(tree, capsys):
    rc = onboard.main(["write", "env", json.dumps({"ADZUNA_APP_ID": "abc123", "MAIL_APPS_USER": "me@example.com",
                                                   "MAIL_ACCOUNTS": "apps"})])
    out = capsys.readouterr().out
    assert rc == 0 and "abc123" not in out and "me@example.com" not in out
    assert "set      .env ADZUNA_APP_ID" in out
    text = config.ENV_PATH.read_text()
    example = config.ENV_EXAMPLE.read_text()
    assert "ADZUNA_APP_ID=abc123\n" in text and "MAIL_APPS_USER=me@example.com\n" in text
    assert "# MAIL_APPS_USER=" not in text                    # the placeholder line was uncommented in place
    assert len(text.splitlines()) == len(example.splitlines())
    assert [ln for ln in text.splitlines() if ln.startswith("# ") and "=" not in ln] == \
           [ln for ln in example.splitlines() if ln.startswith("# ") and "=" not in ln]
    assert config.get_secret("ADZUNA_APP_ID") == "abc123"


def test_replacing_a_set_key_needs_yes_and_an_unknown_key_is_refused(tree, capsys):
    onboard.write("env", {"FINDWORK_TOKEN": "one"})
    assert onboard.main(["write", "env", '{"FINDWORK_TOKEN": "two"}']) == onboard.NEEDS_YES
    assert "FINDWORK_TOKEN already set" in capsys.readouterr().out
    assert config.env_value("FINDWORK_TOKEN") == "one"
    assert "changed" in onboard.write("env", {"FINDWORK_TOKEN": "two"}, yes=True)
    assert "unchanged" in onboard.write("env", {"FINDWORK_TOKEN": "two"})
    with pytest.raises(onboard.Refused, match="OPENAI_KEY: not a key"):
        onboard.write("env", {"OPENAI_KEY": "x"})


def test_set_env_keeps_export_quotes_spaces_and_appends_a_new_key(tmp_path):
    env = tmp_path / "e.env"
    env.write_text("# keys\nexport ADZUNA_APP_ID=old\nOTHER=1\n")
    assert config.set_env("ADZUNA_APP_ID", "new", env) == "changed"
    assert config.set_env("MAIL_APPS_PASS", "ab cd ef", env) == "set"
    assert config.set_env("OTHER", "", env) == "cleared"
    assert env.read_text() == '# keys\nexport ADZUNA_APP_ID=new\nOTHER=\nMAIL_APPS_PASS="ab cd ef"\n'
    assert config.env_value("MAIL_APPS_PASS", env) == "ab cd ef"
    with pytest.raises(ValueError, match="one line"):
        config.set_env("OTHER", "a\nb", env)
    with pytest.raises(ValueError, match="not an environment variable name"):
        config.set_env("bad key", "x", env)


def test_a_missing_env_starts_from_the_example(tree):
    assert not config.ENV_PATH.exists()
    config.set_env("CAREERJET_AFFID", "aff")
    assert config.ENV_PATH.read_text().startswith("# jobhunt secrets")


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file modes")
def test_a_new_env_is_readable_by_its_owner_only(tree):
    config.set_env("CAREERJET_AFFID", "aff")
    assert config.ENV_PATH.stat().st_mode & 0o777 == 0o600


# What set_env writes, every reader reads back: get_secret (so every adapter and the mail pull)
# as well as env_value (the Keys tab and write env). Review of PR #41: load_env only stripped
# quotes, so `pa"ss word` came back as `pa\"ss word` and a value lost a leading or trailing `'`.
TRICKY = {"K_DQUOTE": 'pa"ss word', "K_BACKSLASH": "back\\slash", "K_TRAIL_BS": "end\\",
          "K_ESCAPED": 'a\\"b', "K_LEAD_SQ": "'lead", "K_TRAIL_SQ": "trail'", "K_BOTH_SQ": "'both'",
          "K_WRAPPED": '"wrapped"', "K_HASH": "has # hash", "K_SPACES": "  spaced  ", "K_PLAIN": "plain"}


def test_get_secret_reads_back_every_value_set_env_writes(tree, monkeypatch):
    for key, value in TRICKY.items():
        monkeypatch.delenv(key, raising=False)
        config.set_env(key, value)
    for key, value in TRICKY.items():
        assert config.get_secret(key) == value, key
        assert config.env_value(key) == value, key


def test_hand_written_quotes_read_the_same_in_both_readers(monkeypatch):
    config.ENV_PATH.write_text("export A=\"x y\"\nB='single # kept'\nC= plain \nD=\"unbalanced\nE=it's\nF=''\n")
    monkeypatch.setattr(config, "_ENV_CACHE", None)
    want = {"A": "x y", "B": "single # kept", "C": "plain", "D": '"unbalanced', "E": "it's", "F": ""}
    for key, value in want.items():
        assert config.load_env()[key] == value, key
        assert config.env_value(key) == value, key


def test_write_env_deletes_its_payload_file_whatever_the_outcome(tree, capsys):
    payload = onboard.ONBOARD_DIR / "payload-env.json"
    payload.write_text('{"FINDWORK_TOKEN": "one"}')
    assert onboard.main(["write", "env", str(payload)]) == 0
    assert not payload.exists() and "removed" in capsys.readouterr().out
    payload.write_text('{"FINDWORK_TOKEN": "two"}')             # already set: refused until --yes
    assert onboard.main(["write", "env", str(payload)]) == onboard.NEEDS_YES
    assert not payload.exists() and "write the payload again" in capsys.readouterr().out
    assert config.env_value("FINDWORK_TOKEN") == "one"


def test_write_env_leaves_a_payload_file_outside_data_onboard(tree):
    mine = tree / "my-keys.json"
    mine.write_text('{"FINDWORK_TOKEN": "one"}')
    assert onboard.main(["write", "env", str(mine)]) == 0
    assert mine.exists() and config.env_value("FINDWORK_TOKEN") == "one"


def test_an_env_payload_that_does_not_parse_never_prints_its_values(tree, capsys):
    # Review of PR #41: PyYAML's error quotes the offending line, so an unescaped `"` in a
    # password used to print the password.
    payload = onboard.ONBOARD_DIR / "payload-env.json"
    payload.write_text('{"MAIL_APPS_PASS": "hunter"2-secret"}')
    assert onboard.main(["write", "env", str(payload)]) == 1
    out = capsys.readouterr().out
    assert "hunter" not in out and "2-secret" not in out
    assert "line 1, column" in out and "not shown" in out
    assert not payload.exists() and not config.ENV_PATH.exists()
    with pytest.raises(onboard.Refused, match="neither JSON nor YAML: "):   # other payloads keep the detail
        onboard.read_payload('{"name": "a"b"}')


def test_a_carriage_return_is_refused_before_any_key_is_written(tree):
    with pytest.raises(onboard.Refused, match="FINDWORK_TOKEN: the value must be one line"):
        onboard.write("env", {"ADZUNA_APP_ID": "ok", "FINDWORK_TOKEN": "a\rb"})
    assert not config.ENV_PATH.exists()


def test_provenance_matches_whole_names_not_letters(tree):
    data = {"cv": {"sections": {"skills": [{"label": "Go"}, {"label": "C++"}], "experience": [{"company": "Google"}]}}}
    prov = [{"what": "experience Google", "from": ["interview"]}]
    errors = onboard.provenance_errors(data, prov)
    assert [e.split(":")[0] for e in errors] == ["no provenance for skills 'Go'", "no provenance for skills 'C++'"]
    prov.append({"what": "skills Go, C++", "from": ["interview"]})
    assert onboard.provenance_errors(data, prov) == []


# ---- dream ------------------------------------------------------------------------------------

def test_write_dream_adds_to_the_table_and_keeps_a_name_already_there(tree):
    out = onboard.write("dream", [{"name": "Example Robotics", "careers_url": "https://example.com/jobs"},
                                  "Ledgerly"])
    assert "added    dream Example Robotics" in out and "added    dream Ledgerly" in out
    out = onboard.write("dream", {"companies": ["Ledgerly"]})
    assert "kept     dream Ledgerly" in out
    conn = db.connect(db.DB_PATH)
    assert [d["name"] for d in db.list_dream(conn)] == ["Example Robotics", "Ledgerly"]
    conn.close()
    assert dream.is_dream("Ledgerly")
    with pytest.raises(onboard.Refused, match="needs a name"):
        onboard.write("dream", [{"note": "x"}])


# ---- payloads ---------------------------------------------------------------------------------

def test_a_payload_from_a_file_or_stdin(tree, monkeypatch):
    f = tree / "p.yaml"
    f.write_text("seniority: staff\n")
    assert onboard.read_payload(str(f)) == {"seniority": "staff"}
    monkeypatch.setattr("sys.stdin", io.StringIO('{"seniority": "lead"}'))
    assert onboard.read_payload("-") == {"seniority": "lead"}
    assert onboard.read_payload('{"a": 1}') == {"a": 1}
