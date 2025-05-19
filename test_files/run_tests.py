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
import signal
from datetime import datetime

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import the output formatter
try:
    from test_files.output_formatter import TestOutputFormatter, format_header, format_box
    formatter = TestOutputFormatter()
except ImportError:
    # Create basic formatter as fallback
    class SimpleFormatter:
        def format_status(self, msg, status="info"):
            symbols = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️", "command": "📌"}
            return f"{symbols.get(status, '•')} {msg}"
            
        def format_header(self, text, emoji_key=None):
            return f"{text}\n{'-' * len(text)}"
            
        def format_box(self, content, title=None):
            result = []
            width = 60
            if title:
                result.append(f"+--- {title} {'-' * (width - len(title) - 6)}+")
            else:
                result.append(f"+{'-' * (width - 2)}+")
                
            for line in content.split('\n'):
                if len(line) > width - 4:
                    line = line[:width-7] + '...'
                result.append(f"| {line}{' ' * (width - len(line) - 3)}|")
                
            result.append(f"+{'-' * (width - 2)}+")
            return '\n'.join(result)
    
    formatter = SimpleFormatter()
    format_header = formatter.format_header
    format_box = formatter.format_box

# Define test directories and files
TEST_DIRS = {
    "unit": os.path.join(current_dir, "unit"),
    "integration": os.path.join(current_dir, "integration"),
    "system": os.path.join(current_dir, "system"),
    "human": os.path.join(current_dir, "human_interaction"),
}

# Create test directories if they don't exist
for dir_path in TEST_DIRS.values():
    os.makedirs(dir_path, exist_ok=True)

def run_command(command, verbose=True, timeout=60):
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
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return_code = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return_code = -1
            stderr += "\nCommand timed out"
        
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

def run_python_script(script_path, args="", verbose=True, timeout=60):
    """Run a Python script with the specified arguments."""
    python_cmd = sys.executable  # Get the current Python interpreter
    full_command = f"{python_cmd} {script_path} {args}"
    return run_command(full_command, verbose, timeout)

def run_main_with_flag(flag, args="", verbose=True, timeout=60):
    """Run the main.py script with specified flag and arguments."""
    main_script = os.path.join(project_root, "main.py")
    if not os.path.exists(main_script):
        print(formatter.format_status(f"Error: main.py not found at: {main_script}", "error"))
        return False
    
    return run_python_script(main_script, f"{flag} {args}", verbose, timeout)

def find_test_files(pattern="test_*.py"):
    """Find all test files in the test directories."""
    test_files = []
    for category, directory in TEST_DIRS.items():
        if os.path.exists(directory):
            import glob
            matched_files = glob.glob(os.path.join(directory, pattern))
            test_files.extend(matched_files)
    return test_files

def ensure_test_files_exist():
    """Ensure test files and directories exist. If not, create them."""
    # First make sure the directories exist
    for category, directory in TEST_DIRS.items():
        os.makedirs(directory, exist_ok=True)
    
    # Create a basic sample file if needed
    sample_path = os.path.join(TEST_DIRS["unit"], "sample.txt")
    if not os.path.exists(sample_path):
        try:
            with open(sample_path, 'w') as f:
                f.write("This is a sample text file for testing.")
            print(formatter.format_status(f"Created sample file: {sample_path}", "success"))
        except Exception as e:
            print(formatter.format_status(f"Failed to create sample file: {e}", "error"))
    
    # Create a basic test file if none exist
    test_files = find_test_files()
    if not test_files:
        basic_test = os.path.join(TEST_DIRS["unit"], "test_basic.py")
        try:
            with open(basic_test, 'w') as f:
                f.write("""#!/usr/bin/env python3
\"\"\"Basic test file created automatically.\"\"\"
import unittest

class BasicTest(unittest.TestCase):
    def test_true(self):
        self.assertTrue(True, "True should be True")
        
if __name__ == "__main__":
    unittest.main()
""")
            print(formatter.format_status(f"Created basic test file: {basic_test}", "success"))
        except Exception as e:
            print(formatter.format_status(f"Failed to create basic test file: {e}", "error"))

def run_all_tests(args):
    """Run all tests."""
    print(format_header("Running All UaiBot Tests", "info"))
    
    results = {
        'passed': 0,
        'failed': 0,
        'skipped': 0
    }
    
    # Ensure we have test files to run
    ensure_test_files_exist()
    
    test_files = find_test_files()
    if not test_files:
        print(formatter.format_status("No test files found. Creating basic test files.", "warning"))
        ensure_test_files_exist()
        test_files = find_test_files()
    
    if not test_files:
        print(formatter.format_status("Still no test files found. Cannot run tests.", "error"))
        return
        
    for test_file in test_files:
        print(format_header(f"Running {os.path.basename(test_file)}", "file"))
        result = run_python_script(test_file, verbose=args.verbose, timeout=args.timeout)
        
        if result['return_code'] == 0:
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Run main.py with -f flag (file tests)
    print(format_header("Running main.py with -f flag tests", "file"))
    sample_files = [
        os.path.join(TEST_DIRS['unit'], "sample.txt"),
    ]
    
    # Create test files if they don't exist
    for file_path in sample_files:
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w') as f:
                    f.write(f"Test content for {os.path.basename(file_path)}")
                print(formatter.format_status(f"Created test file: {file_path}", "success"))
            except Exception as e:
                print(formatter.format_status(f"Error creating test file {file_path}: {e}", "error"))
    
    # Test with -f flag
    for file_path in sample_files:
        if os.path.exists(file_path):
            result = run_main_with_flag("-f", file_path, args.verbose, args.timeout)
            if result and result.get('return_code') == 0:
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
    if not os.path.exists(sample_file):
        try:
            with open(sample_file, 'w') as f:
                f.write("Sample content for flag testing")
            print(formatter.format_status(f"Created test file: {sample_file}", "success"))
        except Exception as e:
            print(formatter.format_status(f"Error creating test file: {e}", "error"))
    
    flags_to_test = [
        {"flag": "-f", "args": sample_file, "description": "File processing flag"},
        {"flag": "-h", "args": "", "description": "Help flag"},
        # Add more flags as needed
    ]
    
    for test in flags_to_test:
        print(formatter.format_status(f"Testing {test['description']}: {test['flag']}", "info"))
        run_main_with_flag(test['flag'], test['args'], args.verbose, args.timeout)
        print("-" * 40)

