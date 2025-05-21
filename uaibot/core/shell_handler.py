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
from uaibot.utils import get_platform_name, run_command
from uaibot.core.device_manager.usb_detector import USBDetector
from uaibot.core.browser_handler import BrowserHandler
from uaibot.core.file_search import FileSearch

try:
    from uaibot.core.platform_commands import get_platform_command
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
        
        # Create a FileSearch instance
        self.file_search = FileSearch(quiet_mode=quiet_mode)
    
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
        return self.file_search.find_folders(folder_name, location, max_results)
    
    def find_files(self, file_pattern, location="~", max_results=20):
        """
        Find files matching a given pattern.
        
        This method uses the FileSearch class to find files, providing a safer
        and more reliable way to search compared to shell commands.
        
        Args:
            file_pattern (str): Pattern to search for (e.g. "*.txt")
            location (str): Root directory to start the search
            max_results (int): Maximum number of results to return
            
        Returns:
            str: Formatted search results
        """
        return self.file_search.find_files(file_pattern, location, max_results)
    
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
