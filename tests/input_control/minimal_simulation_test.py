#!/usr/bin/env python3
"""
Minimal simulation test for UaiBot's mouse and keyboard handler.

This test doesn't even try to import PyAutoGUI directly, but instead
works with our handler at a higher level. It's designed to work
even in environments where PyAutoGUI would normally fail.
"""
import os
import sys
import time

# Force simulation mode by setting empty DISPLAY
os.environ['DISPLAY'] = ''

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

def main():
    """Run the minimal test"""
    print("=== Minimal Simulation Mode Test ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print("DISPLAY=" + os.environ.get('DISPLAY', '(not set)'))
    
    # Create a minimal version of the handler
    # This doesn't even depend on X11 display
    class MinimalHandler:
        def __init__(self):
            self.mouse_position = (0, 0)
            self.screen_size = (1920, 1080)
            
        def move_mouse(self, x, y):
            print(f"[SIMULATION] Moving mouse to {x}, {y}")
            self.mouse_position = (x, y)
            return True
            
        def click(self, x=None, y=None, button='left'):
            if x is not None and y is not None:
                self.mouse_position = (x, y)
            print(f"[SIMULATION] Clicking {button} at {self.mouse_position}")
            return True
            
        def type_text(self, text):
            print(f"[SIMULATION] Typing: {text}")
            return True
            
    print("\nCreating minimal handler for tests...")
    minimal = MinimalHandler()
    
    # Test basic operations
    print("\n--- Testing with minimal handler ---")
    minimal.move_mouse(100, 200)
    minimal.click()
    minimal.click(300, 400, 'right')
    minimal.type_text("Hello world")
    
    # Now try to import the real handler safely
    try:
        print("\n--- Attempting to import real handler ---")
        from input_control.mouse_keyboard_handler import MouseKeyboardHandler
        print("✅ Successfully imported MouseKeyboardHandler")
        
        print("\nCreating MouseKeyboardHandler instance...")
        handler = MouseKeyboardHandler()
        print(f"✅ Handler created. Simulation mode: {handler._simulate_only}")
        
        # Verify we're in simulation mode
        if not handler._simulate_only:
            print("WARNING: Not in simulation mode! This shouldn't happen.")
        
        # Test basic operations
        print("\n--- Testing with real handler ---")
        handler.move_mouse(100, 200)
        handler.click()
        handler.click(300, 400, 'right')
        handler.type_text("Hello world")
        
        print("\n✅ All tests completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error with real handler: {e}")
        import traceback
        traceback.print_exc()
        print("\n✅ But minimal handler worked correctly!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
