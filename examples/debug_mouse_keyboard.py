#!/usr/bin/env python3
"""
Debug test for mouse and keyboard handler showing detailed error output.
"""
import os
import sys
import traceback

# Set empty display for simulation mode
os.environ['DISPLAY'] = ''

# Show current directory and Python path
print(f"Current directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

# Try to import the module with error display
try:
    # Add project root to path for importing
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    print(f"Project root: {project_root}")
    sys.path.insert(0, project_root)
    
    print("\nTrying to import MouseKeyboardHandler...")
    from input_control.mouse_keyboard_handler import MouseKeyboardHandler
    print("✅ Successfully imported MouseKeyboardHandler")
    
    print("\nChecking module file...")
    import input_control.mouse_keyboard_handler as mkh
    print(f"Module location: {mkh.__file__}")
    print(f"Module content exists: {os.path.exists(mkh.__file__)}")
    
    print("\nCreating handler instance...")
    handler = MouseKeyboardHandler()
    print(f"✅ Handler created successfully")
    print(f"   Simulation mode: {handler._simulate_only}")
    print(f"   PyAutoGUI available: {handler.pyautogui_available}")
    print(f"   Keyboard available: {handler.keyboard_available}")
    print(f"   Mouse available: {handler.mouse_available}")
    
    print("\nRunning simple tests...")
    print("- Moving mouse...")
    handler.move_mouse(100, 100)
    print("- Clicking...")
    handler.click()
    print("- Typing text...")
    handler.type_text("Hello world")
    
    print("\n✅ All tests completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nDetailed traceback:")
    traceback.print_exc()
    
    print("\nChecking for input_control directory...")
    input_control_dir = os.path.join(project_root, "input_control")
    if os.path.exists(input_control_dir):
        print(f"✅ Directory exists: {input_control_dir}")
        print("Contents:")
        for item in os.listdir(input_control_dir):
            print(f"  - {item}")
    else:
        print(f"❌ Directory not found: {input_control_dir}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nDetailed traceback:")
    traceback.print_exc()
