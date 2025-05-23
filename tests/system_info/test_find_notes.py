#!/usr/bin/env python3
"""
Test script to directly check the find_folders method
"""

import os
import sys

# Add the parent directory to the path so we can import uaibot.core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from uaibot.core.shell_handler import ShellHandler

def test_find_notes():
    """Test the find_folders method with notes"""
    shell_handler = ShellHandler(safe_mode=False, quiet_mode=False)
    
    print("Testing find_folders with 'notes'...")
    result = shell_handler.find_folders("notes")
    print(result)
    
    print("\nTesting with include_cloud=True explicitly...")
    result = shell_handler.find_folders("notes", include_cloud=True)
    print(result)
    
    print("\nTesting with include_cloud=False...")
    result = shell_handler.find_folders("notes", include_cloud=False)
    print(result)

if __name__ == "__main__":
    test_find_notes()
