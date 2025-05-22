#!/usr/bin/env python3
"""
UaiBot Screen Session Testing Script
Tests UaiBot's ability to interact with screen sessions using both screen_manager.py and session_manager.py
"""
import subprocess
import time
import os
import sys
import random
import string

# Define colors for better terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Get the project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Import the screen handler modules directly
sys.path.append(PROJECT_ROOT)
try:
    from app.core.screen_handler.screen_manager import ScreenManager
    from app.core.screen_handler.session_manager import ScreenSessionHandler
except ImportError as e:
    print(f"{RED}Error importing screen modules: {e}{RESET}")
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

def create_temp_file(content):
    """Create a temporary file with given content"""
    temp_filename = f"uaibot_test_{''.join(random.choices(string.ascii_lowercase, k=8))}.txt"
    temp_path = os.path.join(PROJECT_ROOT, temp_filename)
    
    with open(temp_path, 'w') as f:
        f.write(content)
    
    return temp_path

def create_screen_session(session_name="uaibot_test"):
    """Create a new screen session"""
    try:
        # Check if a session with this name already exists
        result = subprocess.run(
            ['screen', '-ls', session_name], 
            capture_output=True, 
            text=True
        )
        
        if session_name in result.stdout:
            print_step(f"Screen session '{session_name}' already exists")
            return True
            
        print_step(f"Creating screen session '{session_name}'")
        
        # Create a detached screen session
        subprocess.run(
            ['screen', '-dmS', session_name], 
            check=True
        )
        
        # Give it a moment to start
        time.sleep(1)
        
        # Verify it was created
        result = subprocess.run(
            ['screen', '-ls'], 
            capture_output=True, 
            text=True
        )
        
        if session_name in result.stdout:
            print_result(True, f"Created screen session '{session_name}'")
            return True
        else:
            print_result(False, f"Failed to create screen session '{session_name}'")
            return False
    except Exception as e:
        print_result(False, f"Error creating screen session: {e}")
        return False

def cleanup_screen_session(session_name="uaibot_test"):
    """Clean up the screen session"""
    try:
        print_step(f"Cleaning up screen session '{session_name}'")
        
        # Kill the screen session
        subprocess.run(
            ['screen', '-S', session_name, '-X', 'quit'], 
            capture_output=True
        )
        
        # Verify it was removed
        result = subprocess.run(
            ['screen', '-ls'], 
            capture_output=True, 
            text=True
        )
        
        if session_name not in result.stdout:
            print_result(True, f"Removed screen session '{session_name}'")
            return True
        else:
            print_result(False, f"Failed to remove screen session '{session_name}'")
            return False
    except Exception as e:
        print_result(False, f"Error cleaning up screen session: {e}")
        return False

