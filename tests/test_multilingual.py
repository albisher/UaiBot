#!/usr/bin/env python3
"""
UaiBot Functionality Testing Script
Tests UaiBot by sending natural language commands in both English and Arabic.
"""
import subprocess
import time
import platform
import sys
import os
import datetime

# Define colors for better terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Path to main.py - adjust if needed
MAIN_PY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")

def print_header(text):
    """Print a formatted header"""
    width = 80
    print("\n" + BLUE + BOLD + "=" * width)
    print(text.center(width))
    print("=" * width + RESET + "\n")

def print_test(name, description):
    """Print test information"""
    print(BOLD + f"🧪 Test: {name}" + RESET)
    print(f"📝 Description: {description}\n")

def print_command(command):
    """Print the command being tested"""
    print(YELLOW + f"🔍 Command: {command}" + RESET)

def print_result(success, message=""):
    """Print the test result"""
    if success:
        print(GREEN + "✅ PASSED" + RESET)
    else:
        print(RED + "❌ FAILED" + RESET)
    if message:
        print(message)
    print()

def run_command(command, quiet=True):
    """Run a UaiBot command and return the result"""
    quiet_flag = "-q" if quiet else ""
    full_command = f"python {MAIN_PY_PATH} {quiet_flag} -c \"{command}\""
    
    try:
        print(YELLOW + f"Executing: {full_command}" + RESET)
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        output = result.stdout.strip() + result.stderr.strip()
        return output, result.returncode == 0
    except Exception as e:
        return str(e), False

def run_test(name, description, command, expected_success=True, expected_content=None):
    """Run a single test and report results"""
    print_test(name, description)
    print_command(command)
    output, success = run_command(command)
    
    # Check if the output contains any of the expected content
    content_found = True
    if expected_content and isinstance(expected_content, list):
        content_found = any(text.lower() in output.lower() for text in expected_content)
    elif expected_content:
        content_found = expected_content.lower() in output.lower()
        
    test_passed = (success == expected_success) and (expected_content is None or content_found)
    
    print_result(test_passed)
    print(f"Output: {output[:200]}{'...' if len(output) > 200 else ''}")
    return test_passed

def main():
    """Run all tests"""
    print_header("UaiBot Multilingual Testing Suite")
    print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Testing UaiBot at: {MAIN_PY_PATH}")
    
    tests_passed = 0
    tests_total = 0
    
    # English commands
    print_header("English Commands")
    
    # System information commands
    tests_total += 1
    if run_test(
        "System Info", 
        "Get basic system information", 
        "show me system information", 
        expected_content=["system", "information"]
    ):
        tests_passed += 1
    
    # USB device commands
    tests_total += 1
    if run_test(
        "USB Devices", 
        "List USB devices", 
        "show me all usb devices", 
        expected_content=["USB", "device"]
    ):
        tests_passed += 1
    
    tests_total += 1
    if run_test(
        "USB Detailed", 
        "Get detailed USB information", 
        "tell me more about the connected usb devices", 
        expected_content=["USB", "device", "connected"]
    ):
        tests_passed += 1
    
    # File operations
    tests_total += 1
    if run_test(
        "Directory Listing", 
        "List files in current directory", 
        "show me files in this folder", 
        expected_content=["main.py"]
    ):
        tests_passed += 1
    
    # Screen session related
    tests_total += 1
    if run_test(
        "Screen Sessions", 
        "Check for active screen sessions", 
        "are there any active screen sessions", 
        expected_content=["screen", "session"]
    ):
        tests_passed += 1
    
    # Arabic commands
    print_header("Arabic Commands")
    
    # System information in Arabic
    tests_total += 1
    if run_test(
        "System Info (Arabic)", 
        "Get system information in Arabic", 
        "أظهر معلومات النظام", 
        expected_content=["system"]
    ):
        tests_passed += 1
    
    # USB devices in Arabic
    tests_total += 1
    if run_test(
        "USB Devices (Arabic)", 
        "List USB devices in Arabic", 
        "اعرض أجهزة USB المتصلة", 
        expected_content=["USB", "device"]
    ):
        tests_passed += 1
    
    # File operations in Arabic
    tests_total += 1
    if run_test(
        "Directory Listing (Arabic)", 
        "List files in current directory in Arabic", 
        "أظهر الملفات في هذا المجلد", 
        expected_content=["main.py"]
    ):
        tests_passed += 1
    
    # Mixed Arabic-English commands
    print_header("Mixed Arabic-English Commands")
    
    tests_total += 1
    if run_test(
        "Mixed Language", 
        "Get USB devices with mixed languages", 
        "أظهر USB devices", 
        expected_content=["USB", "device"]
    ):
        tests_passed += 1
    
    # More complex commands
    print_header("Complex Commands")
    
    tests_total += 1
    if run_test(
        "Detailed Disk Space", 
        "Check disk space usage", 
        "show detailed disk space information with human readable format", 
        expected_content=["disk", "space", "available"]
    ):
        tests_passed += 1
    
    tests_total += 1
    if run_test(
        "Screen Handling", 
        "Test screen session integration", 
        "send ls command to screen session", 
        expected_content=["screen", "session"]
    ):
        tests_passed += 1
    
    # Quiet mode commands
    print_header("Quiet Mode Tests")
    
    tests_total += 1
    if run_test(
        "USB Devices in Quiet Mode", 
        "Show USB devices with quiet output", 
        "show usb devices quietly", 
        expected_content=["USB", "device"]
    ):
        tests_passed += 1
    
    # Show final results
    print_header("Test Results")
    print(f"Tests Passed: {tests_passed}/{tests_total} ({tests_passed/tests_total*100:.1f}%)")
    
    if tests_passed == tests_total:
        print(GREEN + BOLD + "\n🎉 All tests passed! UaiBot is functioning correctly!" + RESET)
    else:
        print(RED + BOLD + f"\n⚠️ {tests_total - tests_passed} tests failed. Please review the output above." + RESET)

if __name__ == "__main__":
    main()
