#!/usr/bin/env bash
# Scheduled read-only AI pass: hunt orchestrator (discover, triage, match) -> digest.
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

echo "== [1/2] Hunt: discover, triage, match (python -m src.hunt) ==" | tee -a "$LOG"
# Read-only AI stages only, under the orchestrator: a ledger in data/hunt/<run>/, retries,
# coverage checks, the models of config/hunt.toml. HUNT_HARNESS overrides [harness].default.
# A run that died earlier is never resumed here: a scheduled pass starts clean.
HARNESS_ARGS=()
[ -n "${HUNT_HARNESS:-}" ] && HARNESS_ARGS=(--harness "$HUNT_HARNESS")
python -m src.hunt run --to match ${HARNESS_ARGS[@]+"${HARNESS_ARGS[@]}"} 2>&1 | tee -a "$LOG" \
  || echo "Hunt stage failed (python -m src.hunt status latest); the digest shows the unscored backlog." | tee -a "$LOG"

echo "== [2/2] Digest (now reflects today's scores) ==" | tee -a "$LOG"
python -m src.notify 2>&1 | tee -a "$LOG" || true

echo "AI pass complete. Log: $LOG"
