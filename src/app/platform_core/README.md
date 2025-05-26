# Platform Core

The Platform Core module provides platform-specific functionality and abstractions for UaiBot, ensuring consistent behavior across different operating systems while maintaining platform-specific optimizations.

## Overview

The Platform Core is designed with the following principles:
- Platform-agnostic interfaces with platform-specific implementations
- Clean separation of concerns
- Comprehensive internationalization support
- Robust error handling and fallbacks
- Extensive test coverage

## Directory Structure

```
platform_core/
├── common/                 # Common interfaces and utilities
│   ├── base_handler.py    # Base handler interface
│   └── system_info.py     # Base system info gatherer
├── mac/                   # macOS-specific implementations
│   ├── input_handler.py
│   ├── audio_handler.py
│   ├── display_handler.py
│   ├── usb_handler.py
│   └── system_info.py
├── windows/              # Windows-specific implementations
│   ├── input_handler.py
│   ├── audio_handler.py
│   ├── display_handler.py
│   ├── usb_handler.py
│   └── system_info.py
├── ubuntu/              # Ubuntu-specific implementations
│   ├── input_handler.py
│   ├── audio_handler.py
│   ├── display_handler.py
│   ├── usb_handler.py
│   └── system_info.py
├── translations/        # Internationalization files
│   ├── en.json        # English translations
│   ├── ar.json        # Arabic translations
│   └── ...
├── i18n.py            # Internationalization support
├── platform_manager.py # Platform management and coordination
└── README.md          # This file
```

## Key Components

### Platform Manager

The `PlatformManager` class serves as the central coordinator for platform-specific functionality. It:
- Detects the current platform
- Manages platform-specific handlers
- Provides a unified interface for system information
- Handles configuration management
- Coordinates between different platform components

### System Information

The system information gathering system provides detailed information about the current system state:
- Platform-specific details (OS version, kernel version, etc.)
- Hardware information (CPU, memory, disk, network)
- Real-time metrics (usage, performance)
- Localized output in multiple languages

### Internationalization

The i18n system provides comprehensive language support:
- Built-in support for multiple languages
- Special handling for RTL languages (Arabic, Hebrew, etc.)
- Regional variants for Arabic (Saudi, Egyptian, Moroccan, etc.)
- Fallback mechanisms for missing translations
- Consistent formatting across platforms

### Platform Handlers

Platform-specific handlers provide consistent interfaces for:
- Input handling (keyboard, mouse, touch)
- Audio input/output
- Display management
- USB device interaction

## Usage

### Basic Usage

```python
from uaibot.platform_core.platform_manager import PlatformManager

# Initialize platform manager
platform_manager = PlatformManager()
platform_manager.initialize()

# Get system information
system_info = platform_manager.get_system_info()

# Get platform-specific handler
input_handler = platform_manager.get_handler('input')
```

### Internationalization

```python
from uaibot.platform_core.i18n import gettext, is_rtl

# Get translated text
text = gettext('platform_info', 'ar')  # Arabic
text = gettext('platform_info', 'ar-SA')  # Saudi Arabic

# Check if language is RTL
is_rtl_language = is_rtl('ar')
```

## Supported Platforms

- macOS (Darwin)
- Windows
- Ubuntu (Linux)

## Language Support

### Primary Languages
- Arabic (Modern Standard Arabic)
- Arabic Regional Variants:
  - Saudi Arabic (ar-SA)
  - Egyptian Arabic (ar-EG)
  - Moroccan Arabic (ar-MA)
  - Kuwaiti Arabic (ar-KW)
  - And more...

### Secondary Languages
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Russian (ru)
- Hindi (hi)

## Development

### Adding New Platform Support

1. Create a new platform directory (e.g., `platform_core/new_platform/`)
2. Implement platform-specific handlers
3. Add platform detection in `PlatformManager`
4. Add platform-specific tests
5. Update documentation

### Adding New Language Support

1. Create a new translation file in `translations/` (e.g., `new_lang.json`)
2. Add language code to `SUPPORTED_LANGUAGES` in `i18n.py`
3. Add RTL support if needed
4. Add language-specific tests

## Testing

Run the test suite:
```bash
pytest tests/unit/platform_core/
```

## Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive tests for new functionality
3. Update documentation for any changes
4. Ensure proper error handling and fallbacks
5. Maintain backward compatibility

## License

This module is part of UaiBot and is subject to the project's license terms. 