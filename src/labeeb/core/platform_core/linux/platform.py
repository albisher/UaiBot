import os
import platform
import subprocess
from typing import Any, Dict, List, Optional
from ..common.platform_interface import PlatformInterface
from ..common.platform_factory import PlatformFactory
from ..common.system_info import BaseSystemInfoGatherer
from ...device_manager.usb_detector import USBDetector
from ...awareness.bluetooth_awareness import BluetoothAwarenessManager
from .audio_handler import LinuxAudioHandler
from .fs_handler import LinuxFSHandler
from .net_handler import LinuxNetHandler
from .ui_handler import LinuxUIHandler

class LinuxPlatform(PlatformInterface):
    def __init__(self):
        self._platform_name = "Linux"
        self.audio_handler = LinuxAudioHandler()
        self.fs_handler = LinuxFSHandler()
        self.net_handler = LinuxNetHandler()
        self.ui_handler = LinuxUIHandler()
        self.usb_detector = USBDetector(quiet_mode=True)
        self.bt_manager = BluetoothAwarenessManager()
        self.audio_handler.initialize()
        self.fs_handler.initialize()
        self.net_handler.initialize()
        self.ui_handler.initialize()

    def get_platform_name(self) -> str:
        return self._platform_name

    def get_system_info(self) -> Dict[str, Any]:
        # Use platform module for basic info, can be extended
        return {
            "os_name": platform.system(),
            "os_version": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
        }

    def execute_command(self, command: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "return_code": e.returncode
            }

    def get_file_path(self, path: str) -> str:
        return os.path.normpath(path)

    def get_environment_variable(self, name: str) -> Optional[str]:
        return os.environ.get(name)

    def set_environment_variable(self, name: str, value: str) -> bool:
        try:
            os.environ[name] = value
            return True
        except Exception:
            return False

    def get_process_list(self) -> List[Dict[str, Any]]:
        # Use ps command for process list
        try:
            result = self.execute_command("ps -eo pid,ppid,user,%cpu,%mem,vsz,rss,tt,stat,start,time,command")
            if not result["success"]:
                return []
            processes = []
            lines = result["stdout"].strip().split("\n")[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 12:
                    processes.append({
                        "pid": int(parts[0]),
                        "ppid": int(parts[1]),
                        "user": parts[2],
                        "cpu_percent": float(parts[3]),
                        "memory_percent": float(parts[4]),
                        "vsz": int(parts[5]),
                        "rss": int(parts[6]),
                        "tty": parts[7],
                        "stat": parts[8],
                        "start": parts[9],
                        "time": parts[10],
                        "command": " ".join(parts[11:])
                    })
            return processes
        except Exception:
            return []

    def get_network_info(self) -> Dict[str, Any]:
        return self.net_handler.get_status()

    def get_display_info(self) -> Dict[str, Any]:
        return self.ui_handler.get_screen_info()

    def get_audio_info(self) -> Dict[str, Any]:
        return self.audio_handler.get_status()

    def get_input_devices(self) -> Dict[str, Any]:
        # This could be extended to use evdev or xinput for Linux
        return {"keyboard": True, "mouse": True}

    def get_usb_devices(self) -> List[Dict[str, Any]]:
        # Return a list of dicts for USB devices
        info = self.usb_detector.get_usb_devices()
        if isinstance(info, str):
            return [{"info": info}]
        return info

    def get_bluetooth_devices(self) -> List[Dict[str, Any]]:
        bt_info = self.bt_manager.get_bluetooth_devices()
        return bt_info.get("devices", []) 