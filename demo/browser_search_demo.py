#!/usr/bin/env python3
"""
Browser Search Demo for UaiBot
Demonstrates mouse and keyboard interaction to open a browser and perform a search.
"""
import os
import sys
import time
import subprocess

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

# Set display environment variables
os.environ['DISPLAY'] = ':0'
os.environ['XAUTHORITY'] = os.path.expanduser('~/.Xauthority')

from platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler

def open_browser():
    """Open the default browser using xdg-open."""
    try:
        # Try to open with xdg-open first
        subprocess.Popen(['xdg-open', 'https://www.google.com'])
    except Exception:
        try:
            # Fallback to google-chrome
            subprocess.Popen(['google-chrome', 'https://www.google.com'])
        except Exception:
            try:
                # Try firefox as last resort
                subprocess.Popen(['firefox', 'https://www.google.com'])
            except Exception as e:
                print(f"Error opening browser: {e}")
                return False
    time.sleep(2)  # Wait for browser to open
    return True

def demo_browser_search():
    """Demonstrate browser interaction using mouse and keyboard control."""
    print("\n=== Browser Search Demo ===")
    print("This demo will:")
    print("1. Open a new browser window")
    print("2. Navigate to Google")
    print("3. Search for 'Kuwait'")
    
    # Get user confirmation
    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("Demo skipped.")
        return
    
    # Initialize the input handler
    handler = MouseKeyboardHandler()
    
    try:
        # Get screen dimensions
        screen_width, screen_height = handler.get_screen_size()
        print(f"Screen size: {screen_width}x{screen_height}")
        
        # 1. Open browser using xdg-open
        print("\nOpening browser...")
        if not open_browser():
            print("Failed to open browser. Exiting demo.")
            return
        
        # 2. Wait for page to load and move to search bar
        print("Moving to search bar...")
        time.sleep(2)  # Wait for page to load
        
        # Move to search bar (approximate position)
        search_x = screen_width // 2
        search_y = screen_height // 4
        handler.move_mouse(search_x, search_y)
        handler.click()
        time.sleep(0.5)
        
        # 3. Type search term
        print("Searching for Kuwait...")
        handler.type_text("Kuwait")
        handler.press_key('enter')
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"\nError during demo: {str(e)}")
        print("Please make sure you have a browser installed and the screen is visible.")

if __name__ == "__main__":
    demo_browser_search() 