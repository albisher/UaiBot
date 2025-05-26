# Platform Manager

The Platform Manager is a central component that handles platform detection, system information gathering, and platform-specific functionality management.

## Overview

The Platform Manager provides:
- Platform detection and validation
- System information gathering
- Platform-specific handler management
- Configuration management
- Internationalization support

## Architecture

```
platform_manager.py
├── Platform Detection
│   ├── OS Detection
│   └── Support Validation
├── System Info Gathering
│   ├── Factory Method
│   └── Info Collection
├── Handler Management
│   ├── Handler Registration
│   └── Handler Access
└── Configuration
    ├── Config Loading
    └── Config Updates
```

## Core Components

### Platform Detection

```python
def detect_platform() -> str:
    """Detect the current platform."""
    system = platform.system().lower()
    if system == 'darwin':
        return 'mac'
    elif system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'ubuntu'
    return 'unknown'
```

### System Info Gathering

```python
def get_system_info(self, language: Optional[str] = None) -> Dict[str, Any]:
    """Get system information with optional localization."""
    gatherer = self.get_system_info_gatherer()
    return gatherer.get_system_info(language)
```

### Handler Management

```python
def get_handler(self, handler_name: str) -> Optional[Any]:
    """Get a platform-specific handler."""
    if not self.is_handler_available(handler_name):
        return None
    return self._handlers.get(handler_name)
```

## Usage Examples

### Basic Platform Detection
```python
from uaibot.platform_core.platform_manager import PlatformManager

# Create manager instance
manager = PlatformManager()

# Get current platform
platform = manager.get_current_platform()
print(f"Current platform: {platform}")
```

### System Information
```python
# Get system information
system_info = manager.get_system_info()

# Get localized system information
localized_info = manager.get_system_info(language='ar')
```

### Platform Handlers
```python
# Check handler availability
if manager.is_handler_available('network'):
    # Get handler
    network_handler = manager.get_handler('network')
    # Use handler
    network_info = network_handler.get_info()
```

## Platform Support

### Supported Platforms
- macOS
- Windows
- Ubuntu

### Platform-Specific Features

#### macOS
- Native system information gathering
- macOS-specific handlers
- Apple Silicon support

#### Windows
- Windows Management Instrumentation (WMI)
- Windows-specific handlers
- PowerShell integration

#### Ubuntu
- Linux system information gathering
- Ubuntu-specific handlers
- Systemd integration

## Configuration

### Configuration Structure
```python
{
    "platform": {
        "name": "mac",
        "version": "12.0",
        "architecture": "arm64"
    },
    "handlers": {
        "network": {
            "enabled": true,
            "timeout": 5
        }
    }
}
```

### Configuration Management
```python
# Update configuration
manager.update_config({
    "handlers": {
        "network": {
            "timeout": 10
        }
    }
})

# Get configuration
config = manager.get_config()
```

## Error Handling

The Platform Manager implements robust error handling:
- Platform detection failures
- Handler initialization errors
- Configuration loading issues
- System information gathering errors

## Performance

The manager is optimized for performance:
- Lazy loading of handlers
- Caching of system information
- Efficient platform detection
- Minimal resource usage

## Testing

The system includes comprehensive tests:
- Platform detection
- System information gathering
- Handler management
- Configuration management
- Error handling

## Contributing

When contributing to the Platform Manager:
1. Follow existing patterns
2. Add appropriate tests
3. Update documentation
4. Consider platform-specific implications
5. Maintain backward compatibility

## Best Practices

### Adding New Platforms

1. Create platform-specific implementation
2. Add platform detection support
3. Implement required handlers
4. Add platform-specific tests
5. Update documentation

### Adding New Handlers

1. Create handler implementation
2. Register handler with manager
3. Add handler configuration
4. Add handler tests
5. Update documentation

### Platform-Specific Considerations

1. Handle platform differences gracefully
2. Implement proper fallbacks
3. Consider performance implications
4. Test on all supported platforms
5. Document platform-specific features 