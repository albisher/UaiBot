"""
DEPRECATED: Sensor awareness logic has been moved to platform_core/platform_manager.py.
Use PlatformManager for all sensor awareness logic.
"""

# Deprecated stub for backward compatibility
from platform_core.platform_manager import PlatformManager
from src.app.core.platform_core.platform_utils import get_platform_name, is_mac, is_windows

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SensorData:
    """Represents sensor data with its properties."""
    brightness: Optional[float] = None
    temperature: Optional[float] = None
    battery_level: Optional[float] = None
    is_charging: Optional[bool] = None

class SensorAwarenessManager:
    """Provides awareness of system sensors across different platforms.
    
    This manager handles sensor data for:
    - Screen brightness
    - System temperature
    - Battery status
    
    Attributes:
        sensor_data (SensorData): Current sensor readings
    """
    
    def __init__(self):
        self.sensor_data = SensorData()
        self._refresh_sensors()
    
    def _refresh_sensors(self) -> None:
        """Refresh all sensor readings."""
        self._get_screen_brightness()
        self._get_system_temperature()
        self._get_battery_status()
    
    def _get_screen_brightness(self) -> None:
        """Get screen brightness reading."""
        try:
            if is_mac():
                import subprocess
                try:
                    out = subprocess.check_output(["brightness", "-l"]).decode()
                    for line in out.splitlines():
                        if "brightness" in line:
                            self.sensor_data.brightness = float(line.split()[-1])
                except FileNotFoundError:
                    logger.error("'brightness' CLI tool not found. Install with 'brew install brightness'.")
                    self.sensor_data.brightness = None
                except Exception as e:
                    logger.error(f"Failed to get brightness: {e}")
                    self.sensor_data.brightness = None
            elif is_windows():
                import screen_brightness_control as sbc
                val = sbc.get_brightness(display=0)
                self.sensor_data.brightness = val[0] if val else None
            else:  # Linux
                import screen_brightness_control as sbc
                val = sbc.get_brightness(display=0)
                self.sensor_data.brightness = val[0] if val else None
        except Exception as e:
            logger.error(f"Failed to get screen brightness: {str(e)}")
            self.sensor_data.brightness = None
    
    def _get_system_temperature(self) -> None:
        """Get system temperature reading."""
        try:
            if is_mac():
                try:
                    import subprocess
                    out = subprocess.check_output(["osx-cpu-temp"]).decode()
                    self.sensor_data.temperature = float(out.strip().replace("°C", ""))
                except FileNotFoundError:
                    logger.warning("'osx-cpu-temp' CLI tool not found. Install with 'brew install osx-cpu-temp'. Trying psutil fallback.")
                    try:
                        import psutil
                        temps = psutil.sensors_temperatures()
                        if temps:
                            for name, entries in temps.items():
                                if entries:
                                    self.sensor_data.temperature = entries[0].current
                                    break
                        else:
                            self.sensor_data.temperature = None
                    except Exception as e2:
                        logger.error(f"psutil fallback failed for temperature: {e2}")
                        self.sensor_data.temperature = None
                except Exception as e:
                    logger.error(f"Failed to get temperature: {e}")
                    self.sensor_data.temperature = None
            elif is_windows():
                import wmi
                w = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
                temperature_infos = w.Sensor()
                for sensor in temperature_infos:
                    if sensor.SensorType == "Temperature":
                        self.sensor_data.temperature = float(sensor.Value)
                        break
            else:  # Linux
                import psutil
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            self.sensor_data.temperature = entries[0].current
                            break
        except Exception as e:
            logger.error(f"Failed to get system temperature: {str(e)}")
            self.sensor_data.temperature = None
    
    def _get_battery_status(self) -> None:
        """Get battery status."""
        try:
            if is_mac():
                try:
                    import subprocess
                    out = subprocess.check_output(["pmset", "-g", "batt"]).decode()
                    for line in out.splitlines():
                        if "InternalBattery" in line:
                            self.sensor_data.battery_level = float(line.split("%")[-2].split()[-1])
                            self.sensor_data.is_charging = "charging" in line.lower()
                except Exception as e:
                    logger.warning(f"pmset failed for battery. Trying psutil fallback. Error: {e}")
                    try:
                        import psutil
                        battery = psutil.sensors_battery()
                        if battery:
                            self.sensor_data.battery_level = battery.percent
                            self.sensor_data.is_charging = battery.power_plugged
                        else:
                            self.sensor_data.battery_level = None
                            self.sensor_data.is_charging = None
                    except Exception as e2:
                        logger.error(f"psutil fallback failed for battery: {e2}")
                        self.sensor_data.battery_level = None
                        self.sensor_data.is_charging = None
            elif is_windows():
                import psutil
                battery = psutil.sensors_battery()
                if battery:
                    self.sensor_data.battery_level = battery.percent
                    self.sensor_data.is_charging = battery.power_plugged
            else:  # Linux
                import psutil
                battery = psutil.sensors_battery()
                if battery:
                    self.sensor_data.battery_level = battery.percent
                    self.sensor_data.is_charging = battery.power_plugged
        except Exception as e:
            logger.error(f"Failed to get battery status: {str(e)}")
            self.sensor_data.battery_level = None
            self.sensor_data.is_charging = None
    
    def get_screen_brightness(self) -> Dict[str, Any]:
        """Get current screen brightness.
        Returns:
            Dict[str, Any]: Dictionary containing brightness information, status, and message
        """
        self._get_screen_brightness()
        if self.sensor_data.brightness is not None:
            return {"brightness": self.sensor_data.brightness, "status": "ok", "message": ""}
        else:
            return {"brightness": None, "status": "unavailable", "message": "Screen brightness not available. Ensure 'brightness' tool is installed and supported on your display."}
    
    def get_system_temperature(self) -> Dict[str, Any]:
        """Get current system temperature.
        Returns:
            Dict[str, Any]: Dictionary containing temperature information, status, and message
        """
        self._get_system_temperature()
        if self.sensor_data.temperature is not None:
            return {"temperature": self.sensor_data.temperature, "status": "ok", "message": ""}
        else:
            return {"temperature": None, "status": "unavailable", "message": "System temperature not available. Try installing 'osx-cpu-temp' or ensure sensors are supported."}
    
    def get_battery_status(self) -> Dict[str, Any]:
        """Get current battery status.
        Returns:
            Dict[str, Any]: Dictionary containing battery information, status, and message
        """
        self._get_battery_status()
        if self.sensor_data.battery_level is not None:
            return {
                "battery_level": self.sensor_data.battery_level,
                "is_charging": self.sensor_data.is_charging,
                "status": "ok",
                "message": ""
            }
        else:
            return {
                "battery_level": None,
                "is_charging": None,
                "status": "unavailable",
                "message": "Battery status not available. Try installing 'psutil' or ensure sensors are supported."
            }
    
    def get_all_sensors(self) -> Dict[str, Any]:
        """Get all sensor readings.
        Returns:
            Dict[str, Any]: Dictionary containing all sensor information, status, and message
        """
        self._refresh_sensors()
        return {
            "brightness": self.sensor_data.brightness,
            "temperature": self.sensor_data.temperature,
            "battery_level": self.sensor_data.battery_level,
            "is_charging": self.sensor_data.is_charging,
            "status": "ok" if all([
                self.sensor_data.brightness is not None,
                self.sensor_data.temperature is not None,
                self.sensor_data.battery_level is not None
            ]) else "partial" if any([
                self.sensor_data.brightness is not None,
                self.sensor_data.temperature is not None,
                self.sensor_data.battery_level is not None
            ]) else "unavailable",
            "message": "Some sensor data may be unavailable. See individual fields for details."
        } 