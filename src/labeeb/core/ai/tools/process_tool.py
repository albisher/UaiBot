"""
Process Tool Implementation

This module provides the ProcessTool for process management operations,
implementing A2A (Agent-to-Agent), MCP (Model Context Protocol), and SmolAgents patterns.
"""

import logging
import asyncio
import time
import os
import signal
import psutil
import subprocess
from typing import Dict, Any, List, Optional, Union, Tuple
from labeeb.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class ProcessTool(BaseTool):
    """Tool for process management operations."""
    
    def __init__(self):
        """Initialize the ProcessTool."""
        super().__init__(
            name="ProcessTool",
            description="Handles process management operations including starting, stopping, and monitoring processes"
        )
        self._max_processes = 100
        self._max_memory = 1024 * 1024 * 1024  # 1GB
        self._max_cpu = 100  # 100%
        self._operation_history = []
        self._max_history = 100
        self._processes = {}
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a process management operation.
        
        Args:
            action (str): The action to execute
            **kwargs: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the operation
        """
        try:
            if not self.validate_input(action, **kwargs):
                return self.handle_error(ValueError("Invalid input"))
            
            if action == "start_process":
                return self._start_process(**kwargs)
            elif action == "stop_process":
                return self._stop_process(**kwargs)
            elif action == "list_processes":
                return self._list_processes(**kwargs)
            elif action == "get_process_info":
                return self._get_process_info(**kwargs)
            else:
                return self.handle_error(ValueError(f"Unknown action: {action}"))
                
        except Exception as e:
            return self.handle_error(e)
    
    def get_available_actions(self) -> Dict[str, str]:
        """
        Get available process management operations.
        
        Returns:
            Dict[str, str]: Available operations and their descriptions
        """
        return {
            "start_process": "Start a new process",
            "stop_process": "Stop a running process",
            "list_processes": "List all running processes",
            "get_process_info": "Get detailed information about a process"
        }
    
    def _start_process(self, command: str, args: Optional[List[str]] = None, 
                      cwd: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Start a new process."""
        try:
            if len(self._processes) >= self._max_processes:
                return self.handle_error(ValueError("Maximum number of processes reached"))
            
            process = subprocess.Popen(
                [command] + (args or []),
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self._processes[process.pid] = {
                'process': process,
                'command': command,
                'args': args,
                'cwd': cwd,
                'start_time': time.time()
            }
            
            self._operation_history.append({
                'operation': 'start',
                'details': {
                    'pid': process.pid,
                    'command': command,
                    'args': args
                },
                'timestamp': time.time()
            })
            
            if len(self._operation_history) > self._max_history:
                self._operation_history.pop(0)
            
            return {
                "pid": process.pid,
                "command": command,
                "args": args,
                "cwd": cwd,
                "started": True
            }
        except Exception as e:
            return self.handle_error(e)
    
    def _stop_process(self, pid: int, force: bool = False, **kwargs) -> Dict[str, Any]:
        """Stop a running process."""
        try:
            if pid not in self._processes:
                return self.handle_error(ValueError(f"Process {pid} not found"))
            
            process = self._processes[pid]['process']
            if force:
                process.kill()
            else:
                process.terminate()
            
            del self._processes[pid]
            
            self._operation_history.append({
                'operation': 'stop',
                'details': {
                    'pid': pid
                },
                'timestamp': time.time()
            })
            
            if len(self._operation_history) > self._max_history:
                self._operation_history.pop(0)
            
            return {
                "pid": pid,
                "stopped": True,
                "force": force
            }
        except psutil.NoSuchProcess:
            return self.handle_error(ValueError(f"Process {pid} not found"))
        except Exception as e:
            return self.handle_error(e)
    
    def _list_processes(self, **kwargs) -> Dict[str, Any]:
        """List all running processes."""
        try:
            processes = []
            for pid, process_info in self._processes.items():
                try:
                    system_process = psutil.Process(pid)
                    processes.append({
                        'pid': pid,
                        'command': process_info['command'],
                        'args': process_info['args'],
                        'cwd': process_info['cwd'],
                        'start_time': process_info['start_time'],
                        'cpu_percent': system_process.cpu_percent(),
                        'memory_rss': system_process.memory_info().rss,
                        'status': system_process.status()
                    })
                except psutil.NoSuchProcess:
                    processes.append({
                        'pid': pid,
                        'command': process_info['command'],
                        'args': process_info['args'],
                        'cwd': process_info['cwd'],
                        'start_time': process_info['start_time'],
                        'status': 'terminated'
                    })
            
            self._operation_history.append({
                'operation': 'list',
                'details': {
                    'count': len(processes)
                },
                'timestamp': time.time()
            })
            
            return {
                "processes": processes,
                "count": len(processes)
            }
        except Exception as e:
            return self.handle_error(e)
    
    def _get_process_info(self, pid: int, **kwargs) -> Dict[str, Any]:
        """Get detailed information about a process."""
        try:
            if pid not in self._processes:
                return self.handle_error(ValueError(f"Process {pid} not found"))
            
            process_info = self._processes[pid]
            system_process = psutil.Process(pid)
            cpu_percent = system_process.cpu_percent()
            memory_info = system_process.memory_info()
            
            if cpu_percent > self._max_cpu:
                logger.warning(f"Process {pid} exceeds CPU limit: {cpu_percent}%")
            if memory_info.rss > self._max_memory:
                logger.warning(f"Process {pid} exceeds memory limit: {memory_info.rss}")
            
            status = {
                'pid': pid,
                'command': process_info['command'],
                'args': process_info['args'],
                'cwd': process_info['cwd'],
                'start_time': process_info['start_time'],
                'cpu_percent': cpu_percent,
                'memory_rss': memory_info.rss,
                'memory_vms': memory_info.vms,
                'status': system_process.status()
            }
            
            self._operation_history.append({
                'operation': 'status',
                'details': {
                    'pid': pid
                },
                'timestamp': time.time()
            })
            
            return {
                "pid": pid,
                "name": system_process.name(),
                "username": system_process.username(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_info.percent,
                "status": system_process.status(),
                "create_time": system_process.create_time(),
                "num_threads": system_process.num_threads(),
                "num_handles": system_process.num_handles() if hasattr(system_process, "num_handles") else None,
                "io_counters": system_process.io_counters()._asdict() if system_process.io_counters() else None,
                "connections": [conn._asdict() for conn in system_process.connections()] if system_process.connections() else None,
                "process_info": status
            }
        except psutil.NoSuchProcess:
            return self.handle_error(ValueError(f"Process {pid} not found"))
        except Exception as e:
            return self.handle_error(e) 