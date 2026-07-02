"""Tiny YAML config loader shared across scripts."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"


def load_yaml(name: str) -> dict:
    import yaml  # PyYAML

    path = CONFIG_DIR / name if not name.startswith("/") else Path(name)
    if not path.exists():
        raise FileNotFoundError(f"Missing config: {path}. Copy the .example and edit it.")
    with open(path) as f:
        return yaml.safe_load(f) or {}
