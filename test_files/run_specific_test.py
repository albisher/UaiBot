#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    # Get the base directory of the project
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    
    # Check if a command was provided as an argument
    if len(sys.argv) < 2:
        print("Usage: python run_specific_test.py \"your file operation request here\"")
        return
    
    # Get the request from command line arguments
    request = " ".join(sys.argv[1:])
    
    print("\n" + "="*80)
    print(f"Executing request: {request}")
    print("="*80)
    
    # Execute the request using main.py with the -f flag
    try:
        # Determine if special handling is needed
        if any(word in request.lower() for word in ["delete", "remove", "احذف"]):
            # Use echo y to pipe 'y' to the confirmation prompt and --no-safe-mode for deletion
            cmd = f"echo y | python {os.path.join(project_dir, 'main.py')} -f --no-safe-mode -c \"{request}\""
            print(f"Command: {cmd}")
            
            # Execute with shell=True to allow piping
            process = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        elif any(word in request.lower() for word in ["image", "sound", "picture", "audio", "صورة", "صوتي", "beep", "circle", "دائرة", "صفارة"]):
            # Use --no-safe-mode for media file creation with expanded keyword detection
            cmd = ["python", os.path.join(project_dir, "main.py"), "-f", "--no-safe-mode", "-c", request]
            print(f"Command: {' '.join(cmd)}")
            process = subprocess.run(cmd, text=True, capture_output=True)
        elif any(word in request.lower() for word in ["list", "show", "display", "ls", "dir"]):
            # Special handling for listing files
            cmd = ["python", os.path.join(project_dir, "main.py"), "-f", "-c", request]
            print(f"Command: {' '.join(cmd)}")
            
            # Also run direct ls command for debugging
            if "test_files" in request:
                print("Running direct ls command for comparison:")
                ls_cmd = f"ls -la {os.path.join(project_dir, 'test_files')}"
                subprocess.run(ls_cmd, shell=True)
            
            process = subprocess.run(cmd, text=True, capture_output=True)
        else:
            # Regular command execution
            cmd = ["python", os.path.join(project_dir, "main.py"), "-f", "-c", request]
            print(f"Command: {' '.join(cmd)}")
            process = subprocess.run(cmd, text=True, capture_output=True)
        
        # Print results
        print("\nSTDOUT:")
        print(process.stdout)
        
        if process.stderr:
            print("\nSTDERR:")
            print(process.stderr)
        
        print(f"Exit code: {process.returncode}")
    
    except Exception as e:
        print(f"Error executing command: {e}")

if __name__ == "__main__":
    main()
