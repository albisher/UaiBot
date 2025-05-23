#!/usr/bin/env python3
"""
Test script that directly accesses shell_handler with debug output
"""

import os
import sys
import traceback

# Add the parent directory to the path so we can import uaibot.core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from uaibot.core.shell_handler import ShellHandler

def test_find_folders_with_debug():
    """Test find_folders with extensive debug output"""
    print("Creating ShellHandler...")
    shell_handler = ShellHandler(safe_mode=False, quiet_mode=False)
    
    print("\nAttempting to find notes folders with debug...")
    try:
        print("Calling find_folders('notes')...")
        result = shell_handler.find_folders("notes")
        print("Result received successfully!")
        print("\n--- Result ---")
        print(result)
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_find_folders_with_debug()
