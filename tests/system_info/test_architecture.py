#!/usr/bin/env python3
"""
UaiBot Modular Architecture Testing Script
Tests the new modular structure to ensure all components work together correctly.
"""
import os
import sys
import subprocess
import importlib
import inspect
import platform

# Define colors for better terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Get the project root (one level up from the tests directory)
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)

# Add project root to path
sys.path.append(PROJECT_ROOT)

def print_header(text):
    """Print a formatted header"""
    width = 80
    print("\n" + BLUE + BOLD + "=" * width)
    print(text.center(width))
    print("=" * width + RESET + "\n")

def print_subheader(text):
    """Print a formatted subheader"""
    print(YELLOW + BOLD + f"\n{text}" + RESET)

def print_success(text):
    """Print a success message"""
    print(GREEN + f"✅ {text}" + RESET)

def print_failure(text):
    """Print a failure message"""
    print(RED + f"❌ {text}" + RESET)

def print_info(text):
    """Print an info message"""
    print(f"ℹ️ {text}")

def test_module_imports():
    """Test importing all project modules"""
    # Debug information
    import sys
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print_header("Testing Module Imports")
    
    modules_to_test = [
        # Core modules
        ("core.ai_handler", ["AIHandler"]),
        ("core.shell_handler", ["ShellHandler"]),
        ("core.utils", ["get_project_root", "load_config", "get_platform_name"]),
        
        # Command processor
        ("command_processor", ["CommandProcessor"]),
        
        # Device manager
        ("device_manager", ["USBDetector"]),
        
        # Screen handler
        ("uaibot.core.screen_handler.screen_manager", ["ScreenManager"]),
        ("uaibot.core.screen_handler.session_manager", ["ScreenSessionHandler", "SessionManager"]),
        
        # Utils
        ("utils", []),
    ]
    
    all_passed = True
    
    for module_name, expected_exports in modules_to_test:
        print_subheader(f"Testing import: {module_name}")
        
        try:
            # Try to import the module
            module = importlib.import_module(module_name)
            print_success(f"Successfully imported {module_name}")
            
            # Check for expected exports
            for export in expected_exports:
                if hasattr(module, export):
                    attr = getattr(module, export)
                    if inspect.isclass(attr) or inspect.isfunction(attr):
                        print_success(f"Found expected export: {export}")
                    else:
                        print_failure(f"Export {export} exists but is not a class or function")
                        all_passed = False
                else:
                    print_failure(f"Missing expected export: {export}")
                    all_passed = False
                    
        except ImportError as e:
            print_failure(f"Failed to import {module_name}: {e}")
            all_passed = False
    
    return all_passed

def test_module_composition(quiet=True):
    """Test that modules can be instantiated and composed together"""
    print_header("Testing Module Composition")
    
    # First check if main modules can be imported
    try:
        from uaibot.core.ai_handler import AIHandler
        from uaibot.core.shell_handler import ShellHandler
        from uaibot.core.command_processor import CommandProcessor
        from uaibot.core.device_manager import USBDetector
        from uaibot.core.screen_handler.screen_manager import ScreenManager
        print_success("All primary modules imported successfully")
    except ImportError as e:
        print_failure(f"Failed to import primary modules: {e}")
        return False
    
    all_passed = True
    
    # Test device manager instantiation
    print_subheader("Testing device_manager.USBDetector instantiation")
    try:
        usb_detector = USBDetector(quiet_mode=quiet)
        print_success("USBDetector instantiated successfully")
    except Exception as e:
        print_failure(f"Failed to instantiate USBDetector: {e}")
        all_passed = False
        return all_passed
    
    # Test screen manager instantiation
    print_subheader("Testing uaibot.core.screen_handler.ScreenManager instantiation")
    try:
        screen_manager = ScreenManager(quiet_mode=quiet)
        print_success("ScreenManager instantiated successfully")
    except Exception as e:
        print_failure(f"Failed to instantiate ScreenManager: {e}")
        all_passed = False
        return all_passed
    
    # Test shell handler instantiation
    print_subheader("Testing core.ShellHandler instantiation")
    try:
        shell_handler = ShellHandler(safe_mode=True, quiet_mode=quiet)
        print_success("ShellHandler instantiated successfully")
    except Exception as e:
        print_failure(f"Failed to instantiate ShellHandler: {e}")
        all_passed = False
        return all_passed
    
    # Test passing screen manager to shell handler
    print_subheader("Testing ShellHandler + ScreenManager integration")
    try:
        shell_handler.screen_manager = screen_manager
        print_success("Set ScreenManager in ShellHandler")
        
        # Test send_to_screen_session functionality
        result = shell_handler.send_to_screen_session("echo 'test'")
        if "screen session" in result.lower() or "no active screen sessions" in result.lower():
            print_success("ShellHandler.send_to_screen_session works")
        else:
            print_failure(f"Unexpected response from send_to_screen_session: {result}")
            all_passed = False
    except Exception as e:
        print_failure(f"Failed to integrate ScreenManager with ShellHandler: {e}")
        all_passed = False
    
    # Test command processor instantiation with dependencies
    print_subheader("Testing CommandProcessor instantiation with dependencies")
    try:
        # Mock an AI handler since we don't want to make real API calls
        class MockAIHandler:
            def __init__(self, *args, **kwargs):
                pass
                
            def query_ai(self, *args, **kwargs):
                return "This is a mock AI response"
        
        # Create the command processor with all dependencies
        command_processor = CommandProcessor(
            ai_handler=MockAIHandler(), 
            shell_handler=shell_handler,
            quiet_mode=quiet
        )
        print_success("CommandProcessor instantiated successfully with all dependencies")
        
        # Test a simple command
        print_subheader("Testing CommandProcessor.process_command")
        try:
            result = command_processor.process_command("show me usb devices")
            print_success(f"CommandProcessor processed command successfully")
            print_info(f"Result: {result[:100]}...")
        except Exception as e:
            print_failure(f"CommandProcessor.process_command failed: {e}")
            all_passed = False
    except Exception as e:
        print_failure(f"Failed to instantiate CommandProcessor: {e}")
        all_passed = False
    
    return all_passed

