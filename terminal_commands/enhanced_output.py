#!/usr/bin/env python3
"""
Output Formatter Integration Example

This module demonstrates how to integrate the new output formatting utilities
with the existing UaiBot codebase, specifically focusing on the terminal_commands
output processor.

Usage:
1. Import this module instead of directly using terminal_commands.output_processor
2. The formatted outputs will automatically use the new styling guidelines
"""

import platform
import os
import sys

# Add project root to sys.path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the original output processor
from terminal_commands.output_processor import OutputProcessor

# Import the new formatting utilities
from utils.output_formatter import (
    EMOJI, format_header, format_table_row, format_box,
    format_status_line, format_list, create_divider
)

class EnhancedOutputProcessor(OutputProcessor):
    """Enhanced version of the OutputProcessor using the new formatting guidelines."""
    
    def process_uptime(self, raw_output):
        """Process uptime command output with enhanced formatting."""
        # Example implementation for macOS/Linux
        if "load" in raw_output:
            # Extract the uptime part from output like: "14:30  up 3 days,  2:14, 5 users, load averages: 1.20 1.33 1.42"
            uptime_parts = raw_output.split(",")
            if len(uptime_parts) >= 2:
                up_part = uptime_parts[0].split("up ")[1].strip()
                # Format nicely with new utilities
                return format_status_line("System uptime", "info", up_part, emoji=True)
        
        # Fallback for simple output
        return format_status_line("System uptime", "info", raw_output.strip(), emoji=True)
    
    def process_memory(self, raw_output):
        """Process memory command output with enhanced formatting."""
        if not raw_output:
            return format_status_line("Memory information", "error", "Unable to retrieve memory information", emoji=True)
            
        mem_data = {}
        status = "success"
        
        try:
            if platform.system().lower() == 'darwin':
                # Process macOS memory info
                lines = raw_output.split('\n')
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        mem_data[key.strip()] = value.strip()
                
                # Extract key metrics
                if 'Memory Used' in mem_data:
                    memory_used = mem_data['Memory Used']
                    if 'Memory Available' in mem_data:
                        memory_avail = mem_data['Memory Available']
                        # Check if memory usage is high
                        if "GB" in memory_used and "GB" in memory_avail:
                            try:
                                used_gb = float(memory_used.split(' ')[0])
                                avail_gb = float(memory_avail.split(' ')[0])
                                if used_gb / (used_gb + avail_gb) > 0.85:  # More than 85% used
                                    status = "warning"
                            except (ValueError, IndexError):
                                pass
            
            elif platform.system().lower() == 'linux':
                # Process Linux memory info (free command)
                lines = raw_output.split('\n')
                if len(lines) >= 2:  # Ensure we have at least the header and one data line
                    # Process header and data line
                    for line in lines[1:]:  # Skip the header
                        if line.startswith('Mem:'):
                            parts = line.split()
                            if len(parts) >= 7:
                                total = int(parts[1]) / 1024  # Convert to MB
                                used = int(parts[2]) / 1024
                                free = int(parts[3]) / 1024
                                
                                mem_data['Total'] = f"{total:.2f} MB"
                                mem_data['Used'] = f"{used:.2f} MB"
                                mem_data['Free'] = f"{free:.2f} MB"
                                
                                # Check if memory usage is high
                                if used / total > 0.85:  # More than 85% used
                                    status = "warning"
                                
                                break
            
            # Format as a box for nicer presentation
            content = "Memory Information:\n"
            for key, value in mem_data.items():
                content += f"{key}: {value}\n"
            
            # Add a note for high memory usage
            if status == "warning":
                content += f"\n{EMOJI['warning']} Memory usage is high!"
                
            return format_box(content.strip(), title="Memory Status")
            
        except Exception as e:
            return format_status_line("Memory information", "error", f"Error processing output: {str(e)}", emoji=True)
    
    def process_disk(self, raw_output):
        """Process disk space command output with enhanced formatting."""
        if not raw_output or len(raw_output.strip()) == 0:
            return format_status_line("Disk space", "error", "Unable to retrieve disk information", emoji=True)
        
        try:
            # Format as a table
            header = format_header("Disk Usage", emoji=EMOJI["folder"])
            lines = raw_output.strip().split('\n')
            
            # Extract table rows and format them
            formatted_lines = []
            warning_disks = []
            
            for i, line in enumerate(lines):
                # Skip header line in df output
                if i == 0 or not line.strip():
                    continue
                    
                # Process data line
                parts = line.split()
                if len(parts) >= 5:
                    filesystem = parts[0]
                    size = parts[1]
                    used = parts[2]
                    avail = parts[3]
                    use_percent = parts[4]
                    mount = " ".join(parts[5:]) if len(parts) > 5 else ""
                    
                    # Check if disk usage is high (>85%)
                    if "%" in use_percent:
                        try:
                            percent = int(use_percent.rstrip('%'))
                            if percent > 85:
                                warning_disks.append((mount or filesystem, percent))
                                emoji = EMOJI["warning"]
                            else:
                                emoji = EMOJI["green"]
                        except ValueError:
                            emoji = ""
                    else:
                        emoji = ""
                        
                    # Format the line
                    if mount:
                        formatted_lines.append(f"{emoji} {mount:<15} {size:>8} {used:>8} {avail:>8} {use_percent:>5}")
                    else:
                        formatted_lines.append(f"{emoji} {filesystem:<15} {size:>8} {used:>8} {avail:>8} {use_percent:>5}")
            
            # Add headers
            table_header = f"{'Mount Point':<17} {'Size':>8} {'Used':>8} {'Avail':>8} {'Use%':>5}"
            formatted_output = header + table_header + "\n" + "-" * len(table_header) + "\n" + "\n".join(formatted_lines)
            
            # Add warnings if any disks are nearly full
            if warning_disks:
                warnings = [f"Disk {disk[0]} is at {disk[1]}% capacity!" for disk in warning_disks]
                formatted_output += "\n\n" + format_status_line("Warning", "warning", emoji=False) + "\n"
                formatted_output += "\n".join([f"• {w}" for w in warnings])
                
            return formatted_output
            
        except Exception as e:
            return format_status_line("Disk space", "error", f"Error processing output: {str(e)}", emoji=True)

# Example usage
if __name__ == "__main__":
    # Example raw outputs
    uptime_raw = "14:30  up 3 days, 2:14, 5 users, load averages: 1.20 1.33 1.42"
    
    memory_raw_mac = """Memory Used: 14.25 GB
Memory Available: 1.75 GB
Swap Used: 3.5 GB"""
    
    memory_raw_linux = """               total        used        free      shared  buff/cache   available
Mem:          32056       14725        2134         772       15196       16558
Swap:          2048          25        2023"""
    
    disk_raw = """Filesystem     1K-blocks      Used Available Use% Mounted on
/dev/sda1      103081248  83574216  14254828  86% /
/dev/sda2      103081248   5744216  97337032   6% /home
/dev/sdb1      206162496 185546248  10308124  95% /media/data"""
    
    # Create processor instance
    processor = EnhancedOutputProcessor()
    
    # Process and print example outputs
    print("\n" + processor.process_uptime(uptime_raw))
    print("\n" + processor.process_memory(memory_raw_mac))
    print("\n" + processor.process_disk(disk_raw))
