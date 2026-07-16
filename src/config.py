"""Tiny YAML config loader shared across scripts."""
from __future__ import annotations

import os
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


def notify_setting(key: str, default):
    """Read one key from config/notify.yaml; falls back to default if the file
    is absent (it is gitignored, so fresh clones won't have it)."""
    try:
        return load_yaml("notify.yaml").get(key, default)
    except FileNotFoundError:
        return default


def followup_days() -> int:
    """Days after applying (or after a contact bump) that a follow-up comes due."""
    raw = notify_setting("followup_days", 7)
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"config/notify.yaml: followup_days must be an integer, got {raw!r}")


_ENV_CACHE: dict | None = None


def load_env() -> dict:
    """Parse ROOT/.env into a dict (cached). Blanks and `# comments` skipped.

    Supports optional `export ` prefix and single/double-quoted values. Does NOT
    mutate os.environ, so real environment variables always win in get_secret().
    """
    global _ENV_CACHE
    if _ENV_CACHE is not None:
        return _ENV_CACHE
    env: dict[str, str] = {}
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key:
                env[key] = val
    _ENV_CACHE = env
    return env


def get_secret(key: str, default: str | None = None) -> str | None:
    """Read a secret: real environment first, then .env, then default."""
    val = os.environ.get(key)
    if val:
        return val
    return load_env().get(key, default)
