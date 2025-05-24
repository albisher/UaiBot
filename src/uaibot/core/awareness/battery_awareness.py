import psutil
from typing import Optional, Dict

class BatteryAwarenessManager:
    """Provides awareness of battery state."""
    def get_battery_info(self) -> Optional[Dict[str, any]]:
        if hasattr(psutil, 'sensors_battery'):
            batt = psutil.sensors_battery()
            if batt:
                return {
                    'percent': batt.percent,
                    'plugged': batt.power_plugged,
                    'secsleft': batt.secsleft
                }
        return None 