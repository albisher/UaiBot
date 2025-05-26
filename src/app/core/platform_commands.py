"""
DEPRECATED: Platform-specific command utilities have been moved to platform_core/platform_manager.py.
Use PlatformManager for all platform/OS detection and command logic.
"""

# Deprecated stub for backward compatibility
from platform_core.platform_manager import PlatformManager

import platform
import os
import shlex
import re
from typing import Dict, List, Optional, Tuple, Union

class PlatformCommands:
    """Handles platform-specific command generation and execution."""
    
    def __init__(self):
        """Initialize the platform detection and set appropriate commands."""
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_macos = self.system == "darwin"
        self.is_linux = self.system == "linux"
        
        # Detect Linux distribution if on Linux
        self.linux_distro = None
        self.is_ubuntu = False
        if self.is_linux:
            try:
                if os.path.exists('/etc/os-release'):
                    with open('/etc/os-release', 'r') as f:
                        os_data = f.read()
                        if 'ubuntu' in os_data.lower():
                            self.linux_distro = "ubuntu"
                            self.is_ubuntu = True
                        elif 'debian' in os_data.lower():
                            self.linux_distro = "debian"
                        elif 'fedora' in os_data.lower():
                            self.linux_distro = "fedora"
                        elif 'centos' in os_data.lower() or 'rhel' in os_data.lower():
                            self.linux_distro = "rhel"
                        elif 'arch' in os_data.lower():
                            self.linux_distro = "arch"
            except Exception:
                pass  # Fallback to generic Linux if detection fails
        
        # Detect the current shell
        self.shell = os.environ.get('SHELL', '').split('/')[-1]
        if not self.shell and self.is_windows:
            self.shell = 'cmd.exe'
        
    def get_system_info(self) -> Dict[str, str]:
        """Get basic system information."""
        info = {
            'os': platform.system(),
            'version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'kernel_release': platform.release(),
        }
        
        if self.is_linux and self.linux_distro:
            info['linux_distribution'] = self.linux_distro
        
        return info
    
    def get_notes_command(self, action: str, search_term: Optional[str] = None) -> str:
        """Generate appropriate notes-related commands for the current platform."""
        if action == "list":
            if self.is_macos:
                return """osascript -e 'tell application "Notes" to get name of every note'"""
            elif self.is_linux:
                # Ubuntu-specific approach
                if self.is_ubuntu:
                    return 'find ~ -name "*.note" -o -name "*.txt" | grep -i note | head -n 15'
                # Generic Linux approach
                return 'find ~ -name "*.txt" -o -name "*.md" | grep -i note | head -n 15'
            else:  # Windows
                return 'dir /s /b "%USERPROFILE%\\*.txt" | findstr /i "note"'
                
        elif action == "count":
            if self.is_macos:
                return """osascript -e 'tell application "Notes" to get the count of notes'"""
            elif self.is_linux:
                if self.is_ubuntu:
                    return 'find ~ -name "*.note" -o -name "*.txt" | grep -i note | wc -l'
                return 'find ~ -name "*.txt" -o -name "*.md" | grep -i note | wc -l'
            else:  # Windows
                return 'dir /s /b "%USERPROFILE%\\*.txt" | findstr /i "note" | find /c /v ""'
                
        elif action == "open":
            if self.is_macos:
                return 'open -a Notes'
            elif self.is_linux:
                if self.is_ubuntu:
                    return 'gnome-text-editor'  # Ubuntu's text editor
                # Try various note applications that might be installed
                return 'xdg-open ~/Documents'  # Fallback to opening Documents folder
            else:  # Windows
                return 'start notepad'
                
        elif action == "search" and search_term:
            safe_term = shlex.quote(search_term)
            if self.is_macos:
                return f"""osascript -e 'tell application "Notes" to get name of notes where name contains "{search_term}" or body contains "{search_term}"'"""
            elif self.is_linux:
                if self.is_ubuntu:
                    return f'find ~ -name "*.note" -o -name "*.txt" | xargs grep -l "{safe_term}" 2>/dev/null | head -n 10'
                return f'find ~ -name "*.txt" -o -name "*.md" | xargs grep -l "{safe_term}" 2>/dev/null | head -n 10'
            else:  # Windows
                return f'findstr /s /i /m "{search_term}" "%USERPROFILE%\\*.txt"'
        
        # Fallback for unknown actions
        return f"echo 'Notes {action} not supported on {platform.system()}'"
    
    def get_file_search_command(self, search_type: str, search_term: str, location: Optional[str] = None) -> str:
        """Generate file/folder search commands based on platform."""
        # Sanitize the search term and location
        safe_term = re.sub(r'[^\w\s.-]', '', search_term)  # Remove special chars
        
        # Default location if none specified
        if not location:
            if self.is_windows:
                location = '%USERPROFILE%'
            else:
                location = '~'
        
        # Sanitize location too
        safe_location = location
        if not self.is_windows:  # For non-Windows systems
            safe_location = shlex.quote(location)
        
        if search_type == "file":
            if self.is_linux or self.is_macos:
                # Fix the search pattern - was incorrectly using Documents as part of the name
                return f"find {safe_location} -type f -name '*{safe_term}*' -not -path '*/\\.*' 2>/dev/null | head -n 15"
            else:  # Windows
                return f'powershell "Get-ChildItem -Path {safe_location} -Recurse -File -Filter *{safe_term}* | Select-Object -First 15 | ForEach-Object {{$_.FullName}}"'
        
        elif search_type == "folder":
            if self.is_linux or self.is_macos:
                return f"find {safe_location} -type d -name '*{safe_term}*' -not -path '*/\\.*' 2>/dev/null | head -n 15"
            else:  # Windows
                return f'powershell "Get-ChildItem -Path {safe_location} -Recurse -Directory -Filter *{safe_term}* | Select-Object -First 15 | ForEach-Object {{$_.FullName}}"'
            
        # Default case
        return f"echo 'Unknown search type: {search_type}'"
    
    def get_system_status_command(self, status_type: str) -> str:
        """Generate system status commands based on platform."""
        if status_type == "uptime":
            if self.is_linux or self.is_macos:
                return "uptime"
            else:  # Windows
                return "net statistics workstation | findstr Statistics"
                
        elif status_type == "memory":
            if self.is_macos:
                return "vm_stat && top -l 1 | grep PhysMem"
            elif self.is_linux:
                return "free -h"
            else:  # Windows
                return "systeminfo | findstr /C:\"Total Physical Memory\" /C:\"Available Physical Memory\""
                
        elif status_type == "disk":
            if self.is_linux or self.is_macos:
                return "df -h"
            else:  # Windows
                return "wmic logicaldisk get deviceid,volumename,size,freespace"
                
        elif status_type == "cpu":
            if self.is_macos:
                return "top -l 1 | head -n 10"
            elif self.is_linux:
                return "top -bn1 | head -n 10"
            else:  # Windows
                return "wmic cpu get name, loadpercentage /value"
                
        # Summary - combines multiple commands
        elif status_type == "summary":
            if self.is_linux:
                return "echo 'System: ' $(uname -a) && echo '\nUptime: ' $(uptime) && echo '\nMemory: ' && free -h && echo '\nDisk: ' && df -h | grep -v 'tmpfs|udev'"
            elif self.is_macos:
                return "echo 'System: ' $(uname -a) && echo '\nUptime: ' $(uptime) && echo '\nMemory: ' && vm_stat && echo '\nDisk: ' && df -h"
            else:  # Windows
                return "systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\" /C:\"System Manufacturer\" /C:\"System Model\" /C:\"System Type\" /C:\"Total Physical Memory\" /C:\"Available Physical Memory\""
                
        # Default to uptime if unknown status type
        if self.is_linux or self.is_macos:
            return "uptime"
        else:  # Windows
            return "net statistics workstation | findstr Statistics"
    
    def get_create_file_command(self, filename: str, content: Optional[str] = None, location: Optional[str] = None) -> str:
        """Generate command to create a file with content."""
        # Sanitize the filename
        safe_filename = re.sub(r'[^\w\s.-]', '', filename)  # Remove special chars except dot, hyphen, underscore
        
        # Default location if none specified
        if not location:
            if self.is_windows:
                location = '%USERPROFILE%\\Desktop'
            else:
                location = '~/Desktop'
        
        # Handle special location names
        if location.lower() == 'desktop':
            if self.is_windows:
                location = '%USERPROFILE%\\Desktop'
            else:
                location = '~/Desktop'
                
        elif location.lower() == 'documents':
            if self.is_windows:
                location = '%USERPROFILE%\\Documents'
            else:
                location = '~/Documents'
                
        elif location.lower() == 'downloads':
            if self.is_windows:
                location = '%USERPROFILE%\\Downloads'
            else:
                location = '~/Downloads'
        
        # Expand tilde to full home path for Linux/Mac
        if not self.is_windows and location.startswith('~'):
            expanded_location = os.path.expanduser(location)
            if os.path.exists(expanded_location):
                location = expanded_location
        
        # Create full path
        if self.is_windows:
            full_path = f"{location}\\{safe_filename}"
        else:
            full_path = f"{location}/{safe_filename}"
            
        # If no content specified, create empty file
        if not content:
            if self.is_linux or self.is_macos:
                return f"touch {shlex.quote(full_path)}"
            else:  # Windows
                return f'type nul > "{full_path}"'
                
        # With content: escape and write
        safe_content = content.replace("'", "''").replace('"', '\\"')
        if self.is_linux or self.is_macos:
            # For Linux/Mac, use echo with single quotes for most reliable escaping
            # The tr command ensures newlines are preserved if the content has them
            if '\n' in safe_content:
                # For multiline content, use a here-document
                return f"cat > {shlex.quote(full_path)} << 'EOT'\n{safe_content}\nEOT"
            else:
                # For single line content, use echo
                return f"echo '{safe_content}' > {shlex.quote(full_path)}"
        else:  # Windows
            # Use echo for single line, or a temp file approach for multiline
            if '\n' in safe_content:
                # Fix: Handle the backslash in f-strings properly
                formatted_content = safe_content.replace("\n", "^& echo ")
                return f'echo {formatted_content} > "{full_path}"'
            else:
                return f'echo {safe_content} > "{full_path}"'
            
    def get_open_command(self, item: str, with_app: Optional[str] = None) -> str:
        """Generate command to open a file, folder, or application."""
        # Sanitize input
        safe_item = shlex.quote(item) if not self.is_windows else item
        
        # Check if item is a URL
        is_url = item.startswith(('http://', 'https://'))
        
        # Check if item is a path
        is_path = ('/' in item) if not self.is_windows else ('\\' in item)
        
        # MacOS commands
        if self.is_macos:
            if with_app:
                safe_app = shlex.quote(with_app)
                return f"open -a {safe_app} {safe_item}"
            elif is_url:
                return f"open {safe_item}"
            elif is_path:
                return f"open {safe_item}"
            else:
                # Assume it's an application
                return f"open -a {safe_item}"
                
        # Linux commands
        elif self.is_linux:
            if is_url:
                return f"xdg-open {safe_item}"
            elif is_path:
                return f"xdg-open {safe_item}"
            else:
                # Try to launch as an application
                return f"{item.lower()} & 2>/dev/null || xdg-open {safe_item}"
                
        # Windows commands
        else:
            if is_url:
                return f"start {safe_item}"
            else:
                return f"start \"\" \"{item}\""
                
    def get_platform_info(self) -> Dict[str, Union[str, bool]]:
        """Get detailed platform information."""
        return {
            "system": self.system,
            "is_windows": self.is_windows,
            "is_macos": self.is_macos,
            "is_linux": self.is_linux,
            "linux_distro": self.linux_distro,
            "is_ubuntu": self.is_ubuntu,
            "shell": self.shell,
            "version": platform.version(),
            "architecture": platform.machine()
        }

# Example usage
if __name__ == "__main__":
    platform_cmds = PlatformCommands()
    print(f"Detected platform: {platform_cmds.get_platform_info()}")
    
    # Example of getting notes command
    print(f"Notes list command: {platform_cmds.get_notes_command('list')}")
    
    # Example of file search
    print(f"Search for 'report' files: {platform_cmds.get_file_search_command('file', 'report')}")
    
    # Example of system status
    print(f"Memory status: {platform_cmds.get_system_status_command('memory')}")
