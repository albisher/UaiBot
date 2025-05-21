import re
from typing import Dict, Optional, Any, Union, List
import logging
from uaibot.core.system_commands import SystemCommands
from uaibot.core.multilingual_commands import MultilingualCommands
from uaibot.core.utils import Utils
from uaibot.core.browser_handler import BrowserHandler

logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self, use_regex: bool = True, fast_mode: bool = False):
        self.use_regex = use_regex
        self.fast_mode = fast_mode
        self.system_commands = SystemCommands()
        self.multilingual_commands = MultilingualCommands()
        self.utils = Utils()
        self.browser_handler = BrowserHandler()
        
        # Command history
        self.command_history = []
        self.current_command = None
        self.command_queue = []
        self.command_results = {}
        
    def ai_interpret_command(self, command: str) -> Dict[str, Any]:
        """Interpret commands using AI-driven logic."""
        command_lower = command.lower()
        command_stripped = command.strip()

        # Check for browser commands first
        browser_indicators = [
            # Direct search commands
            "search", "look for", "find", "query", "look up", "google",
            
            # Question formats
            "what is", "who is", "where is", "how to", "what's", "what are",
            "when is", "why is", "which is",
            
            # Polite requests
            "can you find", "could you search", "please search", "would you search",
            "i want to know", "i need to know", "tell me about", "show me",
            "get information about", "find out about",
            
            # Time and weather related
            "what's the weather", "weather in", "current time in", "time in",
            "what time is it in",
            
            # General information requests
            "information about", "details about", "learn about", "read about",
            "know about",
            
            # Action requests
            "how do i", "how can i", "where can i", "what should i",
            "when should i",
            
            # Comparison requests
            "compare", "difference between", "versus", "vs",
            
            # Location based
            "near me", "around here", "in this area", "local",
            
            # News and updates
            "latest news about", "recent updates on", "what's new in",
            "what's happening with"
        ]
        
        if any(indicator in command_lower for indicator in browser_indicators):
            return {"type": "browser", "operation": "search", "command": command}

        # --- File operations (English & basic Arabic) ---
        # Create file
        if (
            "create" in command_lower and "file" in command_lower
            or "make" in command_lower and "file" in command_lower
            or "new file" in command_lower
            or "انشاء ملف" in command_lower
            or "ملف جديد" in command_lower
        ):
            filename = self._extract_filename(command)
            content = self._extract_content(command)
            # Handle commands like 'create a new file test.txt and write ...'
            if not filename:
                # Try to find filename after 'file' or 'ملف'
                import re
                match = re.search(r'(?:file|ملف)\s+([\w\-.]+)', command_lower)
                if match:
                    filename = match.group(1)
            return {"type": "file", "operation": "create", "filename": filename, "content": content}

        # Read file
        if (
            ("read" in command_lower or "show" in command_lower or "display" in command_lower or "open" in command_lower or "عرض" in command_lower or "افتح" in command_lower)
            and ("file" in command_lower or "ملف" in command_lower or any(ext in command_lower for ext in [".txt", ".md", ".json", ".py"]))
        ):
            filename = self._extract_filename(command)
            if not filename:
                import re
                match = re.search(r'(?:file|ملف)\s+([\w\-.]+)', command_lower)
                if match:
                    filename = match.group(1)
            return {"type": "file", "operation": "read", "filename": filename}

        # Write file
        if (
            ("write" in command_lower or "update" in command_lower or "save" in command_lower or "modify" in command_lower or "change" in command_lower or "اكتب" in command_lower or "تحديث" in command_lower)
            and ("file" in command_lower or "ملف" in command_lower or any(ext in command_lower for ext in [".txt", ".md", ".json", ".py"]))
        ):
            filename = self._extract_filename(command)
            content = self._extract_content(command)
            return {"type": "file", "operation": "write", "filename": filename, "content": content}

        # Append file
        if (
            ("append" in command_lower or "add" in command_lower or "اضف" in command_lower or "اضافة" in command_lower)
            and ("file" in command_lower or "ملف" in command_lower or any(ext in command_lower for ext in [".txt", ".md", ".json", ".py"]))
        ):
            filename = self._extract_filename(command)
            content = self._extract_content(command)
            return {"type": "file", "operation": "append", "filename": filename, "content": content}

        # Delete file
        if (
            ("delete" in command_lower or "remove" in command_lower or "حذف" in command_lower or "امسح" in command_lower)
            and ("file" in command_lower or "ملف" in command_lower or any(ext in command_lower for ext in [".txt", ".md", ".json", ".py"]))
        ):
            filename = self._extract_filename(command)
            if not filename:
                import re
                match = re.search(r'(?:file|ملف)\s+([\w\-.]+)', command_lower)
                if match:
                    filename = match.group(1)
            return {"type": "file", "operation": "delete", "filename": filename}

        # List files
        if (
            ("list" in command_lower or "show all" in command_lower or "عرض الكل" in command_lower or "عرض جميع" in command_lower)
            and ("files" in command_lower or "ملفات" in command_lower or "directory" in command_lower or "مجلد" in command_lower or "." in command_lower)
        ):
            return {"type": "file", "operation": "list"}

        # Search files
        if (
            ("search" in command_lower or "find" in command_lower or "look for" in command_lower or "ابحث" in command_lower)
            and ("file" in command_lower or "ملف" in command_lower or "files" in command_lower or "ملفات" in command_lower)
        ):
            pattern = self._extract_pattern(command)
            return {"type": "file", "operation": "search", "pattern": pattern}

        # --- System, Language, Utility (unchanged for now) ---
        # System operations
        elif any(word in command_lower for word in ["system status", "system info"]):
            return {"type": "system", "operation": "status"}
        elif any(word in command_lower for word in ["cpu info", "processor info"]):
            return {"type": "system", "operation": "cpu"}
        elif any(word in command_lower for word in ["memory info", "ram info"]):
            return {"type": "system", "operation": "memory"}
        elif any(word in command_lower for word in ["disk info", "storage info"]):
            return {"type": "system", "operation": "disk"}
        elif any(word in command_lower for word in ["network info", "connection info"]):
            return {"type": "system", "operation": "network"}
        elif any(word in command_lower for word in ["process info", "running processes"]):
            return {"type": "system", "operation": "process"}
        elif any(word in command_lower for word in ["system logs", "show logs"]):
            return {"type": "system", "operation": "logs"}
            
        # Language operations
        elif any(word in command_lower for word in ["set language", "change language"]):
            return {"type": "language", "operation": "set", "language": self._extract_language(command)}
        elif any(word in command_lower for word in ["detect language", "identify language"]):
            return {"type": "language", "operation": "detect", "text": self._extract_text(command)}
        elif any(word in command_lower for word in ["translate", "convert to"]):
            return {"type": "language", "operation": "translate", "text": self._extract_text(command), "target_language": self._extract_language(command)}
        elif any(word in command_lower for word in ["supported languages", "available languages"]):
            return {"type": "language", "operation": "list"}
            
        # Utility operations
        elif any(word in command_lower for word in ["help", "show help"]):
            return {"type": "utility", "operation": "help"}
        elif any(word in command_lower for word in ["version", "show version"]):
            return {"type": "utility", "operation": "version"}
        elif any(word in command_lower for word in ["status", "show status"]):
            return {"type": "utility", "operation": "status"}
        elif any(word in command_lower for word in ["configuration", "show config"]):
            return {"type": "utility", "operation": "config"}
        elif any(word in command_lower for word in ["logs", "show logs"]):
            return {"type": "utility", "operation": "logs"}
        elif any(word in command_lower for word in ["enable debug", "turn on debug"]):
            return {"type": "utility", "operation": "debug", "enabled": True}
        elif any(word in command_lower for word in ["disable debug", "turn off debug"]):
            return {"type": "utility", "operation": "debug", "enabled": False}
        elif any(word in command_lower for word in ["errors", "show errors"]):
            return {"type": "utility", "operation": "errors"}
            
        return {"type": "unknown", "operation": "unknown"}
        
    def _extract_filename(self, command: str) -> str:
        """Extract filename from command."""
        # Try to find filename in quotes
        match = re.search(r'[\'"]([^\'"]+)[\'"]', command)
        if match:
            return match.group(1)
            
        # Try to find filename after certain keywords
        for keyword in ["file", "called", "named"]:
            parts = command.split(keyword)
            if len(parts) > 1:
                filename = parts[1].strip().split()[0]
                if filename.endswith(('.txt', '.py', '.json', '.md')):
                    return filename
                    
        return ""
        
    def _extract_content(self, command: str) -> str:
        """Extract content from command."""
        # Try to find content in quotes
        match = re.search(r'[\'"]([^\'"]+)[\'"]', command)
        if match:
            return match.group(1)
            
        # Try to find content after certain keywords
        for keyword in ["content", "text", "with"]:
            parts = command.split(keyword)
            if len(parts) > 1:
                return parts[1].strip()
                
        return ""
        
    def _extract_pattern(self, command: str) -> str:
        """Extract pattern from command."""
        # Try to find pattern in quotes
        match = re.search(r'[\'"]([^\'"]+)[\'"]', command)
        if match:
            return match.group(1)
            
        # Try to find pattern after certain keywords
        for keyword in ["for", "containing", "matching"]:
            parts = command.split(keyword)
            if len(parts) > 1:
                return parts[1].strip()
                
        return ""
        
    def _extract_language(self, command: str) -> str:
        """Extract language from command."""
        # Try to find language in quotes
        match = re.search(r'[\'"]([^\'"]+)[\'"]', command)
        if match:
            return match.group(1)
            
        # Try to find language after certain keywords
        for keyword in ["to", "language"]:
            parts = command.split(keyword)
            if len(parts) > 1:
                return parts[1].strip()
                
        return ""
        
    def _extract_text(self, command: str) -> str:
        """Extract text from command."""
        # Try to find text in quotes
        match = re.search(r'[\'"]([^\'"]+)[\'"]', command)
        if match:
            return match.group(1)
            
        # Try to find text after certain keywords
        for keyword in ["text", "content"]:
            parts = command.split(keyword)
            if len(parts) > 1:
                return parts[1].strip()
                
        return ""
        
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command."""
        # Add to command history
        self.command_history.append(command)
        self.current_command = command
        
        # Interpret command
        if self.use_regex:
            # Use regex-based command interpretation
            command_lower = command.lower()
            
            # File commands
            if any(word in command_lower for word in ["create", "make", "new file"]):
                return self._handle_file_command("create", self._extract_filename(command), self._extract_content(command))
            elif any(word in command_lower for word in ["read", "open", "show", "display", "content"]):
                return self._handle_file_command("read", self._extract_filename(command))
            elif any(word in command_lower for word in ["write", "save", "update", "modify", "change"]):
                return self._handle_file_command("write", self._extract_filename(command), self._extract_content(command))
            elif any(word in command_lower for word in ["append", "add"]):
                return self._handle_file_command("append", self._extract_filename(command), self._extract_content(command))
            elif any(word in command_lower for word in ["delete", "remove"]):
                return self._handle_file_command("delete", self._extract_filename(command))
            elif any(word in command_lower for word in ["list", "show all", "show files"]):
                return self._handle_file_command("list")
            elif any(word in command_lower for word in ["search", "find", "look for"]):
                return self._handle_file_command("search", pattern=self._extract_pattern(command))
                
            # System commands
            elif any(word in command_lower for word in ["system status", "system info"]):
                return self.system_commands.execute_command(command)
            elif any(word in command_lower for word in ["cpu info", "processor info"]):
                return self.system_commands.execute_command(command)
            elif any(word in command_lower for word in ["memory info", "ram info"]):
                return self.system_commands.execute_command(command)
            elif any(word in command_lower for word in ["disk info", "storage info"]):
                return self.system_commands.execute_command(command)
            elif any(word in command_lower for word in ["network info", "connection info"]):
                return self.system_commands.execute_command(command)
            elif any(word in command_lower for word in ["process info", "running processes"]):
                return self.system_commands.execute_command(command)
            elif any(word in command_lower for word in ["system logs", "show logs"]):
                return self.system_commands.execute_command(command)
                
            # Language commands
            elif any(word in command_lower for word in ["set language", "change language"]):
                return self.multilingual_commands.execute_command(command)
            elif any(word in command_lower for word in ["detect language", "identify language"]):
                return self.multilingual_commands.execute_command(command)
            elif any(word in command_lower for word in ["translate", "convert to"]):
                return self.multilingual_commands.execute_command(command)
            elif any(word in command_lower for word in ["supported languages", "available languages"]):
                return self.multilingual_commands.execute_command(command)
                
            # Utility commands
            elif any(word in command_lower for word in ["help", "show help"]):
                return self.utils.execute_command(command)
            elif any(word in command_lower for word in ["version", "show version"]):
                return self.utils.execute_command(command)
            elif any(word in command_lower for word in ["status", "show status"]):
                return self.utils.execute_command(command)
            elif any(word in command_lower for word in ["configuration", "show config"]):
                return self.utils.execute_command(command)
            elif any(word in command_lower for word in ["logs", "show logs"]):
                return self.utils.execute_command(command)
            elif any(word in command_lower for word in ["enable debug", "turn on debug"]):
                return self.utils.execute_command(command)
            elif any(word in command_lower for word in ["disable debug", "turn off debug"]):
                return self.utils.execute_command(command)
            elif any(word in command_lower for word in ["errors", "show errors"]):
                return self.utils.execute_command(command)
        else:
            # Use AI-driven command interpretation
            interpretation = self.ai_interpret_command(command)
            
            if interpretation["type"] == "browser":
                return self.browser_handler.execute_command(command)
            elif interpretation["type"] == "file":
                return self._handle_file_command(interpretation["operation"], interpretation.get("filename"), interpretation.get("content"), interpretation.get("pattern"))
            elif interpretation["type"] == "system":
                return self.system_commands.execute_command(command)
            elif interpretation["type"] == "language":
                return self.multilingual_commands.execute_command(command)
            elif interpretation["type"] == "utility":
                return self.utils.execute_command(command)
                
        return {"status": "error", "message": "Unknown command"}
        
    def _handle_file_command(self, operation: str, filename: str = None, content: str = None, pattern: str = None) -> Dict[str, Any]:
        """Handle file operations."""
        try:
            if operation == "create":
                # Extract filename from content if not provided
                if not filename and content:
                    filename = content.split(" ")[-1]
                if not filename:
                    return {"status": "error", "message": "No filename specified"}
                    
                with open(filename, 'w') as f:
                    f.write("")
                return {"status": "success", "filename": filename, "message": f"File {filename} created successfully"}
                
            elif operation == "read":
                if not filename:
                    return {"status": "error", "message": "No filename specified"}
                    
                with open(filename, 'r') as f:
                    content = f.read()
                return {"status": "success", "filename": filename, "content": content}
                
            elif operation == "write":
                if not filename:
                    return {"status": "error", "message": "No filename specified"}
                if not content:
                    return {"status": "error", "message": "No content specified"}
                    
                with open(filename, 'w') as f:
                    f.write(content)
                return {"status": "success", "filename": filename, "message": f"File {filename} written successfully"}
                
            elif operation == "append":
                if not filename:
                    return {"status": "error", "message": "No filename specified"}
                if not content:
                    return {"status": "error", "message": "No content specified"}
                    
                with open(filename, 'a') as f:
                    f.write(content)
                return {"status": "success", "filename": filename, "message": f"Content appended to {filename} successfully"}
                
            elif operation == "delete":
                if not filename:
                    return {"status": "error", "message": "No filename specified"}
                    
                import os
                if not os.path.exists(filename):
                    return {"status": "error", "message": f"File {filename} does not exist"}
                    
                os.remove(filename)
                return {"status": "success", "filename": filename, "message": f"File {filename} deleted successfully"}
                
            elif operation == "list":
                import os
                files = os.listdir('.')
                return {"status": "success", "files": files}
                
            elif operation == "search":
                if not pattern:
                    return {"status": "error", "message": "No search pattern specified"}
                    
                import os
                import fnmatch
                files = [f for f in os.listdir('.') if fnmatch.fnmatch(f, pattern)]
                return {"status": "success", "pattern": pattern, "files": files}
                
        except Exception as e:
            self.utils.log_error(str(e))
            return {"status": "error", "message": str(e)}
            
    def get_command_history(self) -> List[str]:
        """Get command history."""
        return self.command_history
        
    def get_current_command(self) -> Optional[str]:
        """Get current command."""
        return self.current_command
        
    def get_command_queue(self) -> List[str]:
        """Get command queue."""
        return self.command_queue
        
    def get_command_results(self) -> Dict[str, Any]:
        """Get command results."""
        return self.command_results 