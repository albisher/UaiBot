"""
Screen session management module for UaiBot.
Handles detection and interaction with screen sessions.
"""
import subprocess
import logging
from typing import List

# Set up logging
logger = logging.getLogger(__name__)

class ScreenSessionManager:
    def __init__(self, quiet_mode: bool = False):
        """
        Initialize the ScreenSessionManager.
        
        Args:
            quiet_mode (bool): If True, reduces terminal output
        """
        self.quiet_mode = quiet_mode
        self.screen_session_indicators: List[str] = [
            "screen session", "serial port", "usb terminal", "in screen", "on screen", 
            "to screen", "through screen", "via screen", "in the screen", "on the screen",
            "in terminal session", "in the terminal session", "over serial", "screened os",
            "remote device", "remote os", "remote system", "remote machine", "other os",
            "other machine", "over usb connection", "over my usb", "over the usb",
            "through screen", "in screen session", "other system", "screened system",
            "connected system", "device usb"
        ]
    
    def check_screen_exists(self) -> bool:
        """
        Check if any screen sessions exist.
        
        Returns:
            bool: True if screen sessions exist, False otherwise
        """
        try:
            result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
            screen_output = result.stdout + result.stderr
            return "No Sockets found" not in screen_output
        except Exception as e:
            logger.error(f"Error checking screen sessions: {str(e)}")
            return False
    
    def is_explicitly_screen(self, query_lower: str) -> bool:
        """
        Determine if the query explicitly mentions a screen session.
        
        Args:
            query_lower (str): Lowercased query string
            
        Returns:
            bool: True if screen session is explicitly mentioned
        """
        return any(indicator in query_lower for indicator in self.screen_session_indicators)
    
    def log(self, message: str) -> None:
        """Print a message if not in quiet mode"""
        if not self.quiet_mode:
            print(message) 