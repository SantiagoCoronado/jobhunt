#!/usr/bin/env bash
# One-command setup (macOS or Linux/WSL): a python check, then the installer, `python -m src.setup`.
# Usage:  ./setup.sh                       asks which agent CLIs you use
#         ./setup.sh --harness claude,pi   no question;  --yes takes the CLIs on PATH
#         ./setup.sh --check               report only, writes nothing
#         PYTHON=python3.12 ./setup.sh
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "setup: $PY not found; install Python 3.11 or newer, or point PYTHON at one" >&2
  exit 1
fi
if ! "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
  echo "setup: jobhunt needs Python 3.11 or newer ($("$PY" --version 2>&1) found); set PYTHON=python3.12 or similar" >&2
  exit 1
fi
exec "$PY" -m src.setup "$@"
