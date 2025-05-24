import platform
from typing import List, Dict

class AudioAwarenessManager:
    """Provides awareness of audio input/output devices."""
    def get_audio_devices(self) -> List[Dict[str, str]]:
        devices = []
        try:
            if platform.system() == "Darwin":
                import subprocess, json
                out = subprocess.check_output(["system_profiler", "SPAudioDataType", "-json"])
                data = json.loads(out)
                for dev in data.get("SPAudioDataType", []):
                    devices.append({"name": dev.get("_name", ""), "type": dev.get("coreaudio_device_transport", "")})
            elif platform.system() == "Windows":
                import sounddevice as sd
                for dev in sd.query_devices():
                    devices.append({"name": dev["name"], "hostapi": str(dev["hostapi"])})
            else:  # Linux
                import sounddevice as sd
                for dev in sd.query_devices():
                    devices.append({"name": dev["name"], "hostapi": str(dev["hostapi"])})
        except Exception:
            pass
        return devices 