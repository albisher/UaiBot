import logging
import subprocess
from typing import Any, Dict, Optional

from ..base_handler import BaseHandler

class LinuxAudioHandler(BaseHandler):
    """Linux-specific audio handler implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Linux audio handler.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._mixer = None
    
    def initialize(self) -> bool:
        """Initialize the Linux audio handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            import alsaaudio
            self._mixer = alsaaudio.Mixer()
            self._initialized = True
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Linux audio handler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up audio resources."""
        self._mixer = None
        self._initialized = False
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get audio capabilities.
        
        Returns:
            Dict[str, bool]: Dictionary of available audio capabilities
        """
        return {
            'playback': True,
            'recording': self._check_input_available(),
            'volume_control': True,
            'mute_control': True
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current audio status.
        
        Returns:
            Dict[str, Any]: Dictionary containing audio status information
        """
        try:
            if not self._initialized:
                return {'error': 'Handler not initialized'}
                
            return {
                'volume': self.get_volume(),
                'muted': self._mixer.getmute()[0],
                'input_available': self._check_input_available(),
                'output_available': True
            }
        except Exception as e:
            logging.error(f"Error getting audio status: {e}")
            return {'error': str(e)}
    
    def set_volume(self, volume: float) -> bool:
        """Set system volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._initialized:
                return False
                
            volume = max(0, min(100, int(volume * 100)))
            self._mixer.setvolume(volume)
            return True
        except Exception as e:
            logging.error(f"Error setting volume: {e}")
            return False
    
    def get_volume(self) -> Optional[float]:
        """Get current system volume.
        
        Returns:
            Optional[float]: Current volume level (0.0 to 1.0) or None if error
        """
        try:
            if not self._initialized:
                return None
            return self._mixer.getvolume()[0] / 100.0
        except Exception as e:
            logging.error(f"Error getting volume: {e}")
            return None
    
    def _check_input_available(self) -> bool:
        """Check if audio input is available.
        
        Returns:
            bool: True if input is available, False otherwise
        """
        try:
            result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
            return 'card' in result.stdout
        except Exception:
            return False 