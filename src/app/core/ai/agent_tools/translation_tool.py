"""
Translation tool with A2A, MCP, and SmolAgents compliance.

This tool provides translation capabilities while following:
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

class TranslationTool(BaseTool):
    """Tool for performing translation operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the translation tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="translation",
            description="Tool for performing translation operations",
            config=config
        )
        self._api_key = config.get('api_key')
        self._api_url = config.get('api_url', 'https://translation.googleapis.com/language/translate/v2')
        self._source_language = config.get('source_language', 'auto')
        self._target_language = config.get('target_language', 'en')
        self._cache_duration = config.get('cache_duration', 3600)  # 1 hour
        self._max_requests = config.get('max_requests', 100)  # per minute
        self._max_text_length = config.get('max_text_length', 5000)
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._cache = {}  # Translation cache
        self._request_times = []  # Request rate limiting
    
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
            
            # Initialize cache and request tracking
            self._cache = {}
            self._request_times = []
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize TranslationTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._cache = {}
            self._request_times = []
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up TranslationTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'translate': True,
            'detect': True,
            'languages': True,
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
            'source_language': self._source_language,
            'target_language': self._target_language,
            'cache_duration': self._cache_duration,
            'max_requests': self._max_requests,
            'max_text_length': self._max_text_length,
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
        if command == 'translate':
            return await self._translate_text(args)
        elif command == 'detect':
            return await self._detect_language(args)
        elif command == 'languages':
            return await self._get_supported_languages(args)
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
    
    def _check_rate_limit(self) -> bool:
        """Check if the rate limit has been exceeded.
        
        Returns:
            bool: True if rate limit is not exceeded, False otherwise
        """
        current_time = time.time()
        # Remove requests older than 1 minute
        self._request_times = [t for t in self._request_times if current_time - t < 60]
        return len(self._request_times) < self._max_requests
    
    def _add_request(self) -> None:
        """Add a request to the rate limit tracking."""
        self._request_times.append(time.time())
    
    def _get_cache_key(self, text: str, source: str, target: str) -> str:
        """Generate a cache key for translation.
        
        Args:
            text: Text to translate
            source: Source language
            target: Target language
            
        Returns:
            str: Cache key
        """
        return f"{text}|{source}|{target}"
    
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
    
    async def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the translation API.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            Dict[str, Any]: API response
        """
        if not self._check_rate_limit():
            return {'error': 'Rate limit exceeded'}
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self._api_url}/{endpoint}"
                params['key'] = self._api_key
                
                async with session.post(url, json=params) as response:
                    if response.status != 200:
                        return {'error': f'API request failed: {response.status}'}
                    
                    data = await response.json()
                    self._add_request()
                    return data
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            return {'error': str(e)}
    
    async def _translate_text(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Translate text from one language to another.
        
        Args:
            args: Translation arguments
            
        Returns:
            Dict[str, Any]: Translation result
        """
        try:
            if not args or 'text' not in args:
                return {'error': 'Missing text to translate'}
            
            text = args['text']
            if len(text) > self._max_text_length:
                return {'error': f'Text exceeds maximum length ({self._max_text_length})'}
            
            source = args.get('source', self._source_language)
            target = args.get('target', self._target_language)
            
            cache_key = self._get_cache_key(text, source, target)
            
            # Check cache
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Make API request
            params = {
                'q': text,
                'source': source,
                'target': target,
                'format': 'text'
            }
            data = await self._make_api_request('translate', params)
            
            if 'error' in data:
                return data
            
            # Cache response
            self._cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            
            result = {
                'status': 'success',
                'action': 'translate',
                'source': source,
                'target': target,
                'translation': data['data']['translations'][0]['translatedText']
            }
            
            self._add_to_history('translate', {
                'source': source,
                'target': target,
                'text_length': len(text)
            })
            
            return result
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return {'error': str(e)}
    
    async def _detect_language(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Detect the language of text.
        
        Args:
            args: Detection arguments
            
        Returns:
            Dict[str, Any]: Detection result
        """
        try:
            if not args or 'text' not in args:
                return {'error': 'Missing text to detect'}
            
            text = args['text']
            if len(text) > self._max_text_length:
                return {'error': f'Text exceeds maximum length ({self._max_text_length})'}
            
            cache_key = self._get_cache_key(text, 'detect', '')
            
            # Check cache
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Make API request
            params = {
                'q': text
            }
            data = await self._make_api_request('detect', params)
            
            if 'error' in data:
                return data
            
            # Cache response
            self._cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            
            result = {
                'status': 'success',
                'action': 'detect',
                'language': data['data']['detections'][0][0]['language'],
                'confidence': data['data']['detections'][0][0]['confidence']
            }
            
            self._add_to_history('detect', {
                'text_length': len(text)
            })
            
            return result
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return {'error': str(e)}
    
    async def _get_supported_languages(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get list of supported languages.
        
        Args:
            args: Language list arguments
            
        Returns:
            Dict[str, Any]: List of supported languages
        """
        try:
            target = args.get('target', self._target_language) if args else self._target_language
            
            cache_key = f"languages|{target}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Make API request
            params = {
                'target': target
            }
            data = await self._make_api_request('languages', params)
            
            if 'error' in data:
                return data
            
            # Cache response
            self._cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            
            result = {
                'status': 'success',
                'action': 'languages',
                'languages': data['data']['languages']
            }
            
            self._add_to_history('languages', {
                'target': target
            })
            
            return result
        except Exception as e:
            logger.error(f"Error getting supported languages: {e}")
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