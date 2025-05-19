#!/usr/bin/env python3
"""
Demo script for UaiBot's mouse and keyboard control functionality.

This script demonstrates how to use the MouseKeyboardHandler class to
control mouse and keyboard programmatically for automation tasks.

For more examples, see:
- examples/pyautogui_basic_example.py - Basic PyAutoGUI example from enhancement document
- examples/mouse_keyboard_example.py - More comprehensive example with all features

Reference: /reference/enhance_knm.txt
"""
import os
import sys
import time
import argparse

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.append(project_root)

# Import the mouse and keyboard handler
from input_control.mouse_keyboard_handler import MouseKeyboardHandler

# Import the output formatter for nice output
try:
    from utils.basic_output_formatter import BasicOutputFormatter
    formatter = BasicOutputFormatter()
except ImportError:
    # Fallback if formatter not available
    class SimpleFormatter:
        def format_header(self, text, _=None): return f"\n--- {text} ---\n"
        def format_status(self, msg, status="info"): return f"[{status}] {msg}"
    formatter = SimpleFormatter()

def demo_mouse_movement(handler, pause=1.0):
    """Demonstrate mouse movement functions."""
    print(formatter.format_header("Mouse Movement Demo", "computer"))
    
    # Get screen size and current position
    screen_width, screen_height = handler.get_screen_size()
    start_x, start_y = handler.get_mouse_position()
    print(f"Screen size: {screen_width}x{screen_height}")
    print(f"Starting mouse position: ({start_x}, {start_y})")
    
    # Move to corners
    corners = [
        (100, 100, "top-left"),
        (screen_width - 100, 100, "top-right"),
        (screen_width - 100, screen_height - 100, "bottom-right"),
        (100, screen_height - 100, "bottom-left")
    ]
    
    for x, y, name in corners:
        print(f"\nMoving mouse to {name} corner ({x}, {y})...")
        handler.move_mouse(x, y)
        time.sleep(pause)
    
    # Return to center
    center_x, center_y = screen_width // 2, screen_height // 2
    print(f"\nReturning to center ({center_x}, {center_y})...")
    handler.move_mouse(center_x, center_y)
    time.sleep(pause)
    
    # Return to starting position
    print(f"\nReturning to start position ({start_x}, {start_y})...")
    handler.move_mouse(start_x, start_y)
    
    print(formatter.format_status("Mouse movement demo completed", "success"))

def demo_mouse_clicks(handler, pause=1.0):
    """Demonstrate mouse click functions."""
    print(formatter.format_header("Mouse Clicking Demo", "computer"))
    
    # Get current position
    start_x, start_y = handler.get_mouse_position()
    
    # Center of screen
    screen_width, screen_height = handler.get_screen_size()
    center_x, center_y = screen_width // 2, screen_height // 2
    
    # Move to center
    print("Moving to center of screen...")
    handler.move_mouse(center_x, center_y)
    time.sleep(pause)
    
    # Left click
    print("Performing left click...")
    handler.click()
    time.sleep(pause)
    
    # Double click
    print("Performing double click...")
    handler.double_click()
    time.sleep(pause)
    
    # Right click
    print("Performing right click...")
    handler.right_click()
    time.sleep(pause)
    
    # Return to starting position
    print(f"Returning to start position ({start_x}, {start_y})...")
    handler.move_mouse(start_x, start_y)
    
    print(formatter.format_status("Mouse clicking demo completed", "success"))

def demo_keyboard_input(handler, pause=1.0):
    """Demonstrate keyboard input functions."""
    print(formatter.format_header("Keyboard Input Demo", "computer"))
    
    # Type text with delay between characters
    print("Typing text with delay...")
    handler.type_text("Hello from UaiBot!", interval=0.1)
    time.sleep(pause)
    
    # Press individual keys
    print("Pressing Enter key...")
    handler.press_key('enter')
    time.sleep(pause)
    
    # Press a sequence of keys
    print("Pressing a sequence of arrow keys...")
    handler.press_keys(['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right'])
    time.sleep(pause)
    
    # Use hotkey
    print("Pressing Ctrl+A hotkey...")
    handler.hotkey('ctrl', 'a')
    time.sleep(pause)
    
    # Delete the selected text
    print("Pressing Delete key...")
    handler.press_key('delete')
    
    print(formatter.format_status("Keyboard input demo completed", "success"))

def demo_advanced_functions(handler, pause=1.0):
    """Demonstrate advanced functions."""
    print(formatter.format_header("Advanced Functions Demo", "computer"))
    
    # Take screenshot
    print("Taking screenshot...")
    screenshot_path = os.path.join(project_root, "screenshot.png")
    
    if handler.screenshot(filename=screenshot_path):
        print(f"Screenshot saved to: {screenshot_path}")
    else:
        print("Failed to take screenshot")
    
    time.sleep(pause)
    
    # Demonstrate drag operation
    screen_width, screen_height = handler.get_screen_size()
    start_x, start_y = screen_width // 4, screen_height // 2
    end_x, end_y = (screen_width * 3) // 4, screen_height // 2
    
    print(f"Performing drag from ({start_x}, {start_y}) to ({end_x}, {end_y})...")
    handler.drag(start_x, start_y, end_x, end_y)
    
    print(formatter.format_status("Advanced functions demo completed", "success"))

def main():
    """Main function to run the demonstration."""
    parser = argparse.ArgumentParser(description='UaiBot Mouse and Keyboard Control Demo')
    parser.add_argument('--pause', type=float, default=1.0,
                       help='Pause duration between actions')
    parser.add_argument('--demos', type=str, default='all',
                       help='Demos to run (comma-separated): mouse,clicks,keyboard,advanced,all')
    args = parser.parse_args()
    
    # Create the handler
    handler = MouseKeyboardHandler()
    
    if not handler.pyautogui_available:
        print(formatter.format_status("PyAutoGUI is not available. Please install it with: pip install pyautogui", "error"))
        return
    
    # Show intro
    print(formatter.format_header("UaiBot Mouse and Keyboard Control Demo", "robot"))
    print("This demo will control your mouse and keyboard.")
    print("Make sure you have a way to interrupt the script if needed.")
    print("Move your mouse to a corner of the screen to abort.")
    print("\nStarting demos in 3 seconds...")
    time.sleep(3)
    
    # Determine which demos to run
    demos = args.demos.lower().split(',')
    run_all = 'all' in demos
    
    try:
        # Run selected demos
        if run_all or 'mouse' in demos:
            demo_mouse_movement(handler, args.pause)
            
        if run_all or 'clicks' in demos:
            demo_mouse_clicks(handler, args.pause)
            
        if run_all or 'keyboard' in demos:
            demo_keyboard_input(handler, args.pause)
            
        if run_all or 'advanced' in demos:
            demo_advanced_functions(handler, args.pause)
        
        # Completion message
        print("\n" + formatter.format_status("All demonstrations completed successfully!", "success"))
        print("You can control mouse and keyboard in your own scripts using the MouseKeyboardHandler class.")
        print("For more information, see the documentation in /reference/enhance_knm.txt")
        print("\nFor simpler examples, check out these files in the examples directory:")
        print("- pyautogui_basic_example.py - Basic PyAutoGUI example from enhancement document")
        print("- mouse_keyboard_example.py - More comprehensive example with all features")
        
    except Exception as e:
        print("\n" + formatter.format_status(f"Demo interrupted: {e}", "error"))
        
    except KeyboardInterrupt:
        print("\n" + formatter.format_status("Demo interrupted by user", "warning"))

if __name__ == "__main__":
    main()
