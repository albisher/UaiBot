"""
USB query handling module for UaiBot.
Handles detection and interaction with USB devices.
"""
import re
import logging
from typing import Tuple, Optional

# Import from the device_manager for USB detection
from device_manager.usb_detector import USBDetector

# Set up logging
logger = logging.getLogger(__name__)

class USBQueryHandler:
    def __init__(self, shell_handler, quiet_mode: bool = False):
        """
        Initialize the USBQueryHandler.
        
        Args:
            shell_handler: Shell handler instance for executing commands
            quiet_mode (bool): If True, reduces terminal output
        """
        self.shell_handler = shell_handler
        self.quiet_mode = quiet_mode
        self.usb_detector = USBDetector(quiet_mode=quiet_mode)
        
        # Patterns for remote system indicators
        self.remote_system_indicators = [
            "screened os", "remote device", "remote os", "remote system", 
            "remote machine", "other os", "other machine", "over usb connection", 
            "over my usb", "over the usb", "through screen", "in screen session",
            "other system", "screened system", "connected system", "device usb"
        ]
        
        # Patterns for extracting commands from device queries
        self.device_command_patterns = [
            r'(?:on|to|with)\s+(?:the\s+)?(?:usb|serial|device|remote|screen).*?(?:do|run|execute|type|send)\s+[\'"]?([\w\s\-\.\/\*]+)[\'"]',
            r'(?:do|run|execute|type|send)\s+[\'"]?([\w\s\-\.\/\*]+)[\'"].*?(?:on|to|with)\s+(?:the\s+)?(?:usb|serial|device|remote|screen)',
        ]
    
    def handle_usb_device_query(self, query_lower: str, screen_exists: bool, explicitly_screen: bool) -> Tuple[bool, str]:
        """
        Handle queries about USB devices.
        
        Args:
            query_lower (str): Lowercased query string
            screen_exists (bool): Whether a screen session exists
            explicitly_screen (bool): Whether screen is explicitly mentioned
            
        Returns:
            tuple: (bool, str) - (True, result) if handled, (False, "") otherwise
        """
        if any(term in query_lower for term in ['usb', 'serial', 'tty', 'dev/cu', 'dev/tty']) or \
           any(indicator in query_lower for indicator in self.remote_system_indicators):
            
            # Extract command if one is specified
            command_match = self._extract_device_command(query_lower)
            if command_match:
                self.log(f"Sending command '{command_match}' to active USB/screen session...")
                result = self.shell_handler.send_to_screen_session(command_match)
                self.log(result)
                return True, result
            
            # Handle device listing based on query
            if "list" in query_lower or "show" in query_lower or "what" in query_lower or "check" in query_lower:
                self.log("Checking for connected USB devices...")
                
                if screen_exists and (explicitly_screen or any(indicator in query_lower for indicator in self.remote_system_indicators)):
                    # Send commands to screen session for remote device detection
                    device_cmd = self.usb_detector.get_remote_device_command()
                    self.log(f"Checking for USB devices on remote system via screen session...")
                    result = self.shell_handler.send_to_screen_session(device_cmd)
                    self.log(result)
                    return True, result
                else:
                    # Use the local detection method
                    result = self.usb_detector.get_usb_devices()
                    self.log(result)
                    return True, result
        
        return False, ""
    
    def _extract_device_command(self, query_lower: str) -> Optional[str]:
        """
        Extract a command from a device query if one is specified.
        
        Args:
            query_lower (str): Lowercased query string
            
        Returns:
            Optional[str]: Extracted command if found, None otherwise
        """
        for pattern in self.device_command_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return match.group(1).strip()
        return None
    
    def log(self, message: str) -> None:
        """Print a message if not in quiet mode"""
        if not self.quiet_mode:
            print(message) 