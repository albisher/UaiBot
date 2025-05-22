#!/usr/bin/env python3
"""
UaiBot Camera/Vision Handler Test Script
Tests camera detection and access functionality
"""
import os
import sys
import time
import platform as sys_platform

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

# Import the platform manager to get the appropriate USB handler
try:
    from app.platform_uai.platform_manager import PlatformManager
except ImportError as e:
    print(f"{RED}Error importing platform modules: {e}{RESET}")
    print(f"Make sure you're running this script from the UaiBot project root.")
    sys.exit(1)

# Try to import cv2 for camera handling
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

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

def test_detect_camera_devices():
    """Test detection of camera/webcam devices"""
    print_step("Testing detection of camera/webcam devices")
    
    if not CV2_AVAILABLE:
        print_result(False, "OpenCV (cv2) is not available. Cannot detect cameras.")
        print("To install OpenCV: pip install opencv-python")
        return False, []
        
    # On most systems, cameras are indexed starting from 0
    max_cameras_to_check = 5  # Check up to 5 possible camera indices
    detected_cameras = []
    
    for idx in range(max_cameras_to_check):
        try:
            print_step(f"Checking for camera at index {idx}...")
            cap = cv2.VideoCapture(idx)
            
            if cap.isOpened():
                # Read a frame to verify it's working
                ret, frame = cap.read()
                if ret:
                    # Get camera properties
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    
                    camera_info = {
                        'index': idx,
                        'width': width,
                        'height': height,
                        'fps': fps
                    }
                    detected_cameras.append(camera_info)
                    print_result(True, f"Camera found at index {idx}: {width}x{height} @ {fps}fps")
                else:
                    print_result(False, f"Could not read frame from camera at index {idx}")
                    
                # Release the camera
                cap.release()
            else:
                print(f"No camera at index {idx}")
        except Exception as e:
            print_result(False, f"Error checking camera index {idx}: {str(e)}")
    
    if detected_cameras:
        print_result(True, f"Detected {len(detected_cameras)} camera(s)")
        return True, detected_cameras
    else:
        print_result(False, "No cameras detected")
        return False, []

def test_camera_capture(camera_index=0):
    """Test capturing a frame from the camera"""
    print_step(f"Testing camera capture from index {camera_index}")
    
    if not CV2_AVAILABLE:
        print_result(False, "OpenCV (cv2) is not available. Cannot capture from camera.")
        return False
        
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print_result(False, f"Failed to open camera {camera_index}")
            return False
            
        # Try to read a frame
        print_step("Reading a frame from camera...")
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print_result(False, "Failed to capture frame")
            cap.release()
            return False
            
        # Get frame properties
        height, width = frame.shape[:2]
        print_result(True, f"Captured frame: {width}x{height}")
        
        # Save the frame to a file for verification
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(PROJECT_ROOT, f"camera_test_{timestamp}.jpg")
        
        cv2.imwrite(output_path, frame)
        print_result(True, f"Saved test image to: {output_path}")
        
        # Release the camera
        cap.release()
        
        return True
    except Exception as e:
        print_result(False, f"Error during camera capture: {str(e)}")
        return False

def test_usb_camera_devices(usb_handler):
    """Test detection of USB camera devices using the USB handler"""
    print_step("Testing USB camera detection via USB handler")
    
    if not usb_handler:
        print_result(False, "No USB handler available")
        return False
        
    try:
        # Get all USB devices
        devices = usb_handler.get_device_list()
        
        # Filter for potential camera devices
        camera_keywords = ['camera', 'webcam', 'video', 'capture', 'logitech', 'microsoft', 'facetime']
        
        camera_devices = []
        for device in devices:
            product = str(device.get('product', '')).lower()
            manufacturer = str(device.get('manufacturer', '')).lower()
            
            if any(keyword in product or keyword in manufacturer for keyword in camera_keywords):
                camera_devices.append(device)
        
        if camera_devices:
            print_result(True, f"Found {len(camera_devices)} potential camera device(s) via USB")
            for i, device in enumerate(camera_devices):
                print(f"  {i+1}. {device.get('product', 'Unknown')} - "
                      f"Manufacturer: {device.get('manufacturer', 'Unknown')}")
            return True
        else:
            print(f"No camera devices found among {len(devices)} USB devices")
            return False
    except Exception as e:
        print_result(False, f"Error detecting USB camera devices: {str(e)}")
        return False

def main():
    """Run the camera/vision tests"""
    print_header("UaiBot Camera/Vision Handler Tests")
    
    # Print platform info
    system_platform = sys_platform.system()
    print(f"System Platform: {system_platform}")
    
    # Check for OpenCV
    if not CV2_AVAILABLE:
        print(f"{YELLOW}Warning: OpenCV (cv2) is not installed. Some tests will be skipped.{RESET}")
        print("To install OpenCV: pip install opencv-python")
    else:
        print(f"OpenCV version: {cv2.__version__}")
    
    # Initialize the platform manager
    platform_mgr = PlatformManager()
    
    if not platform_mgr.platform_supported:
        print(f"{RED}Error: Unsupported platform: {system_platform}{RESET}")
        return False
    
    # Initialize and get the USB handler
    print_step("Initializing platform manager")
    if not platform_mgr.initialize():
        print(f"{RED}Error: Failed to initialize platform manager{RESET}")
        return False
        
    # Get the USB handler
    print_step(f"Getting USB handler for platform: {platform_mgr.platform_name}")
    usb_handler = platform_mgr.get_usb_handler()
    
    # Run the tests and track results
    test_results = []
    
    # Test camera detection
    camera_detected, camera_list = test_detect_camera_devices()
    test_results.append(("Camera Detection", camera_detected))
    
    # Test camera capture if cameras were detected
    if camera_detected and camera_list:
        capture_result = test_camera_capture(camera_list[0]['index'])
        test_results.append(("Camera Capture", capture_result))
    
    # Test USB camera detection through USB handler
    if usb_handler:
        usb_camera_result = test_usb_camera_devices(usb_handler)
        test_results.append(("USB Camera Detection", usb_camera_result))
    else:
        print(f"{YELLOW}Warning: No USB handler available. USB camera detection skipped.{RESET}")
    
    # Print summary
    print_header("Camera Test Results")
    all_passed = True
    tests_run = 0
    
    for test_name, result in test_results:
        if result:
            print(f"{GREEN}✅ {test_name}: PASSED{RESET}")
            tests_run += 1
        else:
            print(f"{RED}❌ {test_name}: FAILED{RESET}")
            all_passed = False
            tests_run += 1
    
    if all_passed and tests_run > 0:
        print(f"\n{GREEN}🎉 All camera tests passed!{RESET}")
    elif tests_run == 0:
        print(f"\n{YELLOW}⚠️ No camera tests were able to run. Please check requirements.{RESET}")
        all_passed = False
    else:
        print(f"\n{RED}⚠️ Some camera tests failed. Please review the output above.{RESET}")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
