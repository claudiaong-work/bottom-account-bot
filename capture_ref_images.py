"""
Helper to capture reference images for PyAutoGUI image matching.
Run this once to create the reference images the bot needs.

For each element, the script will:
1. Tell you what to make visible on screen
2. Wait for you to press ENTER
3. Let you select the region by clicking top-left then bottom-right
"""

import pyautogui
import time
import os

REF_DIR = os.path.join(os.path.dirname(__file__), "ref_images")
os.makedirs(REF_DIR, exist_ok=True)

ELEMENTS = [
    ("search_box", "the 'Cari' search box on the Pilih Toko page"),
    ("detail_button", "a 'Detail' link/button in the shop list"),
    ("iklan_shopee_menu", "the 'Iklan Shopee' menu item in the left sidebar"),
    ("popup_close", "the 'X' close button on any popup (if visible)"),
    ("date_filter", "the date filter dropdown (e.g. '3 bulan terakhir')"),
    ("filter_1bulan", "the '1 bulan terakhir' option in the dropdown"),
    ("filter_3bulan", "the '3 bulan terakhir' option in the dropdown"),
    ("account_topright", "the account/shop name at the top-right corner"),
    ("ganti_toko", "the 'Ganti toko' option in the dropdown menu"),
]


def capture_element(name, description):
    print(f"\n{'='*50}")
    print(f"Capture: {name}")
    print(f"Make sure '{description}' is visible on screen.")
    input("Press ENTER, then click TOP-LEFT corner of the element...")
    time.sleep(0.5)

    print("Click the TOP-LEFT corner now...")
    time.sleep(3)
    x1, y1 = pyautogui.position()
    print(f"  Top-left: ({x1}, {y1})")

    print("Now click the BOTTOM-RIGHT corner...")
    time.sleep(3)
    x2, y2 = pyautogui.position()
    print(f"  Bottom-right: ({x2}, {y2})")

    region = (x1, y1, x2 - x1, y2 - y1)
    screenshot = pyautogui.screenshot(region=region)
    filepath = os.path.join(REF_DIR, f"{name}.png")
    screenshot.save(filepath)
    print(f"  Saved: {filepath}")


def main():
    print("Reference Image Capture Tool")
    print("=" * 50)
    print("This will help you capture UI elements for the bot.")
    print("You have 3 seconds after pressing ENTER to position your cursor.\n")

    for name, desc in ELEMENTS:
        filepath = os.path.join(REF_DIR, f"{name}.png")
        if os.path.exists(filepath):
            skip = input(f"'{name}' already exists. Skip? (Y/n): ").strip().lower()
            if skip != "n":
                continue
        capture_element(name, desc)

    print("\n" + "=" * 50)
    print("All reference images captured!")
    print(f"Saved to: {REF_DIR}")


if __name__ == "__main__":
    main()
