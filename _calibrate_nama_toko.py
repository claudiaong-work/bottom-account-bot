"""Recalibrate the two Pilih Toko search-filter coords:
  NAMA_TOKO_DROPDOWN  - the 'Nama Toko' filter dropdown
  USERNAME_TOKO_OPTION - the 'Username Toko' item inside the opened dropdown

Live-browser calibration only. Bring the Shopee 'Pilih Toko' page to the FRONT
before each hover. Uses osascript dialogs + 5s hover delay (no input(), since the
script runs without a TTY). Prints the new constants to paste into
shopee_ads_screenshot.py.
"""
import time
import subprocess
import pyautogui


def dialog(msg):
    subprocess.run([
        "osascript", "-e",
        f'display dialog "{msg}" with title "Calibrate Nama Toko" '
        f'buttons {{"OK"}} default button "OK"'
    ])


def main():
    dialog(
        "STEP 1 of 2.\\n\\n"
        "Bring the Shopee browser to the FRONT and make sure you are on the "
        "'Pilih Toko' page.\\n\\n"
        "Click OK, then move your mouse to the CENTER of the 'Nama Toko' "
        "dropdown and HOLD it there. You have 5 seconds."
    )
    time.sleep(5)
    p1 = pyautogui.position()
    print(f"NAMA_TOKO_DROPDOWN = ({p1.x}, {p1.y})")

    dialog(
        "STEP 2 of 2.\\n\\n"
        "Now CLICK the 'Nama Toko' dropdown so the 'Username Toko' option is "
        "visible.\\n\\n"
        "Then click OK, move your mouse over the 'Username Toko' option and "
        "HOLD it there. You have 5 seconds."
    )
    time.sleep(5)
    p2 = pyautogui.position()
    print(f"USERNAME_TOKO_OPTION = ({p2.x}, {p2.y})")

    print("\n=== Paste into shopee_ads_screenshot.py ===")
    print(f"NAMA_TOKO_DROPDOWN = ({p1.x}, {p1.y})")
    print(f"USERNAME_TOKO_OPTION = ({p2.x}, {p2.y})")

    dialog(
        f"Recorded:\\n\\n"
        f"NAMA_TOKO_DROPDOWN = ({p1.x}, {p1.y})\\n"
        f"USERNAME_TOKO_OPTION = ({p2.x}, {p2.y})\\n\\n"
        f"Tell Claude these numbers (they are also printed in the terminal)."
    )


if __name__ == "__main__":
    main()
