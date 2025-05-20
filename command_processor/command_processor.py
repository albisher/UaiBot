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

# Import from the device_manager for USB detection
from device_manager.usb_detector import USBDetector

# Import our new modules for improved command processing
from command_processor.ai_command_extractor import AICommandExtractor
from command_processor.logger import CommandLogger

# Set up logging
logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self, ai_handler, shell_handler, quiet_mode=False, fast_mode=False, output_facade=None):
        """
        Initialize the CommandProcessor.
        
        Args:
            ai_handler: AI handler instance for processing commands
            shell_handler: Shell handler instance for executing commands
            quiet_mode (bool): If True, reduces terminal output
            fast_mode (bool): If True, handles errors quickly and exits
            output_facade: Reference to the output facade for UI handling
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
            device_command_patterns = [
                r'(?:on|to|with)\s+(?:the\s+)?(?:usb|serial|device|remote|screen).*?(?:do|run|execute|type|send)\s+[\'"]?([\w\s\-\.\/\*]+)[\'"]',
                r'(?:do|run|execute|type|send)\s+[\'"]?([\w\s\-\.\/\*]+)[\'"].*?(?:on|to|with)\s+(?:the\s+)?(?:usb|serial|device|remote|screen)',
            ]
            
            command_match = None
            for pattern in device_command_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    command_match = match.group(1).strip()
                    self.log(f"Sending command '{command_match}' to active USB/screen session...")
                    result = self.shell_handler.send_to_screen_session(command_match)
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
        is_usb_query, usb_result = self._check_usb_query(user_input)
        if is_usb_query:
            return usb_result
        
        # Check for direct shell command execution (starts with ! or common command)
        if user_input.startswith("!") or user_input.split()[0] in self.common_commands:
            # If it starts with !, remove it before execution
            command = user_input[1:].strip() if user_input.startswith("!") else user_input
            return self._try_direct_execution(command)
        
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
        
        # Extract command and metadata from AI response
        success, command, metadata = self.command_extractor.extract_command(ai_response)
        
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
        
        Args:
            query (str): The user query
        
        Returns:
            tuple: (is_folder_search, result)
        """
        query_lower = query.lower()
        
        # Common folder names that users might ask about
        common_folders = {
            "note": ["notes", "note", "notebook", "notebooks", "notes app", "apple notes"],
            "document": ["documents", "document", "docs", "doc"],
            "download": ["downloads", "download"],
            "desktop": ["desktop"],
            "picture": ["pictures", "picture", "photos", "photo", "images", "image"],
            "music": ["music", "songs", "audio"],
            "video": ["videos", "video", "movies", "movie"],
            "application": ["applications", "apps", "app", "programs", "program"],
            "project": ["projects", "project", "repos", "repositories", "repository", "code"],
            "work": ["work", "workspace", "office"],
            "school": ["school", "university", "college", "academic"],
            "game": ["games", "game", "steam", "gaming"]
        }
        
        # ===== Enhanced detection for direct "show me" commands =====
        # Direct commands like "show me X" or "show X"
        direct_show_patterns = [
            r"^show\s+(?:me\s+)?(?:my\s+)?(.+?)(?:\s+folders?)?$",
            r"^display\s+(?:my\s+)?(.+?)(?:\s+folders?)?$",
            r"^list\s+(?:my\s+)?(.+?)(?:\s+folders?)?$",
            r"^open\s+(?:my\s+)?(.+?)(?:\s+folders?)?$"
        ]
        
        # Check for direct commands first (highest priority)
        import re
        for pattern in direct_show_patterns:
            match = re.match(pattern, query_lower)
            if match:
                requested_item = match.group(1).strip()
                # Check if it's a known folder type
                for folder_type, variants in common_folders.items():
                    if requested_item in variants or any(v in requested_item for v in variants):
                        if folder_type == "note":
                            # Special handling for Notes app on macOS
                            return True, self.shell_handler.find_folders("Notes", location="~", include_cloud=True)
                        else:
                            # Handle other folder types
                            search_term = folder_type.title() + "s"  # e.g., Documents, Downloads
                            return True, self.shell_handler.find_folders(search_term, location="~", include_cloud=True)
        
        # Check if query is asking to list folders with more general phrases
        contains_list_action = any(action in query_lower for action in 
                             ["list", "show", "find", "where", "locate", "search for", "look for", "get"])
                             
        # Phrases that indicate the user is asking about a folder's location
        folder_query_phrases = [
            "where is", "where are", "find my", "show my", "look for my", "search for my",
            "where can i find", "do i have", "got any", "have any", "locate my"
        ]
        
        # If query contains folder query phrases, mark it as a list action
        if not contains_list_action:
            contains_list_action = any(phrase in query_lower for phrase in folder_query_phrases)
        
        if contains_list_action:
            # Check for each type of common folder
            for folder_type, variants in common_folders.items():
                if any(variant in query_lower for variant in variants):
                    # Determine the search parameters based on folder type
                    if folder_type == "note":
                        # For Notes, use specialized search with cloud folders
                        return True, self.shell_handler.find_folders("Notes", location="~", include_cloud=True)
                    elif folder_type in ["document", "download", "desktop", "picture", "music", "video"]:
                        # Search in home directory for these common folders
                        search_term = folder_type.title() + "s"  # e.g., Documents, Downloads
                        return True, self.shell_handler.find_folders(search_term, location="~", include_cloud=True)
                    else:
                        # General search
                        search_term = folder_type + "s"
                        return True, self.shell_handler.find_folders(search_term, location="~", include_cloud=True)
        
        # Check for possession-based queries about folders
        has_possession = any(term in query_lower for term in ["my", "i have", "i've got", "i got", "do i have"])
        if has_possession:
            for folder_type, variants in common_folders.items():
                if any(variant in query_lower for variant in variants):
                    search_term = folder_type.title() if folder_type == "note" else folder_type.title() + "s"
                    return True, self.shell_handler.find_folders(search_term, location="~")
        
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
