import re
from typing import Dict, Optional, Any, Union, List
import logging
from uaibot.core.system_commands import SystemCommands
from uaibot.core.multilingual_commands import MultilingualCommands
from uaibot.core.utils import Utils
from uaibot.core.browser_handler import BrowserHandler
from uaibot.core.browser_interaction import BrowserInteractionHandler
from uaibot.core.memory_handler import MemoryHandler
from uaibot.core.browser_handler import BrowserAutomationHandler
import pyautogui
import time

logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self, use_regex: bool = True, fast_mode: bool = False):
        self.use_regex = use_regex
        self.fast_mode = fast_mode
        self.system_commands = SystemCommands()
        self.multilingual_commands = MultilingualCommands()
        self.utils = Utils()
        self.browser_handler = BrowserHandler()
        self.browser_interaction = BrowserInteractionHandler()
        self.memory = MemoryHandler()
        self.browser_automation = BrowserAutomationHandler()
        
        # Command history
        self.command_history = []
        self.current_command = None
        self.command_queue = []
        self.command_results = {}
        
    def ai_interpret_command(self, command: str) -> Dict[str, Any]:
        """Interpret commands using AI-driven logic."""
        command_lower = command.lower()
        command_stripped = command.strip()

        # Split command into sequential parts
        sequential_parts = []
        current_part = []
        
        # Common conjunctions and action separators
        separators = ["and", "then", "after", "next", "followed by", "subsequently"]
        
        # Split the command into words
        words = command_lower.split()
        
        for word in words:
            if word in separators:
                if current_part:
                    sequential_parts.append(" ".join(current_part))
                    current_part = []
            else:
                current_part.append(word)
        
        if current_part:
            sequential_parts.append(" ".join(current_part))
            
        # If we have multiple parts, return a sequence command
        if len(sequential_parts) > 1:
            return {
                "type": "sequence",
                "operations": [self._interpret_single_command(part) for part in sequential_parts]
            }
            
        # Otherwise, interpret as a single command
        return self._interpret_single_command(command)
        
    def _interpret_single_command(self, command: str) -> Dict[str, Any]:
        """Interpret a single command part."""
        command_lower = command.lower()

        # Browser search
        if any(word in command_lower for word in ["search", "look for", "find", "query", "look up", "google", "where is", "what is", "who is", "tell me about"]):
            return {"type": "browser", "operation": "search", "query": command}

        # Click middle link
        if "click the middle link" in command_lower or "click middle link" in command_lower:
            return {"type": "browser_interaction", "operation": "click_middle_link"}

        # Focus browser
        if "focus" in command_lower and "browser" in command_lower or "more focused on the text" in command_lower:
            return {"type": "browser_interaction", "operation": "focus_browser"}

        # Set volume
        if "volume" in command_lower:
            import re
            match = re.search(r'(\d+)%', command_lower)
            volume = int(match.group(1)) if match else 80
            return {"type": "browser_interaction", "operation": "set_volume", "volume": volume}

        # Go to YouTube in Safari
        if "safari" in command_lower and "youtube" in command_lower:
            return {"type": "browser_interaction", "operation": "open_url", "browser": "safari", "url": "https://www.youtube.com"}

        # Search in current browser (contextual)
        if "in there search for" in command_lower:
            query = command_lower.split("in there search for", 1)[-1].strip()
            return {"type": "browser", "operation": "search", "query": query}

        # Play and cast to TV
        if "play" in command_lower and "cast" in command_lower and "tv" in command_lower:
            return {"type": "browser_interaction", "operation": "play_and_cast", "query": command}

        # Check for browser commands
        browser_indicators = [
            # Question formats
            "what's", "what are",
            "when is", "why is", "which is",
            
            # Polite requests
            "can you find", "could you search", "please search", "would you search",
            "i want to know", "i need to know", "show me",
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
            
        # Open Chrome
        if "open" in command_lower and "chrome" in command_lower:
            return {"type": "browser_interaction", "operation": "open_browser", "browser": "chrome"}

        # In main bar write
        if command.startswith("in main bar write"):
            text = command.replace("in main bar write", "").strip()
            return {
                "type": "browser_interaction",
                "operation": "type_in_address_bar",
                "text": text
            }

        # In the same page search bar write Kuwait
        if "in the same page search bar write" in command_lower:
            text = command_lower.split("in the same page search bar write", 1)[-1].strip()
            return {"type": "browser_interaction", "operation": "type_in_search_bar", "text": text}

        # On same page hit enter
        if "on same page hit enter" in command_lower:
            return {"type": "browser_interaction", "operation": "press_enter"}

        # Move mouse to that chrome you just opened
        if command.startswith("move mouse to that chrome you just opened"):
            return {
                "type": "browser_interaction",
                "operation": "move_mouse_to_last_chrome"
            }

        return {"type": "error", "message": "Unknown command"}
        
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
        """Execute the interpreted command."""
        try:
            # Store command in history
            self.command_history.append(command)
            self.current_command = command
            
            # Interpret the command
            interpretation = self.ai_interpret_command(command)
            
            # Handle sequence commands
            if interpretation["type"] == "sequence":
                results = []
                for operation in interpretation["operations"]:
                    result = self._execute_single_operation(operation)
                    results.append(result)
                    # If any operation fails, stop the sequence
                    if result.get("status") == "error":
                        break
                return {
                    "status": "success" if all(r.get("status") != "error" for r in results) else "error",
                    "results": results
                }
            
            # Handle single operation
            return self._execute_single_operation(interpretation)
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def _execute_single_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single operation."""
        try:
            if operation["type"] == "browser":
                if operation["operation"] == "search":
                    # Use 'query' if present, fallback to 'command' for compatibility
                    search_query = operation.get("query", operation.get("command"))
                    # Use perform_search instead of execute_command
                    # Default to DuckDuckGo for now
                    url = "https://duckduckgo.com"
                    result_message = self.browser_handler.perform_search(url, search_query)
                    result = {
                        "status": "success" if "Opened" in result_message else "error",
                        "message": result_message,
                        "browser": None,
                        "url": url,
                        "browser_automation": True
                    }
                    logger.debug(f"Browser search result: {result}")
                    # Store the browser and search info in memory
                    browser = result.get("browser")
                    state = result.get("browser_state", {})
                    if browser:
                        self.memory.update_browser_state(browser, state)
                    url = result.get("url", "")
                    self.memory.update_search(search_query, url)
                    return result
            elif operation["type"] == "browser_interaction":
                # Use last browser from memory if not specified
                browser = operation.get("browser")
                if browser is None:
                    browser = self.memory.get_last_browser()
                if operation["operation"] == "click_middle_link":
                    result = self.browser_interaction.click_middle_link(browser)
                    logger.debug(f"Click middle link result: {result}")
                    return result
                elif operation["operation"] == "focus_browser":
                    result = self.browser_interaction.focus_browser(browser)
                    logger.debug(f"Focus browser result: {result}")
                    return result
                elif operation["operation"] == "set_volume":
                    result = self.browser_interaction.set_volume(operation["volume"])
                    logger.debug(f"Set volume result: {result}")
                    return result
                elif operation["operation"] == "play_and_cast":
                    result = self.browser_interaction.play_media(operation.get("media"))
                    logger.debug(f"Play media result: {result}")
                    return result
                elif operation["operation"] == "open_url":
                    browser = operation.get("browser")
                    url = operation.get("url")
                    if browser and url:
                        result = self.browser_automation.open_browser(browser, url)
                        logger.debug(f"Open URL result: {result}")
                        return {"status": "success", "message": result}
                    else:
                        return {"status": "error", "message": "Missing browser or URL for open_url operation"}
                elif operation["operation"] == "open_browser":
                    browser = operation.get("browser")
                    if browser:
                        result = self.browser_automation.open_browser(browser, "https://www.google.com")
                        logger.debug(f"Open browser result: {result}")
                        return {"status": "success", "message": result}
                    else:
                        return {"status": "error", "message": "Missing browser for open_browser operation"}
                elif operation["operation"] == "type_in_address_bar":
                    text = operation.get("text")
                    if text:
                        # Check if we have last_window_details and activate the window
                        if self.browser_automation.last_window_details:
                            window = self.browser_automation.last_window_details
                            self.pyautogui.moveTo(window["left"] + window["width"] // 2, window["top"] + 10)
                            self.pyautogui.click()
                            time.sleep(0.2)
                        pyautogui.hotkey('ctrl', 'l')  # Focus address bar
                        time.sleep(0.2)
                        pyautogui.typewrite(text)
                        logger.debug(f"Typed in address bar: {text}")
                        return {"status": "success", "message": f"Typed {text} in address bar"}
                    else:
                        return {"status": "error", "message": "Missing text for type_in_address_bar operation"}
                elif operation["operation"] == "type_in_search_bar":
                    text = operation.get("text")
                    if text:
                        # Check if we have last_window_details and activate the window
                        if self.browser_automation.last_window_details:
                            window = self.browser_automation.last_window_details
                            self.pyautogui.moveTo(window["left"] + window["width"] // 2, window["top"] + 10)
                            self.pyautogui.click()
                            time.sleep(0.2)
                        pyautogui.hotkey('ctrl', 'l')  # Focus search bar
                        time.sleep(0.2)
                        pyautogui.typewrite(text)
                        logger.debug(f"Typed in search bar: {text}")
                        return {"status": "success", "message": f"Typed {text} in search bar"}
                    else:
                        return {"status": "error", "message": "Missing text for type_in_search_bar operation"}
                elif operation["operation"] == "press_enter":
                    pyautogui.press('enter')
                    logger.debug("Pressed Enter key")
                    return {"status": "success", "message": "Pressed Enter key"}
            elif operation["type"] == "file":
                return self._handle_file_command(
                    operation["operation"],
                    operation.get("filename"),
                    operation.get("content"),
                    operation.get("pattern")
                )
            elif operation["type"] == "system":
                return self.system_commands.execute_command(operation["operation"])
            elif operation["type"] == "language":
                return self.multilingual_commands.execute_command(
                    operation["operation"],
                    operation.get("text"),
                    operation.get("language")
                )
            elif operation["type"] == "utility":
                return self.utils.execute_command(operation["operation"])
            elif operation["type"] == "error":
                return {"status": "error", "message": operation["message"]}
            elif operation["type"] == "move_mouse_to_last_chrome":
                if self.browser_handler.last_window_details:
                    window = self.browser_handler.last_window_details
                    self.browser_handler.pyautogui.moveTo(window["left"] + window["width"] // 2, window["top"] + window["height"] // 2)
                    logger.debug("Moved mouse to last opened Chrome window")
                    return {"status": "success", "message": "Moved mouse to last opened Chrome window"}
                else:
                    logger.error("No last window details available")
                    return {"status": "error", "message": "No last window details available"}
            return {"status": "error", "message": "Unknown operation type"}
        except Exception as e:
            logger.error(f"Error executing operation: {str(e)}")
            return {"status": "error", "message": str(e)}
        
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