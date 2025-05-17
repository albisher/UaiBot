#!/usr/bin/env python3
# filepath: /Users/amac/Documents/code/UaiBot/demo_run_command.py
"""
Demo script showing how to use the run_command utility to execute terminal commands.
This interactive script allows users to try different command execution methods.
"""
import os
import sys
import time

from core.utils import run_command

def print_separator(title=""):
    """Print a separator line with an optional title"""
    width = 60
    if title:
        print("\n" + "=" * 10 + f" {title} " + "=" * (width - 12 - len(title)))
    else:
        print("\n" + "=" * width)
        
def run_demo_command(command, **kwargs):
    """Run a command and display its results in a formatted way"""
    print(f"\nExecuting: {command}")
    if kwargs:
        print(f"Options: {kwargs}")
        
    result = run_command(command, **kwargs)
    
    if isinstance(result, dict):  # Synchronous execution
        print(f"Return code: {result['returncode']}")
        print(f"Success: {'✅ YES' if result['success'] else '❌ NO'}")
        
        if result.get('stdout'):
            print("\nOutput:")
            output_lines = result['stdout'].strip().split("\n")
            if len(output_lines) > 10:
                for line in output_lines[:5]:
                    print(f"  {line}")
                print("  ...[output truncated]...")
                for line in output_lines[-5:]:
                    print(f"  {line}")
            else:
                for line in output_lines:
                    print(f"  {line}")
                    
        if result.get('stderr') and result['stderr'].strip():
            print("\nErrors:")
            print(f"  {result['stderr']}")
            
    else:  # Asynchronous execution (Popen object)
        print("Asynchronous process started. Gathering output...")
        stdout, stderr = result.communicate()
        print(f"Return code: {result.returncode}")
        print(f"Success: {'✅ YES' if result.returncode == 0 else '❌ NO'}")
        if stdout:
            print("\nOutput:")
            print(f"  {stdout.strip()}")
        if stderr:
            print("\nErrors:")
            print(f"  {stderr.strip()}")
            
def main_menu():
    """Show the main menu and handle user choice"""
    while True:
        print_separator("UaiBot run_command Demo")
        print("\nChoose a demo to run:")
        print("1. Basic command execution")
        print("2. Execute a command with arguments")
        print("3. Run a command with environment variables")
        print("4. Execute a command asynchronously")
        print("5. Run a command with timeout")
        print("6. Enter your own command")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '0':
            print("\nExiting demo. Goodbye!")
            break
        elif choice == '1':
            basic_command_demo()
        elif choice == '2':
            arguments_demo()
        elif choice == '3':
            env_vars_demo()
        elif choice == '4':
            async_demo()
        elif choice == '5':
            timeout_demo()
        elif choice == '6':
            custom_command_demo()
        else:
            print("\n❌ Invalid choice. Please try again.")

def basic_command_demo():
    """Demonstrate basic command execution"""
    print_separator("Basic Command Demo")
    run_demo_command("ls -la")
    run_demo_command("uname -a")
    run_demo_command("echo 'Hello from UaiBot!'")
    input("\nPress Enter to return to the main menu...")
    
def arguments_demo():
    """Demonstrate command execution with arguments"""
    print_separator("Command with Arguments Demo")
    print("Running the same command using different argument styles:")
    
    # String form with shell=True (less secure)
    run_demo_command("echo Hello UaiBot argument test", shell=True)
    
    # List form (more secure)
    run_demo_command(["echo", "Hello", "UaiBot", "argument", "test"])
    
    print("\nCompare how special characters are treated:")
    filename = "test.txt; echo SECURITY_BREACH"
    
    # String form with shell=True (vulnerable to injection)
    print("\nUsing shell=True (potentially unsafe):")
    run_demo_command(f"ls {filename}", shell=True)
    
    # List form (safe from injection)
    print("\nUsing list form (safe):")
    run_demo_command(["ls", filename])
    
    input("\nPress Enter to return to the main menu...")
    
def env_vars_demo():
    """Demonstrate command execution with environment variables"""
    print_separator("Environment Variables Demo")
    
    # Create custom environment
    custom_env = os.environ.copy()
    custom_env["UAIBOT_DEMO_VAR"] = "This is a custom environment variable!"
    
    # Run command with custom environment
    run_demo_command("echo $UAIBOT_DEMO_VAR", shell=True, env=custom_env)
    
    # Show that the variable is not in the regular environment
    run_demo_command("echo $UAIBOT_DEMO_VAR", shell=True)
    
    input("\nPress Enter to return to the main menu...")
    
def async_demo():
    """Demonstrate asynchronous command execution"""
    print_separator("Asynchronous Execution Demo")
    
    print("Starting a command that will take 3 seconds to complete...")
    process = run_command("sleep 3; echo 'Long-running task completed!'", 
                        shell=True, async_mode=True, capture_output=True, text=True)
    
    print("\nDoing other work while the command runs...")
    for i in range(6):
        print(f"  Working... {i+1}/6")
        time.sleep(0.5)
        
    print("\nNow getting the result of the long-running command:")
    stdout, stderr = process.communicate()
    print(f"Command output: {stdout.strip() if stdout else 'No output'}")
    print(f"Command errors: {stderr.strip() if stderr and stderr.strip() else 'None'}")
    print(f"Exit code: {process.returncode}")
    
    input("\nPress Enter to return to the main menu...")
    
def timeout_demo():
    """Demonstrate command execution with timeout"""
    print_separator("Timeout Demo")
    
    print("Running a command with a 2-second timeout that should complete in time:")
    run_demo_command("sleep 1; echo 'Completed in time'", shell=True, timeout=2)
    
    print("\nRunning a command with a 1-second timeout that will time out:")
    run_demo_command("sleep 3; echo 'This should not be printed'", shell=True, timeout=1)
    
    input("\nPress Enter to return to the main menu...")
    
def custom_command_demo():
    """Let the user run their own custom command"""
    print_separator("Custom Command Demo")
    
    while True:
        command = input("\nEnter a command to run (or 'back' to return): ").strip()
        
        if command.lower() == 'back':
            break
            
        use_shell = input("Use shell=True? (y/n): ").strip().lower() == 'y'
        async_mode = input("Run asynchronously? (y/n): ").strip().lower() == 'y'
        capture = input("Capture output? (y/n, default=y): ").strip().lower() != 'n'
        
        if async_mode:
            process = run_command(command, shell=use_shell, async_mode=True, 
                                capture_output=capture, text=True)
            print("Process started. Press Enter when you want to get results...")
            input()
            stdout, stderr = process.communicate()
            print("\nResults:")
            print(f"Output: {stdout if stdout else 'None'}")
            print(f"Errors: {stderr if stderr else 'None'}")
            print(f"Exit code: {process.returncode}")
        else:
            run_demo_command(command, shell=use_shell)
            
        choice = input("\nTry another command? (y/n): ").strip().lower()
        if choice != 'y':
            break

if __name__ == "__main__":
    main_menu()
