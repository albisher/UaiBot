"""
macOS audio handler for Labeeb.

This module provides platform-specific audio handling for macOS,
including audio input/output and system audio control.
"""
import os
import sys
from typing import Dict, Any, Optional, List
from ..common.base_handler import BaseHandler
from ..platform_manager import platform_manager

class MacAudioHandler(BaseHandler):
    """Handler for macOS audio devices."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the macOS audio handler."""
        super().__init__(config)
        self._audio_enabled = False
        self._input_device = None
        self._output_device = None
        self._volume = 0.0
    
    def initialize(self) -> bool:
        """Initialize the audio handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            # Check if audio is available
            self._check_audio_availability()
            
            # Initialize audio devices
            self._initialize_input_device()
            self._initialize_output_device()
            
            return self._audio_enabled
        except Exception as e:
            print(f"Failed to initialize MacAudioHandler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up audio handler resources."""
        self._audio_enabled = False
        self._input_device = None
        self._output_device = None
        self._volume = 0.0
    
    def is_available(self) -> bool:
        """Check if audio handling is available.
        
        Returns:
            bool: True if audio handling is available, False otherwise.
        """
        return self._audio_enabled
    
    def _check_audio_availability(self) -> None:
        """Check if audio is available on the system."""
        try:
            import CoreAudio
            # Check if audio is available
            self._audio_enabled = True
        except ImportError:
            print("Failed to import CoreAudio module")
            self._audio_enabled = False
    
    def _initialize_input_device(self) -> None:
        """Initialize audio input device."""
        try:
            import CoreAudio
            # Get default input device
            self._input_device = CoreAudio.AudioDeviceID()
            self._input_device.set_default_input()
        except Exception as e:
            print(f"Failed to initialize input device: {e}")
            self._input_device = None
    
    def _initialize_output_device(self) -> None:
        """Initialize audio output device."""
        try:
            import CoreAudio
            # Get default output device
            self._output_device = CoreAudio.AudioDeviceID()
            self._output_device.set_default_output()
        except Exception as e:
            print(f"Failed to initialize output device: {e}")
            self._output_device = None
    
    def get_input_devices(self) -> List[Dict[str, Any]]:
        """Get list of available input devices.
        
        Returns:
            List[Dict[str, Any]]: List of input device information.
        """
        try:
            import CoreAudio
            devices = []
            for device in CoreAudio.AudioDeviceID.get_input_devices():
                devices.append({
                    'id': device.id,
                    'name': device.name,
                    'manufacturer': device.manufacturer,
                    'sample_rate': device.sample_rate,
                    'channels': device.channels
                })
            return devices
        except Exception as e:
            print(f"Failed to get input devices: {e}")
            return []
    
    def get_output_devices(self) -> List[Dict[str, Any]]:
        """Get list of available output devices.
        
        Returns:
            List[Dict[str, Any]]: List of output device information.
        """
        try:
            import CoreAudio
            devices = []
            for device in CoreAudio.AudioDeviceID.get_output_devices():
                devices.append({
                    'id': device.id,
                    'name': device.name,
                    'manufacturer': device.manufacturer,
                    'sample_rate': device.sample_rate,
                    'channels': device.channels
                })
            return devices
        except Exception as e:
            print(f"Failed to get output devices: {e}")
            return []
    
    def set_input_device(self, device_id: int) -> bool:
        """Set the input device.
        
        Args:
            device_id: The ID of the input device to use.
            
        Returns:
            bool: True if the device was set successfully, False otherwise.
        """
        try:
            import CoreAudio
            device = CoreAudio.AudioDeviceID(device_id)
            device.set_default_input()
            self._input_device = device
            return True
        except Exception as e:
            print(f"Failed to set input device: {e}")
            return False
    
    def set_output_device(self, device_id: int) -> bool:
        """Set the output device.
        
        Args:
            device_id: The ID of the output device to use.
            
        Returns:
            bool: True if the device was set successfully, False otherwise.
        """
        try:
            import CoreAudio
            device = CoreAudio.AudioDeviceID(device_id)
            device.set_default_output()
            self._output_device = device
            return True
        except Exception as e:
            print(f"Failed to set output device: {e}")
            return False
    
    def get_volume(self) -> float:
        """Get the current system volume.
        
        Returns:
            float: The current volume (0.0 to 1.0).
        """
        try:
            import CoreAudio
            if self._output_device:
                return self._output_device.get_volume()
            return 0.0
        except Exception as e:
            print(f"Failed to get volume: {e}")
            return 0.0
    
    def set_volume(self, volume: float) -> bool:
        """Set the system volume.
        
        Args:
            volume: The volume to set (0.0 to 1.0).
            
        Returns:
            bool: True if the volume was set successfully, False otherwise.
        """
        try:
            import CoreAudio
            if self._output_device:
                self._output_device.set_volume(volume)
                self._volume = volume
                return True
            return False
        except Exception as e:
            print(f"Failed to set volume: {e}")
            return False
    
    def is_muted(self) -> bool:
        """Check if the system is muted.
        
        Returns:
            bool: True if the system is muted, False otherwise.
        """
        try:
            import CoreAudio
            if self._output_device:
                return self._output_device.is_muted()
            return False
        except Exception as e:
            print(f"Failed to check mute status: {e}")
            return False
    
    def set_muted(self, muted: bool) -> bool:
        """Set the system mute state.
        
        Args:
            muted: True to mute, False to unmute.
            
        Returns:
            bool: True if the mute state was set successfully, False otherwise.
        """
        try:
            import CoreAudio
            if self._output_device:
                self._output_device.set_muted(muted)
                return True
            return False
        except Exception as e:
            print(f"Failed to set mute state: {e}")
            return False
