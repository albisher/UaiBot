#!/usr/bin/env python3
"""
Interactive test script for the output formatter.
Provides a human-like testing experience by simulating real user interactions.
"""

import os
import sys
import time
import random
from src.contextlib import contextmanager

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from test_files.output_formatter import TestOutputFormatter

@contextmanager
def simulate_user_delay(min_delay=0.3, max_delay=1.0):
    """Simulate human-like delay between operations."""
    yield
    time.sleep(random.uniform(min_delay, max_delay))

def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    os.system('cls' if os.name == 'nt' else 'clear')

def interactive_formatter_test():
    """Run an interactive test of the formatter with simulated user behavior."""
    clear_screen()
    print("Starting interactive formatter test...\n")
    
    with simulate_user_delay():
        formatter = TestOutputFormatter()
        
    print("Testing basic formatting capabilities...\n")
    with simulate_user_delay():
        header = formatter.format_header("File Operation Test", "file")
        print(header)
    
    with simulate_user_delay():
        print(formatter.format_status("Checking test directory", "info"))
    
    with simulate_user_delay():
        print(formatter.format_status("Creating test files", "info"))
        
    # Simulate file operations with thinking box
    test_files = ["config.yaml", "data.json", "script.py"]
    
    for file in test_files:
        formatter.reset_output_status()
        with simulate_user_delay(1.0, 2.0):
            formatter.print_thinking_box(f"Processing file: {file}\nChecking file integrity...")
        
        # Random success/failure for demonstration
        success = random.choice([True, False])
        with simulate_user_delay():
            formatter.print_result(
                "success" if success else "error",
                f"{'Successfully processed' if success else 'Failed to process'} {file}"
            )
    
    # Test command output formatting
    with simulate_user_delay(1.0, 1.5):
        print("\nTesting command output formatting:")
        cmd_output = formatter.format_command_output(
            "python -m unittest discover",
            "...\nRan 12 tests in 0.123s\n\nOK",
            "",
            0
        )
        print(cmd_output)
    
    # Test box formatting
    with simulate_user_delay():
        print("\nTesting box formatting:")
        content = "This is a test of the box formatter.\nIt should properly format multiple lines.\nAnd maintain spacing."
        box = formatter.format_box(content, "Test Results")
        print(box)
    
    # Display platform info
    with simulate_user_delay():
        platform_info = formatter.get_platform_info()
        print("\nPlatform Information:")
        for key, value in platform_info.items():
            print(f"  {key.capitalize()}: {value}")
    
    print("\nInteractive test completed!")

if __name__ == "__main__":
    interactive_formatter_test()
