#!/usr/bin/env python3
"""
Keyboard simulation utilities for UaiBot tests.
Provides cross-platform keyboard event simulation for automated testing.
"""

import os
import sys
import time
import random
import platform
from src.typing import List, Dict, Optional, Callable

# Common keyboard layouts for realistic typing simulation
QWERTY_LAYOUT = {
    'a': 'sq', 'b': 'vgn', 'c': 'xvd', 'd': 'sfcx', 'e': 'wrsdf',
    'f': 'dgrvt', 'g': 'fhbvt', 'h': 'gjnbyu', 'i': 'ujklo',
    'j': 'hkmnui', 'k': 'jlmio', 'l': 'kop;,', 'm': 'njk,',
    'n': 'bmhj', 'o': 'iklp', 'p': 'ol;[\'', 'q': 'asw',
    'r': 'etfd', 's': 'adwxz', 't': 'rfgy', 'u': 'yhji',
    'v': 'cfgb', 'w': 'qsea', 'x': 'zsdc', 'y': 'tghu',
    'z': 'asx', ' ': ' ', '.': ',l;', ',': 'm.l'
}

class KeyboardSimulator:
    """Cross-platform keyboard event simulator for testing."""
    
    def __init__(self, typing_speed: Dict = None):
        """
        Initialize the keyboard simulator.
        
        Args:
            typing_speed: Dictionary with typing speed parameters
                - min_delay: Minimum delay between keystrokes (seconds)
                - max_delay: Maximum delay between keystrokes (seconds)
                - mistake_probability: Probability of making a typo (0-1)
        """
        self.system = platform.system()
        
        # Default typing characteristics if not specified
        self.typing_speed = typing_speed or {
            "min_delay": 0.05,  # seconds
            "max_delay": 0.15,  # seconds
            "mistake_probability": 0.02  # 2% chance of typo
        }
        
        # Try to load platform-specific keyboard libraries
        self.backend = self._initialize_backend()
        
    def _initialize_backend(self) -> Dict:
        """Initialize appropriate keyboard control backend based on platform."""
        backend = {"type": None, "module": None}
        
        try:
            # Try pyautogui first (cross-platform)
            import pyautogui
            backend["type"] = "pyautogui"
            backend["module"] = pyautogui
            return backend
        except ImportError:
            pass
            
        # Platform-specific fallbacks
        if self.system == "Windows":
            try:
                # Windows-specific keyboard control
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                backend["type"] = "win32com"
                backend["module"] = shell
                return backend
            except ImportError:
                pass
                
        elif self.system == "Darwin":  # macOS
            # AppleScript fallback for macOS
            backend["type"] = "applescript"
            return backend
            
        else:  # Linux
            try:
                # Try pynput for Linux
                from pynput.keyboard import Controller
                keyboard = Controller()
                backend["type"] = "pynput"
                backend["module"] = keyboard
                return backend
            except ImportError:
                # xdotool fallback for Linux
                if os.system("which xdotool > /dev/null 2>&1") == 0:
                    backend["type"] = "xdotool"
                    return backend
                    
        # Last resort: subprocess for all platforms
        backend["type"] = "subprocess"
        return backend
        
    def type_text(self, text: str, with_mistakes: bool = True) -> str:
        """
        Simulate human typing with realistic timing and occasional mistakes.
        
        Args:
            text: Text to type
            with_mistakes: Whether to simulate typing mistakes
            
        Returns:
            The text that was actually "typed" (may include corrected mistakes)
        """
        if not text:
            return ""
            
        typed_text = ""
        
        # If we don't have a proper backend, just return the original text
        if not self.backend["type"] or self.backend["type"] == "subprocess":
            # Simulate the typing time only
            for char in text:
                time.sleep(random.uniform(
                    self.typing_speed["min_delay"],
                    self.typing_speed["max_delay"]
                ))
            return text
        
        # Simulate character-by-character typing with realistic timing
        for char in text:
            # Possibly make a typing mistake
            if with_mistakes and random.random() < self.typing_speed["mistake_probability"]:
                mistake_char = self._get_nearby_key(char)
                typed_text += mistake_char
                self._type_character(mistake_char)
                
                # Pause briefly before correction
                time.sleep(random.uniform(0.1, 0.3))
                
                # Press backspace to correct the mistake
                self._type_special_key("backspace")
                typed_text = typed_text[:-1]  # Remove the mistake from tracking
            
            # Type the correct character
            typed_text += char
            self._type_character(char)
            
            # Natural pause between keystrokes
            time.sleep(random.uniform(
                self.typing_speed["min_delay"],
                self.typing_speed["max_delay"]
            ))
            
            # Occasionally add a longer pause (human thinking/hesitation)
            if random.random() < 0.05:
                time.sleep(random.uniform(0.3, 0.7))
                
        return typed_text
    
    def _type_character(self, char: str):
        """Type a single character using the appropriate backend."""
        if self.backend["type"] == "pyautogui":
            self.backend["module"].write(char, interval=0)
            
        elif self.backend["type"] == "win32com":
            # For Windows using win32com
            self.backend["module"].SendKeys(char)
            
        elif self.backend["type"] == "pynput":
            # For Linux using pynput
            self.backend["module"].press(char)
            self.backend["module"].release(char)
            
        elif self.backend["type"] == "applescript":
            # For macOS using AppleScript
            os.system(f'osascript -e \'tell application "System Events" to keystroke "{char}"\' > /dev/null 2>&1')
            
        elif self.backend["type"] == "xdotool":
            # For Linux using xdotool
            os.system(f'xdotool type "{char}" > /dev/null 2>&1')
    
    def _type_special_key(self, key_name: str):
        """Type a special key like Enter, Backspace, etc."""
        if self.backend["type"] == "pyautogui":
            self.backend["module"].press(key_name)
            
        elif self.backend["type"] == "win32com":
            # Map key names to win32com format
            key_map = {
                "enter": "{ENTER}",
                "backspace": "{BACKSPACE}",
                "tab": "{TAB}",
                "escape": "{ESC}",
                "space": " "
            }
            self.backend["module"].SendKeys(key_map.get(key_name.lower(), ""))
            
        elif self.backend["type"] == "pynput":
            # Map key names to pynput format
            from pynput.keyboard import Key
            key_map = {
                "enter": Key.enter,
                "backspace": Key.backspace,
                "tab": Key.tab,
                "escape": Key.esc,
                "space": Key.space
            }
            key = key_map.get(key_name.lower())
            if key:
                self.backend["module"].press(key)
                self.backend["module"].release(key)
                
        elif self.backend["type"] == "applescript":
            # Map key names to AppleScript format
            key_map = {
                "enter": "return",
                "backspace": "delete",
                "tab": "tab",
                "escape": "escape",
                "space": "space"
            }
            applescript_key = key_map.get(key_name.lower())
            if applescript_key:
                os.system(f'osascript -e \'tell application "System Events" to key code {applescript_key}\' > /dev/null 2>&1')
                
        elif self.backend["type"] == "xdotool":
            # Map key names to xdotool format
            key_map = {
                "enter": "Return",
                "backspace": "BackSpace",
                "tab": "Tab",
                "escape": "Escape",
                "space": "space"
            }
            xdotool_key = key_map.get(key_name.lower())
            if xdotool_key:
                os.system(f'xdotool key {xdotool_key} > /dev/null 2>&1')
    
    def _get_nearby_key(self, char: str) -> str:
        """Get a key near the intended one on a QWERTY keyboard to simulate realistic typos."""
        if not char.strip():  # Whitespace
            return char
            
        if char.lower() in QWERTY_LAYOUT:
            neighbors = QWERTY_LAYOUT[char.lower()]
            if not neighbors:
                return char
                
            # Choose a random neighboring key
            mistake = random.choice(neighbors)
            
            # Maintain the same case as the original character
            if char.isupper():
                mistake = mistake.upper()
                
            return mistake
        return char


# Example usage when run directly
if __name__ == "__main__":
    print("Keyboard Simulator Test")
    print("----------------------")
    
    simulator = KeyboardSimulator()
    
    print("Simulating typing in 3 seconds...")
    time.sleep(3)
    
    test_text = "Hello, this is a keyboard simulation test!"
    result = simulator.type_text(test_text)
    
    print(f"\nOriginal text: {test_text}")
    print(f"Typed text: {result}")
    print("Test completed!")
