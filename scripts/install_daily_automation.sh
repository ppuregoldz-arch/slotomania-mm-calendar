#!/bin/bash
# Installs the MM Dashboard daily update as a real macOS background job (launchd), so it
# runs automatically once a day WITHOUT Cursor, this chat, or any terminal needing to be open.
#
# Usage:
#   ./scripts/install_daily_automation.sh install    # install + start the daily job
#   ./scripts/install_daily_automation.sh uninstall   # stop + remove it
#   ./scripts/install_daily_automation.sh status      # check if it's currently loaded
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_SRC="$ROOT/scripts/com.mmdashboard.dailyupdate.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.mmdashboard.dailyupdate.plist"
LABEL="com.mmdashboard.dailyupdate"

case "${1:-}" in
  install)
    mkdir -p "$HOME/Library/LaunchAgents"
    mkdir -p "$ROOT/mm_calendar/data/logs"
    cp "$PLIST_SRC" "$PLIST_DST"
    chmod +x "$ROOT/scripts/daily_update.sh"
    # Unload first in case it's already loaded (safe no-op if not), then load fresh.
    launchctl unload "$PLIST_DST" 2>/dev/null || true
    launchctl load "$PLIST_DST"
    echo "Installed and loaded '$LABEL'."
    echo "It will run automatically every day at 10:00 (edit the plist's Hour/Minute + reinstall to change)."
    echo "It also just ran once now (RunAtLoad) — check the log:"
    echo "  tail -f \"$ROOT/mm_calendar/data/logs/daily_update.log\""
    ;;
  uninstall)
    launchctl unload "$PLIST_DST" 2>/dev/null || true
    rm -f "$PLIST_DST"
    echo "Uninstalled '$LABEL'. The dashboard itself is untouched — this only stops the automatic daily refresh."
    ;;
  status)
    if launchctl list | grep -q "$LABEL"; then
      echo "'$LABEL' is loaded and scheduled."
      launchctl list "$LABEL"
    else
      echo "'$LABEL' is NOT currently loaded. Run: ./scripts/install_daily_automation.sh install"
    fi
    ;;
  *)
    echo "Usage: $0 {install|uninstall|status}"
    exit 1
    ;;
esac
