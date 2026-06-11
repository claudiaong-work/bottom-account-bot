#!/bin/zsh
# Weekly Thursday runner for the Bottom Account screenshot bot.
# Invoked by the com.aha.bottom-screenshot LaunchAgent at 09:00 every Thursday.
# Requires: Mac awake, logged in to Shopee Seller Centre, on the "Pilih Toko" page.

PROJECT_DIR="/Users/claudia/bottom-account-automation"
PYTHON="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
STAMP="$(date +%Y%m%d)"

cd "$PROJECT_DIR" || exit 1
echo "===== Run started: $(date) =====" >> "$LOG_DIR/screenshot_$STAMP.log"
"$PYTHON" shopee_ads_screenshot.py >> "$LOG_DIR/screenshot_$STAMP.log" 2>&1
echo "===== Run finished: $(date) (exit $?) =====" >> "$LOG_DIR/screenshot_$STAMP.log"
