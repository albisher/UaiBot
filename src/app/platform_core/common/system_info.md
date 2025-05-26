# System Information Gathering

The system information gathering system provides a unified interface for retrieving detailed system information across different platforms, with support for localization and platform-specific optimizations.

## Overview

The system is built around the `BaseSystemInfoGatherer` abstract base class, which defines the interface for gathering system information. Platform-specific implementations inherit from this base class and provide platform-specific information while maintaining a consistent interface.

## Architecture

```
BaseSystemInfoGatherer (Abstract)
├── MacSystemInfoGatherer
├── WindowsSystemInfoGatherer
└── UbuntuSystemInfoGatherer
```

## Base Interface

### BaseSystemInfoGatherer

The base class defines the core interface for system information gathering:

```python
class BaseSystemInfoGatherer(ABC):
    @abstractmethod
    def get_system_info(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get system information for the current platform."""
        pass
    
    def get_common_info(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get common system information available on all platforms."""
        pass
    
    def get_localized_system_info(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get system information with localized labels."""
        pass
```

## Information Categories

The system information is organized into the following categories:

### Platform Information
- System name and version
- Release information
- Machine architecture
- Processor details
- Platform-specific details (e.g., macOS version, Windows edition)

### CPU Information
- Physical and logical core counts
- CPU frequencies (max, min, current)
- Per-core usage statistics
- Total CPU usage

### Memory Information
- Total memory
- Available memory
- Used memory
- Memory usage percentage

### Disk Information
- Total disk space
- Used disk space
- Free disk space
- Disk usage percentage

### Network Information
- Bytes sent/received
- Packets sent/received
- Network interface details

## Platform-Specific Implementations

### MacSystemInfoGatherer

Gathers macOS-specific information:
- macOS version (via `sw_vers`)
- Kernel version (via `uname`)
- Boot time (via `sysctl`)
- Hostname (via `hostname`)

### WindowsSystemInfoGatherer

Gathers Windows-specific information:
- Windows version (via registry)
- Edition information
- Build number
- Hostname

### UbuntuSystemInfoGatherer

Gathers Ubuntu-specific information:
- Ubuntu version (via `lsb_release`)
- Kernel version (via `uname`)
- Boot time (via `uptime`)
- Hostname

## Internationalization

The system information gathering system supports localization through:

1. Language-specific labels for all information categories
2. RTL language support (Arabic, Hebrew, etc.)
3. Regional variants for Arabic
4. Fallback mechanisms for missing translations

Example usage:
```python
# Get system info in English
en_info = gatherer.get_system_info('en')

# Get system info in Arabic
ar_info = gatherer.get_system_info('ar')

# Get system info in Saudi Arabic
ar_sa_info = gatherer.get_system_info('ar-SA')
```

## Error Handling

The system implements robust error handling:
- Graceful fallbacks for missing information
- Platform-specific error handling
- Consistent error reporting across platforms
- Localized error messages

## Performance Considerations

The system is designed for efficiency:
- Caching of common information
- Lazy loading of platform-specific details
- Minimal system calls
- Efficient data structures

## Usage Examples

### Basic Usage
```python
from labeeb.platform_core.platform_manager import get_platform_system_info_gatherer

# Get the appropriate gatherer for current platform
gatherer = get_platform_system_info_gatherer()

# Get system information
info = gatherer.get_system_info()

# Access specific information
platform_info = info['platform']
cpu_info = info['cpu']
memory_info = info['memory']
```

### Localized Usage
```python
# Get localized system information
localized_info = gatherer.get_localized_system_info('ar')

# Access localized labels
platform_label = localized_info['معلومات النظام']
cpu_label = localized_info['معلومات المعالج']
```

## Testing

The system includes comprehensive tests:
- Unit tests for each platform implementation
- Integration tests for the platform manager
- Localization tests
- Error handling tests
- Performance tests

## Contributing

When adding new system information:
1. Add the information to the appropriate category
2. Implement platform-specific gathering methods
3. Add localization support
4. Add appropriate tests
5. Update documentation

## Best Practices

1. Use the common interface for new implementations
2. Implement proper error handling
3. Add localization support
4. Write comprehensive tests
5. Document platform-specific details
6. Consider performance implications
7. Maintain backward compatibility 