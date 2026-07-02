#!/usr/bin/env bash
# Install the macOS launchd daily job (parity with the Windows setup_task.ps1).
# Schedules ./run.sh at 08:00 local; run.sh's own 18h guard collapses duplicate wakes.
set -euo pipefail
cd "$(dirname "$0")/.."            # repo root
DIR="$(pwd)"

LABEL="com.jobhunt.daily"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
mkdir -p "$HOME/Library/LaunchAgents"

sed "s#__JOBHUNT_DIR__#$DIR#g" mac/com.jobhunt.daily.plist > "$PLIST"

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo "Installed: $PLIST"
echo "  -> runs $DIR/run.sh daily at 08:00 (and on next wake if asleep)."
echo
echo "Test now:   launchctl start $LABEL"
echo "Logs:       tail -f $DIR/data/launchd.out.log"
echo "Uninstall:  launchctl unload \"$PLIST\" && rm \"$PLIST\""
