"""Recalibrate the 3 date filter coords using osascript dialogs.
Assumes you're already on the Iklan Shopee page with Performa visible."""
import subprocess
import time
import pyautogui

steps = [
    ("DATE_FILTER_DROPDOWN", "the date filter dropdown (e.g. '1 Bulan Terakhir (GMT+7)')", False),
    ("FILTER_1BULAN", "'1 bulan terakhir' option (the dropdown will be opened for you)", True),
    ("FILTER_3BULAN", "'3 bulan terakhir' option (the dropdown will be re-opened)", True),
]

results = {}
for name, desc, needs_dropdown_open in steps:
    if needs_dropdown_open and "DATE_FILTER_DROPDOWN" in results:
        x, y = results["DATE_FILTER_DROPDOWN"]
        pyautogui.click(x, y)
        time.sleep(1.5)
    subprocess.run([
        "osascript", "-e",
        f'display dialog "Click OK then hover {desc} within 5 seconds." with title "Calibrate Date Filter" buttons {{"OK"}} default button "OK"'
    ])
    time.sleep(5)
    pos = pyautogui.position()
    results[name] = (pos.x, pos.y)
    print(f"  {name} = ({pos.x}, {pos.y})")

print("\n=== Paste into shopee_ads_screenshot.py ===")
for name, (x, y) in results.items():
    print(f"{name} = ({x}, {y})")
