#!/usr/bin/env python3
"""
Test script to verify platform detection and platform-specific modules
"""
import os
import sys
import platform

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.platform_uai.platform_utils import detect_platform, get_audio_handler, get_usb_handler

def main():
    # Print system information
    print(f"System: {platform.system()}")
    print(f"Platform: {platform.platform()}")
    
    # Detect platform
    platform_name, platform_dir = detect_platform()
    print(f"Detected platform: {platform_name}")
    print(f"Platform directory: {platform_dir}")
    
    # Try to load platform-specific handlers
    print("\nTesting Audio Handler:")
    audio_handler = get_audio_handler()
    if audio_handler:
        print(f"  Audio handler class: {audio_handler.__class__.__name__}")
        print(f"  Audio devices: {len(audio_handler.list_audio_devices())}")
    else:
        print("  Failed to load audio handler for this platform")
    
    print("\nTesting USB Handler:")
    usb_handler = get_usb_handler()
    if usb_handler:
        print(f"  USB handler class: {usb_handler.__class__.__name__}")
        devices = usb_handler.get_device_list()
        print(f"  USB devices found: {len(devices)}")
    else:
        print("  Failed to load USB handler for this platform")

if __name__ == "__main__":
    main()
