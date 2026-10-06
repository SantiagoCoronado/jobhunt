"""The dream companies table (docs/spec-pre-release.md decision 9): the db accessors, src.dream
reading it (cached per process), `query dream {list|add|rm}`, and the `init` migration that
moves an existing profile's list into it once. Every test runs on a temp DB."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from src import db, dream, init, query
from src.config import ROOT


@pytest.fixture
def conn():
    c = db.connect(db.DB_PATH)          # conftest points DB_PATH at this test's temp dir
    yield c
    c.close()


@pytest.fixture
def from_table():
    """Drop the conftest seed so src.dream reads the temp table."""
    dream.reset_cache()
    yield
    dream.reset_cache()


# ---- db accessors ----

def test_add_list_get_remove(conn):
    row = db.add_dream(conn, "  Example Robotics ", ["ExampleRobotics", "example robotics", " "],
                       "https://example.com/careers", "robots", added_at="2026-10-06T00:00:00+00:00")
    assert row["name"] == "Example Robotics"
    assert row["match"] == ["examplerobotics", "example robotics"]       # lowercased, deduped, name kept
    assert row["careers_url"] == "https://example.com/careers" and row["note"] == "robots"
    assert row["added_at"] == "2026-10-06T00:00:00+00:00"
    db.add_dream(conn, "Acme")
    assert [d["name"] for d in db.list_dream(conn)] == ["Acme", "Example Robotics"]
    assert db.get_dream(conn, "example ROBOTICS")["name"] == "Example Robotics"
    assert db.remove_dream(conn, "EXAMPLE robotics") is True
    assert db.remove_dream(conn, "Example Robotics") is False
    assert [d["name"] for d in db.list_dream(conn)] == ["Acme"]


def test_add_refuses_a_duplicate_in_any_case_and_an_empty_name(conn):
    db.add_dream(conn, "Acme")
    with pytest.raises(ValueError, match="already a dream company"):
        db.add_dream(conn, "ACME")
    with pytest.raises(ValueError, match="needs a name"):
        db.add_dream(conn, "  ")


# ---- src.dream on the table ----

def test_dream_reads_the_table_and_caches_per_process(conn, from_table):
    db.add_dream(conn, "Example Robotics", ["examplerobotics"])
    conn.commit()
    assert dream.is_dream("ExampleRobotics GmbH") and not dream.is_dream("Acme")
    db.add_dream(conn, "Acme")
    conn.commit()
    assert not dream.is_dream("Acme")              # cached: one read per process
    dream.reset_cache()
    assert dream.is_dream("Acme")                   # a writer resets, the next read sees it


def test_no_database_means_no_dream_companies_and_none_is_created(from_table):
    assert not db.DB_PATH.exists()
    assert dream.dream_companies() == [] and not dream.is_dream("Example Robotics")
    assert not db.DB_PATH.exists()


def test_an_unmigrated_profile_list_still_counts(conn, from_table, monkeypatch):
    db.add_dream(conn, "Acme", note="from the table")
    conn.commit()
    monkeypatch.setattr(dream, "_CACHE", {"dream_companies": [
        {"name": "Example Robotics", "match": ["examplerobotics"]}, "acme"]})
    names = [d["name"] for d in dream.dream_companies()]
    assert names == ["Acme", "Example Robotics"]      # the table wins a name both carry
    assert dream.is_dream("ExampleRobotics")


# ---- query dream ----

def test_query_dream_add_list_rm(conn, from_table, monkeypatch, capsys):
    monkeypatch.setattr(query, "connect", lambda: conn)
    query.cmd_dream("add", "Example Robotics", ["examplerobotics, example-robotics", "ER Labs"],
                    "https://example.com/jobs", "robots")
    added = json.loads(capsys.readouterr().out)["added"]
    assert added["match"] == ["examplerobotics", "example-robotics", "er labs", "example robotics"]
    assert dream.is_dream("ER Labs")                 # the add reset the cache
    query.cmd_dream("list")
    assert [d["name"] for d in json.loads(capsys.readouterr().out)] == ["Example Robotics"]
    with pytest.raises(SystemExit, match="already a dream company"):
        query.cmd_dream("add", "example robotics")
    query.cmd_dream("rm", "Example Robotics")
    assert json.loads(capsys.readouterr().out) == {"removed": "Example Robotics"}
    assert not dream.is_dream("ER Labs")
    with pytest.raises(SystemExit, match="not a dream company"):
        query.cmd_dream("rm", "Example Robotics")
    with pytest.raises(SystemExit, match="needs a company name"):
        query.cmd_dream("add")


# ---- the init migration ----

PROFILE = """\
name: Alex Example
shortlist_threshold: 70

