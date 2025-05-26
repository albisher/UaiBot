"""
macOS display handler for Labeeb.

This module provides platform-specific display handling for macOS,
including screen capture, display information, and display control.

Supports RTL languages (Arabic, Hebrew, etc.) with proper text display and capture.
"""
import os
import sys
from typing import Dict, Any, Optional, List, Tuple
from ..common.base_handler import BaseHandler

class MacDisplayHandler(BaseHandler):
    """Handler for macOS display devices."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the macOS display handler."""
        super().__init__(config)
        self._display_enabled = False
        self._displays = []
        self._main_display = None
        self._screen_capture = None
        self._text_direction = 'ltr'  # Default text direction
    
    def initialize(self) -> bool:
        """Initialize the display handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            # Check if display handling is available
            self._check_display_availability()
            
            # Initialize displays
            self._initialize_displays()
            
            # Initialize text direction
            self._initialize_text_direction()
            
            return self._display_enabled
        except Exception as e:
            print(f"Failed to initialize MacDisplayHandler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up display handler resources."""
        self._display_enabled = False
        self._displays = []
        self._main_display = None
        if self._screen_capture:
            self._screen_capture.stop()
            self._screen_capture = None
    
    def is_available(self) -> bool:
        """Check if display handling is available.
        
        Returns:
            bool: True if display handling is available, False otherwise.
        """
        return self._display_enabled
    
    def _check_display_availability(self) -> None:
        """Check if display handling is available on the system."""
        try:
            import Quartz
            # Check if display handling is available
            self._display_enabled = True
        except ImportError:
            print("Failed to import Quartz module")
            self._display_enabled = False
    
    def _initialize_displays(self) -> None:
        """Initialize display devices."""
        try:
            import Quartz
            # Get all displays
            display_list = Quartz.CGDisplayCreateList(None)
            for display_id in display_list:
                display_info = {
                    'id': display_id,
                    'name': Quartz.CGDisplayGetDisplayName(display_id),
                    'bounds': Quartz.CGDisplayGetBounds(display_id),
                    'is_main': display_id == Quartz.CGMainDisplayID()
                }
                self._displays.append(display_info)
                if display_info['is_main']:
                    self._main_display = display_info
        except Exception as e:
            print(f"Failed to initialize displays: {e}")
            self._displays = []
            self._main_display = None
    
    def _initialize_text_direction(self) -> None:
        """Initialize text direction based on system settings."""
        try:
            import Quartz
            # Get system text direction
            if self._rtl_support:
                self._text_direction = 'rtl'
            else:
                self._text_direction = 'ltr'
        except Exception as e:
            print(f"Failed to initialize text direction: {e}")
            self._text_direction = 'ltr'
    
    def get_displays(self) -> List[Dict[str, Any]]:
        """Get list of available displays.
        
        Returns:
            List[Dict[str, Any]]: List of display information.
        """
        return self._displays
    
    def get_main_display(self) -> Optional[Dict[str, Any]]:
        """Get the main display information.
        
        Returns:
            Optional[Dict[str, Any]]: Main display information or None if not available.
        """
        return self._main_display
    
    def get_display_bounds(self, display_id: int) -> Optional[Tuple[int, int, int, int]]:
        """Get the bounds of a specific display.
        
        Args:
            display_id: The ID of the display.
            
        Returns:
            Optional[Tuple[int, int, int, int]]: Display bounds (x, y, width, height) or None if not found.
        """
        try:
            import Quartz
            bounds = Quartz.CGDisplayGetBounds(display_id)
            return (bounds.origin.x, bounds.origin.y, bounds.size.width, bounds.size.height)
        except Exception as e:
            print(f"Failed to get display bounds: {e}")
            return None
    
    def capture_screen(self, display_id: Optional[int] = None) -> Optional[bytes]:
        """Capture the screen of a specific display.
        
        Args:
            display_id: The ID of the display to capture, or None for main display.
            
        Returns:
            Optional[bytes]: The captured screen image data or None if capture failed.
        """
        try:
            import Quartz
            import io
            from PIL import Image
            
            # Use main display if no display_id specified
            if display_id is None:
                display_id = Quartz.CGMainDisplayID()
            
            # Create screen capture
            image = Quartz.CGDisplayCreateImage(display_id)
            if not image:
                return None
            
            # Convert to PNG data
            data = io.BytesIO()
            pil_image = Image.frombytes('RGBA', (image.get_width(), image.get_height()), 
                                      image.get_data(), 'raw', 'BGRA')
            
            # Handle RTL text in image if needed
            if self._rtl_support:
                # TODO: Implement RTL text detection and handling in captured image
                # This would require OCR and text direction analysis
                pass
            
            pil_image.save(data, 'PNG')
            return data.getvalue()
            
        except Exception as e:
            print(f"Failed to capture screen: {e}")
            return None
    
    def start_screen_recording(self, display_id: Optional[int] = None, 
                             output_path: Optional[str] = None) -> bool:
        """Start recording the screen of a specific display.
        
        Args:
            display_id: The ID of the display to record, or None for main display.
            output_path: Path to save the recording, or None for default location.
            
        Returns:
            bool: True if recording started successfully, False otherwise.
        """
        try:
            import Quartz
            import AVFoundation
            
            # Use main display if no display_id specified
            if display_id is None:
                display_id = Quartz.CGMainDisplayID()
            
            # Create screen recording
            self._screen_capture = AVFoundation.AVScreenCapture()
            self._screen_capture.set_display_id(display_id)
            
            # Set RTL support if needed
            if self._rtl_support:
                self._screen_capture.set_text_direction('rtl')
            
            if output_path:
                self._screen_capture.set_output_path(output_path)
            
            return self._screen_capture.start()
            
        except Exception as e:
            print(f"Failed to start screen recording: {e}")
            return False
    
    def stop_screen_recording(self) -> Optional[str]:
        """Stop the current screen recording.
        
        Returns:
            Optional[str]: Path to the recorded file or None if recording failed.
        """
        try:
            if not self._screen_capture:
                return None
            
            output_path = self._screen_capture.get_output_path()
            self._screen_capture.stop()
            self._screen_capture = None
            
            return output_path
            
        except Exception as e:
            print(f"Failed to stop screen recording: {e}")
            return None
    
    def get_display_resolution(self, display_id: Optional[int] = None) -> Optional[Tuple[int, int]]:
        """Get the resolution of a specific display.
        
        Args:
            display_id: The ID of the display, or None for main display.
            
        Returns:
            Optional[Tuple[int, int]]: Display resolution (width, height) or None if not found.
        """
        try:
            import Quartz
            # Use main display if no display_id specified
            if display_id is None:
                display_id = Quartz.CGMainDisplayID()
            
            # Get display mode
            mode = Quartz.CGDisplayCopyDisplayMode(display_id)
            if not mode:
                return None
            
            # Get resolution
            width = Quartz.CGDisplayModeGetWidth(mode)
            height = Quartz.CGDisplayModeGetHeight(mode)
            
            return (width, height)
            
        except Exception as e:
            print(f"Failed to get display resolution: {e}")
            return None
    
    def set_display_resolution(self, display_id: int, width: int, height: int) -> bool:
        """Set the resolution of a specific display.
        
        Args:
            display_id: The ID of the display.
            width: The desired width.
            height: The desired height.
            
        Returns:
            bool: True if resolution was set successfully, False otherwise.
        """
        try:
            import Quartz
            # Get current display mode
            current_mode = Quartz.CGDisplayCopyDisplayMode(display_id)
            if not current_mode:
                return False
            
            # Get available display modes
            modes = Quartz.CGDisplayCopyAllDisplayModes(display_id, None)
            if not modes:
                return False
            
            # Find matching mode
            target_mode = None
            for i in range(Quartz.CFArrayGetCount(modes)):
                mode = Quartz.CFArrayGetValueAtIndex(modes, i)
                if (Quartz.CGDisplayModeGetWidth(mode) == width and 
                    Quartz.CGDisplayModeGetHeight(mode) == height):
                    target_mode = mode
                    break
            
            if not target_mode:
                return False
            
            # Set display mode
            return Quartz.CGDisplaySetDisplayMode(display_id, target_mode, None) == 0
            
        except Exception as e:
            print(f"Failed to set display resolution: {e}")
            return False
    
    def get_text_direction(self) -> str:
        """Get the current text direction.
        
        Returns:
            str: Text direction ('ltr' or 'rtl').
        """
        return self._text_direction
    
    def set_text_direction(self, direction: str) -> bool:
        """Set the text direction.
        
        Args:
            direction: Text direction ('ltr' or 'rtl').
            
        Returns:
            bool: True if direction was set successfully, False otherwise.
        """
        if direction not in ('ltr', 'rtl'):
            return False
        
        self._text_direction = direction
        return True 