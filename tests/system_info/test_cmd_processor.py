import sys
import os
sys.path.insert(0, os.path.abspath('.'))  # Add current directory to path

# Import our modified command processor from the root directory
from command_processor import CommandProcessor
from uaibot.core.shell_handler import ShellHandler

# Mock AI Handler for testing, now with JSON and structured responses
class MockAIHandler:
    def get_ai_response(self, prompt):
        print(f"AI prompt received, length: {len(prompt)} chars")
        
        # Extract the user request from the prompt
        if "USER REQUEST:" in prompt:
            request = prompt.split("USER REQUEST:", 1)[1].split("\n")[0].strip().lower()
        else:
            request = prompt.lower()
        
        # Return appropriate response based on the request
        if "file" in request or "document" in request:
            # Return a JSON-formatted response
            return """```json
{
  "command": "find ~/Documents -type f -name \"*.*\" | head -n 10",
  "explanation": "This command searches for files in your Documents directory and shows the first 10 results",
  "alternatives": ["ls ~/Documents | head -n 10"],
  "requires_implementation": false
}
```"""
        elif "search" in request and "ai" in request:
            # Return a code block formatted response
            return """```shell
find ~ -name "*AI*" -o -path "*/*AI*/*" -type f 2>/dev/null | head -n 10
```"""
        elif "disk" in request or "storage" in request or "space" in request:
            # Return a simple command without formatting 
            return """To check disk usage, you can run:
df -h
This will show disk space usage in a human-readable format."""
        elif "optimize" in request or "performance" in request:
            # Return an error response in JSON format
            return """```json
{
  "error": true,
  "error_message": "System optimization requires administrator privileges and custom configuration",
  "requires_implementation": true
}
```"""
        else:
            # Return a fallback command
            return """I'll help with that.

```shell
ls -la
```

This will show all files in the current directory, including hidden ones."""
    
    def query_ai(self, prompt):
        # Add this method to maintain compatibility
        return self.get_ai_response(prompt)

# Create instances
ai_handler = MockAIHandler()
shell_handler = ShellHandler()
cmd_processor = CommandProcessor(ai_handler, shell_handler, quiet_mode=False)

# Test commands
test_requests = [
    "what files do I have",
    "search for documents about AI",
    "show me my disk usage"
]

# Process each test request
for request in test_requests:
    print("\n" + "="*50)
    print(f"PROCESSING: '{request}'")
    print("="*50)
    result = cmd_processor.process_command(request)
    print(f"\nRESULT:\n{result}\n")

# Try an unknown command that should be logged
print("\n" + "="*50)
print("PROCESSING: 'optimize my system for gaming'")
print("="*50)
result = cmd_processor.process_command("optimize my system for gaming")
print(f"\nRESULT:\n{result}\n")

# Check if implementation log was created
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
implementation_log = os.path.join(logs_dir, 'implementation_needed.log')

if os.path.exists(implementation_log):
    print(f"✅ Implementation log created at: {implementation_log}")
    # Get the last line of the log
    with open(implementation_log, 'r') as f:
        log_lines = f.readlines()
        if log_lines:
            print(f"Last log entry: {log_lines[-1].strip()}")
        else:
            print("Log file exists but is empty")
else:
    print(f"❌ Implementation log not found at: {implementation_log}")
