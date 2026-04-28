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
DATE_FILTER_DROPDOWN = (1108, 479)
FILTER_1BULAN = (627, 628)
FILTER_3BULAN = (663, 662)

# Metric cards (4 per row, evenly spaced)
# Row 1 (y=564): Iklan Dilihat, Produk Terjual, Jumlah Klik, Penjualan dari Iklan
# Row 2 (y=666): Persentase Klik, Biaya Iklan, Pesanan, ROAS
METRIC_CARDS = {
    "Iklan Dilihat":        (459, 571),
    "Produk Terjual":       (473, 649),
    "Jumlah Klik":          (813, 552),
    "Penjualan dari Iklan": (798, 667),
    "Persentase Klik":      (1059, 568),
    "Biaya Iklan":          (1108, 656),
    "Pesanan":              (1395, 559),
    "ROAS":                 (1403, 664),
}
DESIRED_SELECTED = {"Biaya Iklan", "ROAS"}


# Search filter dropdown
NAMA_TOKO_DROPDOWN = (397, 322)
USERNAME_TOKO_OPTION = (418, 400)

# Screenshot crop region (pyautogui coords)
CROP_TOP_LEFT = (205, 458)
CROP_BOTTOM_RIGHT = (1621, 1000)

# Top-right account menu
ACCOUNT_BUTTON = (1645, 199)
GANTI_TOKO = (1486, 547)

# --- Brand list ---
BRANDS = {}
with open(os.path.join(os.path.dirname(__file__), "brands.csv")) as f:
    reader = csv.DictReader(f)
    for row in reader:
        BRANDS[row["akun"]] = row["shopee_username"]


def is_card_selected(card_pos, debug_name=None):
    """Check if a metric card is selected by scanning for a colored top border.
    Samples a wider strip above the card center to tolerate layout drift."""
    tmp_path = os.path.join(SCREENSHOT_DIR, "_tmp_detect.png")
    subprocess.run(["screencapture", "-x", tmp_path])
    from PIL import Image
    img = Image.open(tmp_path)
    cx, cy = card_pos
    colored_count = 0
    best_sample = (0, 0, 0, 0, 0)  # (dy, dx, r, g, b)
    best_sat = 0
    for dy in range(-70, -4):
        for dx in range(-80, 81, 10):
            px_x = (cx + dx) * 2
            px_y = (cy + dy) * 2
            r, g, b = img.getpixel((px_x, px_y))[:3]
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            saturation = (max_c - min_c) / max_c if max_c > 0 else 0
            if saturation > best_sat:
                best_sat = saturation
                best_sample = (dy, dx, r, g, b)
            if saturation > 0.25 and max_c > 100:
                colored_count += 1
    if debug_name:
        dy_b, dx_b, r, g, b = best_sample
        print(f"      [{debug_name}] colored={colored_count}, best_sat={best_sat:.2f} at dy={dy_b} dx={dx_b} rgb=({r},{g},{b})")
        # Save a debug crop centered on the card showing the sample region
        safe_name = debug_name.replace(" ", "_").replace("/", "_")
        dbg_path = os.path.join(SCREENSHOT_DIR, f"_dbg_{safe_name}.png")
        crop_box = (
            max(0, (cx - 100) * 2),
            max(0, (cy - 80) * 2),
            min(img.width, (cx + 100) * 2),
            min(img.height, (cy + 20) * 2),
        )
        img.crop(crop_box).save(dbg_path)
    os.remove(tmp_path)
    return colored_count >= 5


def notify(message):
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "Shopee Ads Bot"'
    ])


def take_screenshot(brand_akun, filter_name, y_offset=0):
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{brand_akun}_{filter_name}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    time.sleep(1.5)
    tmp_path = os.path.join(SCREENSHOT_DIR, "_tmp_full.png")
    subprocess.run(["screencapture", "-x", tmp_path])
    from PIL import Image
    img = Image.open(tmp_path)
    x1 = CROP_TOP_LEFT[0] * 2
    y1 = (CROP_TOP_LEFT[1] + y_offset) * 2
    x2 = CROP_BOTTOM_RIGHT[0] * 2
    y2 = (CROP_BOTTOM_RIGHT[1] + y_offset) * 2
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
    time.sleep(PAGE_LOAD_WAIT + 7)


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


def select_date_filter(filter_name, y_offset=0):
    pyautogui.moveTo(855, 400)
    time.sleep(0.5)
    pyautogui.click(DATE_FILTER_DROPDOWN[0], DATE_FILTER_DROPDOWN[1] + y_offset)
    time.sleep(2)
    if filter_name == "1bulan":
        pyautogui.click(FILTER_1BULAN[0], FILTER_1BULAN[1] + y_offset)
    else:
        pyautogui.click(FILTER_3BULAN[0], FILTER_3BULAN[1] + y_offset)
    time.sleep(PAGE_LOAD_WAIT + 2)


def scroll_to_performa():
    pyautogui.moveTo(855, 500)
    time.sleep(0.5)
    pyautogui.scroll(-7)
    time.sleep(SCROLL_DELAY)
    pyautogui.scroll(-8)
    time.sleep(SCROLL_DELAY)
    pyautogui.scroll(-3)
    time.sleep(2)


