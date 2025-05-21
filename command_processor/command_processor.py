"""
Command processing module for UaiBot.
Handles determining whether commands should be executed locally or sent to a screen session.
"""
import re
import subprocess
import platform
import json
import os
import logging
from typing import Dict, Any, Tuple, Optional

# Import from the core
from core.ai_handler import get_system_info
from core.file_search import FileSearch
from core.shell_handler import ShellHandler
from core.query_processor import QueryProcessor
from core.system_info_gatherer import SystemInfoGatherer

# Import from the device_manager for USB detection
from device_manager.usb_detector import USBDetector

# Import our new modules for improved command processing
from command_processor.ai_command_extractor import AICommandExtractor
from command_processor.logger import CommandLogger

# Import our new handler modules
from command_processor.screen_session_manager import ScreenSessionManager
from command_processor.usb_query_handler import USBQueryHandler
from command_processor.folder_search_handler import FolderSearchHandler
from command_processor.direct_execution_handler import DirectExecutionHandler

# Set up logging
logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self, ai_handler, shell_handler, quiet_mode=False, fast_mode=False, output_facade=None, debug=False):
        """
        Initialize the CommandProcessor.
        
        Args:
            ai_handler: AI handler instance for processing commands
            shell_handler: Shell handler instance for executing commands
            quiet_mode (bool): If True, reduces terminal output
            fast_mode (bool): If True, handles errors quickly and exits
            output_facade: Reference to the output facade for UI handling
            debug (bool): If True, enables debug mode
        """
        self.ai_handler = ai_handler
        self.shell_handler = shell_handler
        self.quiet_mode = quiet_mode
        self.fast_mode = fast_mode
        self.system_platform = platform.system().lower()
        self.usb_detector = USBDetector(quiet_mode=quiet_mode)
        
        # Get output facade if provided or import as needed
        if output_facade:
            self.output = output_facade
        else:
            try:
                from utils.output_facade import output
                self.output = output
            except ImportError:
                self.output = None
        
        # Initialize our specialized handlers
        self.screen_manager = ScreenSessionManager(quiet_mode=quiet_mode)
        self.usb_handler = USBQueryHandler(shell_handler, quiet_mode=quiet_mode)
        self.folder_handler = FolderSearchHandler(quiet_mode=quiet_mode)
        self.direct_handler = DirectExecutionHandler(shell_handler, quiet_mode=quiet_mode)
        
        # Initialize the AI command extractor and logger
        self.command_extractor = AICommandExtractor()
        self.command_logger = CommandLogger()
        
        # Common terminal commands
        self.common_commands = [
            # File & directory operations
            'ls', 'pwd', 'cd', 'mkdir', 'rmdir', 'cp', 'mv', 'rm', 'touch', 'cat', 'find',
            # Text viewing/editing
            'more', 'less', 'head', 'tail', 'nano', 'vi', 'vim', 'grep', 'awk', 'sed',
            # System info
            'top', 'ps', 'kill', 'killall', 'df', 'du', 'free', 'uptime', 'date', 'cal', 'who', 'whoami',
            # Networking
            'ping', 'curl', 'wget', 'ssh', 'scp', 'ifconfig', 'netstat', 'traceroute', 'nslookup',
            # macOS specific
            'open', 'pbcopy', 'pbpaste', 'say', 'ditto', 'mdfind', 'diskutil',
            # Miscellaneous
            'echo', 'history', 'man', 'clear', 'alias', 'crontab'
        ]
        
        # Patterns for screen session and remote system indicators
        self.screen_session_indicators = [
            "screen session", "serial port", "usb terminal", "in screen", "on screen", 
            "to screen", "through screen", "via screen", "in the screen", "on the screen",
            "in terminal session", "in the terminal session", "over serial", "screened os",
            "remote device", "remote os", "remote system", "remote machine", "other os",
            "other machine", "over usb connection", "over my usb", "over the usb",
            "through screen", "in screen session", "other system", "screened system",
            "connected system", "device usb"
        ]
        
        self.file_search = FileSearch(quiet_mode=quiet_mode)
        self.query_processor = QueryProcessor(self.ai_handler, getattr(self.ai_handler, 'config', {}))
        self.system_info = SystemInfoGatherer()
        
        self.debug = debug
    
    def log(self, message):
        """Print a message if not in quiet mode"""
        if not self.quiet_mode:
            if self.output:
                self.output.info(message)
            else:
                print(message)
    
    def check_screen_exists(self):
        """
        Check if any screen sessions exist.
        
        Returns:
            bool: True if screen sessions exist, False otherwise
        """
        try:
            result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
            screen_output = result.stdout + result.stderr
            return "No Sockets found" not in screen_output
        except Exception:
            return False
    
    def is_explicitly_screen(self, query_lower):
        """
        Determine if the query explicitly mentions a screen session.
        
        Args:
            query_lower (str): Lowercased query string
            
        Returns:
            bool: True if screen session is explicitly mentioned
        """
        return any(indicator in query_lower for indicator in self.screen_session_indicators)
    
    def handle_usb_device_query(self, query_lower, screen_exists, explicitly_screen):
        """
        Handle queries about USB devices.
        
        Args:
            query_lower (str): Lowercased query string
            screen_exists (bool): Whether a screen session exists
            explicitly_screen (bool): Whether screen is explicitly mentioned
            
        Returns:
            tuple: (bool, str) - (True, result) if handled, (False, "") otherwise
        """
        remote_system_indicators = [
            "screened os", "remote device", "remote os", "remote system", 
            "remote machine", "other os", "other machine", "over usb connection", 
            "over my usb", "over the usb", "through screen", "in screen session",
            "other system", "screened system", "connected system", "device usb"
        ]
        
        if any(term in query_lower for term in ['usb', 'serial', 'tty', 'dev/cu', 'dev/tty']) or \
           any(indicator in query_lower for indicator in remote_system_indicators):
            
            # Extract command if one is specified
            command = self._extract_device_command(query_lower)
            if command:
                self.log(f"Sending command '{command}' to active USB/screen session...")
                result = self.shell_handler.send_to_screen_session(command)
                self.log(result)
                return True, result
            
            # Handle device listing based on query
            if "list" in query_lower or "show" in query_lower or "what" in query_lower or "check" in query_lower:
                self.log("Checking for connected USB devices...")
                
                if screen_exists and (explicitly_screen or any(indicator in query_lower for indicator in remote_system_indicators)):
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
    
    def _extract_device_command(self, query: str) -> Optional[str]:
        """
        Extract a command from a device-related query using string operations.
        
        Args:
            query (str): The query to extract the command from
            
        Returns:
            Optional[str]: The extracted command or None if no command found
        """
        # Keywords that indicate a command follows
        command_indicators = ["do", "run", "execute", "type", "send"]
        
        # Keywords that indicate a device target
        device_indicators = ["on", "to", "with", "the usb", "the serial", "the device", "the remote", "the screen"]
        
        # Split the query into words
        words = query.split()
        
        # Look for command indicators
        for i, word in enumerate(words):
            if word in command_indicators and i + 1 < len(words):
                # Found a command indicator, look for the command
                command_parts = []
                
                # Check if the command is in quotes
                if i + 1 < len(words) and words[i + 1].startswith(("'", '"')):
                    # Find the closing quote
                    quote_char = words[i + 1][0]
                    command_parts.append(words[i + 1][1:])  # Remove opening quote
                    
                    for j in range(i + 2, len(words)):
                        if words[j].endswith(quote_char):
                            command_parts.append(words[j][:-1])  # Remove closing quote
                            break
                        command_parts.append(words[j])
                else:
                    # No quotes, take the next word as the command
                    command_parts.append(words[i + 1])
                
                # Check if the command is followed by a device indicator
                command_str = ' '.join(command_parts)
                remaining_text = ' '.join(words[i + len(command_parts) + 1:])
                
                if any(indicator in remaining_text for indicator in device_indicators):
                    return command_str
        
        return None
    
    def process_command(self, user_input):
        """
        Process a single user command, determining whether it should be executed
        locally or sent to a screen session.
        
        Args:
            user_input (str): The command to process
            
        Returns:
            str: Command output or error message
        """
        if not user_input or not user_input.strip():
            return "Please enter a command."
            
        # First, check if this is a file or folder search query
        is_folder_search, folder_result = self._handle_folder_search(user_input)
        if is_folder_search:
            return folder_result
        
        # Check if query matches a USB/screen session use case
        screen_exists = self.screen_manager.check_screen_exists()
        explicitly_screen = self.screen_manager.is_explicitly_screen(user_input.lower())
        is_usb_query, usb_result = self.usb_handler.handle_usb_device_query(user_input.lower(), screen_exists, explicitly_screen)
        if is_usb_query:
            return usb_result
        
        # Check for direct shell command execution
        direct_result = self.direct_handler.handle_direct_execution(user_input)
        if direct_result:
            return direct_result
        
        query_lower = user_input.lower()
        
        # Direct command handling for Apple Notes app and other special folders
        if "notes" in query_lower and ("folder" in query_lower or 
                                      "app" in query_lower or
                                      "show me" in query_lower or
                                      "where" in query_lower):
            # Special case for Apple Notes - ensure we handle it directly
            return self.shell_handler.find_folders("Notes", location="~", include_cloud=True)
            
        # Check if this is a file/folder search request
        if "find" in query_lower or "search" in query_lower:
            # Extract search term if any
            search_terms = ["file", "folder", "directory"]
            for term in search_terms:
                if term in query_lower:
                    pattern = rf"(?:find|search)(?:\s+for)?\s+(?:a|the)?\s+{term}(?:s)?\s+(?:named|called)?\s+['\"]*([a-zA-Z0-9_\-\.\s]+)['\"\s]*"
                    match = re.search(pattern, query_lower)
                    if match:
                        search_name = match.group(1).strip()
                        if term in ["folder", "directory"]:
                            return self.shell_handler.find_folders(search_name)
                        else:
                            # Use find with both files and directories for generic file search
                            return self._try_direct_execution(f'find ~ -name "*{search_name}*" -type f 2>/dev/null | head -n 20')
        
        # Handle based on AI response
        return self._handle_with_ai(user_input)
    
    def _try_direct_execution(self, command):
        """
        Try to execute a command directly.
        
        Args:
            command (str): The command to execute
            
        Returns:
            str: Command output or error message
        """
        # Show the command that will be executed
        if self.output:
            self.output.command(command)
        else:
            self.log(f"Executing command: {command}")
        
        # Determine whether the command needs shell execution
        safety_level = self.shell_handler.check_command_safety_level(command) \
            if hasattr(self.shell_handler, 'check_command_safety_level') else None
            
        try:
            force_shell = safety_level in ['NOT_IN_WHITELIST', 'REQUIRES_SHELL_TRUE_ASSESSMENT'] \
                if safety_level else True
                
            # Execute the command
            result = self.shell_handler.execute_command(command, force_shell=force_shell)
            
            # Log the execution result
            self.command_logger.log_command_execution(command, command, True, result)
            
            # Show the result
            if self.output:
                self.output.result(True, result)
            
            return result
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            
            # Show the error
            if self.output:
                self.output.result(False, error_msg)
            else:
                self.log(error_msg)
            
            # Log the execution failure
            self.command_logger.log_command_execution(command, command, False, str(e))
            
            return error_msg
    
    def _handle_with_ai(self, user_input):
        """
        Handle the request using AI to generate a command.
        
        Args:
            user_input (str): The user request
            
        Returns:
            str: Execution result or error message
        """
        # Start a new output sequence for this AI-driven command
        if self.output:
            self.output.new_sequence()
            
        # Get system information for the AI prompt
        system_info = get_system_info()
        
        # Use our improved AI prompt that encourages structured responses
        prompt = self.command_extractor.format_ai_prompt(
            user_input, 
            {"system": system_info, "version": platform.release()}
        )

        if getattr(self, 'debug', False):
            print("\n[UaiBot DEBUG] AI Prompt Sent:\n", prompt)
        
        # Show thinking process if we have the output handler
        if self.output:
            thinking_msg = f"Analyzing your request: '{user_input}'\nGenerating appropriate command..."
            self.output.thinking(thinking_msg)
        else:
            self.log(f"Asking AI for a command...")
        
        # Get response from AI
        try:
            ai_response = self.ai_handler.get_ai_response(prompt)
        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            if self.output:
                self.output.error(error_msg)
            else:
                self.log(error_msg)
            return error_msg
        
        if getattr(self, 'debug', False):
            print("\n[UaiBot DEBUG] AI Response Received:\n", ai_response)

        # Extract command and metadata from AI response
        success, command, metadata = self.command_extractor.extract_command(ai_response)

        if getattr(self, 'debug', False):
            print("\n[UaiBot DEBUG] Extracted Command/Metadata:\n", json.dumps({"success": success, "command": command, "metadata": metadata}, indent=2, ensure_ascii=False))
        
        # Handle browser automation intent
        if metadata.get("intent") == "browser_automation":
            from core.browser_handler import BrowserAutomationHandler
            browser = metadata.get("browser", "")
            url = metadata.get("url", "")
            actions = metadata.get("actions", [])
            handler = BrowserAutomationHandler()
            result = handler.execute_actions(browser, url, actions)
            return result

        if success and command:
            # Show the command that will be executed
            if self.output:
                self.output.command(command)
            else:
                self.log(f"AI suggested command: {command}")
            
            # Execute the command
            result = self._try_direct_execution(command)
            
            # Show the result
            if self.output:
                self.output.result(True, result)
                
                # If there's an explanation, add it
                if metadata.get("parsed_json") and metadata["parsed_json"].get("explanation"):
                    self.output.explanation(metadata["parsed_json"]["explanation"])
                    
                # Return a simpler response for the calling function
                return result
            else:
                # Format the response for legacy output path
                formatted_response = f"📋 I ran this command for you:\n{command}\n\n📊 Result:\n{result}"
                
                # If there's an explanation in the metadata, add it
                if metadata.get("parsed_json") and metadata["parsed_json"].get("explanation"):
                    formatted_response += f"\n\n💡 {metadata['parsed_json']['explanation']}"
                    
                return formatted_response
        
        elif metadata["is_error"]:
            # This is an error response - log it for implementation
            error_message = metadata["error_message"] or "This request cannot be handled by a simple command."
            
            # Extract detailed implementation requirements
            details = self.command_extractor.extract_implementation_details(ai_response)
            
            # Log the implementation requirement
            self.command_logger.log_implementation_needed(user_input, error_message, details)
            
            # Format the response based on output handler availability
            if self.output:
                # Show the error using the output handler
                self.output.error(f"Unable to execute this request: {error_message}")
                self.output.info("This request has been logged for future implementation.")
                
                # Add complexity info if available
                if details.get("complexity") != "unknown":
                    self.output.info(f"This appears to be a {details['complexity']} complexity task.")
                    
                return error_message
            else:
                # Legacy output format
                self.log(f"AI Error: {error_message}")
                
                response = (f"❌ I'm unable to execute this request: {error_message}\n\n"
                          f"This request has been logged for future implementation.")
                           
                # Add complexity info if available
                if details.get("complexity") != "unknown":
                    response += f"\n\nThis appears to be a {details['complexity']} complexity task."
                    
                return response
        else:
            # No command found but no explicit error - treat as general response
            # Clean up the AI response to make it user-friendly
            clean_response = ai_response.replace("```json", "").replace("```", "").strip()
            
            # Try to parse as JSON to extract any useful info
            try:
                data = json.loads(clean_response)
                if isinstance(data, dict):
                    if "error" in data and data["error"]:
                        # This is an error response in JSON format
                        error_message = data.get("error_message", "This request cannot be handled by a simple command.")
                        
                        # Log the implementation requirement
                        self.command_logger.log_implementation_needed(
                            user_input, 
                            error_message, 
                            {"reason": error_message}
                        )
                        
                        # Display using output handler if available
                        if self.output:
                            self.output.error(f"Unable to execute this request: {error_message}")
                            self.output.info("This request has been logged for future implementation.")
                            return error_message
                        else:
                            return f"❌ I'm unable to execute this request: {error_message}\n\nThis request has been logged for future implementation."
                    
                    # There might be other useful information in the JSON
                    if "explanation" in data:
                        if self.output:
                            self.output.explanation(data['explanation'])
                            return data['explanation']
                        else:
                            return f"💡 {data['explanation']}"
            except json.JSONDecodeError:
                # Not valid JSON, just use the raw response
                pass
            
            # Return a clean version of the AI response as information
            if self.output:
                self.output.explanation(clean_response)
                return clean_response
            else:    
                return f"💡 {clean_response}"
            
    def _handle_folder_search(self, query):
        """
        Check if the query is asking about files or folders and handle accordingly.
        Uses AI-driven extraction instead of regex-based detection.
        
        Args:
            query (str): The user query
        
        Returns:
            tuple: (is_folder_search, result)
        """
        # Use AI to determine if this is a folder search query
        prompt = self.command_extractor.format_ai_prompt(
            query,
            {"system": "Check if the query is asking to list or find a folder. If so, extract the folder name."}
        )
        ai_response = self.ai_handler.process_command(prompt)
        success, command, metadata = self.command_extractor.extract_command(ai_response)
        
        if success and metadata.get("intent") == "folder_search":
            folder_name = metadata.get("folder_name", "")
            if folder_name:
                if folder_name.lower() == "notes":
                    return True, self.shell_handler.find_folders("Notes", location="~", include_cloud=True)
                else:
                    return True, self.shell_handler.find_folders(folder_name, location="~", include_cloud=True)
        
        return False, ""
    
    def _check_usb_query(self, user_input):
        """Check if the query is about USB devices."""
        # Keywords that indicate USB queries
        usb_keywords = [
            "usb", "devices", "attached", "connect", "plugged", "inserted", 
            "ports", "hardware", "serial", "tty", "dev", "cu.", "tty."
        ]
        
        # Check if the query contains USB-related keywords
        if any(keyword in user_input.lower() for keyword in usb_keywords):
            # Get USB device information using run_command
            result = self.usb_detector.get_usb_devices()
            return True, result
            
        return False, None

def process_command(self, user_input):
    """Process user input and execute commands directly."""
    # ...existing code...
    
    # Check for current directory queries (high priority)
    if self._is_directory_query(user_input.lower()):
        return self._handle_directory_query(user_input)
    
    # Check if this is a file or folder search query
    is_folder_search, folder_result = self._handle_folder_search(user_input)
    if is_folder_search:
        return folder_result
        
    # ...existing code...

def _is_directory_query(self, query):
    """Check if the query is about the current directory."""
    directory_keywords = [
        'where am i', 'current directory', 'pwd', 'active folder', 
        'current folder', 'present working directory', 'what directory',
        'which directory', 'what folder', 'which folder', 'active folder now',
        'what is active folder', 'what is current folder'
    ]
    return any(keyword in query for keyword in directory_keywords)
    
def _handle_directory_query(self, query):
    """Handle queries about the current directory."""
    if hasattr(self.shell_handler, 'handle_directory_query'):
        return self.shell_handler.handle_directory_query(query)
    else:
        # Fallback if the handler doesn't have the method
        if self.system_platform == 'windows':
            command = 'cd'
        else:
            command = 'pwd'
        result = self.shell_handler.execute_command(command)
        return f"📁 Current directory: {result.strip()}"
