#!/bin/bash
# Daily MM Dashboard update pipeline — the "learns and improves every day" automation.
#
# Runs 5 steps in order:
#   1. refresh_dwh_snapshots.py — refresh DWH actuals and Smart Calendar snapshots up to
#                                 yesterday, when those rows are available in the DWH
#   2. pull_real_months.py      — force-refresh Monday content + merge the new DWH snapshots
#   3. calibrate_model.py       — recompute every prediction-model constant from the CURRENT
#                                 full real dataset (this is what makes predictions improve daily)
#   4. build_calendar_html.py   — rebuild the dashboard with the new content + calibration
#   5. validate_calendar.py     — fail the daily run if hard planning rules are violated
#
# Meant to run once a day, unattended, via launchd (see scripts/install_daily_automation.sh).
# Safe to also run manually any time: cd "Cursor Work" && ./scripts/daily_update.sh
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

LOG_DIR="$ROOT/mm_calendar/data/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/daily_update.log"
STAMP="$(date '+%Y-%m-%d %H:%M:%S')"

# Keep the log from growing forever — trim to the last ~2000 lines before each run.
if [ -f "$LOG_FILE" ]; then
  tail -n 2000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

{
  echo ""
  echo "===== $STAMP : daily_update.sh starting ====="

  STEP_OK=1

  echo "--- [1/5] refresh_dwh_snapshots.py (DWH actuals + Smart Calendar through yesterday) ---"
  if python3 scripts/refresh_dwh_snapshots.py; then
    echo "[1/5] OK"
  else
    echo "[1/5] FAILED — aborting (keeping yesterday's data/dashboard untouched)"
    STEP_OK=0
  fi

  if [ "$STEP_OK" = "1" ]; then
    echo "--- [2/5] pull_real_months.py --refresh (force-refresh Monday content + merge real outcomes) ---"
    if python3 scripts/pull_real_months.py --refresh; then
      echo "[2/5] OK"
    else
      echo "[2/5] FAILED — aborting (keeping yesterday's dashboard untouched)"
      STEP_OK=0
    fi
  fi

  if [ "$STEP_OK" = "1" ]; then
    echo "--- [3/5] calibrate_model.py (recompute model constants from real data) ---"
    if python3 scripts/calibrate_model.py; then
      echo "[3/5] OK"
    else
      echo "[3/5] FAILED — aborting (keeping yesterday's dashboard untouched)"
      STEP_OK=0
    fi
  fi

  if [ "$STEP_OK" = "1" ]; then
    echo "--- [4/5] build_calendar_html.py (rebuild dashboard) ---"
    if python3 scripts/build_calendar_html.py; then
      echo "[4/5] OK"
    else
      echo "[4/5] FAILED"
      STEP_OK=0
    fi
  fi

  if [ "$STEP_OK" = "1" ]; then
    echo "--- [5/5] validate_calendar.py (hard-rule validation) ---"
    if python3 scripts/validate_calendar.py; then
      echo "[5/5] OK"
    else
      echo "[5/5] FAILED"
      STEP_OK=0
    fi
  fi

  if [ "$STEP_OK" = "1" ]; then
    echo "===== $(date '+%Y-%m-%d %H:%M:%S') : daily_update.sh SUCCESS ====="
  else
    echo "===== $(date '+%Y-%m-%d %H:%M:%S') : daily_update.sh FAILED — see above ====="
  fi
} >> "$LOG_FILE" 2>&1

# Also echo a short status to stdout/stderr (visible if run manually or checked via launchd's
# own stdout/stderr log files).
tail -n 20 "$LOG_FILE"
