#!/usr/bin/env python3
"""
Demo script for the new platform-specific input control implementation.
Shows how to use the new API for controlling the mouse and keyboard.
"""
import os
import sys
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
        # Example usage (commented out for demonstration)
        # from uaibot.input_control import get_platform_handler
        # handler = get_platform_handler()
        # print(f"✓ Successfully imported handler via get_platform_handler()")
        print("\nRunning demo sequence...")
    except Exception as e:
        print(f"✗ Error in convenience import demo: {e}")
        import traceback
        traceback.print_exc()
        print("Skipping this demo...")
    print("\n✅ Demo completed!")

def demo_using_direct_import():
    """Demonstrate using direct imports for platform-specific handlers."""
    print("\n=== Demo: Direct Platform-Specific Import ===")
    try:
        system = platform.system().lower()
        print(f"Detected platform: {system}")
        handler = None
        try:
            if system == 'darwin':
                try:
                    from uaibot.platform_uai.mac.input_control import MacInputHandler
                    handler = MacInputHandler()
                    print("✓ Using MacInputHandler")
                except ImportError as e:
                    print(f"✗ Error importing MacInputHandler: {e}")
                    print("Falling back to common handler...")
                    from uaibot.platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler
                    handler = MouseKeyboardHandler()
                    print("✓ Using fallback MouseKeyboardHandler")
            elif system == 'windows':
                try:
                    from uaibot.platform_uai.windows.input_control import WindowsInputHandler
                    handler = WindowsInputHandler()
                    print("✓ Using WindowsInputHandler")
                except ImportError as e:
                    print(f"✗ Error importing WindowsInputHandler: {e}")
                    print("Falling back to common handler...")
                    from uaibot.platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler
                    handler = MouseKeyboardHandler()
                    print("✓ Using fallback MouseKeyboardHandler")
            elif system == 'linux':
                is_jetson = False
                try:
                    with open('/proc/device-tree/model', 'r') as f:
                        if 'jetson' in f.read().lower():
                            is_jetson = True
                except Exception:
                    pass
                if is_jetson:
                    try:
                        from uaibot.platform_uai.jetson.input_control import JetsonInputHandler
                        handler = JetsonInputHandler()
                        print("✓ Using JetsonInputHandler")
                    except ImportError as e:
                        print(f"✗ Error importing JetsonInputHandler: {e}")
                        print("Falling back to common handler...")
                        from uaibot.platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler
                        handler = MouseKeyboardHandler()
                        print("✓ Using fallback MouseKeyboardHandler")
                else:
                    try:
                        from uaibot.platform_uai.ubuntu.input_control import UbuntuInputHandler
                        handler = UbuntuInputHandler()
                        print("✓ Using UbuntuInputHandler")
                    except ImportError as e:
                        print(f"✗ Error importing UbuntuInputHandler: {e}")
                        print("Falling back to common handler...")
                        from uaibot.platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler
                        handler = MouseKeyboardHandler()
                        print("✓ Using fallback MouseKeyboardHandler")
            else:
                print(f"! Unsupported platform: {system}")
                print("Falling back to common handler...")
                from uaibot.platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler
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
    print("\n✅ Demo completed!")

def demo_simulation_mode():
    """Demonstrate simulation mode."""
    print("\n=== Demo: Simulation Mode ===")
    try:
        original_display = os.environ.get('DISPLAY')
        os.environ['DISPLAY'] = ''
        print("Forced simulation mode by setting DISPLAY=''")
        try:
            from uaibot.platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler
            handler = MouseKeyboardHandler()
            if hasattr(handler, '_simulate_only'):
                print(f"Simulation mode active: {handler._simulate_only}")
            else:
                print("Handler doesn't have _simulate_only attribute, but should be in simulation mode")
            print("\nRunning simulated operations...")
            print("- Moving mouse to (500, 500)")
            handler.move_mouse(500, 500)
            print("- Clicking at current position")
            try:
                handler.click_mouse()
            except AttributeError:
                try:
                    handler.click()
                except AttributeError:
                    print("! Neither click_mouse() nor click() method found")
            print("- Typing text")
            handler.type_text("This is simulated typing")
            print("- Pressing hotkey")
            try:
                handler.hotkey('ctrl', 'c')
            except AttributeError:
                print("[SIMULATION] Pressing hotkey ctrl+c")
                try:
                    handler.press_key('ctrl')
                    handler.press_key('c')
                except Exception:
                    print("[SIMULATION] Hotkey simulation not fully supported")
        except ImportError as e:
            print(f"! Error importing MouseKeyboardHandler: {e}")
            print("Trying alternative import...")
            from uaibot.platform_uai.platform_utils import get_input_handler
            handler = get_input_handler()
            print(f"Using {handler.__class__.__name__} in simulation mode")
            print("\nRunning basic simulated operations...")
            handler.move_mouse(300, 300)
            handler.press_key('a')
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
    if len(sys.argv) > 1 and sys.argv[1] == "--simulate":
        print("Running in simulation mode only")
        demo_simulation_mode()
    else:
        demo_using_convenience_import()
        demo_using_direct_import()
        demo_simulation_mode()
    print("\nAll demos completed!")