# Dream companies, hand-picked.
dream_companies:
  - {name: "Example Robotics", match: [example robotics, examplerobotics]}
  # a comment inside the list
  - name: Acme
    note: the one with the rockets
    careers_url: https://acme.example/careers

  - Initech
dream_rule: >
  waived for these
relocation_line: "open to relocating"
"""


def _root(tmp_path: Path, text: str = PROFILE) -> Path:
    root = tmp_path / "tree"
    for ex in init.EXAMPLES:
        (root / ex).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / ex, root / ex)
        (root / init.real_name(ex)).write_text((ROOT / ex).read_text())
    (root / init.PROFILE).write_text(text)
    return root


def _table(root: Path) -> list[dict]:
    c = db.connect(root / "data" / "jobs.db")
    try:
        return db.list_dream(c)
    finally:
        c.close()


def test_init_moves_the_profile_list_once_under_a_dated_note(tmp_path, capsys):
    root = _root(tmp_path)
    assert init.plan(root)["dream"] == ["Example Robotics", "Acme", "Initech"]
    assert init.run(root, check=True) == 1
    assert "pending  config/profile.yaml: dream_companies (3)" in capsys.readouterr().out

    res = init.migrate_dream(root, today="2026-10-06")
    assert res == {"moved": ["Example Robotics", "Acme", "Initech"], "kept": []}
    rows = {d["name"]: d for d in _table(root)}
    assert rows["Example Robotics"]["match"] == ["example robotics", "examplerobotics"]
    assert rows["Acme"]["note"] == "the one with the rockets"
    assert rows["Acme"]["careers_url"] == "https://acme.example/careers"
    assert rows["Initech"]["match"] == ["initech"]

    text = (root / init.PROFILE).read_text()
    assert "# ---- moved by `python -m src.init` on 2026-10-06: the dream companies" in text
    assert '# dream_companies:\n#   - {name: "Example Robotics"' in text     # kept, as comments
    assert "# Dream companies, hand-picked.\n" in text                        # the user's own line stays
    parsed = yaml.safe_load(text)
    assert "dream_companies" not in parsed
    assert parsed["dream_rule"].strip() == "waived for these" and parsed["shortlist_threshold"] == 70

    # a second run moves nothing and leaves the file as it is
    assert init.plan(root)["dream"] == []
    assert init.migrate_dream(root, today="2026-10-07") == {"moved": [], "kept": []}
    assert (root / init.PROFILE).read_text() == text
    assert len(_table(root)) == 3


def test_init_run_migrates_and_reports(tmp_path, capsys):
    root = _root(tmp_path)
    assert init.run(root) == 0
    assert "dream_companies moved into data/jobs.db (3 added)" in capsys.readouterr().out
    assert init.run(root, check=True) == 0
    assert "pending" not in capsys.readouterr().out


def test_init_keeps_a_name_the_table_already_has(tmp_path):
    root = _root(tmp_path)
    c = db.connect(root / "data" / "jobs.db")
    db.add_dream(c, "acme", note="typed in the TUI first")
    c.commit()
    c.close()
    res = init.migrate_dream(root, today="2026-10-06")
    assert res == {"moved": ["Example Robotics", "Initech"], "kept": ["Acme"]}
    assert {d["name"]: d["note"] for d in _table(root)}["acme"] == "typed in the TUI first"


def test_init_handles_a_flow_list_and_a_profile_without_one(tmp_path):
    root = _root(tmp_path, "name: X\ndream_companies: [Acme, Initech]\nnotes: hi\n")
    assert init.migrate_dream(root, today="2026-10-06")["moved"] == ["Acme", "Initech"]
    assert yaml.safe_load((root / init.PROFILE).read_text()) == {"name": "X", "notes": "hi"}
    root2 = _root(tmp_path / "b", "name: X\n")
    assert init.plan(root2)["dream"] == [] and init.migrate_dream(root2) == {"moved": [], "kept": []}
    assert not (root2 / "data" / "jobs.db").exists()


def test_init_refuses_a_rewrite_that_would_change_another_key(tmp_path, monkeypatch):
    # if the rewrite ever touched another key, the parsed profiles would differ: nothing is
    # written then, to the table or to the profile
    text = "dream_companies:\n- Acme\nnotes: |\n  kept\n"
    root = _root(tmp_path, text)
    monkeypatch.setattr(init, "comment_out_key", lambda t, k, n: t.replace("notes: |\n  kept\n", "notes: changed\n"))
    with pytest.raises(SystemExit, match="could not comment out"):
        init.migrate_dream(root)
    assert (root / init.PROFILE).read_text() == text
    assert not (root / "data" / "jobs.db").exists()
