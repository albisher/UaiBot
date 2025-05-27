import platform
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BluetoothDevice:
    """Represents a Bluetooth device with its properties."""
    name: str
    address: str
    connected: bool
    status: str

class BluetoothAwarenessManager:
    """Provides awareness of Bluetooth devices across different platforms.
    
    This manager handles device enumeration for:
    - macOS: Uses system_profiler
    - Windows: Uses PowerShell
    - Linux: Uses bluetoothctl
    
    Attributes:
        devices (List[BluetoothDevice]): List of discovered Bluetooth devices
    """
    
    def __init__(self):
        self.devices: List[BluetoothDevice] = []
        self._refresh_devices()
    
    def _refresh_devices(self) -> None:
        """Refresh the list of Bluetooth devices."""
        self.devices = []
        try:
            if platform.system() == "Darwin":
                try:
                    import objc
                    from IOBluetooth import IOBluetoothDevice
                    # This is a placeholder for a more advanced pyobjc-based implementation
                    # For now, fallback to generic
                    raise ImportError("pyobjc IOBluetooth not fully implemented, falling back to generic.")
                except Exception as e:
                    logger.info(f"pyobjc IOBluetooth not available or failed: {e}. Falling back to generic.")
                    self._get_generic_devices()
            elif platform.system() == "Windows":
                self._get_windows_devices()
            else:  # Linux
                self._get_linux_devices()
        except Exception as e:
            logger.error(f"Failed to enumerate Bluetooth devices: {e}")
    
    def _get_windows_devices(self) -> None:
        """Get Bluetooth devices on Windows using PowerShell."""
        try:
            import subprocess, json
            cmd = ["powershell", "Get-PnpDevice -Class Bluetooth | ConvertTo-Json"]
            out = subprocess.check_output(cmd)
            for dev in json.loads(out):
                device = BluetoothDevice(
                    name=dev.get("FriendlyName", ""),
                    status=dev.get("Status", ""),
                    connected=dev.get("Status", "") == "OK"
                )
                self.devices.append(device)
        except Exception as e:
            logger.error(f"Failed to get Windows Bluetooth devices: {str(e)}")
    
    def _get_linux_devices(self) -> None:
        """Get Bluetooth devices on Linux using bluetoothctl."""
        try:
            import subprocess
            import shutil
            if not shutil.which("bluetoothctl"):
                logger.warning("bluetoothctl not found; skipping Bluetooth device detection.")
                return
            out = subprocess.check_output(["bluetoothctl", "paired-devices"], timeout=3).decode()
            for line in out.splitlines():
                if line.startswith("Device"):
                    _, addr, name = line.split(maxsplit=2)
                    device = BluetoothDevice(
                        name=name,
                        address=addr,
                        connected=True,
                        status="connected"
                    )
                    self.devices.append(device)
        except subprocess.TimeoutExpired:
            logger.warning("bluetoothctl timed out; skipping Bluetooth device detection.")
        except Exception as e:
            logger.error(f"Failed to get Linux Bluetooth devices: {str(e)}")
    
    def _get_generic_devices(self) -> None:
        # Placeholder for cross-platform Bluetooth device detection
        # On macOS, could use 'system_profiler SPBluetoothDataType' as a fallback
        try:
            import subprocess
            out = subprocess.check_output(["system_profiler", "SPBluetoothDataType"]).decode()
            # Very basic parsing for demonstration
            for line in out.splitlines():
                if "Address" in line:
                    address = line.split(":")[-1].strip()
                    self.devices.append(BluetoothDevice(name="Unknown", address=address, connected=False, status="unknown"))
        except Exception as e:
            logger.error(f"Generic Bluetooth detection failed: {e}")
    
    def get_bluetooth_devices(self) -> Dict[str, Any]:
        """Get a list of all Bluetooth devices.
        
        Returns:
            Dict[str, Any]: Dictionary containing device information and status
        """
        self._refresh_devices()
        if self.devices:
            return {"devices": [d.__dict__ for d in self.devices], "status": "ok", "message": ""}
        else:
            return {"devices": [], "status": "unavailable", "message": "No Bluetooth devices found. Ensure Bluetooth is enabled and devices are paired."}
    
    def get_connected_devices(self) -> Dict[str, Any]:
        """Get a list of connected Bluetooth devices.
        
        Returns:
            Dict[str, Any]: Dictionary containing connected device information and status
        """
        self._refresh_devices()
        connected = [d.__dict__ for d in self.devices if d.connected]
        if connected:
            return {"devices": connected, "status": "ok", "message": ""}
        else:
            return {"devices": [], "status": "unavailable", "message": "No connected Bluetooth devices found."} 