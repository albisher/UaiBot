import platform
from typing import List, Dict

class BluetoothAwarenessManager:
    """Provides awareness of Bluetooth devices."""
    def get_bluetooth_devices(self) -> List[Dict[str, str]]:
        devices = []
        try:
            if platform.system() == "Darwin":
                import subprocess, plistlib
                out = subprocess.check_output(["system_profiler", "SPBluetoothDataType", "-xml"])
                plist = plistlib.loads(out)
                bt_data = plist[0]["_items"][0].get("device_title", {})
                for name, info in bt_data.items():
                    devices.append({"name": name, "connected": str(info.get("device_connected", ""))})
            elif platform.system() == "Windows":
                # Windows: Use pywin32 or subprocess with PowerShell
                import subprocess, json
                cmd = ["powershell", "Get-PnpDevice -Class Bluetooth | ConvertTo-Json"]
                out = subprocess.check_output(cmd)
                for dev in json.loads(out):
                    devices.append({"name": dev.get("FriendlyName", ""), "status": dev.get("Status", "")})
            else:  # Linux
                import subprocess
                out = subprocess.check_output(["bluetoothctl", "paired-devices"]).decode()
                for line in out.splitlines():
                    if line.startswith("Device"):
                        _, addr, name = line.split(maxsplit=2)
                        devices.append({"address": addr, "name": name})
        except Exception:
            pass
        return devices 