# Labeeb System Awareness Module

This module provides comprehensive system awareness capabilities for Labeeb, allowing it to monitor and understand various aspects of the system environment.

## Overview

The awareness module is divided into several sub-capabilities, each focusing on a specific aspect of system awareness:

1. **Audio Awareness**
   - Monitors audio input/output devices
   - Cross-platform support (macOS, Windows, Linux)
   - Provides device information including name, type, and host API

2. **Bluetooth Awareness**
   - Tracks Bluetooth devices and their connection status
   - Platform-specific implementations for optimal device discovery
   - Supports device name, address, and connection state monitoring

3. **Sensor Awareness**
   - Monitors system sensors including:
     - Screen brightness
     - System temperature
     - Battery status
   - Cross-platform support with fallback mechanisms

4. **User Routine Awareness**
   - Tracks user activity patterns:
     - Keyboard activity
     - Mouse movement
     - Screen dimming
     - Window changes
   - Provides idle time monitoring
   - Platform-specific event monitoring

## Usage

### Audio Awareness

```python
from labeeb.core.awareness.audio_awareness import AudioAwarenessManager

audio_mgr = AudioAwarenessManager()
devices = audio_mgr.get_audio_devices()
input_devices = audio_mgr.get_input_devices()
output_devices = audio_mgr.get_output_devices()
```

### Bluetooth Awareness

```python
from labeeb.core.awareness.bluetooth_awareness import BluetoothAwarenessManager

bt_mgr = BluetoothAwarenessManager()
devices = bt_mgr.get_bluetooth_devices()
connected_devices = bt_mgr.get_connected_devices()
```

### Sensor Awareness

```python
from labeeb.core.awareness.sensor_awareness import SensorAwarenessManager

sensor_mgr = SensorAwarenessManager()
brightness = sensor_mgr.get_screen_brightness()
temperature = sensor_mgr.get_system_temperature()
battery = sensor_mgr.get_battery_status()
all_sensors = sensor_mgr.get_all_sensors()
```

### User Routine Awareness

```python
from labeeb.core.awareness.user_routine_awareness import UserRoutineAwarenessManager

routine_mgr = UserRoutineAwarenessManager()
activity = routine_mgr.get_user_routine()
is_active = routine_mgr.is_user_active(idle_threshold_seconds=300)
```

## Dependencies

- `sounddevice`: For audio device monitoring
- `screen-brightness-control`: For screen brightness control
- `psutil`: For system monitoring
- `pywin32`: For Windows-specific features
- `Xlib`: For Linux-specific features
- `Quartz`: For macOS-specific features

## Error Handling

All managers implement comprehensive error handling:
- Platform-specific operations are wrapped in try-except blocks
- Failed operations are logged with appropriate error messages
- Graceful fallbacks are provided when operations fail

## Testing

Run the test suite:

```bash
pytest tests/core/test_awareness_subcapabilities.py -v
```

## Contributing

When adding new awareness capabilities:
1. Create a new manager class in the appropriate file
2. Implement platform-specific methods
3. Add comprehensive error handling
4. Write unit tests
5. Update this documentation

## Platform Support

- **macOS**: Full support for all capabilities
- **Windows**: Full support with Windows-specific implementations
- **Linux**: Full support with Linux-specific implementations

## Future Improvements

- Add support for more sensors
- Implement device hot-plugging detection
- Add historical data tracking
- Implement machine learning for user pattern recognition
- Add support for more audio device properties
- Implement Bluetooth device pairing management 