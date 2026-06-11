"""Navigate to a brand's Iklan Shopee page, scroll to Performa, then recalibrate
the 3 date-filter coords (dropdown button + '1 bulan' + '3 bulan' options) with
osascript dialogs. Start on the Pilih Toko page.

Usage: python3 _calibrate_date_full.py [BRAND]   (default BR)
"""
import sys
import time
import subprocess
import pyautogui
from shopee_ads_screenshot import (
    BRANDS,
    select_username_filter,
    search_shop,
    click_first_detail,
    click_iklan_shopee,
    close_popup,
    scroll_to_performa,
)

AKUN = sys.argv[1].upper() if len(sys.argv) > 1 else "BR"
username = BRANDS[AKUN]

print(f"Navigating to Iklan Shopee for {AKUN} ({username})...")
print("Be on the Pilih Toko page. Starting in 3s — don't touch the mouse...")
time.sleep(3)

select_username_filter()
search_shop(username)
click_first_detail()
click_iklan_shopee(AKUN)
close_popup()
scroll_to_performa()
print("Page set up. Starting date-filter calibration dialogs...\n")

steps = [
    ("DATE_FILTER_DROPDOWN", "the date filter dropdown button (e.g. '1 Bulan Terakhir (GMT+7)')", False),
    ("FILTER_1BULAN", "the '1 bulan terakhir' option (the dropdown will be opened for you)", True),
    ("FILTER_3BULAN", "the '3 bulan terakhir' option (the dropdown will be re-opened)", True),
]

results = {}
for name, desc, needs_dropdown_open in steps:
    if needs_dropdown_open and "DATE_FILTER_DROPDOWN" in results:
        x, y = results["DATE_FILTER_DROPDOWN"]
        pyautogui.click(x, y)
        time.sleep(1.5)
    subprocess.run([
        "osascript", "-e",
        f'display dialog "Click OK then hover {desc} within 5 seconds." '
        f'with title "Calibrate Date Filter" buttons {{"OK"}} default button "OK"'
    ])
    time.sleep(5)
    pos = pyautogui.position()
    results[name] = (pos.x, pos.y)
    print(f"  {name} = ({pos.x}, {pos.y})")

print("\n=== Paste into shopee_ads_screenshot.py ===")
for name, (x, y) in results.items():
    print(f"{name} = ({x}, {y})")
