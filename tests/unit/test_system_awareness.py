import pytest
from uaibot.core.awareness.system_awareness import SystemAwarenessManager

def test_mouse_position():
    mgr = SystemAwarenessManager()
    pos = mgr.get_mouse_position()
    assert isinstance(pos, tuple) and len(pos) == 2

def test_open_windows():
    mgr = SystemAwarenessManager()
    windows = mgr.get_open_windows()
    assert isinstance(windows, list)

def test_system_resources():
    mgr = SystemAwarenessManager()
    res = mgr.get_system_resources()
    assert "cpu_percent" in res and "memory" in res

def test_keyboard_listener(monkeypatch):
    mgr = SystemAwarenessManager()
    called = {"pressed": False}
    def fake_callback(key):
        called["pressed"] = True
    listener = mgr.listen_keyboard(fake_callback)
    # Simulate a key press event
    fake_callback("a")
    assert called["pressed"]
    listener.stop() 