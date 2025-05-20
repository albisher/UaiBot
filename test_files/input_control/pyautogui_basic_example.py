#!/usr/bin/env python3
"""
PyAutoGUI Basic Example

This script demonstrates the exact code shown in the enhancement document
for controlling mouse and keyboard with PyAutoGUI.
"""
import time

print("PyAutoGUI Basic Example")
print("======================")

# Check if PyAutoGUI is installed
try:
    import pyautogui
    print("✅ PyAutoGUI is installed")
except ImportError:
    print("❌ PyAutoGUI is not installed. Please install with:")
    print("   pip install pyautogui")
    exit(1)

# Basic safety check - give user time to abort
print("\nThis script will control your mouse and keyboard.")
print("Move your mouse to a corner of the screen to abort.")
print("Starting in 5 seconds...")

for i in range(5, 0, -1):
    print(f"{i}...")
    time.sleep(1)

print("\nRunning example from enhancement document...")

# EXAMPLE CODE FROM ENHANCEMENT DOCUMENT
# -------------------------------------

# Move the mouse to coordinates (100, 150)
print("Moving mouse to coordinates (100, 150)")
pyautogui.moveTo(100, 150)
time.sleep(1)

# Click the mouse at the current position
print("Clicking at current position")
pyautogui.click()
time.sleep(1)

# Type text with a short interval between each character
print("Typing text with delay")
pyautogui.write('Hello, world!', interval=0.25)
time.sleep(1)

# Press the 'esc' key
print("Pressing ESC key")
pyautogui.press('esc')
time.sleep(1)

# Hold down the shift key and press the left arrow four times
print("Holding SHIFT and pressing left arrow four times")
with pyautogui.hold('shift'):
    pyautogui.press(['left', 'left', 'left', 'left'])
time.sleep(1)

# Press a hotkey combination (Ctrl+C)
print("Pressing Ctrl+C hotkey")
pyautogui.hotkey('ctrl', 'c')
time.sleep(1)

print("\nExample completed successfully!")
print("For more information, see the PyAutoGUI documentation at:")
print("https://pyautogui.readthedocs.io")
