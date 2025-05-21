#!/usr/bin/env python3

import os
import sys
import platform
import json

# Import the utility functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uaibot.utils import run_command

# Create a simplified version of the command processor's extract_command_from_ai_response function
def extract_command_from_ai_response(ai_response):
    """Extract a command from the AI response."""
    if not ai_response:
        return None
        
    # Handle error responses
    if ai_response.startswith("ERROR:"):
        print(f"AI returned error: {ai_response}")
        return None
    
    # Check for code blocks
    import re
    code_block_pattern = r'```(?:bash|shell|zsh|sh|console|terminal)?\s*(.*?)\s*```'
    code_blocks = re.findall(code_block_pattern, ai_response, re.DOTALL)
    
    if code_blocks:
        command = code_blocks[0].strip()
        command_lines = [line.strip() for line in command.split('\n') 
                         if line.strip() and not line.strip().startswith('#')]
        if command_lines:
            return command_lines[0]
    
    print("No command could be extracted")
    return None

# Process test with various AI responses
def test_extraction():
    print("\n=== Testing Command Extraction ===\n")
    
    test_cases = [
        # Should work - properly formatted code block
        """Here's the command to list files:
```shell
ls -la
```""",
        
        # Should work - code block with multiple lines
        """You can use this:
```shell
# List files with details
ls -la
# This is a comment
```""",
        
        # Should fail - error response
        "ERROR: I cannot perform this action",
        
        # Test with backticks
        "Use the command `find ~ -name \"*.py\"` to find Python files",
        
        # Test with command phrase
        "You can run: df -h to check disk space"
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"Test {i+1}:")
        print(f"AI response: {test_case}")
        command = extract_command_from_ai_response(test_case)
        print(f"Extracted command: {command}")
        print()

# Test execution on real OS
def test_execution():
    print("\n=== Testing Command Execution ===\n")
    
    test_commands = [
        "ls -la",
        "df -h",
        "find ~ -name \"*.py\" -maxdepth 2 | head -n 5",
        "ERROR: Cannot execute this"
    ]
    
    for i, command in enumerate(test_commands):
        print(f"Test {i+1}:")
        print(f"Command: {command}")
        
        # Skip commands that start with ERROR:
        if command.startswith("ERROR:"):
            print("Skipping execution - command is an error message")
            continue
        
        result = run_command(command, shell=True, capture_output=True, text=True)
        if result['success']:
            print(f"Success! Output (truncated):")
            output_lines = result['stdout'].strip().split('\n')
            print('\n'.join(output_lines[:5]))
            if len(output_lines) > 5:
                print(f"... and {len(output_lines) - 5} more lines")
        else:
            print(f"Failed: {result['stderr']}")
        print()

if __name__ == "__main__":
    print(f"Running tests on: {platform.system()} {platform.release()}")
    test_extraction()
    test_execution()
    print("Tests completed!")
