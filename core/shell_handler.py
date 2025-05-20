"""
Shell command handling for UaiBot in a modular structure.
This version removes the send_to_screen_session method and uses the ScreenManager instead.
"""
import subprocess
import shlex
import os
import platform
import json
import enum
from core.utils import get_platform_name, run_command
from device_manager.usb_detector import USBDetector
from core.browser_handler import BrowserHandler

try:
    from core.platform_commands import get_platform_command
except ImportError:
    # Define a placeholder if the module is not available
    def get_platform_command(platform, command_type, subtype=None):
        return None

# Define CommandSafetyLevel enumeration to fix the import error
class CommandSafetyLevel(enum.Enum):
    """Safety levels for shell commands."""
    SAFE = "SAFE"
    NOT_IN_WHITELIST = "NOT_IN_WHITELIST" 
    POTENTIALLY_DANGEROUS = "POTENTIALLY_DANGEROUS"
    REQUIRES_SHELL_TRUE = "REQUIRES_SHELL_TRUE"
    EMPTY = "EMPTY"
    UNKNOWN = "UNKNOWN"

# Basic list of commands that are generally safe.
SAFE_COMMAND_WHITELIST = [
    # Basic navigation and file operations
    'ls', 'cd', 'pwd', 'echo', 'cat', 'mkdir', 'rmdir', 'cp', 'mv', 'find', 'grep',
    # Programming and development tools
    'python', 'python3', 'pip', 'git', 'man', 'uname',
    # System information and management
    'df', 'du', 'free', 'top', 'ps', 'kill', 'killall', 'uptime', 'cal', 'date',
    # macOS specific commands
    'osascript', 'screen', 'open', 'softwareupdate', 'caffeinate', 'say',
    # Text editors and viewers
    'nano', 'vi', 'vim', 'less', 'more', 'head', 'tail',
    # Network tools
    'ping', 'curl', 'wget', 'ssh', 'scp', 'telnet', 'netstat', 'ifconfig', 'traceroute', 'nslookup',
    # Text processing
    'grep', 'awk', 'sed', 'sort', 'uniq', 'wc', 'diff', 'pbcopy', 'pbpaste',
    # File management
    'touch', 'ditto', 'chmod', 'chown', 'chgrp', 'ln',
    # System commands
    'history', 'crontab', 'alias', 'which', 'whereis', 'whoami', 'who', 'w', 
    # Advanced macOS commands
    'networksetup', 'airport', 'scutil', 'mdfind', 'diskutil', 'system_profiler', 
    'sw_vers', 'sysctl', 'pmset', 'launchctl', 'defaults', 'plutil', 'hdiutil', 
    'screencapture', 'security', 'xcode-select', 'xcodebuild', 'xcrun', 'codesign', 
    'spctl', 'ioreg', 'pkgutil', 'automator', 'afplay'
]

# Commands that should always require confirmation or be blocked in certain modes.
POTENTIALLY_DANGEROUS_COMMANDS = [
    'rm', 'sudo', 'mkfs', 'shutdown', 'reboot', 'dd', 'fdisk', 'kill', 
    'chmod', 'chown', 'chgrp', 'mv', 'cp', 'rmdir', 'ln -s', 'format',
    'diskutil', 'diskpart', 'parted', 'gparted', '> /dev/', '| sudo', 
    'mkfs', 'fsck', 'mount', 'umount', ':(){', 'eval', 'dmesg'
]

