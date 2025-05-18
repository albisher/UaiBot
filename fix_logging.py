#!/usr/bin/env python3
# filepath: /Users/amac/Documents/code/UaiBot/fix_logging.py
import os
import json
import sys
import datetime
from pathlib import Path

def ensure_log_dirs():
    """Create and validate log directories using multiple methods"""
    log_dirs_to_try = [
        # Main project directory logs
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'),
        # Home directory logs
        os.path.join(os.path.expanduser('~'), '.uaibot', 'logs'),
        # /tmp directory logs - should be universally writable
        os.path.join('/tmp', 'uaibot_logs') if sys.platform != 'win32' else os.path.join(
            os.environ.get('TEMP', 'C:\\Temp'), 'uaibot_logs'),
    ]
    
    success = False
    for log_dir in log_dirs_to_try:
        try:
            print(f"Attempting to create log directory: {log_dir}")
            os.makedirs(log_dir, exist_ok=True)
            
            # Test if directory is writable by attempting to create a test file
            test_file = os.path.join(log_dir, '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            
            # Check if we can read the file
            with open(test_file, 'r') as f:
                content = f.read()
                if content != 'test':
                    raise ValueError(f"Content verification failed: {content}")
            
            # Clean up test file
            os.remove(test_file)
            
            # Update the command_patterns.json with the verified log directory
            update_config_with_log_dir(log_dir)
            
            print(f"✅ Successfully configured log directory: {log_dir}")
            success = True
            break
        except Exception as e:
            print(f"❌ Error with log directory {log_dir}: {str(e)}")
    
    if not success:
        print("CRITICAL: Unable to create any log directories")
        return None
    
    return log_dir

def update_config_with_log_dir(log_dir):
    """Update the config file with the verified log directory"""
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'settings.json')
    
    try:
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # Load existing config or create new one
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update the log directory
        config['log_directory'] = log_dir
        
        # Save the config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Updated config file with log directory: {log_dir}")
    except Exception as e:
        print(f"Error updating config file: {str(e)}")

def create_test_logs(log_dir):
    """Create test log entries in the specified directory"""
    try:
        # Create log file paths
        command_log = os.path.join(log_dir, 'command_requests.log')
        implementation_log = os.path.join(log_dir, 'implementation_needed.log')
        unknown_log = os.path.join(log_dir, 'unknown_commands.log')
        
        # Create a test log entry
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "user_input": "test command",
            "command": None,
            "status": "implementation_needed",
            "details": "TEST: This is a test log entry created by fix_logging.py",
            "os": sys.platform,
            "shell": os.environ.get('SHELL', 'unknown').split('/')[-1] if sys.platform != 'win32' else 'cmd.exe'
        }
        
        # Write to all log files
        with open(command_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        with open(implementation_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        with open(unknown_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"✅ Test logs created successfully in {log_dir}")
        
        # Show log contents
        for log_file in [command_log, implementation_log, unknown_log]:
            print(f"\n{os.path.basename(log_file)} content:")
            with open(log_file, 'r') as f:
                print(f.read().strip())
        
        return True
    except Exception as e:
        print(f"❌ Error creating test logs: {str(e)}")
        return False

if __name__ == "__main__":
    print("UaiBot Logging System Repair\n")
    log_dir = ensure_log_dirs()
    if log_dir:
        create_test_logs(log_dir)
        print("\nLogging system repair complete.")
    else:
        print("\nLogging system repair FAILED.")
