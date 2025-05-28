"""
System Resource Tool Implementation

This module provides the SystemResourceTool for monitoring and managing system resources,
implementing A2A (Agent-to-Agent), MCP (Model Context Protocol), and SmolAgents patterns.
"""
import os
import psutil
from typing import Any, Dict
from .base_tool import BaseTool

class SystemResourceTool(BaseTool):
    """Tool for monitoring and managing system resources."""
    
    def __init__(self):
        """Initialize the SystemResourceTool."""
        super().__init__(
            name="SystemResourceTool",
            description="Monitors and manages system resources including CPU, memory, and disk usage"
        )
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a system resource operation.
        
        Args:
            action (str): The action to execute
            **kwargs: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the operation
        """
        try:
            if not self.validate_input(action, **kwargs):
                return self.handle_error(ValueError("Invalid input"))
            
            if action == "get_cpu_usage":
                return self._get_cpu_usage(**kwargs)
            elif action == "get_memory_usage":
                return self._get_memory_usage(**kwargs)
            elif action == "get_disk_usage":
                return self._get_disk_usage(**kwargs)
            elif action == "get_process_info":
                return self._get_process_info(**kwargs)
            else:
                return self.handle_error(ValueError(f"Unknown action: {action}"))
                
        except Exception as e:
            return self.handle_error(e)
    
    def get_available_actions(self) -> Dict[str, str]:
        """
        Get available system resource operations.
        
        Returns:
            Dict[str, str]: Available operations and their descriptions
        """
        return {
            "get_cpu_usage": "Get CPU usage statistics",
            "get_memory_usage": "Get memory usage statistics",
            "get_disk_usage": "Get disk usage statistics",
            "get_process_info": "Get information about running processes"
        }
    
    def _get_cpu_usage(self, **kwargs) -> Dict[str, Any]:
        """Get CPU usage statistics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        return {
            "cpu_percent": cpu_percent,
            "cpu_count": cpu_count,
            "cpu_freq": {
                "current": cpu_freq.current if cpu_freq else None,
                "min": cpu_freq.min if cpu_freq else None,
                "max": cpu_freq.max if cpu_freq else None
            }
        }
    
    def _get_memory_usage(self, **kwargs) -> Dict[str, Any]:
        """Get memory usage statistics."""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "virtual_memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free
            },
            "swap_memory": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent
            }
        }
    
    def _get_disk_usage(self, path: str = "/", **kwargs) -> Dict[str, Any]:
        """Get disk usage statistics."""
        disk = psutil.disk_usage(path)
        
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
    
    def _get_process_info(self, pid: int = None, **kwargs) -> Dict[str, Any]:
        """Get information about running processes."""
        if pid is None:
            # Get all processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return {"processes": processes}
        else:
            # Get specific process
            try:
                process = psutil.Process(pid)
                return {
                    "pid": process.pid,
                    "name": process.name(),
                    "username": process.username(),
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "status": process.status(),
                    "create_time": process.create_time()
                }
            except psutil.NoSuchProcess:
                return self.handle_error(ValueError(f"Process {pid} not found"))

    async def forward(self, **kwargs):
        action = kwargs.get('action', 'status')
        return await self._execute_command(action, kwargs)

    async def _execute_command(self, action: str, args: dict) -> dict:
        if action == "status":
            return {
                "cpu": self._get_cpu_usage(),
                "memory": self._get_memory_usage(),
                "disk": self._get_disk_usage()
            }
        elif action == "get_cpu_usage":
            return self._get_cpu_usage()
        elif action == "get_memory_usage":
            return self._get_memory_usage()
        elif action == "get_disk_usage":
            return self._get_disk_usage(**args)
        elif action == "get_process_info":
            return self._get_process_info(**args)
        else:
            return {"error": f"Unknown action: {action}"} 