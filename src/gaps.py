"""Deterministic skill-gap extraction: the numbers behind /jh-upskill.

  python -m src.gaps [--min-score 70] [--json]     # fleet mode
  python -m src.gaps --job <id> [--json]           # one posting

Two signals, clearly separated (spec 3a of docs/spec-email-report-upskill.md):

1. matcher_missing: aggregate of the job-matcher's own `missing_skills` field
   from match_verdict. LLM-judged per JD, so it is the PRIMARY signal.
2. description_gaps: lexicon scan (config/skills_lexicon.yaml) of raw
   descriptions, minus everything the profile already claims. Covers unscored
   jobs and terms the matcher did not single out.

Every row carries counts and, where the jobs were applied to, the responded
rate, so /jh-upskill can put n next to every claim. The LLM downstream decides
vocabulary-gap vs real-gap vs noise; this module only counts.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from dataclasses import dataclass, field

from .config import load_yaml
from .db import connect
from .stats import _outcome

APPLIED_STATUSES = ("applied", "screen", "interview", "offer", "rejected", "ghosted")
PIPELINE_STATUSES = ("shortlisted", "applied", "screen", "interview", "offer")
EXAMPLE_CAP = 5


@dataclass
class TermStat:
    term: str
    category: str = ""
    jobs: int = 0
    examples: list[int] = field(default_factory=list)
    applied: int = 0
    responded: int = 0

    def add(self, job_id: int, status: str, applied_at: str | None) -> None:
        self.jobs += 1
        if len(self.examples) < EXAMPLE_CAP:
            self.examples.append(job_id)
        if applied_at or status in APPLIED_STATUSES:
            self.applied += 1
            if _outcome(status) == "responded":
                self.responded += 1

    def row(self) -> dict:
        return {"term": self.term, "category": self.category, "jobs": self.jobs,
                "examples": self.examples, "applied": self.applied,
                "responded": self.responded}


def _pattern(term: str) -> re.Pattern:
    """Word-ish boundaries that survive c++, c#, node.js, ci/cd."""
    return re.compile(rf"(?<![a-z0-9+#]){re.escape(term.lower())}(?![a-z0-9+#])")


@dataclass
class Lexicon:
    entries: list[dict]

    @classmethod
    def load(cls, name: str = "skills_lexicon.yaml") -> Lexicon:
        raw = load_yaml(name).get("terms") or []
        entries = []
        for e in raw:
            pats = [_pattern(e["term"])] + [_pattern(a) for a in e.get("aliases", [])]
            entries.append({"term": e["term"], "category": e.get("category", ""),
                            "patterns": pats})
        return cls(entries)

    def hits(self, text: str) -> list[dict]:
        low = text.lower()
        return [e for e in self.entries
                if any(p.search(low) for p in e["patterns"])]


def profile_covered(lex: Lexicon, profile_name: str = "profile.yaml") -> set[str]:
    """Lexicon terms the profile already claims (term or alias matches any
    profile skill string), the subtraction set."""
    prof = load_yaml(profile_name)
    blob = " | ".join(
        str(s) for s in (prof.get("must_have_skills") or []) + (prof.get("nice_to_have_skills") or []))
    return {e["term"] for e in lex.hits(blob)}


