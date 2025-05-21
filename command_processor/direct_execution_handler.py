"""
Direct command execution handling module for UaiBot.
Handles execution of direct shell commands.
"""
import logging
from typing import List

# Set up logging
logger = logging.getLogger(__name__)

class DirectExecutionHandler:
    def __init__(self, shell_handler, quiet_mode: bool = False):
        """
        Initialize the DirectExecutionHandler.
        
        Args:
            shell_handler: Shell handler instance for executing commands
            quiet_mode (bool): If True, reduces terminal output
        """
        self.shell_handler = shell_handler
        self.quiet_mode = quiet_mode
        
        # Common terminal commands
        self.common_commands: List[str] = [
            # File & directory operations
            'ls', 'pwd', 'cd', 'mkdir', 'rmdir', 'cp', 'mv', 'rm', 'touch', 'cat', 'find',
            # Text viewing/editing
            'more', 'less', 'head', 'tail', 'nano', 'vi', 'vim', 'grep', 'awk', 'sed',
            # System info
            'top', 'ps', 'kill', 'killall', 'df', 'du', 'free', 'uptime', 'date', 'cal', 'who', 'whoami',
            # Networking
            'ping', 'curl', 'wget', 'ssh', 'scp', 'ifconfig', 'netstat', 'traceroute', 'nslookup',
            # macOS specific
            'open', 'pbcopy', 'pbpaste', 'say', 'ditto', 'mdfind', 'diskutil',
            # Miscellaneous
            'echo', 'history', 'man', 'clear', 'alias', 'crontab'
        ]
    
    def handle_direct_execution(self, command: str) -> str:
        """
        Handle direct command execution.
        
        Args:
            command (str): The command to execute
            
        Returns:
            str: Command output or error message
        """
        # If it starts with !, remove it before execution
        if command.startswith("!"):
            command = command[1:].strip()
        
        # Check if it's a common command
        if command.split()[0] in self.common_commands:
            self.log(f"Executing command: {command}")
            return self._try_direct_execution(command)
        
        return ""
    
    def _try_direct_execution(self, command: str) -> str:
        """
        Try to execute a command directly.
        
        Args:
            command (str): The command to execute
            
        Returns:
            str: Command output or error message
        """
        try:
            return self.shell_handler.execute_command(command)
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return f"Error executing command: {str(e)}"
    
    def log(self, message: str) -> None:
        """Print a message if not in quiet mode"""
        if not self.quiet_mode:
            print(message) 