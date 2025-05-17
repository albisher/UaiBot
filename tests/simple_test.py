#!/usr/bin/env python3
"""
Simple direct test of shell_handler functions
"""

import os
import sys
import platform
import traceback

# Make sure we can import from the parent directory
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

try:
    # First try to import the shell handler class
    print("Importing ShellHandler...")
    from core.shell_handler import ShellHandler
    print("ShellHandler imported successfully")
    
    # Check platform
    print(f"\nPlatform: {platform.system()}")
    
    # Create instance
    print("\nCreating ShellHandler instance...")
    shell = ShellHandler(safe_mode=False, quiet_mode=False)
    print("ShellHandler instance created successfully")
    
    # Test the find_folders function
    print("\nTesting find_folders method...")
    print("Calling find_folders('notes', include_cloud=True)...")
    result = shell.find_folders("notes", include_cloud=True)
    print("\nResult from find_folders:")
    print(result)
    
    print("\nTest completed successfully!")
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    print("\nStacktrace:")
    traceback.print_exc()
