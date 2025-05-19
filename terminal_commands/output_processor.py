"""
Output processor for UaiBot commands.
Formats raw command output into user-friendly results.
"""
import platform
import re
import json
from utils.output_formatter import (
    EMOJI, format_header, format_table_row, format_box,
    format_status_line, format_list, create_divider
)

class OutputProcessor:
    """Processes raw command output into human-readable format."""
    
    def process_uptime(self, raw_output):
        """Process uptime command output."""
        # Example implementation for macOS/Linux
        if "load" in raw_output:
            # Extract the uptime part from output like: "14:30  up 3 days,  2:14, 5 users, load averages: 1.20 1.33 1.42"
            uptime_parts = raw_output.split(",")
            if len(uptime_parts) >= 2:
                up_part = uptime_parts[0].split("up ")[1].strip()
                # Format nicely using output_formatter
                return format_status_line(f"Your system has been running for {up_part}", "time")
        
        # Fallback for simple output
        return format_status_line(f"System uptime: {raw_output.strip()}", "time")
    
    def process_windows_uptime(self, raw_output):
        """Process Windows uptime output."""
        # This would require actual implementation to parse Windows-specific format
        # Simplified example using output_formatter
        return format_status_line(f"System uptime: {raw_output.strip()}", "time")
    
    def process_disk_space(self, raw_output):
        """Process disk space command output."""
        if not raw_output:
            return format_status_line("Unable to retrieve disk space information.", "error")
        
        lines = raw_output.strip().split('\n')
        if len(lines) < 2:
            return format_status_line(f"Disk space information: {raw_output.strip()}", "folder")
        
        # Skip header line and process disk partitions
        result = format_header("Disk Space Information", "folder")
        
        # Process each line into a formatted table
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
                    # Display drive info with appropriate icon based on usage
                    status_key = "green"
                    try:
                        usage = int(use_percent.strip('%'))
                        if usage > 90:
                            status_key = "red"
                        elif usage > 70:
                            status_key = "yellow"
                    except ValueError:
                        pass
                        
                    result += format_status_line(f"{mount}", status_key) + "\n"
                    result += f"  {avail} free of {size} ({use_percent} used)\n\n"
        
        return result.strip()
    
    def process_windows_disk_space(self, raw_output):
        """Process Windows disk space output."""
        # Using output_formatter for consistent formatting
        header = format_header("Disk Space Information", "folder")
        return header + raw_output.strip()
    
    def process_macos_memory(self, raw_output):
        """Process macOS vm_stat output."""
        # Using output_formatter for consistent formatting
        header = format_header("Memory Information", "stats")
        return header + format_box(raw_output.strip(), title="Memory Statistics")
    
    def process_linux_memory(self, raw_output):
        """Process Linux free -h output."""
        # Using output_formatter for consistent formatting
        header = format_header("Memory Information", "stats")
        return header + format_box(raw_output.strip(), title="Memory Statistics")
    
    def process_windows_memory(self, raw_output):
        """Process Windows memory output."""
        # Using output_formatter for consistent formatting
        header = format_header("Memory Information", "stats")
        return header + format_box(raw_output.strip(), title="Memory Statistics")
    
    def process_notes_folders(self, raw_output):
        """Process Notes folder search output."""
        if not raw_output or raw_output.strip() == "":
            return format_status_line("I didn't find any Notes folders on your system.", "info")
            
        folders = raw_output.strip().split("\n")
        
        result = format_header("Notes Folders", "document")
        folder_list = []
        
        for folder in folders:
            folder = folder.strip()
            if folder:
                if "iCloud" in folder:
                    folder_list.append(f"iCloud Notes: {folder}")
                elif "Containers" in folder:
                    folder_list.append(f"Local Notes: {folder}")
                elif "Notes.app" in folder:
                    folder_list.append(f"Notes Application: {folder}")
                else:
                    folder_list.append(folder)
        
        # Format as a proper list
        if folder_list:
            result += format_list(folder_list)
            
        return result.strip()
    
    def process_notes_topics(self, raw_output):
        """Process notes topic list output."""
        if not raw_output or raw_output.strip() == "":
            return format_status_line("I didn't find any Notes topics.", "info")
        
        # Format for macOS AppleScript output which will be like: {"Notes", "Work", "Personal"}
        if raw_output.strip().startswith('{') and raw_output.strip().endswith('}'):
            # Clean up the output from AppleScript
            cleaned = raw_output.strip()[1:-1]
            # Split on commas and clean up quotes
            topics = [topic.strip(' "\'') for topic in cleaned.split(',') if topic.strip()]
        else:
            topics = raw_output.strip().split("\n")
        
        result = format_header("Notes Topics", "document")
        topic_list = [topic.strip() for topic in topics if topic.strip()]
        
        # Format as a proper list
        if topic_list:
            result += format_list(topic_list)
            
        return result.strip()
    
    def process_youtube_results(self, raw_output):
        """Process YouTube API results."""
        try:
            data = json.loads(raw_output)
            if "items" in data and len(data["items"]) > 0:
                result = format_header("Trending on YouTube", "stats")
                video_list = []
                
                for i, item in enumerate(data["items"]):
                    if "snippet" in item:
                        snippet = item["snippet"]
                        title = snippet.get("title", "Unknown")
                        channel = snippet.get("channelTitle", "Unknown Channel")
                        video_list.append(f"**{title}**\nby {channel}")
                
                # Format as numbered list
                if video_list:
                    result += format_list(video_list, bullet_type="number")
                return result
            else:
                return format_status_line("No trending videos found on YouTube.", "error")
        except json.JSONDecodeError:
            return format_status_line("Error parsing YouTube API response.", "error")
        except Exception as e:
            return format_status_line(f"Error processing YouTube results: {str(e)}", "error")
    
    def process_general_search(self, raw_output, search_term):
        """Process general search results."""
        if not raw_output or raw_output.strip() == "":
            return format_status_line(f"I didn't find anything matching '{search_term}'.", "search")
        
        items = raw_output.strip().split("\n")
        
        result = format_header(f"Search Results for '{search_term}'", "search")
        item_list = [item.strip() for item in items if item.strip()]
        
        # Format as a bullet list
        if item_list:
            result += format_list(item_list)
                
        return result.strip()
