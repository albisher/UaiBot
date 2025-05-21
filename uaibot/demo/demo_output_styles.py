#!/usr/bin/env python3
"""
Output Style Demo

This script demonstrates the use of the OutputStyleManager to provide
consistent, configurable output formatting for UaiBot.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.append(project_root)

from utils.output_style_manager import OutputStyleManager

def demo_theme(style_mgr, theme_name):
    """Demonstrate a specific theme"""
    style_mgr.set_theme(theme_name)
    
    divider = "=" * style_mgr.get_terminal_width()
    print(f"\n{divider}")
    print(f"Theme: {theme_name}")
    print(f"{divider}")
    
    # Show header
    print(style_mgr.format_header("System Status", "robot"))
    
    # Show status lines
    print(style_mgr.format_status_line("Database connection", "success", "Connected"))
    print(style_mgr.format_status_line("Memory usage", "warning", "85% used"))
    print(style_mgr.format_status_line("Network", "error", "Disconnected"))
    
    # Show a box
    content = "CPU: 45% utilization\nRAM: 3.2GB/8GB used\nDisk: 120GB free"
    print("\n" + style_mgr.format_box(content, title="System Resources"))
    
    # Device list
    devices = [
        {"name": "Arduino Mega", "status": "Connected", "port": "/dev/ttyACM0"},
        {"name": "Webcam C920", "status": "Available", "port": "/dev/video0"},
        {"name": "USB Drive", "status": "Mounted", "path": "/media/usb0"}
    ]
    
    print("\n" + style_mgr.format_header("Connected Devices", "computer"))
    
    for i, device in enumerate(devices):
        status_emoji = "green" if device["status"] in ["Connected", "Available", "Mounted"] else "red"
        status_icon = style_mgr.get_emoji(status_emoji)
        print(f"{i+1}. {status_icon} {device['name']}")
        if "port" in device:
            print(f"   │  Port: {device['port']}")
        if "path" in device:
            print(f"   │  Path: {device['path']}")
        print(f"   └  Status: {device['status']}")

def main():
    """Main function to run the demo"""
    # Create style manager
    style_mgr = OutputStyleManager()
    
    # Show available themes
    themes = list(style_mgr.config.get("themes", {}).keys())
    print(f"Available themes: {', '.join(themes)}")
    
    # Demo each theme
    for theme in themes:
        demo_theme(style_mgr, theme)
        time.sleep(0.5)  # Pause briefly between themes
    
    print("\nDemo completed!")

if __name__ == "__main__":
    main()
