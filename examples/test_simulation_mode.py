#!/usr/bin/env python3
"""
Test for mouse and keyboard handler in simulation mode.
This script tests if the MouseKeyboardHandler class works correctly in simulation mode.
"""
import os
import sys
import time
import traceback

# Set empty display to force simulation mode
os.environ['DISPLAY'] = ''

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

# Import the handler class
try:
    from input_control.mouse_keyboard_handler import MouseKeyboardHandler
    print("Successfully imported MouseKeyboardHandler")
except ImportError as e:
    print(f"Error importing MouseKeyboardHandler: {e}")
    traceback.print_exc()
    sys.exit(1)

# Create handler instance
handler = MouseKeyboardHandler()

# Print initial status
print("\n=== Mouse Keyboard Handler Test (Simulation Mode) ===")
print(f"PyAutoGUI available: {handler.pyautogui_available}")
print(f"Keyboard library available: {handler.keyboard_available}")
print(f"Mouse library available: {handler.mouse_available}")
print(f"Simulation mode: {handler._simulate_only}")
print(f"Platform: {handler.platform}")

# Get screen size
width, height = handler.get_screen_size()
print(f"Screen size: {width}x{height}")

# Get mouse position
x, y = handler.get_mouse_position()
print(f"Mouse position: {x}, {y}")

# Test mouse movement
print("\n--- Testing Mouse Movement ---")
handler.move_mouse(100, 100)
print(f"New mouse position: {handler.get_mouse_position()}")

# Test click
print("\n--- Testing Mouse Clicks ---")
handler.click()
handler.click(200, 200, button='right')
handler.double_click(300, 300)

# Test keyboard input
print("\n--- Testing Keyboard Input ---")
handler.type_text("Hello from UaiBot!")
handler.press_key('enter')
handler.hotkey('ctrl', 'c')

# Test key holding pattern
print("\n--- Testing Key Hold Pattern ---")
with handler.hold_key('shift'):
    handler.press_keys(['left', 'left', 'left', 'left'])

print("\nTest completed successfully!")
