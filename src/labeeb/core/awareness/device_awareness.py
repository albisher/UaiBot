"""
Labeeb Device Awareness

This module provides device awareness functionality for Labeeb.
It monitors and manages device-related information and capabilities.
"""

# Deprecated stub for backward compatibility
from platform_core.platform_manager import PlatformManager

# import platform  # No longer needed
import logging
from typing import Dict, List, Any, Optional
import psutil
import pyautogui
from src.app.core.platform_core.platform_utils import get_platform_name

class DeviceAwarenessTool:
    """
    Tool for detecting and monitoring devices (USB, Audio, Screen) across platforms.
    """
    name = 'device_awareness'
    description = "Detect and monitor devices (USB, Audio, Screen) across platforms"

    def __init__(self):
        self.logger = logging.getLogger("DeviceAwarenessTool")
        self._setup_platform_specific()

    def _setup_platform_specific(self):
        """Setup platform-specific device monitoring."""
        self.system = get_platform_name()
        if self.system == "Darwin":
            self._setup_macos()
        elif self.system == "Windows":
            self._setup_windows()
        else:  # Linux
            self._setup_linux()

    def _setup_macos(self):
        """Setup device monitoring for macOS."""
        try:
            from Foundation import NSWorkspace
            self.ns_workspace = NSWorkspace
        except ImportError:
            self.logger.warning("NSWorkspace not available on macOS")
            self.ns_workspace = None

    def _setup_windows(self):
        """Setup device monitoring for Windows."""
        try:
            import win32com.client
            self.wmi = win32com.client.GetObject("winmgmts:")
        except ImportError:
            self.logger.warning("WMI not available on Windows")
            self.wmi = None

    def _setup_linux(self):
        """Setup device monitoring for Linux."""
        try:
            import subprocess
            self.subprocess = subprocess
        except ImportError:
            self.logger.warning("subprocess not available on Linux")
            self.subprocess = None

    async def execute(self, action: str, **kwargs) -> Any:
        """Execute a device awareness action."""
        if action == "get_usb_devices":
            return await self.get_usb_devices()
        elif action == "get_audio_devices":
            return await self.get_audio_devices()
        elif action == "get_screen_devices":
            return await self.get_screen_devices()
        elif action == "get_all_devices":
            return await self.get_all_devices()
        else:
            return {"error": f"Unknown action: {action}"}

    async def get_usb_devices(self) -> List[Dict[str, Any]]:
        """Get list of connected USB devices."""
        devices = []
        if self.system == "Darwin":
            devices = await self._get_macos_usb_devices()
        elif self.system == "Windows":
            devices = await self._get_windows_usb_devices()
        else:  # Linux
            devices = await self._get_linux_usb_devices()
        return devices

    async def _get_macos_usb_devices(self) -> List[Dict[str, Any]]:
        """Get USB devices on macOS."""
        devices = []
        try:
            if self.ns_workspace:
                mounted_volumes = self.ns_workspace.sharedWorkspace().mountedRemovableMedia()
                for volume in mounted_volumes:
                    devices.append({
                        "name": str(volume),
                        "type": "usb",
                        "platform": "macos"
                    })
        except Exception as e:
            self.logger.error(f"Error getting macOS USB devices: {str(e)}")
        return devices

    async def _get_windows_usb_devices(self) -> List[Dict[str, Any]]:
        """Get USB devices on Windows."""
        devices = []
        try:
            if self.wmi:
                for device in self.wmi.InstancesOf("Win32_USBHub"):
                    devices.append({
                        "name": device.DeviceName,
                        "type": "usb",
                        "platform": "windows"
                    })
        except Exception as e:
            self.logger.error(f"Error getting Windows USB devices: {str(e)}")
        return devices

    async def _get_linux_usb_devices(self) -> List[Dict[str, Any]]:
        """Get USB devices on Linux."""
        devices = []
        try:
            if self.subprocess:
                output = self.subprocess.check_output(["lsusb"]).decode()
                for line in output.splitlines():
                    if line.strip():
                        devices.append({
                            "name": line.strip(),
                            "type": "usb",
                            "platform": "linux"
                        })
        except Exception as e:
            self.logger.error(f"Error getting Linux USB devices: {str(e)}")
        return devices

    async def get_audio_devices(self) -> List[Dict[str, Any]]:
        """Get list of audio input/output devices."""
        devices = []
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                devices.append({
                    "name": device_info.get("name"),
                    "type": "audio",
                    "inputs": device_info.get("maxInputChannels", 0),
                    "outputs": device_info.get("maxOutputChannels", 0),
                    "platform": self.system
                })
            p.terminate()
        except ImportError:
            self.logger.warning("PyAudio not available for audio device detection")
        except Exception as e:
            self.logger.error(f"Error getting audio devices: {str(e)}")
        return devices

    async def get_screen_devices(self) -> List[Dict[str, Any]]:
        """Get list of screen/monitor devices."""
        devices = []
        try:
            # Get primary screen info
            primary = pyautogui.size()
            devices.append({
                "name": "Primary Display",
                "type": "screen",
                "width": primary.width,
                "height": primary.height,
                "platform": self.system
            })
            
            # Try to get additional screens
            if self.system == "Darwin":
                try:
                    import Quartz
                    displays = Quartz.CGGetActiveDisplayList(10, None, None)[1]
                    for i, display in enumerate(displays):
                        if i > 0:  # Skip primary display
                            bounds = Quartz.CGDisplayBounds(display)
                            devices.append({
                                "name": f"Display {i+1}",
                                "type": "screen",
                                "width": int(bounds.size.width),
                                "height": int(bounds.size.height),
                                "platform": "macos"
                            })
                except ImportError:
                    self.logger.warning("Quartz not available for screen detection")
        except Exception as e:
            self.logger.error(f"Error getting screen devices: {str(e)}")
        return devices

    async def get_all_devices(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all detected devices."""
        return {
            "usb": await self.get_usb_devices(),
            "audio": await self.get_audio_devices(),
            "screen": await self.get_screen_devices()
        } 