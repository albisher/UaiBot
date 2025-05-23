#!/usr/bin/env python3
"""
Platform Support Test Script for UaiBot
Tests the platform detection, initialization, and handler loading
"""
import os
import sys
import platform

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Define colors for better terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{BOLD}{'=' * 80}")
    print(f"{text.center(80)}")
    print(f"{'=' * 80}{RESET}\n")

def print_subheader(text):
    print(f"\n{YELLOW}{BOLD}{text}{RESET}")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_failure(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"➤ {text}")

def test_platform_detection():
    print_subheader("Testing Platform Detection")
    
    try:
        from uaibot.platform_uai.platform_utils import detect_platform
        platform_name, platform_dir = detect_platform()
        
        if platform_name:
            print_success(f"Platform detected: {platform_name} (directory: {platform_dir})")
            return True
        else:
            print_failure(f"Platform detection failed for {platform.system()}")
            return False
    except Exception as e:
        print_failure(f"Error during platform detection: {e}")
        return False

def test_platform_manager():
    print_subheader("Testing Platform Manager")
    
    try:
        from uaibot.platform_uai.platform_manager import PlatformManager
        platform_manager = PlatformManager()
        
        if platform_manager.platform_supported:
            print_success(f"Platform supported: {platform_manager.platform_name}")
            
            # Get platform info
            platform_info = platform_manager.get_platform_info()
            print_info(f"Platform info: {platform_info}")
            
            # Initialize platform manager
            success = platform_manager.initialize()
            if success:
                print_success("Platform initialization successful")
            else:
                print_failure("Platform initialization failed")
                return False
                
            # Check handlers
            if platform_manager.audio_handler:
                print_success("Audio handler initialized")
            else:
                print_info("Audio handler not available")
                
            if platform_manager.usb_handler:
                print_success("USB handler initialized")
            else:
                print_info("USB handler not available")
                
            if platform_manager.input_handler:
                print_success("Input handler initialized")
            else:
                print_failure("Input handler not available")
                return False
                
            # Clean up
            platform_manager.cleanup()
            print_success("Platform cleanup successful")
            
            return True
        else:
            print_failure(f"Platform not supported: {platform.system()}")
            return False
    except Exception as e:
        print_failure(f"Error during platform manager testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_handlers_directly():
    print_subheader("Testing Handlers Directly")
    
    # Test audio handler
    try:
        from uaibot.platform_uai.platform_utils import get_audio_handler
        audio_handler = get_audio_handler()
        if audio_handler:
            print_success(f"Audio handler loaded: {type(audio_handler).__name__}")
        else:
            print_info("Audio handler not available")
    except Exception as e:
        print_info(f"Error loading audio handler: {e}")
        
    # Test USB handler
    try:
        from uaibot.platform_uai.platform_utils import get_usb_handler
        usb_handler = get_usb_handler()
        if usb_handler:
            print_success(f"USB handler loaded: {type(usb_handler).__name__}")
        else:
            print_info("USB handler not available")
    except Exception as e:
        print_info(f"Error loading USB handler: {e}")
        
    # Test input handler
    try:
        from uaibot.platform_uai.platform_utils import get_input_handler
        input_handler = get_input_handler()
        if input_handler:
            print_success(f"Input handler loaded: {type(input_handler).__name__}")
            return True
        else:
            print_failure("Input handler not available")
            return False
    except Exception as e:
        print_failure(f"Error loading input handler: {e}")
        return False

def main():
    print_header("UaiBot Platform Support Test")
    print_info(f"Current system: {platform.system()} {platform.release()} {platform.version()}")
    print_info(f"Architecture: {platform.machine()} ({platform.processor()})")
    
    # Run tests
    platform_detection_ok = test_platform_detection()
    platform_manager_ok = test_platform_manager()
    handlers_ok = test_handlers_directly()
    
    # Summarize results
    print_header("Test Results")
    print(f"Platform Detection: {'✓ PASS' if platform_detection_ok else '✗ FAIL'}")
    print(f"Platform Manager: {'✓ PASS' if platform_manager_ok else '✗ FAIL'}")
    print(f"Handler Loading: {'✓ PASS' if handlers_ok else '✗ FAIL'}")
    
    # Overall result
    if platform_detection_ok and platform_manager_ok and handlers_ok:
        print_success("All platform support tests passed!")
        return 0
    else:
        print_failure("Some platform support tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
