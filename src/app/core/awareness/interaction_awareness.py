"""
Interaction awareness module for UaiBot.

This module provides cross-platform tools for monitoring and interacting with
the user interface, system resources, and input devices.
"""
import logging
import platform
from typing import Dict, List, Optional, Tuple, Any
import time
from dataclasses import dataclass
from datetime import datetime

try:
    import pyautogui
    import psutil
    from pynput import mouse, keyboard
    from PIL import Image as PILImage
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

@dataclass
class InteractionState:
    """Current state of user interaction."""
    last_mouse_position: Tuple[int, int] = (0, 0)
    last_mouse_click: Optional[datetime] = None
    last_keyboard_activity: Optional[datetime] = None
    active_window: Optional[str] = None
    system_load: float = 0.0
    memory_usage: float = 0.0

class InteractionAwarenessTool:
    name = 'interaction_awareness'
    """Tool for monitoring and interacting with the user interface."""
    
    def __init__(self):
        self.logger = logging.getLogger("InteractionAwarenessTool")
        self.state = InteractionState()
        self._setup_monitoring()
        
    def _setup_monitoring(self):
        """Set up input monitoring."""
        if not PYAUTOGUI_AVAILABLE:
            self.logger.warning("PyAutoGUI not available. Some features will be disabled.")
            return
            
        # Set up mouse listener
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click
        )
        self.mouse_listener.start()
        
        # Set up keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press
        )
        self.keyboard_listener.start()
        
    def _on_mouse_move(self, x: int, y: int):
        """Handle mouse movement."""
        self.state.last_mouse_position = (x, y)
        
    def _on_mouse_click(self, x: int, y: int, button, pressed):
        """Handle mouse clicks."""
        if pressed:
            self.state.last_mouse_click = datetime.now()
            
    def _on_key_press(self, key):
        """Handle keyboard input."""
        self.state.last_keyboard_activity = datetime.now()
        
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        if not PYAUTOGUI_AVAILABLE:
            return (0, 0)
        return pyautogui.position()
        
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        if not PYAUTOGUI_AVAILABLE:
            return (0, 0)
        return pyautogui.size()
        
    def get_active_window(self) -> Optional[str]:
        """Get active window title."""
        if not PYAUTOGUI_AVAILABLE:
            return None
        try:
            return pyautogui.getActiveWindow().title
        except:
            return None
            
    def get_system_info(self) -> Dict[str, Any]:
        """Get system resource usage."""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }
        
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[PILImage.Image]:
        """Take a screenshot of the screen or region."""
        if not PYAUTOGUI_AVAILABLE:
            return None
        try:
            return pyautogui.screenshot(region=region)
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return None
            
    def find_on_screen(self, image_path: str, confidence: float = 0.9) -> Optional[Tuple[int, int]]:
        """Find an image on screen."""
        if not PYAUTOGUI_AVAILABLE:
            return None
        try:
            return pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        except Exception as e:
            self.logger.error(f"Failed to find image: {e}")
            return None
            
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using Whisper."""
        if not WHISPER_AVAILABLE:
            self.logger.warning("Whisper not available for transcription")
            return None
        try:
            model = whisper.load_model("tiny")
            result = model.transcribe(audio_path)
            return result["text"]
        except Exception as e:
            self.logger.error(f"Failed to transcribe audio: {e}")
            return None
            
    def execute(self, action: str, **kwargs) -> Any:
        """Execute an interaction action."""
        actions = {
            "get_mouse_position": self.get_mouse_position,
            "get_screen_size": self.get_screen_size,
            "get_active_window": self.get_active_window,
            "get_system_info": self.get_system_info,
            "take_screenshot": lambda: self.take_screenshot(kwargs.get("region")),
            "find_on_screen": lambda: self.find_on_screen(kwargs.get("image_path"), kwargs.get("confidence", 0.9)),
            "transcribe_audio": lambda: self.transcribe_audio(kwargs.get("audio_path"))
        }
        
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
            
        return actions[action]() 