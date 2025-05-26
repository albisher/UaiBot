import logging
import pyttsx3
import sounddevice as sd
import numpy as np
from typing import Dict, Any, List
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class AudioControlTool:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()
        self._configure_platform()

    def _configure_platform(self) -> None:
        """Configure platform-specific audio settings"""
        try:
            self.engine = pyttsx3.init()
            
            if self.platform_info['name'] == 'mac':
                self.engine.setProperty('voice', 'com.apple.speech.synthesis.voice.karen')
                self.engine.setProperty('rate', 150)
            elif self.platform_info['name'] == 'windows':
                self.engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0')
                self.engine.setProperty('rate', 150)
            elif self.platform_info['name'] == 'ubuntu':
                self.engine.setProperty('voice', 'english-us')
                self.engine.setProperty('rate', 150)
        except Exception as e:
            logger.error(f"Error configuring platform: {str(e)}")

    def speak_text(self, text: str) -> Dict[str, Any]:
        """Speak text using text-to-speech"""
        try:
            result = {
                'platform': self.platform_info['name'],
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
                'platform': self.platform_info['name'],
                'action': 'speak',
                'status': 'error',
                'error': str(e)
            }

    def get_audio_devices(self) -> Dict[str, Any]:
        """Get available audio devices"""
        try:
            devices = sd.query_devices()
            return {
                'platform': self.platform_info['name'],
                'action': 'get_devices',
                'status': 'success',
                'devices': devices
            }
        except Exception as e:
            logger.error(f"Error getting audio devices: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'action': 'get_devices',
                'status': 'error',
                'error': str(e)
            }

    def record_audio(self, duration: float = 5.0) -> Dict[str, Any]:
        """Record audio"""
        try:
            result = {
                'platform': self.platform_info['name'],
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
                'platform': self.platform_info['name'],
                'action': 'record',
                'status': 'error',
                'error': str(e)
            }

    def play_audio(self, audio_data: np.ndarray, sample_rate: int = 44100) -> Dict[str, Any]:
        """Play audio"""
        try:
            result = {
                'platform': self.platform_info['name'],
                'action': 'play',
                'status': 'success'
            }

            sd.play(audio_data, sample_rate)
            sd.wait()
            return result

        except Exception as e:
            logger.error(f"Error playing audio: {str(e)}")
            return {
                'platform': self.platform_info['name'],
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