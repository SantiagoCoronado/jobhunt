#!/usr/bin/env bash
# One-command setup for a fresh machine (macOS or Linux/WSL).
# Usage:  ./setup.sh          (uses python3)
#         PYTHON=python3.12 ./setup.sh
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"
echo "== Creating virtualenv (.venv) with $("$PY" --version 2>&1) =="
"$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "== Installing dependencies (this pulls the Typst renderer, give it a minute) =="
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "== Creating your user files from the examples (git-ignored; existing files are kept) =="
python -m src.init
echo
echo "Setup complete. Next:"
echo "  source .venv/bin/activate"
echo "  python -m src.discover  # first discovery run"
echo "  # then, in Claude Code from this folder:  /jh-match  ->  /jh-tailor <id>  ->  /jh-followups"
echo
echo "To run it on a schedule:             docs/scheduling.md (cron or launchd, nothing installed)"
echo "To open the TUI with one word:       scripts/install_launcher.sh   # then: jobhunt"