# Calibrated row-1 card top edge (logical y). Used as anchor for auto-detect.
EXPECTED_CARD_TOP_Y = 536


def detect_y_offset():
    """Scan for the actual top of row 1 cards and return offset from calibrated.
    Positive = page scrolled less than calibrated (cards lower); negative = more (cards higher)."""
    tmp_path = os.path.join(SCREENSHOT_DIR, "_tmp_offset.png")
    subprocess.run(["screencapture", "-x", tmp_path])
    from PIL import Image
    img = Image.open(tmp_path)
    _, height = img.size
    x_screen = METRIC_CARDS["Iklan Dilihat"][0] * 2
    in_white = False
    white_start = None
    for y in range(600, min(1500, height)):
        r, g, b = img.getpixel((x_screen, y))[:3]
        is_white = r > 248 and g > 248 and b > 248
        if is_white and not in_white:
            in_white = True
            white_start = y
        elif not is_white and in_white:
            run_len = y - white_start
            if run_len >= 100:
                actual_top_logical = white_start // 2
                os.remove(tmp_path)
                offset = actual_top_logical - EXPECTED_CARD_TOP_Y
                print(f"    Card top detected at logical y={actual_top_logical} (offset {offset:+d})")
                return offset
            in_white = False
    os.remove(tmp_path)
    print("    Could not detect card position, assuming offset=0")
    return 0


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

    print("  7b. Detecting card position offset...")
    y_offset = detect_y_offset()

    cards_adjusted = {name: (x, y + y_offset) for name, (x, y) in METRIC_CARDS.items()}

    print("  8. Setting chart metrics (need: only Biaya Iklan + ROAS)...")
    for name, pos in cards_adjusted.items():
        selected = is_card_selected(pos, debug_name=name)
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
        select_date_filter(filter_name, y_offset=y_offset)

        print(f"  8. Taking screenshot ({filter_name})...")
        path = take_screenshot(akun, filter_name, y_offset=y_offset)
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


def calibrate_cards():
    """Re-record the 8 metric card positions on the Iklan Shopee page."""
    print("\n=== METRIC CARDS CALIBRATION ===")
    subprocess.run([
        "osascript", "-e",
        'display dialog "Navigate to Iklan Shopee page, scroll so all 8 metric cards are visible. Click OK to start." with title "Calibrate Cards" buttons {"OK"} default button "OK"'
    ])

    card_names = [
        "Iklan Dilihat", "Produk Terjual", "Jumlah Klik", "Penjualan dari Iklan",
        "Persentase Klik", "Biaya Iklan", "Pesanan", "ROAS",
    ]
    results = {}
    for name in card_names:
        subprocess.run([
            "osascript", "-e",
            f'display dialog "Click OK then hover the CENTER of the \'{name}\' card within 5 seconds." with title "Calibrate Cards" buttons {{"OK"}} default button "OK"'
        ])
        time.sleep(5)
        pos = pyautogui.position()
        results[name] = (pos.x, pos.y)
        print(f"  {name} = ({pos.x}, {pos.y})")

    print("\n=== Paste into METRIC_CARDS in shopee_ads_screenshot.py ===")
    print("METRIC_CARDS = {")
    for name, (x, y) in results.items():
        print(f'    "{name}":{" " * (22 - len(name))}({x}, {y}),')
    print("}")


def calibrate_crop():
    """Re-record the screenshot crop region (Performa section)."""
    print("\n=== SCREENSHOT CROP CALIBRATION ===")
    subprocess.run([
        "osascript", "-e",
        'display dialog "Navigate to Iklan Shopee page, scroll so cards + chart + date axis are all visible. Click OK to start." with title "Calibrate Crop" buttons {"OK"} default button "OK"'
    ])

    subprocess.run([
        "osascript", "-e",
        'display dialog "Click OK then hover the TOP-LEFT corner of the area to capture within 5 seconds." with title "Calibrate Crop" buttons {"OK"} default button "OK"'
    ])
    time.sleep(5)
    tl = pyautogui.position()
    print(f"  TOP-LEFT = ({tl.x}, {tl.y})")

    subprocess.run([
        "osascript", "-e",
        'display dialog "Click OK then hover the BOTTOM-RIGHT corner (below the date axis) within 5 seconds." with title "Calibrate Crop" buttons {"OK"} default button "OK"'
    ])
    time.sleep(5)
    br = pyautogui.position()
    print(f"  BOTTOM-RIGHT = ({br.x}, {br.y})")

    print("\n=== Paste into shopee_ads_screenshot.py ===")
    print(f"CROP_TOP_LEFT = ({tl.x}, {tl.y})")
    print(f"CROP_BOTTOM_RIGHT = ({br.x}, {br.y})")


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--calibrate":
        calibrate()
        return

    if len(sys.argv) >= 2 and sys.argv[1] == "--calibrate-cards":
        calibrate_cards()
        return

    if len(sys.argv) >= 2 and sys.argv[1] == "--calibrate-crop":
        calibrate_crop()
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
