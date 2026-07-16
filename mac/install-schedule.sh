#!/usr/bin/env bash
# Install the macOS launchd daily job (parity with the Windows setup_task.ps1).
#
#   ./mac/install-schedule.sh        # plain daily: run.sh (discover + queue + digest)
#   ./mac/install-schedule.sh --ai   # AI pass: scripts/ai_pass.sh (discover + headless
#                                    # Claude triage/match + digest with fresh scores)
#
# The two variants are mutually exclusive: installing one unloads the other so
# discover never runs twice a day.
set -euo pipefail
cd "$(dirname "$0")/.."            # repo root
DIR="$(pwd)"

if [ "${1:-}" = "--ai" ]; then
  LABEL="com.jobhunt.aipass";  TEMPLATE="mac/com.jobhunt.aipass.plist";  OTHER="com.jobhunt.daily"
  TARGET="$DIR/scripts/ai_pass.sh"
else
  LABEL="com.jobhunt.daily";   TEMPLATE="mac/com.jobhunt.daily.plist";  OTHER="com.jobhunt.aipass"
  TARGET="$DIR/run.sh"
fi

PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
OTHER_PLIST="$HOME/Library/LaunchAgents/$OTHER.plist"
mkdir -p "$HOME/Library/LaunchAgents"

# Mutually exclusive with the other variant.
if [ -f "$OTHER_PLIST" ]; then
  launchctl unload "$OTHER_PLIST" 2>/dev/null || true
  rm "$OTHER_PLIST"
  echo "Removed the other variant: $OTHER"
fi

sed "s#__JOBHUNT_DIR__#$DIR#g" "$TEMPLATE" > "$PLIST"

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo "Installed: $PLIST"
echo "  -> runs $TARGET daily at 08:00 (and on next wake if asleep)."
echo
echo "Test now:   launchctl start $LABEL"
echo "Logs:       tail -f $DIR/data/launchd.out.log"
echo "Uninstall:  launchctl unload \"$PLIST\" && rm \"$PLIST\""
