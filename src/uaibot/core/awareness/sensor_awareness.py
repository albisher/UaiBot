import platform
from typing import Dict, Any

class SensorAwarenessManager:
    """Provides awareness of system sensors (e.g., screen brightness)."""
    def get_screen_brightness(self) -> Dict[str, Any]:
        try:
            if platform.system() == "Darwin":
                import subprocess
                out = subprocess.check_output(["brightness", "-l"]).decode()
                for line in out.splitlines():
                    if "brightness" in line:
                        val = float(line.split()[-1])
                        return {"brightness": val}
            elif platform.system() == "Windows":
                import screen_brightness_control as sbc
                val = sbc.get_brightness(display=0)
                return {"brightness": val[0] if val else None}
            else:  # Linux
                import screen_brightness_control as sbc
                val = sbc.get_brightness(display=0)
                return {"brightness": val[0] if val else None}
        except Exception:
            pass
        return {"brightness": None} 