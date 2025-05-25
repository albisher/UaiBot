import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from uaibot.core.plugins import PluginManager

@pytest.fixture
def weather_plugin_manager(plugin_manager):
    """Create a plugin manager with the weather plugin."""
    # Copy the weather plugin to the test plugins directory
    weather_plugin = Path(__file__).parent.parent / "plugins" / "weather_plugin.py"
    test_plugin = Path(plugin_manager.plugins_dir) / "weather_plugin.py"
    test_plugin.write_text(weather_plugin.read_text())
    
    # Register and load the plugin
    plugin_info = plugin_manager.register_plugin(str(test_plugin))
    plugin_manager.load_plugin("weather")
    
    return plugin_manager

def test_weather_plugin_initialization(weather_plugin_manager):
    """Test weather plugin initialization."""
    module = weather_plugin_manager.get_plugin_module("weather")
    assert module is not None
    
    # Test initialization without API key
    with pytest.raises(ValueError):
        module.initialize({})
    
    # Test initialization with API key
    plugin = module.initialize({"api_key": "test_key"})
    assert plugin is not None
    assert plugin.api_key == "test_key"

@patch('requests.get')
def test_get_current_weather(mock_get, weather_plugin_manager):
    """Test getting current weather."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "main": {
            "temp": 20.5,
            "humidity": 65
        },
        "weather": [{
            "description": "clear sky"
        }],
        "wind": {
            "speed": 5.2
        }
    }
    mock_get.return_value = mock_response
    
    # Initialize plugin with test API key
    module = weather_plugin_manager.get_plugin_module("weather")
    plugin = module.initialize({"api_key": "test_key"})
    
    # Test getting current weather
    result = plugin.get_current_weather("London")
    
    assert result == {
        'temperature': 20.5,
        'description': 'clear sky',
        'humidity': 65,
        'wind_speed': 5.2
    }
    
    # Verify API call
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "http://api.openweathermap.org/data/2.5/weather"
    assert kwargs['params']['q'] == "London"
    assert kwargs['params']['appid'] == "test_key"
    assert kwargs['params']['units'] == "metric"

@patch('requests.get')
def test_get_forecast(mock_get, weather_plugin_manager):
    """Test getting weather forecast."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "list": [
            {
                "dt_txt": "2024-03-20 12:00:00",
                "main": {
                    "temp": 20.5,
                    "humidity": 65
                },
                "weather": [{
                    "description": "clear sky"
                }],
                "wind": {
                    "speed": 5.2
                }
            }
        ]
    }
    mock_get.return_value = mock_response
    
    # Initialize plugin with test API key
    module = weather_plugin_manager.get_plugin_module("weather")
    plugin = module.initialize({"api_key": "test_key"})
    
    # Test getting forecast
    result = plugin.get_forecast("London", days=1)
    
    assert 'forecast' in result
    assert len(result['forecast']) == 1
    assert result['forecast'][0]['datetime'] == "2024-03-20 12:00:00"
    assert result['forecast'][0]['temperature'] == 20.5
    
    # Verify API call
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "http://api.openweathermap.org/data/2.5/forecast"
    assert kwargs['params']['q'] == "London"
    assert kwargs['params']['appid'] == "test_key"
    assert kwargs['params']['units'] == "metric"
    assert kwargs['params']['cnt'] == 8  # 1 day * 8 (3-hour intervals)

@patch('requests.get')
def test_get_weather_alerts(mock_get, weather_plugin_manager):
    """Test getting weather alerts."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "alerts": [
            {
                "event": "Severe Thunderstorm Warning",
                "description": "Severe thunderstorm warning in effect",
                "start": "2024-03-20T12:00:00Z",
                "end": "2024-03-20T15:00:00Z"
            }
        ]
    }
    mock_get.return_value = mock_response
    
    # Initialize plugin with test API key
    module = weather_plugin_manager.get_plugin_module("weather")
    plugin = module.initialize({"api_key": "test_key"})
    
    # Test getting alerts
    result = plugin.get_weather_alerts("London")
    
    assert 'alerts' in result
    assert len(result['alerts']) == 1
    assert result['alerts'][0]['event'] == "Severe Thunderstorm Warning"
    
    # Verify API call
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "http://api.openweathermap.org/data/2.5/onecall"
    assert kwargs['params']['q'] == "London"
    assert kwargs['params']['appid'] == "test_key"
    assert kwargs['params']['exclude'] == "current,minutely,hourly,daily"

@patch('requests.get')
def test_api_error_handling(mock_get, weather_plugin_manager):
    """Test API error handling."""
    # Mock API error
    mock_get.side_effect = Exception("API Error")
    
    # Initialize plugin with test API key
    module = weather_plugin_manager.get_plugin_module("weather")
    plugin = module.initialize({"api_key": "test_key"})
    
    # Test error handling for current weather
    with pytest.raises(Exception) as exc_info:
        plugin.get_current_weather("London")
    assert str(exc_info.value) == "API Error"
    
    # Test error handling for forecast
    with pytest.raises(Exception) as exc_info:
        plugin.get_forecast("London")
    assert str(exc_info.value) == "API Error"
    
    # Test error handling for alerts
    with pytest.raises(Exception) as exc_info:
        plugin.get_weather_alerts("London")
    assert str(exc_info.value) == "API Error" 