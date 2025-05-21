import re
import json
import platform
import subprocess
import shlex
from pathlib import Path
import os

class CommandProcessor:
    """Process user input and execute commands directly."""
    
    def __init__(self, shell_handler=None):
        self.system_platform = platform.system().lower()
        self.shell_handler = shell_handler or ShellHandler()
        self.command_registry = CommandRegistry(self.system_platform)
        self.output_processor = OutputProcessor()
    
    def process_command(self, user_input):
        """Process user input and execute commands directly."""
        query_lower = user_input.lower()
        
        # YOUTUBE/MEDIA QUERIES
        if self._is_youtube_query(query_lower):
            return self._execute_youtube_query(query_lower)
            
        # NOTES/APP SPECIFIC QUERIES
        if self._is_notes_query(query_lower):
            return self._execute_notes_query(query_lower)
        
        # SYSTEM INFORMATION QUERIES
        if self._is_system_info_query(query_lower):
            return self._execute_system_info_command(query_lower)
            
        # FILE/FOLDER OPERATIONS
        if self._is_file_folder_query(query_lower):
            return self._execute_file_folder_command(query_lower)
            
        # GENERAL COMMAND DETECTION
        if self._is_general_command_query(query_lower):
            return self._execute_general_command(query_lower)
            
        # ONLY as last resort, use AI
        return self._handle_with_ai(user_input)
    
    def _is_youtube_query(self, query):
        """Detect YouTube-related queries."""
        return re.search(r'(youtube|trending|playing on youtube|video|trending video)', query) is not None
        
    def _is_notes_query(self, query):
        """Detect Notes-related queries."""
        return re.search(r'(notes\b|note\b|topics|notes topic|apple notes)', query) is not None
    
    def _is_system_info_query(self, query):
        """Detect system info queries with comprehensive patterns."""
        if re.search(r'(how\s+long|since|uptime|duration|running\s+time|system\s+on\s+time|time\s+running)', query):
            return True
            
        if re.search(r'(memory|ram|available\s+memory|free\s+memory|memory\s+usage)', query):
            return True
            
        if re.search(r'(disk|space|storage|free\s+space|available\s+space|disk\s+usage)', query):
            return True
            
        return False

    def _is_file_folder_query(self, query):
        """Detect file and folder operation queries."""
        if re.search(r'(notes?\s+folders?|where\s+.*\s+notes|show\s+.*\s+notes|list\s+.*\s+notes|find\s+.*\s+notes)', query):
            return True
            
        if re.search(r'(folders?|directories?|where\s+.*\s+folders?|show\s+.*\s+folders?|list\s+.*\s+folders?)', query):
            return True
            
        if re.search(r'(files?|where\s+.*\s+files?|show\s+.*\s+files?|list\s+.*\s+files?|find\s+.*\s+files?)', query):
            return True
            
        return False
    
    def _is_general_command_query(self, query):
        """Detect if the query is asking for a general command to be executed."""
        # This is a simplified implementation
        command_indicators = ['run', 'execute', 'show me', 'display', 'get', 'find', 'search', 'list']
        return any(indicator in query for indicator in command_indicators)
    
    def _execute_youtube_query(self, query):
        """Execute YouTube trending query and return processed results."""
        # Attempt to get API key from environment or config
        api_key = self._get_api_key("YOUTUBE_API_KEY")
        
        if not api_key:
            return "🔴 Could not access YouTube API - no API key available.\n\n" \
                   "I need a YouTube API key to check trending videos. You can set this up by:\n" \
                   "1. Creating a Google Cloud project\n" \
                   "2. Enabling the YouTube Data API v3\n" \
                   "3. Setting the YOUTUBE_API_KEY environment variable"
        
        try:
            cmd = f"curl -s 'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q=trending&key={api_key}'"
            result = self.shell_handler.execute_command(cmd)
            return self.output_processor.process_youtube_results(result)
        except Exception as e:
            return f"❌ Error retrieving YouTube trending videos: {str(e)}"
    
    def _execute_notes_query(self, query):
        """Execute Notes-related query."""
        if "topic" in query or "list" in query:
            if self.system_platform == "darwin":  # macOS
                # Try to use notes CLI if it exists
                if self.shell_handler.command_exists("notes"):
                    result = self.shell_handler.execute_command("notes topic list")
                    return self.output_processor.process_notes_topics(result)
                else:
                    # Alternative: find Notes folders and content
                    cmd = self.command_registry.get_command("notes_folders")
                    result = self.shell_handler.execute_command(cmd)
                    return self.output_processor.process_notes_folders(result)
            else:
                # For other platforms, search for notes in common locations
                search_term = "notes"
                result = self.shell_handler.find_folders(search_term, location="~", include_cloud=True)
                return self.output_processor.process_general_search(result, search_term)
    
    def _execute_system_info_command(self, query):
        """Execute appropriate system command for information queries."""
        if 'uptime' in query or 'how long' in query or 'running' in query:
            if self.system_platform in ['darwin', 'linux']:
                output = self.shell_handler.execute_command('uptime')
                readable_uptime = self.output_processor.process_uptime(output)
                return readable_uptime
            elif self.system_platform == 'windows':
                cmd = 'powershell "Get-CimInstance -ClassName Win32_OperatingSystem | Select LastBootUpTime"'
                output = self.shell_handler.execute_command(cmd)
                readable_uptime = self.output_processor.process_windows_uptime(output)
                return readable_uptime
        
        if 'disk' in query or 'space' in query or 'storage' in query:
            if self.system_platform in ['darwin', 'linux']:
                output = self.shell_handler.execute_command('df -h')
                return self.output_processor.process_disk_space(output)
            elif self.system_platform == 'windows':
                cmd = 'powershell "Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free"'
                output = self.shell_handler.execute_command(cmd)
                return self.output_processor.process_windows_disk_space(output)
                
        if 'memory' in query or 'ram' in query:
            if self.system_platform == 'darwin':
                output = self.shell_handler.execute_command('vm_stat')
                return self.output_processor.process_macos_memory(output)
            elif self.system_platform == 'linux':
                output = self.shell_handler.execute_command('free -h')
                return self.output_processor.process_linux_memory(output)
            elif self.system_platform == 'windows':
                cmd = 'powershell "Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory,TotalVisibleMemorySize"'
                output = self.shell_handler.execute_command(cmd)
                return self.output_processor.process_windows_memory(output)
        
        return "I wasn't able to find system information for that query."
    
    def _execute_file_folder_command(self, query):
        """Execute appropriate file/folder command."""
        query_lower = query.lower()
        words = query_lower.split()
        
        # Create file command
        if any(word in ['create', 'make', 'new'] for word in words) and 'file' in words:
            return self._handle_create_file(query)
            
        # Read file command
        elif any(word in ['read', 'show', 'display', 'get'] for word in words) and 'content' in words:
            return self._handle_read_file(query)
            
        # Write file command
        elif any(word in ['write', 'update', 'modify', 'change'] for word in words):
            return self._handle_write_file(query)
            
        # Append file command
        elif any(word in ['add', 'append'] for word in words):
            return self._handle_append_file(query)
            
        # Delete file command
        elif any(word in ['delete', 'remove'] for word in words):
            return self._handle_delete_file(query)
            
        # List files command
        elif any(word in ['list', 'show', 'display'] for word in words) and 'files' in words:
            return self._handle_list_files()
            
        # Search files command
        elif any(word in ['find', 'search', 'look'] for word in words):
            return self._handle_search_files(query)
            
        # Legacy folder/file search
        if 'note' in words and ('folder' in words or 'app' in words):
            return self.shell_handler.find_folders("Notes", location="~", include_cloud=True)
            
        if 'folder' in words or 'director' in words:
            folder_name = self._extract_search_term(query)
            return self.shell_handler.find_folders(folder_name, location="~", include_cloud=True)
        
        if 'file' in words:
            file_name = self._extract_search_term(query)
            return self.shell_handler.find_files(file_name, location="~")
        
        return "I wasn't able to understand what files or folders you're looking for."
    
    def _handle_create_file(self, query):
        """Handle file creation commands."""
        words = query.split()
        filename = None
        content = None
        
        # Find filename
        for i, word in enumerate(words):
            if word in ['file', 'named', 'called'] and i + 1 < len(words):
                filename = words[i + 1]
                break
        
        # Find content between quotes
        quote_start = query.find('"')
        if quote_start == -1:
            quote_start = query.find("'")
        if quote_start != -1:
            quote_end = query.find('"', quote_start + 1)
            if quote_end == -1:
                quote_end = query.find("'", quote_start + 1)
            if quote_end != -1:
                content = query[quote_start + 1:quote_end]
        
        if filename and content:
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                return {
                    "status": "success",
                    "file": filename,
                    "message": f"File {filename} created successfully"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }
        return None

    def _handle_read_file(self, query):
        """Handle file reading commands."""
        words = query.split()
        filename = None
        
        # Find filename
        for i, word in enumerate(words):
            if word == 'file' and i + 1 < len(words):
                filename = words[i + 1]
                break
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                return {
                    "status": "success",
                    "file": filename,
                    "content": content
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }
        return None

    def _handle_write_file(self, query):
        """Handle file writing commands."""
        words = query.split()
        filename = None
        content = None
        
        # Find filename
        for i, word in enumerate(words):
            if word == 'file' and i + 1 < len(words):
                filename = words[i + 1]
                break
        
        # Find content between quotes
        quote_start = query.find('"')
        if quote_start == -1:
            quote_start = query.find("'")
        if quote_start != -1:
            quote_end = query.find('"', quote_start + 1)
            if quote_end == -1:
                quote_end = query.find("'", quote_start + 1)
            if quote_end != -1:
                content = query[quote_start + 1:quote_end]
        
        if filename and content:
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                return {
                    "status": "success",
                    "file": filename,
                    "message": f"File {filename} updated successfully"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }
        return None

    def _handle_append_file(self, query):
        """Handle file append commands."""
        words = query.split()
        filename = None
        content = None
        
        # Find filename after 'to'
        for i, word in enumerate(words):
            if word == 'to' and i + 1 < len(words):
                filename = words[i + 1]
                break
        
        # Find content between quotes
        quote_start = query.find('"')
        if quote_start == -1:
            quote_start = query.find("'")
        if quote_start != -1:
            quote_end = query.find('"', quote_start + 1)
            if quote_end == -1:
                quote_end = query.find("'", quote_start + 1)
            if quote_end != -1:
                content = query[quote_start + 1:quote_end]
        
        if filename and content:
            try:
                with open(filename, 'a') as f:
                    f.write(content)
                return {
                    "status": "success",
                    "file": filename,
                    "message": f"Content appended to {filename} successfully"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }
        return None

    def _handle_delete_file(self, query):
        """Handle file deletion commands."""
        words = query.split()
        filename = None
        
        # Find filename after 'file' or use last word
        for i, word in enumerate(words):
            if word == 'file' and i + 1 < len(words):
                filename = words[i + 1]
                break
        
        if not filename:
            filename = words[-1]
            
        try:
            if os.path.exists(filename):
                os.remove(filename)
                return {
                    "status": "success",
                    "file": filename,
                    "message": f"File {filename} deleted successfully"
                }
            return {
                "status": "error",
                "message": f"File {filename} does not exist"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def _handle_list_files(self):
        """Handle list files command."""
        try:
            files = os.listdir('.')
            return {
                "status": "success",
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def _handle_search_files(self, query):
        """Handle search files command."""
        # Find pattern between quotes
        quote_start = query.find('"')
        if quote_start == -1:
            quote_start = query.find("'")
        if quote_start != -1:
            quote_end = query.find('"', quote_start + 1)
            if quote_end == -1:
                quote_end = query.find("'", quote_start + 1)
            if quote_end != -1:
                pattern = query[quote_start + 1:quote_end]
                try:
                    files = [f for f in os.listdir('.') if pattern in f]
                    return {
                        "status": "success",
                        "pattern": pattern,
                        "files": files,
                        "count": len(files)
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": str(e)
                    }
        return None
    
    def _execute_general_command(self, query):
        """Execute a general command based on the query."""
        # This would require more sophisticated NLU or LLM processing
        # For safety, this should be carefully implemented with proper safeguards
        return "I understand you want to execute a command, but I need to be more specific about what command you're looking for."
    
    def _handle_with_ai(self, user_input):
        """Fallback to AI-based handling."""
        # This would integrate with your AI model
        return "I'd need to use AI to better understand your request. Let me try that for you..."
    
    def _extract_search_term(self, query):
        """Extract a search term from the query."""
        # Very simple implementation - would need more sophisticated NLU
        words = query.split()
        # Look for words after common indicators
        for i, word in enumerate(words):
            if word in ['find', 'search', 'for', 'with', 'named', 'called']:
                if i + 1 < len(words):
                    return words[i + 1]
        # Fallback to the last word
        return words[-1] if words else ""
    
    def _get_api_key(self, key_name):
        """Get API key from environment variable."""
        return os.environ.get(key_name)


class ShellHandler:
    """Handle shell command execution."""
    
    def execute_command(self, command, force_shell=False):
        """Execute a shell command and return the output."""
        try:
            if isinstance(command, list) and not force_shell:
                result = subprocess.run(command, capture_output=True, text=True, check=False)
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Failed to execute command: {str(e)}"
    
    def command_exists(self, command):
        """Check if a command exists."""
        try:
            subprocess.run(['which', command], capture_output=True, text=True, check=False)
            return True
        except:
            return False
    
    def find_folders(self, folder_name, location="~", include_cloud=False):
        """Find folders matching a pattern."""
        system = platform.system().lower()
        try:
            expanded_location = str(Path(location).expanduser())
            
            if system in ['darwin', 'linux']:
                cmd = f'find {expanded_location} -type d -name "*{folder_name}*" 2>/dev/null | head -n 10'
                if system == 'darwin' and include_cloud:
                    # Also check iCloud and Library locations for macOS
                    cmd = f'{cmd}; find ~/Library/Mobile\\ Documents -type d -name "*{folder_name}*" 2>/dev/null | head -n 5'
            elif system == 'windows':
                cmd = f'powershell "Get-ChildItem -Path {expanded_location} -Recurse -Directory -Filter *{folder_name}* | Select-Object -First 10 | Select-Object FullName"'
            
            result = self.execute_command(cmd, force_shell=True)
            return result
        except Exception as e:
            return f"Error finding folders: {str(e)}"
    
    def find_files(self, file_name, location="~"):
        """Find files matching a pattern."""
        system = platform.system().lower()
        try:
            expanded_location = str(Path(location).expanduser())
            
            if system in ['darwin', 'linux']:
                cmd = f'find {expanded_location} -type f -name "*{file_name}*" 2>/dev/null | head -n 10'
            elif system == 'windows':
                cmd = f'powershell "Get-ChildItem -Path {expanded_location} -Recurse -File -Filter *{file_name}* | Select-Object -First 10 | Select-Object FullName"'
            
            result = self.execute_command(cmd, force_shell=True)
            return result
        except Exception as e:
            return f"Error finding files: {str(e)}"


class CommandRegistry:
    """Registry for all terminal commands with platform-specific variants."""
    
    def __init__(self, platform):
        self.platform = platform
        # Initialize command dictionary
        self.commands = {
            # System Information Commands
            "uptime": {
                "darwin": "uptime",
                "linux": "uptime",
                "windows": 'powershell "Get-CimInstance -ClassName Win32_OperatingSystem | Select LastBootUpTime"'
            },
            "memory": {
                "darwin": "vm_stat",
                "linux": "free -h",
                "windows": 'powershell "Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory,TotalVisibleMemorySize"'
            },
            "disk_space": {
                "darwin": "df -h",
                "linux": "df -h",
                "windows": 'powershell "Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free"'
            },
            
            # File/Folder Commands
            "find_folders": {
                "darwin": 'find ~ -type d -name "*{search_term}*" 2>/dev/null | grep -v "Library/|.Trash" | head -n {limit}',
                "linux": 'find ~ -type d -name "*{search_term}*" 2>/dev/null | head -n {limit}',
                "windows": 'powershell "Get-ChildItem -Path $HOME -Recurse -Directory -Filter *{search_term}* | Select-Object -First {limit} | Select-Object FullName"'
            },
            
            # App-Specific Commands
            "notes_folders": {
                "darwin": self._get_macos_notes_command(),
                "linux": 'find ~ -type d -name "*[nN]otes*" 2>/dev/null',
                "windows": 'powershell "Get-ChildItem -Path $HOME -Recurse -Directory -Filter *notes* | Select-Object FullName"'
            },
            
            # YouTube/Media Commands
            "youtube_trending": {
                "darwin": 'curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q=trending&key={api_key}"',
                "linux": 'curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q=trending&key={api_key}"',
                "windows": 'powershell "Invoke-RestMethod -Uri \'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q=trending&key={api_key}\'"'
            }
        }
    
    def _get_macos_notes_command(self):
        """Get comprehensive command to find Notes folders on macOS."""
        # Check multiple locations
        return 'find ~/Library/Containers/com.apple.Notes ~/Library/Group\ Containers/group.com.apple.notes ~/Library/Mobile\ Documents/com~apple~Notes /Applications/Notes.app -type d 2>/dev/null'
    
    def get_command(self, command_type, **params):
        """Get platform-specific command with parameters filled in."""
        if command_type not in self.commands:
            raise ValueError(f"Unknown command type: {command_type}")
            
        if self.platform not in self.commands[command_type]:
            raise ValueError(f"Platform {self.platform} not supported for {command_type}")
            
        cmd_template = self.commands[command_type][self.platform]
        # Fill in any parameters in the command template
        return cmd_template.format(**params)


class OutputProcessor:
    """Process raw command output into human-readable format."""
    
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
    
    def process_windows_uptime(self, raw_output):
        """Process Windows uptime output."""
        # This would require actual implementation to parse Windows-specific format
        # Simplified example
        return f"⏱️ System uptime: {raw_output.strip()}"
    
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
    
    def process_windows_disk_space(self, raw_output):
        """Process Windows disk space output."""
        # Simplified implementation
        return f"💾 Disk space information:\n\n{raw_output.strip()}"
    
    def process_macos_memory(self, raw_output):
        """Process macOS vm_stat output."""
        # Simplified implementation
        return f"🧠 Memory information:\n\n{raw_output.strip()}"
    
    def process_linux_memory(self, raw_output):
        """Process Linux free -h output."""
        # Simplified implementation
        return f"🧠 Memory information:\n\n{raw_output.strip()}"
    
    def process_windows_memory(self, raw_output):
        """Process Windows memory output."""
        # Simplified implementation
        return f"🧠 Memory information:\n\n{raw_output.strip()}"
    
    def process_notes_folders(self, raw_output):
        """Process Notes folder search output."""
        if not raw_output or raw_output.strip() == "":
            return "📝 I didn't find any Notes folders on your system."
            
        folders = raw_output.strip().split("\n")
        
        result = "📝 **Notes Folders**\n\n"
        for folder in folders:
            folder = folder.strip()
            if folder:
                if "iCloud" in folder:
                    result += f"• iCloud Notes: {folder}\n"
                elif "Containers" in folder:
                    result += f"• Local Notes: {folder}\n"
                elif "Notes.app" in folder:
                    result += f"• Notes Application: {folder}\n"
                else:
                    result += f"• {folder}\n"
                    
        return result.strip()
    
    def process_notes_topics(self, raw_output):
        """Process notes topic list output."""
        if not raw_output or raw_output.strip() == "":
            return "📝 I didn't find any Notes topics."
        
        topics = raw_output.strip().split("\n")
        
        result = "📝 **Notes Topics**\n\n"
        for topic in topics:
            topic = topic.strip()
            if topic:
                result += f"• {topic}\n"
        
        return result.strip()
    
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
