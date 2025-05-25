import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from uaibot.core.ai.uaibot_agent import UaiAgent
from uaibot.core.plugins import PluginManager

@pytest.fixture
def weather_agent(uaibot_agent, weather_plugin_manager):
    """Create a UaiAgent instance with the weather plugin loaded."""
    # Initialize the weather plugin with a test API key
    module = weather_plugin_manager.get_plugin_module("weather")
    plugin = module.initialize({"api_key": "test_key"})
    
    # Add the plugin to the agent's plugin manager
    uaibot_agent.plugin_manager = weather_plugin_manager
    
    return uaibot_agent

@patch('requests.get')
def test_weather_command_execution(mock_get, weather_agent):
    """Test executing weather commands through the agent."""
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
    
    # Test current weather command
    result = weather_agent.plan_and_execute(
        command="weather",
        parameters={"city": "London"}
    )
    
    assert result['status'] == 'success'
    assert 'temperature' in result['data']
    assert result['data']['temperature'] == 20.5
    assert result['data']['description'] == 'clear sky'
    
    # Verify API call
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "http://api.openweathermap.org/data/2.5/weather"
    assert kwargs['params']['q'] == "London"

@patch('requests.get')
def test_forecast_command_execution(mock_get, weather_agent):
    """Test executing forecast commands through the agent."""
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
    
    # Test forecast command
    result = weather_agent.plan_and_execute(
        command="forecast",
        parameters={"city": "London", "days": 1}
    )
    
    assert result['status'] == 'success'
    assert 'forecast' in result['data']
    assert len(result['data']['forecast']) == 1
    assert result['data']['forecast'][0]['datetime'] == "2024-03-20 12:00:00"
    
    # Verify API call
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "http://api.openweathermap.org/data/2.5/forecast"
    assert kwargs['params']['q'] == "London"

@patch('requests.get')
def test_alerts_command_execution(mock_get, weather_agent):
    """Test executing alerts commands through the agent."""
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
    
    # Test alerts command
    result = weather_agent.plan_and_execute(
        command="alerts",
        parameters={"city": "London"}
    )
    
    assert result['status'] == 'success'
    assert 'alerts' in result['data']
    assert len(result['data']['alerts']) == 1
    assert result['data']['alerts'][0]['event'] == "Severe Thunderstorm Warning"
    
    # Verify API call
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "http://api.openweathermap.org/data/2.5/onecall"
    assert kwargs['params']['q'] == "London"

def test_invalid_weather_command(weather_agent):
    """Test handling of invalid weather commands."""
    result = weather_agent.plan_and_execute(
        command="invalid_weather_command",
        parameters={"city": "London"}
    )
    
    assert result['status'] == 'error'
    assert 'Unknown command' in result['message']

def test_missing_parameters(weather_agent):
    """Test handling of missing parameters."""
    result = weather_agent.plan_and_execute(
        command="weather",
        parameters={}
    )
    
    assert result['status'] == 'error'
    assert 'Missing required parameter' in result['message']

@patch('requests.get')
def test_api_error_handling(mock_get, weather_agent):
    """Test handling of API errors through the agent."""
    # Mock API error
    mock_get.side_effect = Exception("API Error")
    
    result = weather_agent.plan_and_execute(
        command="weather",
        parameters={"city": "London"}
    )
    
    assert result['status'] == 'error'
    assert 'API Error' in result['message'] 