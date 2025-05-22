#!/usr/bin/env python3
# filepath: /Users/amac/Documents/code/UaiBot/test_unknown_cmd_improved.py
import sys
import os
import json
import platform
sys.path.insert(0, os.path.abspath('.'))  # Add current directory to path

from app.command_processor.CommandProcessor import CommandProcessor
from app.core.shell_handler import ShellHandler

# Create a mock AI handler that properly simulates an error response
class ImprovedFailingAIHandler:
    def __init__(self):
        self.attempts = 0
    
    def get_ai_response(self, prompt):
        self.attempts += 1
        # On first attempt, return a clear error with no code block
        if self.attempts == 1:
            return """I'm unable to generate a command for system optimization as it requires multiple specialized steps.

ERROR: System optimization requires multiple specialized commands and configuration changes that cannot be done with a single command.
"""
        # On second attempt (retry), still return an error but with useful information
        else:
            return """I apologize, but I can't provide a single command for this. System optimization involves:

1. Analyzing performance bottlenecks
2. Adjusting system settings 
3. Potentially installing specialized software

ERROR: This complex operation cannot be automated with a single shell command safely.
"""
    
    def query_ai(self, prompt):
        return self.get_ai_response(prompt)

# Set up the processor with our improved failing AI handler
ai_handler = ImprovedFailingAIHandler()
shell_handler = ShellHandler()
cmd_processor = CommandProcessor(ai_handler, shell_handler, quiet_mode=False)

def check_logs():
    """Check all possible log locations for implementation logs"""
    log_dirs_to_check = [
        # Current directory logs
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'),
        # Home directory logs
        os.path.join(os.path.expanduser('~'), '.uaibot', 'logs'),
        # /tmp directory logs
        os.path.join('/tmp', 'uaibot_logs') if platform.system() != 'Windows' else 
        os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'uaibot_logs')
    ]
    
    for log_dir in log_dirs_to_check:
        implementation_log = os.path.join(log_dir, 'implementation_needed.log')
        if os.path.exists(implementation_log):
            print(f"✅ Implementation log found at: {implementation_log}")
            with open(implementation_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    latest_entry = json.loads(lines[-1])
                    print(f"Last log entry: {lines[-1].strip()}")
                    # Check if this is our test entry
                    if "optimize my system" in latest_entry.get("user_input", ""):
                        print("✅ Found our test entry in logs!")
                        return True
    
    print("❌ Test entry not found in any implementation log")
    return False

# Process a request that should be logged as needing implementation
print("=" * 50)
print("Testing unknown command handling")
print("=" * 50)
print("Processing unknown command: 'optimize my system for ultra performance'")
result = cmd_processor.process_command("optimize my system for ultra performance")

print(f"\nRESULT:\n{result}\n")

# Check if our test entry is in the logs
print("Checking logs...")
found = check_logs()

print("\n" + "=" * 50)
print(f"Test {'PASSED' if found else 'FAILED'}")
print("=" * 50)
