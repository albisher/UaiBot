#!/usr/bin/env python3
"""
Example Command Processor with Enhanced Output Formatting

This example shows how to integrate the EnhancedOutputProcessor into
a command processor implementation for UaiBot.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.append(project_root)

# Import the enhanced output processor
from terminal_commands.enhanced_output_processor import EnhancedOutputProcessor

class ExampleCommandProcessor:
    """
    Example command processor that uses the enhanced output processor.
    
    This is a simplified version to demonstrate the integration.
    """
    
    def __init__(self, config_path=None):
        """Initialize the command processor with user preferences."""
        self.config = self._load_config(config_path)
        
        # Get user's theme preference from config or use default
        user_theme = self.config.get("output_style", "default")
        self.output_processor = EnhancedOutputProcessor(theme=user_theme)
    
    def _load_config(self, config_path=None):
        """Load user configuration."""
        if not config_path:
            config_path = os.path.join(project_root, "config", "user_settings.json")
            
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        # Return default config if loading fails
        return {"output_style": "default"}
    
    def save_config(self, config_path=None):
        """Save current configuration."""
        if not config_path:
            config_path = os.path.join(project_root, "config", "user_settings.json")
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def set_output_theme(self, theme_name):
        """Set the output theme and save to user preferences."""
        if theme_name in ["default", "minimal", "professional"]:
            # Update processor theme
            self.output_processor.style_mgr.set_theme(theme_name)
            
            # Save to user settings
            if self.config:
                self.config["output_style"] = theme_name
                self.save_config()
            
            return True
        return False
    
    def process_command(self, command):
        """Process a command and return formatted output."""
        command = command.strip().lower()
        
        # Example command handling
        if command == "help":
            return self.cmd_help()
        elif command.startswith("theme "):
            # Handle theme command (e.g., "theme minimal")
            parts = command.split(' ', 1)
            if len(parts) > 1:
                theme_name = parts[1].strip()
                if self.set_output_theme(theme_name):
                    return self.output_processor.style_mgr.format_status_line(
                        f"Theme changed to {theme_name}", "success")
                else:
                    return self.output_processor.style_mgr.format_status_line(
                        f"Invalid theme: {theme_name}", "error")
        elif command == "status":
            return self.cmd_system_status()
        elif command == "disk":
            return self.cmd_disk_space()
        elif command == "uptime":
            return self.cmd_uptime()
        else:
            return self.output_processor.style_mgr.format_status_line(
                f"Unknown command: {command}", "error")
    
    def cmd_help(self):
        """Show help information."""
        # Create nicely formatted help content
        help_content = "Available commands:\n\n"
        help_content += "help      - Show this help information\n"
        help_content += "status    - Show system status\n"
        help_content += "disk      - Show disk space information\n"
        help_content += "uptime    - Show system uptime\n"
        help_content += "theme X   - Change output theme (default, minimal, professional)\n"
        
        # Format with a nice box and header
        return self.output_processor.style_mgr.format_header("Command Help", "info") + \
               self.output_processor.style_mgr.format_box(help_content, title="Available Commands")
    
    def cmd_system_status(self):
        """Show system status."""
        # This would normally get real system information
        # For this example, we'll use dummy data
        status_data = {
            "hostname": "example-host",
            "uptime": "2 days, 3:45",
            "cpu_usage": "32%",
            "memory_available": "4.5 GB",
            "disk_space_free": "120GB",
            "network_status": "Connected",
            "warnings": ["Memory usage high", "Software update available"],
            "errors": []
        }
        
        # Use the processor to format as JSON
        return self.output_processor.process_system_status(json.dumps(status_data))
    
    def cmd_disk_space(self):
        """Show disk space information."""
        # Dummy disk space output similar to df command
        disk_output = """Filesystem     Size    Used   Avail Capacity  Mounted on
/dev/sda1      120Gi   80Gi   40Gi    67%     /
/dev/sdb1      500Gi  200Gi  300Gi    40%     /data
/dev/sdc1     1000Gi  750Gi  250Gi    75%     /backups"""
        
        return self.output_processor.process_disk_space(disk_output)
    
    def cmd_uptime(self):
        """Show system uptime."""
        # Dummy uptime output
        uptime_output = "14:30 up 2 days, 3:45, 3 users, load average: 0.52, 0.58, 0.59"
        
        return self.output_processor.process_uptime(uptime_output)

# Simple demo if run directly
if __name__ == "__main__":
    processor = ExampleCommandProcessor()
    
    print("UaiBot Command Processor Example")
    print("Type 'help' for available commands, 'exit' to quit")
    print("")
    
    while True:
        command = input("> ")
        if command.lower() in ["exit", "quit"]:
            break
        
        # Process the command and print the result
        result = processor.process_command(command)
        print(result)
        print("")  # Add a blank line after each command
