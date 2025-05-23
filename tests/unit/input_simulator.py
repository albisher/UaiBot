#!/usr/bin/env python3
"""
Input simulation utilities for UaiBot testing.
Provides cross-platform input simulation for keyboard, mouse, and sound.
"""

import os
import sys
import time
import random
import platform
import tempfile
from uaibot.typing import Dict, List, Optional, Tuple, Union, Any, Callable

class InputSimulator:
    """Cross-platform input simulation for testing."""
    
    def __init__(self):
        """Initialize the simulator with available input methods."""
        self.platform = platform.system()
        self.modules = self._initialize_modules()
        
        # Human-like timing and behavior params
        self.typing_params = {
            'min_delay': 0.05,  # seconds between keystrokes
            'max_delay': 0.15,
            'mistake_rate': 0.03,  # 3% chance of typo
            'correction_pause': 0.3,  # pause before backspace
            'thinking_probability': 0.05,  # chance of longer pause
            'thinking_time': (0.5, 1.2)  # range for thinking pause
        }
        
        self.mouse_params = {
            'move_duration': (0.3, 1.0),  # seconds for movement
            'click_delay': (0.1, 0.3),  # delay before clicking
            'jitter': 5,  # pixels of random movement
            'overshoot_probability': 0.1,  # chance to overshoot target
            'double_click_interval': 0.15  # seconds between double clicks
        }
        
        self.keyboard_layout = self._get_keyboard_layout()
    
    def _initialize_modules(self) -> Dict[str, Any]:
        """Initialize platform-specific modules for input simulation."""
        modules = {
            'keyboard': None,
            'mouse': None,
            'sound': None
        }
        
        # Try to import cross-platform modules first
        try:
            import pyautogui
            modules['keyboard'] = pyautogui
            modules['mouse'] = pyautogui
        except ImportError:
            pass
            
        # Platform-specific fallbacks
        if self.platform == 'Windows':
            if not modules['keyboard']:
                try:
                    import win32api
                    import win32con
                    modules['keyboard'] = {'api': win32api, 'con': win32con}
                except ImportError:
                    pass
                    
            try:
                import winsound
                modules['sound'] = winsound
            except ImportError:
                pass
                
        elif self.platform == 'Darwin':  # macOS
            pass  # macOS-specific fallbacks if needed
            
        else:  # Linux
            pass  # Linux-specific fallbacks if needed
            
        # Cross-platform sound options
        if not modules['sound']:
            try:
                import playsound
                modules['sound'] = playsound.playsound
            except ImportError:
                try:
                    import pygame
                    pygame.mixer.init()
                    modules['sound'] = pygame.mixer.Sound
                except ImportError:
                    pass
                    
        return modules
    
    def _get_keyboard_layout(self) -> Dict[str, str]:
        """Return keyboard layout map for realistic typos."""
        # QWERTY layout with adjacent keys for each key
        return {
            'a': 'sqzw', 'b': 'vghn', 'c': 'xdfv', 'd': 'sfxce', 'e': 'wsdr',
            'f': 'dgrc', 'g': 'fhty', 'h': 'gjyu', 'i': 'ujko', 'j': 'hkni',
            'k': 'jloi', 'l': 'kp;o', 'm': 'njk,', 'n': 'bmhj', 'o': 'iklp',
            'p': 'ol[', 'q': 'wa', 'r': 'etfd', 's': 'adwz', 't': 'rfgy',
            'u': 'yijh', 'v': 'cfgb', 'w': 'qeas', 'x': 'zsdc', 'y': 'tghu',
            'z': 'asx', '0': '9-=', '1': '2`', '2': '13', '3': '24', '4': '35',
            '5': '46', '6': '57', '7': '68', '8': '79', '9': '80', ' ': ' ',
            '.': ',/', ',': 'm.', '/': '.;', ';': 'l\'/p', '\'': ';[', '[': ']p\'', 
            ']': '[\\', '\\': ']=', '=': '-0\\', '-': '9=', '`': '1'
        }
    
    def simulate_typing(self, text: str, realistic: bool = True) -> str:
        """
        Simulate realistic human typing with variable speed and occasional mistakes.
        
        Args:
            text: Text to type
            realistic: Whether to use realistic timing and mistakes
            
        Returns:
            The text that was actually "typed" (may include typo/correction sequences)
        """
        if not text:
            return ""
            
        # For testing purposes in command-line, we're just simulating the timing
        # without actually sending keystrokes
        
        result_text = ""
        
        for char in text:
            # Possibly make a typing mistake
            if realistic and random.random() < self.typing_params['mistake_rate']:
                mistake_char = self._get_mistake_for(char)
                result_text += mistake_char  # Add the mistake
                
                # Simulate pause before noticing the mistake
                time.sleep(self.typing_params['correction_pause'])
                
                # Remove the mistake (backspace)
                result_text = result_text[:-1]
                
            # Type the correct character
            result_text += char
            
            if realistic:
                # Normal typing delay
                time.sleep(random.uniform(
                    self.typing_params['min_delay'],
                    self.typing_params['max_delay']
                ))
                
                # Occasional thinking pause
                if random.random() < self.typing_params['thinking_probability']:
                    time.sleep(random.uniform(
                        self.typing_params['thinking_time'][0],
                        self.typing_params['thinking_time'][1]
                    ))
        
        return result_text
    
    def _get_mistake_for(self, char: str) -> str:
        """Get a realistic typing mistake for the given character."""
        # For printable characters, use keyboard layout for adjacent keys
        if char.lower() in self.keyboard_layout:
            adjacent_keys = self.keyboard_layout[char.lower()]
            mistake = random.choice(adjacent_keys) if adjacent_keys else char
            
            # Preserve case
            if char.isupper() and mistake.isalpha():
                mistake = mistake.upper()
                
            return mistake
            
        # For other characters, just return the original
        return char
    
    def simulate_mouse_click(self, x: Optional[int] = None, y: Optional[int] = None, 
                           button: str = 'left', clicks: int = 1) -> bool:
        """
        Simulate human-like mouse clicking.
        
        Args:
            x: X coordinate (or None for current position)
            y: Y coordinate (or None for current position)
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            
        Returns:
            True if successful, False otherwise
        """
        if not self.modules['mouse']:
            return False
            
        try:
            # Move to position if specified
            if x is not None and y is not None:
                self.simulate_mouse_movement(x, y)
            
            # Add pre-click delay (humans hesitate slightly before clicking)
            time.sleep(random.uniform(
                self.mouse_params['click_delay'][0],
                self.mouse_params['click_delay'][1]
            ))
            
            # Perform click(s)
            mouse = self.modules['mouse']
            
            for i in range(clicks):
                if hasattr(mouse, 'click'):
                    # PyAutoGUI style
                    mouse.click(button=button)
                else:
                    # TODO: Platform-specific click implementation
                    pass
                    
                # Delay between multiple clicks
                if i < clicks - 1:
                    time.sleep(self.mouse_params['double_click_interval'])
                    
            return True
            
        except Exception:
            return False
    
    def simulate_mouse_movement(self, x: int, y: int, 
                              duration: Optional[float] = None) -> bool:
        """
        Simulate human-like mouse movement.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            duration: Movement duration override (None for automatic)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.modules['mouse']:
            return False
            
        try:
            mouse = self.modules['mouse']
            
            # Add human-like jitter
            target_x = x + random.randint(-self.mouse_params['jitter'], self.mouse_params['jitter'])
            target_y = y + random.randint(-self.mouse_params['jitter'], self.mouse_params['jitter'])
            
            # Determine movement duration
            if duration is None:
                duration = random.uniform(
                    self.mouse_params['move_duration'][0],
                    self.mouse_params['move_duration'][1]
                )
            
            # Perform movement
            if hasattr(mouse, 'moveTo'):
                # PyAutoGUI style
                mouse.moveTo(target_x, target_y, duration=duration)
            else:
                # TODO: Platform-specific movement implementation
                pass
                
            return True
            
        except Exception:
            return False
    
    def simulate_sound(self, frequency: int = 440, duration: float = 0.5,
                     file_path: Optional[str] = None) -> bool:
        """
        Play a sound or tone.
        
        Args:
            frequency: Tone frequency in Hz
            duration: Sound duration in seconds
            file_path: Optional path to sound file to play
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if file_path and os.path.exists(file_path):
                # Play sound file if available
                if callable(self.modules['sound']):
                    self.modules['sound'](file_path)
                    return True
            elif hasattr(self.modules.get('sound', {}), 'Beep'):
                # Windows winsound.Beep
                self.modules['sound'].Beep(frequency, int(duration * 1000))
                return True
            else:
                # Fallback: console bell
                print("\a", end="", flush=True)
                time.sleep(duration)
                return True
                
            return False
            
        except Exception:
            return False
    
    def create_test_tone_file(self, output_path: Optional[str] = None) -> str:
        """
        Create a simple test tone WAV file.
        
        Args:
            output_path: Path to save the file, or None for temp file
            
        Returns:
            Path to the created file
        """
        if not output_path:
            # Create temporary file
            fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(fd)
            
        try:
            # Try using wave and numpy if available
            import wave
            import numpy as np
            
            # Create a simple sine wave
            sample_rate = 44100
            duration = 0.5
            frequency = 440
            samples = int(duration * sample_rate)
            
            # Generate sine wave
            t = np.linspace(0, duration, samples, False)
            tone = np.sin(2 * np.pi * frequency * t)
            audio = (tone * 32767).astype(np.int16)
            
            # Write to WAV file
            with wave.open(output_path, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 2 bytes (16 bits)
                wf.setframerate(sample_rate)
                wf.writeframes(audio.tobytes())
                
        except ImportError:
            # Fallback: create minimal valid WAV file
            with open(output_path, 'wb') as f:
                # Simple WAV header + basic sine wave approximation
                # RIFF header
                f.write(b'RIFF')
                f.write(int(36).to_bytes(4, 'little'))  # File size - 8
                f.write(b'WAVE')
                
                # Format chunk
                f.write(b'fmt ')
                f.write(int(16).to_bytes(4, 'little'))  # Chunk size
                f.write(int(1).to_bytes(2, 'little'))   # PCM format
                f.write(int(1).to_bytes(2, 'little'))   # Mono
                f.write(int(44100).to_bytes(4, 'little'))  # Sample rate
                f.write(int(44100 * 2).to_bytes(4, 'little'))  # Byte rate
                f.write(int(2).to_bytes(2, 'little'))   # Block align
                f.write(int(16).to_bytes(2, 'little'))  # Bits per sample
                
                # Data chunk
                f.write(b'data')
                data_size = 1000 * 2  # 1000 samples * 2 bytes
                f.write(int(data_size).to_bytes(4, 'little'))
                
                # Generate simple sine wave (approximate)
                for i in range(1000):
                    # Simple alternating values for a rough tone
                    value = 16384 if i % 5 < 2 else -16384
                    f.write(int(value).to_bytes(2, 'little', signed=True))
                    
        return output_path


# Example usage when run directly
if __name__ == "__main__":
    print("Input Simulator Test")
    print("-------------------")
    
    simulator = InputSimulator()
    
    print("\nTesting typing simulation:")
    text = "Hello world! This is a test of typing simulation."
    result = simulator.simulate_typing(text)
    print(f"Original: {text}")
    print(f"Simulated: {result}")
    
    print("\nTesting sound:")
    if simulator.simulate_sound():
        print("Sound played successfully")
    else:
        print("Sound playback not available")
        
    print("\nCreating test tone file...")
    tone_file = simulator.create_test_tone_file()
    print(f"Created test tone at: {tone_file}")
    
    print("\nTest complete.")
