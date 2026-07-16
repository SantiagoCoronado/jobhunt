#!/usr/bin/env bash
# Scheduled read-only AI pass: discover -> headless Claude (triage + match) -> digest.
# This is the "honest digest" ordering: scoring happens BEFORE notify, so the
# email contains today's jobs, not yesterday's leftovers.
#
# Nothing here submits an application. Tailoring and applying stay interactive.
#
# Run manually:            ./scripts/ai_pass.sh [--force]
# Install on a schedule:   ./mac/install-schedule.sh --ai
set -euo pipefail
cd "$(dirname "$0")/.."

# Same collapse-duplicate-wakes guard as run.sh, separate state file.
GUARD="data/.last_ai_pass"; MIN_GAP=64800
_mtime() { stat -c %Y "$1" 2>/dev/null || stat -f %m "$1"; }
if [ "${1:-}" != "--force" ] && [ -f "$GUARD" ] && [ $(( $(date +%s) - $(_mtime "$GUARD") )) -lt $MIN_GAP ]; then
  echo "Skipped: last AI pass was under 18h ago. Use --force to override."
  exit 0
fi

# Lockfile (mkdir is atomic) so a scheduled run never overlaps a manual one.
LOCK="data/.ai_pass.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "Skipped: another AI pass is running ($LOCK exists)."
  exit 0
fi
trap 'rmdir "$LOCK"' EXIT
mkdir -p data/logs && touch "$GUARD"
LOG="data/logs/ai-pass-$(date +%Y%m%d-%H%M).log"

[ -d .venv ] && source .venv/bin/activate || true

echo "== [1/3] Discover ==" | tee -a "$LOG"
python -m src.discover 2>&1 | tee -a "$LOG"

echo "== [2/3] Triage + match (headless Claude) ==" | tee -a "$LOG"
if command -v claude >/dev/null 2>&1; then
  # Read-only AI stages only: triage the discovered pile, score the keepers.
  # Tools are limited to local files + python; no browsing, no MCP, no submits.
  claude -p "Run the /jh-triage flow, then the /jh-match flow (use the scaled \
bucket-ordered pass if the pile is large). End with one line: jobs triaged, \
kept vs dropped, jobs scored, how many shortlisted." \
    --allowedTools "Bash(python:*)" "Bash(.venv/bin/python:*)" "Read" "Write" "Task" "Agent" "Skill" "Workflow" \
    --max-turns 100 2>&1 | tee -a "$LOG" \
    || echo "AI stage failed; digest will show the unscored backlog." | tee -a "$LOG"
else
  echo "claude CLI not found; skipping AI stage (digest will show unscored count)." | tee -a "$LOG"
fi

echo "== [3/3] Digest (now reflects today's scores) ==" | tee -a "$LOG"
python -m src.notify 2>&1 | tee -a "$LOG" || true

echo "AI pass complete. Log: $LOG"
