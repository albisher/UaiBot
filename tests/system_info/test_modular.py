#!/usr/bin/env python3
"""
Test script for the modular UaiBot structure.
Tests key functionalities like USB detection and command processing.
"""
import os
import sys

# Add parent directory to path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import modules directly from their files to avoid package issues
from app.core.device_manager.usb_detector import USBDetector
from app.core.screen_handler.screen_manager import ScreenManager
from app.utils import get_platform_name

def test_usb_detection():
    """Test USB device detection"""
    print("=== Testing USB Device Detection ===")
    detector = USBDetector(quiet_mode=False)
    print(detector.get_usb_devices())
    print("\nUSB Detection Test Complete!")

def test_screen_manager():
    """Test screen session management"""
    print("\n=== Testing Screen Session Management ===")
    manager = ScreenManager(quiet_mode=False)
    sessions = manager.list_sessions()
    print(f"Found {len(sessions)} screen sessions:")
    for session_id, status in sessions.items():
        print(f"  - {session_id}: {status}")
    
    if sessions:
        print("\nNote: To test sending commands to screen sessions,")
        print("first create a screen session with 'screen' command.")
    print("\nScreen Manager Test Complete!")

def test_utils():
    """Test utility functions"""
    print("\n=== Testing Utility Functions ===")
    platform_name = get_platform_name()
    print(f"Platform Name: {platform_name}")
    print("\nUtility Functions Test Complete!")

if __name__ == "__main__":
    print("UaiBot Modular Structure Test")
    print("=============================")
    test_usb_detection()
    test_screen_manager()
    test_utils()
    print("\nAll tests completed!")
