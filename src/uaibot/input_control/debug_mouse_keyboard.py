#!/usr/bin/env python3
"""
Debug test for mouse and keyboard handler showing detailed error output.
"""
import os
import sys
import traceback

# Set DISPLAY to empty to force simulation mode
# We need to check if PyAutoGUI is already imported before changing this
import sys
if 'pyautogui' not in sys.modules:
    print("Setting DISPLAY='' to force simulation mode")
    os.environ['DISPLAY'] = ''
else:
    print("WARNING: PyAutoGUI already imported, cannot force simulation mode")
    
# Print current DISPLAY value
print(f"DISPLAY environment variable: '{os.environ.get('DISPLAY', '')}'")
print(f"WAYLAND_DISPLAY environment variable: '{os.environ.get('WAYLAND_DISPLAY', '')}'")
print(f"Is headless environment: {not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY')}")

# Show current directory and Python path
print(f"Current directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

# Try to import the module with error display
try:
    # Add project root to path for importing
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../.."))
    print(f"Project root: {project_root}")
    sys.path.insert(0, project_root)
    
    print("\nTrying to import from compatibility layer...")
    from input_control.mouse_keyboard_handler import MouseKeyboardHandler as LegacyHandler
    print("✅ Successfully imported from compatibility layer")
    
    print("\nTrying to import from platform_uai...")
    from uaibot.platform_uai.platform_utils import get_input_handler
    handler = get_input_handler()
    print(f"✅ Successfully imported from platform_uai: {handler.__class__.__name__}")
    
    print("\nChecking module files...")
    import input_control.mouse_keyboard_handler as legacy_mkh
    import platform_uai.common.input_control.mouse_keyboard_handler as new_mkh
    print(f"Legacy module location: {legacy_mkh.__file__}")
    print(f"New module location: {new_mkh.__file__}")
    print(f"Module content exists: {os.path.exists(legacy_mkh.__file__)} (legacy)")
    print(f"Module content exists: {os.path.exists(new_mkh.__file__)} (new)")
    
    print("\nCreating handler instance from .legacy import...")
    legacy_handler = LegacyHandler()
    print(f"✅ Legacy handler created successfully")
    
    print("\nChecking handler from platform_utils...")
    platform_handler = handler  # From the import above
    print(f"✅ Platform handler: {type(platform_handler).__name__}")
    
    # Check attributes if they exist
    if hasattr(platform_handler, '_simulate_only'):
        print(f"   Simulation mode: {platform_handler._simulate_only}")
    if hasattr(platform_handler, 'pyautogui_available'):
        print(f"   PyAutoGUI available: {platform_handler.pyautogui_available}")
    if hasattr(platform_handler, 'keyboard_available'):
        print(f"   Keyboard available: {platform_handler.keyboard_available}")
    if hasattr(platform_handler, 'mouse_available'):
        print(f"   Mouse available: {platform_handler.mouse_available}")
    
    print("\nRunning simple tests using platform handler...")
    print("- Moving mouse...")
    platform_handler.move_mouse(100, 100)
    print("- Clicking...")
    platform_handler.click_mouse()
    print("- Typing text...")
    platform_handler.type_text("Hello world")
    
    print("\nRunning simple tests using legacy handler...")
    print("- Moving mouse...")
    legacy_handler.move_mouse(100, 100)
    print("- Clicking...")
    legacy_handler.click_mouse()
    print("- Typing text...")
    legacy_handler.type_text("Hello world")
    
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
