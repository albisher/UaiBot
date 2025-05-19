#!/usr/bin/env python3
"""
UaiBot Test Runner
-----------------
Centralized script for running different UaiBot test suites.
Provides command-line options for running specific tests or all tests.
"""

import os
import sys
import argparse
import platform
import subprocess
from datetime import datetime

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import the output formatter
from test_files.output_formatter import TestOutputFormatter, format_header, format_box

# Initialize formatter
formatter = TestOutputFormatter()

# Define test directories and files
TEST_DIRS = {
    "unit": os.path.join(project_root, "test_files", "unit"),
    "integration": os.path.join(project_root, "test_files", "integration"),
    "system": os.path.join(project_root, "test_files", "system"),
    "human": os.path.join(project_root, "test_files", "human_interaction"),
}

# Create test directories if they don't exist
for dir_path in TEST_DIRS.values():
    os.makedirs(dir_path, exist_ok=True)

def run_command(command, verbose=True):
    """Run a shell command and return the output."""
    try:
        if verbose:
            print(f"\n{formatter.format_status(f'Running: {command}', 'command')}")
        
        process = subprocess.Popen(
            command, 
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        return_code = process.returncode
        
        if verbose:
            if stdout:
                print(stdout)
            if stderr:
                print(formatter.format_status(stderr, 'error'))
            
            status = 'success' if return_code == 0 else 'error'
            print(formatter.format_status(
                f"Command completed with exit code: {return_code}",
                status
            ))
            
        return {
            'stdout': stdout,
            'stderr': stderr,
            'return_code': return_code
        }
    except Exception as e:
        if verbose:
            print(formatter.format_status(f"Error executing command: {e}", 'error'))
        return {
            'stdout': '',
            'stderr': str(e),
            'return_code': -1
        }

def run_python_script(script_path, args="", verbose=True):
    """Run a Python script with the specified arguments."""
    python_cmd = sys.executable  # Get the current Python interpreter
    full_command = f"{python_cmd} {script_path} {args}"
    return run_command(full_command, verbose)

def run_main_with_flag(flag, args="", verbose=True):
    """Run the main.py script with specified flag and arguments."""
    main_script = os.path.join(project_root, "main.py")
    if not os.path.exists(main_script):
        print(formatter.format_status(f"Error: main.py not found at: {main_script}", "error"))
        return False
    
    return run_python_script(main_script, f"{flag} {args}", verbose)

def find_test_files():
    """Find all test files in the test directories."""
    test_files = []
    for category, directory in TEST_DIRS.items():
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(os.path.join(directory, file))
    return test_files

def run_all_tests(args):
    """Run all tests."""
    print(format_header("Running All UaiBot Tests", "info"))
    
    results = {
        'passed': 0,
        'failed': 0,
        'skipped': 0
    }
    
    test_files = find_test_files()
    if not test_files:
        print(formatter.format_status("No test files found.", "warning"))
        return
    
    for test_file in test_files:
        print(format_header(f"Running {os.path.basename(test_file)}", "file"))
        result = run_python_script(test_file, verbose=args.verbose)
        
        if result['return_code'] == 0:
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Run main.py with -f flag (file tests)
    print(format_header("Running main.py with -f flag tests", "file"))
    sample_files = [
        os.path.join(TEST_DIRS['unit'], "sample.txt"),
        os.path.join(TEST_DIRS['unit'], "sample_binary.bin")
    ]
    
    # Create test files if they don't exist
    for file_path in sample_files:
        try:
            with open(file_path, 'w') as f:
                f.write(f"Test content for {os.path.basename(file_path)}")
        except Exception as e:
            print(formatter.format_status(f"Error creating test file {file_path}: {e}", "error"))
    
    # Test with -f flag
    for file_path in sample_files:
        result = run_main_with_flag("-f", file_path, args.verbose)
        if result and result['return_code'] == 0:
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Print summary
    print("\n" + format_box(
        f"Total Tests: {results['passed'] + results['failed']}\n"
        f"Passed: {results['passed']}\n"
        f"Failed: {results['failed']}\n"
        f"Skipped: {results['skipped']}",
        "Test Summary"
    ))

def run_flag_tests(args):
    """Run tests specifically for command line flags."""
    print(format_header("Running Flag Tests", "command"))
    
    main_script = os.path.join(project_root, "main.py")
    
    # Test file flag (-f)
    sample_file = os.path.join(TEST_DIRS['unit'], "flag_test_sample.txt")
    
    # Create test file
    with open(sample_file, 'w') as f:
        f.write("Sample content for flag testing")
    
    flags_to_test = [
        {"flag": "-f", "args": sample_file, "description": "File processing flag"},
        {"flag": "--file", "args": sample_file, "description": "File processing long flag"},
        {"flag": "-h", "args": "", "description": "Help flag"},
        # Add more flags as needed
    ]
    
    for test in flags_to_test:
        print(formatter.format_status(f"Testing {test['description']}: {test['flag']}", "info"))
        run_main_with_flag(test['flag'], test['args'], args.verbose)
        print("-" * 40)

def run_interaction_tests(args):
    """Run human-like interaction tests."""
    interaction_test_file = os.path.join(project_root, "test_files", "human_interaction_test.py")
    
    # Check if the test file exists
    if not os.path.exists(interaction_test_file):
        print(formatter.format_status(
            f"Human interaction test file not found: {interaction_test_file}",
            "error"
        ))
        return
    
    print(format_header("Running Human-like Interaction Tests", "info"))
    run_python_script(interaction_test_file, verbose=args.verbose)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="UaiBot Test Runner")
    
    parser.add_argument("-a", "--all", action="store_true", help="Run all tests")
    parser.add_argument("-f", "--flag-tests", action="store_true", help="Run flag tests")
    parser.add_argument("-i", "--interaction", action="store_true", help="Run human interaction tests")
    parser.add_argument("-u", "--unit", action="store_true", help="Run unit tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--main-f", help="Run main.py with -f flag and specified file")
    
    args = parser.parse_args()
    
    # Print header
    print(format_header("UaiBot Test Runner", "info"))
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Run selected tests
    if args.all:
        run_all_tests(args)
    elif args.flag_tests:
        run_flag_tests(args)
    elif args.interaction:
        run_interaction_tests(args)
    elif args.unit:
        # Run unit tests only
        unit_test_dir = TEST_DIRS['unit']
        if os.path.exists(unit_test_dir):
            test_files = [f for f in os.listdir(unit_test_dir) 
                         if f.startswith("test_") and f.endswith(".py")]
            
            for test_file in test_files:
                run_python_script(os.path.join(unit_test_dir, test_file), verbose=args.verbose)
        else:
            print(formatter.format_status(f"Unit test directory not found: {unit_test_dir}", "error"))
    elif args.main_f:
        # Run main.py with -f flag and specified file
        run_main_with_flag("-f", args.main_f, True)
    else:
        # No specific test selected, print help
        parser.print_help()
        print("\nAvailable test commands:")
        print("  python run_tests.py --all              # Run all tests")
        print("  python run_tests.py --flag-tests       # Test command line flags")
        print("  python run_tests.py --interaction      # Run human interaction tests")
        print("  python run_tests.py --unit             # Run unit tests only")
        print("  python run_tests.py --main-f FILE      # Run main.py with -f flag")

if __name__ == "__main__":
    main()
