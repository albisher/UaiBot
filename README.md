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

## System Awareness Tool

UaiBot includes a SystemAwarenessTool for querying system state, mouse, windows, keyboard, and processes. This tool is registered with the agent and can be used from both the CLI and GUI.

### Example Usage

```python
# Get system info
result = agent.plan_and_execute(command="get_system_info")

# Get mouse position
result = agent.plan_and_execute(command="get_mouse_position")

# Get process list
result = agent.plan_and_execute(command="get_process_list")
```

### Available Actions
- `get_system_info`: Returns OS, version, CPU, memory, disk, and time
- `get_mouse_position`: Returns current mouse coordinates
- `get_screen_size`: Returns screen size
- `get_mouse_info`: Returns mouse position and pixel color
- `get_process_list`: Returns running processes

## User Routine Awareness Tool

UaiBot includes a UserRoutineAwarenessTool for tracking user routines and activity patterns. This tool is registered with the agent and can be used from both the CLI and GUI.

### Example Usage

```python
# Get current activity state
result = agent.plan_and_execute(command="get_activity")

# Update keyboard activity
result = agent.plan_and_execute(command="update_keyboard_activity")
```

### Available Actions
- `get_activity`: Returns the current activity state
- `update_input_activity`: Updates last input activity timestamp
- `update_screen_dim`: Updates last screen dim timestamp
- `update_keyboard_activity`: Updates last keyboard activity timestamp
- `update_mouse_activity`: Updates last mouse activity timestamp
- `update_window_change`: Updates last window change timestamp

## Device Awareness Tool

UaiBot includes a DeviceAwarenessTool for detecting and monitoring devices across platforms. This tool is registered with the agent and can be used from both the CLI and GUI.

### Example Usage

```python
# Get all connected devices
result = agent.plan_and_execute(command="get_all_devices")

# Get USB devices
result = agent.plan_and_execute(command="get_usb_devices")

# Get audio devices
result = agent.plan_and_execute(command="get_audio_devices")

# Get screen devices
result = agent.plan_and_execute(command="get_screen_devices")
```

### Available Actions
- `get_all_devices`: Returns all detected devices (USB, audio, screen)
- `get_usb_devices`: Returns connected USB devices
- `get_audio_devices`: Returns audio input/output devices
- `get_screen_devices`: Returns screen/monitor devices

### Platform Support
- **macOS**: Full support for USB, audio, and screen devices
- **Windows**: Full support for USB and audio devices, basic screen support
- **Linux**: Basic USB support via lsusb, audio support via PyAudio

### Dependencies
- PyAudio for audio device detection
- Platform-specific libraries (Quartz for macOS, WMI for Windows)
- PyAutoGUI for screen information

## Troubleshooting & Cross-Platform Notes
- Some features (e.g., window info, app awareness) may be limited on certain platforms.
- All platform-specific code is guarded; if a feature is unavailable, a clear error is returned.
- For best results, ensure all dependencies are installed for your OS (see `requirements.txt`).
- If you encounter issues, check the logs and consult the [Technology Stack MDC](docs/rules/technology_stack.mdc).
