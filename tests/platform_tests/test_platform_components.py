#!/usr/bin/env python3
"""
UaiBot platform test script

This script tests the platform-specific components and verifies that they work correctly
on the current system. It also demonstrates how to use the platform manager.
"""
import os
import sys
import platform

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from platform_uai.platform_manager import PlatformManager
from uaibot.utils import get_platform_name, load_config

def main():
    """Test platform-specific components"""
    print("UaiBot Platform Test")
    print("====================")
    print(f"System: {platform.system()}")
    print(f"Platform: {platform.platform()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Detected platform: {get_platform_name()}")
    print()
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration. Please check config/settings.json")
        sys.exit(1)
    else:
        print("Configuration loaded successfully.")
        print(f"  AI Provider: {config.get('default_ai_provider', 'Not specified')}")
        if config.get('default_ai_provider') == 'ollama':
            print(f"  Ollama Model: {config.get('default_ollama_model', 'Not specified')}")
            print(f"  Ollama URL: {config.get('ollama_base_url', 'Not specified')}")
        elif config.get('default_ai_provider') == 'google':
            print(f"  Google Model: {config.get('default_google_model', 'Not specified')}")
            print(f"  Google API Key: {'Set' if config.get('google_api_key') else 'Not set'}")
    print()
    
    # Initialize platform manager
    print("Initializing platform manager...")
    platform_mgr = PlatformManager()
    if platform_mgr.platform_supported:
        print(f"Platform '{platform_mgr.platform_name}' is supported.")
        if platform_mgr.initialize():
            print("Platform initialization successful!")
            
            # Test audio handler
            print("\nTesting Audio Handler:")
            audio = platform_mgr.get_audio_handler()
            if audio:
                print(f"  Audio handler class: {audio.__class__.__name__}")
                devices = audio.list_audio_devices()
                print(f"  Found {len(devices)} audio device(s):")
                for i, device in enumerate(devices):
                    print(f"    {i+1}. {device.get('name', 'Unknown')} - {device.get('maxInputChannels', 0)} in, {device.get('maxOutputChannels', 0)} out")
            else:
                print("  Audio handler not available.")
                
            # Test USB handler
            print("\nTesting USB Handler:")
            usb = platform_mgr.get_usb_handler()
            if usb:
                print(f"  USB handler class: {usb.__class__.__name__}")
                devices = usb.get_device_list()
                print(f"  Found {len(devices)} USB device(s):")
                for i, device in enumerate(devices):
                    print(f"    {i+1}. {device.get('product', 'Unknown')} by {device.get('manufacturer', 'Unknown')}")
                    
                print("\n  Storage devices:")
                storage_devices = usb.get_storage_devices()
                if storage_devices:
                    for i, device in enumerate(storage_devices):
                        print(f"    {i+1}. {device.get('name', 'Unknown')} - {device.get('mountPoint', 'Not mounted')}")
                else:
                    print("    No storage devices found.")
            else:
                print("  USB handler not available.")
        else:
            print("Platform initialization failed.")
    else:
        print(f"Platform '{platform.system()}' is not supported.")
    
if __name__ == "__main__":
    main()
