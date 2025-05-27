"""
Cache tool with A2A, MCP, and SmolAgents compliance.

This tool provides caching operations while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import json
import pickle
from typing import Dict, Any, List, Optional, Union, Tuple
from labeeb.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class CacheTool(BaseTool):
    """Tool for performing caching operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the cache tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="cache",
            description="Tool for performing caching operations",
            config=config
        )
        self._max_size = config.get('max_size', 1000)
        self._max_memory = config.get('max_memory', 100 * 1024 * 1024)  # 100MB
        self._default_ttl = config.get('default_ttl', 3600)  # 1 hour
        self._serializer = config.get('serializer', 'json')
        self._cache = {}
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Validate serializer
            if self._serializer not in ['json', 'pickle']:
                logger.error(f"Invalid serializer: {self._serializer}")
                return False
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize CacheTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._cache.clear()
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up CacheTool: {e}")
    
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
            'clear': True,
            'stats': True,
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
            'max_size': self._max_size,
            'max_memory': self._max_memory,
            'default_ttl': self._default_ttl,
            'serializer': self._serializer,
            'cache_size': len(self._cache),
            'memory_usage': self._get_memory_usage(),
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
        elif command == 'clear':
            return await self._clear()
        elif command == 'stats':
            return await self._stats()
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
    
    def _serialize(self, data: Any) -> bytes:
        """Serialize data.
        
        Args:
            data: Data to serialize
            
        Returns:
            bytes: Serialized data
        """
        if self._serializer == 'json':
            return json.dumps(data).encode()
        else:  # pickle
            return pickle.dumps(data)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize data.
        
        Args:
            data: Data to deserialize
            
        Returns:
            Any: Deserialized data
        """
        if self._serializer == 'json':
            return json.loads(data.decode())
        else:  # pickle
            return pickle.loads(data)
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage.
        
        Returns:
            int: Memory usage in bytes
        """
        total_size = 0
        for key, value in self._cache.items():
            total_size += len(key.encode())
            total_size += len(self._serialize(value))
        return total_size
    
    async def _get(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get value from cache.
        
        Args:
            args: Get arguments
            
        Returns:
            Dict[str, Any]: Get result
        """
        try:
            if not args or 'key' not in args:
                return {'error': 'Missing required arguments'}
            
            key = args['key']
            
            # Check if key exists
            if key not in self._cache:
                return {
                    'status': 'error',
                    'action': 'get',
                    'error': f'Key not found: {key}'
                }
            
            # Get value
            value, expiry = self._cache[key]
            
            # Check expiry
            if expiry and time.time() > expiry:
                del self._cache[key]
                return {
                    'status': 'error',
                    'action': 'get',
                    'error': f'Key expired: {key}'
                }
            
            self._add_to_history('get', {
                'key': key,
                'value_size': len(self._serialize(value))
            })
            
            return {
                'status': 'success',
                'action': 'get',
                'key': key,
                'value': value
            }
        except Exception as e:
            logger.error(f"Error getting value from cache: {e}")
            return {'error': str(e)}
    
    async def _set(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Set value in cache.
        
        Args:
            args: Set arguments
            
        Returns:
            Dict[str, Any]: Set result
        """
        try:
            if not args or 'key' not in args or 'value' not in args:
                return {'error': 'Missing required arguments'}
            
            key = args['key']
            value = args['value']
            ttl = args.get('ttl', self._default_ttl)
            
            # Check cache size
            if len(self._cache) >= self._max_size:
                return {
                    'status': 'error',
                    'action': 'set',
                    'error': 'Cache size limit reached'
                }
            
            # Check memory usage
            value_size = len(self._serialize(value))
            if self._get_memory_usage() + value_size > self._max_memory:
                return {
                    'status': 'error',
                    'action': 'set',
                    'error': 'Memory limit reached'
                }
            
            # Set value
            expiry = time.time() + ttl if ttl > 0 else None
            self._cache[key] = (value, expiry)
            
            self._add_to_history('set', {
                'key': key,
                'value_size': value_size,
                'ttl': ttl
            })
            
            return {
                'status': 'success',
                'action': 'set',
                'key': key,
                'ttl': ttl
            }
        except Exception as e:
            logger.error(f"Error setting value in cache: {e}")
            return {'error': str(e)}
    
    async def _delete(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delete value from cache.
        
        Args:
            args: Delete arguments
            
        Returns:
            Dict[str, Any]: Delete result
        """
        try:
            if not args or 'key' not in args:
                return {'error': 'Missing required arguments'}
            
            key = args['key']
            
            # Check if key exists
            if key not in self._cache:
                return {
                    'status': 'error',
                    'action': 'delete',
                    'error': f'Key not found: {key}'
                }
            
            # Delete value
            del self._cache[key]
            
            self._add_to_history('delete', {
                'key': key
            })
            
            return {
                'status': 'success',
                'action': 'delete',
                'key': key
            }
        except Exception as e:
            logger.error(f"Error deleting value from cache: {e}")
            return {'error': str(e)}
    
    async def _clear(self) -> Dict[str, Any]:
        """Clear cache.
        
        Returns:
            Dict[str, Any]: Clear result
        """
        try:
            self._cache.clear()
            
            self._add_to_history('clear', {
                'cache_size': 0
            })
            
            return {
                'status': 'success',
                'action': 'clear'
            }
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return {'error': str(e)}
    
    async def _stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dict[str, Any]: Cache statistics
        """
        try:
            stats = {
                'size': len(self._cache),
                'memory_usage': self._get_memory_usage(),
                'max_size': self._max_size,
                'max_memory': self._max_memory,
                'default_ttl': self._default_ttl,
                'serializer': self._serializer
            }
            
            self._add_to_history('stats', stats)
            
            return {
                'status': 'success',
                'action': 'stats',
                'stats': stats
            }
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
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