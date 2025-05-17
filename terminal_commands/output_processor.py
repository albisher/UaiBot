"""
Output processor for UaiBot commands.
Formats raw command output into user-friendly results.
"""
import platform
import re

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
                return f"Your system has been running for {up_part}"
        
        # Fallback for simple output
        return f"System uptime: {raw_output.strip()}"
    
    def process_memory(self, raw_output):
        """Process memory command output."""
        if platform.system().lower() == 'darwin':
            # Process vm_stat output on macOS
            lines = raw_output.strip().split('\n')
            memory_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    memory_info[key.strip()] = value.strip()
            
            # Estimate memory usage from vm_stat output
            return f"Memory information:\n{raw_output}"
        else:
            # Simple output for other platforms
            return f"Memory information:\n{raw_output}"
    
    def process_disk_space(self, raw_output):
        """Process disk space command output."""
        return f"Disk space information:\n{raw_output}"
    
    def process_notes_topics(self, raw_output):
        """Process Notes topics/folders search output."""
        if not raw_output or raw_output.strip() == "":
            return "I couldn't find any Notes topics on your system."
        
        # Format for macOS AppleScript output which will be like: {"Notes", "Work", "Personal"}
        if platform.system().lower() == 'darwin':
            # Remove any leading/trailing whitespace and brackets
            cleaned_output = raw_output.strip()
            if cleaned_output.startswith('{') and cleaned_output.endswith('}'):
                cleaned_output = cleaned_output[1:-1]
            
            # Split on commas and clean up each topic name
            topics = [topic.strip(' "\'') for topic in cleaned_output.split(',') if topic.strip()]
            
            if not topics:
                return "I couldn't find any Notes topics on your system."
                
            result = "📝 Here are your Notes topics:\n\n"
            for topic in topics:
                result += f"• {topic}\n"
                
            return result.strip()
        else:
            # For other platforms
            folders = raw_output.strip().split('\n')
            
            result = "📝 Here are your Notes folders:\n\n"
            for folder in folders:
                folder = folder.strip()
                if folder:
                    result += f"• {folder}\n"
                    
            return result.strip()
    
    def process_notes_count(self, raw_output):
        """Process Notes count output."""
        if not raw_output or raw_output.strip() == "":
            return "I couldn't determine the number of notes."
        
        try:
            count = int(raw_output.strip())
            return f"📝 You have {count} notes in your Notes app."
        except ValueError:
            return f"Notes count information: {raw_output.strip()}"
    
    def process_notes_list(self, raw_output):
        """Process Notes list output."""
        if not raw_output or raw_output.strip() == "":
            return "I couldn't find any notes in your Notes app."
        
        # Format for macOS AppleScript output which will be like: {"Note 1", "Shopping List", "Ideas"}
        if platform.system().lower() == 'darwin':
            # Remove any leading/trailing whitespace and brackets
            cleaned_output = raw_output.strip()
            if cleaned_output.startswith('{') and cleaned_output.endswith('}'):
                cleaned_output = cleaned_output[1:-1]
            
            # Split on commas and clean up each note name
            notes = [note.strip(' "\'') for note in cleaned_output.split(',') if note.strip()]
            
            if not notes:
                return "I couldn't find any notes in your Notes app."
                
            result = "📝 Here are your Notes:\n\n"
            for note in notes:
                result += f"• {note}\n"
                
            return result.strip()
        else:
            # For other platforms
            return f"Notes list: {raw_output.strip()}"
    
    def process_folder_search(self, raw_output, search_term):
        """Process folder search results."""
        if not raw_output or raw_output.strip() == "":
            return f"I didn't find any folders matching '{search_term}'."
            
        folders = raw_output.strip().split('\n')
        
        result = f"📂 Here are folders matching '{search_term}':\n\n"
        for folder in folders:
            folder = folder.strip()
            if folder:
                result += f"• {folder}\n"
                
        return result.strip()
