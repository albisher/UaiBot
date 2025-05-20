#!/usr/bin/env python3
"""
Mouse and Keyboard Control Example for UaiBot

This script demonstrates how to control the mouse and keyboard using PyAutoGUI
and other libraries based on the enhancement guidelines in enhance_knm.txt.
"""

import sys
import time
import platform

print("Mouse and Keyboard Control Example")
print("=================================")

# Check for required libraries
try:
    import pyautogui
    print("✅ PyAutoGUI is installed")
except ImportError:
    print("❌ PyAutoGUI is not installed. Install with: pip install pyautogui")
    sys.exit(1)

# Check for optional libraries
try:
    import keyboard
    keyboard_available = True
    print("✅ keyboard library is installed")
except ImportError:
    keyboard_available = False
    print("ℹ️ keyboard library is not installed (optional for advanced keyboard features)")
    print("  To install (Windows/Linux only): pip install keyboard")

try:
    import mouse
    mouse_available = True
    print("✅ mouse library is installed")
except ImportError:
    mouse_available = False
    print("ℹ️ mouse library is not installed (optional for advanced mouse features)")
    print("  To install: pip install mouse")

print("\nSystem Information:")
print(f"- Platform: {platform.system()}")
print(f"- Python Version: {platform.python_version()}")
print(f"- PyAutoGUI Version: {pyautogui.__version__}")

# Set safety features
print("\nConfiguring PyAutoGUI safety features...")
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1
print("- FAILSAFE is enabled (move mouse to corner of screen to abort)")
print("- Default PAUSE between actions: 0.1 seconds")

def demo_mouse_movement():
    """Demonstrate mouse movement functions."""
    print("\n=== Mouse Movement Demo ===")
    
    # Get screen size and current position
    screen_width, screen_height = pyautogui.size()
    start_x, start_y = pyautogui.position()
    print(f"Screen size: {screen_width}x{screen_height}")
    print(f"Starting mouse position: ({start_x}, {start_y})")
    
    # Warning and confirmation
    print("\nThis will move your mouse cursor.")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Mouse movement demo skipped.")
        return
    
    # Move the mouse to specific coordinates
    print(f"\nMoving mouse to position (100, 150)...")
    pyautogui.moveTo(100, 150, duration=0.5)
    time.sleep(1)
    
    # Return to starting position
    print(f"Returning to starting position ({start_x}, {start_y})...")
    pyautogui.moveTo(start_x, start_y, duration=0.5)
    
    print("Mouse movement demo completed.")

def demo_mouse_clicks():
    """Demonstrate mouse click functions."""
    print("\n=== Mouse Clicking Demo ===")
    
    # Warning and confirmation
    print("This will perform mouse clicks.")
    print("Please open a text editor or similar application to see the effects.")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Mouse clicking demo skipped.")
        return
    
    # Get current position
    start_x, start_y = pyautogui.position()
    
    # Left click
    print("Performing left click...")
    pyautogui.click()
    time.sleep(1)
    
    # Right click
    print("Performing right click...")
    pyautogui.rightClick()
    time.sleep(1)
    
    # Double click
    print("Performing double click...")
    pyautogui.doubleClick()
    time.sleep(1)
    
    print("Mouse clicking demo completed.")

def demo_keyboard_input():
    """Demonstrate keyboard input functions."""
    print("\n=== Keyboard Input Demo ===")
    
    # Warning and confirmation
    print("This will type text and simulate key presses.")
    print("Please open a text editor or similar application to see the effects.")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Keyboard input demo skipped.")
        return
    
    # Type text
    print("Typing text with delay...")
    pyautogui.write('Hello, world!', interval=0.25)
    time.sleep(1)
    
    # Press individual keys
    print("Pressing Enter key...")
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # Hold down keys and press others
    print("Holding shift and pressing left arrow keys...")
    with pyautogui.hold('shift'):
        pyautogui.press(['left', 'left', 'left', 'left'])
    time.sleep(0.5)
    
    # Hotkey combination
    print("Pressing Ctrl+C hotkey...")
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)
    
    print("Keyboard input demo completed.")

def demo_advanced_features():
    """Demonstrate advanced features of keyboard and mouse libraries."""
    print("\n=== Advanced Features Demo ===")
    
    # Skip if not available
    if not (keyboard_available or mouse_available):
        print("Advanced features demo skipped (keyboard or mouse libraries not available).")
        return
    
    # Warning and confirmation
    print("This will demonstrate advanced keyboard and mouse features.")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Advanced features demo skipped.")
        return
    
    # Keyboard event registration (if available)
    if keyboard_available:
        print("\nKeyboard hotkey registration demo:")
        print("Registering Ctrl+Alt+P hotkey for 5 seconds...")
        print("Try pressing Ctrl+Alt+P...")
        
        # Define callback
        def hotkey_callback():
            print("Hotkey detected! Ctrl+Alt+P was pressed.")
        
        # Register hotkey
        keyboard.add_hotkey('ctrl+alt+p', hotkey_callback)
        
        # Wait for 5 seconds
        time.sleep(5)
        
        # Unregister hotkey
        keyboard.remove_hotkey('ctrl+alt+p')
        print("Hotkey unregistered.")
    
    # Mouse event registration (if available)
    if mouse_available:
        print("\nMouse event registration demo:")
        print("Registering click event for 5 seconds...")
        print("Try clicking your mouse...")
        
        # Define callback
        def click_callback(x, y, button, pressed):
            if pressed:
                print(f"Mouse clicked at position ({x}, {y})")
        
        # Register event
        mouse.on_click(click_callback)
        
        # Wait for 5 seconds
        time.sleep(5)
        
        # Unregister event
        mouse.unhook_all()
        print("Mouse event unregistered.")
    
    print("Advanced features demo completed.")

def demo_screenshot():
    """Demonstrate screenshot capabilities."""
    print("\n=== Screenshot Demo ===")
    
    # Warning and confirmation
    print("This will take a screenshot.")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Screenshot demo skipped.")
        return
    
    # Take a screenshot
    print("Taking screenshot...")
    screenshot = pyautogui.screenshot()
    
    # Save the screenshot
    filename = 'uaibot_screenshot.png'
    screenshot.save(filename)
    print(f"Screenshot saved as {filename}")
    
    print("Screenshot demo completed.")

def main():
    """Main function to run all demos."""
    print("\nWelcome to the Mouse and Keyboard Control Demo!")
    print("This demo shows how to control the mouse and keyboard using Python.")
    print("It uses techniques described in the enhancement document.\n")
    
    while True:
        print("\nAvailable demos:")
        print("1. Mouse Movement")
        print("2. Mouse Clicks")
        print("3. Keyboard Input")
        print("4. Advanced Features")
        print("5. Screenshot")
        print("0. Exit")
        
        choice = input("\nSelect a demo (0-5): ")
        
        if choice == '1':
            demo_mouse_movement()
        elif choice == '2':
            demo_mouse_clicks()
        elif choice == '3':
            demo_keyboard_input()
        elif choice == '4':
            demo_advanced_features()
        elif choice == '5':
            demo_screenshot()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
    
    print("\nThank you for using the Mouse and Keyboard Control Demo!")
    print("For more information, see the documentation in 'enhance_knm.txt'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
