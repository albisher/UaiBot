#!/usr/bin/env python3
"""
UaiBot Terminal Command Test Script
Tests UaiBot's ability to handle all terminal commands listed in enhancements2.txt
"""
import os
import sys
import subprocess
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

try:
    from app.core.shell_handler import ShellHandler
    from app.core.screen_handler.session_manager import ScreenSessionHandler
except ImportError as e:
    print(f"{RED}Error importing modules: {e}{RESET}")
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

def get_command_groups():
    """Return groups of commands to test"""
    # These commands are structured based on enhancements2.txt
    return {
        "File Navigation": [
            "pwd",
            "ls",
            "ls -a",
            "ls -l",
            "cd ..",
            "cd ~",
        ],
        "Directory Management": [
            "mkdir test_dir",
            "rmdir test_dir",
        ],
        "File Operations": [
            "touch test_file.txt",
            "echo 'Hello UaiBot' > test_file.txt",
            "cat test_file.txt",
            "cp test_file.txt test_file2.txt",
            "mv test_file2.txt test_file_renamed.txt",
            "rm test_file.txt",
            "rm test_file_renamed.txt",
        ],
        "System Information": [
            "date",
            "cal",
            "uptime",
            "df -h",
            "du -sh .",
        ]
    }

def test_local_commands(shell_handler):
    """Test execution of terminal commands locally"""
    print_header("Testing Local Terminal Commands")
    
    command_groups = get_command_groups()
    results = {}
    
    for group_name, commands in command_groups.items():
        print_step(f"Testing {group_name} Commands")
        group_results = []
        
        for command in commands:
            if command in ["rmdir test_dir", "cat test_file.txt", "cp test_file.txt test_file2.txt", 
                          "mv test_file2.txt test_file_renamed.txt", "rm test_file.txt", "rm test_file_renamed.txt"]:
                # Skip commands that depend on previous commands' success to avoid errors
                continue
                
            try:
                print_step(f"Executing: {command}")
                result = shell_handler.execute_command(command)
                
                # Check if command execution was successful
                success = result != "Command execution failed"
                print_result(success, result[:100] + "..." if len(result) > 100 else result)
                group_results.append((command, success))
            except Exception as e:
                print_result(False, f"Error executing {command}: {str(e)}")
                group_results.append((command, False))
        
        # Calculate group success rate
        successful = sum(1 for _, success in group_results if success)
        total = len(group_results)
        results[group_name] = {
            "commands": group_results,
            "success_rate": successful / total if total > 0 else 0
        }
    
    # Run the dependent commands in sequence
    print_step("Testing Command Sequences")
    sequence_test_success = test_command_sequence(shell_handler)
    
    # Print summary
    print_header("Local Command Test Summary")
    for group_name, data in results.items():
        success_rate = data["success_rate"] * 100
        if success_rate == 100:
            print(f"{GREEN}✅ {group_name}: 100% ({len(data['commands'])} commands){RESET}")
        elif success_rate > 75:
            print(f"{YELLOW}⚠️ {group_name}: {success_rate:.1f}% ({int(success_rate * len(data['commands']) / 100)}/{len(data['commands'])} commands){RESET}")
        else:
            print(f"{RED}❌ {group_name}: {success_rate:.1f}% ({int(success_rate * len(data['commands']) / 100)}/{len(data['commands'])} commands){RESET}")
    
    if sequence_test_success:
        print(f"{GREEN}✅ Command Sequences: PASSED{RESET}")
    else:
        print(f"{RED}❌ Command Sequences: FAILED{RESET}")
    
    # Calculate overall success
    total_commands = sum(len(data["commands"]) for data in results.values())
    total_successful = sum(int(data["success_rate"] * len(data["commands"])) for data in results.values())
    overall_success_rate = total_successful / total_commands if total_commands > 0 else 0
    
    return overall_success_rate > 0.8 and sequence_test_success

