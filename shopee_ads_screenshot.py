import pyautogui
import time
import subprocess
import os
import csv
import sys
import webbrowser
from datetime import datetime

from config import (
    SELLER_CENTER_URL,
    SCREENSHOT_DIR,
    PAGE_LOAD_WAIT,
    CLICK_DELAY,
    SCROLL_DELAY,
    POPUP_WAIT,
)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

# --- Coordinate map (pyautogui coords for 1710x1112 screen) ---
# Pilih Toko page
SEARCH_BOX = (511, 336)
FIRST_DETAIL_LINK = (1225, 540)

# Shop dashboard - sidebar
IKLAN_SHOPEE_MENU = (80, 739)

# Iklan Shopee page (positions after scrolling down)
DATE_FILTER_DROPDOWN = (1105, 328)
FILTER_1BULAN = (667, 464)
FILTER_3BULAN = (670, 494)

# Search filter dropdown
NAMA_TOKO_DROPDOWN = (397, 322)
USERNAME_TOKO_OPTION = (418, 400)

# Top-right account menu
ACCOUNT_BUTTON = (1645, 199)
GANTI_TOKO = (1509, 485)

# --- Brand list ---
BRANDS = {}
with open(os.path.join(os.path.dirname(__file__), "brands.csv")) as f:
    reader = csv.DictReader(f)
    for row in reader:
        BRANDS[row["akun"]] = row["shopee_username"]


def notify(message):
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "Shopee Ads Bot"'
    ])


def take_screenshot(brand_akun, filter_name):
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{brand_akun}_{filter_name}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    time.sleep(1.5)
    subprocess.run(["screencapture", "-x", filepath])
    print(f"  Saved: {filepath}")
    return filepath


def select_username_filter():
    pyautogui.click(*NAMA_TOKO_DROPDOWN)
    time.sleep(CLICK_DELAY)
    pyautogui.click(*USERNAME_TOKO_OPTION)
    time.sleep(CLICK_DELAY)


def search_shop(username):
    pyautogui.click(*SEARCH_BOX)
    time.sleep(CLICK_DELAY)
    pyautogui.hotkey("command", "a")
    time.sleep(0.2)
    pyautogui.typewrite(username, interval=0.03)
    time.sleep(0.3)
    pyautogui.press("enter")
    time.sleep(PAGE_LOAD_WAIT)


def click_first_detail():
    pyautogui.click(*FIRST_DETAIL_LINK)
    time.sleep(PAGE_LOAD_WAIT)


def click_iklan_shopee():
    pyautogui.click(*IKLAN_SHOPEE_MENU)
    time.sleep(PAGE_LOAD_WAIT)


def close_popup():
    time.sleep(POPUP_WAIT)
    # Try pressing Escape to close any popup
    pyautogui.press("escape")
    time.sleep(CLICK_DELAY)


def select_date_filter(filter_name):
    pyautogui.click(*DATE_FILTER_DROPDOWN)
    time.sleep(CLICK_DELAY)
    if filter_name == "1bulan":
        pyautogui.click(*FILTER_1BULAN)
    else:
        pyautogui.click(*FILTER_3BULAN)
    time.sleep(PAGE_LOAD_WAIT)


def scroll_to_performa():
    pyautogui.moveTo(855, 500)
    time.sleep(0.5)
    pyautogui.scroll(-7)
    time.sleep(SCROLL_DELAY)
    pyautogui.scroll(-8)
    time.sleep(SCROLL_DELAY)


def go_back_to_pilih_toko():
    pyautogui.click(*ACCOUNT_BUTTON)
    time.sleep(CLICK_DELAY)
    pyautogui.click(*GANTI_TOKO)
    time.sleep(PAGE_LOAD_WAIT)


