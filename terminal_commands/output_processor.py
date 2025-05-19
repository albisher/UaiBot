"""
Output processor for UaiBot commands.
Formats raw command output into user-friendly results.
"""
import platform
import re
import json

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
                # Format nicely
                return f"⏱️ Your system has been running for {up_part}"
        
        # Fallback for simple output
        return f"⏱️ System uptime: {raw_output.strip()}"
    
    def process_memory(self, raw_output):
        """Process memory command output."""
        if not raw_output:
            return "❌ Unable to retrieve memory information."
            
        if platform.system().lower() == 'darwin':
            # Process vm_stat output on macOS
            lines = raw_output.strip().split('\n')
            memory_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    memory_info[key.strip()] = value.strip()
            
            # Estimate memory usage from vm_stat output
            return f"🧠 **Memory Information**\n\n{raw_output}"
        else:
            # Simple output for other platforms
            return f"🧠 **Memory Information**\n\n{raw_output}"
    
    def process_disk_space(self, raw_output):
        """Process disk space command output."""
        if not raw_output:
            return "❌ Unable to retrieve disk space information."
        
        lines = raw_output.strip().split('\n')
        if len(lines) < 2:
            return f"💾 Disk space information: {raw_output.strip()}"
        
        # Skip header line and process disk partitions
        result = "💾 **Disk Space Information**\n\n"
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
                    result += f"• {mount}:\n"
                    result += f"  - {avail} free of {size} ({use_percent} used)\n\n"
        
        return result.strip()
    
    def process_notes_topics(self, raw_output):
        """Process Notes topics/folders search output."""
        if not raw_output or raw_output.strip() == "":
            return "📝 I couldn't find any Notes topics on your system."
        
        # Format for macOS AppleScript output which will be like: {"Notes", "Work", "Personal"}
        if platform.system().lower() == 'darwin':
            # Remove any leading/trailing whitespace and brackets
            cleaned_output = raw_output.strip()
            if cleaned_output.startswith('{') and cleaned_output.endswith('}'):
                cleaned_output = cleaned_output[1:-1]
            
            # Split on commas and clean up each topic name
            topics = [topic.strip(' "\'') for topic in cleaned_output.split(',') if topic.strip()]
            
            if not topics:
                return "📝 I couldn't find any Notes topics on your system."
                
            result = "📝 **Notes Topics**\n\n"
            for topic in topics:
                result += f"• {topic}\n"
                
            return result.strip()
        else:
            # For other platforms
            folders = raw_output.strip().split('\n')
            
            result = "📝 **Notes Folders**\n\n"
            for folder in folders:
                folder = folder.strip()
                if folder:
                    result += f"• {folder}\n"
                    
            return result.strip()
    
    def process_notes_count(self, raw_output):
        """Process Notes count output."""
        if not raw_output or raw_output.strip() == "":
            return "❌ I couldn't determine the number of notes."
        
        try:
            count = int(raw_output.strip())
            return f"📝 You have {count} notes in your Notes app."
        except ValueError:
            return f"📝 Notes count information: {raw_output.strip()}"
    
    def process_notes_list(self, raw_output):
        """Process Notes list output."""
        if not raw_output or raw_output.strip() == "":
            return "📝 I couldn't find any notes in your Notes app."
        
        # Format for macOS AppleScript output which will be like: {"Note 1", "Shopping List", "Ideas"}
        if platform.system().lower() == 'darwin':
            # Remove any leading/trailing whitespace and brackets
            cleaned_output = raw_output.strip()
            if cleaned_output.startswith('{') and cleaned_output.endswith('}'):
                cleaned_output = cleaned_output[1:-1]
            
            # Split on commas and clean up each note name
            notes = [note.strip(' "\'') for note in cleaned_output.split(',') if note.strip()]
            
            if not notes:
                return "📝 I couldn't find any notes in your Notes app."
                
            result = "📝 **Your Notes**\n\n"
            for note in notes:
                result += f"• {note}\n"
                
            return result.strip()
        else:
            # For other platforms
            return f"📝 **Notes List**\n\n{raw_output.strip()}"
    
    def process_folder_search(self, raw_output, search_term):
        """Process folder search results."""
        if not raw_output or raw_output.strip() == "":
            return f"🔍 I didn't find any folders matching '{search_term}'."
            
        folders = raw_output.strip().split('\n')
        
        result = f"📂 **Folders matching '{search_term}'**\n\n"
        for folder in folders:
            folder = folder.strip()
            if folder:
                result += f"• {folder}\n"
                
        return result.strip()
        
    def process_windows_uptime(self, raw_output):
        """Process Windows uptime output."""
        # This would require actual implementation to parse Windows-specific format
        return f"⏱️ System uptime: {raw_output.strip()}"
        
    def process_windows_disk_space(self, raw_output):
        """Process Windows disk space output."""
        return f"💾 **Disk space information**:\n\n{raw_output.strip()}"
    
    def process_macos_memory(self, raw_output):
        """Process macOS vm_stat output."""
        return f"🧠 **Memory information**:\n\n{raw_output.strip()}"
    
    def process_linux_memory(self, raw_output):
        """Process Linux free -h output."""
        return f"🧠 **Memory information**:\n\n{raw_output.strip()}"
    
    def process_windows_memory(self, raw_output):
        """Process Windows memory output."""
        return f"🧠 **Memory information**:\n\n{raw_output.strip()}"
        
    def process_youtube_results(self, raw_output):
        """Process YouTube API results."""
        try:
            data = json.loads(raw_output)
            if "items" in data and len(data["items"]) > 0:
                result = "🎬 **Currently Trending on YouTube**\n\n"
                for i, item in enumerate(data["items"]):
                    if "snippet" in item:
                        snippet = item["snippet"]
                        title = snippet.get("title", "Unknown")
                        channel = snippet.get("channelTitle", "Unknown Channel")
                        result += f"{i+1}. **{title}**\n   by {channel}\n\n"
                return result.strip()
            else:
                return "❌ No trending videos found on YouTube."
        except json.JSONDecodeError:
            return "❌ Error parsing YouTube API response."
        except Exception as e:
            return f"❌ Error processing YouTube results: {str(e)}"
    
    def process_general_search(self, raw_output, search_term):
        """Process general search results."""
        if not raw_output or raw_output.strip() == "":
            return f"🔍 I didn't find anything matching '{search_term}'."
        
        items = raw_output.strip().split("\n")
        
        result = f"🔍 **Search Results for '{search_term}'**\n\n"
        for item in items:
            item = item.strip()
            if item:
                result += f"• {item}\n"
                
        return result.strip()
