#!/usr/bin/env python3
"""
Enhanced Output Processor for UaiBot commands.

Formats raw command output into user-friendly results using the OutputStyleManager.
This provides consistent styling across the application with support for theming.
"""
import platform
import re
import json
import os
import sys

# Add parent directory to path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

# Import the style manager
from utils.output_style_manager import OutputStyleManager
# Import the output handler for direct output
from utils.output_handler import output_handler

class EnhancedOutputProcessor:
    """
    Processes raw command output into human-readable format with consistent styling.
    Uses OutputStyleManager for theming support.
    """
    
    def __init__(self, theme="default"):
        """
        Initialize the output processor with the specified theme.
        
        Args:
            theme (str): Theme to use for styling (default, minimal, professional)
        """
        self.style_mgr = OutputStyleManager(theme=theme)
        
    def process_uptime(self, raw_output):
        """Process uptime command output."""
        if not raw_output:
            return self.style_mgr.format_status_line("Unable to retrieve uptime information", "error")
        
        # Example implementation for macOS/Linux
        if "load" in raw_output:
            # Extract the uptime part from output like: "14:30  up 3 days,  2:14, 5 users, load averages: 1.20 1.33 1.42"
            uptime_parts = raw_output.split(",")
            if len(uptime_parts) >= 2:
                up_part = uptime_parts[0].split("up ")[1].strip()
                # Format nicely
                return self.style_mgr.format_status_line(f"Your system has been running for {up_part}", "time")
        
        # Fallback for simple output
        return self.style_mgr.format_status_line(f"System uptime: {raw_output.strip()}", "time")
    
    def process_memory(self, raw_output):
        """Process memory command output."""
        if not raw_output:
            return self.style_mgr.format_status_line("Unable to retrieve memory information", "error")
            
        header = self.style_mgr.format_header("Memory Information", "stats")
        
        if platform.system().lower() == 'darwin':
            # Process vm_stat output on macOS
            lines = raw_output.strip().split('\n')
            memory_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    memory_info[key.strip()] = value.strip()
            
            # Format the output in a box
            return header + self.style_mgr.format_box(raw_output.strip(), title="Memory Statistics")
        else:
            # Simple output for other platforms
            return header + self.style_mgr.format_box(raw_output.strip(), title="Memory Statistics")
    
    def process_disk_space(self, raw_output):
        """Process disk space command output."""
        if not raw_output:
            return self.style_mgr.format_status_line("Unable to retrieve disk space information", "error")
        
        lines = raw_output.strip().split('\n')
        if len(lines) < 2:
            return self.style_mgr.format_status_line(f"Disk space information: {raw_output.strip()}", "folder")
        
        # Skip header line and process disk partitions
        header = self.style_mgr.format_header("Disk Space Information", "folder")
        result = ""
        
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 5:
                filesystem = parts[0]
                size = parts[1]
                used = parts[2]
                avail = parts[3]
                use_percent = parts[4]
                mount = " ".join(parts[5:])
                
                if mount == "/" or mount == "/System/Volumes/Data" or "user" in mount.lower():
                    # Determine status based on usage percentage
                    status_key = "success"  # Default to green/success
                    try:
                        usage = int(use_percent.strip('%'))
                        if usage > 90:
                            status_key = "error"
                        elif usage > 70:
                            status_key = "warning"
                    except ValueError:
                        pass
                    
                    result += self.style_mgr.format_status_line(f"{mount}", status_key) + "\n"
                    result += f"  {avail} free of {size} ({use_percent} used)\n\n"
        
        return header + result.strip()
    
    def process_notes_topics(self, raw_output):
        """Process Notes topics/folders search output."""
        if not raw_output or raw_output.strip() == "":
            return self.style_mgr.format_status_line("I couldn't find any Notes topics on your system", "info")
        
        header = self.style_mgr.format_header("Notes Topics", "document")
        
        # Format for macOS AppleScript output which will be like: {"Notes", "Work", "Personal"}
        if platform.system().lower() == 'darwin':
            # Remove any leading/trailing whitespace and brackets
            cleaned_output = raw_output.strip()
            if cleaned_output.startswith('{') and cleaned_output.endswith('}'):
                cleaned_output = cleaned_output[1:-1]
            
            # Split on commas and clean up each topic name
            topics = [topic.strip(' "\'') for topic in cleaned_output.split(',') if topic.strip()]
            
            if not topics:
                return self.style_mgr.format_status_line("I couldn't find any Notes topics on your system", "info")
            
            # Build result with bullets
            result = ""
            for topic in topics:
                result += f"• {topic}\n"
                
            return header + result.strip()
        else:
            # For other platforms
            folders = raw_output.strip().split('\n')
            
            # Build result with bullets
            result = ""
            for folder in folders:
                folder = folder.strip()
                if folder:
                    result += f"• {folder}\n"
                    
            return header + result.strip()
    
    def process_running_processes(self, raw_output):
        """Process ps command output for running processes."""
        if not raw_output:
            return self.style_mgr.format_status_line("Unable to retrieve process information", "error")
        
        header = self.style_mgr.format_header("Running Processes", "computer")
        
        lines = raw_output.strip().split('\n')
        if len(lines) <= 1:  # Only header or empty
            return header + "No processes found."
            
        # Get top 5 processes by CPU or memory (depends on sort order)
        processes = lines[1:6]  # Skip header, get top 5
        
        result = ""
        for proc in processes:
            parts = proc.split()
            if len(parts) >= 4:  # Basic validation
                # Extract relevant parts (format depends on ps command used)
                try:
                    pid = parts[0]
                    cpu = parts[2] if len(parts) > 2 else "?"
                    mem = parts[3] if len(parts) > 3 else "?"
                    name = parts[-1]  # Last part is usually process name
                    
                    result += f"• {name} (PID: {pid}, CPU: {cpu}, MEM: {mem})\n"
                except IndexError:
                    result += f"• {proc}\n"  # Fallback
        
        return header + result

    def process_system_status(self, raw_output):
        """Process a general system status check."""
        try:
            data = json.loads(raw_output)
            
            header = self.style_mgr.format_header("System Status", "robot")
            content = ""
            
            for key, value in data.items():
                if key == "errors" and value:
                    for error in value:
                        content += self.style_mgr.format_status_line(error, "error") + "\n"
                elif key == "warnings" and value:
                    for warning in value:
                        content += self.style_mgr.format_status_line(warning, "warning") + "\n"
                else:
                    status_key = "success"
                    content += self.style_mgr.format_status_line(f"{key}: {value}", status_key) + "\n"
            
            return header + content
        except json.JSONDecodeError:
            # Not JSON, return formatted raw output
            return self.style_mgr.format_box(raw_output, title="System Status")

    def command_to_output_handler(self, command, raw_output, processor_method=None):
        """
        Process a command and display it through the output handler.
        
        Args:
            command (str): The command that was executed
            raw_output (str): The raw output from the command
            processor_method (str): Name of the processor method to use
                                   (if None, will try to guess from command)
        """
        # Display the command that was executed
        output_handler.command(command)
        
        # If no processor method specified, try to infer from command
        if processor_method is None:
            # Simple matching logic - could be enhanced
            if command.startswith("uptime"):
                processor_method = "process_uptime"
            elif command.startswith("vm_stat") or command.startswith("free"):
                processor_method = "process_memory"
            elif command.startswith("df"):
                processor_method = "process_disk_space"
            elif "ps" in command:
                processor_method = "process_running_processes"
        
        # Process the output
        success = bool(raw_output)
        
        if processor_method and hasattr(self, processor_method):
            formatted_output = getattr(self, processor_method)(raw_output)
            # Show success/failure
            if success:
                output_handler.result(True, "Command executed successfully")
            else:
                output_handler.result(False, "Command returned no data")
            
            # Display formatted output
            output_handler.capture_print("\n" + formatted_output)
        else:
            # Default processing for commands without specific processor
            if success:
                output_handler.result(True, "Command executed successfully")
                output_handler.box(raw_output, title="Output")
            else:
                output_handler.result(False, "Command failed or returned no output")

