import logging
from typing import Any, Dict, Optional
from ..base_handler import BaseHandler

logger = logging.getLogger(__name__)

class MacOSAudioHandler(BaseHandler):
    """macOS-specific audio handler implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the macOS audio handler.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._audio_session = None
    
    def initialize(self) -> bool:
        """Initialize the macOS audio handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Initialize AVFoundation audio session
            from Foundation import NSBundle
            from AVFoundation import AVAudioSession
            
            bundle = NSBundle.bundleWithIdentifier_('com.apple.AVFoundation')
            if bundle is None:
                logging.error("Failed to load AVFoundation bundle")
                return False
                
            self._audio_session = AVAudioSession.sharedInstance()
            self._audio_session.setActive_error_(True, None)
            self._initialized = True
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize macOS audio handler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up audio resources."""
        try:
            if self._audio_session:
                self._audio_session.setActive_error_(False, None)
                self._audio_session = None
            self._initialized = False
        except Exception as e:
            logging.error(f"Error during macOS audio handler cleanup: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get audio capabilities.
        
        Returns:
            Dict[str, bool]: Dictionary of available audio capabilities
        """
        return {
            'playback': True,
            'recording': True,
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
                'muted': self._audio_session.outputVolume() == 0,
                'input_available': self._audio_session.isInputAvailable(),
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
                
            volume = max(0.0, min(1.0, volume))
            self._audio_session.setOutputVolume_(volume)
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
            return self._audio_session.outputVolume()
        except Exception as e:
            logging.error(f"Error getting volume: {e}")
            return None 