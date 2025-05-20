"""
Command Logger Module

Handles logging for command processing, especially for requests that
need implementation or generated errors.
"""

import os
import time
import logging
import platform
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CommandLogger:
    """Logs command processing information for analysis and improvement."""
    
    def __init__(self, log_dir: str = None):
        """
        Initialize the command logger.
        
        Args:
            log_dir: Directory to store logs (default: project_root/logs)
        """
        self.log_dir = log_dir or self._get_default_log_dir()
        self._ensure_log_dir()
        
    def _get_default_log_dir(self) -> str:
        """Get the default log directory location."""
        # Try different potential locations
        potential_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs'),
            os.path.join(os.path.expanduser('~'), '.uaibot', 'logs'),
            '/tmp/uaibot_logs'
        ]
        
        # Use first writable path
        for path in potential_paths:
            try:
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                test_file = os.path.join(path, '.write_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                return path
            except (IOError, PermissionError):
                continue
                
        # If all else fails, use current directory
        return os.path.join(os.getcwd(), 'logs')
        
    def _ensure_log_dir(self):
        """Ensure the log directory exists."""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create log directory: {e}")
            # Fall back to temp directory if we can't create the log dir
            self.log_dir = '/tmp/uaibot_logs'
            os.makedirs(self.log_dir, exist_ok=True)
    
    def log_implementation_needed(self, request: str, error_message: str, details: Dict[str, Any] = None) -> bool:
        """
        Log a command that needs implementation.
        
        Args:
            request: The original user request
            error_message: Error message from AI
            details: Additional details about the implementation needed
            
        Returns:
            Success flag
        """
        try:
            log_file = os.path.join(self.log_dir, 'implementation_needed.log')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            system_info = f"{platform.system()} {platform.release()}"
            
            # Format details if provided
            details_str = ""
            if details:
                # Format requirements as a list
                requirements = details.get('requirements', [])
                if requirements:
                    details_str += "\n  Requirements:"
                    for i, req in enumerate(requirements, 1):
                        details_str += f"\n    {i}. {req}"
                        
                # Add complexity if available
                complexity = details.get('complexity', 'unknown')
                if complexity:
                    details_str += f"\n  Complexity: {complexity}"
                    
                # Add reason if available
                reason = details.get('reason', '')
                if reason and reason != "Unknown reason":
                    details_str += f"\n  Reason: {reason}"
            
            # Construct the log entry
            log_entry = f"[{timestamp}] [{system_info}] REQUEST: {request}\nERROR: {error_message}{details_str}\n\n"
            
            # Write to log file
            with open(log_file, 'a') as f:
                f.write(log_entry)
            
            return True
        except Exception as e:
            logger.error(f"Failed to log implementation needed: {e}")
            return False
            
    def log_command_execution(self, request: str, command: str, success: bool, output: str) -> bool:
        """
        Log information about executed commands for analysis.
        
        Args:
            request: Original user request
            command: Command that was executed
            success: Whether execution was successful
            output: Command output
            
        Returns:
            Success flag
        """
        try:
            log_file = os.path.join(self.log_dir, 'command_executions.log')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Truncate output if it's too long
            if len(output) > 500:
                output = output[:500] + "... [truncated]"
                
            status = "SUCCESS" if success else "FAILURE"
            
            # Construct the log entry
            log_entry = (f"[{timestamp}] [{status}]\n"
                        f"REQUEST: {request}\n"
                        f"COMMAND: {command}\n"
                        f"OUTPUT: {output}\n\n")
            
            # Write to log file
            with open(log_file, 'a') as f:
                f.write(log_entry)
            
            return True
        except Exception as e:
            logger.error(f"Failed to log command execution: {e}")
            return False
