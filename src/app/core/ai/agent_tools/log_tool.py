"""
Log tool with A2A, MCP, and SmolAgents compliance.

This tool provides logging operations while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import json
import os
from typing import Dict, Any, List, Optional, Union, Tuple
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class LogTool(BaseTool):
    """Tool for performing logging operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the log tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="log",
            description="Tool for performing logging operations",
            config=config
        )
        self._log_dir = config.get('log_dir', 'logs')
        self._max_file_size = config.get('max_file_size', 10 * 1024 * 1024)  # 10MB
        self._max_files = config.get('max_files', 5)
        self._log_format = config.get('log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._date_format = config.get('date_format', '%Y-%m-%d %H:%M:%S')
        self._handlers = {}
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Create log directory
            os.makedirs(self._log_dir, exist_ok=True)
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize LogTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            # Close all handlers
            for handler in self._handlers.values():
                handler.close()
            self._handlers.clear()
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up LogTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'log': True,
            'get_logs': True,
            'clear_logs': True,
            'rotate_logs': True,
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
            'log_dir': self._log_dir,
            'max_file_size': self._max_file_size,
            'max_files': self._max_files,
            'log_format': self._log_format,
            'date_format': self._date_format,
            'handlers': len(self._handlers),
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
        if command == 'log':
            return await self._log(args)
        elif command == 'get_logs':
            return await self._get_logs(args)
        elif command == 'clear_logs':
            return await self._clear_logs(args)
        elif command == 'rotate_logs':
            return await self._rotate_logs(args)
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
    
    def _get_handler(self, name: str) -> logging.FileHandler:
        """Get or create a file handler.
        
        Args:
            name: Handler name
            
        Returns:
            logging.FileHandler: File handler
        """
        if name not in self._handlers:
            # Create handler
            handler = logging.FileHandler(
                os.path.join(self._log_dir, f'{name}.log'),
                maxBytes=self._max_file_size,
                backupCount=self._max_files
            )
            
            # Set formatter
            formatter = logging.Formatter(
                self._log_format,
                datefmt=self._date_format
            )
            handler.setFormatter(formatter)
            
            # Store handler
            self._handlers[name] = handler
        
        return self._handlers[name]
    
    async def _log(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log a message.
        
        Args:
            args: Log arguments
            
        Returns:
            Dict[str, Any]: Log result
        """
        try:
            if not args or 'message' not in args:
                return {'error': 'Missing required arguments'}
            
            message = args['message']
            level = args.get('level', 'INFO')
            name = args.get('name', 'default')
            
            # Get handler
            handler = self._get_handler(name)
            
            # Create logger
            logger = logging.getLogger(name)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, level.upper()))
            
            # Log message
            logger.log(getattr(logging, level.upper()), message)
            
            self._add_to_history('log', {
                'name': name,
                'level': level,
                'message': message
            })
            
            return {
                'status': 'success',
                'action': 'log',
                'name': name,
                'level': level
            }
        except Exception as e:
            logger.error(f"Error logging message: {e}")
            return {'error': str(e)}
    
    async def _get_logs(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get log contents.
        
        Args:
            args: Get logs arguments
            
        Returns:
            Dict[str, Any]: Get logs result
        """
        try:
            if not args or 'name' not in args:
                return {'error': 'Missing required arguments'}
            
            name = args['name']
            max_lines = args.get('max_lines', 1000)
            
            # Get log file path
            log_file = os.path.join(self._log_dir, f'{name}.log')
            
            # Check if file exists
            if not os.path.exists(log_file):
                return {
                    'status': 'error',
                    'action': 'get_logs',
                    'error': f'Log file not found: {name}'
                }
            
            # Read log file
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Get last N lines
            lines = lines[-max_lines:]
            
            self._add_to_history('get_logs', {
                'name': name,
                'lines': len(lines)
            })
            
            return {
                'status': 'success',
                'action': 'get_logs',
                'name': name,
                'lines': lines
            }
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return {'error': str(e)}
    
    async def _clear_logs(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Clear log contents.
        
        Args:
            args: Clear logs arguments
            
        Returns:
            Dict[str, Any]: Clear logs result
        """
        try:
            if not args or 'name' not in args:
                return {'error': 'Missing required arguments'}
            
            name = args['name']
            
            # Get log file path
            log_file = os.path.join(self._log_dir, f'{name}.log')
            
            # Check if file exists
            if not os.path.exists(log_file):
                return {
                    'status': 'error',
                    'action': 'clear_logs',
                    'error': f'Log file not found: {name}'
                }
            
            # Clear log file
            with open(log_file, 'w') as f:
                f.write('')
            
            self._add_to_history('clear_logs', {
                'name': name
            })
            
            return {
                'status': 'success',
                'action': 'clear_logs',
                'name': name
            }
        except Exception as e:
            logger.error(f"Error clearing logs: {e}")
            return {'error': str(e)}
    
    async def _rotate_logs(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Rotate log files.
        
        Args:
            args: Rotate logs arguments
            
        Returns:
            Dict[str, Any]: Rotate logs result
        """
        try:
            if not args or 'name' not in args:
                return {'error': 'Missing required arguments'}
            
            name = args['name']
            
            # Get handler
            if name not in self._handlers:
                return {
                    'status': 'error',
                    'action': 'rotate_logs',
                    'error': f'Handler not found: {name}'
                }
            
            # Rotate logs
            handler = self._handlers[name]
            handler.doRollover()
            
            self._add_to_history('rotate_logs', {
                'name': name
            })
            
            return {
                'status': 'success',
                'action': 'rotate_logs',
                'name': name
            }
        except Exception as e:
            logger.error(f"Error rotating logs: {e}")
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