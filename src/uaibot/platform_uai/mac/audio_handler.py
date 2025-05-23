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

# Try to import pyaudio, fall back to simulation if not available
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("PyAudio not available, falling back to simulated audio")

class AudioHandler(BaseAudioHandler):
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.input_device = None
        self.output_device = None
        self.default_recording_seconds = 5
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.recordings_dir = os.path.join(get_project_root(), "audio", "recordings")
        
        # Create recordings directory if it doesn't exist
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
        
        # Set default devices on initialization
        self.set_default_devices()

    def set_default_devices(self):
        """Set default audio input and output devices"""
        devices = self.list_audio_devices()
        
        # Try to find the default input device (microphone)
        for device in devices:
            if device['maxInputChannels'] > 0 and 'microphone' in device['name'].lower():
                self.input_device = device['index']
                break
        
        # If no microphone found, use the first available input device
        if self.input_device is None:
            for device in devices:
                if device['maxInputChannels'] > 0:
                    self.input_device = device['index']
                    break
        
        # Try to find the default output device (speaker)
        for device in devices:
            if device['maxOutputChannels'] > 0 and ('speaker' in device['name'].lower() or 'headphone' in device['name'].lower()):
                self.output_device = device['index']
                break
        
        # If no speaker found, use the first available output device
        if self.output_device is None:
            for device in devices:
                if device['maxOutputChannels'] > 0:
                    self.output_device = device['index']
                    break

    def list_audio_devices(self):
        """List available audio devices using PyAudio"""
        devices = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            devices.append({
                "index": i,
                "name": device_info["name"],
                "maxInputChannels": device_info["maxInputChannels"],
                "maxOutputChannels": device_info["maxOutputChannels"],
                "defaultSampleRate": device_info["defaultSampleRate"],
            })
        return devices
    
    def record_audio(self, seconds=None, filename=None):
        """
        Record audio for a specified number of seconds
        
        Args:
            seconds (float): Duration to record in seconds
            filename (str): Output filename (if None, generates a timestamped filename)
            
        Returns:
            str: Path to the recorded audio file
        """
        if seconds is None:
            seconds = self.default_recording_seconds
            
        if filename is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.recordings_dir, f"recording_{timestamp}.wav")
        elif not os.path.isabs(filename):
            filename = os.path.join(self.recordings_dir, filename)
            
        frames = []
        
        print(f"Recording from device index {self.input_device} for {seconds} seconds...")
        
        stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=self.input_device,
            frames_per_buffer=self.chunk
        )
        
        for i in range(0, int(self.rate / self.chunk * seconds)):
            data = stream.read(self.chunk)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        # Save recording
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print(f"Recording saved to {filename}")
        return filename
        
    def play_audio(self, filename):
        """
        Play an audio file
        
        Args:
            filename (str): Path to the audio file to play
        """
        if not os.path.isabs(filename):
            filename = os.path.join(self.recordings_dir, filename)
            
        if not os.path.exists(filename):
            print(f"Error: File {filename} not found")
            return False
            
        # Open the wave file
        wf = wave.open(filename, 'rb')
        
        # Open a stream
        stream = self.p.open(
            format=self.p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
            output_device_index=self.output_device
        )
        
        # Read data in chunks and play
        data = wf.readframes(self.chunk)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(self.chunk)
            
        # Clean up
        stream.stop_stream()
        stream.close()
        
        return True
    
    def set_input_device(self, device_index):
        """Set the audio input device"""
        devices = self.list_audio_devices()
        valid_indices = [device["index"] for device in devices if device["maxInputChannels"] > 0]
        
        if device_index in valid_indices:
            self.input_device = device_index
            return True
        else:
            print(f"Error: Invalid input device index {device_index}")
            return False
            
    def set_output_device(self, device_index):
        """Set the audio output device"""
        devices = self.list_audio_devices()
        valid_indices = [device["index"] for device in devices if device["maxOutputChannels"] > 0]
        
        if device_index in valid_indices:
            self.output_device = device_index
            return True
        else:
            print(f"Error: Invalid output device index {device_index}")
            return False
            
    def __del__(self):
        """Clean up PyAudio on destruction"""
        if hasattr(self, 'p') and self.p:
            self.p.terminate()
