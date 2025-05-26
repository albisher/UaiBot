"""
Search tool with A2A, MCP, and SmolAgents compliance.

This tool provides search functionality while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import aiohttp
from typing import Dict, Any, List, Optional, Union
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class SearchTool(BaseTool):
    """Tool for performing web searches."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the search tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="search",
            description="Tool for performing web searches",
            config=config
        )
        self._api_key = config.get('api_key', '')
        self._api_url = config.get('api_url', 'https://api.search.example.com/v1')
        self._max_results = config.get('max_results', 10)
        self._cache_duration = config.get('cache_duration', 3600)  # 1 hour
        self._max_requests = config.get('max_requests', 100)  # per hour
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._cache = {}  # Search cache
        self._session = None
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            if not self._api_key:
                logger.error("API key is required")
                return False
            
            # Initialize HTTP session
            self._session = aiohttp.ClientSession()
            
            # Initialize cache
            self._cache = {}
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize SearchTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            if self._session:
                await self._session.close()
                self._session = None
            
            self._cache = {}
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up SearchTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'web_search': True,
            'image_search': True,
            'news_search': True,
            'video_search': True,
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
            'api_url': self._api_url,
            'max_results': self._max_results,
            'cache_duration': self._cache_duration,
            'max_requests': self._max_requests,
            'cache_size': len(self._cache),
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
        if command == 'web_search':
            return await self._web_search(args)
        elif command == 'image_search':
            return await self._image_search(args)
        elif command == 'news_search':
            return await self._news_search(args)
        elif command == 'video_search':
            return await self._video_search(args)
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
    
    def _get_cache_key(self, operation: str, **kwargs) -> str:
        """Generate a cache key for search operation.
        
        Args:
            operation: Operation performed
            **kwargs: Additional parameters
            
        Returns:
            str: Cache key
        """
        import hashlib
        params = [operation]
        for key, value in sorted(kwargs.items()):
            if isinstance(value, (list, tuple)):
                params.append(f"{key}={hashlib.md5(str(value).encode()).hexdigest()}")
            else:
                params.append(f"{key}={value}")
        return "|".join(params)
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            bool: True if cache is valid, False otherwise
        """
        if cache_key not in self._cache:
            return False
        
        cache_time = self._cache[cache_key]['timestamp']
        return time.time() - cache_time < self._cache_duration
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make an API request.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            Dict[str, Any]: API response
        """
        try:
            if not self._session:
                raise Exception("HTTP session not initialized")
            
            url = f"{self._api_url}/{endpoint}"
            headers = {
                'Authorization': f'Bearer {self._api_key}',
                'Content-Type': 'application/json'
            }
            
            async with self._session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API request failed: {error_text}")
                
                return await response.json()
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            raise
    
    async def _process_search(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Process search operation.
        
        Args:
            operation: Operation to perform
            **kwargs: Operation parameters
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            # Check cache
            cache_key = self._get_cache_key(operation, **kwargs)
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Process operation
            if operation == 'web_search':
                query = kwargs.get('query')
                params = {
                    'q': query,
                    'limit': min(kwargs.get('limit', self._max_results), self._max_results),
                    'offset': kwargs.get('offset', 0),
                    'type': 'web'
                }
                
                result = await self._make_request('search', params)
                processed_data = {
                    'status': 'success',
                    'action': 'web_search',
                    'results': result.get('results', []),
                    'total': result.get('total', 0)
                }
            
            elif operation == 'image_search':
                query = kwargs.get('query')
                params = {
                    'q': query,
                    'limit': min(kwargs.get('limit', self._max_results), self._max_results),
                    'offset': kwargs.get('offset', 0),
                    'type': 'image'
                }
                
                result = await self._make_request('search', params)
                processed_data = {
                    'status': 'success',
                    'action': 'image_search',
                    'results': result.get('results', []),
                    'total': result.get('total', 0)
                }
            
            elif operation == 'news_search':
                query = kwargs.get('query')
                params = {
                    'q': query,
                    'limit': min(kwargs.get('limit', self._max_results), self._max_results),
                    'offset': kwargs.get('offset', 0),
                    'type': 'news'
                }
                
                result = await self._make_request('search', params)
                processed_data = {
                    'status': 'success',
                    'action': 'news_search',
                    'results': result.get('results', []),
                    'total': result.get('total', 0)
                }
            
            elif operation == 'video_search':
                query = kwargs.get('query')
                params = {
                    'q': query,
                    'limit': min(kwargs.get('limit', self._max_results), self._max_results),
                    'offset': kwargs.get('offset', 0),
                    'type': 'video'
                }
                
                result = await self._make_request('search', params)
                processed_data = {
                    'status': 'success',
                    'action': 'video_search',
                    'results': result.get('results', []),
                    'total': result.get('total', 0)
                }
            
            # Cache result
            self._cache[cache_key] = {
                'data': processed_data,
                'timestamp': time.time()
            }
            
            return processed_data
        except Exception as e:
            logger.error(f"Error processing search: {e}")
            return {'error': str(e)}
    
    async def _web_search(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform web search.
        
        Args:
            args: Search arguments
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            if not args or 'query' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_search(
                'web_search',
                query=args['query'],
                limit=args.get('limit', self._max_results),
                offset=args.get('offset', 0)
            )
            
            if 'error' not in result:
                self._add_to_history('web_search', {
                    'query': args['query'],
                    'limit': args.get('limit', self._max_results),
                    'offset': args.get('offset', 0),
                    'total_results': result['total']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return {'error': str(e)}
    
    async def _image_search(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform image search.
        
        Args:
            args: Search arguments
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            if not args or 'query' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_search(
                'image_search',
                query=args['query'],
                limit=args.get('limit', self._max_results),
                offset=args.get('offset', 0)
            )
            
            if 'error' not in result:
                self._add_to_history('image_search', {
                    'query': args['query'],
                    'limit': args.get('limit', self._max_results),
                    'offset': args.get('offset', 0),
                    'total_results': result['total']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error performing image search: {e}")
            return {'error': str(e)}
    
    async def _news_search(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform news search.
        
        Args:
            args: Search arguments
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            if not args or 'query' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_search(
                'news_search',
                query=args['query'],
                limit=args.get('limit', self._max_results),
                offset=args.get('offset', 0)
            )
            
            if 'error' not in result:
                self._add_to_history('news_search', {
                    'query': args['query'],
                    'limit': args.get('limit', self._max_results),
                    'offset': args.get('offset', 0),
                    'total_results': result['total']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error performing news search: {e}")
            return {'error': str(e)}
    
    async def _video_search(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform video search.
        
        Args:
            args: Search arguments
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            if not args or 'query' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_search(
                'video_search',
                query=args['query'],
                limit=args.get('limit', self._max_results),
                offset=args.get('offset', 0)
            )
            
            if 'error' not in result:
                self._add_to_history('video_search', {
                    'query': args['query'],
                    'limit': args.get('limit', self._max_results),
                    'offset': args.get('offset', 0),
                    'total_results': result['total']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error performing video search: {e}")
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