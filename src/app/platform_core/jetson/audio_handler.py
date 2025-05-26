"""
Platform-specific audio handling for NVIDIA Jetson
"""

class JetsonAudioHandler:
    def __init__(self):
        self.input_device = None
        self.output_device = None
        self.default_recording_seconds = 5
        
        # Try to initialize PyAudio
        try:
            import pyaudio
            self.p = pyaudio.PyAudio()
            self.format = pyaudio.paInt16
            self.channels = 1
            self.rate = 44100
            self.chunk = 1024
            self._has_pyaudio = True
        except ImportError:
            print("PyAudio not found. Install with: pip install pyaudio")
            print("You may also need to install portaudio: sudo apt-get install portaudio19-dev")
            self._has_pyaudio = False
        
        # Create recordings directory if it doesn't exist
        from labeeb.utils import get_project_root
        import os
        self.recordings_dir = os.path.join(get_project_root(), "audio", "recordings")
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
        
        # Set default devices
        self.set_default_devices()
        
    def list_audio_devices(self):
        """List available audio devices"""
        devices = []
        
        if self._has_pyaudio:
            # Use PyAudio to enumerate devices
            for i in range(self.p.get_device_count()):
                device_info = self.p.get_device_info_by_index(i)
                devices.append(device_info)
        else:
            # Fallback to arecord -l and aplay -l commands for ALSA devices
            try:
                import subprocess
                import re
                
                # Get recording devices
                result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse output to extract device information
                    pattern = r'card (\d+): (\w+) \[(.*?)\], device (\d+): (.*?) \[(.*?)\]'
                    for match in re.finditer(pattern, result.stdout):
                        card, card_id, card_name, dev, dev_name, _ = match.groups()
                        devices.append({
                            'index': int(card),
                            'name': f"{card_name} {dev_name}",
                            'maxInputChannels': 2,  # Assumption
                            'maxOutputChannels': 0
                        })
                
                # Get playback devices
                result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
                if result.returncode == 0:
                    pattern = r'card (\d+): (\w+) \[(.*?)\], device (\d+): (.*?) \[(.*?)\]'
                    for match in re.finditer(pattern, result.stdout):
                        card, card_id, card_name, dev, dev_name, _ = match.groups()
                        # Check if this device is already in the list (as input)
                        found = False
                        for d in devices:
                            if d['index'] == int(card) and d['name'] == f"{card_name} {dev_name}":
                                d['maxOutputChannels'] = 2  # Update existing entry
                                found = True
                                break
                        if not found:
                            devices.append({
                                'index': int(card),
                                'name': f"{card_name} {dev_name}",
                                'maxInputChannels': 0,
                                'maxOutputChannels': 2  # Assumption
                            })
            except Exception as e:
                print(f"Error detecting audio devices: {e}")
        
        return devices
    
    def set_default_devices(self):
        """Set default audio input and output devices"""
        devices = self.list_audio_devices()
        
        if not devices:
            print("No audio devices found.")
            return
        
        # Try to find the default input device (microphone)
        for device in devices:
            if device.get('maxInputChannels', 0) > 0:
                # Prefer built-in or USB microphones
                name = device.get('name', '').lower()
                if 'mic' in name or 'input' in name or 'capture' in name:
                    self.input_device = device.get('index')
                    break
        
        # If no specific microphone found, use the first available input device
        if self.input_device is None:
            for device in devices:
                if device.get('maxInputChannels', 0) > 0:
                    self.input_device = device.get('index')
                    break
        
        # Try to find the default output device
        for device in devices:
            if device.get('maxOutputChannels', 0) > 0:
                # Prefer built-in or HDMI output
                name = device.get('name', '').lower()
                if 'speak' in name or 'output' in name or 'playback' in name or 'hdmi' in name:
                    self.output_device = device.get('index')
                    break
        
        # If no specific output found, use the first available output device
        if self.output_device is None:
            for device in devices:
                if device.get('maxOutputChannels', 0) > 0:
                    self.output_device = device.get('index')
                    break
        
    def record_audio(self, seconds=None, filename=None):
        """
        Record audio for a specified number of seconds
        
        Args:
            seconds (float): Duration to record in seconds
            filename (str): Output filename (if None, generates a timestamped filename)
            
        Returns:
            str: Path to the recorded audio file
        """
        import os
        import datetime
        
        # Use defaults if not specified
        if seconds is None:
            seconds = self.default_recording_seconds
            
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.recordings_dir, f"recording_{timestamp}.wav")
        
        if self._has_pyaudio and self.input_device is not None:
            # Use PyAudio for recording (preferred method)
            import wave
            
            # Open recording stream
            stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.input_device,
                frames_per_buffer=self.chunk
            )
            
            print(f"Recording for {seconds} seconds...")
            frames = []
            
            # Record audio
            for i in range(0, int(self.rate / self.chunk * seconds)):
                data = stream.read(self.chunk)
                frames.append(data)
                
            print("Recording complete.")
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            
            # Save the recorded audio to a WAV file
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            print(f"Audio saved to {filename}")
            return filename
        else:
            # Fallback to arecord command line tool
            try:
                import subprocess
                
                # Create the command for recording
                cmd = [
                    'arecord',
                    '-f', 'S16_LE',  # Format: 16-bit signed little-endian
                    '-c', str(self.channels),  # Number of channels
                    '-r', str(self.rate),  # Sample rate
                    '-d', str(seconds),  # Duration in seconds
                    filename  # Output file
                ]
                
                # Add device selection if available
                if self.input_device is not None:
                    cmd.extend(['-D', f'hw:{self.input_device},0'])
                
                print(f"Recording for {seconds} seconds using arecord...")
                subprocess.run(cmd)
                print(f"Recording complete. Audio saved to {filename}")
                
                return filename
            except Exception as e:
                print(f"Error recording audio: {e}")
                return None
        """
        Record audio for a specified number of seconds
        
        Args:
            seconds (float): Duration to record in seconds
            filename (str): Output filename (if None, generates a timestamped filename)
            
        Returns:
            str: Path to the recorded audio file
        """
        # TO BE IMPLEMENTED - this is a placeholder
        print("Jetson audio recording not yet implemented")
        return None
        
    def play_audio(self, filename):
        """
        Play an audio file
        
        Args:
            filename (str): Path to the audio file to play
        """
        # TO BE IMPLEMENTED - this is a placeholder
        print(f"Jetson audio playback not yet implemented (file: {filename})")
        return False
