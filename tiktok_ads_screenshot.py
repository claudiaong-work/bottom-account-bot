import sys
import subprocess
import time
import pyautogui

pyautogui.FAILSAFE = True

ADS_URL = "https://seller-id.tokopedia.com/ads-creation/dashboard"

TIKTOK_PROFILES = {
    "IDL-M": "Profile 11",
    "TAK-M": "Profile 9",
}

PAGE_LOAD_WAIT = 6


def activate_chrome():
    subprocess.run(
        ["osascript", "-e", 'tell application "Google Chrome" to activate'],
        check=False,
    )
    time.sleep(0.3)


def navigate_current_tab(url):
    """Assumes the target brand's Chrome window is currently focused."""
    activate_chrome()
    pyautogui.hotkey("command", "l")
    time.sleep(0.3)
    pyautogui.typewrite(url, interval=0.01)
    pyautogui.press("enter")


def next_chrome_window():
    """Cycle to the next Chrome window (Cmd+`)."""
    activate_chrome()
    pyautogui.hotkey("command", "`")
    time.sleep(0.5)


def process_brand(brand):
    print(f"\n=== {brand} ===")
    print(f"  Navigating current window to ads dashboard...")
    navigate_current_tab(ADS_URL)
    print(f"  Waiting {PAGE_LOAD_WAIT}s for page load...")
    time.sleep(PAGE_LOAD_WAIT)
    # TODO: scroll to chart, toggle metrics, screenshot
    print(f"  (Screenshot step will go here)")


def main():
    if len(sys.argv) < 2:
        brands = list(TIKTOK_PROFILES.keys())
    else:
        brands = [b.strip().upper() for b in sys.argv[1:]]

    print("TikTok Ads Screenshot Bot")
    print(f"Brands: {', '.join(brands)}")
    print("=" * 40)
    print("SETUP:")
    print(f"  - Make sure each brand's Chrome profile window is open ({len(brands)} windows total).")
    print(f"  - Focus the window for the FIRST brand ({brands[0]}) before running.")
    print("=" * 40)
    time.sleep(2)

    for i, b in enumerate(brands):
        process_brand(b)
        if i < len(brands) - 1:
            print(f"  Switching to next Chrome window (Cmd+`)...")
            next_chrome_window()

    print("\nDone!")


if __name__ == "__main__":
    main()
