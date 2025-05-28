"""
Labeeb Speech Tool

This module provides speech-related functionality for Labeeb.
It handles speech recognition, synthesis, and voice interaction capabilities.

- TTS: Uses pyttsx3 (offline, cross-platform) or system TTS as fallback.
- STT: Uses whisper (offline, cross-platform, local model).
"""
import logging
import platform
import subprocess
from typing import Optional
from labeeb.core.platform_core.platform_utils import get_platform_name, is_mac, is_windows, is_linux

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

class SpeechTool:
    name = 'speech'
    description = "Text-to-Speech (TTS) and Speech-to-Text (STT) functionality"
    
    def __init__(self):
        self.logger = logging.getLogger("SpeechTool")
        self.tts_engine = None
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
            except Exception as e:
                self.logger.warning(f"pyttsx3 init failed: {e}")
                self.tts_engine = None

    async def tts(self, text: str, lang: Optional[str] = None) -> bool:
        """Text-to-speech: speak the given text."""
        if self.tts_engine:
            try:
                if lang:
                    for voice in self.tts_engine.getProperty('voices'):
                        if lang in voice.languages or lang in voice.id:
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                return True
            except Exception as e:
                self.logger.error(f"pyttsx3 TTS failed: {e}")
        # Fallback to system TTS
        system = get_platform_name()
        try:
            if system == "Darwin":
                subprocess.run(["say", text], check=True)
                return True
            elif system == "Linux":
                subprocess.run(["espeak", text], check=True)
                return True
            elif system == "Windows":
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Speak(text)
                return True
        except Exception as e:
            self.logger.error(f"System TTS failed: {e}")
        return False

    async def stt(self, audio_path: str, model: str = "tiny") -> Optional[str]:
        """Speech-to-text: transcribe audio file using Whisper."""
        if not WHISPER_AVAILABLE:
            self.logger.warning("Whisper not available for STT")
            return None
        try:
            model = whisper.load_model(model)
            result = model.transcribe(audio_path)
            return result["text"]
        except Exception as e:
            self.logger.error(f"Whisper STT failed: {e}")
            return None

    async def execute(self, action: str, **kwargs):
        if action == "tts":
            return await self.tts(kwargs.get("text", ""), kwargs.get("lang"))
        elif action == "stt":
            return await self.stt(kwargs.get("audio_path", ""), kwargs.get("model", "tiny"))
        else:
            raise ValueError(f"Unknown action: {action}") 