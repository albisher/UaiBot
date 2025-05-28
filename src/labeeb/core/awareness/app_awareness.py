"""
DEPRECATED: App awareness logic has been moved to platform_core/platform_manager.py.
Use PlatformManager for all app awareness logic.
"""

# Deprecated stub for backward compatibility
from platform_core.platform_manager import PlatformManager
from src.app.core.platform_core.platform_utils import get_platform_name

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AppInfo:
    name: str
    pid: int
    user: Optional[str] = None
    status: Optional[str] = None
    window_title: Optional[str] = None
    memory_rss: Optional[int] = None  # in bytes
    memory_vms: Optional[int] = None  # in bytes
    cpu_percent: Optional[float] = None

class AppAwarenessManager:
    """Provides awareness of running and foreground applications across platforms, with detailed info."""
    def __init__(self):
        self.platform = get_platform_name()

    def get_running_apps(self) -> Dict[str, Any]:
        """Get a list of running applications/processes with details."""
        try:
            import psutil
            apps = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'memory_info', 'cpu_percent']):
                try:
                    info = proc.info
                    window_title = None
                    # Platform-specific window title
                    if self.platform == "Darwin":
                        # Try to get window title using osascript (expensive, so only for foreground app)
                        pass
                    elif self.platform == "Windows":
                        try:
                            import win32process, win32gui
                            def callback(hwnd, result):
                                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                                if pid == info['pid'] and win32gui.IsWindowVisible(hwnd):
                                    title = win32gui.GetWindowText(hwnd)
                                    if title:
                                        result.append(title)
                            titles = []
                            import win32con
                            win32gui.EnumWindows(callback, titles)
                            if titles:
                                window_title = titles[0]
                        except Exception:
                            pass
                    elif self.platform == "Linux":
                        # Could use wmctrl/xprop for window titles, but skip for now
                        pass
                    mem = info.get('memory_info')
                    apps.append(AppInfo(
                        name=info.get('name', ''),
                        pid=info.get('pid', -1),
                        user=info.get('username'),
                        status=info.get('status'),
                        window_title=window_title,
                        memory_rss=mem.rss if mem else None,
                        memory_vms=mem.vms if mem else None,
                        cpu_percent=info.get('cpu_percent')
                    ))
                except Exception as e:
                    logger.debug(f"Failed to get info for process: {e}")
            return {"apps": [a.__dict__ for a in apps], "status": "ok", "message": ""}
        except Exception as e:
            logger.error(f"Failed to enumerate running apps: {e}")
            return {"apps": [], "status": "unavailable", "message": str(e)}

    def get_foreground_app(self) -> Dict[str, Any]:
        """Get the current foreground/active application with details."""
        try:
            if self.platform == "Darwin":
                try:
                    import subprocess, psutil
                    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
                    name = subprocess.check_output(["osascript", "-e", script]).decode().strip()
                    pid = None
                    window_title = None
                    mem_rss = None
                    mem_vms = None
                    cpu_percent = None
                    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                        if proc.info['name'] == name:
                            pid = proc.info['pid']
                            mem = proc.info.get('memory_info')
                            mem_rss = mem.rss if mem else None
                            mem_vms = mem.vms if mem else None
                            cpu_percent = proc.info.get('cpu_percent')
                            break
                    # Try to get window title (expensive, so only for foreground)
                    try:
                        script = 'tell application "System Events" to get the title of the front window of (first application process whose frontmost is true)'
                        window_title = subprocess.check_output(["osascript", "-e", script]).decode().strip()
                    except Exception:
                        window_title = None
                    return {"app": {"name": name, "pid": pid, "window_title": window_title, "memory_rss": mem_rss, "memory_vms": mem_vms, "cpu_percent": cpu_percent}, "status": "ok", "message": ""}
                except Exception as e:
                    logger.error(f"Failed to get foreground app (macOS): {e}")
                    return {"app": None, "status": "unavailable", "message": str(e)}
            elif self.platform == "Windows":
                try:
                    import win32gui, win32process, psutil
                    hwnd = win32gui.GetForegroundWindow()
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc = psutil.Process(pid)
                    name = proc.name()
                    window_title = win32gui.GetWindowText(hwnd)
                    mem = proc.memory_info()
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    return {"app": {"name": name, "pid": pid, "window_title": window_title, "memory_rss": mem.rss, "memory_vms": mem.vms, "cpu_percent": cpu_percent}, "status": "ok", "message": ""}
                except Exception as e:
                    logger.error(f"Failed to get foreground app (Windows): {e}")
                    return {"app": None, "status": "unavailable", "message": str(e)}
            else:  # Linux
                try:
                    import subprocess, psutil
                    win_id = subprocess.check_output(["xdotool", "getactivewindow"]).strip()
                    win_name = subprocess.check_output(["xdotool", "getwindowname", win_id]).decode().strip()
                    pid = int(subprocess.check_output(["xdotool", "getwindowpid", win_id]).strip())
                    proc = psutil.Process(pid)
                    name = proc.name()
                    mem = proc.memory_info()
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    return {"app": {"name": name, "pid": pid, "window_title": win_name, "memory_rss": mem.rss, "memory_vms": mem.vms, "cpu_percent": cpu_percent}, "status": "ok", "message": ""}
                except Exception as e:
                    logger.error(f"Failed to get foreground app (Linux): {e}")
                    return {"app": None, "status": "unavailable", "message": str(e)}
        except Exception as e:
            logger.error(f"Failed to get foreground app: {e}")
            return {"app": None, "status": "unavailable", "message": str(e)}

    def get_app_windows(self) -> Dict[str, Any]:
        """Get a list of open application windows (where possible)."""
        try:
            if self.platform == "Darwin":
                try:
                    import subprocess
                    script = 'tell application "System Events" to get the name of every window of (every process whose visible is true)'
                    out = subprocess.check_output(["osascript", "-e", script]).decode()
                    windows = [w.strip() for w in out.split(",") if w.strip()]
                    return {"windows": windows, "status": "ok", "message": ""}
                except Exception as e:
                    logger.error(f"Failed to get app windows (macOS): {e}")
                    return {"windows": [], "status": "unavailable", "message": str(e)}
            elif self.platform == "Windows":
                try:
                    import win32gui
                    def enum_handler(hwnd, result):
                        if win32gui.IsWindowVisible(hwnd):
                            result.append(win32gui.GetWindowText(hwnd))
                    windows = []
                    win32gui.EnumWindows(enum_handler, windows)
                    windows = [w for w in windows if w]
                    return {"windows": windows, "status": "ok", "message": ""}
                except Exception as e:
                    logger.error(f"Failed to get app windows (Windows): {e}")
                    return {"windows": [], "status": "unavailable", "message": str(e)}
            else:  # Linux
                try:
                    import subprocess
                    out = subprocess.check_output(["wmctrl", "-l"]).decode()
                    windows = [line.split(None, 3)[-1] for line in out.splitlines() if len(line.split(None, 3)) == 4]
                    return {"windows": windows, "status": "ok", "message": ""}
                except Exception as e:
                    logger.error(f"Failed to get app windows (Linux): {e}")
                    return {"windows": [], "status": "unavailable", "message": str(e)}
        except Exception as e:
            logger.error(f"Failed to get app windows: {e}")
            return {"windows": [], "status": "unavailable", "message": str(e)} 