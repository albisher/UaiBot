#!/usr/bin/env python3
# test_all_systems.py

"""
A simpler test script for the get_system_info() function.
Tests detection of various operating systems and edge cases.
"""

import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the function to test
from app.core.ai_handler import get_system_info

def get_current_system():
    """Get the current system info."""
    return get_system_info()

def simulate_os(name, platform_info="", machine="x86_64", version="1.0"):
    """Simulate an OS by patching the platform module."""
    import platform as real_platform
    
    # Save original methods
    original_system = real_platform.system
    original_platform_func = real_platform.platform
    original_machine = real_platform.machine
    original_version = real_platform.version
    
    # Create mock methods
    real_platform.system = lambda: name
    real_platform.platform = lambda: f"{name}-{version}-{platform_info}"
    real_platform.machine = lambda: machine
    real_platform.version = lambda: version
    
    try:
        # Get result with our mocked platform
        result = get_system_info()
        return result
    finally:
        # Restore original methods
        real_platform.system = original_system
        real_platform.platform = original_platform_func
        real_platform.machine = original_machine
        real_platform.version = original_version

def main():
    """Run tests for various operating systems."""
    # Test current system
    print(f"Current system: {get_current_system()}")
    
    # Test various systems
    systems_to_test = [
        ("Darwin", "macOS-like", "arm64", "22.0.0"),
        ("Windows", "Windows-like", "AMD64", "10.0.19041"),
        ("Linux", "Linux-like", "x86_64", "5.15.0"),
        ("FreeBSD", "FreeBSD-like", "amd64", "13.2"),
        ("OpenBSD", "OpenBSD-like", "amd64", "7.3"),
        ("NetBSD", "NetBSD-like", "amd64", "9.3"),
        ("SunOS", "SunOS-like", "sun4", "5.11"),
        ("AIX", "AIX-like", "powerpc", "7.2"),
        ("HPUX", "HPUX-like", "ia64", "11.31"),
        ("UnknownOS", "Unknown-like", "unknown", "0.0")
    ]
    
    print("\n=== Testing various operating systems ===")
    for system, platform_info, machine, version in systems_to_test:
        try:
            result = simulate_os(system, platform_info, machine, version)
            print(f"{system}: {result}")
        except Exception as e:
            print(f"{system}: ERROR - {e}")
    
    print("\nTesting complete!")

if __name__ == "__main__":
    main()
