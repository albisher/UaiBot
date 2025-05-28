import subprocess
from typing import Dict, List, Optional
import sounddevice as sd
import soundfile as sf

from ...common.audio.audio_interface import AudioInterface

class MacOSAudio(AudioInterface):
    """macOS implementation of audio operations."""
    
    def get_audio_devices(self) -> List[Dict[str, str]]:
        """Get list of audio devices."""
        devices = []
        for i, device in enumerate(sd.query_devices()):
            device_info = {
                'id': str(i),
                'name': device['name'],
                'type': 'input' if device['max_input_channels'] > 0 else 'output',
                'channels': str(device['max_input_channels'] if device['max_input_channels'] > 0 else device['max_output_channels']),
                'sample_rate': str(device['default_samplerate'])
            }
            devices.append(device_info)
        return devices
    
    def get_default_device(self, device_type: str) -> Dict[str, str]:
        """Get default audio device of specified type."""
        devices = sd.query_devices()
        if device_type == 'input':
            default_device = sd.query_devices(kind='input')
        else:
            default_device = sd.query_devices(kind='output')
        
        return {
            'id': str(default_device['index']),
            'name': default_device['name'],
            'type': device_type,
            'channels': str(default_device['max_input_channels'] if device_type == 'input' else default_device['max_output_channels']),
            'sample_rate': str(default_device['default_samplerate'])
        }
    
    def set_default_device(self, device_id: str, device_type: str) -> bool:
        """Set default audio device."""
        try:
            # macOS requires AppleScript to change audio devices
            script = f'''
            tell application "System Preferences"
                activate
                set current pane to pane id "com.apple.preference.sound"
            end tell
            tell application "System Events"
                tell process "System Preferences"
                    click tab group 1 of window "Sound"
                    select row {int(device_id) + 1} of table 1 of scroll area 1 of group 1 of tab group 1 of window "Sound"
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', script], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_volume(self, device_id: Optional[str] = None) -> float:
        """Get volume level for a device."""
        try:
            result = subprocess.run(
                ['osascript', '-e', 'output volume of (get volume settings)'],
                capture_output=True,
                text=True,
                check=True
            )
            return float(result.stdout.strip()) / 100.0
        except (subprocess.CalledProcessError, ValueError):
            return 0.0
    
    def set_volume(self, volume: float, device_id: Optional[str] = None) -> bool:
        """Set volume level for a device."""
        try:
            volume_percent = int(volume * 100)
            subprocess.run(
                ['osascript', '-e', f'set volume output volume {volume_percent}'],
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def is_muted(self, device_id: Optional[str] = None) -> bool:
        """Check if device is muted."""
        try:
            result = subprocess.run(
                ['osascript', '-e', 'output muted of (get volume settings)'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().lower() == 'true'
        except subprocess.CalledProcessError:
            return False
    
    def set_mute(self, muted: bool, device_id: Optional[str] = None) -> bool:
        """Set mute state for a device."""
        try:
            subprocess.run(
                ['osascript', '-e', f'set volume output muted {str(muted).lower()}'],
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def play_sound(self, sound_file: str) -> bool:
        """Play a sound file."""
        try:
            data, samplerate = sf.read(sound_file)
            sd.play(data, samplerate)
            sd.wait()
            return True
        except Exception:
            return False
    
    def record_audio(self, duration: float, output_file: str) -> bool:
        """Record audio for specified duration."""
        try:
            samplerate = 44100
            recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2)
            sd.wait()
            sf.write(output_file, recording, samplerate)
            return True
        except Exception:
            return False 