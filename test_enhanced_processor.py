#!/usr/bin/env python3
"""
Simple test for the enhanced output processor.
"""

import os
import sys

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.append(project_root)

# Debug information
print(f"Current directory: {current_dir}")
print(f"Project root: {project_root}")
print(f"Files in terminal_commands:")
try:
    files = os.listdir(os.path.join(project_root, "terminal_commands"))
    for file in files:
        print(f"  - {file}")
except Exception as e:
    print(f"Error listing files: {e}")

# Try importing the enhanced output processor
try:
    from terminal_commands.enhanced_output_processor import EnhancedOutputProcessor
    
    # Create instance with default theme
    processor = EnhancedOutputProcessor()
    print("Successfully created processor with default theme\n")
    
    # Test some basic processing
    print("Testing uptime processing:")
    print(processor.process_uptime("14:30 up 2 days, 3:45, 3 users, load average: 0.52, 0.58, 0.59"))
    
    print("\nTesting system status processing:")
    status_data = """{
        "hostname": "example-host",
        "uptime": "2 days, 3:45",
        "cpu_usage": "32%",
        "memory_available": "4.5 GB",
        "disk_space_free": "120GB",
        "network_status": "Connected",
        "warnings": ["Memory usage high", "Software update available"],
        "errors": []
    }"""
    print(processor.process_system_status(status_data))
    
    # Try switching themes
    print("\nSwitching to minimal theme:")
    processor.style_mgr.set_theme("minimal")
    print(processor.process_uptime("14:30 up 2 days, 3:45, 3 users, load average: 0.52, 0.58, 0.59"))
    
    print("\nTesting completed successfully!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
