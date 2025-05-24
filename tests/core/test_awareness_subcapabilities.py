import pytest
import time
from datetime import datetime
from uaibot.core.awareness.audio_awareness import AudioAwarenessManager
from uaibot.core.awareness.bluetooth_awareness import BluetoothAwarenessManager
from uaibot.core.awareness.sensor_awareness import SensorAwarenessManager
from uaibot.core.awareness.user_routine_awareness import UserRoutineAwarenessManager

def test_audio_awareness_manager():
    mgr = AudioAwarenessManager()
    
    # Test all devices
    devices = mgr.get_audio_devices()
    assert isinstance(devices, list)
    for dev in devices:
        assert isinstance(dev, dict)
        assert "name" in dev
        assert "type" in dev or "hostapi" in dev
    
    # Test input devices
    input_devices = mgr.get_input_devices()
    assert isinstance(input_devices, list)
    for dev in input_devices:
        assert isinstance(dev, dict)
        assert "name" in dev
    
    # Test output devices
    output_devices = mgr.get_output_devices()
    assert isinstance(output_devices, list)
    for dev in output_devices:
        assert isinstance(dev, dict)
        assert "name" in dev

def test_bluetooth_awareness_manager():
    mgr = BluetoothAwarenessManager()
    
    # Test all devices
    devices = mgr.get_bluetooth_devices()
    assert isinstance(devices, list)
    for dev in devices:
        assert isinstance(dev, dict)
        assert "name" in dev
        assert any(key in dev for key in ["address", "connected", "status"])
    
    # Test connected devices
    connected_devices = mgr.get_connected_devices()
    assert isinstance(connected_devices, list)
    for dev in connected_devices:
        assert isinstance(dev, dict)
        assert "name" in dev
        assert dev.get("connected", False) or dev.get("status", "") == "OK"

def test_sensor_awareness_manager():
    mgr = SensorAwarenessManager()
    
    # Test screen brightness
    brightness = mgr.get_screen_brightness()
    assert isinstance(brightness, dict)
    assert "brightness" in brightness
    assert brightness["brightness"] is None or 0 <= brightness["brightness"] <= 1
    
    # Test system temperature
    temperature = mgr.get_system_temperature()
    assert isinstance(temperature, dict)
    assert "temperature" in temperature
    assert temperature["temperature"] is None or temperature["temperature"] > 0
    
    # Test battery status
    battery = mgr.get_battery_status()
    assert isinstance(battery, dict)
    assert "battery_level" in battery
    assert "is_charging" in battery
    assert battery["battery_level"] is None or 0 <= battery["battery_level"] <= 100
    
    # Test all sensors
    all_sensors = mgr.get_all_sensors()
    assert isinstance(all_sensors, dict)
    assert all(key in all_sensors for key in ["brightness", "temperature", "battery_level", "is_charging"])

def test_user_routine_awareness_manager():
    mgr = UserRoutineAwarenessManager()
    
    # Test initial state
    routine = mgr.get_user_routine()
    assert isinstance(routine, dict)
    assert "idle_time_seconds" in routine
    assert routine["idle_time_seconds"] >= 0
    
    # Test input activity
    mgr.update_input_activity()
    time.sleep(0.1)
    routine = mgr.get_user_routine()
    assert routine["idle_time_seconds"] < 1
    
    # Test screen dim
    mgr.update_screen_dim()
    time.sleep(0.1)
    routine = mgr.get_user_routine()
    assert "screen_dim_idle_seconds" in routine
    assert routine["screen_dim_idle_seconds"] >= 0
    
    # Test keyboard activity
    mgr.update_keyboard_activity()
    time.sleep(0.1)
    routine = mgr.get_user_routine()
    assert "keyboard_idle_seconds" in routine
    assert routine["keyboard_idle_seconds"] >= 0
    
    # Test mouse activity
    mgr.update_mouse_activity()
    time.sleep(0.1)
    routine = mgr.get_user_routine()
    assert "mouse_idle_seconds" in routine
    assert routine["mouse_idle_seconds"] >= 0
    
    # Test window change
    mgr.update_window_change()
    time.sleep(0.1)
    routine = mgr.get_user_routine()
    assert "window_change_idle_seconds" in routine
    assert routine["window_change_idle_seconds"] >= 0
    
    # Test last activity timestamp
    assert "last_activity" in routine
    try:
        datetime.fromisoformat(routine["last_activity"])
    except ValueError:
        pytest.fail("Invalid ISO format timestamp")
    
    # Test user active status
    assert mgr.is_user_active(idle_threshold_seconds=1)  # Should be active
    time.sleep(1.1)
    assert not mgr.is_user_active(idle_threshold_seconds=1)  # Should be inactive 