#!/usr/bin/env python3
"""
Comprehensive test for the UaiBot find_folders method
"""
import os
import sys
import traceback

# Import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Importing required modules...")
    from uaibot.core.shell_handler import ShellHandler
    print("Modules imported successfully!")
    
    print("\nCreating ShellHandler instance...")
    shell = ShellHandler(safe_mode=False)
    print("ShellHandler created successfully!")
    
    # Test with Notes
    print("\n===== TEST: Find Notes folders =====")
    try:
        print("Calling find_folders('notes', include_cloud=True)...")
        result = shell.find_folders('notes', include_cloud=True)
        print("\nResult:")
        print(result)
        print("\n✅ Test passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        traceback.print_exc()
    
    # Test with docs folders
    print("\n===== TEST: Find docs folders =====")
    try:
        print("Calling find_folders('doc', include_cloud=False)...")
        result = shell.find_folders('doc', include_cloud=False)
        print("\nResult:")
        print(result)
        print("\n✅ Test passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        traceback.print_exc()
    
    print("\nAll tests completed!")

except Exception as e:
    print(f"Error setting up tests: {str(e)}")
    traceback.print_exc()
