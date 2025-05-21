#!/usr/bin/env python3
# test_edge_cases.py

import sys
import os
import unittest
from unittest import mock

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import directly from the module file
from uaibot.core.ai_handler import get_system_info

class MockPlatform:
    @staticmethod
    def system():
        return "UnknownOS"
    
    @staticmethod
    def platform():
        return "UnknownOS-1.0"
    
    @staticmethod
    def machine():
        return "x86_64"
    
    @staticmethod
    def processor():
        return "x86_64"
    
    @staticmethod
    def version():
        return "1.0"

@mock.patch('core.ai_handler.platform', MockPlatform)
@mock.patch('os.environ.get', return_value="/bin/funny_shell")
def test_unknown_os(mock_env):
    """Test that an unknown OS is handled correctly."""
    result = get_system_info()
    print(f"Unknown OS result: {result}")
    assert "UnknownOS-1.0" in result
    assert "x86_64" in result
    assert "funny_shell" in result
    return result

def main():
    """Run the test for an unknown OS."""
    try:
        result = test_unknown_os()
        print("\nTest passed! Unknown OS handled correctly.")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
