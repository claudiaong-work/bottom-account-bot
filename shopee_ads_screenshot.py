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
DATE_FILTER_DROPDOWN = (1083, 501)
FILTER_1BULAN = (641, 636)
FILTER_3BULAN = (649, 673)

# Metric cards (4 per row, evenly spaced)
# Row 1 (y=564): Iklan Dilihat, Produk Terjual, Jumlah Klik, Penjualan dari Iklan
# Row 2 (y=666): Persentase Klik, Biaya Iklan, Pesanan, ROAS
METRIC_CARDS = {
    "Iklan Dilihat":        (442, 564),
    "Produk Terjual":       (789, 564),
    "Jumlah Klik":          (1135, 564),
    "Penjualan dari Iklan": (1482, 564),
    "Persentase Klik":      (442, 666),
    "Biaya Iklan":          (789, 666),
    "Pesanan":              (1135, 666),
    "ROAS":                 (1482, 666),
}
DESIRED_SELECTED = {"Biaya Iklan", "ROAS"}


# Search filter dropdown
NAMA_TOKO_DROPDOWN = (397, 322)
USERNAME_TOKO_OPTION = (418, 400)

# Screenshot crop region (pyautogui coords)
CROP_TOP_LEFT = (206, 412)
CROP_BOTTOM_RIGHT = (1630, 1006)

# Top-right account menu
ACCOUNT_BUTTON = (1645, 199)
GANTI_TOKO = (1486, 547)

# --- Brand list ---
BRANDS = {}
with open(os.path.join(os.path.dirname(__file__), "brands.csv")) as f:
    reader = csv.DictReader(f)
    for row in reader:
        BRANDS[row["akun"]] = row["shopee_username"]


def is_card_selected(card_pos):
    """Check if a metric card is selected by scanning for a colored top border.
    Samples pixels in a strip above the card center (y-35 to y-25)."""
    tmp_path = os.path.join(SCREENSHOT_DIR, "_tmp_detect.png")
    subprocess.run(["screencapture", "-x", tmp_path])
    from PIL import Image
    img = Image.open(tmp_path)
    cx, cy = card_pos
    colored_count = 0
    for dy in range(-35, -24):
        for dx in range(-40, 41, 10):
            px_x = (cx + dx) * 2
            px_y = (cy + dy) * 2
            r, g, b = img.getpixel((px_x, px_y))[:3]
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            saturation = (max_c - min_c) / max_c if max_c > 0 else 0
            if saturation > 0.3 and max_c > 100:
                colored_count += 1
    os.remove(tmp_path)
    return colored_count >= 3


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
    # Take full screenshot then crop to Performa section
    tmp_path = os.path.join(SCREENSHOT_DIR, "_tmp_full.png")
    subprocess.run(["screencapture", "-x", tmp_path])
    from PIL import Image
    img = Image.open(tmp_path)
    # Retina 2x: multiply pyautogui coords by 2
    x1 = CROP_TOP_LEFT[0] * 2
    y1 = CROP_TOP_LEFT[1] * 2
    x2 = CROP_BOTTOM_RIGHT[0] * 2
    y2 = CROP_BOTTOM_RIGHT[1] * 2
    cropped = img.crop((x1, y1, x2, y2))
    cropped.save(filepath)
    os.remove(tmp_path)
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


def get_seller_domain(akun):
    if akun.startswith("TH."):
        return "seller.shopee.co.th"
    return "seller.shopee.co.id"


def click_iklan_shopee(akun):
    domain = get_seller_domain(akun)
    pyautogui.hotkey("command", "l")
    time.sleep(0.5)
    pyautogui.typewrite(f"https://{domain}/portal/marketing/pas/index", interval=0.01)
    time.sleep(0.3)
    pyautogui.press("enter")
    time.sleep(PAGE_LOAD_WAIT + 2)


def is_popup_present():
    """Check if a dimmed overlay (popup backdrop) is visible."""
    tmp_path = os.path.join(SCREENSHOT_DIR, "_tmp_popup.png")
    subprocess.run(["screencapture", "-x", tmp_path])
    from PIL import Image
    img = Image.open(tmp_path)
    sample_points = [(400, 900), (1400, 900), (400, 300)]
    dim_count = 0
    for x, y in sample_points:
        r, g, b = img.getpixel((x * 2, y * 2))[:3]
        if r < 80 and g < 80 and b < 80:
            dim_count += 1
    os.remove(tmp_path)
    return dim_count >= 2


def close_popup():
    time.sleep(POPUP_WAIT)
    if not is_popup_present():
        print("    No popup detected, continuing...")
        return
    pyautogui.press("escape")
    time.sleep(CLICK_DELAY)
    if not is_popup_present():
        print("    Popup closed with Escape")
        return
    pyautogui.press("escape")
    time.sleep(CLICK_DELAY)
    if not is_popup_present():
        print("    Popup closed with second Escape")
        return
    subprocess.run([
        "osascript", "-e",
        'display dialog "Popup still open — please close it, then click OK." with title "Shopee Ads Bot" buttons {"OK"} default button "OK" with icon caution'
    ])


def select_date_filter(filter_name):
    pyautogui.moveTo(855, 400)
    time.sleep(0.5)
    pyautogui.click(*DATE_FILTER_DROPDOWN)
    time.sleep(2)
    if filter_name == "1bulan":
        pyautogui.click(*FILTER_1BULAN)
    else:
        pyautogui.click(*FILTER_3BULAN)
    time.sleep(PAGE_LOAD_WAIT + 2)


def scroll_to_performa():
    pyautogui.moveTo(855, 500)
    time.sleep(0.5)
    pyautogui.scroll(-7)
    time.sleep(SCROLL_DELAY)
    pyautogui.scroll(-8)
    time.sleep(2)


def go_back_to_pilih_toko(akun=None):
    pyautogui.hotkey("command", "l")
    time.sleep(0.5)
    pyautogui.typewrite("https://seller.shopee.co.id/portal/shop", interval=0.01)
    time.sleep(0.3)
    pyautogui.press("enter")
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

    print("  4. Navigating to Iklan Shopee...")
    click_iklan_shopee(akun)

    print("  5. Closing popup...")
    close_popup()

    print("  7. Scrolling to Performa section...")
    scroll_to_performa()

    print("  8. Setting chart metrics (need: only Biaya Iklan + ROAS)...")
    for name, pos in METRIC_CARDS.items():
        selected = is_card_selected(pos)
        should_be = name in DESIRED_SELECTED
        if selected and not should_be:
            print(f"    {name} is ON → clicking to deselect")
            pyautogui.click(*pos)
            time.sleep(1)
        elif not selected and should_be:
            print(f"    {name} is OFF → clicking to select")
            pyautogui.click(*pos)
            time.sleep(1)
        else:
            status = "ON" if selected else "OFF"
            print(f"    {name} {status} → OK")

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
    if len(sys.argv) >= 2 and sys.argv[1] == "--calibrate":
        calibrate()
        return

    if len(sys.argv) >= 2:
        brand_list = [b.strip().upper() for b in sys.argv[1:]]
    else:
        from read_brands_from_sheet import fetch_bottom_brands
        print("No brands specified — fetching from Google Sheet...")
        brand_list = fetch_bottom_brands()
        brand_list = [b for b in brand_list if b in BRANDS]
        if not brand_list:
            print("No brands found in sheet (or none matched brands.csv).")
            sys.exit(1)
        print(f"Found {len(brand_list)} brands: {', '.join(brand_list)}")

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
