import logging
import pyttsx3
import sounddevice as sd
import numpy as np
from typing import Dict, Any, List, Optional
from app.agent_tools.base_tool import BaseAgentTool
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class AudioControlTool(BaseAgentTool):
    """Tool for controlling audio devices and settings with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the audio control tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._platform_manager = None
        self._platform_info = None
        self._handlers = None
        self._audio_handler = None
        self._default_device = config.get('default_device')
        self._volume_step = config.get('volume_step', 5)
        self._max_volume = config.get('max_volume', 100)
    
    def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self._platform_manager = PlatformManager()
            self._platform_info = self._platform_manager.get_platform_info()
            self._handlers = self._platform_manager.get_handlers()
            self._audio_handler = self._handlers.get('audio')
            if not self._audio_handler:
                logger.error("Audio handler not found")
                return False
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AudioControlTool: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._platform_manager = None
            self._platform_info = None
            self._handlers = None
            self._audio_handler = None
            self._initialized = False
        except Exception as e:
            logger.error(f"Error cleaning up AudioControlTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        return {
            'volume_control': True,
            'mute_control': True,
            'device_selection': True,
            'device_info': True,
            'platform_specific_optimization': bool(self._platform_info)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        return {
            'initialized': self._initialized,
            'platform': self._platform_info.get('name') if self._platform_info else None,
            'default_device': self._default_device,
            'volume_step': self._volume_step,
            'max_volume': self._max_volume
        }
    
    def execute(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a command using this tool.
        
        Args:
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        if not self._initialized:
            return {'error': 'Tool not initialized'}
        
        try:
            if command == 'get_devices':
                return self._get_devices()
            elif command == 'set_volume':
                return self._set_volume(args)
            elif command == 'get_volume':
                return self._get_volume(args)
            elif command == 'set_mute':
                return self._set_mute(args)
            elif command == 'is_muted':
                return self._is_muted(args)
            elif command == 'get_device_info':
                return self._get_device_info(args)
            else:
                return {'error': f'Unknown command: {command}'}
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return {'error': str(e)}
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands for this tool.
        
        Returns:
            List[str]: List of available command names
        """
        return [
            'get_devices',
            'set_volume',
            'get_volume',
            'set_mute',
            'is_muted',
            'get_device_info'
        ]
    
    def get_command_help(self, command: str) -> Dict[str, Any]:
        """Get help information for a specific command.
        
        Args:
            command: Command name to get help for
            
        Returns:
            Dict[str, Any]: Help information for the command
        """
        help_info = {
            'get_devices': {
                'description': 'Get list of available audio devices',
                'args': {}
            },
            'set_volume': {
                'description': 'Set volume for a specific device',
                'args': {
                    'device_id': 'Optional device ID',
                    'volume': 'Volume level (0-100)'
                }
            },
            'get_volume': {
                'description': 'Get current volume for a device',
                'args': {
                    'device_id': 'Optional device ID'
                }
            },
            'set_mute': {
                'description': 'Set mute state for a device',
                'args': {
                    'device_id': 'Optional device ID',
                    'mute': 'True to mute, False to unmute'
                }
            },
            'is_muted': {
                'description': 'Check if a device is muted',
                'args': {
                    'device_id': 'Optional device ID'
                }
            },
            'get_device_info': {
                'description': 'Get detailed information about a device',
                'args': {
                    'device_id': 'Device ID'
                }
            }
        }
        return help_info.get(command, {'error': f'Unknown command: {command}'})
    
    def validate_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> bool:
        """Validate if a command and its arguments are valid.
        
        Args:
            command: Command to validate
            args: Optional arguments to validate
            
        Returns:
            bool: True if command and arguments are valid, False otherwise
        """
        if command not in self.get_available_commands():
            return False
        
        if command == 'set_volume':
            if not args or 'volume' not in args:
                return False
            volume = args['volume']
            if not isinstance(volume, (int, float)) or volume < 0 or volume > self._max_volume:
                return False
        
        elif command == 'set_mute':
            if not args or 'mute' not in args:
                return False
            if not isinstance(args['mute'], bool):
                return False
        
        elif command == 'get_device_info':
            if not args or 'device_id' not in args:
                return False
        
        return True
    
    def _get_devices(self) -> Dict[str, Any]:
        """Get list of available audio devices.
        
        Returns:
            Dict[str, Any]: List of audio devices
        """
        try:
            devices = self._audio_handler.get_devices()
            return {
                'status': 'success',
                'devices': devices
            }
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            return {'error': str(e)}
    
    def _set_volume(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Set volume for a specific device.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            device_id = args.get('device_id', self._default_device)
            volume = args['volume']
            
            self._audio_handler.set_volume(device_id, volume)
            return {
                'status': 'success',
                'device_id': device_id,
                'volume': volume
            }
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return {'error': str(e)}
    
    def _get_volume(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current volume for a device.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Current volume information
        """
        try:
            device_id = args.get('device_id', self._default_device)
            volume = self._audio_handler.get_volume(device_id)
            return {
                'status': 'success',
                'device_id': device_id,
                'volume': volume
            }
        except Exception as e:
            logger.error(f"Error getting volume: {e}")
            return {'error': str(e)}
    
    def _set_mute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Set mute state for a device.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            device_id = args.get('device_id', self._default_device)
            mute = args['mute']
            
            self._audio_handler.set_mute(device_id, mute)
            return {
                'status': 'success',
                'device_id': device_id,
                'muted': mute
            }
        except Exception as e:
            logger.error(f"Error setting mute state: {e}")
            return {'error': str(e)}
    
    def _is_muted(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a device is muted.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Mute state information
        """
        try:
            device_id = args.get('device_id', self._default_device)
            muted = self._audio_handler.is_muted(device_id)
            return {
                'status': 'success',
                'device_id': device_id,
                'muted': muted
            }
        except Exception as e:
            logger.error(f"Error checking mute state: {e}")
            return {'error': str(e)}
    
    def _get_device_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a device.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Device information
        """
        try:
            device_id = args['device_id']
            info = self._audio_handler.get_device_info(device_id)
            return {
                'status': 'success',
                'device_id': device_id,
                'info': info
            }
        except Exception as e:
            logger.error(f"Error getting device info: {e}")
            return {'error': str(e)}

    def _configure_platform(self) -> None:
        """Configure platform-specific audio settings"""
        try:
            self.engine = pyttsx3.init()
            
            if self._platform_info['name'] == 'mac':
                self.engine.setProperty('voice', 'com.apple.speech.synthesis.voice.karen')
                self.engine.setProperty('rate', 150)
            elif self._platform_info['name'] == 'windows':
                self.engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0')
                self.engine.setProperty('rate', 150)
            elif self._platform_info['name'] == 'ubuntu':
                self.engine.setProperty('voice', 'english-us')
                self.engine.setProperty('rate', 150)
        except Exception as e:
            logger.error(f"Error configuring platform: {str(e)}")

    def speak_text(self, text: str) -> Dict[str, Any]:
        """Speak text using text-to-speech"""
        try:
            result = {
                'platform': self._platform_info['name'],
                'action': 'speak',
                'status': 'success',
                'text': text
            }

            self.engine.say(text)
            self.engine.runAndWait()
            return result

        except Exception as e:
            logger.error(f"Error speaking text: {str(e)}")
            return {
                'platform': self._platform_info['name'],
                'action': 'speak',
                'status': 'error',
                'error': str(e)
            }

    def get_audio_devices(self) -> Dict[str, Any]:
        """Get available audio devices"""
        try:
            devices = sd.query_devices()
            return {
                'platform': self._platform_info['name'],
                'action': 'get_devices',
                'status': 'success',
                'devices': devices
            }
        except Exception as e:
            logger.error(f"Error getting audio devices: {str(e)}")
            return {
                'platform': self._platform_info['name'],
                'action': 'get_devices',
                'status': 'error',
                'error': str(e)
            }

    def record_audio(self, duration: float = 5.0) -> Dict[str, Any]:
        """Record audio"""
        try:
            result = {
                'platform': self._platform_info['name'],
                'action': 'record',
                'status': 'success',
                'audio': None
            }

            # Record audio
            sample_rate = 44100
            recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2)
            sd.wait()
            result['audio'] = recording
            return result

        except Exception as e:
            logger.error(f"Error recording audio: {str(e)}")
            return {
                'platform': self._platform_info['name'],
                'action': 'record',
                'status': 'error',
                'error': str(e)
            }

    def play_audio(self, audio_data: np.ndarray, sample_rate: int = 44100) -> Dict[str, Any]:
        """Play audio"""
        try:
            result = {
                'platform': self._platform_info['name'],
                'action': 'play',
                'status': 'success'
            }

            sd.play(audio_data, sample_rate)
            sd.wait()
            return result

        except Exception as e:
            logger.error(f"Error playing audio: {str(e)}")
            return {
                'platform': self._platform_info['name'],
                'action': 'play',
                'status': 'error',
                'error': str(e)
            }

    def check_audio_availability(self) -> bool:
        """Check if audio control is available"""
        try:
            # Test audio control
            devices = sd.query_devices()
            return len(devices) > 0
        except Exception as e:
            logger.error(f"Error checking audio availability: {str(e)}")
            return False 