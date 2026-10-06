"""The example files and tests/fixtures/ are one content, copied by scripts/gen_fixtures.py."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import gen_fixtures  # noqa: E402


def test_fixtures_match_examples():
    assert gen_fixtures.drift() == [], "run: python scripts/gen_fixtures.py"


def test_examples_parse_and_carry_the_invented_candidate():
    prof = yaml.safe_load((ROOT / "config" / "profile.example.yaml").read_text())
    master = yaml.safe_load((ROOT / "resume" / "master_resume.example.yaml").read_text())
    answers = yaml.safe_load((ROOT / "resume" / "answers.example.yaml").read_text())
    assert prof["name"] == "Alex Example"
    assert master["cv"]["name"] == prof["name"]
    assert isinstance(prof["shortlist_threshold"], int)
    for key in ("comp", "location_rule", "dealbreakers", "dream_rule",
                "relocation_line", "dream_shortlist_threshold", "notes",
                "candidate_line", "role_families", "work_authorization", "header_location"):
        assert key in prof, key
    assert master["cv"]["location"] == prof["header_location"]
    ids = [e["id"] for e in answers["answers"]]
    assert "why-company" in ids and len(ids) == len(set(ids))
    assert all(isinstance(e["draft"], bool) for e in answers["answers"])


def test_sources_local_example_is_all_comments():
    """An unedited copy must target nowhere: every key in the example is commented out."""
    data = yaml.safe_load((ROOT / "config" / "sources.local.example.yaml").read_text())
    assert data is None


def test_no_em_dashes_in_examples():
    for rel in gen_fixtures.PAIRS:
        assert "—" not in (ROOT / rel).read_text(), rel
