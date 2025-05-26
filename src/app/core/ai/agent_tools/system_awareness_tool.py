"""
System awareness tool with A2A, MCP, and SmolAgents compliance.

This tool provides system information while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import os
import platform
import psutil
import logging
from typing import Dict, Any, List, Optional
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class SystemAwarenessTool(BaseTool):
    """Tool for gathering system information with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the system awareness tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="system_awareness",
            description="Tool for gathering system information with platform-specific optimizations",
            config=config
        )
        self._refresh_interval = config.get('refresh_interval', 5)  # seconds
        self._last_refresh = 0
        self._cached_info = {}
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Initial system info collection
            self._cached_info = self._collect_system_info()
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize SystemAwarenessTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._cached_info.clear()
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up SystemAwarenessTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'system_info': True,
            'process_info': True,
            'network_info': True,
            'disk_info': True,
            'memory_info': True,
            'cpu_info': True
        }
        return {**base_capabilities, **tool_capabilities}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        base_status = super().get_status()
        tool_status = {
            'refresh_interval': self._refresh_interval,
            'last_refresh': self._last_refresh,
            'cached_info': bool(self._cached_info)
        }
        return {**base_status, **tool_status}
    
    async def _execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific command.
        
        Args:
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        if command == 'info':
            return await self._get_system_info(args)
        elif command == 'processes':
            return await self._get_process_info(args)
        elif command == 'network':
            return await self._get_network_info(args)
        elif command == 'disk':
            return await self._get_disk_info(args)
        elif command == 'memory':
            return await self._get_memory_info(args)
        elif command == 'cpu':
            return await self._get_cpu_info(args)
        else:
            return {'error': f'Unknown command: {command}'}
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information.
        
        Returns:
            Dict[str, Any]: Dictionary containing system information
        """
        try:
            return {
                'platform': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor()
                },
                'python': {
                    'version': platform.python_version(),
                    'implementation': platform.python_implementation(),
                    'compiler': platform.python_compiler()
                },
                'hostname': platform.node(),
                'username': os.getlogin()
            }
        except Exception as e:
            logger.error(f"Error collecting system info: {e}")
            return {}
    
    async def _get_system_info(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get system information.
        
        Args:
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: System information
        """
        try:
            # Check if we need to refresh the cache
            if not self._cached_info or (args and args.get('force_refresh', False)):
                self._cached_info = self._collect_system_info()
                self._last_refresh = psutil.cpu_times().user
            
            return {
                'status': 'success',
                'info': self._cached_info
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {'error': str(e)}
    
    async def _get_process_info(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get process information.
        
        Args:
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Process information
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            return {
                'status': 'success',
                'processes': processes
            }
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            return {'error': str(e)}
    
    async def _get_network_info(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get network information.
        
        Args:
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Network information
        """
        try:
            network_info = {
                'interfaces': psutil.net_if_addrs(),
                'connections': psutil.net_connections(),
                'io_counters': psutil.net_io_counters(pernic=True)
            }
            
            return {
                'status': 'success',
                'network': network_info
            }
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
            return {'error': str(e)}
    
    async def _get_disk_info(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get disk information.
        
        Args:
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Disk information
        """
        try:
            disk_info = {
                'partitions': psutil.disk_partitions(),
                'usage': psutil.disk_usage('/'),
                'io_counters': psutil.disk_io_counters()
            }
            
            return {
                'status': 'success',
                'disk': disk_info
            }
        except Exception as e:
            logger.error(f"Error getting disk info: {e}")
            return {'error': str(e)}
    
    async def _get_memory_info(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get memory information.
        
        Args:
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Memory information
        """
        try:
            memory_info = {
                'virtual': psutil.virtual_memory()._asdict(),
                'swap': psutil.swap_memory()._asdict()
            }
            
            return {
                'status': 'success',
                'memory': memory_info
            }
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {'error': str(e)}
    
    async def _get_cpu_info(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get CPU information.
        
        Args:
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: CPU information
        """
        try:
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'total_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'cpu_times': psutil.cpu_times()._asdict(),
                'cpu_percent': psutil.cpu_percent(interval=1, percpu=True)
            }
            
            return {
                'status': 'success',
                'cpu': cpu_info
            }
        except Exception as e:
            logger.error(f"Error getting CPU info: {e}")
            return {'error': str(e)} 