import os
import socket
import datetime
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
    Provides awareness of system state, mouse, windows, keyboard, processes, and more.
    This capability is for knowing, not doing.
    """

    def get_mouse_position(self) -> Tuple[int, int]:
        """Return the current mouse position as (x, y)."""
        return pyautogui.position()

    def get_screen_size(self) -> Tuple[int, int]:
        """Return the primary screen size as (width, height)."""
        return pyautogui.size()

    def get_mouse_info(self) -> Dict[str, any]:
        """Return mouse position and pixel color under the cursor."""
        pos = pyautogui.position()
        try:
            color = pyautogui.screenshot().getpixel(pos)
        except Exception:
            color = None
        return {
            'position': pos,
            'color': color
        }

    def get_open_windows(self) -> List[Dict[str, any]]:
        """Return a list of open windows with title and geometry (best effort cross-platform)."""
        if gw is None:
            return []
        system = platform.system()
        if system == 'Windows':
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
        else:
            # On macOS/Linux, getAllWindows may not be available; use getAllTitles
            try:
                titles = gw.getAllTitles()
                return [{'title': t} for t in titles if t.strip()]
            except Exception:
                return []

    def get_active_window(self) -> Optional[Dict[str, any]]:
        """Return the active window's title and geometry, or None."""
        if gw is None:
            return None
        w = gw.getActiveWindow()
        if w:
            return {
                'title': w.title,
                'left': getattr(w, 'left', None),
                'top': getattr(w, 'top', None),
                'width': getattr(w, 'width', None),
                'height': getattr(w, 'height', None)
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

    def get_network_info(self) -> Dict[str, any]:
        """Return basic network info: hostname, IP."""
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
        except Exception:
            ip = None
        return {
            'hostname': hostname,
            'ip': ip
        }

    def get_uptime(self) -> str:
        """Return system uptime as a human-readable string."""
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        now = datetime.datetime.now()
        delta = now - boot_time
        return str(delta).split('.')[0]

    def get_battery_info(self) -> Optional[Dict[str, any]]:
        """Return battery status if available."""
        if hasattr(psutil, 'sensors_battery'):
            batt = psutil.sensors_battery()
            if batt:
                return {
                    'percent': batt.percent,
                    'plugged': batt.power_plugged,
                    'secsleft': batt.secsleft
                }
        return None

    def get_user_sessions(self) -> List[Dict[str, any]]:
        """Return info about logged-in users/sessions."""
        return [u._asdict() for u in psutil.users()]

    def get_env_vars(self) -> Dict[str, str]:
        """Return a snapshot of environment variables."""
        return dict(os.environ)

    def get_time_info(self) -> Dict[str, str]:
        """Return current time, timezone, and locale info."""
        import locale
        return {
            'now': datetime.datetime.now().isoformat(),
            'timezone': datetime.datetime.now(datetime.timezone.utc).astimezone().tzname(),
            'locale': locale.getdefaultlocale()[0]
        }

    def get_editing_apps(self) -> List[Dict[str, any]]:
        """Return a list of processes likely to be editing or listening (editors, recorders, terminals, etc)."""
        editing_keywords = [
            'code', 'editor', 'notepad', 'sublime', 'vim', 'emacs', 'nano', 'word', 'excel',
            'powerpoint', 'pages', 'numbers', 'keynote', 'audacity', 'recorder', 'terminal', 'iterm', 'cmd', 'powershell', 'pycharm', 'idea', 'jupyter', 'obs', 'zoom', 'teams', 'slack', 'discord', 'skype', 'screen', 'listen', 'record', 'studio', 'logic', 'garageband', 'photoshop', 'gimp', 'paint', 'draw', 'inkscape', 'illustrator', 'premiere', 'aftereffects', 'finalcut', 'resolve', 'blender', 'maya', 'cad', 'autocad', 'fusion', 'solidworks', 'matlab', 'octave', 'spyder', 'rstudio', 'notion', 'onenote', 'evernote', 'scrivener', 'writer', 'composer', 'audition', 'sound', 'music', 'video', 'vlc', 'media', 'player', 'quicktime', 'preview', 'pdf', 'acrobat', 'foxit', 'sumatra', 'evince', 'okular', 'zathura', 'calibre', 'kindle', 'ebook', 'reader', 'browser', 'chrome', 'firefox', 'safari', 'edge', 'opera', 'brave', 'vivaldi', 'explorer', 'finder', 'explorer.exe', 'finder.app'
        ]
        procs = self.get_processes()
        editing_procs = []
        for p in procs:
            name = (p.get('name') or '').lower()
            if any(k in name for k in editing_keywords):
                editing_procs.append(p)
        return editing_procs 