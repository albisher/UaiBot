#!/usr/bin/env python3
"""
Example script demonstrating the output formatting utilities.
This shows how to create consistent, visually appealing command-line output
according to the UaiBot formatting guidelines.
"""

import os
import sys

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.append(project_root)

from utils.output_formatter import (
    EMOJI, format_header, format_table_row, format_box, 
    format_status_line, format_list, create_divider
)

def demo_system_report():
    """Demonstrate a system status report with consistent formatting"""
    print(format_header("UaiBot System Report", emoji=EMOJI["robot"]))
    
    # System status section
    print(format_header("System Status", emoji=EMOJI["stats"]))
    print(format_table_row("CPU", "45% utilization"))
    print(format_table_row("RAM", "3.2GB/8GB used"))
    print(format_table_row("Disk", "120GB free"))
    
    print("")  # Add spacing between sections
    
    # Connected devices section
    print(format_header("Connected Devices", emoji=EMOJI["mobile"]))
    devices = [
        {"name": "Arduino Mega", "status": "Connected", "port": "/dev/ttyACM0"},
        {"name": "Webcam C920", "status": "Available", "port": "/dev/video0"},
        {"name": "USB Drive", "status": "Mounted", "path": "/media/usb0"}
    ]
    
    for i, device in enumerate(devices):
        status_emoji = EMOJI["green"] if device["status"] in ["Connected", "Available", "Mounted"] else EMOJI["red"]
        print(f"{i+1}. {status_emoji} {device['name']}")
        if "port" in device:
            print(f"   │  Port: {device['port']}")
        if "path" in device:
            print(f"   │  Path: {device['path']}")
        print(f"   └  Status: {device['status']}")
        
    print("")  # Add spacing between sections
    
    # Recent commands in a box
    commands = [
        "ls -la",
        "git status",
        "python main.py --verbose"
    ]
    
    cmd_list = format_list(commands, bullet_type="number")
    print(format_box(f"Recent Commands:\n\n{cmd_list}", title="Command History"))
    
    # Add a tip at the end
    print(f"\n{EMOJI['tip']} Tip: Use 'uaibot help' to see available commands.")

def demo_error_message():
    """Demonstrate error message formatting"""
    print(f"\n{EMOJI['error']} Error: Unable to connect to device\n")
    print("│  Error details:")
    print("│  • Port /dev/ttyACM0 is in use by another process")
    print("│  • Process: screen (PID 1234)")
    print("│")
    print("│  Possible solutions:")
    solutions = [
        "Close the other application using the device",
        "Try using a different port",
        "Run: sudo lsof /dev/ttyACM0 to see all processes using it"
    ]
    for i, solution in enumerate(solutions):
        print(f"│  {i+1}. {solution}")

def demo_help_command():
    """Demonstrate help command formatting"""
    print(f"\n{EMOJI['document']} Screen Command Reference\n")
    print("  Control terminal screen sessions with these commands:\n")
    print("  screen -S NAME       Create new session named NAME")
    print("  screen -r NAME       Reattach to session NAME")
    print("  screen -ls           List all sessions")
    print("  ")
    print("  Inside a screen session:")
    print("  ")
    print("  Ctrl+A d            Detach from current session")
    print("  Ctrl+A c            Create new window")
    print("  Ctrl+A n            Switch to next window")
    print("  Ctrl+A p            Switch to previous window")
    print("  ")
    print("  Use 'uaibot help COMMAND' for more information on other commands.")

def main():
    """Run all demo functions"""
    # Create a full-width divider with the title
    term_width = os.get_terminal_size().columns
    title = "UaiBot Output Formatting Demo"
    padding = (term_width - len(title) - 4) // 2
    print("\n" + "=" * padding + f" {title} " + "=" * padding + "\n")
    
    demo_system_report()
    
    print("\n" + create_divider(style="full") + "\n")
    
    demo_error_message()
    
    print("\n" + create_divider(style="full") + "\n")
    
    demo_help_command()
    
    print("\n" + create_divider(style="full") + "\n")
    
    print(f"{EMOJI['success']} Demo completed successfully!")

if __name__ == "__main__":
    main()
