# UaiBot Framework

A powerful and extensible framework for building intelligent agents and bots.

## Features

- **Agent System**: Core framework for building intelligent agents
- **Caching System**: Efficient caching with memory and disk storage
- **Authentication System**: Secure user management and access control
- **Plugin System**: Extensible plugin architecture for adding new functionality
- **Weather Plugin**: Example plugin demonstrating weather data integration
- **Comprehensive Testing**: Extensive test coverage for all components

## Installation

```bash
pip install uaibot
```

## Quick Start

```python
from uaibot.core.ai.uaibot_agent import UaiAgent

# Initialize the agent
agent = UaiAgent()

# Execute a command
result = agent.plan_and_execute(
    command="weather",
    parameters={"city": "London"}
)
```

## Plugin System

The UaiBot framework includes a powerful plugin system that allows you to extend its functionality. Plugins can add new commands, integrate with external services, and enhance the agent's capabilities.

### Creating a Plugin

```python
from uaibot.core.plugins import PluginInfo

# Define plugin metadata
plugin_info = PluginInfo(
    name="my_plugin",
    version="1.0.0",
    description="My custom plugin",
    author="Your Name",
    entry_point="my_plugin:initialize"
)

# Create plugin class
class MyPlugin:
    def __init__(self, config):
        self.config = config
    
    def handle_command(self, command, parameters):
        # Handle plugin commands
        pass

# Initialize function
def initialize(config):
    return MyPlugin(config)
```

### Loading Plugins

```python
from uaibot.core.plugins import PluginManager

# Initialize plugin manager
plugin_manager = PluginManager()

# Load a plugin
plugin_info = plugin_manager.register_plugin("path/to/plugin.py")
plugin_manager.load_plugin(plugin_info.name)
```

### Weather Plugin

The framework includes a weather plugin that demonstrates plugin integration:

```python
# Initialize weather plugin
weather_plugin = plugin_manager.get_plugin_module("weather").initialize({
    "api_key": "your_api_key"
})

# Get current weather
weather = weather_plugin.get_current_weather("London")

# Get forecast
forecast = weather_plugin.get_forecast("London", days=5)

# Get weather alerts
alerts = weather_plugin.get_weather_alerts("London")
```

## Testing

The framework includes comprehensive tests for all components:

### Running Tests

```bash
pytest tests/
```

### Test Coverage

- Unit tests for core components
- Integration tests for plugin system
- End-to-end tests for agent functionality
- Mock tests for external service integration

## Architecture

The UaiBot framework consists of several core components:

1. **Agent System**: Core framework for building intelligent agents
2. **Caching System**: Efficient caching with memory and disk storage
3. **Authentication System**: Secure user management and access control
4. **Plugin System**: Extensible plugin architecture
5. **Weather Plugin**: Example plugin implementation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Changelog

### 1.0.0
- Initial release
- Implemented caching system
- Added authentication system
- Created plugin system
- Added weather plugin
- Implemented comprehensive testing
