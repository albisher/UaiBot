"""
Command Pattern Detector Module
Provides functionality to analyze command patterns and determine proper routing
"""
import shlex

class CommandPatternDetector:
    def __init__(self):
        # Common terminal commands that we might need to handle
        self.common_commands = [
            # File & directory operations
            'ls', 'pwd', 'cd', 'mkdir', 'rmdir', 'cp', 'mv', 'rm', 'touch', 'cat', 'find',
            # Text viewing/editing
            'more', 'less', 'head', 'tail', 'nano', 'vi', 'vim', 'grep', 'awk', 'sed',
            # System info
            'top', 'ps', 'kill', 'killall', 'df', 'du', 'free', 'uptime', 'date', 'cal', 
            'who', 'whoami',
            # Networking
            'ping', 'curl', 'wget', 'ssh', 'scp', 'ifconfig', 'netstat', 'traceroute', 'nslookup',
            # macOS specific
            'open', 'pbcopy', 'pbpaste', 'say', 'ditto', 'mdfind', 'diskutil',
            # Miscellaneous
            'echo', 'history', 'man', 'clear', 'alias', 'crontab'
        ]
        
        self.interactive_commands = ['nano', 'vi', 'vim', 'less', 'more', 'top', 'man']
        self.navigation_commands = ['ls', 'pwd', 'cd', 'clear']
        
        # Screen and device-related indicators
        self.screen_session_indicators = [
            "screen session", "serial port", "usb terminal", "in screen", "on screen", 
            "to screen", "through screen", "via screen", "in the screen", "on the screen",
            "in terminal session", "in the terminal session", "over serial", "screened os",
            "remote device", "remote os", "remote system", "remote machine", "other os",
            "other machine", "over usb connection", "over my usb", "over the usb",
            "through screen", "in screen session", "other system", "screened system",
            "connected system", "device usb"
        ]
        
        self.usb_device_indicators = ['usb', 'serial', 'tty', 'dev/cu', 'dev/tty']
        
        # Command extraction patterns
        self.command_verbs = ["make", "tell", "have", "do", "run", "execute", "type", "send"]
        self.target_indicators = ["it", "screen", "terminal", "session", "usb", "device", "remote"]
        self.preposition_indicators = ["in", "on", "at", "to", "with", "through", "via"]
        
    def get_command_type(self, command_str):
        """
        Determine the type of command
        
        Args:
            command_str (str): The command string to analyze
            
        Returns:
            str: The command type ('TERMINAL', 'SCREEN', 'USB', 'OTHER')
        """
        if not command_str.strip():
            return "EMPTY"
            
        command_parts = command_str.split()
        if not command_parts:
            return "EMPTY"
            
        command_base = command_parts[0].lower()
        
        # Check if this is a direct command that we recognize
        if command_base in self.common_commands:
            return "TERMINAL"
            
        # Check for screen-specific commands
        if command_base == "screen":
            return "SCREEN"
            
        # Check for USB-specific commands
        for indicator in self.usb_device_indicators:
            if indicator in command_str.lower():
                return "USB"
                
        # Default to 'OTHER' for everything else
        return "OTHER"
        
    def is_explicit_screen_command(self, query_lower):
        """
        Check if the query explicitly mentions a screen session
        
        Args:
            query_lower (str): The lowercase query string
            
        Returns:
            bool: True if the query mentions a screen explicitly
        """
        return any(indicator in query_lower for indicator in self.screen_session_indicators)
        
    def detect_command_target(self, command, context=""):
        """
        Determine if a command should go to the screen session or local system.
        
        Args:
            command (str): The command to analyze
            context (str): Additional context text that might hint at target
            
        Returns:
            str: "SCREEN", "LOCAL", or "UNKNOWN"
        """
        context_lower = context.lower()
        
        # If explicit screen indicators in context, prefer screen
        if self.is_explicit_screen_command(context_lower):
            return "SCREEN"
            
        # Split the command to get the base command
        command_parts = command.split()
        base_command = command_parts[0] if command_parts else ""
        
        # Navigation commands with no args are ambiguous
        # They could be for either local system or screen session
        if base_command in self.navigation_commands and len(command_parts) == 1:
            # Check if we have a USB/serial context
            if any(term in context_lower for term in self.usb_device_indicators):
                return "SCREEN"
            else:
                return "LOCAL"
                
        # System information commands typically run locally
        sys_commands = ['top', 'ps', 'df', 'du', 'uptime', 'date', 'whoami', 'who']
        if base_command in sys_commands:
            return "LOCAL"
            
        # Mac-specific commands almost always run locally
        mac_commands = ['open', 'say', 'pbcopy', 'pbpaste', 'networksetup', 'airport',
                        'system_profiler', 'sw_vers', 'defaults', 'osascript']
        if base_command in mac_commands:
            return "LOCAL"
            
        # If we can't determine, default to LOCAL for safety
        return "LOCAL"
        
    def extract_screen_command(self, query_lower):
        """
        Try to extract a command from a natural language query about screen/terminal
        
        Args:
            query_lower (str): The lowercase query string
            
        Returns:
            str or None: The extracted command, or None if no command found
        """
        words = query_lower.split()
        
        # Pattern 1: "make it do X" or "tell screen to do X"
        for i in range(len(words) - 3):
            if (words[i] in ["make", "tell", "have"] and 
                words[i+1] in ["it", "screen", "terminal", "session"] and
                words[i+2] in ["do", "run", "execute", "type"]):
                # Extract command after the verb
                remaining = ' '.join(words[i+3:])
                return self._extract_quoted_command(remaining)
        
        # Pattern 2: "in screen do X" or "on terminal do X"
        for i in range(len(words) - 3):
            if (words[i] in ["in", "on", "at"] and
                words[i+1] in ["the", "screen", "terminal", "session"] and
                any(words[i+j] in ["do", "run", "execute", "type"] for j in range(2, 4))):
                # Find the verb
                verb_idx = i + 2 if words[i+2] in ["do", "run", "execute", "type"] else i + 3
                # Extract command after the verb
                remaining = ' '.join(words[verb_idx+1:])
                return self._extract_quoted_command(remaining)
        
        # Pattern 3: "send X to screen" or "run X in terminal"
        for i in range(len(words) - 3):
            if words[i] in ["send", "run", "do", "execute", "type"]:
                # Extract command after the verb
                remaining = ' '.join(words[i+1:])
                command = self._extract_quoted_command(remaining)
                if command:
                    # Check if the command is followed by a target indicator
                    remaining_after_command = remaining[len(command):].strip()
                    if any(indicator in remaining_after_command for indicator in 
                          ["to", "in", "on", "at", "screen", "terminal", "session"]):
                        return command
        
        # If no complex pattern matched, check for simple commands
        for cmd in self.common_commands:
            if cmd in query_lower and any(term in query_lower for term in ['screen', 'terminal', 'session', 'serial']):
                return cmd
                
        return None
        
    def extract_device_command(self, query_lower):
        """
        Try to extract a command related to USB devices
        
        Args:
            query_lower (str): The lowercase query string
            
        Returns:
            str or None: The extracted command, or None if no command found
        """
        words = query_lower.split()
        
        # Pattern 1: "on usb do X" or "with device do X"
        for i in range(len(words) - 3):
            if (words[i] in ["on", "to", "with"] and
                words[i+1] in ["the", "usb", "serial", "device", "remote", "screen"] and
                any(words[i+j] in ["do", "run", "execute", "type", "send"] for j in range(2, 4))):
                # Find the verb
                verb_idx = i + 2 if words[i+2] in ["do", "run", "execute", "type", "send"] else i + 3
                # Extract command after the verb
                remaining = ' '.join(words[verb_idx+1:])
                return self._extract_quoted_command(remaining)
        
        # Pattern 2: "do X on usb" or "send X to device"
        for i in range(len(words) - 3):
            if words[i] in ["do", "run", "execute", "type", "send"]:
                # Extract command after the verb
                remaining = ' '.join(words[i+1:])
                command = self._extract_quoted_command(remaining)
                if command:
                    # Check if the command is followed by a target indicator
                    remaining_after_command = remaining[len(command):].strip()
                    if any(indicator in remaining_after_command for indicator in 
                          ["on", "to", "with", "usb", "serial", "device", "remote", "screen"]):
                        return command
        
        # If no specific pattern, check for certain verbs or actions
        if any(action in query_lower for action in ['list', 'show', 'check', 'get']):
            if any(term in query_lower for term in ['usb', 'device', 'serial']):
                return "list_devices"
                
        return None
        
    def _extract_quoted_command(self, text):
        """
        Extract a command from quoted text or single word.
        
        Args:
            text (str): The text to extract from
            
        Returns:
            str or None: The extracted command, or None if no command found
        """
        text = text.strip()
        
        # Check for quoted command
        if text.startswith(("'", '"')):
            quote_char = text[0]
            end_quote = text.find(quote_char, 1)
            if end_quote != -1:
                return text[1:end_quote]
        
        # Check for backtick command
        if text.startswith('`'):
            end_backtick = text.find('`', 1)
            if end_backtick != -1:
                return text[1:end_backtick]
        
        # If no quotes, take the first word
        return text.split()[0] if text else None
