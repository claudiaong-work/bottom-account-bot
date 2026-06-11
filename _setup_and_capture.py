"""Navigate to a brand's Iklan Shopee page, scroll to the Performa cards, and
take ONE full screencapture for precise card-center measurement. Leaves the page
in view (does NOT go back to Pilih Toko). No dialogs.

Usage: python3 _setup_and_capture.py [BRAND]   (default BR)
Start on the Pilih Toko page.
"""
import sys
import time
import subprocess
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

time.sleep(1.5)
out = "/tmp/cards_full.png"
subprocess.run(["screencapture", "-x", out])
print(f"\nCaptured full screen to {out}")
print("Page left in view. Measure card centers from the capture.")
