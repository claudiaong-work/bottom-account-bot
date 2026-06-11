"""Recalibrate the other two Pilih Toko coords on the same page:
  SEARCH_BOX        - the 'Cari' search input
  FIRST_DETAIL_LINK - the first 'Detail' link in the results table

Live-browser calibration only. Uses osascript dialogs + 5s hover delay.
Run right after _calibrate_nama_toko.py while the browser is still set up.
"""
import time
import subprocess
import pyautogui


def dialog(msg):
    subprocess.run([
        "osascript", "-e",
        f'display dialog "{msg}" with title "Calibrate Pilih Toko" '
        f'buttons {{"OK"}} default button "OK"'
    ])


def main():
    dialog(
        "STEP 1 of 2.\\n\\n"
        "On the 'Pilih Toko' page, click OK then hover over the CENTER of the "
        "'Cari' search input box and HOLD. You have 5 seconds."
    )
    time.sleep(5)
    p1 = pyautogui.position()
    print(f"SEARCH_BOX = ({p1.x}, {p1.y})")

    dialog(
        "STEP 2 of 2.\\n\\n"
        "Now SEARCH for any store you hold so a result row with a blue 'Detail' "
        "link appears.\\n\\n"
        "Then click OK and hover over the FIRST 'Detail' link and HOLD. "
        "You have 5 seconds."
    )
    time.sleep(5)
    p2 = pyautogui.position()
    print(f"FIRST_DETAIL_LINK = ({p2.x}, {p2.y})")

    print("\n=== Paste into shopee_ads_screenshot.py ===")
    print(f"SEARCH_BOX = ({p1.x}, {p1.y})")
    print(f"FIRST_DETAIL_LINK = ({p2.x}, {p2.y})")

    dialog(
        f"Recorded:\\n\\n"
        f"SEARCH_BOX = ({p1.x}, {p1.y})\\n"
        f"FIRST_DETAIL_LINK = ({p2.x}, {p2.y})\\n\\n"
        f"Tell Claude these numbers (also printed in the terminal)."
    )


if __name__ == "__main__":
    main()
