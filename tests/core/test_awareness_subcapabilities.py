import pytest
from uaibot.core.awareness.audio_awareness import AudioAwarenessManager
from uaibot.core.awareness.bluetooth_awareness import BluetoothAwarenessManager
from uaibot.core.awareness.sensor_awareness import SensorAwarenessManager
from uaibot.core.awareness.user_routine_awareness import UserRoutineAwarenessManager
import time

def test_audio_awareness_manager():
    mgr = AudioAwarenessManager()
    devices = mgr.get_audio_devices()
    assert isinstance(devices, list)
    for dev in devices:
        assert isinstance(dev, dict)
        assert "name" in dev

def test_bluetooth_awareness_manager():
    mgr = BluetoothAwarenessManager()
    devices = mgr.get_bluetooth_devices()
    assert isinstance(devices, list)
    for dev in devices:
        assert isinstance(dev, dict)
        assert "name" in dev or "address" in dev

def test_sensor_awareness_manager():
    mgr = SensorAwarenessManager()
    brightness = mgr.get_screen_brightness()
    assert isinstance(brightness, dict)
    assert "brightness" in brightness


def test_user_routine_awareness_manager():
    mgr = UserRoutineAwarenessManager()
    # Simulate input activity
    mgr.update_input_activity()
    time.sleep(0.1)
    routine = mgr.get_user_routine()
    assert "idle_time_seconds" in routine
    assert routine["idle_time_seconds"] >= 0
    # Simulate screen dim
    mgr.update_screen_dim()
    time.sleep(0.1)
    routine = mgr.get_user_routine()
    assert "screen_dim_idle_seconds" in routine
    assert routine["screen_dim_idle_seconds"] >= 0 