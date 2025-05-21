#!/usr/bin/env python3
# direct_test.py

import sys
import os
import platform

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from uaibot.core.ai_handler import get_system_info

def test_fallback_case():
    """Test what happens with unknown OS directly."""
    # Create a mock class to replace platform.system
    class MockPlatformSystem:
        @staticmethod
        def system():
            return "UnknownOS"
    
    # Save original
    original_system = platform.system
    
    try:
        # Replace with mock
        platform.system = MockPlatformSystem.system
        
        # Call function
        result = get_system_info()
        return result
    finally:
        # Restore original
        platform.system = original_system

def main():
    """Run tests and print results."""
    # First get normal system info
    print("Current system info:")
    current_info = get_system_info()
    print(current_info)
    
    # Now test with unknown OS
    print("\nTesting with unknown OS:")
    try:
        unknown_info = test_fallback_case()
        print(unknown_info)
        print("\nTest passed - function handles unknown OS")
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