def test_screen_manager():
    """Test the ScreenManager module"""
    print_header("Testing ScreenManager")
    
    session_name = "uaibot_test_manager"
    temp_file = create_temp_file("This is a test file for screen manager\n")
    temp_filename = os.path.basename(temp_file)
    
    # Create screen session
    if not create_screen_session(session_name):
        return False
    
    try:
        # Initialize the screen manager
        print_step("Initializing ScreenManager")
        manager = ScreenManager(quiet_mode=False)
        
        # Test listing sessions
        print_step("Testing list_sessions()")
        sessions = manager.list_sessions()
        session_found = any(session_name in s for s in sessions.keys())
        print_result(session_found, f"Sessions: {sessions}")
        
        # Test sending a command
        print_step(f"Testing send_command_to_session() - creating file in {temp_filename}")
        result = manager.send_command_to_session(f"echo 'Hello from ScreenManager' > {temp_filename}", session_id=session_name)
        print_result(True if "sent to screen session" in result else False, result)
        
        # Wait a moment for command to execute
        time.sleep(1)
        
        # Verify the file was created by the screen session
        print_step(f"Verifying file {temp_filename} was modified")
        if os.path.exists(temp_filename):
            with open(temp_filename, 'r') as f:
                content = f.read().strip()
            file_updated = "Hello from ScreenManager" in content
            print_result(file_updated, f"File content: {content}")
        else:
            print_result(False, f"File {temp_filename} not found")
        
        # Clean up
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        return session_found
    
    finally:
        # Cleanup screen session
        cleanup_screen_session(session_name)
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_session_handler():
    """Test the ScreenSessionHandler module"""
    print_header("Testing ScreenSessionHandler")
    
    session_name = "uaibot_test_handler"
    temp_file = create_temp_file("This is a test file for session handler\n")
    temp_filename = os.path.basename(temp_file)
    
    # Create screen session
    if not create_screen_session(session_name):
        return False
    
    try:
        # Initialize the session handler
        print_step("Initializing ScreenSessionHandler")
        handler = ScreenSessionHandler(quiet_mode=False)
        
        # Test checking if screen exists
        print_step("Testing check_screen_exists()")
        screen_exists = handler.check_screen_exists()
        print_result(screen_exists, f"Screen exists: {screen_exists}")
        
        # Test getting screen sessions
        print_step("Testing get_screen_sessions()")
        sessions = handler.get_screen_sessions()
        session_found = False
        if isinstance(sessions, dict) and 'all' in sessions:
            session_found = any(session_name in s for s in sessions['all'])
        print_result(session_found, f"Sessions: {sessions}")
        
        # Test sending a command
        print_step(f"Testing send_to_screen() - creating file in {temp_filename}")
        result = handler.send_to_screen(f"echo 'Hello from SessionHandler' > {temp_filename}", session_id=session_name)
        print_result(True if "sent to screen session" in result else False, result)
        
        # Wait a moment for command to execute
        time.sleep(1)
        
        # Verify the file was created by the screen session
        print_step(f"Verifying file {temp_filename} was modified")
        if os.path.exists(temp_filename):
            with open(temp_filename, 'r') as f:
                content = f.read().strip()
            file_updated = "Hello from SessionHandler" in content
            print_result(file_updated, f"File content: {content}")
        else:
            print_result(False, f"File {temp_filename} not found")
            
        # Test sending an interactive command
        print_step("Testing send_to_screen() with interactive command")
        result = handler.send_to_screen("top -n 1", session_id=session_name)
        interactive_handled = "interactive command" in result.lower()
        print_result(interactive_handled, result)
        
        # Clean up
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        return session_found and interactive_handled
    
    finally:
        # Cleanup screen session
        cleanup_screen_session(session_name)
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_arabic_commands():
    """Test sending Arabic commands to screen sessions"""
    print_header("Testing Arabic Commands in Screen Sessions")
    
    session_name = "uaibot_test_arabic"
    temp_file = create_temp_file("هذا ملف اختبار للأوامر العربية\n")
    temp_filename = os.path.basename(temp_file)
    
    # Create screen session
    if not create_screen_session(session_name):
        return False
    
    try:
        # Initialize handlers
        print_step("Initializing handlers")
        manager = ScreenManager(quiet_mode=False)
        handler = ScreenSessionHandler(quiet_mode=False)
        
        # Test sending Arabic command with ScreenManager
        print_step("Testing sending Arabic text with ScreenManager")
        arabic_text = "مرحبا من مدير الشاشة"
        result = manager.send_command_to_session(f"echo '{arabic_text}' > {temp_filename}", session_id=session_name)
        print_result(True if "sent to screen session" in result else False, result)
        
        # Wait a moment for command to execute
        time.sleep(1)
        
        # Verify Arabic text was written
        if os.path.exists(temp_filename):
            with open(temp_filename, 'r') as f:
                content = f.read().strip()
            print_result(arabic_text in content, f"ScreenManager Arabic content: {content}")
        else:
            print_result(False, f"File {temp_filename} not found")
        
        # Test sending Arabic command with SessionHandler
        print_step("Testing sending Arabic text with SessionHandler")
        arabic_text = "مرحبا من معالج الجلسة"
        result = handler.send_to_screen(f"echo '{arabic_text}' > {temp_filename}", session_id=session_name)
        print_result(True if "sent to screen session" in result else False, result)
        
        # Wait a moment for command to execute
        time.sleep(1)
        
        # Verify Arabic text was written
        if os.path.exists(temp_filename):
            with open(temp_filename, 'r') as f:
                content = f.read().strip()
            print_result(arabic_text in content, f"SessionHandler Arabic content: {content}")
        else:
            print_result(False, f"File {temp_filename} not found")
        
        # Clean up
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        return True
    
    finally:
        # Cleanup screen session
        cleanup_screen_session(session_name)
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    """Run all tests"""
    print_header("UaiBot Screen Session Testing")
    
    # Check if screen is installed
    try:
        subprocess.run(['screen', '--version'], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print(f"{RED}Error: 'screen' command not found. Please install screen first.{RESET}")
        return
    
    tests_results = []
    
    # Test the ScreenManager
    tests_results.append(("ScreenManager", test_screen_manager()))
    
    # Test the ScreenSessionHandler
    tests_results.append(("ScreenSessionHandler", test_session_handler()))
    
    # Test Arabic commands
    tests_results.append(("Arabic Commands", test_arabic_commands()))
    
    # Print summary
    print_header("Test Results")
    all_passed = True
    
    for test_name, result in tests_results:
        if result:
            print(f"{GREEN}✅ {test_name}: PASSED{RESET}")
        else:
            print(f"{RED}❌ {test_name}: FAILED{RESET}")
            all_passed = False
    
    if all_passed:
        print(f"\n{GREEN}🎉 All screen session tests passed!{RESET}")
    else:
        print(f"\n{RED}⚠️ Some tests failed. Please review the output above.{RESET}")

if __name__ == "__main__":
    main()
