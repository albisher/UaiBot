"""
Platform-specific audio handling for macOS
Implements the BaseAudioHandler interface.
"""
import subprocess
import json
import wave
import os
from uaibot.utils import get_project_root
from uaibot.platform_uai.common.audio_handler import BaseAudioHandler, SimulatedAudioHandler
import tempfile
import pyaudio
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Try to import pyaudio, fall back to simulation if not available
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("PyAudio not available, falling back to simulated audio")

class MacAudioHandler(BaseAudioHandler):
    """macOS-specific audio handler implementation."""
    
    def __init__(self):
        """Initialize the macOS audio handler."""
        self.pyaudio = None
        self.recording_stream = None
        self.recording_frames = []
        self.recording_file = None
        super().__init__()
    
    def _platform_specific_init(self) -> None:
        """Initialize PyAudio for macOS."""
        try:
            self.pyaudio = pyaudio.PyAudio()
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio: {e}")
            raise
    
    def list_audio_devices(self) -> List[Dict[str, Any]]:
        """List available audio devices on macOS.
        
        Returns:
            List of dictionaries containing device information.
        """
        if not self.is_initialized:
            return []
        
        devices = []
        for i in range(self.pyaudio.get_device_count()):
            try:
                device_info = self.pyaudio.get_device_info_by_index(i)
                devices.append({
                    'id': i,
                    'name': device_info['name'],
                    'input_channels': device_info['maxInputChannels'],
                    'output_channels': device_info['maxOutputChannels'],
                    'default_samplerate': device_info['defaultSampleRate']
                })
            except Exception as e:
                logger.error(f"Error getting device info for device {i}: {e}")
        
        return devices
    
    def get_default_input_device(self) -> Optional[Dict[str, Any]]:
        """Get the default input device on macOS.
        
        Returns:
            Dictionary containing device information or None if not available.
        """
        if not self.is_initialized:
            return None
        
        try:
            device_info = self.pyaudio.get_default_input_device_info()
            return {
                'id': device_info['index'],
                'name': device_info['name'],
                'input_channels': device_info['maxInputChannels'],
                'output_channels': device_info['maxOutputChannels'],
                'default_samplerate': device_info['defaultSampleRate']
            }
        except Exception as e:
            logger.error(f"Error getting default input device: {e}")
            return None
    
    def get_default_output_device(self) -> Optional[Dict[str, Any]]:
        """Get the default output device on macOS.
        
        Returns:
            Dictionary containing device information or None if not available.
        """
        if not self.is_initialized:
            return None
        
        try:
            device_info = self.pyaudio.get_default_output_device_info()
            return {
                'id': device_info['index'],
                'name': device_info['name'],
                'input_channels': device_info['maxInputChannels'],
                'output_channels': device_info['maxOutputChannels'],
                'default_samplerate': device_info['defaultSampleRate']
            }
        except Exception as e:
            logger.error(f"Error getting default output device: {e}")
            return None
    
    def start_recording(self, device_id: Optional[str] = None) -> bool:
        """Start recording audio on macOS.
        
        Args:
            device_id: ID of the device to use for recording.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.is_initialized:
            return False
        
        try:
            # Create a temporary file for recording
            self.recording_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            
            # Initialize recording parameters
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            
            # Open recording stream
            self.recording_stream = self.pyaudio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=int(device_id) if device_id else None,
                frames_per_buffer=CHUNK
            )
            
            self.recording_frames = []
            return True
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            return False
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording audio on macOS.
        
        Returns:
            Path to the recorded audio file or None if recording failed.
        """
        if not self.recording_stream:
            return None
        
        try:
            # Stop and close the recording stream
            self.recording_stream.stop_stream()
            self.recording_stream.close()
            self.recording_stream = None
            
            # Save the recorded audio to the temporary file
            CHANNELS = 1
            RATE = 44100
            FORMAT = pyaudio.paInt16
            
            wf = wave.open(self.recording_file.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.pyaudio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self.recording_frames))
            wf.close()
            
            # Get the file path and reset recording state
            file_path = self.recording_file.name
            self.recording_file = None
            self.recording_frames = []
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            return None
    
    def play_audio(self, file_path: str, device_id: Optional[str] = None) -> bool:
        """Play an audio file on macOS.
        
        Args:
            file_path: Path to the audio file.
            device_id: ID of the device to use for playback.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.is_initialized:
            return False
        
        try:
            # Open the audio file
            wf = wave.open(file_path, 'rb')
            
            # Open playback stream
            stream = self.pyaudio.open(
                format=self.pyaudio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                output_device_index=int(device_id) if device_id else None
            )
            
            # Read data in chunks and play
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
            
            # Clean up
            stream.stop_stream()
            stream.close()
            wf.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
    
    def get_audio_levels(self) -> Dict[str, float]:
        """Get current audio levels on macOS.
        
        Returns:
            Dictionary containing input and output levels.
        """
        if not self.is_initialized:
            return {"input": 0.0, "output": 0.0}
        
        try:
            # Get input level from recording stream if active
            input_level = 0.0
            if self.recording_stream:
                data = self.recording_stream.read(1024, exception_on_overflow=False)
                input_level = max(abs(int.from_bytes(data[i:i+2], byteorder='little', signed=True)) 
                                for i in range(0, len(data), 2)) / 32768.0
            
            # Output level is not directly accessible, return 0.0
            return {
                "input": input_level,
                "output": 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting audio levels: {e}")
            return {"input": 0.0, "output": 0.0}
    
    def _platform_specific_cleanup(self) -> None:
        """Clean up PyAudio resources."""
        if self.recording_stream:
            self.recording_stream.stop_stream()
            self.recording_stream.close()
            self.recording_stream = None
        
        if self.recording_file:
            try:
                os.unlink(self.recording_file.name)
            except Exception as e:
                logger.error(f"Error removing temporary recording file: {e}")
            self.recording_file = None
        
        if self.pyaudio:
            self.pyaudio.terminate()
            self.pyaudio = None

    def __del__(self):
        """Clean up PyAudio on destruction"""
        if hasattr(self, 'p') and self.p:
            self.p.terminate()
