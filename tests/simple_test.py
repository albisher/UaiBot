#!/usr/bin/env python3
import os
import sys

# Add examples to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "examples"))

print("Python path:", sys.path)
print("Checking directories:")
print("- examples exists:", os.path.exists("examples"))
print("- examples/example_command_processor.py exists:", 
      os.path.exists("examples/example_command_processor.py"))
print("- terminal_commands exists:", os.path.exists("terminal_commands"))
print("- terminal_commands/enhanced_output_processor.py exists:",
      os.path.exists("terminal_commands/enhanced_output_processor.py"))

# Import the module we created
try:
    from terminal_commands.enhanced_output_processor import EnhancedOutputProcessor
    print("Successfully imported EnhancedOutputProcessor")
    
    # Create an instance
    processor = EnhancedOutputProcessor()
    print("Created processor instance")
    
    # Test it
    result = processor.process_uptime("14:30 up 2 days, 3:45, 3 users, load average: 0.52, 0.58, 0.59")
    print("Test result:", result)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
