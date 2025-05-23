#!/usr/bin/env python3
"""
Sound simulation utilities for UaiBot tests.
Provides cross-platform audio testing tools for simulating and testing audio I/O.
"""

import os
import sys
import time
import random
import platform
from src.typing import Dict, Optional, Tuple, List

class SoundSimulator:
    """Cross-platform sound testing utilities."""
    
    def __init__(self):
        """Initialize the sound simulator with appropriate backend."""
        self.system = platform.system()
        self.backend = self._initialize_backend()
        
    def _initialize_backend(self) -> Dict:
        """Initialize appropriate audio backend based on platform."""
        backend = {"type": None, "module": None}
        
        # Try different audio libraries in order of preference
        try:
            # Try playsound first (simple cross-platform library)
            import playsound
            backend["type"] = "playsound"
            backend["module"] = playsound.playsound
            return backend
        except ImportError:
            pass
            
        try:
            # Try pygame next (good cross-platform support)
            import pygame
            pygame.mixer.init()
            backend["type"] = "pygame"
            backend["module"] = pygame.mixer
            return backend
        except ImportError:
            pass
            
        try:
            # Try pydub with simpleaudio
            from src.pydub import AudioSegment
            from pydub.playback import play
            backend["type"] = "pydub"
            backend["module"] = {"AudioSegment": AudioSegment, "play": play}
            return backend
        except ImportError:
            pass
            
        # Platform-specific fallbacks
        if self.system == "Windows":
            try:
                # Windows-specific with winsound
                import winsound
                backend["type"] = "winsound"
                backend["module"] = winsound
                return backend
            except ImportError:
                pass
                
        elif self.system == "Darwin":  # macOS
            # AppleScript/afplay fallback for macOS
            if os.system("which afplay > /dev/null 2>&1") == 0:
                backend["type"] = "afplay"
                return backend
                
        else:  # Linux
            # Check for command line players
            for cmd in ["aplay", "paplay", "ffplay"]:
                if os.system(f"which {cmd} > /dev/null 2>&1") == 0:
                    backend["type"] = cmd
                    return backend
        
        # Last resort: system beep
        backend["type"] = "beep"
        return backend
    
    def play_sound(self, sound_file: Optional[str] = None, 
                  frequency: int = 440, duration: float = 1.0) -> bool:
        """
        Play a sound file or generate a tone.
        
        Args:
            sound_file: Path to sound file, or None to generate tone
            frequency: Frequency in Hz for generated tone
            duration: Duration in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # If sound file is provided and exists
            if sound_file and os.path.exists(sound_file):
                return self._play_sound_file(sound_file)
            else:
                # Generate a simple tone
                return self._generate_tone(frequency, duration)
                
        except Exception as e:
            print(f"Sound playback error: {e}")
            return False
    
    def _play_sound_file(self, sound_file: str) -> bool:
        """Play a sound file using the available backend."""
        try:
            if self.backend["type"] == "playsound":
                self.backend["module"](sound_file)
                return True
                
            elif self.backend["type"] == "pygame":
                sound = self.backend["module"].Sound(sound_file)
                sound.play()
                # Wait for playback to finish
                while pygame.mixer.get_busy():
                    time.sleep(0.1)
                return True
                
            elif self.backend["type"] == "pydub":
                sound = self.backend["module"]["AudioSegment"].from_file(sound_file)
                self.backend["module"]["play"](sound)
                return True
                
            elif self.backend["type"] == "winsound":
                self.backend["module"].PlaySound(sound_file, self.backend["module"].SND_FILENAME)
                return True
                
            elif self.backend["type"] == "afplay":
                os.system(f'afplay "{sound_file}"')
                return True
                
            elif self.backend["type"] in ["aplay", "paplay", "ffplay"]:
                os.system(f'{self.backend["type"]} "{sound_file}"')
                return True
                
            return False
            
        except Exception as e:
            print(f"Error playing sound file: {e}")
            return False
    
    def _generate_tone(self, frequency: int, duration: float) -> bool:
        """Generate a simple tone of the specified frequency and duration."""
        try:
            if self.backend["type"] == "pygame":
                # Generate a simple sine wave
                import numpy as np
                sample_rate = 44100
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                tone = np.sin(frequency * t * 2 * np.pi)
                tone = np.asarray([32767 * tone, 32767 * tone]).T.astype(np.int16)
                
                import pygame.sndarray
                sound = pygame.sndarray.make_sound(tone)
                sound.play()
                
                # Wait for playback to finish
                while pygame.mixer.get_busy():
                    time.sleep(0.1)
                    
                return True
                
            elif self.backend["type"] == "winsound":
                self.backend["module"].Beep(frequency, int(duration * 1000))
                return True
                
            elif self.backend["type"] == "beep":
                # Try simple console beep
                print("\a")  # ASCII bell character
                sys.stdout.flush()
                time.sleep(duration)
                return True
                
            # For other backends, return false as they can't generate tones easily
            return False
            
        except Exception as e:
            print(f"Error generating tone: {e}")
            return False
    
    def record_audio(self, duration: float = 3.0, 
                    sample_rate: int = 44100,
                    output_file: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Record audio from the microphone.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Sample rate in Hz
            output_file: Path to save recording, or None for temp file
            
        Returns:
            Tuple of (success, file_path)
        """
        # Try to use pyaudio for recording if available
        try:
            import pyaudio
            import wave
            import tempfile
            
            if output_file is None:
                # Create a temporary file if no output file specified
                temp_fd, output_file = tempfile.mkstemp(suffix=".wav")
                os.close(temp_fd)
            
            # Recording parameters
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            CHUNK = 1024
            
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Start recording
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                               rate=sample_rate, input=True,
                               frames_per_buffer=CHUNK)
            
            print(f"Recording for {duration} seconds...")
            frames = []
            
            # Record in chunks for the specified duration
            for i in range(0, int(sample_rate / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Save the recording
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(frames))
            
            return True, output_file
            
        except ImportError:
            print("PyAudio not available for recording")
            return False, None
        except Exception as e:
            print(f"Error recording audio: {e}")
            return False, None


# Example usage when run directly
if __name__ == "__main__":
    print("Sound Simulator Test")
    print("------------------")
    
    simulator = SoundSimulator()
    
    print("Testing tone generation...")
    success = simulator.play_sound(frequency=440, duration=0.5)
    print("Tone played successfully!" if success else "Tone playback failed")
    
    time.sleep(0.5)
    
    print("Testing tone with different frequency...")
    success = simulator.play_sound(frequency=880, duration=0.5)
    print("Second tone played successfully!" if success else "Second tone playback failed")
    
    # Try recording if possible
    print("\nTrying audio recording (3 seconds)...")
    success, file_path = simulator.record_audio(duration=3.0)
    
    if success and file_path:
        print(f"Recording saved to: {file_path}")
        print("Playing back recording...")
        simulator.play_sound(file_path)
    else:
        print("Recording not available or failed")
    
    print("Test completed!")
