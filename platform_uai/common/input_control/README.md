# UaiBot Input Control Framework

## Overview

This directory contains the platform-agnostic foundation for UaiBot's input control system. The input control system provides a unified interface for controlling mouse and keyboard across different platforms (Windows, macOS, Ubuntu, and Jetson).

## Files

- `base_handler.py`: Abstract base class defining the interface for all platform-specific implementations
- `mouse_keyboard_handler.py`: Cross-platform implementation with simulation mode support
- `__init__.py`: Package initialization file

## Architecture

The input control system follows a platform-specific architecture:

1. The `BaseInputHandler` abstract class defines the interface that all platform-specific handlers must implement.

2. Each platform (Windows, macOS, Ubuntu, Jetson) has its own implementation that inherits from `BaseInputHandler`.

3. The common `MouseKeyboardHandler` class provides a cross-platform implementation with simulation mode that works on all platforms.

4. The `platform_utils.py` file provides a `get_input_handler()` function that automatically selects the appropriate handler for the current platform.

5. A compatibility layer in `/input_control/mouse_keyboard_handler.py` ensures backward compatibility with existing code.

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
from platform_uai.platform_utils import get_input_handler
handler = get_input_handler()

# Method 2: Using the convenience function in the root input_control.py
from input_control import get_platform_handler
handler = get_platform_handler()

# Method 3: Using a specific implementation directly
from platform_uai.ubuntu.input_control import UbuntuInputHandler
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
