#!/usr/bin/env python3
import os
import subprocess
import time
import sys

# Import our output formatter
from src.output_formatter import format_header, format_status, format_command_output, format_box

def main():
    print(format_header("Running UaiBot file operation tests...", "info"))
    
    # Get the base directory of the project
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    
    # Path to the test requests file
    requests_file = os.path.join(current_dir, 'ai_human_requests.txt')
    
    # Check if the requests file exists
    if not os.path.exists(requests_file):
        print(format_status(f"Error: Test requests file not found at {requests_file}", "error"))
        return
    
    # Read the test requests
    with open(requests_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Execute each valid request
    for line in lines:
        line = line.strip()
        # Skip empty lines, comments, and section headers
        if not line or line.startswith('#') or line.startswith('//'):
            continue
            
        print("\n" + "="*80)
        print(format_status(f"Executing request: {line}", "info"))
        print("="*80)
        
        # Execute the request using main.py with the -f flag
        try:
            # Handle different types of commands
            if "Delete" in line or "احذف" in line:
                # Use yes confirmation via echo
                cmd = f"echo y | python {os.path.join(project_dir, 'main.py')} -f -c \"{line}\""
                print(f"Command: {cmd}")
                process = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            elif any(term in line.lower() for term in ["image", "sound", "circle", "صورة", "دائرة", "صوتي"]):
                # Always use --no-safe-mode for media operations
                cmd = ["python", os.path.join(project_dir, "main.py"), "-f", "--no-safe-mode", "-c", line]
                cmd_str = ' '.join(cmd)
                process = subprocess.run(cmd, text=True, capture_output=True)
            elif "Display all files" in line or "List" in line:
                # Using the command that was successful in terminal output
                cmd = ["python", os.path.join(project_dir, "main.py"), "-f", "-c", line]
                cmd_str = ' '.join(cmd)
                process = subprocess.run(cmd, text=True, capture_output=True)
            else:
                # Regular command execution
                cmd = ["python", os.path.join(project_dir, "main.py"), "-f", "-c", line]
                cmd_str = ' '.join(cmd)
                process = subprocess.run(cmd, text=True, capture_output=True)
            
            # Format and print the command output (only once)
            print(format_command_output(
                cmd if isinstance(cmd, str) else cmd_str,
                process.stdout,
                process.stderr,
                process.returncode
            ))
            
            # Check for errors and try alternative approach if needed
            if "Error" in process.stdout and "--no-safe-mode" not in str(cmd):
                print("\n" + format_status("Detected error, retrying with --no-safe-mode flag...", "warning"))
                if isinstance(cmd, list):
                    new_cmd = cmd.copy()
                    if "-f" in new_cmd:
                        new_cmd.insert(new_cmd.index("-f") + 1, "--no-safe-mode")
                    else:
                        new_cmd.append("--no-safe-mode")
                    new_cmd_str = ' '.join(new_cmd)
                    retry_process = subprocess.run(new_cmd, text=True, capture_output=True)
                    print(format_command_output(
                        new_cmd_str,
                        retry_process.stdout,
                        retry_process.stderr,
                        retry_process.returncode
                    ))
            
            # Small delay between commands to see results better
            time.sleep(1)
        
        except Exception as e:
            print(format_status(f"Error executing command: {e}", "error"))
    
    print("\n" + format_status("All file operation tests completed.", "success"))

if __name__ == "__main__":
    main()
