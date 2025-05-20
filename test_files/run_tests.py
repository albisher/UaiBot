#!/usr/bin/env python3
"""
UaiBot Master Test Script
Runs all tests to fully validate UaiBot's functionality
"""
import os
import sys
import subprocess
import argparse
import time

# Define colors for terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Get project root and tests directory
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)

def print_header(text):
    """Print formatted header"""
    width = 80
    print("\n" + BLUE + BOLD + "=" * width)
    print(text.center(width))
    print("=" * width + RESET + "\n")

def print_subheader(text):
    """Print formatted subheader"""
    print("\n" + YELLOW + BOLD + text + RESET + "\n")

def run_test_script(script_name, description=None):
    """Run a test script and return the result"""
    if description:
        print_subheader(description)
    else:
        print_subheader(f"Running {script_name}")
        
    script_path = os.path.join(TESTS_DIR, script_name)
    
    if not os.path.exists(script_path):
        print(f"{RED}Error: Test script {script_name} not found{RESET}")
        return False
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False, # Show output directly
            text=True,
            check=False # Don't raise exception on non-zero return
        )
        
        success = result.returncode == 0
        
        elapsed = time.time() - start_time
        if success:
            print(f"\n{GREEN}✅ {script_name} completed successfully in {elapsed:.2f}s{RESET}")
        else:
            print(f"\n{RED}❌ {script_name} failed with return code {result.returncode} after {elapsed:.2f}s{RESET}")
            
        return success
    
    except Exception as e:
        print(f"\n{RED}❌ Error running {script_name}: {e}{RESET}")
        return False

def run_language_command_test(language, command, description):
    """Run a specific language command test"""
    print_subheader(description)
    
    main_script = os.path.join(PROJECT_ROOT, "main.py")
    
    if not os.path.exists(main_script):
        print(f"{RED}Error: main.py not found{RESET}")
        return False
    
    try:
        print(f"Testing command: {YELLOW}{command}{RESET}")
        result = subprocess.run(
            [sys.executable, main_script, "-c", command],
            capture_output=True,
            text=True
        )
        
        success = result.returncode == 0
        
        if success:
            print(f"{GREEN}✅ Command executed successfully{RESET}")
            print(f"Output: {result.stdout[:200]}{'...' if len(result.stdout) > 200 else ''}")
        else:
            print(f"{RED}❌ Command failed with return code {result.returncode}{RESET}")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            
        return success
    
    except Exception as e:
        print(f"{RED}❌ Error running command: {e}{RESET}")
        return False

def main():
    """Run all tests"""
    parser = argparse.ArgumentParser(description="UaiBot Master Test Suite")
    parser.add_argument("--quick", action="store_true", help="Run only quick tests")
    parser.add_argument("--architecture", action="store_true", help="Run architecture tests only")
    parser.add_argument("--multilingual", action="store_true", help="Run multilingual tests only")
    parser.add_argument("--screen", action="store_true", help="Run screen session tests only")
    parser.add_argument("--terminal", action="store_true", help="Run terminal command tests only")
    parser.add_argument("--audio", action="store_true", help="Run audio functionality tests only")
    parser.add_argument("--camera", action="store_true", help="Run camera functionality tests only")
    args = parser.parse_args()
    
    print_header("UaiBot Master Test Suite")
    
    # Keep track of test results
    results = {}
    
    # If specific tests are requested, run only those
    if args.architecture or args.multilingual or args.screen or args.terminal or args.audio or args.camera:
        if args.architecture:
            results["Architecture Tests"] = run_test_script("test_architecture.py", "Running Architecture Tests")
        if args.multilingual:
            results["Multilingual Tests"] = run_test_script("test_multilingual.py", "Running Multilingual Tests")
        if args.screen:
            results["Screen Session Tests"] = run_test_script("test_screen_sessions.py", "Running Screen Session Tests")
        if args.terminal:
            results["Terminal Command Tests"] = run_test_script("test_terminal_commands.py", "Running Terminal Command Tests")
        if args.audio:
            results["Audio Tests"] = run_test_script("test_audio.py", "Running Audio Tests")
        if args.camera:
            results["Camera Tests"] = run_test_script("test_camera.py", "Running Camera Tests")
    else:
        # Run all tests or quick tests
        
        # Always run architecture tests
        results["Architecture Tests"] = run_test_script("test_architecture.py", "Running Architecture Tests")
        
        # Run multilingual tests - skip in quick mode
        if not args.quick:
            results["Multilingual Tests"] = run_test_script("test_multilingual.py", "Running Multilingual Tests")
        
        # Run screen session tests - skip in quick mode
        if not args.quick:
            results["Screen Session Tests"] = run_test_script("test_screen_sessions.py", "Running Screen Session Tests")
            
        # Run terminal command tests - skip in quick mode
        if not args.quick:
            results["Terminal Command Tests"] = run_test_script("test_terminal_commands.py", "Running Terminal Command Tests")
            
        # Run audio tests - skip in quick mode
        if not args.quick:
            results["Audio Tests"] = run_test_script("test_audio.py", "Running Audio Tests")
            
        # Run camera tests - skip in quick mode
        if not args.quick:
            results["Camera Tests"] = run_test_script("test_camera.py", "Running Camera Tests")
        
        # Always do quick language tests
        print_subheader("Running Quick Language Tests")
        
        # English
        results["English Command Test"] = run_language_command_test(
            "English",
            "show me usb devices",
            "Testing English Command"
        )
        
        # Arabic
        results["Arabic Command Test"] = run_language_command_test(
            "Arabic",
            "أظهر أجهزة USB المتصلة",
            "Testing Arabic Command"
        )
    
    # Print overall results
    print_header("Test Results Summary")
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        if passed:
            print(f"{GREEN}✅ {test_name}: PASSED{RESET}")
        else:
            print(f"{RED}❌ {test_name}: FAILED{RESET}")
    
    if all_passed:
        print(f"\n{GREEN}{BOLD}🎉 All tests passed! UaiBot is functioning correctly.{RESET}")
    else:
        print(f"\n{RED}{BOLD}⚠️ Some tests failed. Please review the output above.{RESET}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
