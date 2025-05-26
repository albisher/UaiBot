"""Shell interaction handler for macOS in the Labeeb platform.

This module provides functionality for:
- Terminal command execution
- Shell script management
- Process control and monitoring
- Environment variable handling
- Shell session management

The module implements macOS-specific shell handling while maintaining
compatibility with the core Labeeb shell system.
"""

from typing import List, Tuple, Optional
from ..shell_handler import BaseShellHandler
import subprocess

class MacShellHandler(BaseShellHandler):
    """macOS-specific shell handler implementation."""
    
    def get_safe_commands(self) -> List[str]:
        """Get the list of safe commands for macOS.
        
        Returns:
            List of safe command names
        """
        return [
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
        
    def get_dangerous_commands(self) -> List[str]:
        """Get the list of dangerous commands for macOS.
        
        Returns:
            List of dangerous command names
        """
        return [
            'rm', 'sudo', 'mkfs', 'shutdown', 'reboot', 'dd', 'fdisk', 'kill', 
            'chmod', 'chown', 'chgrp', 'mv', 'cp', 'rmdir', 'ln -s', 'format',
            'diskutil', 'diskpart', 'parted', 'gparted', '> /dev/', '| sudo', 
            'mkfs', 'fsck', 'mount', 'umount', ':(){', 'eval', 'dmesg'
        ]
        
    def execute_command(self, command: str, force_shell: bool = False, timeout: Optional[int] = None) -> Tuple[int, str, str]:
        """Execute a shell command on macOS.
        
        Args:
            command: The command to execute
            force_shell: Whether to force shell execution
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            # Fix command for macOS if needed
            command = self.fix_platform_command(command)
            
            # Execute the command
            process = subprocess.Popen(
                command,
                shell=True if force_shell else False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            return process.returncode, stdout, stderr
            
        except subprocess.TimeoutExpired:
            process.kill()
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
            
    def fix_platform_command(self, command: str) -> str:
        """Fix command for macOS-specific requirements.
        
        Args:
            command: The command string to fix
            
        Returns:
            Fixed command string
        """
        # Add macOS-specific command fixes here
        return command 