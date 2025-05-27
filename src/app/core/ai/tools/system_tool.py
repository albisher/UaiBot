"""
System tool module that provides system-related functionality.
"""

import os
import platform
import subprocess
from typing import Dict, List, Optional, Union

from .tool_registry import ToolRegistry

class SystemTool:
    """Tool for system-related operations."""
    
    def __init__(self):
        """Initialize the system tool."""
        self.name = "system_tool"
        self.description = "Tool for system-related operations"
        self.version = "1.0.0"
        
    def get_system_info(self) -> Dict[str, str]:
        """Get system information.
        
        Returns:
            Dict[str, str]: System information including OS, version, etc.
        """
        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
        return info
        
    def execute_command(self, command: str) -> Dict[str, Union[str, int]]:
        """Execute a system command.
        
        Args:
            command (str): Command to execute
            
        Returns:
            Dict[str, Union[str, int]]: Command output and exit code
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            return {
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "exit_code": -1
            }
            
    def get_environment_variable(self, name: str) -> Optional[str]:
        """Get an environment variable.
        
        Args:
            name (str): Name of the environment variable
            
        Returns:
            Optional[str]: Value of the environment variable or None if not found
        """
        return os.environ.get(name)
        
    def set_environment_variable(self, name: str, value: str) -> bool:
        """Set an environment variable.
        
        Args:
            name (str): Name of the environment variable
            value (str): Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.environ[name] = value
            return True
        except Exception:
            return False
            
    def list_directory(self, path: str) -> List[str]:
        """List contents of a directory.
        
        Args:
            path (str): Path to list
            
        Returns:
            List[str]: List of files and directories
        """
        try:
            return os.listdir(path)
        except Exception:
            return []
            
    def get_current_directory(self) -> str:
        """Get current working directory.
        
        Returns:
            str: Current working directory
        """
        return os.getcwd()
        
    def change_directory(self, path: str) -> bool:
        """Change current working directory.
        
        Args:
            path (str): Path to change to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.chdir(path)
            return True
        except Exception:
            return False

# Register the tool
ToolRegistry.register(SystemTool) 