def test_main_script():
    """Test running the main script with basic commands"""
    print_header("Testing main.py Script")
    
    main_script = os.path.join(PROJECT_ROOT, "main.py")
    if not os.path.exists(main_script):
        print_failure(f"main.py not found at {main_script}")
        return False
    
    commands_to_test = [
        ("Simple test", "echo test", True),
        ("USB devices test", "show usb devices", True),
        ("Help command", "help", True),
        ("Invalid command", "this_is_not_a_valid_command_123456", True)
    ]
    
    all_passed = True
    
    for desc, cmd, expected_success in commands_to_test:
        print_subheader(f"Testing: {desc} - '{cmd}'")
        
        try:
            result = subprocess.run(
                [sys.executable, main_script, "-q", "-c", cmd],
                capture_output=True,
                text=True
            )
            
            # Success is defined as the process returning 0 if we expect success
            success = (result.returncode == 0) == expected_success
            
            if success:
                print_success(f"Command executed with expected result")
                if result.stdout.strip():
                    print_info(f"Output: {result.stdout[:100]}...")
            else:
                print_failure(f"Command did not execute with expected result")
                print_info(f"Return code: {result.returncode}")
                print_info(f"Stdout: {result.stdout}")
                print_info(f"Stderr: {result.stderr}")
                all_passed = False
        except Exception as e:
            print_failure(f"Error executing main.py: {e}")
            all_passed = False
    
    return all_passed

def test_integration():
    """Test that all modules work together for common use cases"""
    print_header("Testing Component Integration")
    
    # Define some integration test cases
    test_cases = [
        {
            "name": "USB Device Detection",
            "setup": """
from device_manager import USBDetector
from uaibot.core.shell_handler import ShellHandler

usb_detector = USBDetector(quiet_mode=True)
shell_handler = ShellHandler(quiet_mode=True)
shell_handler.usb_detector = usb_detector
            """,
            "test": """
# Test if shell handler uses the USB detector
devices_from_shell = shell_handler.get_usb_devices()
devices_from_detector = usb_detector.get_usb_devices()

result = (devices_from_shell == devices_from_detector)
            """
        },
        {
            "name": "Screen Manager Integration",
            "setup": """
from uaibot.core.screen_handler.screen_manager import ScreenManager
from uaibot.core.shell_handler import ShellHandler

screen_manager = ScreenManager(quiet_mode=True)
shell_handler = ShellHandler(quiet_mode=True)
shell_handler.screen_manager = screen_manager
            """,
            "test": """
# Test if shell handler forwards to screen manager
cmd1 = shell_handler.send_to_screen_session("test command")
cmd2 = screen_manager.send_command_to_session("test command")

# Should both contain similar messages about screen sessions
result = ("screen session" in cmd1.lower() and "screen session" in cmd2.lower())
            """
        },
        {
            "name": "Command Processor Integration",
            "setup": """
class MockAIHandler:
    def __init__(self, *args, **kwargs):
        pass
        
    def query_ai(self, *args, **kwargs):
        return "echo test response"

from uaibot.core.shell_handler import ShellHandler
from command_processor import CommandProcessor

shell_handler = ShellHandler(quiet_mode=True)
command_processor = CommandProcessor(
    ai_handler=MockAIHandler(),
    shell_handler=shell_handler,
    quiet_mode=True
)
            """,
            "test": """
# Test if command processor handles USB queries
result1 = "usb" in command_processor.process_command("show usb devices").lower()

# Test if command processor handles basic commands
result2 = command_processor.process_command("echo test") == "test"

result = result1 and result2
            """
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print_subheader(f"Integration Test: {test_case['name']}")
        
        # Create a local namespace
        local_vars = {}
        
        try:
            # Execute the setup code
            exec(test_case["setup"], globals(), local_vars)
            print_success("Setup completed successfully")
            
            # Execute the test code
            exec(test_case["test"], globals(), local_vars)
            
            # Check the result
            if local_vars.get("result", False):
                print_success(f"Integration test passed")
            else:
                print_failure(f"Integration test failed")
                all_passed = False
                
        except Exception as e:
            print_failure(f"Error in integration test: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests for the modular architecture"""
    print_header("UaiBot Modular Architecture Testing")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Project Root: {PROJECT_ROOT}")
    
    test_results = {
        "Module Imports": test_module_imports(),
        "Module Composition": test_module_composition(quiet=True),
        "Main Script": test_main_script(),
        "Component Integration": test_integration()
    }
    
    print_header("Overall Test Results")
    
    all_passed = True
    for test_name, passed in test_results.items():
        if passed:
            print(GREEN + f"✅ {test_name}: PASSED" + RESET)
        else:
            print(RED + f"❌ {test_name}: FAILED" + RESET)
            all_passed = False
    
    if all_passed:
        print(GREEN + BOLD + "\n🎉 All architecture tests passed! The modular structure is working correctly." + RESET)
    else:
        print(RED + BOLD + "\n⚠️ Some architecture tests failed. Please review the output above." + RESET)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
