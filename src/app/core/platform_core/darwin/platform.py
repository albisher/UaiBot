import os
import sys
import subprocess
import platform
from typing import Any, Dict, List, Optional
import objc
from Foundation import NSBundle, NSProcessInfo
from AppKit import NSScreen
from CoreAudio import AudioObjectGetPropertyData, kAudioObjectPropertyElementMain
from IOBluetooth import IOBluetoothDevice
from IOKit import IOServiceMatching, IOServiceGetMatchingServices

from ..common.platform_interface import PlatformInterface

class DarwinPlatform(PlatformInterface):
    """macOS platform implementation."""
    
    def __init__(self):
        """Initialize the Darwin platform implementation."""
        self._platform_name = "darwin"
    
    def get_platform_name(self) -> str:
        """Get the name of the current platform."""
        return self._platform_name
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        process_info = NSProcessInfo.processInfo()
        return {
            "os_name": platform.system(),
            "os_version": platform.mac_ver()[0],
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "memory": {
                "physical": process_info.physicalMemory(),
                "available": process_info.physicalMemory() - process_info.physicalMemory() * 0.2  # Estimate
            }
        }
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a system command."""
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
        """Get platform-specific file path."""
        return os.path.normpath(path)
    
    def get_environment_variable(self, name: str) -> Optional[str]:
        """Get environment variable value."""
        return os.environ.get(name)
    
    def set_environment_variable(self, name: str, value: str) -> bool:
        """Set environment variable value."""
        try:
            os.environ[name] = value
            return True
        except Exception:
            return False
    
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get list of running processes."""
        try:
            result = self.execute_command("ps -eo pid,ppid,user,%cpu,%mem,vsz,rss,tt,stat,start,time,command")
            if not result["success"]:
                return []
            
            processes = []
            lines = result["stdout"].strip().split("\n")[1:]  # Skip header
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
        """Get network information."""
        try:
            result = self.execute_command("ifconfig")
            if not result["success"]:
                return {}
            
            # Parse ifconfig output
            interfaces = {}
            current_interface = None
            
            for line in result["stdout"].split("\n"):
                if line and not line.startswith("\t"):
                    current_interface = line.split(":")[0]
                    interfaces[current_interface] = {"name": current_interface}
                elif current_interface and line.strip():
                    if "inet " in line:
                        interfaces[current_interface]["ip"] = line.split("inet ")[1].split(" ")[0]
                    elif "ether" in line:
                        interfaces[current_interface]["mac"] = line.split("ether ")[1].split(" ")[0]
            
            return {"interfaces": interfaces}
        except Exception:
            return {}
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get display information."""
        screens = []
        for screen in NSScreen.screens():
            frame = screen.frame()
            screens.append({
                "width": int(frame.size.width),
                "height": int(frame.size.height),
                "x": int(frame.origin.x),
                "y": int(frame.origin.y),
                "scale_factor": screen.backingScaleFactor()
            })
        return {"screens": screens}
    
    def get_audio_info(self) -> Dict[str, Any]:
        """Get audio device information."""
        # This is a simplified version. A full implementation would use CoreAudio APIs
        try:
            result = self.execute_command("system_profiler SPAudioDataType")
            if not result["success"]:
                return {}
            
            devices = []
            current_device = None
            
            for line in result["stdout"].split("\n"):
                if ":" in line and not line.startswith(" "):
                    if current_device:
                        devices.append(current_device)
                    current_device = {"name": line.split(":")[0].strip()}
                elif current_device and ":" in line:
                    key, value = line.split(":", 1)
                    current_device[key.strip()] = value.strip()
            
            if current_device:
                devices.append(current_device)
            
            return {"devices": devices}
        except Exception:
            return {}
    
    def get_input_devices(self) -> Dict[str, Any]:
        """Get input device information."""
        try:
            result = self.execute_command("system_profiler SPUSBDataType SPBluetoothDataType")
            if not result["success"]:
                return {}
            
            devices = {
                "keyboard": [],
                "mouse": [],
                "trackpad": []
            }
            
            for line in result["stdout"].split("\n"):
                if "Keyboard" in line:
                    devices["keyboard"].append({"name": line.split(":")[0].strip()})
                elif "Mouse" in line:
                    devices["mouse"].append({"name": line.split(":")[0].strip()})
                elif "Trackpad" in line:
                    devices["trackpad"].append({"name": line.split(":")[0].strip()})
            
            return devices
        except Exception:
            return {}
    
    def get_usb_devices(self) -> List[Dict[str, Any]]:
        """Get USB device information."""
        try:
            result = self.execute_command("system_profiler SPUSBDataType")
            if not result["success"]:
                return []
            
            devices = []
            current_device = None
            
            for line in result["stdout"].split("\n"):
                if ":" in line and not line.startswith(" "):
                    if current_device:
                        devices.append(current_device)
                    current_device = {"name": line.split(":")[0].strip()}
                elif current_device and ":" in line:
                    key, value = line.split(":", 1)
                    current_device[key.strip()] = value.strip()
            
            if current_device:
                devices.append(current_device)
            
            return devices
        except Exception:
            return []
    
    def get_bluetooth_devices(self) -> List[Dict[str, Any]]:
        """Get Bluetooth device information."""
        try:
            result = self.execute_command("system_profiler SPBluetoothDataType")
            if not result["success"]:
                return []
            
            devices = []
            current_device = None
            
            for line in result["stdout"].split("\n"):
                if ":" in line and not line.startswith(" "):
                    if current_device:
                        devices.append(current_device)
                    current_device = {"name": line.split(":")[0].strip()}
                elif current_device and ":" in line:
                    key, value = line.split(":", 1)
                    current_device[key.strip()] = value.strip()
            
            if current_device:
                devices.append(current_device)
            
            return devices
        except Exception:
            return [] 