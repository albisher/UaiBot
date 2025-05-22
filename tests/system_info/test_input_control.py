#!/usr/bin/env python3
"""
Test for the new platform-specific input control implementation.
"""
import os
import sys
import time
import platform

# Add project root to path for importing
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

def test_platform_manager():
    """Test the platform manager approach to get the input handler."""
    print("\n=== Testing Platform Manager ===")
    try:
        from app.platform_uai.platform_manager import PlatformManager
        
        print("Creating platform manager...")
        manager = PlatformManager()
        
        print("Initializing platform components...")
        manager.initialize()
        
        print(f"Platform name: {manager.platform_name}")
        print(f"Input handler available: {manager.input_handler is not None}")
        
        if manager.input_handler:
            print("\nInput handler information:")
            handler = manager.input_handler
            print(f"Handler class: {handler.__class__.__name__}")
            
            # Check if we're in simulation mode
            if hasattr(handler, '_simulate_only'):
                print(f"Simulation mode: {handler._simulate_only}")
            
            # Test basic functionality
            print("\nTesting basic functionality:")
            print("- Getting screen size...")
            screen_size = handler.get_screen_size()
            print(f"  Screen size: {screen_size}")
            
            print("- Getting mouse position...")
            mouse_pos = handler.get_mouse_position()
            print(f"  Mouse position: {mouse_pos}")
            
            print("- Moving mouse to (100, 100)...")
            handler.move_mouse(100, 100)
            time.sleep(1)
            
            print("- Moving mouse to (200, 200)...")
            handler.move_mouse(200, 200)
            time.sleep(1)
            
            print("- Clicking...")
            handler.click_mouse()
            
            print("\n✅ Platform manager tests completed!")
        else:
            print("❌ Input handler not available from platform manager")
    
    except Exception as e:
        print(f"❌ Error in platform manager test: {e}")
        import traceback
        traceback.print_exc()

def test_direct_import():
    """Test direct import of the platform-specific handler."""
    print("\n=== Testing Direct Import ===")
    try:
        # Try to detect platform
        system = platform.system().lower()
        
        if system == 'darwin':
            from app.platform_uai.mac.input_control import MacInputHandler
            handler = MacInputHandler()
            print("✅ Successfully imported MacInputHandler")
        elif system == 'windows':
            from app.platform_uai.windows.input_control import WindowsInputHandler
            handler = WindowsInputHandler()
            print("✅ Successfully imported WindowsInputHandler")
        elif system == 'linux':
            # Check for Jetson
            is_jetson = False
            try:
                with open('/proc/device-tree/model', 'r') as f:
                    if 'jetson' in f.read().lower():
                        is_jetson = True
            except:
                pass
                
            if is_jetson:
                from app.platform_uai.jetson.input_control import JetsonInputHandler
                handler = JetsonInputHandler()
                print("✅ Successfully imported JetsonInputHandler")
            else:
                from app.platform_uai.ubuntu.input_control import UbuntuInputHandler
                handler = UbuntuInputHandler()
                print("✅ Successfully imported UbuntuInputHandler")
        else:
            print(f"❌ Unsupported platform: {system}")
            return
            
        # Test basic functionality
        print("\nTesting basic functionality:")
        print("- Getting screen size...")
        screen_size = handler.get_screen_size()
        print(f"  Screen size: {screen_size}")
        
        print("- Getting mouse position...")
        mouse_pos = handler.get_mouse_position()
        print(f"  Mouse position: {mouse_pos}")
        
        print("- Moving mouse to (150, 150)...")
        handler.move_mouse(150, 150)
        time.sleep(1)
        
        print("- Moving mouse to (250, 250)...")
        handler.move_mouse(250, 250)
        time.sleep(1)
        
        print("- Clicking...")
        handler.click_mouse()
        
        print("\n✅ Direct import tests completed!")
        
    except Exception as e:
        print(f"❌ Error in direct import test: {e}")
        import traceback
        traceback.print_exc()

def test_compatibility_layer():
    """Test the compatibility layer."""
    print("\n=== Testing Compatibility Layer ===")
    try:
        from input_control.mouse_keyboard_handler import MouseKeyboardHandler
        
        print("Creating handler instance...")
        handler = MouseKeyboardHandler()
        print("✅ Handler created successfully")
        
        # Test basic functionality
        print("\nTesting basic functionality:")
        print("- Getting screen size...")
        screen_size = handler.get_screen_size()
        print(f"  Screen size: {screen_size}")
        
        print("- Getting mouse position...")
        mouse_pos = handler.get_mouse_position()
        print(f"  Mouse position: {mouse_pos}")
        
        print("- Moving mouse to (300, 300)...")
        handler.move_mouse(300, 300)
        time.sleep(1)
        
        print("- Moving mouse to (400, 400)...")
        handler.move_mouse(400, 400)
        time.sleep(1)
        
        print("- Clicking...")
        handler.click_mouse()
        
        print("\n✅ Compatibility layer tests completed!")
        
    except Exception as e:
        print(f"❌ Error in compatibility layer test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(f"Running on: {platform.system()} {platform.release()}")
    
    # Uncomment to force simulation mode for testing
    # os.environ['DISPLAY'] = ''
    # print("Forcing simulation mode (DISPLAY='')")
    
    # Run the tests
    test_platform_manager()
    test_direct_import()
    test_compatibility_layer()
    
    print("\nAll tests completed!")
