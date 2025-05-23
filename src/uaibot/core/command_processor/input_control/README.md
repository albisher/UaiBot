# UaiBot Input Control Framework

## Overview

This directory contains the platform-agnostic foundation for UaiBot's input control system. The input control system provides a unified interface for controlling mouse and keyboard across different platforms (Windows, macOS, Ubuntu, and Jetson).

## File Organization

The input control system follows a clear organization structure:

```
/src/uaibot/
    /platform_uai/           # System files for platform-specific implementations
        /common/
            /input_control/
                base_handler.py      # Core interface definition
                mouse_keyboard_handler.py  # Core implementation
                __init__.py
        /ubuntu/
            /input_control/
                ubuntu_input_handler.py  # Ubuntu-specific implementation
                __init__.py
        /windows/
            /input_control/
                windows_input_handler.py  # Windows-specific implementation
                __init__.py
        /mac/
            /input_control/
                mac_input_handler.py  # macOS-specific implementation
                __init__.py
        /jetson/
            /input_control/
                jetson_input_handler.py  # Jetson-specific implementation
                __init__.py
    /setup/                  # Setup files for one-time initialization
        /input_control/
            input_setup.py   # Input control initialization
            device_setup.py  # Device detection and setup
    /tests/                  # Test files (development only)
        /input_control/
            test_handlers.py
            test_platforms.py
```

## File Naming Conventions

1. **System Files**: Core functionality files that are required for the system to operate
   - Located in `/src/uaibot/platform_uai/`
   - Named descriptively (e.g., `ubuntu_input_handler.py`, `mac_input_handler.py`)
   - No "test" in production filenames

2. **Setup Files**: One-time initialization or health check files
   - Located in `/src/uaibot/setup/`
   - Named with `_setup.py` suffix
   - Run during initial setup or health checks

3. **Test Files**: Development and testing files
   - Located in `/tests/`
   - Named with `test_` prefix
   - Not included in production builds

## Architecture

The input control system follows a platform-specific architecture:

1. The `BaseInputHandler` abstract class defines the interface that all platform-specific handlers must implement.

2. Each platform (Windows, macOS, Ubuntu, Jetson) has its own implementation that inherits from `BaseInputHandler`.

3. The common `MouseKeyboardHandler` class provides a cross-platform implementation with simulation mode that works on all platforms.

4. The `platform_utils.py` file provides a `get_input_handler()` function that automatically selects the appropriate handler for the current platform.

## Simulation Mode

Simulation mode is a key feature that allows UaiBot to run in environments without a display (such as headless servers, CI environments, or Docker containers). 

In simulation mode:
- Mouse movements are tracked internally but not actually performed
- Screen size defaults to a reasonable value (1920x1080)
- All operations are logged but not actually executed

Simulation mode is automatically enabled when:
- No display is available (`DISPLAY` and `WAYLAND_DISPLAY` environment variables are empty or not set)
- Required libraries cannot be imported or initialized
- Explicit activation via setting `DISPLAY=''` before importing

## Usage

```python
# Method 1: Using the platform_utils function
from uaibot.platform_uai.platform_utils import get_input_handler
handler = get_input_handler()

# Method 2: Using a specific implementation directly
from uaibot.platform_uai.ubuntu.input_control import UbuntuInputHandler
handler = UbuntuInputHandler()
```

## Testing

Test files are located in `/tests/input_control/`.

Run the demo script to see the input control system in action:

```bash
python demo/demo_input_control.py
```

To run in simulation mode:

```bash
python demo/demo_input_control.py --simulate
```

or

```bash
DISPLAY= python demo/demo_input_control.py
```
