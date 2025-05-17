"""
Command processing module for UaiBot.
Handles determining whether commands should be executed locally or sent to a screen session.
"""
import re
import subprocess
import platform

# Import from the core
from core.ai_handler import get_system_info

# Import from the device_manager for USB detection
from device_manager.usb_detector import USBDetector

class CommandProcessor:
    def __init__(self, ai_handler, shell_handler, quiet_mode=False):
        """
        Initialize the CommandProcessor.
        
        Args:
            ai_handler: AI handler instance for processing commands
            shell_handler: Shell handler instance for executing commands
            quiet_mode (bool): If True, reduces terminal output
        """
        self.ai_handler = ai_handler
        self.shell_handler = shell_handler
        self.quiet_mode = quiet_mode
        self.system_platform = platform.system().lower()
        self.usb_detector = USBDetector(quiet_mode=quiet_mode)
        
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
        
        # Direct command handling for Apple Notes app and other special folders
        if "notes" in user_input.lower() and ("folder" in user_input.lower() or 
                                            "app" in user_input.lower() or
                                            "show me" in user_input.lower() or
                                            "where" in user_input.lower()):
            # Special case for Apple Notes - ensure we handle it directly
            return self.shell_handler.find_folders("Notes", location="~", include_cloud=True)
            
        # Check if this is a file/folder search request
        if "find" in user_input.lower() or "search" in user_input.lower():
            # Extract search term if any
            search_terms = ["file", "folder", "directory"]
            for term in search_terms:
                if term in user_input.lower():
                    pattern = rf"(?:find|search)(?:\s+for)?\s+(?:a|the)?\s+{term}(?:s)?\s+(?:named|called)?\s+['\"]*([a-zA-Z0-9_\-\.\s]+)['\"\s]*"
                    match = re.search(pattern, user_input.lower())
                    if match:
                        search_name = match.group(1).strip()
                        if term in ["folder", "directory"]:
                            return self.shell_handler.find_folders(search_name)
                        else:
                            # Use find with both files and directories for generic file search
                            return self.shell_handler.execute_command(f'find ~ -name "*{search_name}*" -type f 2>/dev/null | head -n 20', force_shell=True)
        
        # If it's a direct command (starts with ! or is a common command), execute it directly
        if user_input.startswith("!") or user_input.split()[0] in self.common_commands:
            return self.shell_handler.execute_command(user_input)
        
        query_lower = user_input.lower()
        user_input_orig = user_input  # Save original input with proper case
        
        # Check if there's a current screen context
        screen_exists = self.check_screen_exists()
        
        # First check for explicit screen session command indicators
        explicitly_screen = self.is_explicitly_screen(query_lower)
        
        # Check for commands that INITIATE screen sessions
        if query_lower.startswith("screen ") and any(term in query_lower for term in ['dev', 'cu', 'tty', 'serial', 'usb']):
            # This is likely a command to open a new screen session with a device
            cmd = self.shell_handler.execute_command(user_input_orig)
            return cmd
        
        # Handle USB device specific commands
        handled, result = self.handle_usb_device_query(query_lower, screen_exists, explicitly_screen)
        if handled:
            return result
            
        # Fall back to AI for command suggestion if not handled by specific logic
        # Get detailed system information for the AI prompt
        system_info = get_system_info()
        
        prompt_for_ai = (
            f"User request: '{user_input}'. "
            f"You are running on {system_info}. "
            f"Based on this request, suggest a single, common, and safe command specifically for this system. "
            "Avoid generating complex command chains (e.g., using ';', '&&', '||') unless the user's request explicitly implies it and it's a very common pattern. "
            "Do not provide explanations, only the command itself. "
            f"If the request is ambiguous or potentially unsafe to translate into a shell command, respond with 'Error: Cannot fulfill request safely.'"
        )

        ai_response_command = self.ai_handler.query_ai(prompt_for_ai)
        if not self.quiet_mode:
            print(f"AI Suggested Command: {ai_response_command}")

        if ai_response_command and not ai_response_command.startswith("Error:"):
            safety_level = self.shell_handler.check_command_safety_level(ai_response_command)
            if not self.quiet_mode:
                print(f"Command safety level: {safety_level}")
            # Auto-execute suggested command without prompts
            force_shell = safety_level in ['NOT_IN_WHITELIST', 'REQUIRES_SHELL_TRUE_ASSESSMENT']
            if not self.quiet_mode:
                print(f"Executing command: {ai_response_command}")
            command_output = self.shell_handler.execute_command(ai_response_command, force_shell=force_shell)
            return command_output
        elif ai_response_command.startswith("Error:"):
            return f"AI Error: {ai_response_command}\nSkipping execution due to AI error."
        else:
            return "AI did not return a valid command string."
    
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
