#!/usr/bin/env bash
# Daily driver: discover new jobs, queue them for scoring, push a digest.
# The AI stages (scoring, tailoring) run inside Claude Code via /match and /tailor, 
# they are intentionally NOT auto-run here so a human stays in the loop.
set -euo pipefail
cd "$(dirname "$0")"

# Guard: the logon + unlock triggers can fire many times a day; collapse them into one
# real run (minimum ~18h gap). Pass --force to override for a manual run.
GUARD="data/.last_run"; MIN_GAP=64800
# portable file mtime: GNU stat (Linux/WSL) falls back to BSD stat (macOS)
_mtime() { stat -c %Y "$1" 2>/dev/null || stat -f %m "$1"; }
if [ "${1:-}" != "--force" ] && [ -f "$GUARD" ] && [ $(( $(date +%s) - $(_mtime "$GUARD") )) -lt $MIN_GAP ]; then
  echo "Skipped: last run was under 18h ago. Use ./run.sh --force to override."
  exit 0
fi
mkdir -p data && touch "$GUARD"

# activate venv if present
[ -d .venv ] && source .venv/bin/activate || true

echo "== [1/3] Discover =="
python -m src.discover

echo "== [2/3] Queue for scoring =="
python -m src.match export --limit 40

echo "== [3/3] Notify (digest of already-scored matches) =="
python -m src.notify || true

cat <<'EOF'

Next (in Claude Code, from this folder):
  /match              # score the freshly queued jobs
  /tailor <job_id>    # tailor resume + cover letter for a shortlisted job
  /notion-sync        # mirror pipeline to Notion
  /followups          # draft follow-ups for due applications

Or open the local CRM:  python -m src.crm.viewer  ->  http://localhost:5000
EOF
