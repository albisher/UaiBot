#!/usr/bin/env python3
"""
UaiBot Audio Handler Test Script
Tests audio recording and playback functionality across platforms
"""
import os
import sys
import time
import platform as sys_platform
from uaibot.datetime import datetime

# Get the project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Add the project root to the Python path
sys.path.append(os.path.dirname(PROJECT_ROOT))

# Define colors for better terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Import the platform manager to get the appropriate audio handler
try:
    from uaibot.platform_uai.platform_manager import PlatformManager
except ImportError as e:
    print(f"{RED}Error importing platform modules: {e}{RESET}")
    print(f"Make sure you're running this script from the UaiBot project root.")
    sys.exit(1)

def print_header(text):
    """Print a formatted header"""
    width = 80
    print("\n" + BLUE + BOLD + "=" * width)
    print(text.center(width))
    print("=" * width + RESET + "\n")

def print_step(text):
    """Print a step in the test process"""
    print(YELLOW + f"➤ {text}" + RESET)

def print_result(success, message=""):
    """Print the test result"""
    if success:
        print(GREEN + "✅ PASSED" + RESET, end=" ")
    else:
        print(RED + "❌ FAILED" + RESET, end=" ")
    if message:
        print(message)
    print()

def test_list_audio_devices(audio_handler):
    """Test listing audio devices"""
    print_step("Testing list_audio_devices()")
    try:
        devices = audio_handler.list_audio_devices()
        success = isinstance(devices, list)
        
        if success:
            print_result(True, f"Found {len(devices)} audio device(s)")
            for i, device in enumerate(devices):
                print(f"  {i+1}. {device.get('name', 'Unknown')} - "
                      f"Inputs: {device.get('maxInputChannels', 0)}, "
                      f"Outputs: {device.get('maxOutputChannels', 0)}")
        else:
            print_result(False, "Failed to get audio devices list")
        
        return success
    except Exception as e:
        print_result(False, f"Error listing audio devices: {str(e)}")
        return False

def test_audio_recording(audio_handler):
    """Test audio recording functionality"""
    print_step("Testing audio recording")
    
    try:
        # Create a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_filename = f"test_recording_{timestamp}.wav"
        
        print_step(f"Recording 3 seconds of audio to {test_filename}")
        print("Please make some noise for the mic...")
        
        # Start recording
        result = audio_handler.record_audio(seconds=3, filename=test_filename)
        
        # Check if recording was successful
        if result and os.path.exists(result):
            success = True
            file_size = os.path.getsize(result)
            print_result(True, f"Successfully recorded audio ({file_size} bytes) to {result}")
            return True, result
        else:
            print_result(False, "Failed to record audio")
            return False, None
    except Exception as e:
        print_result(False, f"Error during audio recording: {str(e)}")
        return False, None

def test_audio_playback(audio_handler, audio_file):
    """Test audio playback functionality"""
    print_step(f"Testing audio playback with {os.path.basename(audio_file)}")
    
    try:
        # Pause a bit before playing
        time.sleep(1)
        
        print_step("Playing back the recorded audio...")
        result = audio_handler.play_audio(audio_file)
        
        if result:
            print_result(True, "Audio playback completed successfully")
        else:
            print_result(False, "Audio playback failed")
        
        return result
    except Exception as e:
        print_result(False, f"Error during audio playback: {str(e)}")
        return False

def main():
    """Run the audio tests"""
    print_header("UaiBot Audio Handler Tests")
    
    # Print platform info
    system_platform = sys_platform.system()
    print(f"System Platform: {system_platform}")
    
    # Initialize the platform manager
    platform_mgr = PlatformManager()
    
    if not platform_mgr.platform_supported:
        print(f"{RED}Error: Unsupported platform: {system_platform}{RESET}")
        return False
    
    # Initialize and get the audio handler
    print_step("Initializing platform manager")
    if not platform_mgr.initialize():
        print(f"{RED}Error: Failed to initialize platform manager{RESET}")
        return False
        
    # Get the audio handler
    print_step(f"Getting audio handler for platform: {platform_mgr.platform_name}")
    audio_handler = platform_mgr.get_audio_handler()
    
    if not audio_handler:
        print(f"{RED}Error: No audio handler available for {platform_mgr.platform_name}{RESET}")
        return False
        
    print(f"Using {audio_handler.__class__.__name__}")
    
    # Run the tests and track results
    test_results = []
    
    # Test listing audio devices
    devices_result = test_list_audio_devices(audio_handler)
    test_results.append(("List Audio Devices", devices_result))
    
    # Test audio recording
    recording_result, audio_file = test_audio_recording(audio_handler)
    test_results.append(("Audio Recording", recording_result))
    
    # Test audio playback if recording was successful
    if recording_result and audio_file:
        playback_result = test_audio_playback(audio_handler, audio_file)
        test_results.append(("Audio Playback", playback_result))
        
        # Clean up the test file
        try:
            if os.path.exists(audio_file):
                print_step(f"Cleaning up test file: {audio_file}")
                os.remove(audio_file)
        except Exception as e:
            print(f"{YELLOW}Warning: Could not remove test file: {str(e)}{RESET}")
    
    # Print summary
    print_header("Audio Test Results")
    all_passed = True
    
    for test_name, result in test_results:
        if result:
            print(f"{GREEN}✅ {test_name}: PASSED{RESET}")
        else:
            print(f"{RED}❌ {test_name}: FAILED{RESET}")
            all_passed = False
    
    if all_passed:
        print(f"\n{GREEN}🎉 All audio tests passed!{RESET}")
    else:
        print(f"\n{RED}⚠️ Some audio tests failed. Please review the output above.{RESET}")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
