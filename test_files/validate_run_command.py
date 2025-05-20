#!/usr/bin/env python3
"""
Validation script for the run_command utility function.
This script directly tests the functionality of run_command outside of the UaiBot context.
"""
import os
import sys

# Add the parent directory to the path so we can import the UaiBot modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the run_command utility
from core.utils import run_command

def main():
    """Run a series of tests to validate the run_command utility."""
    print("Testing run_command utility...\n")
    
    # Test 1: Simple command execution
    print("Test 1: Simple command - 'echo Hello from UaiBot!'")
    result = run_command("echo Hello from UaiBot!", shell=True, capture_output=True, text=True)
    print(f"Success: {result['success']}")
    print(f"Return code: {result['returncode']}")
    print(f"stdout: {result['stdout']}")
    print(f"stderr: {result['stderr'] or '(no error)'}")
    print("\n" + "-" * 50 + "\n")
    
    # Test 2: Command with arguments
    print("Test 2: Command with arguments - 'ls -la /tmp | head -n 5'")
    result = run_command("ls -la /tmp | head -n 5", shell=True, capture_output=True, text=True)
    print(f"Success: {result['success']}")
    print(f"Return code: {result['returncode']}")
    print(f"stdout: {result['stdout']}")
    print(f"stderr: {result['stderr'] or '(no error)'}")
    print("\n" + "-" * 50 + "\n")
    
    # Test 3: Command that fails
    print("Test 3: Command that fails - 'ls /nonexistent_directory'")
    result = run_command("ls /nonexistent_directory", shell=True, capture_output=True, text=True)
    print(f"Success: {result['success']}")
    print(f"Return code: {result['returncode']}")
    print(f"stdout: {result['stdout'] or '(no output)'}")
    print(f"stderr: {result['stderr']}")
    print("\n" + "-" * 50 + "\n")
    
    # Test 4: System command
    print("Test 4: System command - 'uname -a'")
    result = run_command("uname -a", shell=True, capture_output=True, text=True)
    print(f"Success: {result['success']}")
    print(f"Return code: {result['returncode']}")
    print(f"stdout: {result['stdout']}")
    print(f"stderr: {result['stderr'] or '(no error)'}")
    print("\n" + "-" * 50 + "\n")
    
    # Test 5: Notes-specific command (only on macOS)
    if sys.platform == 'darwin':
        print("Test 5: Notes app command - list folders")
        result = run_command("""osascript -e 'tell application "Notes" to get name of every folder'""", 
                           shell=True, capture_output=True, text=True)
        print(f"Success: {result['success']}")
        print(f"Return code: {result['returncode']}")
        print(f"stdout: {result['stdout']}")
        print(f"stderr: {result['stderr'] or '(no error)'}")
        print("\n" + "-" * 50 + "\n")
    
if __name__ == "__main__":
    main()
