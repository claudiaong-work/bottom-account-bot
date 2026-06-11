"""Navigate to a brand's Iklan page, scroll, click the date button at a given
(x,y), and screencapture the OPEN dropdown so we can measure option positions.
Start on Pilih Toko. Usage: python3 _capture_dropdown.py [BRAND] [X] [Y]
"""
import sys, time, subprocess
import pyautogui
from shopee_ads_screenshot import (
    BRANDS,
    select_username_filter, search_shop, click_first_detail,
    click_iklan_shopee, close_popup, scroll_to_performa,
)

AKUN = sys.argv[1].upper() if len(sys.argv) > 1 else "MORI-M"
BX = int(sys.argv[2]) if len(sys.argv) > 2 else 1110
BY = int(sys.argv[3]) if len(sys.argv) > 3 else 467
print(f"Navigating to {AKUN}, will click date button at ({BX},{BY}). "
      f"Be on Pilih Toko. Starting in 3s — don't touch mouse...")
time.sleep(3)
select_username_filter()
search_shop(BRANDS[AKUN])
click_first_detail()
click_iklan_shopee(AKUN)
close_popup()
scroll_to_performa()
time.sleep(1)

pyautogui.click(BX, BY)
time.sleep(1.5)
subprocess.run(["screencapture", "-x", "/tmp/dd_open.png"])
print(f"Clicked ({BX},{BY}); captured /tmp/dd_open.png (dropdown should be open).")
