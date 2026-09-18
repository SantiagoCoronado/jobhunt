"""`config/hunt.toml`: HOW the hunt runs (harness, per-stage model, caps, timeouts, retries),
never what counts as a fit, which is `config/profile.yaml`'s job.

Decision 6 of the spec: a stage's `model` is a name the harness's LIVE catalog knows
(`python -m src.hunt models`) or absent, meaning the harness default. Nothing here checks a
model against a table in the repo; the catalog check runs at the start of a run (story 6).
Everything else is validated on load so a typo fails the command, never a hunt at minute 40:
unknown stage names, unknown keys, a model on a Python stage, non-positive caps.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..config import CONFIG_DIR

HUNT_TOML = CONFIG_DIR / "hunt.toml"

# The stage registry order (spec section 4). Fixed; `--from/--to/--only/--skip` select within it.
STAGES: tuple[str, ...] = ("discover", "triage", "match", "inbox", "pick", "research", "tailor", "report")
FANNED: frozenset[str] = frozenset({"triage", "match", "inbox", "research", "tailor"})
PYTHON_STAGES: frozenset[str] = frozenset(STAGES) - FANNED

# Decision 10 and 11 defaults, plus each stage's own knobs. A fanned stage may carry `model`
# and `harness` on top of these; a Python stage carries nothing (it runs in-process).
_DEFAULTS: dict[str, dict[str, Any]] = {
    "discover": {},
    "triage": {"concurrency": 8, "timeout_s": 300, "retries": 2, "min_pile": 200, "chunk": 100},
    "match": {"concurrency": 4, "timeout_s": 600, "retries": 2, "chunk": 60, "min_bucket": 3,
              "second_pass_min_bucket": 2, "budget_units": 12},
    "inbox": {"concurrency": 1, "timeout_s": 600, "retries": 1},
    "pick": {},
    "research": {"concurrency": 4, "timeout_s": 900, "retries": 1},
    "tailor": {"concurrency": 3, "timeout_s": 900, "retries": 1},
    "report": {},
}
_RUN_KEYS = ("concurrency", "timeout_s", "retries")
_MIN = {"concurrency": 1, "timeout_s": 1, "retries": 0, "min_pile": 0, "chunk": 1, "min_bucket": 0,
        "second_pass_min_bucket": 0, "budget_units": 0}


@dataclass(frozen=True)
class StageConfig:
    name: str
    fanned: bool
    model: str | None = None          # None: the harness default
    harness: str | None = None        # None: [harness].default
    concurrency: int = 1
    timeout_s: int = 600
    retries: int = 1
    options: dict[str, Any] = field(default_factory=dict)   # chunk, min_pile, min_bucket ...

    @property
    def attempts(self) -> int:
        """Decision 10: `retries = N` means at most 1 + N attempts per unit."""
        return 1 + self.retries

    def option(self, key: str) -> Any:
        return self.options[key]


@dataclass(frozen=True)
class HuntConfig:
    harness: str = "claude"
    global_concurrency: int = 8
    stages: dict[str, StageConfig] = field(default_factory=dict)
    pick_n: int = 5
    pick_dream_slots: int = 2
    harness_templates: dict[str, dict[str, Any]] = field(default_factory=dict)   # [harness.<name>]
    source: Path | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def stage(self, name: str) -> StageConfig:
        if name not in self.stages:
            raise ValueError(f"unknown stage '{name}' (known: {', '.join(STAGES)})")
        return self.stages[name]

    def harness_for(self, stage: str) -> str:
        """The harness a stage runs on: its own override, else the default."""
        return self.stage(stage).harness or self.harness

    def snapshot(self) -> dict[str, Any]:
        """What the ledger records as the config a run started with (spec section 7)."""
        return {
            "source": str(self.source) if self.source else None,
            "harness": {"default": self.harness, "global_concurrency": self.global_concurrency,
                        "templates": sorted(self.harness_templates)},
            "stages": {
                s.name: {"kind": "fanned" if s.fanned else "python", "model": s.model,
                         "harness": s.harness or self.harness,
                         **({"concurrency": s.concurrency, "timeout_s": s.timeout_s,
                             "retries": s.retries} if s.fanned else {}),
                         **s.options}
                for s in self.stages.values()
            },
            "pick": {"n": self.pick_n, "dream_slots": self.pick_dream_slots},
        }


def _where(source: Path | None) -> str:
    return str(source) if source else "hunt config"


def _int(block: dict[str, Any], key: str, default: int, where: str) -> int:
    value = block.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{where}: {key} must be an integer, got {value!r}")
    if value < _MIN.get(key, 0):
        raise ValueError(f"{where}: {key} must be at least {_MIN.get(key, 0)}, got {value}")
    return value


def _name(block: dict[str, Any], key: str, where: str) -> str | None:
    """A model or harness name; absent or "" means the default (the TUI writes "" to clear)."""
    value = block.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{where}: {key} must be a string, got {value!r}")
    return value.strip() or None


def _stage(name: str, block: Any, where: str) -> StageConfig:
    if not isinstance(block, dict):
        raise ValueError(f"{where}: [stages.{name}] must be a table")
    fanned = name in FANNED
    defaults = _DEFAULTS[name]
    allowed = set(defaults) | ({"model", "harness"} if fanned else set())
    unknown = sorted(set(block) - allowed)
    if unknown:
        if not fanned:
            raise ValueError(f"{where}: [stages.{name}] is a Python stage and takes no options, "
                             f"got {', '.join(unknown)}")
        raise ValueError(f"{where}: [stages.{name}] unknown key(s) {', '.join(unknown)} "
                         f"(allowed: {', '.join(sorted(allowed))})")
    if not fanned:
        return StageConfig(name=name, fanned=False)
    here = f"{where} [stages.{name}]"
    options = {k: _int(block, k, v, here) for k, v in defaults.items() if k not in _RUN_KEYS}
    return StageConfig(
        name=name, fanned=True,
        model=_name(block, "model", here), harness=_name(block, "harness", here),
        concurrency=_int(block, "concurrency", defaults["concurrency"], here),
        timeout_s=_int(block, "timeout_s", defaults["timeout_s"], here),
        retries=_int(block, "retries", defaults["retries"], here),
        options=options,
    )


def parse(raw: dict[str, Any], source: Path | None = None) -> HuntConfig:
    """Validate a decoded hunt.toml (an empty dict is the all-defaults config)."""
    where = _where(source)
    if not isinstance(raw, dict):
        raise ValueError(f"{where}: top level must be a table")
    known_top = {"harness", "stages", "pick"}
    stray = sorted(set(raw) - known_top)
    if stray:
        raise ValueError(f"{where}: unknown table(s) {', '.join(stray)} (allowed: harness, stages, pick)")

    harness = raw.get("harness") or {}
    if not isinstance(harness, dict):
        raise ValueError(f"{where}: [harness] must be a table")
    templates = {k: v for k, v in harness.items() if isinstance(v, dict)}
    for tname, block in templates.items():
        if "command" not in block:
            raise ValueError(f"{where}: [harness.{tname}] needs a `command` template (spec section 5)")
    default = _name(harness, "default", f"{where} [harness]") or "claude"
    stray = sorted(set(harness) - set(templates) - {"default", "global_concurrency"})
    if stray:
        raise ValueError(f"{where}: [harness] unknown key(s) {', '.join(stray)}")
    global_cap = _int(harness, "global_concurrency", 8, f"{where} [harness]")

    stages_raw = raw.get("stages") or {}
    if not isinstance(stages_raw, dict):
        raise ValueError(f"{where}: [stages] must be a table")
    unknown = sorted(set(stages_raw) - set(STAGES))
    if unknown:
        raise ValueError(f"{where}: unknown stage(s) {', '.join(unknown)} (known: {', '.join(STAGES)})")
    stages = {name: _stage(name, stages_raw.get(name, {}), where) for name in STAGES}

    pick = raw.get("pick") or {}
    if not isinstance(pick, dict):
        raise ValueError(f"{where}: [pick] must be a table")
    stray = sorted(set(pick) - {"n", "dream_slots"})
    if stray:
        raise ValueError(f"{where}: [pick] unknown key(s) {', '.join(stray)}")
    pick_n = _int(pick, "n", 5, f"{where} [pick]")
    dream_slots = _int(pick, "dream_slots", 2, f"{where} [pick]")
    if dream_slots > pick_n:
        raise ValueError(f"{where}: [pick] dream_slots ({dream_slots}) exceeds n ({pick_n})")

    return HuntConfig(harness=default, global_concurrency=global_cap, stages=stages,
                      pick_n=pick_n, pick_dream_slots=dream_slots, harness_templates=templates,
                      source=source, raw=raw)


def load(path: Path | None = None) -> HuntConfig:
    """Read hunt.toml (the shipped file by default). A missing file is the all-defaults config
    with every model unset, so a clone without the file still runs on the harness defaults."""
    path = path or HUNT_TOML
    if not path.exists():
        return parse({}, None)
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"{path}: not valid TOML: {e}") from e
    return parse(raw, path)


def defaults() -> HuntConfig:
    return parse({}, None)
