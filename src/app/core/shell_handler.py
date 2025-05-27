"""
Shell command handling for Labeeb in a modular structure.
This version removes the send_to_screen_session method and uses the ScreenManager instead.
"""
import subprocess
import shlex
import os
import json
import enum
import re
from typing import Dict, Any, List, Tuple, Optional
from src.app.core.platform_core.platform_utils import get_platform_name
from src.app.core.device_manager.usb_detector import USBDetector
from src.app.core.browser_handler import BrowserHandler
from src.app.core.file_search import FileSearch
from src.app.core.platform_core.platform_manager import PlatformManager

# Define CommandSafetyLevel enumeration to fix the import error
class CommandSafetyLevel(enum.Enum):
    """Safety levels for shell commands."""
    SAFE = "SAFE"
    NOT_IN_WHITELIST = "NOT_IN_WHITELIST" 
    POTENTIALLY_DANGEROUS = "POTENTIALLY_DANGEROUS"
    REQUIRES_SHELL_TRUE = "REQUIRES_SHELL_TRUE"
    EMPTY = "EMPTY"
    UNKNOWN = "UNKNOWN"
    JSON_PLAN = "JSON_PLAN"  # New type for JSON plans
    SEMI_DANGEROUS = "SEMI_DANGEROUS"  # New type for commands that need extra verification

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
        # Get platform-specific shell handler
        platform_manager = PlatformManager()
        self._platform_handler = platform_manager.get_handler('shell')
        
        if self._platform_handler is None:
            raise NotImplementedError(f"No shell handler available for platform {platform_manager.get_platform()}")
            
        # Initialize platform handler with our settings
        self._platform_handler.safe_mode = safe_mode
        self._platform_handler.enable_dangerous_command_check = enable_dangerous_command_check
        self._platform_handler.suppress_prompt = suppress_prompt
        self._platform_handler.quiet_mode = quiet_mode
        self._platform_handler.fast_mode = fast_mode
        
        # Create a USB device detector
        self.usb_detector = USBDetector(quiet_mode=quiet_mode)
        
        # Create a browser handler
        self.browser_handler = BrowserHandler(shell_handler=self)
        
        # Create a FileSearch instance
        self.file_search = FileSearch(quiet_mode=quiet_mode)
        
        # Will be assigned externally
        self.screen_manager = None
        
        self._log_debug(f"ShellHandler initialized. Safe mode: {safe_mode}, Dangerous command check: {enable_dangerous_command_check}, Fast mode: {fast_mode}")
    
    def _log(self, message):
        """Print a message if not in quiet mode"""
        if not self._platform_handler.quiet_mode:
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
        if not self._platform_handler.quiet_mode:
            # Check if we're running in main.py context
            import sys
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, 'log'):
                # Use the main module's log function with debug flag
                main_module.log(message, debug_only=True)
    
    def is_command_safe(self, command):
        """
        Public method to check if a command is safe.
        Forwards to the platform-specific handler.
        
        Args:
            command (str): The command string to check
            
        Returns:
            bool: True if the command is considered safe, False otherwise
        """
        return self._platform_handler.is_command_safe(command)
    
    def is_potentially_dangerous(self, command):
        """
        Public method to check if a command is potentially dangerous.
        Forwards to the platform-specific handler.
        
        Args:
            command (str): The command string to check
            
        Returns:
            bool: True if the command is potentially dangerous, False otherwise
        """
        return self._platform_handler.is_potentially_dangerous(command)
    
    def execute_command(self, command, force_shell=False, timeout=None):
        """
        Execute a shell command.
        Forwards to the platform-specific handler.
        
        Args:
            command (str): The command to execute
            force_shell (bool): Whether to force shell execution
            timeout (int): Command timeout in seconds
            
        Returns:
            Tuple[int, str, str]: (return_code, stdout, stderr)
        """
        return self._platform_handler.execute_command(command, force_shell, timeout)
    
    def get_current_directory(self):
        """
        Get the current working directory.
        Forwards to the platform-specific handler.
        
        Returns:
            str: Current working directory path
        """
        return self._platform_handler.get_current_directory()
    
    def get_usb_devices(self):
        """Get list of connected USB devices."""
        return self.usb_detector.get_connected_devices()
    
    def get_browser_content(self, browser_name=None):
        """Get content from browser."""
        return self.browser_handler.get_content(browser_name)
    
    def find_folders(self, folder_name, location="~", max_results=20, include_cloud=True):
        """Find folders matching the given name."""
        return self.file_search.find_folders(folder_name, location, max_results, include_cloud)
    
    def find_files(self, file_pattern, location="~", max_results=20):
        """Find files matching the given pattern."""
        return self.file_search.find_files(file_pattern, location, max_results)
    
    def handle_directory_query(self, query):
        """Handle directory-related queries."""
        return self.file_search.handle_query(query)
