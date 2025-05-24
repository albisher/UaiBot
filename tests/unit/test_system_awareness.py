import pytest
from uaibot.core.awareness.system_awareness import SystemAwarenessManager
from uaibot.core.awareness.network_awareness import NetworkAwarenessManager
from uaibot.core.awareness.battery_awareness import BatteryAwarenessManager
from uaibot.core.awareness.user_awareness import UserAwarenessManager
from uaibot.core.awareness.time_awareness import TimeAwarenessManager

def test_mouse_position():
    mgr = SystemAwarenessManager()
    pos = mgr.get_mouse_position()
    assert isinstance(pos, tuple) and len(pos) == 2

def test_screen_size():
    mgr = SystemAwarenessManager()
    size = mgr.get_screen_size()
    assert isinstance(size, tuple) and len(size) == 2

def test_mouse_info():
    mgr = SystemAwarenessManager()
    info = mgr.get_mouse_info()
    assert 'position' in info

def test_open_windows():
    mgr = SystemAwarenessManager()
    windows = mgr.get_open_windows()
    assert isinstance(windows, list)
    # On mac/linux, may only have titles
    if windows:
        assert 'title' in windows[0]

def test_system_resources():
    mgr = SystemAwarenessManager()
    res = mgr.get_system_resources()
    assert "cpu_percent" in res and "memory" in res

def test_processes():
    mgr = SystemAwarenessManager()
    procs = mgr.get_processes()
    assert isinstance(procs, list)

def test_active_app():
    mgr = SystemAwarenessManager()
    # Just check it runs, may be None
    _ = mgr.get_active_app()

def test_network_info():
    mgr = SystemAwarenessManager()
    net = mgr.get_network_info()
    assert 'hostname' in net

def test_uptime():
    mgr = SystemAwarenessManager()
    up = mgr.get_uptime()
    assert isinstance(up, str)

def test_battery_info():
    mgr = SystemAwarenessManager()
    # May be None on desktops
    _ = mgr.get_battery_info()

def test_user_sessions():
    mgr = SystemAwarenessManager()
    _ = mgr.get_user_sessions()

def test_env_vars():
    mgr = SystemAwarenessManager()
    env = mgr.get_env_vars()
    assert isinstance(env, dict)

def test_time_info():
    mgr = SystemAwarenessManager()
    t = mgr.get_time_info()
    assert 'now' in t

def test_editing_apps():
    mgr = SystemAwarenessManager()
    editing = mgr.get_editing_apps()
    assert isinstance(editing, list)

# Sub-capability tests

def test_network_awareness():
    mgr = NetworkAwarenessManager()
    net = mgr.get_network_info()
    assert 'hostname' in net

def test_battery_awareness():
    mgr = BatteryAwarenessManager()
    _ = mgr.get_battery_info()

def test_user_awareness():
    mgr = UserAwarenessManager()
    _ = mgr.get_user_sessions()
    _ = mgr.get_env_vars()

def test_time_awareness():
    mgr = TimeAwarenessManager()
    t = mgr.get_time_info()
    assert 'now' in t 