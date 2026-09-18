"""The stage registry (spec section 4): fixed order, two kinds. Python stages run in-process
and are done when their check passes; fanned stages plan units, run them through the pool
(`fan.py`) and ingest. A fanned stage registered without a runner has not landed yet and
`hunt run` refuses it by name."""
from __future__ import annotations

from ..config import STAGES
from . import discover, match, pick, report, triage
from .base import Context, Stage, StageResult

REGISTRY: dict[str, Stage] = {
    "discover": Stage("discover", "python", run=discover.run),
    "triage": Stage("triage", "fanned", run=triage.run, role="triager", tools=frozenset({"read", "write"})),
    "match": Stage("match", "fanned", run=match.run, role="job-matcher", tools=frozenset({"read", "write"})),
    "inbox": Stage("inbox", "fanned", role="inbox-classifier", tools=frozenset({"read", "bash"})),
    "pick": Stage("pick", "python", run=pick.run),
    "research": Stage("research", "fanned", role="company-researcher",
                      tools=frozenset({"read", "write", "bash", "web"}), needs=frozenset({"web"})),
    "tailor": Stage("tailor", "fanned", role="resume-tailor", tools=frozenset({"read", "write", "edit", "bash"})),
    "report": Stage("report", "python", run=report.run),
}
assert tuple(REGISTRY) == STAGES

__all__ = ["REGISTRY", "Context", "Stage", "StageResult"]
