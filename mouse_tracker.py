import pyautogui
import time

LOG_FILE = "mouse_positions.txt"

print("Mouse Position Tracker")
print("=" * 40)
print("Move your mouse to each element.")
print("Positions are logged every second.")
print(f"Logging to: {LOG_FILE}")
print("Press Ctrl+C to stop.\n")

with open(LOG_FILE, "w") as f:
    try:
        while True:
            pos = pyautogui.position()
            line = f"x={pos.x}, y={pos.y}"
            print(f"\r{line}     ", end="", flush=True)
            f.write(line + "\n")
            f.flush()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nDone!")
