#!/bin/zsh
# Sends the Shopee login-reminder email with this week's brand list.
# Invoked by the com.aha.bottom-reminder LaunchAgent at 08:00 every Thursday.

PROJECT_DIR="/Users/claudia/bottom-account-automation"
PYTHON="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
STAMP="$(date +%Y%m%d)"

cd "$PROJECT_DIR" || exit 1
echo "===== Reminder started: $(date) =====" >> "$LOG_DIR/reminder_$STAMP.log"
"$PYTHON" -c "from read_brands_from_sheet import fetch_bottom_brands; from send_email import send_login_reminder; send_login_reminder(fetch_bottom_brands())" >> "$LOG_DIR/reminder_$STAMP.log" 2>&1
echo "===== Reminder finished: $(date) (exit $?) =====" >> "$LOG_DIR/reminder_$STAMP.log"
