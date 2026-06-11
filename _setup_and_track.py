"""Navigate to a brand's Iklan Shopee page, scroll to the Performa cards, then
run a live mouse-position tracker so you can hover each card and read its
logical coordinate. Logs to mouse_positions.txt (one line every 0.3s).

Usage: python3 _setup_and_track.py [BRAND]   (default BR)
Start on the Pilih Toko page. Ctrl+C / kill to stop tracking.
"""
import sys
import time
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
print("Make sure you're on the Pilih Toko page. Starting in 3s — don't touch the mouse...")
time.sleep(3)

select_username_filter()
search_shop(username)
click_first_detail()
click_iklan_shopee(AKUN)
close_popup()
scroll_to_performa()

print("\n" + "=" * 50)
print("Page is set up. Hover over any card to read its coordinate.")
print("Live position (also logged to mouse_positions.txt):")
print("=" * 50)

with open("mouse_positions.txt", "w") as f:
    try:
        while True:
            pos = pyautogui.position()
            line = f"x={pos.x}, y={pos.y}"
            print(f"\r{line}        ", end="", flush=True)
            f.write(line + "\n")
            f.flush()
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("\nDone!")