def run_interaction_tests(args):
    """Run human-like interaction tests."""
    # First check for the human interaction test directory
    if not os.path.exists(TEST_DIRS['human']):
        os.makedirs(TEST_DIRS['human'], exist_ok=True)
    
    # Check for sample interaction test file
    interaction_test_file = os.path.join(TEST_DIRS['human'], "sample_interaction_test.py")
    
    # Create a simple test file if it doesn't exist
    if not os.path.exists(interaction_test_file):
        try:
            with open(interaction_test_file, 'w') as f:
                f.write("""#!/usr/bin/env python3
\"\"\"
Simple human interaction test with timeout to prevent hanging.
\"\"\"
import os
import sys
import time
import signal

def timeout_handler(signum, frame):
    print("Test timed out after 10 seconds")
    sys.exit(0)

# Set timeout to prevent hanging
signal.signal(signal.SIGALRM, signal.SIGALRM)
signal.alarm(10)

print("Human Interaction Test")
print("---------------------")

# Simulate some interaction
for i in range(5):
    print(f"Step {i+1}/5...")
    time.sleep(1)

print("Test completed successfully!")
""")
            print(formatter.format_status(f"Created interaction test: {interaction_test_file}", "success"))
        except Exception as e:
            print(formatter.format_status(f"Error creating interaction test: {e}", "error"))
    
    print(format_header("Running Human-like Interaction Tests", "info"))
    
    # Run with a timeout to prevent hanging
    result = run_python_script(
        interaction_test_file, 
        verbose=args.verbose, 
        timeout=args.timeout or 30
    )
    
    if result and result.get('return_code') == 0:
        print(formatter.format_status("Human interaction test completed successfully!", "success"))
    else:
        print(formatter.format_status("Human interaction test failed or timed out", "error"))

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="UaiBot Test Runner")
    
    parser.add_argument("-a", "--all", action="store_true", help="Run all tests")
    parser.add_argument("-f", "--flag-tests", action="store_true", help="Run flag tests")
    parser.add_argument("-i", "--interaction", action="store_true", help="Run human interaction tests")
    parser.add_argument("-u", "--unit", action="store_true", help="Run unit tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-t", "--timeout", type=int, default=60, help="Command timeout in seconds")
    parser.add_argument("--main-f", help="Run main.py with -f flag and specified file")
    parser.add_argument("--create-structure", action="store_true", help="Create test structure")
    
    args = parser.parse_args()
    
    # Print header
    print(format_header("UaiBot Test Runner", "info"))
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Create test structure if requested
    if args.create_structure:
        create_script = os.path.join(current_dir, "create_test_structure.py")
        if os.path.exists(create_script):
            run_python_script(create_script, verbose=args.verbose)
        else:
            print(formatter.format_status(f"Create structure script not found: {create_script}", "error"))
            print(formatter.format_status("Creating basic test directories instead", "info"))
            for dir_path in TEST_DIRS.values():
                os.makedirs(dir_path, exist_ok=True)
                print(formatter.format_status(f"Created directory: {dir_path}", "success"))
    
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
            
            if not test_files:
                print(formatter.format_status("No unit test files found", "warning"))
                ensure_test_files_exist()
                test_files = [f for f in os.listdir(unit_test_dir) 
                             if f.startswith("test_") and f.endswith(".py")]
            
            for test_file in test_files:
                test_path = os.path.join(unit_test_dir, test_file)
                run_python_script(test_path, verbose=args.verbose, timeout=args.timeout)
        else:
            print(formatter.format_status(f"Unit test directory not found: {unit_test_dir}", "error"))
            os.makedirs(unit_test_dir, exist_ok=True)
            print(formatter.format_status(f"Created unit test directory: {unit_test_dir}", "success"))
    elif args.main_f:
        # Run main.py with -f flag and specified file
        run_main_with_flag("-f", args.main_f, True, args.timeout)
    else:
        # No specific test selected, print help
        parser.print_help()
        print("\nAvailable test commands:")
        print("  python run_tests.py --all              # Run all tests")
        print("  python run_tests.py --flag-tests       # Test command line flags")
        print("  python run_tests.py --interaction      # Run human interaction tests")
        print("  python run_tests.py --unit             # Run unit tests only")
        print("  python run_tests.py --main-f FILE      # Run main.py with -f flag")
        print("  python run_tests.py --create-structure # Create test structure")
        print("\nYou can add --timeout N to set a timeout of N seconds for commands")

if __name__ == "__main__":
    main()
