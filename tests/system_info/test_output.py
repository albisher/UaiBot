#!/usr/bin/env python3
import os
import subprocess
import sys
import re
import argparse

def run_command_with_flags(command, flags=None):
    """
    Run a UaiBot command with specified flags.
    """
    # Get the project directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    
    # Build the command
    cmd = ["python", os.path.join(project_dir, "main.py")]
    if flags:
        cmd.extend(flags)
    cmd.extend(["-c", command])
    
    print("\n" + "="*80)
    print(f"Testing command: {command}")
    print(f"With flags: {' '.join(flags) if flags else 'None'}")
    print("="*80)
    
    # Execute the command
    process = subprocess.run(cmd, text=True, capture_output=True)
    
    print("\nSTDOUT:")
    print(process.stdout)
    
    if process.stderr:
        print("\nSTDERR:")
        print(process.stderr)
    
    print(f"\nExit code: {process.returncode}")
    
    return process

def analyze_output(stdout):
    """
    Analyze the output to check for duplicates.
    """
    # Count occurrences of typical output patterns
    thinking_count = len(re.findall(r"🤔 Thinking\.\.\.", stdout))
    command_count = len(re.findall(r"📌 I'll execute this command:", stdout))
    success_count = len(re.findall(r"✅", stdout))
    error_count = len(re.findall(r"❌", stdout))
    info_count = len(re.findall(r"ℹ️", stdout))
    
    print("\nOutput Analysis:")
    print(f"  Thinking messages: {thinking_count}")
    print(f"  Command execution messages: {command_count}")
    print(f"  Success messages: {success_count}")
    print(f"  Error messages: {error_count}")
    print(f"  Info messages: {info_count}")
    
    # Check for duplicates
    duplicate_detected = thinking_count > 1 or command_count > 1 or (success_count + error_count + info_count) > 1
    
    if duplicate_detected:
        print("❌ Duplicate outputs detected!")
    else:
        print("✅ Output format looks good!")

def main():
    parser = argparse.ArgumentParser(description='Test UaiBot output formatting')
    parser.add_argument('--command', '-c', type=str, default="Display all files in test_files",
                       help='Command to test')
    parser.add_argument('--flags', '-f', type=str, nargs='*', 
                       default=["-f", "--no-safe-mode"],
                       help='Flags to pass to UaiBot')
    args = parser.parse_args()
    
    # Run the command
    process = run_command_with_flags(args.command, args.flags)
    
    # Analyze the output
    analyze_output(process.stdout)

if __name__ == "__main__":
    main()
