"""
macOS-specific awareness handler for Labeeb.

This module provides macOS-specific implementation of the awareness handler,
following A2A (Agent-to-Agent), MCP (Multi-Context Protocol), and SmolAgents patterns.
"""
import os
import sys
import platform
import psutil
import subprocess
from typing import Dict, Any
from ...common.awareness.base_awareness import BaseAwarenessHandler, AwarenessContext

class MacOSAwarenessHandler(BaseAwarenessHandler):
    """macOS-specific implementation of the awareness handler."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the macOS awareness handler.
        
        Args:
            config: Configuration dictionary.
        """
        super().__init__(config)
        self._system_info = {}
        self._user_info = {}
        self._environment_info = {}
        self._update_system_info()
        self._update_user_info()
        self._update_environment_info()
    
    def _run_command(self, command: str) -> str:
        """Run a shell command and return its output.
        
        Args:
            command: Command to run.
            
        Returns:
            str: Command output.
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running command '{command}': {e}")
            return ""
    
    def _update_system_info(self) -> None:
        """Update system information."""
        self._system_info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'used': psutil.virtual_memory().used,
                'percent': psutil.virtual_memory().percent
            },
            'cpu': {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'macos_version': self._run_command('sw_vers -productVersion'),
            'kernel_version': platform.release(),
            'hostname': platform.node(),
            'model': self._run_command('sysctl -n hw.model')
        }
    
    def _update_user_info(self) -> None:
        """Update user information."""
        self._user_info = {
            'username': os.getlogin(),
            'home_dir': os.path.expanduser('~'),
            'user_id': os.getuid(),
            'group_id': os.getgid(),
            'shell': os.environ.get('SHELL', ''),
            'groups': self._run_command('groups').split(),
            'real_name': self._run_command('id -F')
        }
    
    def _update_environment_info(self) -> None:
        """Update environment information."""
        self._environment_info = {
            'python_version': sys.version,
            'python_executable': sys.executable,
            'working_directory': os.getcwd(),
            'environment_variables': dict(os.environ),
            'path': os.environ.get('PATH', '').split(os.pathsep),
            'display': os.environ.get('DISPLAY', ''),
            'terminal': os.environ.get('TERM', ''),
            'language': os.environ.get('LANG', ''),
            'timezone': self._run_command('date +%Z')
        }
    
    def get_system_awareness(self) -> Dict[str, Any]:
        """Get macOS-specific system awareness information.
        
        Returns:
            Dict[str, Any]: System awareness information.
        """
        self._update_system_info()
        return self._system_info
    
    def get_user_awareness(self) -> Dict[str, Any]:
        """Get macOS-specific user awareness information.
        
        Returns:
            Dict[str, Any]: User awareness information.
        """
        self._update_user_info()
        return self._user_info
    
    def get_environment_awareness(self) -> Dict[str, Any]:
        """Get macOS-specific environment awareness information.
        
        Returns:
            Dict[str, Any]: Environment awareness information.
        """
        self._update_environment_info()
        return self._environment_info 