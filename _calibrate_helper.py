"""One-shot helper: navigate to Iklan Shopee on EVRB-M, scroll to cards,
then run the metric-card calibration with osascript dialogs."""
import sys
from shopee_ads_screenshot import (
    BRANDS,
    select_username_filter,
    search_shop,
    click_first_detail,
    click_iklan_shopee,
    close_popup,
    scroll_to_performa,
    calibrate_cards,
)

AKUN = sys.argv[1].upper() if len(sys.argv) > 1 else "EVRB-M"
username = BRANDS[AKUN]

print(f"Navigating to Iklan Shopee for {AKUN} ({username})...")
print("Make sure you're on the Pilih Toko page. Starting in 3s...")
import time
time.sleep(3)

select_username_filter()
search_shop(username)
click_first_detail()
click_iklan_shopee(AKUN)
close_popup()
scroll_to_performa()

print("Cards should now be visible. Starting calibration dialogs...")
calibrate_cards()
