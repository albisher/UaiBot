#!/usr/bin/env python3
"""
Test script to directly check the find_files method
"""

import os
import sys

# Add the parent directory to the path so we can import uaibot.core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from uaibot.core.shell_handler import ShellHandler

def test_find_files():
    """Test the find_files method with different parameters"""
    shell_handler = ShellHandler(safe_mode=False, quiet_mode=False)
    
    print("Testing find_files with 'file'...")
    result = shell_handler.find_files("file")
    print(result)
    
    print("\nTesting with specific location (test_files)...")
    # Make sure test_files directory exists
    test_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_files')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a test file if it doesn't exist
    test_file = os.path.join(test_dir, 'test_file.txt')
    if not os.path.exists(test_file):
        with open(test_file, 'w') as f:
            f.write("This is a test file for find_files testing")
    
    result = shell_handler.find_files("test", test_dir)
    print(result)
    
    print("\nTesting with include_metadata=False...")
    result = shell_handler.find_files("test", test_dir, include_metadata=False)
    print(result)

    # Reproduce the exact command from terminal input
    print("\nTesting with the exact command pattern from terminal...")
    result = shell_handler.execute_command("find '~' -type f -name '*file*' -not -path '*/\\.*' 2>/dev/null | head -n 15", force_shell=True)
    print(result)

if __name__ == "__main__":
    test_find_files()
