#!/usr/bin/env python3
import os
import subprocess
import time

def get_project_paths():
    """
    Get the paths to the test_files directory and project root.
    
    Returns:
        tuple: (test_files_dir, project_dir)
    """
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # test_files dir
    project_dir = os.path.dirname(current_dir)
    return current_dir, project_dir

def run_uaibot_command(request, use_safe_mode=False, pipe_yes=False):
    """
    Run a UaiBot command and return the results.
    
    Args:
        request (str): The request to pass to UaiBot
        use_safe_mode (bool): Whether to use safe mode or not
        pipe_yes (bool): Whether to pipe 'y' to the command for confirmations
        
    Returns:
        tuple: (stdout, stderr, returncode)
    """
    _, project_dir = get_project_paths()
    
    try:
        if pipe_yes:
            # Use echo y to pipe 'y' to the confirmation prompt
            flags = "--no-safe-mode" if not use_safe_mode else ""
            cmd = f"echo y | python {os.path.join(project_dir, 'main.py')} -f {flags} -c \"{request}\""
            print(f"Command: {cmd}")
            process = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        else:
            cmd = ["python", os.path.join(project_dir, "main.py"), "-f"]
            if not use_safe_mode:
                cmd.append("--no-safe-mode")
            cmd.extend(["-c", request])
            print(f"Command: {' '.join(cmd)}")
            process = subprocess.run(cmd, text=True, capture_output=True)
        
        return process.stdout, process.stderr, process.returncode
    except Exception as e:
        return f"Error: {str(e)}", "", 1

def check_file_created(filepath):
    """
    Check if a file was created and print information about it.
    
    Args:
        filepath (str): The path to the file
        
    Returns:
        bool: Whether the file exists
    """
    if os.path.exists(filepath):
        print(f"✅ File exists: {filepath}")
        file_size = os.path.getsize(filepath)
        print(f"   File size: {file_size} bytes")
        return True
    else:
        print(f"❌ File does not exist: {filepath}")
        return False
