"""One-shot helper: navigate to Iklan Shopee, scroll to Performa, then run crop calibration."""
import sys
import time
from shopee_ads_screenshot import (
    BRANDS,
    select_username_filter,
    search_shop,
    click_first_detail,
    click_iklan_shopee,
    close_popup,
    scroll_to_performa,
    calibrate_crop,
)

AKUN = sys.argv[1].upper() if len(sys.argv) > 1 else "EVRB-M"
username = BRANDS[AKUN]

print(f"Navigating to Iklan Shopee for {AKUN} ({username})...")
print("Make sure you're on Pilih Toko. Starting in 3s...")
time.sleep(3)

select_username_filter()
search_shop(username)
click_first_detail()
click_iklan_shopee(AKUN)
close_popup()
scroll_to_performa()

print("Performa section should now be visible. Starting crop calibration dialogs...")
calibrate_crop()
