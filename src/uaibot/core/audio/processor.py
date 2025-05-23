"""
Audio processor module for UaiBot.

This module provides audio processing capabilities using Whisper Tiny.
"""
import whisper
import ffmpeg
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from ..logging_manager import get_logger

logger = get_logger(__name__)

@dataclass
class AudioResult:
    """Data class for audio processing results."""
    text: str
    segments: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

class AudioProcessor:
    """Audio processing using Whisper Tiny."""
    
    def __init__(self):
        """Initialize the audio processor."""
        try:
            self.model = whisper.load_model("tiny")
            logger.info("Audio processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize audio processor: {str(e)}")
            raise

    def transcribe_audio(self, audio_path: str) -> AudioResult:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            AudioResult containing the transcription and segments
        """
        try:
            result = self.model.transcribe(audio_path)
            return AudioResult(
                text=result["text"],
                segments=result["segments"],
                metadata={"model": "Whisper-Tiny"}
            )
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise

    def process_audio_stream(self, stream_data: bytes) -> AudioResult:
        """
        Process audio stream data.
        
        Args:
            stream_data: Raw audio data bytes
            
        Returns:
            AudioResult containing the transcription
        """
        temp_path = Path("temp_audio.wav")
        try:
            # Save stream to temporary file
            with open(temp_path, "wb") as f:
                f.write(stream_data)
            
            # Process the audio
            result = self.transcribe_audio(str(temp_path))
            return result
        except Exception as e:
            logger.error(f"Error processing audio stream: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()

    def process_voice_command(self, audio_path: str) -> AudioResult:
        """
        Process a voice command.
        
        Args:
            audio_path: Path to the voice command audio file
            
        Returns:
            AudioResult containing the command transcription
        """
        return self.transcribe_audio(audio_path)

    def process_meeting_audio(self, audio_path: str) -> AudioResult:
        """
        Process meeting/lecture audio.
        
        Args:
            audio_path: Path to the meeting audio file
            
        Returns:
            AudioResult containing the meeting transcription
        """
        return self.transcribe_audio(audio_path) 