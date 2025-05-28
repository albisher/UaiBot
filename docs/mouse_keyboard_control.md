# Mouse and Keyboard Control in Labeeb

**PyAutoGUI is the official and default technology for all screenshots, mouse, and keyboard automation in Labeeb. All workflows, tools, and tests should use PyAutoGUI for these tasks to ensure cross-platform compatibility (Linux, macOS, Windows).**

This document provides comprehensive guidance on using Labeeb's mouse and keyboard control functionality in different environments, including those without a display server.

## Overview

Labeeb's `MouseKeyboardHandler` class provides cross-platform mouse and keyboard control using PyAutoGUI as the primary library, with optional support for the keyboard and mouse libraries for advanced features.

The handler supports two main operational modes:
1. **Normal mode**: Controls actual mouse and keyboard in a graphical environment
2. **Simulation mode**: Simulates actions without requiring a display server

These libraries allow Labeeb to programmatically simulate mouse movements, clicks, and keyboard input from scripts or the command line interface.

## Installation Requirements

### Core Library
```bash
pip install pyautogui
```

### Optional Libraries
```bash
# For advanced keyboard control (Windows/Linux only)
pip install keyboard

# For advanced mouse event handling
pip install mouse
```

## Basic Usage Examples

### Mouse Control

```python
import pyautogui

# Move the mouse to specific coordinates
pyautogui.moveTo(100, 150)

# Click at the current position
pyautogui.click()

# Right-click
pyautogui.rightClick()

# Double-click
pyautogui.doubleClick()

# Drag from one position to another
pyautogui.dragTo(300, 400, duration=1.0)
```

### Keyboard Control

```python
import pyautogui

# Type text with delay between keystrokes
pyautogui.write('Hello, world!', interval=0.25)

# Press individual keys
pyautogui.press('enter')

# Press multiple keys in sequence
pyautogui.press(['up', 'up', 'down', 'down'])

# Hold down a modifier key and press others
with pyautogui.hold('shift'):
    pyautogui.press(['left', 'left', 'left', 'left'])

# Press hotkey combinations
pyautogui.hotkey('ctrl', 'c')  # Presses Ctrl+C
```

## Advanced Usage

### Advanced Keyboard Control (with keyboard library)

```python
import keyboard

# Register a hotkey
keyboard.add_hotkey('ctrl+alt+p', lambda: print('Hotkey pressed!'))

# Wait for a specific key
keyboard.wait('esc')  # Blocks until ESC is pressed

# Record keystrokes
recorded = keyboard.record(until='esc')  # Records until ESC is pressed

# Play back recorded keystrokes
keyboard.play(recorded, speed_factor=1.0)
```

### Advanced Mouse Control (with mouse library)

```python
import mouse

# Register click event
mouse.on_click(lambda: print('Mouse clicked!'))

# Register move event
mouse.on_move(lambda x, y: print(f'Mouse moved to {x}, {y}'))

# Record and play mouse movements
events = mouse.record(until=5)  # Record for 5 seconds
mouse.play(events)
```

## Labeeb's MouseKeyboardHandler Class

Labeeb provides a `MouseKeyboardHandler` class that wraps these libraries for easy use within the application.

### Basic Usage

```python
from input_control import MouseKeyboardHandler

handler = MouseKeyboardHandler()

# Mouse operations
handler.move_mouse(100, 100)
handler.click()
handler.right_click()
handler.double_click()

# Keyboard operations
handler.type_text("Hello, Labeeb!")
handler.press_key('enter')
handler.hotkey('ctrl', 'c')
```

### Simulation Mode

Simulation mode is automatically activated when no display is available, but you can also force it:

```python
import os
os.environ['DISPLAY'] = ''  # Force simulation mode

from input_control import MouseKeyboardHandler
handler = MouseKeyboardHandler()
```

In simulation mode:
- All actions are logged but not actually performed
- Methods return success status as if actions were performed
- Position tracking is maintained for mouse operations

This is useful for:
- Testing in headless environments
- Running scripts on servers without displays
- CI/CD pipelines
- Debugging without affecting the actual system

### Key Holding Pattern

Hold keys while performing other actions:

```python
# Using a context manager
with handler.hold_key('shift'):
    handler.press_key('left')
    handler.press_key('left')
    
# Or with an action function
def select_and_copy():
    handler.press_key('a')
    return True

handler.hold_key('ctrl', select_and_copy)
```

### Example Scripts

For working examples, see:
- `/demo_mouse_keyboard.py` - Demonstrates the MouseKeyboardHandler class
- `/examples/basic_simulation_test.py` - Simple test for simulation mode
- `/examples/comprehensive_simulation_test.py` - Tests all functions in simulation mode
- `/examples/debug_mouse_keyboard.py` - Detailed debugging information
- `/examples/pyautogui_basic_example.py` - Basic PyAutoGUI example
- `/examples/mouse_keyboard_example.py` - More comprehensive example with all features

## Safety Considerations

1. **Failsafe**: PyAutoGUI has a failsafe feature that stops execution when the mouse is moved to a corner of the screen.
2. **Pauses**: Adding pauses between actions helps prevent issues with scripts running too quickly.
3. **Permissions**: Some platforms may require administrator privileges for keyboard control.

## Platform Compatibility

| Feature | Windows | macOS | Linux | Headless/No Display |
|---------|:-------:|:-----:|:-----:|:------------------:|
| Basic Mouse Control | ✅ | ✅ | ✅ | ✅ (Simulated) |
| Basic Keyboard Control | ✅ | ✅ | ✅ | ✅ (Simulated) |
| Advanced Keyboard Library | ✅ | ❌ | ✅ | ❌ |
| Advanced Mouse Library | ✅ | ✅ | ✅ | ❌ |
| Simulation Mode | ✅ | ✅ | ✅ | ✅ (Default) |

## Troubleshooting

### Linux Permission Issues

If you encounter permission errors with the keyboard or mouse libraries:

```bash
# Add your user to the input group
sudo usermod -a -G input $USER

# Or run your script with sudo
sudo python your_script.py
```

### No Display Available

If you see "No X display available" errors:
- This is normal in headless environments
- The handler will automatically use simulation mode
- Check if the operations you need can work in simulation mode

### Library Installation Issues

If you face dependency installation problems:
- On Linux: `sudo apt-get install python3-xlib python3-tk python3-dev`
- On macOS: `pip install -U pyobjc-core pyobjc`
- On Windows: Ensure you have Python installed from python.org (not Windows Store)

## Reference

For more detailed information, refer to:

- `/reference/enhance_knm.txt` - Enhancement documentation
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io)
- [keyboard Library](https://github.com/boppreh/keyboard)
- [mouse Library](https://github.com/boppreh/mouse)
