#!/usr/bin/env python3
# test_systems_simulation.py

import sys
import os
import platform

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the original function
from app.core.ai_handler import get_system_info as original_get_system_info

def simulate_system(system_type):
    """
    Simulate different system types to test the get_system_info function.
    """
    # Save the original functions
    original_system = platform.system
    
    # Define a mock function for platform.system
    def mock_system():
        return system_type
    
    try:
        # Replace the real function with our mock
        platform.system = mock_system
        
        # Call the original get_system_info function
        return original_get_system_info()
    finally:
        # Restore the original functions
        platform.system = original_system

def main():
    """Test various system types."""
    # Get actual system info first
    print(f"Actual system: {original_get_system_info()}")
    
    # Test with different system types
    print("\nSimulated system types:")
    print("-" * 40)
    
    systems_to_test = ["Darwin", "Windows", "Linux", "FreeBSD", "SunOS", "AIX", "Unknown"]
    
    for system in systems_to_test:
        try:
            info = simulate_system(system)
            print(f"{system}: {info}")
        except Exception as e:
            print(f"{system}: Error - {e}")
    
    print("\nTest completed!")

if __name__ == '__main__':
    main()
