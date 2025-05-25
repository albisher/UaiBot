"""
Weather Plugin for UaiBot
This plugin provides weather-related functionality.
"""

import requests
from typing import Dict, Any, Optional
import os

# Plugin metadata
PLUGIN_INFO = {
    'name': 'weather',
    'version': '1.0.0',
    'description': 'Provides weather information and forecasts',
    'author': 'UaiBot Team',
    'dependencies': [],
    'entry_point': 'weather_plugin.py'
}

class WeatherPlugin:
    """Weather plugin implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenWeather API key is required")
            
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city."""
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return {
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed']
        }
        
    def get_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a city."""
        url = f"http://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'cnt': days * 8  # API returns data in 3-hour intervals
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        forecast = []
        
        for item in data['list']:
            forecast.append({
                'datetime': item['dt_txt'],
                'temperature': item['main']['temp'],
                'description': item['weather'][0]['description'],
                'humidity': item['main']['humidity'],
                'wind_speed': item['wind']['speed']
            })
            
        return {'forecast': forecast}
        
    def get_weather_alerts(self, city: str) -> Dict[str, Any]:
        """Get weather alerts for a city."""
        url = f"http://api.openweathermap.org/data/2.5/onecall"
        params = {
            'q': city,
            'appid': self.api_key,
            'exclude': 'current,minutely,hourly,daily'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        alerts = data.get('alerts', [])
        
        return {
            'alerts': [
                {
                    'event': alert['event'],
                    'description': alert['description'],
                    'start': alert['start'],
                    'end': alert['end']
                }
                for alert in alerts
            ]
        }

    def handle_command(self, command: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle weather-related commands."""
        command = command.lower()
        
        # Extract city from command or params
        city = params.get('city')
        if not city:
            # Try to extract city from command
            words = command.split()
            if 'in' in words:
                city_index = words.index('in') + 1
                if city_index < len(words):
                    city = words[city_index]
        
        if not city:
            return {
                "status": "error",
                "message": "Please specify a city. Example: 'What's the weather in London?'"
            }
        
        # Handle different weather commands
        if 'forecast' in command:
            return self.get_forecast(city)
        elif 'alert' in command or 'warning' in command:
            return self.get_weather_alerts(city)
        else:
            return self.get_current_weather(city)

# Plugin initialization function
def initialize(config: Dict[str, Any]) -> WeatherPlugin:
    """Initialize the weather plugin."""
    return WeatherPlugin(api_key=config.get('api_key')) 