#!/usr/bin/env python3
"""
Test script to verify the Note folder detection in UaiBot
"""
import os
import sys
import subprocess
import platform

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from core
from app.command_processor.command_processor import CommandProcessor
from app.core.shell_handler import ShellHandler
from app.core.ai_handler import AIHandler, get_system_info

def main():
    print("UaiBot Notes Folder Detection Test\n")
    print(f"System: {get_system_info()}")

    # Initialize components with quiet mode off for testing
    shell_handler = ShellHandler(safe_mode=True, quiet_mode=False)
    
    # Create a mock AI handler that just returns command suggestions
    class MockAIHandler:
        def query_ai(self, prompt):
            return "ls -la ~/Library/Containers/com.apple.Notes"
    
    ai_handler = MockAIHandler()
    
    # Initialize the command processor with quiet mode off
    command_processor = CommandProcessor(ai_handler, shell_handler, quiet_mode=False)
    
    # Test different folder detection variations
    print("\n===== TEST: Direct 'show me Notes folders' command =====")
    test_command(command_processor, "show me Notes folders I have")
    
    print("\n===== TEST: Direct 'show Notes' command =====")
    test_command(command_processor, "show Notes")
    
    print("\n===== TEST: Direct 'display my Notes' command =====")
    test_command(command_processor, "display my Notes")
    
    print("\n===== TEST: Direct 'where are my Notes' command =====")
    test_command(command_processor, "where are my Notes")
    
    print("\n===== TEST: Direct 'find Notes app' command =====")
    test_command(command_processor, "find Notes app")
    
    print("\nAll tests completed!")

def test_command(processor, command):
    print(f"Command: {command}")
    try:
        result = processor.process_command(command)
        print(f"\nResult:\n{result}")
        
        # Check if result contains expected content
        success = False
        if "Notes" in result and ("Apple Notes App" in result or "iCloud" in result or "found these folders" in result):
            success = True
            
        print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")
    except Exception as e:
        print(f"\n❌ Test FAILED with error: {str(e)}")
    
if __name__ == "__main__":
    main()
