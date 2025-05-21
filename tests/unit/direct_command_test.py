#!/usr/bin/env python3
import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_files.utils.test_helper import run_uaibot_command, check_file_created

def main():
    """
    Utility to test a single UaiBot command from the command line.
    """
    if len(sys.argv) < 2:
        print("Usage: python direct_command_test.py \"your command here\" [--no-safe-mode]")
        return
    
    # Get command and flags
    request = sys.argv[1]
    use_safe_mode = "--no-safe-mode" not in sys.argv
    
    print("\n" + "="*80)
    print(f"Testing command: {request}")
    print("="*80)
    
    # Run the command
    stdout, stderr, returncode = run_uaibot_command(request, use_safe_mode)
    
    # Print results
    print("\nSTDOUT:")
    print(stdout)
    
    if stderr:
        print("\nSTDERR:")
        print(stderr)
    
    print(f"Exit code: {returncode}")
    
    # If there was an error and we used safe mode, try again without safe mode
    if "Error" in stdout and use_safe_mode:
        print("\n" + "="*80)
        print("Retrying with --no-safe-mode...")
        print("="*80)
        
        stdout, stderr, returncode = run_uaibot_command(request, False)
        
        print("\nSTDOUT:")
        print(stdout)
        
        if stderr:
            print("\nSTDERR:")
            print(stderr)
        
        print(f"Exit code: {returncode}")

if __name__ == "__main__":
    main()
