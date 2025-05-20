#!/usr/bin/env python3
"""
Verification script for the multilingual test fix.
This script simply imports the test_multilingual module to verify that
it can be imported without syntax errors.
"""
import os
import sys
import importlib

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def verify_import():
    """Verify that test_multilingual can be imported without errors."""
    print("Attempting to import test_multilingual module...")
    try:
        import tests.test_multilingual
        print("✅ Success: test_multilingual module imported correctly!")
        return True
    except SyntaxError as e:
        print(f"❌ SyntaxError: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = verify_import()
    sys.exit(0 if success else 1)
