#!/usr/bin/env python3
"""
Test script for enhanced shell command handling.
Tests various command patterns for screen session and local execution.
"""
import sys
import os
import subprocess
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.shell_handler import ShellHandler

def test_screen_commands():
    """Test screen session command handling"""
    shell = ShellHandler(safe_mode=False)
    
    print("=== Testing Screen Session Commands ===")
    
    # Test if screen exists (we'll need this for proper test behavior)
    try:
        result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
        screen_output = result.stdout + result.stderr
        screen_exists = "No Sockets found" not in screen_output
    except Exception:
        screen_exists = False
        
    if not screen_exists:
        print("No screen sessions found. Some tests will be skipped.")
        print("To fully test, first start a screen session with:\n  screen /dev/cu.usbmodem* 115200")
        return
        
    # Basic command test - these should work with screen sessions
    print("\nSending basic navigation commands to screen session:")
    commands = [
        "pwd",
        "ls",
        "ls -la",
        "echo 'Hello from screen session'",
        "date"
    ]
    
    for cmd in commands:
        print(f"\nTesting command: {cmd}")
        result = shell.send_to_screen_session(cmd)
        print(f"Result: {result}")
    
    # Test commands with wildcards and special characters
    print("\nSending commands with wildcards to screen session:")
    commands = [
        "ls *.txt",
        "find . -name '*.py'"
    ]
    
    for cmd in commands:
        print(f"\nTesting command: {cmd}")
        result = shell.send_to_screen_session(cmd)
        print(f"Result: {result}")
    
def test_complex_commands():
    """Test complex command handling"""
    shell = ShellHandler(safe_mode=False)
    
    print("\n=== Testing Complex Command Execution ===")
    
    # Commands with redirects and pipes
    print("\nTesting commands with redirects and pipes:")
    commands = [
        "ls | grep py",
        "echo 'test' > /tmp/test_uaibot.txt",
        "cat /tmp/test_uaibot.txt"
    ]
    
    for cmd in commands:
        print(f"\nTesting command: {cmd}")
        result = shell.execute_command(cmd)
        print(f"Result: {result}")
        
    # Clean up
    shell.execute_command("rm /tmp/test_uaibot.txt")

def test_command_detection():
    """Test if commands are properly detected for screen vs local"""
    shell = ShellHandler(safe_mode=False)
    
    print("\n=== Testing Command Target Detection ===")
    
    commands_and_contexts = [
        ("ls", ""), # Simple command with no context
        ("ls", "on the screen session"),  # With screen context
        ("top", ""),  # Interactive command
        ("cat file.txt", ""),  # File operation
        ("ping google.com", ""),  # Network command
        ("reboot", "on the device"),  # System command with device context
    ]
    
    for cmd, ctx in commands_and_contexts:
        print(f"\nCommand: '{cmd}' with context: '{ctx}'")
        target = shell.detect_command_target(cmd, ctx)
        print(f"Detected target: {target}")

def test_wifi_speed_detection():
    """Test the enhanced Wi-Fi speed detection"""
    import platform
    import re
    
    system_platform = platform.system().lower()
    print("\n=== Testing Enhanced Wi-Fi Speed Detection ===")
    
    if system_platform == 'darwin':
        try:
            speed_info = {}
            
            # Test Method 1: Apple's airport utility
            print("Testing airport utility method...")
            airport = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            try:
                out = subprocess.check_output([airport, "-I"], text=True)
                tx_match = re.search(r"lastTxRate: (\d+)", out)
                if tx_match:
                    speed = int(tx_match.group(1))
                    speed_info['tx_rate'] = speed
                    print(f"✓ Successfully detected TX rate: {speed} Mbps")
                else:
                    print("✗ Could not detect TX rate")
                
                rssi_match = re.search(r"agrCtlRSSI: (-?\d+)", out)
                if rssi_match:
                    rssi = int(rssi_match.group(1))
                    speed_info['signal_strength'] = rssi
                    print(f"✓ Successfully detected signal strength: {rssi} dBm")
                else:
                    print("✗ Could not detect signal strength")
            except Exception as e:
                print(f"✗ Error accessing airport utility: {e}")
            
            # Test Method 2: networksetup
            print("\nTesting networksetup method...")
            try:
                out = subprocess.check_output(["networksetup", "-getinfo", "Wi-Fi"], text=True)
                speed_match = re.search(r"Speed: (\d+)", out)
                if speed_match:
                    link_speed = int(speed_match.group(1))
                    speed_info['link_speed'] = link_speed
                    print(f"✓ Successfully detected link speed: {link_speed} Mbps")
                else:
                    print("✗ Could not detect link speed")
            except Exception as e:
                print(f"✗ Error using networksetup: {e}")
                
            # Print summary
            print("\nWi-Fi Speed Detection Summary:")
            if speed_info:
                for key, value in speed_info.items():
                    print(f"- {key}: {value}")
            else:
                print("No Wi-Fi information could be detected")
                
        except Exception as e:
            print(f"Error during Wi-Fi speed detection test: {e}")
    else:
        print(f"Skipping Wi-Fi speed test on non-macOS platform: {system_platform}")

def test_usb_device_detection():
    """Test enhanced USB device detection"""
    print("\n=== Testing USB Device Detection ===")
    shell = ShellHandler()
    
    # Test the new USB device detection method
    print("Detecting USB devices:")
    devices = shell.get_usb_devices()
    print(devices)
    
    # Also test direct command approach for comparison
    import platform
    system_platform = platform.system().lower()
    print("\nComparing with direct command approach:")
    if system_platform == 'darwin':
        try:
            result = subprocess.run(['ls', '/dev/cu.*'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Direct command results:\n{result.stdout}")
            else:
                print("Direct command failed")
        except Exception as e:
            print(f"Error running direct command: {e}")
    else:
        print(f"Skipping direct command test on non-macOS platform: {system_platform}")
        
    print("\nUSB Device Detection Test Complete")

def main():
    """Run all tests"""
    print("Starting UaiBot enhanced shell command tests\n")
    
    test_command_detection()
    test_complex_commands()
    test_screen_commands()
    test_wifi_speed_detection()
    test_usb_device_detection()
    
    print("\nTests complete!")

if __name__ == "__main__":
    main()
