#!/usr/bin/env python3
import os
import sys
from examples.example_command_processor import ExampleCommandProcessor

# Create the processor
processor = ExampleCommandProcessor()

# Test a few commands
commands = ["help", "status", "disk", "uptime", "theme minimal", "status", "theme default"]

for cmd in commands:
    print(f"\n> {cmd}")
    result = processor.process_command(cmd)
    print(result)

print("\nTesting completed!")
