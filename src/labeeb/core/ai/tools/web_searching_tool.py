"""
WebSearchingTool: Enables the Labeeb agent to perform web searches and retrieve relevant information from the internet.

This tool provides web searching capabilities while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import aiohttp
import time
from typing import Dict, Any, List, Optional, Union
from src.app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class WebSearchingTool(BaseTool):
    """Tool for performing web searches."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the web searching tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="web_search",
            description="Tool for performing web searches",
            config=config
        )
        self._api_key = config.get('api_key')
        self._search_engine = config.get('search_engine', 'google')
        self._max_results = config.get('max_results', 10)
        self._timeout = config.get('timeout', 30)
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._session = None
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Validate configuration
            if not self._api_key:
                logger.error("API key is required")
                return False
            
            if self._search_engine not in ['google', 'bing', 'duckduckgo']:
                logger.error(f"Unsupported search engine: {self._search_engine}")
                return False
            
            # Create HTTP session
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self._timeout)
            )
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize WebSearchingTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            if self._session:
                await self._session.close()
                self._session = None
            
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up WebSearchingTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'search': True,
            'image_search': True,
            'news_search': True,
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
            'search_engine': self._search_engine,
            'max_results': self._max_results,
            'timeout': self._timeout,
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
        if command == 'search':
            return await self._perform_search(args)
        elif command == 'image_search':
            return await self._perform_image_search(args)
        elif command == 'news_search':
            return await self._perform_news_search(args)
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
    
    async def _perform_search(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform a web search.
        
        Args:
            args: Search arguments
            
        Returns:
            Dict[str, Any]: Result of search operation
        """
        try:
            if not args or 'query' not in args:
                return {'error': 'Missing query parameter'}
            
            query = args['query']
            max_results = args.get('max_results', self._max_results)
            
            headers = {}
            if self._search_engine == 'google':
                url = 'https://www.googleapis.com/customsearch/v1'
                params = {
                    'key': self._api_key,
                    'cx': self._config.get('search_engine_id'),
                    'q': query,
                    'num': min(max_results, 10)  # Google's limit is 10 per request
                }
            elif self._search_engine == 'bing':
                url = 'https://api.bing.microsoft.com/v7.0/search'
                headers = {'Ocp-Apim-Subscription-Key': self._api_key}
                params = {
                    'q': query,
                    'count': min(max_results, 50)  # Bing's limit is 50 per request
                }
            elif self._search_engine == 'duckduckgo':
                url = 'https://api.duckduckgo.com/'
                params = {
                    'q': query,
                    'format': 'json',
                    'no_html': 1,
                    'no_redirect': 1
                }
            
            async with self._session.get(url, params=params, headers=headers if self._search_engine == 'bing' else None) as response:
                if response.status != 200:
                    return {'error': f'Search failed with status {response.status}'}
                
                data = await response.json()
                
                if self._search_engine == 'google':
                    results = [{
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    } for item in data.get('items', [])]
                elif self._search_engine == 'bing':
                    results = [{
                        'title': item.get('name', ''),
                        'link': item.get('url', ''),
                        'snippet': item.get('snippet', '')
                    } for item in data.get('webPages', {}).get('value', [])]
                elif self._search_engine == 'duckduckgo':
                    results = [{
                        'title': item.get('Text', ''),
                        'link': item.get('FirstURL', ''),
                        'snippet': item.get('Text', '')
                    } for item in data.get('RelatedTopics', [])]
                
                result = {
                    'status': 'success',
                    'action': 'search',
                    'query': query,
                    'results': results[:max_results]
                }
                
                self._add_to_history('search', {
                    'query': query,
                    'result_count': len(results)
                })
                
                return result
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            return {'error': str(e)}
    
    async def _perform_image_search(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform an image search.
        
        Args:
            args: Search arguments
            
        Returns:
            Dict[str, Any]: Result of image search operation
        """
        try:
            if not args or 'query' not in args:
                return {'error': 'Missing query parameter'}
            
            query = args['query']
            max_results = args.get('max_results', self._max_results)
            
            headers = {}
            if self._search_engine == 'google':
                url = 'https://www.googleapis.com/customsearch/v1'
                params = {
                    'key': self._api_key,
                    'cx': self._config.get('search_engine_id'),
                    'q': query,
                    'searchType': 'image',
                    'num': min(max_results, 10)  # Google's limit is 10 per request
                }
            elif self._search_engine == 'bing':
                url = 'https://api.bing.microsoft.com/v7.0/images/search'
                headers = {'Ocp-Apim-Subscription-Key': self._api_key}
                params = {
                    'q': query,
                    'count': min(max_results, 50)  # Bing's limit is 50 per request
                }
            else:
                return {'error': f'Image search not supported for {self._search_engine}'}
            
            async with self._session.get(url, params=params, headers=headers if self._search_engine == 'bing' else None) as response:
                if response.status != 200:
                    return {'error': f'Image search failed with status {response.status}'}
                
                data = await response.json()
                
                if self._search_engine == 'google':
                    results = [{
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'thumbnail': item.get('image', {}).get('thumbnailLink', ''),
                        'context': item.get('image', {}).get('contextLink', '')
                    } for item in data.get('items', [])]
                elif self._search_engine == 'bing':
                    results = [{
                        'title': item.get('name', ''),
                        'link': item.get('contentUrl', ''),
                        'thumbnail': item.get('thumbnailUrl', ''),
                        'context': item.get('hostPageUrl', '')
                    } for item in data.get('value', [])]
                
                result = {
                    'status': 'success',
                    'action': 'image_search',
                    'query': query,
                    'results': results[:max_results]
                }
                
                self._add_to_history('image_search', {
                    'query': query,
                    'result_count': len(results)
                })
                
                return result
        except Exception as e:
            logger.error(f"Error performing image search: {e}")
            return {'error': str(e)}
    
    async def _perform_news_search(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform a news search.
        
        Args:
            args: Search arguments
            
        Returns:
            Dict[str, Any]: Result of news search operation
        """
        try:
            if not args or 'query' not in args:
                return {'error': 'Missing query parameter'}
            
            query = args['query']
            max_results = args.get('max_results', self._max_results)
            
            headers = {}
            if self._search_engine == 'google':
                url = 'https://www.googleapis.com/customsearch/v1'
                params = {
                    'key': self._api_key,
                    'cx': self._config.get('search_engine_id'),
                    'q': query,
                    'tbm': 'nws',  # News search
                    'num': min(max_results, 10)  # Google's limit is 10 per request
                }
            elif self._search_engine == 'bing':
                url = 'https://api.bing.microsoft.com/v7.0/news/search'
                headers = {'Ocp-Apim-Subscription-Key': self._api_key}
                params = {
                    'q': query,
                    'count': min(max_results, 50)  # Bing's limit is 50 per request
                }
            else:
                return {'error': f'News search not supported for {self._search_engine}'}
            
            async with self._session.get(url, params=params, headers=headers if self._search_engine == 'bing' else None) as response:
                if response.status != 200:
                    return {'error': f'News search failed with status {response.status}'}
                
                data = await response.json()
                
                if self._search_engine == 'google':
                    results = [{
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'date': item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time', '')
                    } for item in data.get('items', [])]
                elif self._search_engine == 'bing':
                    results = [{
                        'title': item.get('name', ''),
                        'link': item.get('url', ''),
                        'snippet': item.get('description', ''),
                        'date': item.get('datePublished', '')
                    } for item in data.get('value', [])]
                
                result = {
                    'status': 'success',
                    'action': 'news_search',
                    'query': query,
                    'results': results[:max_results]
                }
                
                self._add_to_history('news_search', {
                    'query': query,
                    'result_count': len(results)
                })
                
                return result
        except Exception as e:
            logger.error(f"Error performing news search: {e}")
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