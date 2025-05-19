#!/usr/bin/env python3
"""
Demo script for the new platform-specific input control implementation.
Shows how to use the new API for controlling the mouse and keyboard.
"""
import os
import sys
import time
import platform

# Add project root to path for importing
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

# Print some debug information
print(f"Python version: {sys.version}")
print(f"Path: {sys.path}")
print(f"Working directory: {os.getcwd()}")

def demo_using_convenience_import():
    """Demonstrate using the convenience import method."""
    print("\n=== Demo: Convenience Import ===")
    try:
        # First try to import from the input_control module
        try:
            from input_control import get_platform_handler
            handler = get_platform_handler()
            print(f"✓ Successfully imported handler via get_platform_handler()")
        except (ImportError, AttributeError) as e:
            print(f"! Error importing get_platform_handler: {e}")
            print("Trying alternative import...")
            # Alternative import
            from platform_uai.platform_utils import get_input_handler
            handler = get_input_handler()
            print(f"✓ Successfully imported handler via platform_utils.get_input_handler()")
            
        print(f"Handler class: {handler.__class__.__name__}")
        
        print("\nRunning demo sequence...")
    except Exception as e:
        print(f"✗ Error in convenience import demo: {e}")
        import traceback
        traceback.print_exc()
        print("Skipping this demo...")
    
    # Get screen size
    screen_width, screen_height = handler.get_screen_size()
    print(f"Screen size: {screen_width}x{screen_height}")
    
    # Get current mouse position
    x, y = handler.get_mouse_position()
    print(f"Current mouse position: ({x}, {y})")
    
    # Move mouse to center
    center_x, center_y = screen_width // 2, screen_height // 2
    print(f"Moving mouse to center: ({center_x}, {center_y})")
    handler.move_mouse(center_x, center_y, duration=0.5)
    
    # Move in a square pattern
    print("Moving in a square pattern...")
    size = 100  # Size of the square in pixels
    
    # Move to top-left corner of square
    handler.move_mouse(center_x - size//2, center_y - size//2, duration=0.3)
    time.sleep(0.2)
    
    # Move to top-right
    handler.move_mouse(center_x + size//2, center_y - size//2, duration=0.3)
    time.sleep(0.2)
    
    # Move to bottom-right
    handler.move_mouse(center_x + size//2, center_y + size//2, duration=0.3)
    time.sleep(0.2)
    
    # Move to bottom-left
    handler.move_mouse(center_x - size//2, center_y + size//2, duration=0.3)
    time.sleep(0.2)
    
    # Move back to top-left to complete the square
    handler.move_mouse(center_x - size//2, center_y - size//2, duration=0.3)
    
    # Return to center
    handler.move_mouse(center_x, center_y, duration=0.3)
    
    print("\n✅ Demo completed!")

def demo_using_direct_import():
    """Demonstrate using direct imports for platform-specific handlers."""
    print("\n=== Demo: Direct Platform-Specific Import ===")
    try:
        import platform
        
        system = platform.system().lower()
        print(f"Detected platform: {system}")
        
        # Use a try-except block for each platform to handle import errors gracefully
        try:
            if system == 'darwin':
                try:
                    from platform_uai.mac.input_control import MacInputHandler
                    handler = MacInputHandler()
                    print("✓ Using MacInputHandler")
                except ImportError as e:
                    print(f"✗ Error importing MacInputHandler: {e}")
                    print("Falling back to common handler...")
                    from platform_uai.common.input_control import MouseKeyboardHandler
                    handler = MouseKeyboardHandler()
                    print("✓ Using fallback MouseKeyboardHandler")
            elif system == 'windows':
                try:
                    from platform_uai.windows.input_control import WindowsInputHandler
                    handler = WindowsInputHandler()
                    print("✓ Using WindowsInputHandler")
                except ImportError as e:
                    print(f"✗ Error importing WindowsInputHandler: {e}")
                    print("Falling back to common handler...")
                    from platform_uai.common.input_control import MouseKeyboardHandler
                    handler = MouseKeyboardHandler()
                    print("✓ Using fallback MouseKeyboardHandler")
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
                    try:
                        from platform_uai.jetson.input_control import JetsonInputHandler
                        handler = JetsonInputHandler()
                        print("✓ Using JetsonInputHandler")
                    except ImportError as e:
                        print(f"✗ Error importing JetsonInputHandler: {e}")
                        print("Falling back to common handler...")
                        from platform_uai.common.input_control import MouseKeyboardHandler
                        handler = MouseKeyboardHandler()
                        print("✓ Using fallback MouseKeyboardHandler")
                else:
                    try:
                        from platform_uai.ubuntu.input_control import UbuntuInputHandler
                        handler = UbuntuInputHandler()
                        print("✓ Using UbuntuInputHandler")
                    except ImportError as e:
                        print(f"✗ Error importing UbuntuInputHandler: {e}")
                        print("Falling back to common handler...")
                        from platform_uai.common.input_control import MouseKeyboardHandler
                        handler = MouseKeyboardHandler()
                        print("✓ Using fallback MouseKeyboardHandler")
            else:
                print(f"! Unsupported platform: {system}")
                print("Falling back to common handler...")
                from platform_uai.common.input_control import MouseKeyboardHandler
                handler = MouseKeyboardHandler()
                print("✓ Using fallback MouseKeyboardHandler")
        except Exception as e:
            print(f"✗ Error in platform-specific handler: {e}")
            return
    except Exception as e:
        print(f"✗ Error in direct import demo: {e}")
        import traceback
        traceback.print_exc()
        print("Skipping this demo...")
        return
    
    print("\nRunning demo sequence...")
    
    # Perform a simple movement
    x, y = handler.get_mouse_position()
    print(f"Current position: ({x}, {y})")
    
    # Move 100 pixels right
    print(f"Moving 100 pixels right")
    handler.move_mouse(x + 100, y, duration=0.5)
    
    # Move 100 pixels down
    print(f"Moving 100 pixels down")
    handler.move_mouse(x + 100, y + 100, duration=0.5)
    
    # Return to original position
    print(f"Returning to original position")
    handler.move_mouse(x, y, duration=0.5)
    
    print("\n✅ Demo completed!")

def demo_simulation_mode():
    """Demonstrate simulation mode."""
    print("\n=== Demo: Simulation Mode ===")
    try:
        # Save original display setting
        original_display = os.environ.get('DISPLAY')
        
        # Force simulation mode by setting DISPLAY to empty
        os.environ['DISPLAY'] = ''
        print("Forced simulation mode by setting DISPLAY=''")
        
        try:
            # Import handler
            from platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler
            handler = MouseKeyboardHandler()
            
            if hasattr(handler, '_simulate_only'):
                print(f"Simulation mode active: {handler._simulate_only}")
            else:
                print("Handler doesn't have _simulate_only attribute, but should be in simulation mode")
            
            # Run some simulated operations
            print("\nRunning simulated operations...")
            
            print("- Moving mouse to (500, 500)")
            handler.move_mouse(500, 500)
            
            print("- Clicking at current position")
            try:
                # Try the new method name first
                handler.click_mouse()
            except AttributeError:
                # Fall back to the old method name if needed
                try:
                    handler.click()
                except AttributeError:
                    print("! Neither click_mouse() nor click() method found")
            
            print("- Typing text")
            handler.type_text("This is simulated typing")
            
            print("- Pressing hotkey")
            try:
                # Try hotkey method
                handler.hotkey('ctrl', 'c')
            except AttributeError:
                # Alternative: press keys individually
                print("[SIMULATION] Pressing hotkey ctrl+c")
                try:
                    handler.press_key('ctrl')
                    handler.press_key('c')
                except:
                    print("[SIMULATION] Hotkey simulation not fully supported")
        except ImportError as e:
            print(f"! Error importing MouseKeyboardHandler: {e}")
            print("Trying alternative import...")
            from platform_uai.platform_utils import get_input_handler
            handler = get_input_handler()
            print(f"Using {handler.__class__.__name__} in simulation mode")
            
            # Run basic operations with this handler
            print("\nRunning basic simulated operations...")
            handler.move_mouse(300, 300)
            handler.press_key('a')
        
        # Restore original display setting
        if original_display is None:
            if 'DISPLAY' in os.environ:
                del os.environ['DISPLAY']
        else:
            os.environ['DISPLAY'] = original_display
    
    except Exception as e:
        print(f"✗ Error in simulation mode demo: {e}")
        import traceback
        traceback.print_exc()
        print("Simulation demo failed")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    print("UaiBot Input Control Demo")
    print("------------------------")
    print(f"Running on: {platform.system()} {platform.release()}")
    
    # Check if we should force simulation mode
    if len(sys.argv) > 1 and sys.argv[1] == "--simulate":
        print("Running in simulation mode only")
        demo_simulation_mode()
    else:
        # Run all demos
        demo_using_convenience_import()
        demo_using_direct_import()
        demo_simulation_mode()
    
    print("\nAll demos completed!")
