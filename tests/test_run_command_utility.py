#!/usr/bin/env python3
# filepath: /Users/amac/Documents/code/UaiBot/tests/test_run_command_utility.py
"""
Test script for demonstrating the various ways to run terminal commands 
using the new run_command utility function.
"""
import os
import sys
import time

# Add the project root to the path so we can import from core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.utils import run_command

def test_basic_commands():
    """Test basic command execution with different methods"""
    print("=== Testing Basic Command Execution ===")
    
    # Basic usage - list files
    print("\n1. Basic command (list files):")
    result = run_command("ls -la")
    print(f"Success: {result['success']}")
    print(f"Output: \n{result['stdout'][:500]}...")  # Show first 500 chars
    
    # Get system info
    print("\n2. System information:")
    result = run_command("uname -a")
    print(f"System: {result['stdout'].strip()}")
    
    # Run a Python command
    print("\n3. Running a Python one-liner:")
    result = run_command(['python3', '-c', 'print("Hello from Python subprocess!")'])
    print(f"Output: {result['stdout'].strip()}")
    
    # Command with error
    print("\n4. Running a command that will fail:")
    result = run_command("ls /nonexistent_directory")
    print(f"Success: {result['success']}")
    print(f"Return code: {result['returncode']}")
    print(f"Error: {result['stderr']}")

def test_advanced_features():
    """Test more advanced features of the run_command function"""
    print("\n=== Testing Advanced Features ===")
    
    # Change directory
    print("\n1. Running command in a different directory:")
    home_dir = os.path.expanduser("~")
    result = run_command("ls -la", cwd=home_dir)
    print(f"Files in home directory: {len(result['stdout'].splitlines())} files found")
    
    # Environment variables
    print("\n2. Setting custom environment variables:")
    custom_env = os.environ.copy()
    custom_env["TEST_VAR"] = "Hello from environment variable"
    result = run_command("echo $TEST_VAR", shell=True, env=custom_env)
    print(f"Environment variable value: {result['stdout'].strip()}")
    
    # Timeout
    print("\n3. Command with timeout:")
    try:
        result = run_command("sleep 2; echo 'Done sleeping'", shell=True, timeout=1)
        print(f"Success: {result['success']}")
        print(f"Output: {result['stdout'] if result['stdout'] else result['stderr']}")
    except Exception as e:
        print(f"Exception: {e}")

def test_async_execution():
    """Test asynchronous command execution"""
    print("\n=== Testing Asynchronous Execution ===")
    
    print("\n1. Running a command asynchronously:")
    process = run_command("sleep 1; echo 'Command completed!'", shell=True, async_mode=True, capture_output=True, text=True)
    
    print("Doing other work while command runs...")
    for i in range(5):
        print(f"Working... {i+1}/5")
        time.sleep(0.3)
    
    # Now get the output
    stdout, stderr = process.communicate()
    print(f"Command output: {stdout.strip()}")
    print(f"Exit code: {process.returncode}")

def test_shell_injection_prevention():
    """Test that shell injection is prevented by default"""
    print("\n=== Testing Shell Injection Prevention ===")
    
    # Safe approach using list form
    print("\n1. Safe command execution (list form):")
    filename = "test_file.txt; echo 'INJECTION SUCCEEDED'"
    result = run_command(["ls", filename])
    print(f"Output: {result['stderr']}")
    
    # Potentially unsafe with shell=True
    print("\n2. Shell=True (potentially unsafe, use with caution):")
    result = run_command(f"ls {filename}", shell=True)
    print(f"Output: {result['stderr']}")
    
    print("\nNote: In the first case, the command looks for a literal file named "
          "'test_file.txt; echo INJECTION SUCCEEDED', while in the second case with "
          "shell=True, it would actually execute the injected echo command if the ; was "
          "interpreted by the shell.")

def main():
    """Main test function"""
    print("Testing the run_command utility function\n")
    
    test_basic_commands()
    test_advanced_features()
    test_async_execution()
    test_shell_injection_prevention()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()
