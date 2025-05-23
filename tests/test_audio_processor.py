"""Tests for the audio processor module."""

import pytest
from pathlib import Path
from uaibot.core.audio import AudioProcessor, AudioResult

@pytest.fixture
def audio_processor():
    """Create an audio processor instance for testing."""
    return AudioProcessor()

@pytest.fixture
def sample_audio(tmp_path):
    """Create a sample audio file for testing."""
    audio_path = tmp_path / "test_audio.wav"
    # Create a simple WAV file
    import wave
    import struct
    with wave.open(str(audio_path), 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        # Generate a simple sine wave
        for i in range(44100):  # 1 second of audio
            value = int(32767 * 0.5 * (1 + i % 2))  # Square wave
            data = struct.pack('<h', value)
            wav_file.writeframes(data)
    return audio_path

def test_transcribe_audio(audio_processor, sample_audio):
    """Test transcribing an audio file."""
    result = audio_processor.transcribe_audio(str(sample_audio))
    assert isinstance(result, AudioResult)
    assert isinstance(result.text, str)
    assert isinstance(result.segments, list)
    assert all(isinstance(seg, dict) for seg in result.segments)

def test_process_audio_stream(audio_processor, sample_audio):
    """Test processing an audio stream."""
    with open(sample_audio, 'rb') as f:
        audio_data = f.read()
    result = audio_processor.process_audio_stream(audio_data)
    assert isinstance(result, AudioResult)
    assert isinstance(result.text, str)
    assert isinstance(result.segments, list)
    assert all(isinstance(seg, dict) for seg in result.segments)

def test_process_voice_command(audio_processor, sample_audio):
    """Test processing a voice command."""
    result = audio_processor.process_voice_command(str(sample_audio))
    assert isinstance(result, AudioResult)
    assert isinstance(result.text, str)
    assert isinstance(result.segments, list)
    assert all(isinstance(seg, dict) for seg in result.segments)

def test_process_meeting_audio(audio_processor, sample_audio):
    """Test processing meeting audio."""
    result = audio_processor.process_meeting_audio(str(sample_audio))
    assert isinstance(result, AudioResult)
    assert isinstance(result.text, str)
    assert isinstance(result.segments, list)
    assert all(isinstance(seg, dict) for seg in result.segments)

def test_invalid_audio_path(audio_processor):
    """Test processing an invalid audio path."""
    result = audio_processor.transcribe_audio("nonexistent.wav")
    assert isinstance(result, AudioResult)
    assert "Error" in result.text
    assert result.segments == [] 