def test_command_sequence(shell_handler):
    """Test a sequence of commands that depend on each other"""
    print_step("Testing a sequence of dependent commands")
    
    try:
        # Create test directory
        print_step("1. Creating test directory")
        result = shell_handler.execute_command("mkdir -p test_sequence_dir")
        directory_success = "Command execution failed" not in result
        print_result(directory_success, result[:100] if len(result) > 100 else result)
        
        if not directory_success:
            return False
        
        # Create a test file
        print_step("2. Creating test file")
        result = shell_handler.execute_command("echo 'This is a test file' > test_sequence_dir/test_file.txt")
        file_created = "Command execution failed" not in result
        print_result(file_created, result[:100] if len(result) > 100 else result)
        
        if not file_created:
            return False
        
        # Check file content
        print_step("3. Reading file content")
        result = shell_handler.execute_command("cat test_sequence_dir/test_file.txt")
        content_correct = "This is a test file" in result
        print_result(content_correct, result)
        
        if not content_correct:
            return False
        
        # Copy file
        print_step("4. Copying file")
        result = shell_handler.execute_command("cp test_sequence_dir/test_file.txt test_sequence_dir/test_file2.txt")
        copy_success = "Command execution failed" not in result
        print_result(copy_success, result[:100] if len(result) > 100 else result)
        
        # Clean up
        print_step("5. Cleaning up")
        clean_result = shell_handler.execute_command("rm -r test_sequence_dir")
        clean_success = "Command execution failed" not in clean_result
        print_result(clean_success, clean_result[:100] if len(clean_result) > 100 else clean_result)
        
        return all([directory_success, file_created, content_correct, copy_success, clean_success])
        
    except Exception as e:
        print_result(False, f"Error during command sequence: {str(e)}")
        return False

def test_screen_session_commands(screen_handler):
    """Test execution of terminal commands in a screen session"""
    print_header("Testing Screen Session Terminal Commands")
    
    # Check if screen exists
    if not screen_handler.check_screen_exists():
        print(f"{YELLOW}Warning: No screen sessions found. Screen command tests will be skipped.{RESET}")
        print("To test with screen sessions, start a screen session first with:")
        print("  screen -S uaibot_test")
        return False
    
    # Get screen sessions
    sessions = screen_handler.get_screen_sessions()
    if not sessions or not sessions.get('all'):
        print(f"{YELLOW}Warning: No screen sessions available{RESET}")
        return False
    
    session_id = sessions['all'][0]  # Use the first available session
    print_step(f"Using screen session: {session_id}")
    
    # Test a subset of commands in the screen session
    test_commands = [
        "pwd",
        "ls -la",
        "echo 'Hello from screen session'",
        "date"
    ]
    
    success_count = 0
    for command in test_commands:
        print_step(f"Sending to screen: {command}")
        result = screen_handler.send_to_screen(command, session_id=session_id)
        command_success = "sent to screen session" in result
        print_result(command_success, result)
        if command_success:
            success_count += 1
    
    success_rate = success_count / len(test_commands)
    print_step(f"Screen command success rate: {success_rate * 100:.1f}%")
    
    return success_rate >= 0.75  # Consider successful if at least 75% of commands work

def main():
    """Run the terminal command tests"""
    print_header("UaiBot Terminal Command Tests")
    
    # Print platform info
    system_platform = sys_platform.system()
    print(f"System Platform: {system_platform}")
    
    # Initialize handlers
    print_step("Initializing Shell Handler")
    shell_handler = ShellHandler(safe_mode=False)
    
    print_step("Initializing Screen Session Handler")
    screen_handler = ScreenSessionHandler(quiet_mode=False)
    
    # Run the tests
    local_success = test_local_commands(shell_handler)
    screen_success = test_screen_session_commands(screen_handler)
    
    # Print overall summary
    print_header("Terminal Command Test Results")
    
    if local_success:
        print(f"{GREEN}✅ Local Terminal Commands: PASSED{RESET}")
    else:
        print(f"{RED}❌ Local Terminal Commands: FAILED{RESET}")
    
    if screen_success:
        print(f"{GREEN}✅ Screen Session Commands: PASSED{RESET}")
    elif screen_handler.check_screen_exists():
        print(f"{RED}❌ Screen Session Commands: FAILED{RESET}")
    else:
        print(f"{YELLOW}⚠️ Screen Session Commands: SKIPPED (No screen sessions found){RESET}")
    
    overall_success = local_success and (screen_success or not screen_handler.check_screen_exists())
    
    if overall_success:
        print(f"\n{GREEN}🎉 Terminal command tests completed successfully!{RESET}")
    else:
        print(f"\n{RED}⚠️ Some terminal command tests failed. Please review the output above.{RESET}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
