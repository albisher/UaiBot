#!/usr/bin/env python3
"""
Browser Search Demo for UaiBot
Demonstrates mouse and keyboard interaction to open a browser and perform a search using vision-based detection.
Now also takes a silent screenshot for reference and uses a reduced wait time.
"""
import os
import sys
import time
import subprocess
from .pathlib import Path

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

# Use only PyAutoGUI for automation
try:
    import pyautogui
except ImportError:
    print("PyAutoGUI is required. Please install it with: pip install pyautogui")
    sys.exit(1)

SCREENSHOT_PATH = os.path.join(current_dir, "screen_capture.png")

def open_browser():
    """Open the system default browser using xdg-open."""
    try:
        subprocess.run(['xdg-open', 'https://www.google.com'], check=True)
        time.sleep(1)  # Shorter wait for browser to start
        return True
    except Exception as e:
        print(f"Error opening browser: {e}")
        return False

def demo_browser_search():
    """Demonstrate browser interaction using vision-based search bar detection and silent screenshot."""
    print("\n=== Browser Search Demo ===")
    print("This demo will:")
    print("1. Open a new browser window")
    print("2. Navigate to Google")
    print("3. Take a silent screenshot of the screen")
    print("4. Search for 'Kuwait' using vision-based detection")

    # 1. Open browser
    print("\nOpening browser...")
    if not open_browser():
        print("Failed to open browser. Exiting demo.")
        return

    # 2. Wait for page to load (reduced time)
    print("Waiting for browser and Google to load...")
    time.sleep(2)

    # 3. Take a silent screenshot
    print(f"Taking a silent screenshot and saving as {SCREENSHOT_PATH} ...")
    pyautogui.screenshot(SCREENSHOT_PATH)
    print("Screenshot taken.")

    # 4. Use the screenshot as the reference image for vision-based detection
    print("Locating the Google search bar on screen using the screenshot...")
    location = pyautogui.locateOnScreen(SCREENSHOT_PATH, confidence=0.8)
    if location is None:
        print("[ERROR] Could not find the search bar on the screen using the screenshot.")
        print("Make sure the browser is visible and the search bar is present.")
        return

    center = pyautogui.center(location)
    print(f"Found search bar at: {center}")

    # 5. Move mouse and click the search bar
    pyautogui.moveTo(center.x, center.y, duration=0.3)
    pyautogui.click()
    time.sleep(0.2)

    # 6. Type search term and press Enter
    print("Typing 'Kuwait' and pressing Enter...")
    pyautogui.write("Kuwait", interval=0.08)
    pyautogui.press('enter')

    print("\nDemo completed successfully!")

if __name__ == "__main__":
    demo_browser_search() 