def process_brand(akun):
    username = BRANDS.get(akun)
    if not username:
        print(f"  Brand '{akun}' not found in brands.csv, skipping.")
        return []

    print(f"\n{'='*50}")
    print(f"Processing: {akun} ({username})")
    print(f"{'='*50}")

    screenshots = []

    print("  1. Selecting 'Username Toko' filter...")
    select_username_filter()

    print("  2. Searching for shop...")
    search_shop(username)

    print("  3. Clicking Detail...")
    click_first_detail()

    print("  4. Clicking Iklan Shopee in sidebar...")
    click_iklan_shopee()

    print("  5. Closing popup...")
    close_popup()

    print("  6. Scrolling to Performa...")
    scroll_to_performa()

    for filter_name in ["1bulan", "3bulan"]:
        label = "1 bulan" if filter_name == "1bulan" else "3 bulan"
        print(f"  7. Selecting '{label}' filter...")
        select_date_filter(filter_name)

        print(f"  8. Taking screenshot ({filter_name})...")
        path = take_screenshot(akun, filter_name)
        screenshots.append(path)

    print("  9. Going back to Pilih Toko...")
    go_back_to_pilih_toko()

    return screenshots


def calibrate():
    """Interactive calibration mode - move mouse to each element."""
    print("\n=== CALIBRATION MODE ===")
    print("I'll guide you to hover over elements so we can record positions.")
    print("For each element, move your mouse there and press ENTER.\n")

    elements = [
        ("SEARCH_BOX", "the 'Cari' search input on Pilih Toko page"),
        ("FIRST_DETAIL_LINK", "the first 'Detail' link in the table"),
        ("IKLAN_SHOPEE_MENU", "'Iklan Shopee' in the left sidebar (enter a shop first)"),
        ("DATE_FILTER_DROPDOWN", "the date filter dropdown (e.g. '3 bulan terakhir')"),
        ("FILTER_1BULAN", "'1 bulan terakhir' option (open dropdown first)"),
        ("FILTER_3BULAN", "'3 bulan terakhir' option (open dropdown first)"),
        ("ACCOUNT_BUTTON", "the account/shop name at top-right"),
        ("GANTI_TOKO", "'Ganti toko' in the dropdown"),
    ]

    results = {}
    for name, desc in elements:
        input(f"Hover over {desc}, then press ENTER...")
        pos = pyautogui.position()
        results[name] = (pos.x, pos.y)
        print(f"  {name} = ({pos.x}, {pos.y})")

    print("\n=== Copy these into shopee_ads_screenshot.py ===")
    for name, (x, y) in results.items():
        print(f"{name} = ({x}, {y})")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 shopee_ads_screenshot.py BRAND1 BRAND2 ...")
        print("  python3 shopee_ads_screenshot.py --calibrate")
        print(f"\nAvailable brands: {', '.join(sorted(BRANDS.keys()))}")
        sys.exit(1)

    if sys.argv[1] == "--calibrate":
        calibrate()
        return

    brand_list = [b.strip().upper() for b in sys.argv[1:]]

    invalid = [b for b in brand_list if b not in BRANDS]
    if invalid:
        print(f"Unknown brands: {', '.join(invalid)}")
        print(f"Available: {', '.join(sorted(BRANDS.keys()))}")
        sys.exit(1)

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    print("=" * 50)
    print("Shopee Ads Screenshot Bot")
    print(f"Brands: {', '.join(brand_list)}")
    print("=" * 50)

    print("Starting in 3 seconds... switch to your browser!")
    time.sleep(3)

    all_screenshots = {}
    for akun in brand_list:
        screenshots = process_brand(akun)
        if screenshots:
            all_screenshots[akun] = screenshots

    print("\n" + "=" * 50)
    print("DONE! Screenshots saved:")
    for akun, paths in all_screenshots.items():
        print(f"  {akun}:")
        for p in paths:
            print(f"    - {p}")
    print("=" * 50)

    notify("All screenshots done!")
    return all_screenshots


if __name__ == "__main__":
    main()
