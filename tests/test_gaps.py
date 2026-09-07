"""Phase 3 of docs/spec-email-report-upskill.md: deterministic gap extraction."""
import json

import pytest

from src.db import connect
from src.gaps import Lexicon, fleet_gaps, job_gaps, profile_covered

LEXICON = {"terms": [
    {"term": "kubernetes", "aliases": ["k8s"], "category": "infra"},
    {"term": "react", "category": "frontend"},
    {"term": "c++", "category": "language"},
    {"term": "rust", "category": "language"},
]}
PROFILE = {"must_have_skills": ["react", "python"], "nice_to_have_skills": []}


@pytest.fixture
def lex(tmp_path):
    import yaml
    p = tmp_path / "lexicon.yaml"
    p.write_text(yaml.safe_dump(LEXICON))
    return Lexicon.load(str(p))


@pytest.fixture
def covered(tmp_path, lex):
    import yaml
    p = tmp_path / "profile.yaml"
    p.write_text(yaml.safe_dump(PROFILE))
    return profile_covered(lex, str(p))


@pytest.fixture
def conn(tmp_path):
    return connect(tmp_path / "jobs.db")


def _insert(conn, jid, desc="", status="discovered", score=None, applied=None,
            verdict=None):
    conn.execute(
        "INSERT INTO jobs (id, source, external_id, canonical_key, company, title, "
        "description, status, match_score, applied_at, match_verdict) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (jid, "test", f"x{jid}", f"k{jid}", "Co", "Engineer", desc, status, score,
         applied, json.dumps(verdict) if verdict else None))


def test_lexicon_matches_terms_aliases_and_symbols(lex):
    hits = {e["term"] for e in lex.hits("We use k8s, C++ and Rust daily")}
    assert hits == {"kubernetes", "c++", "rust"}
    # word boundaries: 'trust' must not hit 'rust', 'reactive' not 'react'
    assert not lex.hits("a trustworthy, reactive team")


def test_profile_subtraction(covered):
    assert covered == {"react"}


def test_fleet_counts_and_examples(conn, lex, covered):
    _insert(conn, 1, "kubernetes and react", score=80)
    _insert(conn, 2, "kubernetes rules", score=75, status="applied", applied="2026-07-01")
    _insert(conn, 3, "kubernetes here too", score=90, status="screen", applied="2026-07-02")
    out = fleet_gaps(conn, lex, covered)
    k8s = next(r for r in out["description_gaps"] if r["term"] == "kubernetes")
    assert k8s["jobs"] == 3 and k8s["examples"] == [1, 2, 3]
    assert k8s["applied"] == 2 and k8s["responded"] == 1   # screen responded
    # react is profile-covered: never a gap
    assert not any(r["term"] == "react" for r in out["description_gaps"])


def test_fleet_excludes_low_scores_irrelevant_and_expired(conn, lex, covered):
    _insert(conn, 1, "rust", score=40)                      # below floor
    _insert(conn, 2, "rust", status="irrelevant", score=99)
    _insert(conn, 3, "rust", status="expired", score=99)
    assert fleet_gaps(conn, lex, covered)["jobs_scanned"] == 0
    _insert(conn, 4, "rust", status="shortlisted")          # pipeline, unscored
    out = fleet_gaps(conn, lex, covered)
    assert out["jobs_scanned"] == 1
    assert out["description_gaps"][0]["term"] == "rust"


def test_matcher_missing_aggregation_ranks_first(conn, lex, covered):
    _insert(conn, 1, score=80, verdict={"missing_skills": ["Kubernetes", "GraphQL"]})
    _insert(conn, 2, score=85, verdict={"missing_skills": ["kubernetes "]})
    _insert(conn, 3, score=85, verdict="not a dict")   # malformed verdict tolerated
    out = fleet_gaps(conn, lex, covered)
    top = out["matcher_missing"][0]
    assert top["term"] == "kubernetes" and top["jobs"] == 2   # case/space normalized


def test_job_mode(conn, lex, covered):
    _insert(conn, 7, "kubernetes, react and c++", score=72,
            verdict={"missing_skills": ["MLOps"], "reasons": "solid but no ops"})
    out = job_gaps(conn, lex, covered, 7)
    assert out["jd_terms_not_in_profile"] == ["c++", "kubernetes"]
    assert out["matcher_missing"] == ["mlops"]
    assert out["matcher_reasons"] == "solid but no ops"


def test_job_mode_unknown_id_exits(conn, lex, covered):
    with pytest.raises(SystemExit):
        job_gaps(conn, lex, covered, 404)


def test_real_lexicon_and_profile_load(conn):
    # the shipped config files parse and the profile subtracts something
    lex = Lexicon.load()
    covered = profile_covered(lex)
    assert len(lex.entries) >= 60
    assert "react" in covered and "typescript" in covered
    out = fleet_gaps(conn, lex, covered)   # empty DB: shape holds
    assert out["jobs_scanned"] == 0 and out["matcher_missing"] == []
