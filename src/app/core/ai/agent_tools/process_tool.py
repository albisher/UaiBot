"""
Process tool with A2A, MCP, and SmolAgents compliance.

This tool provides process operations while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import os
import signal
import psutil
from typing import Dict, Any, List, Optional, Union, Tuple
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class ProcessTool(BaseTool):
    """Tool for performing process operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the process tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="process",
            description="Tool for performing process operations",
            config=config
        )
        self._max_processes = config.get('max_processes', 100)
        self._max_memory = config.get('max_memory', 1024 * 1024 * 1024)  # 1GB
        self._max_cpu = config.get('max_cpu', 100)  # 100%
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._processes = {}
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize ProcessTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            # Terminate all managed processes
            for pid in list(self._processes.keys()):
                await self._terminate(pid)
            self._processes = {}
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up ProcessTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'start': True,
            'stop': True,
            'restart': True,
            'status': True,
            'list': True,
            'history': True
        }
        return {**base_capabilities, **tool_capabilities}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        base_status = super().get_status()
        tool_status = {
            'max_processes': self._max_processes,
            'max_memory': self._max_memory,
            'max_cpu': self._max_cpu,
            'process_count': len(self._processes),
            'history_size': len(self._operation_history),
            'max_history': self._max_history
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
        if command == 'start':
            return await self._start(args)
        elif command == 'stop':
            return await self._stop(args)
        elif command == 'restart':
            return await self._restart(args)
        elif command == 'status':
            return await self._status(args)
        elif command == 'list':
            return await self._list(args)
        elif command == 'get_history':
            return await self._get_history()
        elif command == 'clear_history':
            return await self._clear_history()
        else:
            return {'error': f'Unknown command: {command}'}
    
    def _add_to_history(self, operation: str, details: Dict[str, Any]) -> None:
        """Add an operation to history.
        
        Args:
            operation: Operation performed
            details: Operation details
        """
        self._operation_history.append({
            'operation': operation,
            'details': details,
            'timestamp': time.time()
        })
        if len(self._operation_history) > self._max_history:
            self._operation_history.pop(0)
    
    async def _start(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start a process.
        
        Args:
            args: Start arguments
            
        Returns:
            Dict[str, Any]: Start result
        """
        try:
            if not args or 'command' not in args:
                return {'error': 'Missing required arguments'}
            
            command = args['command']
            args_list = args.get('args', [])
            env = args.get('env', {})
            cwd = args.get('cwd', os.getcwd())
            
            # Check process limit
            if len(self._processes) >= self._max_processes:
                return {
                    'status': 'error',
                    'action': 'start',
                    'error': 'Maximum number of processes reached'
                }
            
            # Start process
            process = await asyncio.create_subprocess_exec(
                command,
                *args_list,
                env=env,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Store process info
            self._processes[process.pid] = {
                'process': process,
                'command': command,
                'args': args_list,
                'env': env,
                'cwd': cwd,
                'start_time': time.time()
            }
            
            self._add_to_history('start', {
                'pid': process.pid,
                'command': command,
                'args': args_list
            })
            
            return {
                'status': 'success',
                'action': 'start',
                'pid': process.pid
            }
        except Exception as e:
            logger.error(f"Error starting process: {e}")
            return {'error': str(e)}
    
    async def _stop(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Stop a process.
        
        Args:
            args: Stop arguments
            
        Returns:
            Dict[str, Any]: Stop result
        """
        try:
            if not args or 'pid' not in args:
                return {'error': 'Missing required arguments'}
            
            pid = args['pid']
            
            # Check if process exists
            if pid not in self._processes:
                return {
                    'status': 'error',
                    'action': 'stop',
                    'error': f'Process not found: {pid}'
                }
            
            # Stop process
            process = self._processes[pid]['process']
            process.terminate()
            await process.wait()
            
            # Remove process info
            del self._processes[pid]
            
            self._add_to_history('stop', {
                'pid': pid
            })
            
            return {
                'status': 'success',
                'action': 'stop',
                'pid': pid
            }
        except Exception as e:
            logger.error(f"Error stopping process: {e}")
            return {'error': str(e)}
    
    async def _restart(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Restart a process.
        
        Args:
            args: Restart arguments
            
        Returns:
            Dict[str, Any]: Restart result
        """
        try:
            if not args or 'pid' not in args:
                return {'error': 'Missing required arguments'}
            
            pid = args['pid']
            
            # Check if process exists
            if pid not in self._processes:
                return {
                    'status': 'error',
                    'action': 'restart',
                    'error': f'Process not found: {pid}'
                }
            
            # Get process info
            process_info = self._processes[pid]
            
            # Stop process
            process = process_info['process']
            process.terminate()
            await process.wait()
            
            # Start new process
            new_process = await asyncio.create_subprocess_exec(
                process_info['command'],
                *process_info['args'],
                env=process_info['env'],
                cwd=process_info['cwd'],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Update process info
            self._processes[new_process.pid] = {
                'process': new_process,
                'command': process_info['command'],
                'args': process_info['args'],
                'env': process_info['env'],
                'cwd': process_info['cwd'],
                'start_time': time.time()
            }
            
            # Remove old process info
            del self._processes[pid]
            
            self._add_to_history('restart', {
                'old_pid': pid,
                'new_pid': new_process.pid,
                'command': process_info['command']
            })
            
            return {
                'status': 'success',
                'action': 'restart',
                'old_pid': pid,
                'new_pid': new_process.pid
            }
        except Exception as e:
            logger.error(f"Error restarting process: {e}")
            return {'error': str(e)}
    
    async def _status(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get process status.
        
        Args:
            args: Status arguments
            
        Returns:
            Dict[str, Any]: Status result
        """
        try:
            if not args or 'pid' not in args:
                return {'error': 'Missing required arguments'}
            
            pid = args['pid']
            
            # Check if process exists
            if pid not in self._processes:
                return {
                    'status': 'error',
                    'action': 'status',
                    'error': f'Process not found: {pid}'
                }
            
            # Get process info
            process_info = self._processes[pid]
            process = process_info['process']
            
            # Get system process info
            try:
                system_process = psutil.Process(pid)
                cpu_percent = system_process.cpu_percent()
                memory_info = system_process.memory_info()
                
                # Check resource limits
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
            except psutil.NoSuchProcess:
                status = {
                    'pid': pid,
                    'command': process_info['command'],
                    'args': process_info['args'],
                    'cwd': process_info['cwd'],
                    'start_time': process_info['start_time'],
                    'status': 'terminated'
                }
            
            self._add_to_history('status', {
                'pid': pid
            })
            
            return {
                'status': 'success',
                'action': 'status',
                'process': status
            }
        except Exception as e:
            logger.error(f"Error getting process status: {e}")
            return {'error': str(e)}
    
    async def _list(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List processes.
        
        Args:
            args: List arguments
            
        Returns:
            Dict[str, Any]: List result
        """
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
            
            self._add_to_history('list', {
                'count': len(processes)
            })
            
            return {
                'status': 'success',
                'action': 'list',
                'processes': processes
            }
        except Exception as e:
            logger.error(f"Error listing processes: {e}")
            return {'error': str(e)}
    
    async def _get_history(self) -> Dict[str, Any]:
        """Get operation history.
        
        Returns:
            Dict[str, Any]: Operation history
        """
        try:
            return {
                'status': 'success',
                'action': 'get_history',
                'history': self._operation_history
            }
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return {'error': str(e)}
    
    async def _clear_history(self) -> Dict[str, Any]:
        """Clear operation history.
        
        Returns:
            Dict[str, Any]: Result of clearing history
        """
        try:
            self._operation_history = []
            return {
                'status': 'success',
                'action': 'clear_history'
            }
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return {'error': str(e)} 