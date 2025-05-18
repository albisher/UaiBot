import sys
import os
sys.path.insert(0, os.path.abspath('.'))  # Add current directory to path

# Import our modified command processor from the root directory
from command_processor import CommandProcessor
from core.shell_handler import ShellHandler

# Mock AI Handler for testing
class MockAIHandler:
    def get_ai_response(self, prompt):
        print(f"AI prompt received, length: {len(prompt)} chars")
        
        # Extract the user request from the prompt
        if "User request:" in prompt:
            request = prompt.split("User request:", 1)[1].split("'")[1].lower()
        else:
            request = prompt.lower()
        
        # Return appropriate command based on the request
        if "file" in request or "document" in request:
            return """```shell
find ~/Documents -type f -name "*.*" | head -n 10
```"""
        elif "search" in request and "ai" in request:
            return """```shell
find ~ -name "*AI*" -o -path "*/*AI*/*" -type f 2>/dev/null | head -n 10
```"""
        elif "disk" in request or "storage" in request or "space" in request:
            return """```shell
df -h
```"""
        else:
            return """```shell
ls -la
```"""
    
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

print("\nTest completed successfully.")
