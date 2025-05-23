#!/usr/bin/env python3
import os
import subprocess

# Import our output formatter
from uaibot.output_formatter import format_header, format_status, format_command_output, format_box

def main():
    """
    Script to fix and test the 'list files' operation for UaiBot.
    This demonstrates proper commands for listing files in a directory.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    
    print("\n" + "="*80)
    print(format_header("Testing improved file listing for the test_files directory", "folder"))
    print("="*80)
    
    # Use a direct command that works as seen in terminal output
    request = "Display all files in test_files"
    
    try:
        cmd = ["python", os.path.join(project_dir, "main.py"), "-f", "-c", request]
        cmd_str = ' '.join(cmd)
        print(f"Testing command: {cmd_str}")
        process = subprocess.run(cmd, text=True, capture_output=True)
        
        # Print results using our formatter (just once)
        print(format_command_output(
            cmd_str,
            process.stdout,
            process.stderr,
            process.returncode
        ))
        
        # Get reference output from system ls command for comparison
        print("\nReference output from system ls command:")
        try:
            ref_output = subprocess.run(["ls", "-la", current_dir], text=True, capture_output=True)
            print(ref_output.stdout)
        except Exception:
            print("Could not get reference output.")
        
        print("-" * 80)
    
    except Exception as e:
        print(format_status(f"Error executing command: {e}", "error"))

if __name__ == "__main__":
    main()
