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

if [ ! -f config/notify.yaml ]; then
  cp config/notify.yaml.example config/notify.yaml
  echo "== Created config/notify.yaml from the example (git-ignored)."
  echo "   Add your Gmail app password there to enable the email digest. =="
fi

mkdir -p data applications
echo
echo "Setup complete. Next:"
echo "  source .venv/bin/activate"
echo "  ./run.sh --force        # first discovery run"
echo "  # then, in Claude Code from this folder:  /jh-match  ->  /jh-tailor <id>  ->  /jh-followups"
echo
echo "To schedule the daily run on macOS:  ./mac/install-schedule.sh"
