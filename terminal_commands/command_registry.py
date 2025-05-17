"""
Registry for terminal commands with platform-specific variants.
"""
import platform
import os

class CommandRegistry:
    """Registry for all terminal commands with platform-specific variants."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        if self.platform == 'darwin':
            self.platform = 'macos'
        
        # Initialize command dictionary
        self.commands = {
            # System Information Commands
            "uptime": {
                "macos": "uptime",
                "linux": "uptime",
                "windows": 'powershell "Get-CimInstance -ClassName Win32_OperatingSystem | Select LastBootUpTime"'
            },
            "memory": {
                "macos": "vm_stat",
                "linux": "free -h",
                "windows": 'powershell "Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory,TotalVisibleMemorySize"'
            },
            "disk_space": {
                "macos": "df -h",
                "linux": "df -h",
                "windows": 'powershell "Get-PSDrive -PSProvider FileSystem | Select-Object Name,Used,Free"'
            },
            
            # Notes App Commands - Fixed with correct AppleScript syntax for macOS
            "notes_topics": {
                "macos": """osascript -e 'tell application "Notes" to get name of every folder'""",
                "linux": 'find ~ -type d -name "*[nN]otes*" 2>/dev/null',
                "windows": 'powershell "Get-ChildItem -Path $HOME -Recurse -Directory -Filter *notes* | Select-Object FullName"'
            },
            "notes_folders": {
                "macos": """osascript -e 'tell application "Notes" to get name of every folder'""",
                "linux": 'find ~ -type d -name "*[nN]otes*" 2>/dev/null',
                "windows": 'powershell "Get-ChildItem -Path $HOME -Recurse -Directory -Filter *notes* | Select-Object FullName"'
            },
            "notes_count": {
                "macos": """osascript -e 'tell application "Notes" to get the count of notes'""",
                "linux": 'echo "Notes count not available on Linux"',
                "windows": 'echo "Notes count not available on Windows"'
            },
            "notes_list": {
                "macos": """osascript -e 'tell application "Notes" to get name of every note'""",
                "linux": 'echo "Notes list not available on Linux"',
                "windows": 'echo "Notes list not available on Windows"'
            },

            # File/Folder Commands
            "find_folders": {
                "macos": 'find ~ -type d -name "*{search_term}*" 2>/dev/null | grep -v "Library/|.Trash" | head -n {limit}',
                "linux": 'find ~ -type d -name "*{search_term}*" 2>/dev/null | head -n {limit}',
                "windows": 'powershell "Get-ChildItem -Path $HOME -Recurse -Directory -Filter *{search_term}* | Select-Object -First {limit} | Select-Object FullName"'
            }
        }
    
    def get_command(self, command_type, **params):
        """Get platform-specific command with parameters filled in."""
        if command_type not in self.commands:
            raise ValueError(f"Unknown command type: {command_type}")
            
        if self.platform not in self.commands[command_type]:
            raise ValueError(f"Platform {self.platform} not supported for {command_type}")
            
        cmd_template = self.commands[command_type][self.platform]
        # Fill in any parameters in the command template
        if params:
            return cmd_template.format(**params)
        return cmd_template
