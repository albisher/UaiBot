#!/usr/bin/env python3
"""
Basic Output Formatter Demo

A simple demonstration of the basic output formatter with different themes.
"""

import os
import sys
import time

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import our formatter
from utils.basic_output_formatter import BasicOutputFormatter

def demo_theme(theme):
    """Demonstrate a specific theme"""
    formatter = BasicOutputFormatter(theme=theme)
    
    divider = "=" * 70
    print(f"\n{divider}")
    print(f"Theme: {theme}")
    print(f"{divider}")
    
    # Show header
    print(formatter.format_header("System Status", "robot"))
    
    # Show status messages
    print(formatter.format_status("Database connection established", "success"))
    print(formatter.format_status("Memory usage approaching limit (85%)", "warning"))
    print(formatter.format_status("Network connection lost", "error"))
    
    # Show a box with content
    content = "CPU: 45% utilization\nRAM: 3.2GB/8GB used\nDisk: 120GB free"
    print("\n" + formatter.format_box(content, title="System Resources"))
    
    # Show a list
    print("\n" + formatter.format_header("Connected Devices", "computer"))
    devices = [
        "Arduino Mega (COM3)",
        "Webcam C920 (active)",
        "External USB Drive (mounted)"
    ]
    print(formatter.format_list(devices))
    
    # Show command output processing
    status_json = """{"hostname":"example-host","uptime":"3 days","cpu":"24%","warnings":["Battery low"]}"""
    print("\n" + formatter.process_command_output("status", status_json))

def main():
    """Main function to run the demo"""
    print("Basic Output Formatter Demo")
    print("Using simplified theming engine for UaiBot output\n")
    
    # Test each theme
    themes = ["default", "minimal", "professional"]
    for theme in themes:
        demo_theme(theme)
        time.sleep(0.5)  # Brief pause between themes
    
    print("\nDemo completed!")

if __name__ == "__main__":
    main()
