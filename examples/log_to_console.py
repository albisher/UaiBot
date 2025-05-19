#!/usr/bin/env python3
# filepath: /Users/amac/Documents/code/UaiBot/log_to_console.py
import sys
import os
import json
import datetime
import platform

def log_implementation_needed(user_input, details):
    """
    Log directly to console and to a file in current directory.
    This ensures we have a record regardless of permission issues.
    """
    # Create a log entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "user_input": user_input,
        "command": None,
        "status": "implementation_needed",
        "details": details,
        "os": platform.system(),
        "shell": os.environ.get('SHELL', '/bin/bash').split('/')[-1]
    }
    
    # Convert to JSON string
    log_string = json.dumps(log_entry)
    
    # Always print to console 
    print("\n🔴 IMPLEMENTATION NEEDED 🔴")
    print(f"📝 User Input: '{user_input}'")
    print(f"📝 Details: {details}")
    print(f"📝 Full log entry: {log_string}")
    
    # Try to write to a log file in the current directory
    try:
        with open('implementation_needed.log', 'a') as f:
            f.write(log_string + '\n')
        print(f"✅ Log written to {os.path.abspath('implementation_needed.log')}")
    except Exception as e:
        print(f"❌ Could not write to log file: {str(e)}")

# Direct usage example
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python log_to_console.py 'user_input' 'details'")
        sys.exit(1)
        
    user_input = sys.argv[1]
    details = sys.argv[2]
    log_implementation_needed(user_input, details)
    print("Log complete.")
