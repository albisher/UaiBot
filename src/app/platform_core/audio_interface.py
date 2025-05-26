import logging
import sys
from typing import Any, Dict, Optional

from .base_handler import BaseHandler

class AudioInterface:
    """Platform-agnostic audio interface."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the audio interface.
        
        Args:
            config: Optional configuration dictionary
        """
        self._config = config or {}
        self._handler = self._initialize_handler()
    
    def _initialize_handler(self) -> Optional[BaseHandler]:
        """Initialize the appropriate platform-specific handler.
        
        Returns:
            Optional[BaseHandler]: Initialized handler or None if initialization fails
        """
        try:
            if sys.platform == 'darwin':
                from .macos.audio_handler import MacOSAudioHandler
                handler = MacOSAudioHandler(self._config)
            elif sys.platform == 'win32':
                from .windows.audio_handler import WindowsAudioHandler
                handler = WindowsAudioHandler(self._config)
            elif sys.platform.startswith('linux'):
                from .linux.audio_handler import LinuxAudioHandler
                handler = LinuxAudioHandler(self._config)
            else:
                logging.error(f"Unsupported platform: {sys.platform}")
                return None
            
            if not handler.initialize():
                logging.error("Failed to initialize audio handler")
                return None
                
            return handler
            
        except Exception as e:
            logging.error(f"Error initializing audio handler: {e}")
            return None
    
    def get_volume(self) -> Optional[float]:
        """Get current system volume.
        
        Returns:
            Optional[float]: Current volume level (0.0 to 1.0) or None if error
        """
        if not self._handler:
            return None
        return self._handler.get_volume()
    
    def set_volume(self, volume: float) -> bool:
        """Set system volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._handler:
            return False
        return self._handler.set_volume(volume)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current audio status.
        
        Returns:
            Dict[str, Any]: Dictionary containing audio status information
        """
        if not self._handler:
            return {'error': 'No audio handler available'}
        return self._handler.get_status()
    
    def cleanup(self) -> None:
        """Clean up audio resources."""
        if self._handler:
            self._handler.cleanup()
            self._handler = None 