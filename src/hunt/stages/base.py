"""What every stage shares: the run context and the result a stage hands back."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..config import HuntConfig
from ..ledger import Ledger


@dataclass
class Context:
    cfg: HuntConfig
    ledger: Ledger
    harness: str
    cwd: Path
    emit: Callable[[str], None]

    @property
    def run_dir(self) -> Path:
        return self.ledger.run_dir

    def log_path(self, stage: str, unit: str) -> Path:
        path = self.run_dir / self.ledger.unit(stage, unit)["log"]
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


@dataclass
class StageResult:
    summary: dict[str, Any] = field(default_factory=dict)
    verdict: str | None = None            # None: the stage passed its check
    needs_human: list[str] = field(default_factory=list)
    stop: bool = False                    # pick found nothing: report, then stop (exit 3)


@dataclass(frozen=True)
class Stage:
    name: str
    kind: str                                              # python | fanned
    run: Callable[[Context], StageResult] | None = None    # python stages
    role: str | None = None                                # fanned: prompts/agents/<role>.md
    tools: frozenset[str] = frozenset()
    needs: frozenset[str] = frozenset()                    # capabilities the harness must grant

    @property
    def implemented(self) -> bool:
        return self.run is not None
