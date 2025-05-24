import platform
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AudioDevice:
    """Represents an audio device with its properties."""
    name: str
    type: str
    hostapi: Optional[str]
    is_input: bool
    is_output: bool

class AudioAwarenessManager:
    """Provides awareness of audio input/output devices across different platforms.
    
    This manager handles device enumeration for:
    - macOS: Uses system_profiler
    - Windows: Uses sounddevice
    - Linux: Uses sounddevice
    
    Attributes:
        devices (List[AudioDevice]): List of discovered audio devices
    """
    
    def __init__(self):
        self.devices: List[AudioDevice] = []
        self._refresh_devices()
    
    def _refresh_devices(self) -> None:
        """Refresh the list of audio devices."""
        self.devices = []
        try:
            if platform.system() == "Darwin":
                try:
                    import objc
                    from CoreAudio import AudioHardware
                    # This is a placeholder for a more advanced pyobjc-based implementation
                    # For now, fallback to sounddevice
                    raise ImportError("pyobjc CoreAudio not fully implemented, falling back to sounddevice.")
                except Exception as e:
                    logger.info(f"pyobjc CoreAudio not available or failed: {e}. Falling back to sounddevice.")
                    self._get_sounddevice_devices()
            else:
                self._get_sounddevice_devices()
        except Exception as e:
            logger.error(f"Failed to enumerate audio devices: {e}")
    
    def _get_sounddevice_devices(self) -> None:
        try:
            import sounddevice as sd
            for d in sd.query_devices():
                self.devices.append(AudioDevice(
                    name=d.get('name', ''),
                    type=d.get('hostapi', ''),
                    hostapi=d.get('hostapi', None),
                    is_input=bool(d.get('max_input_channels', 0)),
                    is_output=bool(d.get('max_output_channels', 0)),
                ))
        except Exception as e:
            logger.error(f"sounddevice failed to enumerate devices: {e}")
    
    def get_audio_devices(self) -> Dict[str, Any]:
        """Get a list of all audio devices.
        
        Returns:
            Dict[str, Any]: Dictionary containing device information
        """
        self._refresh_devices()
        if self.devices:
            return {"devices": [d.__dict__ for d in self.devices], "status": "ok", "message": ""}
        else:
            return {"devices": [], "status": "unavailable", "message": "No audio devices found. Ensure permissions are granted and devices are connected."}
    
    def get_input_devices(self) -> Dict[str, Any]:
        """Get a list of input audio devices.
        
        Returns:
            Dict[str, Any]: Dictionary containing input device information
        """
        self._refresh_devices()
        inputs = [d.__dict__ for d in self.devices if d.is_input]
        if inputs:
            return {"devices": inputs, "status": "ok", "message": ""}
        else:
            return {"devices": [], "status": "unavailable", "message": "No input audio devices found."}
    
    def get_output_devices(self) -> Dict[str, Any]:
        """Get a list of output audio devices.
        
        Returns:
            Dict[str, Any]: Dictionary containing output device information
        """
        self._refresh_devices()
        outputs = [d.__dict__ for d in self.devices if d.is_output]
        if outputs:
            return {"devices": outputs, "status": "ok", "message": ""}
        else:
            return {"devices": [], "status": "unavailable", "message": "No output audio devices found."} 