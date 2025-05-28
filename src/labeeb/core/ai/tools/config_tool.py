"""
Config tool with A2A, MCP, and SmolAgents compliance.

This tool provides configuration operations while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import json
import yaml
import os
from typing import Dict, Any, List, Optional, Union, Tuple
from labeeb.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class ConfigTool(BaseTool):
    """Tool for performing configuration operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the config tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="config",
            description="Tool for performing configuration operations",
            config=config
        )
        self._config_dir = config.get('config_dir', 'config')
        self._max_file_size = config.get('max_file_size', 1024 * 1024)  # 1MB
        self._default_format = config.get('default_format', 'json')
        self._configs = {}
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Create config directory
            os.makedirs(self._config_dir, exist_ok=True)
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize ConfigTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._configs.clear()
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up ConfigTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'get': True,
            'set': True,
            'delete': True,
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
            'config_dir': self._config_dir,
            'max_file_size': self._max_file_size,
            'default_format': self._default_format,
            'configs': len(self._configs),
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
        if command == 'get':
            return await self._get(args)
        elif command == 'set':
            return await self._set(args)
        elif command == 'delete':
            return await self._delete(args)
        elif command == 'list':
            return await self._list()
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
    
    def _get_file_path(self, name: str, format: Optional[str] = None) -> str:
        """Get config file path.
        
        Args:
            name: Config name
            format: Optional file format
            
        Returns:
            str: Config file path
        """
        format = format or self._default_format
        return os.path.join(self._config_dir, f'{name}.{format}')
    
    def _load_config(self, name: str, format: Optional[str] = None) -> Dict[str, Any]:
        """Load config from file.
        
        Args:
            name: Config name
            format: Optional file format
            
        Returns:
            Dict[str, Any]: Config data
        """
        file_path = self._get_file_path(name, format)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {}
        
        # Check file size
        if os.path.getsize(file_path) > self._max_file_size:
            raise ValueError(f'Config file too large: {name}')
        
        # Load config
        with open(file_path, 'r') as f:
            if format == 'yaml':
                return yaml.safe_load(f) or {}
            else:  # json
                return json.load(f) or {}
    
    def _save_config(self, name: str, data: Dict[str, Any], format: Optional[str] = None) -> None:
        """Save config to file.
        
        Args:
            name: Config name
            data: Config data
            format: Optional file format
        """
        file_path = self._get_file_path(name, format)
        
        # Save config
        with open(file_path, 'w') as f:
            if format == 'yaml':
                yaml.safe_dump(data, f)
            else:  # json
                json.dump(data, f, indent=2)
    
    async def _get(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get config value.
        
        Args:
            args: Get arguments
            
        Returns:
            Dict[str, Any]: Get result
        """
        try:
            if not args or 'name' not in args:
                return {'error': 'Missing required arguments'}
            
            name = args['name']
            key = args.get('key')
            format = args.get('format')
            
            # Load config
            try:
                config = self._load_config(name, format)
            except Exception as e:
                return {
                    'status': 'error',
                    'action': 'get',
                    'error': f'Failed to load config: {str(e)}'
                }
            
            # Get value
            if key:
                if key not in config:
                    return {
                        'status': 'error',
                        'action': 'get',
                        'error': f'Key not found: {key}'
                    }
                value = config[key]
            else:
                value = config
            
            self._add_to_history('get', {
                'name': name,
                'key': key,
                'format': format
            })
            
            return {
                'status': 'success',
                'action': 'get',
                'name': name,
                'key': key,
                'value': value
            }
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return {'error': str(e)}
    
    async def _set(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Set config value.
        
        Args:
            args: Set arguments
            
        Returns:
            Dict[str, Any]: Set result
        """
        try:
            if not args or 'name' not in args or 'value' not in args:
                return {'error': 'Missing required arguments'}
            
            name = args['name']
            value = args['value']
            key = args.get('key')
            format = args.get('format')
            
            # Load config
            try:
                config = self._load_config(name, format)
            except Exception as e:
                return {
                    'status': 'error',
                    'action': 'set',
                    'error': f'Failed to load config: {str(e)}'
                }
            
            # Set value
            if key:
                config[key] = value
            else:
                config = value
            
            # Save config
            try:
                self._save_config(name, config, format)
            except Exception as e:
                return {
                    'status': 'error',
                    'action': 'set',
                    'error': f'Failed to save config: {str(e)}'
                }
            
            self._add_to_history('set', {
                'name': name,
                'key': key,
                'format': format
            })
            
            return {
                'status': 'success',
                'action': 'set',
                'name': name,
                'key': key
            }
        except Exception as e:
            logger.error(f"Error setting config: {e}")
            return {'error': str(e)}
    
    async def _delete(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delete config value.
        
        Args:
            args: Delete arguments
            
        Returns:
            Dict[str, Any]: Delete result
        """
        try:
            if not args or 'name' not in args:
                return {'error': 'Missing required arguments'}
            
            name = args['name']
            key = args.get('key')
            format = args.get('format')
            
            # Load config
            try:
                config = self._load_config(name, format)
            except Exception as e:
                return {
                    'status': 'error',
                    'action': 'delete',
                    'error': f'Failed to load config: {str(e)}'
                }
            
            # Delete value
            if key:
                if key not in config:
                    return {
                        'status': 'error',
                        'action': 'delete',
                        'error': f'Key not found: {key}'
                    }
                del config[key]
            else:
                config = {}
            
            # Save config
            try:
                self._save_config(name, config, format)
            except Exception as e:
                return {
                    'status': 'error',
                    'action': 'delete',
                    'error': f'Failed to save config: {str(e)}'
                }
            
            self._add_to_history('delete', {
                'name': name,
                'key': key,
                'format': format
            })
            
            return {
                'status': 'success',
                'action': 'delete',
                'name': name,
                'key': key
            }
        except Exception as e:
            logger.error(f"Error deleting config: {e}")
            return {'error': str(e)}
    
    async def _list(self) -> Dict[str, Any]:
        """List configs.
        
        Returns:
            Dict[str, Any]: List result
        """
        try:
            # List configs
            configs = []
            for filename in os.listdir(self._config_dir):
                if filename.endswith(('.json', '.yaml', '.yml')):
                    name = os.path.splitext(filename)[0]
                    format = 'yaml' if filename.endswith(('.yaml', '.yml')) else 'json'
                    configs.append({
                        'name': name,
                        'format': format,
                        'size': os.path.getsize(os.path.join(self._config_dir, filename))
                    })
            
            self._add_to_history('list', {
                'configs': len(configs)
            })
            
            return {
                'status': 'success',
                'action': 'list',
                'configs': configs
            }
        except Exception as e:
            logger.error(f"Error listing configs: {e}")
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