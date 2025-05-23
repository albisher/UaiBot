#!/usr/bin/env python3
# Test script for UaiBot command processor
# Tests the direct execution and intent mapping functionality

import os
import sys
import platform
from unittest.mock import Mock
from uaibot.core.command_processor import CommandProcessor

class MockAIHandler:
    """Simple mock AI handler for testing."""
    def get_ai_response(self, prompt):
        # Return a command in code block format as per our expectations
        if "search" in prompt.lower() or "find" in prompt.lower():
            return "```shell\nfind ~ -name \"*.py\" -type f | head -n 5\n```"
        elif "weather" in prompt.lower():
            return "```shell\ncurl wttr.in\n```"
        elif "uptime" in prompt.lower() or "running" in prompt.lower():
            return "```shell\nuptime\n```"
        else:
            return "```shell\necho 'Command processed via AI'\n```"
            
    # Add any other methods that the command processor might expect
    def query_ai(self, *args, **kwargs):
        return self.get_ai_response("Default prompt")

class MockShellHandler:
    """Simple mock shell handler for testing."""
    def execute_command(self, command):
        return (0, f"Mock execution of: {command}", "")
        
    # Add methods that the command processor expects to call
    def find_folders(self, *args, **kwargs):
        return ["~/Documents", "~/Downloads"]
        
    def find_files(self, *args, **kwargs):
        return ["~/file1.txt", "~/file2.py"]
        
    def search_content(self, *args, **kwargs):
        return ["~/file1.txt: matching content", "~/file2.py: matching content"]

def test_command_processor():
    """Test the command processor functionality."""
    print("Testing UaiBot Command Processor")
    print(f"System: {platform.system()} {platform.release()}")
    print("-" * 60)
    
    # Create mock handlers
    ai_handler = MockAIHandler()
    shell_handler = MockShellHandler()
    
    # Create processor with mock handlers
    processor = CommandProcessor(ai_handler, shell_handler)
    
    # Test cases to verify direct execution and intent mapping
    test_commands = [
        # Commands that should be directly executed
        "ls",
        "find . -name *.py",
        "open Safari",
        # Natural language requests that should be mapped to commands
        "show me all Python files",
        "search for important documents",
        "how long has my system been running",
        "open the Notes app",
        "what's in my Documents folder",
        "show me all processes",
        # Commands that should be handled by AI
        "what's the weather like",
        "tell me a joke",
        "create a bash script that counts files"
    ]
    
    # Run tests
    results = []
    for cmd in test_commands:
        print(f"\nTesting: \"{cmd}\"")
        try:
            result = processor.execute_command(cmd)
            success = "✅" if result["status"] == "success" else "❌"
            results.append((cmd, success, result))
            print(f"  {success} Result: {str(result)[:100]}{'...' if len(str(result)) > 100 else ''}")
        except Exception as e:
            results.append((cmd, "❌", f"Error: {str(e)}"))
            print(f"  ❌ Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    success_count = sum(1 for _, status, _ in results if status == "✅")
    print(f"Passed: {success_count}/{len(results)}")
    
    # Print failures
    failures = [(cmd, result) for cmd, status, result in results if status != "✅"]
    if failures:
        print("\nFailed commands:")
        for cmd, result in failures:
            print(f"- \"{cmd}\": {str(result)[:100]}{'...' if len(str(result)) > 100 else ''}")
    
if __name__ == "__main__":
    try:
        test_command_processor()
        print("\nTest script completed successfully!")
        print("If no error messages were displayed, the command processor is working as expected.")
        print("Remember to test the actual integration with real user input.")
    except Exception as e:
        print(f"\nTest script failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
