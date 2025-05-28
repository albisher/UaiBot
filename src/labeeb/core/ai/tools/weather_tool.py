"""
WeatherTool: Retrieves weather information for the Labeeb agent, supporting queries by location and time.

This tool provides weather capabilities while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import aiohttp
from typing import Dict, Any, List, Optional, Union
from src.app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class WeatherTool(BaseTool):
    """Tool for performing weather operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the weather tool.
        
        Args:
            config: Optional configuration dictionary
        """
        if config is None:
            config = {}
        super().__init__(
            name="weather",
            description="Tool for performing weather operations",
            config=config
        )
        self._api_key = config.get('api_key')
        self._api_url = config.get('api_url', 'https://api.openweathermap.org/data/2.5')
        self._units = config.get('units', 'metric')
        self._language = config.get('language', 'en')
        self._cache_duration = config.get('cache_duration', 300)  # 5 minutes
        self._max_requests = config.get('max_requests', 60)  # per minute
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._cache = {}  # Weather data cache
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
            logger.error(f"Failed to initialize WeatherTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._cache = {}
            self._request_times = []
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up WeatherTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'current': True,
            'forecast': True,
            'historical': True,
            'alerts': True,
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
            'units': self._units,
            'language': self._language,
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
        if command == 'current':
            return await self._get_current_weather(args)
        elif command == 'forecast':
            return await self._get_weather_forecast(args)
        elif command == 'historical':
            return await self._get_historical_weather(args)
        elif command == 'alerts':
            return await self._get_weather_alerts(args)
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
    
    def _get_cache_key(self, location: str, command: str, **kwargs) -> str:
        """Generate a cache key for weather data.
        
        Args:
            location: Location to get weather for
            command: Weather command
            **kwargs: Additional parameters
            
        Returns:
            str: Cache key
        """
        params = [location, command]
        for key, value in sorted(kwargs.items()):
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
    
    async def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the weather API.
        
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
                params['appid'] = self._api_key
                params['units'] = self._units
                params['lang'] = self._language
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return {'error': f'API request failed: {response.status}'}
                    
                    data = await response.json()
                    self._add_request()
                    return data
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            return {'error': str(e)}
    
    async def _get_current_weather(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get current weather for a location.
        
        Args:
            args: Location arguments
            
        Returns:
            Dict[str, Any]: Current weather data
        """
        try:
            if not args or 'location' not in args:
                return {'error': 'Missing location'}
            
            location = args['location']
            cache_key = self._get_cache_key(location, 'current')
            
            # Check cache
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Make API request
            params = {'q': location}
            data = await self._make_api_request('weather', params)
            
            if 'error' in data:
                return data
            
            # Cache response
            self._cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            
            result = {
                'status': 'success',
                'action': 'current',
                'location': location,
                'weather': data
            }
            
            self._add_to_history('current', {
                'location': location
            })
            
            return result
        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            return {'error': str(e)}
    
    async def _get_weather_forecast(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get weather forecast for a location.
        
        Args:
            args: Forecast arguments
            
        Returns:
            Dict[str, Any]: Forecast data
        """
        try:
            if not args or 'location' not in args:
                return {'error': 'Missing location'}
            
            location = args['location']
            days = args.get('days', 5)
            
            if days < 1 or days > 16:
                return {'error': 'Invalid forecast days (1-16)'}
            
            cache_key = self._get_cache_key(location, 'forecast', days=days)
            
            # Check cache
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Make API request
            params = {
                'q': location,
                'cnt': days * 8  # API returns 3-hour intervals
            }
            data = await self._make_api_request('forecast', params)
            
            if 'error' in data:
                return data
            
            # Cache response
            self._cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            
            result = {
                'status': 'success',
                'action': 'forecast',
                'location': location,
                'days': days,
                'forecast': data
            }
            
            self._add_to_history('forecast', {
                'location': location,
                'days': days
            })
            
            return result
        except Exception as e:
            logger.error(f"Error getting weather forecast: {e}")
            return {'error': str(e)}
    
    async def _get_historical_weather(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get historical weather data for a location.
        
        Args:
            args: Historical data arguments
            
        Returns:
            Dict[str, Any]: Historical weather data
        """
        try:
            if not args or 'location' not in args or 'date' not in args:
                return {'error': 'Missing location or date'}
            
            location = args['location']
            date = args['date']
            
            cache_key = self._get_cache_key(location, 'historical', date=date)
            
            # Check cache
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Make API request
            params = {
                'q': location,
                'dt': int(time.mktime(time.strptime(date, '%Y-%m-%d')))
            }
            data = await self._make_api_request('onecall/timemachine', params)
            
            if 'error' in data:
                return data
            
            # Cache response
            self._cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            
            result = {
                'status': 'success',
                'action': 'historical',
                'location': location,
                'date': date,
                'weather': data
            }
            
            self._add_to_history('historical', {
                'location': location,
                'date': date
            })
            
            return result
        except Exception as e:
            logger.error(f"Error getting historical weather: {e}")
            return {'error': str(e)}
    
    async def _get_weather_alerts(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get weather alerts for a location.
        
        Args:
            args: Alert arguments
            
        Returns:
            Dict[str, Any]: Weather alert data
        """
        try:
            if not args or 'location' not in args:
                return {'error': 'Missing location'}
            
            location = args['location']
            cache_key = self._get_cache_key(location, 'alerts')
            
            # Check cache
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Make API request
            params = {'q': location}
            data = await self._make_api_request('onecall', params)
            
            if 'error' in data:
                return data
            
            # Cache response
            self._cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            
            result = {
                'status': 'success',
                'action': 'alerts',
                'location': location,
                'alerts': data.get('alerts', [])
            }
            
            self._add_to_history('alerts', {
                'location': location
            })
            
            return result
        except Exception as e:
            logger.error(f"Error getting weather alerts: {e}")
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