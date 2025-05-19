import sys
import os
sys.path.insert(0, os.path.abspath('.'))  # Add current directory to path

from command_processor import CommandProcessor
from core.shell_handler import ShellHandler

# Create a mock AI handler that always fails to generate a command
class FailingAIHandler:
    def get_ai_response(self, prompt):
        # Return error in a format that our improved system recognizes
        return "I'm sorry, I cannot generate a command for this request because it requires system-level optimization which is not safely achievable through a single command.\n\nERROR: System optimization requires multiple specialized commands and custom configuration."
    
    def query_ai(self, prompt):
        return self.get_ai_response(prompt)

# Set up the processor with our failing AI handler
ai_handler = FailingAIHandler()
shell_handler = ShellHandler()
cmd_processor = CommandProcessor(ai_handler, shell_handler, quiet_mode=False)

# Process a request that should be logged as needing implementation
print("Processing unknown command that should be logged...")
result = cmd_processor.process_command("optimize my system for ultra performance")
print(f"\nRESULT:\n{result}\n")

# Check if logs directory exists and has been updated
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
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

print("\nTest completed.")