# Simple test if run directly
if __name__ == "__main__":
    processor = EnhancedOutputProcessor()
    
    # Test uptime processing
    print("\nTesting uptime processing:")
    print(processor.process_uptime("14:30  up 3 days, 2:14, 5 users, load averages: 1.20 1.33 1.42"))
    
    # Test disk space processing
    print("\nTesting disk space processing:")
    disk_output = """Filesystem     Size    Used   Avail Capacity    iused   ifree %iused  Mounted on
/dev/disk1s5s1  466Gi  15.1Gi  370Gi     4%     52110 4881892    1%   /
/dev/disk1s4    466Gi  80.1Gi  370Gi    18%    484008 4881892    9%   /System/Volumes/Data
/dev/disk1s3    466Gi   5.0Gi  370Gi     2%         5 4881892    0%   /private/var/vm"""
    print(processor.process_disk_space(disk_output))
    
    # Switch themes and test again
    print("\nSwitching to minimal theme:")
    processor.style_mgr.set_theme("minimal")
    print(processor.process_uptime("14:30  up 3 days, 2:14, 5 users, load averages: 1.20 1.33 1.42"))
    
    # Test with output handler
    print("\nTesting with output handler:")
    output_handler.reset()
    output_handler.thinking("I need to check system uptime...")
    processor.command_to_output_handler("uptime", "14:30  up 3 days, 2:14, 5 users, load averages: 1.20 1.33 1.42", "process_uptime")
    
    print("\nTesting disk space with output handler:")
    output_handler.reset()
    output_handler.thinking("Checking available disk space...")
    processor.command_to_output_handler("df -h", disk_output, "process_disk_space")
