"""
USB query handling module for UaiBot.
Handles detection and interaction with USB devices.
"""
import logging
from typing import Tuple, Optional

# Import from the device_manager for USB detection
from uaibot.core.device_manager.usb_detector import USBDetector

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
        
        # Keywords for remote system detection
        self.remote_system_keywords = {
            "screen": ["screened", "screen session", "in screen"],
            "remote": ["remote device", "remote os", "remote system", "remote machine"],
            "other": ["other os", "other machine", "other system"],
            "connection": ["over usb", "through usb", "via usb", "usb connection"],
            "device": ["connected system", "device usb", "usb device"]
        }
        
        # Command extraction keywords
        self.command_keywords = {
            "action": ["do", "run", "execute", "type", "send"],
            "target": ["on", "to", "with"],
            "device": ["usb", "serial", "device", "remote", "screen"]
        }
        
        # Query type indicators
        self.query_indicators = {
            "list": ["list", "show", "what", "check", "display"],
            "device": ["usb", "serial", "tty", "dev/cu", "dev/tty"]
        }
    
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
        # Check if query is about USB devices
        is_device_query = any(term in query_lower for term in self.query_indicators["device"]) or \
                         any(any(keyword in query_lower for keyword in keywords) 
                             for keywords in self.remote_system_keywords.values())
        
        if is_device_query:
            # Extract command if one is specified
            command = self._extract_device_command(query_lower)
            if command:
                self.log(f"Sending command '{command}' to active USB/screen session...")
                result = self.shell_handler.send_to_screen_session(command)
                self.log(result)
                return True, result
            
            # Handle device listing based on query
            if any(term in query_lower for term in self.query_indicators["list"]):
                self.log("Checking for connected USB devices...")
                
                # Check if query is about remote system
                is_remote_query = explicitly_screen or \
                                any(any(keyword in query_lower for keyword in keywords) 
                                    for keywords in self.remote_system_keywords.values())
                
                if screen_exists and is_remote_query:
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
        words = query_lower.split()
        
        # Find action word
        action_idx = -1
        for i, word in enumerate(words):
            if word in self.command_keywords["action"]:
                action_idx = i
                break
        
        if action_idx == -1:
            return None
            
        # Find target word
        target_idx = -1
        for i, word in enumerate(words):
            if word in self.command_keywords["target"]:
                target_idx = i
                break
        
        # Extract command based on word order
        if target_idx != -1:
            if target_idx < action_idx:
                # Command is after action word
                command_start = action_idx + 1
                command_end = len(words)
                for i in range(command_start, len(words)):
                    if words[i] in self.command_keywords["device"]:
                        command_end = i
                        break
                command = " ".join(words[command_start:command_end])
            else:
                # Command is before target word
                command_start = 0
                command_end = target_idx
                for i in range(command_start, target_idx):
                    if words[i] in self.command_keywords["action"]:
                        command_start = i + 1
                        break
                command = " ".join(words[command_start:command_end])
        else:
            # No target word, take everything after action word
            command = " ".join(words[action_idx + 1:])
        
        # Clean up command
        command = command.strip()
        if command.startswith('"') or command.startswith("'"):
            command = command[1:]
        if command.endswith('"') or command.endswith("'"):
            command = command[:-1]
            
        return command if command else None
    
    def log(self, message: str) -> None:
        """Print a message if not in quiet mode"""
        if not self.quiet_mode:
            print(message) 