def _norm_skill(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def fleet_gaps(conn: sqlite3.Connection, lex: Lexicon, covered: set[str],
               min_score: int = 70) -> dict:
    rows = conn.execute(
        f"SELECT id, title, status, applied_at, description, match_score, match_verdict "
        f"FROM canonical_jobs WHERE status NOT IN ('irrelevant', 'expired') "
        f"AND (COALESCE(match_score, -1) >= ? "
        f"     OR status IN ({','.join('?' * len(PIPELINE_STATUSES))}))",
        (min_score, *PIPELINE_STATUSES),
    ).fetchall()

    matcher: dict[str, TermStat] = {}
    desc: dict[str, TermStat] = {}
    for r in rows:
        try:
            verdict = json.loads(r["match_verdict"] or "{}")
        except json.JSONDecodeError:
            verdict = {}
        missing = verdict.get("missing_skills") or [] if isinstance(verdict, dict) else []
        for skill in missing:
            if not isinstance(skill, str) or not skill.strip():
                continue
            key = _norm_skill(skill)
            matcher.setdefault(key, TermStat(term=key)).add(
                r["id"], r["status"], r["applied_at"])
        for e in lex.hits(r["description"] or ""):
            if e["term"] in covered:
                continue
            desc.setdefault(e["term"], TermStat(
                term=e["term"], category=e["category"])).add(
                r["id"], r["status"], r["applied_at"])

    rank = sorted(matcher.values(), key=lambda t: -t.jobs)
    drank = sorted(desc.values(), key=lambda t: -t.jobs)
    return {"mode": "fleet", "min_score": min_score, "jobs_scanned": len(rows),
            "matcher_missing": [t.row() for t in rank],
            "description_gaps": [t.row() for t in drank]}


def job_gaps(conn: sqlite3.Connection, lex: Lexicon, covered: set[str],
             job_id: int) -> dict:
    r = conn.execute("SELECT id, company, title, description, match_verdict "
                     "FROM jobs WHERE id=?", (job_id,)).fetchone()
    if r is None:
        raise SystemExit(f"No job with id {job_id}")
    try:
        verdict = json.loads(r["match_verdict"] or "{}")
    except json.JSONDecodeError:
        verdict = {}
    if not isinstance(verdict, dict):
        verdict = {}
    hits = lex.hits(r["description"] or "")
    return {"mode": "job", "job_id": r["id"], "company": r["company"],
            "title": r["title"],
            "jd_terms_not_in_profile": sorted(
                e["term"] for e in hits if e["term"] not in covered),
            "matcher_missing": [_norm_skill(s) for s in
                                (verdict.get("missing_skills") or [])
                                if isinstance(s, str) and s.strip()],
            "matcher_reasons": verdict.get("reasons") or ""}


def _print_ranked(title: str, rows: list[dict], floor: int) -> None:
    shown = [r for r in rows if r["jobs"] >= floor]
    print(f"\n{title} ({len(shown)} terms in {floor}+ jobs; "
          f"{len(rows) - len(shown)} below floor):")
    print(f"  {'term':28s} {'jobs':>4s} {'applied':>7s} {'responded':>9s}  examples")
    for r in shown:
        print(f"  {r['term']:28s} {r['jobs']:4d} {r['applied']:7d} {r['responded']:9d}"
              f"  {','.join(str(i) for i in r['examples'])}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-score", type=int, default=70)
    ap.add_argument("--job", type=int, default=None, help="single-posting mode")
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()

    conn = connect()
    lex = Lexicon.load()
    covered = profile_covered(lex)

    if a.job is not None:
        out = job_gaps(conn, lex, covered, a.job)
        if a.as_json:
            print(json.dumps(out, indent=2))
            return
        print(f"#{out['job_id']} {out['company']} - {out['title']}")
        print(f"  JD terms not in profile: {', '.join(out['jd_terms_not_in_profile']) or 'none'}")
        print(f"  matcher missing_skills:  {', '.join(out['matcher_missing']) or 'none'}")
        if out["matcher_reasons"]:
            print(f"  matcher reasons: {out['matcher_reasons']}")
        return

    out = fleet_gaps(conn, lex, covered, a.min_score)
    if a.as_json:
        print(json.dumps(out, indent=2))
        return
    print(f"Scanned {out['jobs_scanned']} deduped jobs "
          f"(score >= {out['min_score']} or in pipeline).")
    _print_ranked("Matcher missing_skills (LLM-judged, primary)",
                  out["matcher_missing"], floor=2)
    _print_ranked("Description terms not in profile (lexicon scan)",
                  out["description_gaps"], floor=3)
    print("\nCounts are evidence, not verdicts: /jh-upskill classifies each term as "
          "vocabulary gap vs real gap vs noise.")


if __name__ == "__main__":
    main()
