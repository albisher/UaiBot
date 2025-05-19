#!/usr/bin/env python3
"""
Basic simulation mode test for mouse and keyboard handling.
This ensures that the handler works even without a display.
"""
import os
import sys
import time
import traceback

# Force simulation mode
os.environ['DISPLAY'] = ''

# Get project root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

# Try importing the handler
try:
    from input_control.mouse_keyboard_handler import MouseKeyboardHandler
    print("Successfully imported MouseKeyboardHandler")
except Exception as e:
    print(f"Error importing MouseKeyboardHandler: {e}")
    traceback.print_exc()
    sys.exit(1)

# Create handler instance
try:
    print("Creating MouseKeyboardHandler instance...")
    handler = MouseKeyboardHandler()
    print(f"Handler created. Simulation mode: {handler._simulate_only}")
    
    # Basic mouse operations
    print("\nTesting basic mouse operations...")
    handler.move_mouse(100, 100)
    handler.click()
    handler.right_click()
    
    # Basic keyboard operations
    print("\nTesting basic keyboard operations...")
    handler.type_text("Hello world")
    handler.press_key('enter')
    
    print("\nTest completed successfully!")
    
except Exception as e:
    print(f"Error during test: {e}")
    traceback.print_exc()
    sys.exit(1)
