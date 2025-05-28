from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class AudioInterface(ABC):
    """Interface for audio-related operations."""
    
    @abstractmethod
    def get_audio_devices(self) -> List[Dict[str, str]]:
        """Get list of audio devices."""
        pass
    
    @abstractmethod
    def get_default_device(self, device_type: str) -> Dict[str, str]:
        """Get default audio device of specified type."""
        pass
    
    @abstractmethod
    def set_default_device(self, device_id: str, device_type: str) -> bool:
        """Set default audio device."""
        pass
    
    @abstractmethod
    def get_volume(self, device_id: Optional[str] = None) -> float:
        """Get volume level for a device."""
        pass
    
    @abstractmethod
    def set_volume(self, volume: float, device_id: Optional[str] = None) -> bool:
        """Set volume level for a device."""
        pass
    
    @abstractmethod
    def is_muted(self, device_id: Optional[str] = None) -> bool:
        """Check if device is muted."""
        pass
    
    @abstractmethod
    def set_mute(self, muted: bool, device_id: Optional[str] = None) -> bool:
        """Set mute state for a device."""
        pass
    
    @abstractmethod
    def play_sound(self, sound_file: str) -> bool:
        """Play a sound file."""
        pass
    
    @abstractmethod
    def record_audio(self, duration: float, output_file: str) -> bool:
        """Record audio for specified duration."""
        pass 