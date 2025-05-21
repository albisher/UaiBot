#!/usr/bin/env python3
# filepath: /Users/amac/Documents/code/UaiBot/test_unknown_cmd_fixed.py
import sys
import os
sys.path.insert(0, os.path.abspath('.'))  # Add current directory to path

from command_processor import CommandProcessor
from core.shell_handler import ShellHandler

# Create a mock AI handler that always fails to generate a command
class FailingAIHandler:
    def get_ai_response(self, prompt):
        # Format matches what our code looks for when extracting commands
        return """I'm sorry, I cannot generate an executable command for this request.

ERROR: System optimization requires specialized tools and multiple configuration changes that cannot be done with a single command.
"""
    
    def query_ai(self, prompt):
        return self.get_ai_response(prompt)

# Set up the processor with our failing AI handler
ai_handler = FailingAIHandler()
shell_handler = ShellHandler()
cmd_processor = CommandProcessor(ai_handler, shell_handler, quiet_mode=False)

def ensure_logs_dir():
    """Create logs directory and make it writable"""
    try:
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Check if directory is writable
        if not os.access(logs_dir, os.W_OK):
            print(f"Making logs directory writable: {logs_dir}")
            os.chmod(logs_dir, 0o777)
            
        return logs_dir
    except Exception as e:
        print(f"Error creating logs directory: {e}")
        return None

# Ensure logs directory exists and is writable
logs_dir = ensure_logs_dir()
if not logs_dir:
    print("Failed to create logs directory. Test cannot continue.")
    sys.exit(1)

# Process a request that should be logged as needing implementation
print("Processing unknown command that should be logged...")
result = cmd_processor.process_command("optimize my system for ultra performance")
print(f"\nRESULT:\n{result}\n")

# Check if implementation log exists and has been updated
implementation_log = os.path.join(logs_dir, 'implementation_needed.log')

if os.path.exists(implementation_log):
    print(f"✅ Implementation log created at: {implementation_log}")
    # Get the last line of the log
    with open(implementation_log, 'r') as f:
        lines = f.readlines()
        if lines:
            print(f"Last log entry: {lines[-1].strip()}")
else:
    print(f"❌ Implementation log not created at: {implementation_log}")

# Also check the command_requests.log file as a fallback
command_log = os.path.join(logs_dir, 'command_requests.log')
if os.path.exists(command_log):
    print(f"✅ Command requests log created at: {command_log}")
    # Get the last line of the log
    with open(command_log, 'r') as f:
        lines = f.readlines()
        if lines:
            print(f"Last log entry: {lines[-1].strip()}")
else:
    print(f"❌ Command requests log not created at: {command_log}")

print("\nTest completed.")
