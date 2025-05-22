"""
Command Processor Module

This module handles command processing and interpretation using AI-driven logic.
"""

import re
from typing import Dict, Optional, Any, Union, List
import logging
from app.core.system_commands import SystemCommands
from app.core.multilingual_commands import MultilingualCommands
from app.core.utils import Utils
from app.core.browser_handler import BrowserHandler
from app.core.browser_interaction import BrowserInteractionHandler
from app.core.memory_handler import MemoryHandler
from app.core.browser_handler import BrowserAutomationHandler
import pyautogui
import time

logger = logging.getLogger(__name__)

class CommandProcessor:
    """
    Processes and interprets commands using AI-driven logic.
    Supports command sequences, file operations, and system commands.
    """
    
    def __init__(self, use_regex: bool = True, fast_mode: bool = False):
        """Initialize the command processor."""
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
        
        # Command type indicators
        self.command_types = {
            "file": ["create", "read", "write", "delete", "list", "search"],
            "system": ["status", "info", "monitor", "control"],
            "shell": ["execute", "run", "command"]
        }
        
        # Command separators
        self.separators = ["and", "then", "after", "next", "followed by", "subsequently"]
        
        # File operation patterns
        self.file_patterns = {
            "create": r"(?:create|make|new)\s+(?:file|document)\s+(?:named|called)?\s*['\"]?([^'\"]+)['\"]?",
            "read": r"(?:read|open|view|show)\s+(?:file|document)\s+(?:named|called)?\s*['\"]?([^'\"]+)['\"]?",
            "write": r"(?:write|save|update)\s+(?:to|in)\s+(?:file|document)\s+(?:named|called)?\s*['\"]?([^'\"]+)['\"]?",
            "delete": r"(?:delete|remove|erase)\s+(?:file|document)\s+(?:named|called)?\s*['\"]?([^'\"]+)['\"]?",
            "list": r"(?:list|show|display)\s+(?:files|documents)(?:\s+in\s+['\"]?([^'\"]+)['\"]?)?",
            "search": r"(?:search|find|look\s+for)\s+(?:in|within)\s+(?:file|document)\s+(?:named|called)?\s*['\"]?([^'\"]+)['\"]?"
        }
        
        # System command patterns
        self.system_patterns = {
            "status": r"(?:show|display|get)\s+(?:system|computer)\s+status",
            "info": r"(?:show|display|get)\s+(?:system|computer)\s+info(?:rmation)?",
            "monitor": r"(?:monitor|watch|track)\s+(?:system|computer)\s+(?:resources|performance)",
            "control": r"(?:control|manage|adjust)\s+(?:system|computer)\s+(?:settings|configuration)"
        }
        
        # Shell command patterns
        self.shell_patterns = {
            "execute": r"(?:execute|run|perform)\s+(?:command|operation)\s*['\"]?([^'\"]+)['\"]?",
            "run": r"(?:run|execute|perform)\s*['\"]?([^'\"]+)['\"]?",
            "command": r"(?:command|operation)\s*['\"]?([^'\"]+)['\"]?"
        }
    
    def ai_interpret_command(self, command: str) -> Dict[str, Any]:
        """
        Interpret commands using AI-driven logic.
        
        Args:
            command: The command to interpret
            
        Returns:
            Dictionary containing the interpreted command structure
        """
        command_lower = command.lower()
        command_stripped = command.strip()

        # Split command into sequential parts
        sequential_parts = self._split_sequential_commands(command_lower)
        
        # If we have multiple parts, return a sequence command
        if len(sequential_parts) > 1:
            return {
                "type": "sequence",
                "operations": [self._interpret_single_command(part) for part in sequential_parts]
            }
            
        # Otherwise, interpret as a single command
        return self._interpret_single_command(command)
    
    def _split_sequential_commands(self, command: str) -> List[str]:
        """
        Split a command into sequential parts based on separators.
        
        Args:
            command: The command to split
            
        Returns:
            List of command parts
        """
        parts = []
        current_part = []
        words = command.split()
        
        for word in words:
            if word in self.separators:
                if current_part:
                    parts.append(" ".join(current_part))
                    current_part = []
            else:
                current_part.append(word)
        
        if current_part:
            parts.append(" ".join(current_part))
            
        return parts
    
    def _interpret_single_command(self, command: str) -> Dict[str, Any]:
        """
        Interpret a single command.
        
        Args:
            command: The command to interpret
            
        Returns:
            Dictionary containing the interpreted command structure
        """
        command_lower = command.lower()
        
        # Check for file operations
        for operation, pattern in self.file_patterns.items():
            match = re.search(pattern, command_lower)
            if match:
                return {
                    "type": "file",
                    "operation": operation,
                    "parameters": {
                        "filename": match.group(1) if match.groups() else None
                    }
                }
        
        # Check for system commands
        for operation, pattern in self.system_patterns.items():
            if re.search(pattern, command_lower):
                return {
                    "type": "system",
                    "operation": operation,
                    "parameters": {}
                }
        
        # Check for shell commands
        for operation, pattern in self.shell_patterns.items():
            match = re.search(pattern, command_lower)
            if match:
                return {
                    "type": "shell",
                    "operation": operation,
                    "parameters": {
                        "command": match.group(1) if match.groups() else command
                    }
                }
        
        # Default to shell command if no specific type is matched
        return {
            "type": "shell",
            "operation": "execute",
            "parameters": {
                "command": command
            }
        }
    
    def _extract_command_from_ai_response(self, ai_response: str) -> str:
        """
        Extract just the command from an AI response text.
        
        Args:
            ai_response: The AI response text
            
        Returns:
            Extracted command string
        """
        # First check for code blocks - the preferred format
        code_block_pattern = r'```(?:bash|shell|zsh|sh|console|terminal)?\s*(.*?)\s*```'
        code_blocks = re.findall(code_block_pattern, ai_response, re.DOTALL)
        
        if code_blocks:
            # Use the first code block
            return code_blocks[0].strip()
            
        # Next check for backtick-wrapped commands
        backtick_pattern = r'`(.*?)`'
        backticks = re.findall(backtick_pattern, ai_response)
        
        if backticks:
            # Use the first backtick block
            return backticks[0].strip()
            
        # If there are no code blocks or backticks, use the whole response
        # but remove any explanatory text that might be present
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('#', '//', 'Note:', 'Here', 'Try')):
                return line
                
        # If we couldn't find a clear command, return the original response
        return ai_response.strip()
        
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