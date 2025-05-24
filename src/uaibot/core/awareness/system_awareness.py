import pyautogui
import psutil
from typing import List, Tuple, Dict, Optional
import platform

try:
    import pygetwindow as gw
except ImportError:
    gw = None

class SystemAwarenessManager:
    """
    UaiBot System Awareness Capability ('I know')
    Provides awareness of system state, mouse, windows, keyboard, and processes.
    This capability is for knowing, not doing.
    """

    def get_mouse_position(self) -> Tuple[int, int]:
        """Return the current mouse position as (x, y)."""
        return pyautogui.position()

    def get_open_windows(self) -> List[Dict[str, any]]:
        """Return a list of open windows with title and geometry."""
        if gw is None:
            return []
        return [
            {
                'title': w.title,
                'left': w.left,
                'top': w.top,
                'width': w.width,
                'height': w.height
            }
            for w in gw.getAllWindows()
        ]

    def get_active_window(self) -> Optional[Dict[str, any]]:
        """Return the active window's title and geometry, or None."""
        if gw is None:
            return None
        w = gw.getActiveWindow()
        if w:
            return {
                'title': w.title,
                'left': w.left,
                'top': w.top,
                'width': w.width,
                'height': w.height
            }
        return None

    def get_system_resources(self) -> Dict[str, any]:
        """Return CPU, memory, and disk usage info."""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict()
        }

    def get_processes(self) -> List[Dict[str, any]]:
        """Return a list of running processes with pid, name, and status."""
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'status']):
            try:
                procs.append(p.info)
            except Exception:
                continue
        return procs

    def get_active_app(self) -> Optional[str]:
        """Return the name of the currently active application (if possible)."""
        if platform.system() == 'Darwin':
            try:
                import subprocess
                script = 'tell application "System Events" to get name of (processes where frontmost is true)'
                out = subprocess.check_output(['osascript', '-e', script])
                return out.decode('utf-8').strip().split(',')[0]
            except Exception:
                return None
        elif platform.system() == 'Windows' and gw is not None:
            w = gw.getActiveWindow()
            return w.title if w else None
        return None 