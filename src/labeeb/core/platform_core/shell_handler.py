import subprocess
import shlex
import os
import platform
import json
import enum
import re
from typing import Dict, Any, List, Tuple, Optional

"""
This module provides a platform-agnostic shell command execution framework with safety features.
It implements a base shell handler class that can be extended for different operating systems,
with built-in command safety checks, dangerous command detection, and platform-specific adaptations.

Key features:
- Command safety level classification and validation
- Platform-specific command adaptation
- Safe command whitelisting
- Dangerous command detection
- Command execution with timeout support
- Debug logging capabilities

The module uses an enum-based safety level system to categorize commands and provides
methods for executing commands safely while maintaining platform compatibility.

See also: platform_core/mac/shell_handler.py, platform_core/windows/shell_handler.py for platform-specific implementations
"""

class CommandSafetyLevel(enum.Enum):
    """Safety levels for shell commands."""
    SAFE = "SAFE"
    NOT_IN_WHITELIST = "NOT_IN_WHITELIST" 
    POTENTIALLY_DANGEROUS = "POTENTIALLY_DANGEROUS"
    REQUIRES_SHELL_TRUE = "REQUIRES_SHELL_TRUE"
    EMPTY = "EMPTY"
    UNKNOWN = "UNKNOWN"
    JSON_PLAN = "JSON_PLAN"
    SEMI_DANGEROUS = "SEMI_DANGEROUS"

class BaseShellHandler:
    """Base class for platform-specific shell handlers."""
    
    def __init__(self, safe_mode: bool = True, enable_dangerous_command_check: bool = True, 
                 suppress_prompt: bool = False, quiet_mode: bool = False, fast_mode: bool = False):
        """Initialize the shell handler.
        
        Args:
            safe_mode: If True, restricts execution to whitelisted commands
            enable_dangerous_command_check: If True, checks commands against dangerous commands list
            suppress_prompt: If True, does not prompt for confirmation
            quiet_mode: If True, reduces unnecessary terminal output
            fast_mode: If True, doesn't wait for feedback on errors
        """
        if fast_mode:
            safe_mode = False
            enable_dangerous_command_check = False
            
        self.safe_mode = safe_mode
        self.enable_dangerous_command_check = enable_dangerous_command_check
        self.suppress_prompt = suppress_prompt
        self.quiet_mode = quiet_mode
        self.fast_mode = fast_mode
        self.system_platform = platform.system().lower()
        
        # Will be assigned externally
        self.screen_manager = None
        
    def get_safe_commands(self) -> List[str]:
        """Get the list of safe commands for this platform.
        
        Returns:
            List of safe command names
        """
        raise NotImplementedError("Platform-specific implementation required")
        
    def get_dangerous_commands(self) -> List[str]:
        """Get the list of dangerous commands for this platform.
        
        Returns:
            List of dangerous command names
        """
        raise NotImplementedError("Platform-specific implementation required")
        
    def is_command_safe(self, command: str) -> bool:
        """Check if a command is safe to execute.
        
        Args:
            command: The command string to check
            
        Returns:
            True if the command is considered safe, False otherwise
        """
        try:
            command_parts = shlex.split(command)
            return self._is_command_safe(command_parts)
        except ValueError:
            return False
            
    def _is_command_safe(self, command_parts: List[str]) -> bool:
        """Check if command parts are safe.
        
        Args:
            command_parts: List of command parts
            
        Returns:
            True if command is safe, False otherwise
        """
        if not command_parts:
            return False
            
        command_name = command_parts[0]
        safe_commands = self.get_safe_commands()
        
        if command_name in safe_commands:
            return True
            
        # Check for path-like commands
        if '/' in command_name and command_name.split('/')[-1] in safe_commands:
            return True
            
        return False
        
    def is_potentially_dangerous(self, command: str) -> bool:
        """Check if a command is potentially dangerous.
        
        Args:
            command: The command string to check
            
        Returns:
            True if command is potentially dangerous, False otherwise
        """
        try:
            command_parts = shlex.split(command)
            return self._is_potentially_dangerous(command_parts)
        except ValueError:
            return True
            
    def _is_potentially_dangerous(self, command_parts: List[str]) -> bool:
        """Check if command parts are potentially dangerous.
        
        Args:
            command_parts: List of command parts
            
        Returns:
            True if command is potentially dangerous, False otherwise
        """
        if not command_parts:
            return False
            
        command_name = command_parts[0]
        dangerous_commands = self.get_dangerous_commands()
        
        if command_name in dangerous_commands:
            return True
            
        # Check for sudo usage with dangerous commands
        if command_name == 'sudo' and len(command_parts) > 1 and command_parts[1] in dangerous_commands:
            return True
            
        return False
        
    def fix_platform_command(self, command: str) -> str:
        """Fix command for platform-specific requirements.
        
        Args:
            command: The command string to fix
            
        Returns:
            Fixed command string
        """
        return command
        
    def execute_command(self, command: str, force_shell: bool = False, timeout: Optional[int] = None) -> Tuple[int, str, str]:
        """Execute a shell command.
        
        Args:
            command: The command to execute
            force_shell: Whether to force shell execution
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        raise NotImplementedError("Platform-specific implementation required")
        
    def get_current_directory(self) -> str:
        """Get the current working directory.
        
        Returns:
            Current working directory path
        """
        return os.getcwd()
        
    def _log(self, message: str) -> None:
        """Log a message if not in quiet mode.
        
        Args:
            message: Message to log
        """
        if not self.quiet_mode:
            print(message)
            
    def _log_debug(self, message: str) -> None:
        """Log a debug message if not in quiet mode.
        
        Args:
            message: Debug message to log
        """
        if not self.quiet_mode:
            import sys
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, 'log'):
                main_module.log(message, debug_only=True) 