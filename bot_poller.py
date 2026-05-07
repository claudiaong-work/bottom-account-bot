import time
import subprocess
import sys
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "service_account.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SHEET_ID = "1POC6XDI1WEcSUEQG4rXgW5I2SkQwicduVJ9OY1wOW_4"
TRIGGER_CELL = "Bottom!L1"
STATUS_CELL = "Bottom!L2"
POLL_INTERVAL = 120


def get_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def read_cell(service, cell):
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=cell
    ).execute()
    values = result.get("values", [[""]])
    return values[0][0] if values and values[0] else ""


def write_cell(service, cell, value):
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=cell,
        valueInputOption="RAW",
        body={"values": [[value]]},
    ).execute()


def run_bot():
    screenshot_proc = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, "shopee_ads_screenshot.py")],
        capture_output=True, text=True
    )
    print(screenshot_proc.stdout)
    if screenshot_proc.stderr:
        print(screenshot_proc.stderr)

    if screenshot_proc.returncode != 0:
        return False, screenshot_proc.stderr

    from read_brands_from_sheet import fetch_bottom_brands
    brands = fetch_bottom_brands()
    brand_args = " ".join(brands)

    insert_proc = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, "insert_to_slides.py")] + brands,
        capture_output=True, text=True
    )
    print(insert_proc.stdout)
    if insert_proc.stderr:
        print(insert_proc.stderr)

    return insert_proc.returncode == 0, insert_proc.stdout


def main():
    print(f"Bot poller started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Polling {TRIGGER_CELL} every {POLL_INTERVAL}s...")

    service = get_service()
    write_cell(service, STATUS_CELL, "IDLE")

    while True:
        try:
            trigger = read_cell(service, TRIGGER_CELL)

            if trigger.upper() == "RUN":
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Trigger detected! Starting bot...")
                write_cell(service, TRIGGER_CELL, "")
                write_cell(service, STATUS_CELL, "RUNNING...")

                success, output = run_bot()

                if success:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    write_cell(service, STATUS_CELL, f"DONE ({timestamp})")
                    print(f"Bot completed successfully at {timestamp}")

                    from send_email import send_success_report
                    from read_brands_from_sheet import fetch_bottom_brands
                    brands = fetch_bottom_brands()
                    results = {b: [True] for b in brands}
                    send_success_report(results)
                else:
                    write_cell(service, STATUS_CELL, "ERROR - check Mac Mini")
                    print(f"Bot failed!")

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