class ShellHandler:
    def __init__(self, safe_mode=True, enable_dangerous_command_check=True, suppress_prompt=False, quiet_mode=False, fast_mode=False):
        """
        Initializes the ShellHandler.
        Args:
            safe_mode (bool): If True, restricts execution to whitelisted commands.
            enable_dangerous_command_check (bool): If True, checks commands against POTENTIALLY_DANGEROUS_COMMANDS.
            suppress_prompt (bool): If True, does not prompt for confirmation.
            quiet_mode (bool): If True, reduces unnecessary terminal output.
            fast_mode (bool): If True, doesn't wait for feedback on errors, exits immediately.
        """
        self.safe_mode = safe_mode
        self.enable_dangerous_command_check = enable_dangerous_command_check
        self.suppress_prompt = suppress_prompt
        self.quiet_mode = quiet_mode
        self.fast_mode = fast_mode
        self.system_platform = platform.system().lower()
        self.platform_name = get_platform_name()
        
        # Will be assigned externally
        self.screen_manager = None
        
        # Create a USB device detector
        self.usb_detector = USBDetector(quiet_mode=quiet_mode)
        
        # Create a browser handler
        self.browser_handler = BrowserHandler(shell_handler=self)
        
        # Use log method instead of direct print
        self._log_debug(f"ShellHandler initialized. Safe mode: {self.safe_mode}, Dangerous command check: {self.enable_dangerous_command_check}, Fast mode: {self.fast_mode}")
    
    def _log(self, message):
        """Print a message if not in quiet mode"""
        if not self.quiet_mode:
            # Check if we're running in main.py context where a log function might be available
            import sys
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, 'log'):
                # Use the main module's log function
                main_module.log(message, debug_only=False)
            else:
                # Fall back to print but only in non-quiet mode
                print(message)

    def _log_debug(self, message):
        """Log debug messages if not in quiet mode"""
        if not self.quiet_mode:
            # Check if we're running in main.py context
            import sys
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, 'log'):
                # Use the main module's log function with debug flag
                main_module.log(message, debug_only=True)
            # For debug messages, we don't print directly even if log function is not available
            # This change ensures debug messages like initialization don't appear unless logged by main
    
    def log(self, message):
        """Print a message if not in quiet mode"""
        if not self.quiet_mode:
            print(message)
    
    # Update safe commands for the current platform
    def _update_safe_commands_for_platform(self):
        """Update safe commands list with platform-specific commands"""
        # Platform-specific commands are already included in the whitelist
        pass
    
    def is_command_safe(self, command):
        """
        Public method to check if a command is safe.
        Forwards to the internal _is_command_safe method after splitting the command.
        
        Args:
            command (str): The command string to check
            
        Returns:
            bool: True if the command is considered safe, False otherwise
        """
        try:
            command_parts = shlex.split(command)
            return self._is_command_safe(command_parts)
        except ValueError:
            # If shlex cannot split (e.g. unmatched quotes), consider unsafe
            return False
        
    def _is_command_safe(self, command_parts):
        """Checks if the command is on the whitelist."""
        if not command_parts:
            return False
        command_name = command_parts[0]

        # Add platform-specific commands to the safe list
        self._update_safe_commands_for_platform()
        
        if command_name in SAFE_COMMAND_WHITELIST:
            return True
        
        # Basic check for path-like commands (e.g. /bin/ls)
        if '/' in command_name and command_name.split('/')[-1] in SAFE_COMMAND_WHITELIST:
            return True

        return False

    def _is_potentially_dangerous(self, command_parts):
        """Checks if the command is in the list of potentially dangerous commands."""
        if not command_parts:
            return False
        command_name = command_parts[0]
        
        if command_name in POTENTIALLY_DANGEROUS_COMMANDS:
            return True
        # Check for sudo usage with another command
        if command_name == 'sudo' and len(command_parts) > 1 and command_parts[1] in POTENTIALLY_DANGEROUS_COMMANDS:
            return True
        return False
    
    def _fix_platform_command(self, command_string):
        """Adjust command based on platform if needed"""
        # Simple pass-through for now, can be extended in the future
        return command_string
    
    def execute_command(self, command, force_shell=False, timeout=None):
        """Execute a shell command safely and return the output."""
        # Use a shorter timeout in fast mode to avoid hanging
        if self.fast_mode and timeout is None:
            timeout = 5  # 5 seconds timeout in fast mode to ensure quicker response
            
        if self.safe_mode and not force_shell:
            # In safe mode, apply more stringent checks
            if not self.is_command_safe(command):
                return f"Error: Command '{command}' is potentially unsafe. Run with --no-safe-mode to override."
        
        # Special handling for common file search patterns
        if command.startswith("cat ") and ".txt" in command:
            # If trying to cat a non-existent file like "cat .txt", convert to a file search
            if command == "cat .txt" or command.endswith("cat *.txt"):
                # Convert to proper file search
                if self.system_platform in ["linux", "darwin"]:
                    command = "find ~ -type f -name '*.txt' -not -path '*/\\.*' 2>/dev/null | head -n 15"
                else:  # Windows
                    command = 'dir /s /b "%USERPROFILE%\\*.txt"'
                    
        # Handle problematic wildcard patterns that can cause excessive recursion
        if "find" in command and "'**'" in command:
            # Replace '**' wildcard with '*' which is safer
            command = command.replace("'**'", "'*'")
            if not self.quiet_mode:
                print(f"Modified search command for safety: {command}")
        
        try:
            # Prefer using shlex.split for secure command execution without shell=True
            if not force_shell and "|" not in command and ">" not in command and "<" not in command and "*" not in command:
                # Can use more secure execution
                args = shlex.split(command)
                
                if not self.quiet_mode:
                    print(f"Executing with shlex: {args}")
                
                process = subprocess.run(
                    args,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False  # Don't raise exception on non-zero return code
                )
            else:
                # Need to use shell=True for commands with special shell syntax
                if not self.quiet_mode:
                    print(f"Using shell=True for command with special syntax: {command}")
                
                if not self.quiet_mode:
                    print(f"Executing with shell=True: {command}")
                
                process = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False  # Don't raise exception on non-zero return code
                )
                
            # Handle the command output
            if process.returncode != 0:
                # Command failed
                if not self.quiet_mode:
                    print(f"Error executing command: {command}")
                    print(f"Return Code: {process.returncode}")
                    print(f"Stderr:\n{process.stderr}")
                
                # For certain search-related commands, provide better alternatives on failure
                if "find" in command and "file" in command.lower():
                    # If a file search failed, provide a more targeted search
                    # This helps when the user asks for txt files but the command fails
                    if ".txt" in command.lower() or "text" in command.lower():
                        if self.system_platform in ["linux", "darwin"]:
                            fallback_cmd = "find ~ -type f -name '*.txt' 2>/dev/null | head -n 10"
                            fallback_process = subprocess.run(fallback_cmd, shell=True, capture_output=True, text=True)
                            if fallback_process.returncode == 0 and fallback_process.stdout.strip():
                                return f"Found text files:\n{fallback_process.stdout}"
                
                # Standard error handling
                if process.stderr:
                    return process.stderr
                else:
                    return f"Command failed with return code {process.returncode}"
            else:
                # Command succeeded
                return process.stdout
                
        except FileNotFoundError:
            return f"Command not found: {command}"
        except PermissionError:
            return f"Permission denied when running: {command}"
        except subprocess.TimeoutExpired:
            if self.fast_mode:
                # In fast mode, return immediately without retrying
                return f"Command timed out after {timeout} seconds. Fast mode enabled, not retrying."
            else:
                # In normal mode, give more info
                return f"Command timed out after {timeout} seconds: {command}"
        except Exception as e:
            return f"Error executing command: {command}\n{str(e)}"
    
    def detect_command_target(self, command, context=""):
        """
        Determine if a command should go to the screen session or local system.
        
        Args:
            command (str): The command to analyze
            context (str): Additional context text that might hint at target
            
        Returns:
            str: "SCREEN", "LOCAL", or "UNKNOWN"
        """
        # If explicit screen indicators in context, prefer screen
        screen_indicators = [
            "screen", "serial", "usb", "terminal session", "device", 
            "remote", "remote system", "remote machine", "other os", 
            "other machine", "screened", "over usb", "over the usb", 
            "connected device", "through screen"
        ]
        
        if any(indicator in context.lower() for indicator in screen_indicators):
            return "SCREEN"
            
        # Check if command is a direct file/navigation command
        nav_commands = ['ls', 'pwd', 'cd', 'dir']
        sys_commands = ['top', 'ps', 'df', 'du', 'uptime', 'date', 'whoami', 'who']
        
        # Split the command to get the base command
        command_parts = command.split()
        base_command = command_parts[0] if command_parts else ""
        
        # Navigation commands with no args are ambiguous
        if base_command in nav_commands and len(command_parts) == 1:
            # Check if we have a USB/serial context
            if any(term in context.lower() for term in ["usb", "serial", "device", "screen"]):
                return "SCREEN"
            else:
                return "LOCAL"
                
        # System information commands typically run locally
        if base_command in sys_commands:
            return "LOCAL"
            
        # Mac-specific commands almost always run locally
        mac_commands = ['open', 'say', 'pbcopy', 'pbpaste', 'networksetup', 'airport',
                        'system_profiler', 'sw_vers', 'defaults', 'osascript']
        if base_command in mac_commands:
            return "LOCAL"
            
        # If we can't determine, default to LOCAL for safety
        return "LOCAL"
    
    def assess_command_safety(self, command_string):
        """
        Assesses the safety level of a command string.
        Returns:
            CommandSafetyLevel: The safety level enum value
        """
        if not command_string.strip():
            return CommandSafetyLevel.EMPTY

        try:
            command_parts = shlex.split(command_string)
            if not command_parts:
                return CommandSafetyLevel.EMPTY
        except ValueError:
            # If shlex cannot split (e.g. unmatched quotes)
            # Consider it potentially requiring shell=True
            return CommandSafetyLevel.REQUIRES_SHELL_TRUE

        if self.enable_dangerous_command_check and self._is_potentially_dangerous(command_parts):
            return CommandSafetyLevel.POTENTIALLY_DANGEROUS
        
        if self.safe_mode and not self._is_command_safe(command_parts):
            return CommandSafetyLevel.NOT_IN_WHITELIST
            
        # Check for shell operators which indicate a complex command
        shell_operators = ['|', '>', '<', '>>', '<<', '&&', '||', ';']
        if any(operator in command_string for operator in shell_operators):
            return CommandSafetyLevel.REQUIRES_SHELL_TRUE
            
        return CommandSafetyLevel.SAFE
        
    # Alias the older method to use the new one for backwards compatibility
    def check_command_safety_level(self, command_string):
        """
        Legacy method that returns the string representation of the safety level.
        Returns:
            str: 'SAFE', 'NOT_IN_WHITELIST', 'POTENTIALLY_DANGEROUS', 'REQUIRES_SHELL_TRUE_ASSESSMENT', or 'EMPTY'.
        """
        safety_level = self.assess_command_safety(command_string)
        
        # Map the enum value to the old string format
        if safety_level == CommandSafetyLevel.REQUIRES_SHELL_TRUE:
            return 'REQUIRES_SHELL_TRUE_ASSESSMENT'  # Match the old naming
        
        return safety_level.value

    def get_usb_devices(self):
        """
        Get a list of available USB devices.
        
        Returns:
            str: Formatted string with device information
        """
        return self.usb_detector.get_usb_devices()
        
    def get_browser_content(self, browser_name=None):
        """
        Get content from browser tabs (titles and URLs).
        
        Args:
            browser_name (str, optional): Specific browser to target
                                         ("chrome", "firefox", "safari", "edge")
        
        Returns:
            str: Formatted browser content or error message
        """
        return self.browser_handler.get_browser_content(browser_name)
    
    def find_folders(self, folder_name, location="~", max_results=20, include_cloud=True):
        """
        Find folders matching a given name pattern.
        
        Args:
            folder_name (str): Name pattern to search for
            location (str): Root directory to start the search
            max_results (int): Maximum number of results to return
            include_cloud (bool): Whether to include cloud storage folders
            
        Returns:
            str: Formatted search results
        """
        # Sanitize input and expand user path
        folder_name = folder_name.replace('"', '\\"').replace("'", "\\'")  # Escape quotes properly
        location = os.path.expanduser(location)
        
        # Check if location exists
        if not os.path.exists(location):
            return f"Error: The specified location '{location}' does not exist."
        
        try:
            # Prepare results containers
            all_folders = []
            cloud_folders = []
            
            # First check for platform-specific notes folders directly without using find command
            if include_cloud and folder_name.lower() in ["notes", "note", "notes app", "apple notes"]:
                self._get_notes_folders(cloud_folders)
                
            # If we're just looking for notes specifically, we might already have what we need
            if folder_name.lower() in ["notes", "note", "notes app", "apple notes"] and cloud_folders:
                # Skip file system search if we already found what was requested
                pass
            else:
                # Use Python's built-in file system functions for safer, more controlled folder search
                # This avoids shell command issues and works better cross-platform
                self._find_folders_natively(folder_name, location, max_results, all_folders)
            
            # Format the output with emojis according to enhancement guidelines
            if not all_folders and not cloud_folders:
                return f"I searched for '{folder_name}' folders but didn't find any matching folders in {location}."
                
            formatted_result = f"I found these folders matching '{folder_name}':\n\n"
            
            # First show cloud folders (if any)
            if cloud_folders:
                if self.system_platform == "darwin":
                    formatted_result += "🌥️  iCloud/macOS:\n\n"
                elif self.system_platform == "windows":
                    formatted_result += "📝  Note Applications:\n\n"
                else:
                    formatted_result += "📝  Notes:\n\n"
                    
                # Show all folders with type and count
                for cf in cloud_folders:
                    formatted_result += f"  • {cf['name']}    {cf['items']}\n"
                        
                formatted_result += "\n"
            
            # Then show filesystem folders if we have any
            if all_folders:
                formatted_result += "💻 Local Filesystem:\n\n"
                for folder in all_folders:
                    formatted_result += f"  • {folder}\n"
                    
                if len(all_folders) >= max_results:
                    formatted_result += f"\n⚠️  Showing first {max_results} results. To see more, specify a narrower search."
            
            return formatted_result
        except Exception as e:
            # In fast mode, show a simple error and exit
            if self.fast_mode:
                return f"Error searching for folders: Could not search for '{folder_name}' folders."
            return f"Error searching for folders: {str(e)}"
            
    def _get_notes_folders(self, cloud_folders):
        """
        Helper method to get platform-specific notes folders without using find command.
        
        Args:
            cloud_folders (list): List to be populated with note folder information.
        """
        if self.system_platform == "darwin":
            # Add Apple Notes app entry directly - hardcoded path
            if os.path.exists("/Applications/Notes.app"):
                cloud_folders.append({
                    "name": "Apple Notes App", 
                    "path": "/Applications/Notes.app", 
                    "type": "Application", 
                    "items": "Apple Notes"
                })
                
            # Add common macOS Notes locations
            for notes_path in [
                "~/Library/Mobile Documents/com~apple~Notes",
                "~/Library/Group Containers/group.com.apple.notes",
                "~/Library/Containers/com.apple.Notes"
            ]:
                path = os.path.expanduser(notes_path)
                if os.path.exists(path):
                    cloud_folders.append({
                        "name": os.path.basename(path), 
                        "path": path, 
                        "type": "macOS", 
                        "items": "Notes"
                    })
        
        elif self.system_platform == "windows":
            # Add Windows Notes locations
            for notes_path in [
                "~/Documents/OneNote Notebooks",
                "~/OneDrive/Documents/OneNote Notebooks",
                "~/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe"
            ]:
                path = os.path.expanduser(notes_path)
                if os.path.exists(path):
                    note_type = "OneNote" if "OneNote" in notes_path else "Sticky Notes"
                    cloud_folders.append({
                        "name": note_type, 
                        "path": path, 
                        "type": "Windows", 
                        "items": note_type
                    })
        
        elif self.system_platform == "linux":
            # Add Linux Notes locations
            for notes_path in [
                "~/.local/share/bijiben",
                "~/.var/app/org.gnome.Notes",
                "~/.config/joplin-desktop"
            ]:
                path = os.path.expanduser(notes_path)
                if os.path.exists(path):
                    note_type = "Joplin" if "joplin" in notes_path.lower() else "GNOME Notes"
                    cloud_folders.append({
                        "name": note_type, 
                        "path": path, 
                        "type": "Linux", 
                        "items": "Notes App"
                    })
                    
    def _find_folders_natively(self, folder_name, location, max_results, result_list):
        """
        Find folders using Python's native file system functions instead of shell commands.
        This is safer, more reliable, and works cross-platform.
        
        Args:
            folder_name (str): Pattern to search for in folder names
            location (str): Root directory to search in
            max_results (int): Maximum number of results to return
            result_list (list): List to be populated with found folders
        """
        # Convert wildcards to lowercase for case-insensitive matching
        folder_pattern = folder_name.lower()
        
        # Handle wildcard cases specially
        is_wildcard = folder_pattern in ["*", "**"]
        
        # Determine search depth based on mode and pattern
        max_depth = 2 if (is_wildcard or self.fast_mode) else 4
        
        # Keep track of results count
        count = 0
        
        # If searching in home, focus on common directories first
        if location == os.path.expanduser("~"):
            common_dirs = ['Documents', 'Downloads', 'Desktop', 'Pictures', 'Music', 'Videos']
            for common_dir in common_dirs:
                common_path = os.path.join(location, common_dir)
                if os.path.exists(common_path) and count < max_results:
                    self._search_directory(common_path, folder_pattern, max_depth, 1, result_list, max_results, is_wildcard)
                    count = len(result_list)
        
        # If we need more results, perform general search
        if count < max_results:
            self._search_directory(location, folder_pattern, max_depth, 0, result_list, max_results, is_wildcard)
    
    def _search_directory(self, root_dir, pattern, max_depth, current_depth, result_list, max_results, is_wildcard=False):
        """
        Recursively search a directory for folders matching a pattern.
        
        Args:
            root_dir (str): Directory to search in
            pattern (str): Pattern to match folder names against
            max_depth (int): Maximum recursion depth
            current_depth (int): Current recursion depth
            result_list (list): List to be populated with results
            max_results (int): Maximum number of results
            is_wildcard (bool): Whether this is a wildcard search
        """
        # Stop if we have enough results or reached max depth
        if len(result_list) >= max_results or current_depth > max_depth:
            return
            
        try:
            # List all entries in the directory
            entries = os.listdir(root_dir)
            
            # Process all directories first (breadth-first approach)
            for entry in entries:
                # Skip hidden entries
                if entry.startswith('.'):
                    continue
                    
                full_path = os.path.join(root_dir, entry)
                
                # Only process directories
                if os.path.isdir(full_path):
                    # For wildcard searches, add all directories
                    # For specific searches, check if pattern is in the name
                    if is_wildcard or pattern in entry.lower():
                        result_list.append(full_path)
                        if len(result_list) >= max_results:
                            return
            
            # Then recurse into subdirectories if we haven't reached max depth
            if current_depth < max_depth:
                for entry in entries:
                    if entry.startswith('.'):
                        continue
                        
                    full_path = os.path.join(root_dir, entry)
                    if os.path.isdir(full_path):
                        self._search_directory(full_path, pattern, max_depth, 
                                              current_depth + 1, result_list, 
                                              max_results, is_wildcard)
                        if len(result_list) >= max_results:
                            return
        except (PermissionError, FileNotFoundError) as e:
            # Skip directories we can't access
            pass
        except Exception as e:
            # Log unexpected errors but continue
            if not self.quiet_mode:
                print(f"Error searching directory {root_dir}: {str(e)}")
    
    def find_files(self, file_pattern, location="~", max_results=20):
        """
        Find files matching a given pattern using Python's native file system functions.
        
        Args:
            file_pattern (str): Pattern to search for (e.g. "*.txt", "enha*.txt")
            location (str): Root directory to start the search
            max_results (int): Maximum number of results to return
            
        Returns:
            str: Formatted search results
        """
        # Sanitize and expand user path
        location = os.path.expanduser(location)
        
        # Check if location exists
        if not os.path.exists(location):
            return f"Error: The specified location '{location}' does not exist."
        
        try:
            # Prepare results container
            matching_files = []
            
            # Convert glob pattern to regex pattern for matching
            import fnmatch
            import re
            
            # Extract extension from pattern for better targeting
            is_extension_search = False
            target_extension = None
            
            # Check if this is a file extension search (*.ext pattern)
            if file_pattern.startswith('*.'):
                target_extension = file_pattern[2:].lower()
                is_extension_search = True
            
            # Create regex pattern from glob pattern
            if '*' in file_pattern or '?' in file_pattern:
                regex_pattern = fnmatch.translate(file_pattern)
                pattern_obj = re.compile(regex_pattern, re.IGNORECASE)
            else:
                # If no wildcards, do a simple substring search
                pattern_obj = None
            
            # Determine search depth based on mode
            max_depth = 3 if self.fast_mode else 5
            
            # First, search in common document locations for any type of file
            # This provides faster results for common file locations
            common_paths = []
            home = os.path.expanduser('~')
            
            for common_dir in ['Documents', 'Downloads', 'Desktop']:
                path = os.path.join(home, common_dir)
                if os.path.exists(path):
                    common_paths.append(path)
            
            # If location is not home or a custom path, add it to common paths
            # to ensure we search the user's specified location first
            if location != home and location not in common_paths:
                common_paths.insert(0, location)
            
            # Search in all designated locations
            for path in common_paths:
                self._search_files_directory(path, file_pattern, pattern_obj, 
                                           matching_files, max_results, 0, max_depth,
                                           target_extension=target_extension)
                # Stop if we've found enough files
                if len(matching_files) >= max_results:
                    break
            
            # If we haven't found enough results and location wasn't in common paths,
            # search the specified location (to be thorough)
            if len(matching_files) < max_results and location not in common_paths:
                self._search_files_directory(location, file_pattern, pattern_obj, 
                                          matching_files, max_results, 0, max_depth,
                                          target_extension=target_extension)
            
            # Format the results
            if not matching_files:
                return f"No files matching '{file_pattern}' were found in {location}."
            
            formatted_result = f"I found these files matching '{file_pattern}':\n\n"
            formatted_result += "💻 Local Filesystem:\n\n"
            
            for file_path in matching_files:
                # Get file size in human-readable format
                try:
                    size = os.path.getsize(file_path)
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.1f} KB"
                    else:
                        size_str = f"{size/(1024*1024):.1f} MB"
                except:
                    size_str = "unknown size"
                    
                # Add file info to results
                formatted_result += f"  • {file_path} ({size_str})\n"
                
            if len(matching_files) >= max_results:
                formatted_result += f"\n⚠️  Showing first {max_results} results. To see more, specify a narrower search."
            
            return formatted_result
            
        except Exception as e:
            # In fast mode, show a simple error
            if self.fast_mode:
                return f"Error searching for files: Could not search for '{file_pattern}' files."
            return f"Error searching for files: {str(e)}"
    
    def _search_files_directory(self, directory, file_pattern, pattern_obj, result_list, max_results, current_depth, max_depth, target_extension=None):
        """
        Recursively search a directory for files matching a pattern.
        
        Args:
            directory (str): Directory to search in
            file_pattern (str): Original glob pattern (for simple comparisons)
            pattern_obj: Compiled regex pattern object for matching
            result_list (list): List to populate with results
            max_results (int): Maximum number of results
            current_depth (int): Current recursion depth
            max_depth (int): Maximum recursion depth
            target_extension (str, optional): Specific file extension to look for
        """
        # Stop if we have enough results or reached max depth
        if len(result_list) >= max_results or current_depth > max_depth:
            return
            
        try:
            # List all entries in the directory
            entries = os.listdir(directory)
            
            # Process all files first
            for entry in entries:
                # Skip hidden files
                if entry.startswith('.'):
                    continue
                    
                full_path = os.path.join(directory, entry)
                
                # Process regular files
                if os.path.isfile(full_path):
                    # Fast path: if target_extension is specified, check extension first
                    if target_extension:
                        _, ext = os.path.splitext(entry)
                        if ext.lower() != f'.{target_extension}' and ext.lower() != target_extension:
                            continue
                    
                    # Match against the pattern
                    if pattern_obj:
                        # Use regex pattern for wildcard matching
                        if pattern_obj.match(entry):
                            result_list.append(full_path)
                            if len(result_list) >= max_results:
                                return
                    else:
                        # Use simple substring matching
                        if file_pattern.lower() in entry.lower():
                            result_list.append(full_path)
                            if len(result_list) >= max_results:
                                return
            
            # Then recurse into subdirectories
            if current_depth < max_depth:
                for entry in entries:
                    if entry.startswith('.'):
                        continue
                        
                    full_path = os.path.join(directory, entry)
                    if os.path.isdir(full_path):
                        self._search_files_directory(full_path, file_pattern, pattern_obj,
                                                  result_list, max_results, current_depth + 1, max_depth,
                                                  target_extension=target_extension)
                        if len(result_list) >= max_results:
                            return
        except (PermissionError, FileNotFoundError):
            # Skip directories we can't access
            pass
        except Exception as e:
            # Log unexpected errors but continue searching
            if not self.quiet_mode:
                print(f"Error searching directory {directory}: {str(e)}")
    
    def get_current_directory(self):
        """Get the current working directory in a user-friendly format."""
        try:
            # Get the current directory
            if self.system_platform == 'windows':
                command = 'cd'
            else:
                command = 'pwd'
                
            cwd = self.execute_command(command).strip()
            home_path = os.path.expanduser('~')
            
            # Format the path to show ~ for home directory
            if cwd.startswith(home_path):
                cwd = cwd.replace(home_path, '~', 1)
                
            return f"📁 Current directory: {cwd}"
        except Exception as e:
            return f"❌ Error getting current directory: {str(e)}"
        
    def handle_directory_query(self, query):
        """Handle various forms of directory-related queries."""
        query_lower = query.lower()
        
        # Handle different types of directory queries
        if any(term in query_lower for term in ['where am i', 'current directory', 'pwd', 'active folder', 'current folder']):
            return self.get_current_directory()
            
        # List files in current directory
        elif any(term in query_lower for term in ['show files', 'list files', 'what files', 'files in current']):
            command = 'ls -la' if self.system_platform != 'windows' else 'dir'
            result = self.execute_command(command)
            return f"📋 Files in current directory:\n{result}"
            
        # General directory operations
        else:
            return self.get_current_directory()
