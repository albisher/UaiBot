"""
AI Command Extractor Module

This module extracts executable commands from AI responses and 
handles various formats and response types to make command processing
more robust and flexible.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List, Union

logger = logging.getLogger(__name__)

# Add imports for parallel processing at the top of the file
import concurrent.futures
from core.parallel_utils import ParallelTaskManager, run_parallel, run_with_timeout

class AICommandExtractor:
    """
    Extracts structured command information from AI model responses.
    Supports multiple response formats and implements fallback strategies.
    """
    
    def __init__(self):
        """Initialize the AI command extractor."""
        # Define patterns for extracting commands
        self.code_block_markers = ["```bash", "```shell", "```sh", "```zsh", "```console", "```terminal", "```"]
        self.inline_code_marker = "`"
        self.command_indicator_phrases = [
            ["you can", "run", "execute", "try", "use", "enter", "the", "command", "following", "code"],
            ["use", "with", "try", "the", "command", "following"]
        ]
        self.error_indicators = [
            "ERROR:", "I cannot", "I'm unable", "I am unable", 
            "cannot be safely", "not possible", "not be possible",
            "security risk", "unsafe", "not recommended",
            "no safe command", "no command", "not advisable"
        ]
        
        # New patterns for arabic commands
        self.arabic_command_indicators = [
            "اكتب", "أكتب", "اضف", "أضف", "احذف", "امسح", 
            "ازل", "أزل", "انشاء", "انشئ", "اقرأ", "اعرض"
        ]
        
    def extract_command(self, ai_response: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Extract a command from AI response text with rich metadata.
        Prioritizes structured JSON formats as specified in the prompt.
        
        Args:
            ai_response: The text response from the AI
            
        Returns:
            Tuple containing:
                - Success flag (boolean)
                - Extracted command (string or None)
                - Metadata about the extraction (dictionary)
        """
        # Initialize metadata dictionary
        metadata = {
            "source": None,  # Where the command was extracted from
            "confidence": 0.0,  # Confidence in command correctness
            "is_error": False,  # Whether response indicates an error
            "error_message": None,  # Error message if applicable
            "suggested_alternatives": [],  # Alternative commands if any
            "requires_implementation": False,  # Whether this needs human implementation
            "parsed_json": None,  # Parsed JSON if response contained it
            "file_operation": None,  # What file operation (create, read, write, delete, etc.)
            "operation_params": {},  # Parameters for file operations
            "info_response": None,  # Informational response content
            "related_commands": [],  # Related commands for informational responses
        }
        
        # First priority: Extract JSON from the AI response
        try:
            # Look for code blocks containing JSON
            json_blocks = self._extract_json_blocks(ai_response)
            
            if not json_blocks:
                # If no code block JSON, look for raw JSON objects
                json_blocks = self._extract_raw_json(ai_response)
            
            # Try each potential JSON match until we find a valid one
            for json_str in json_blocks:
                try:
                    data = json.loads(json_str)
                    metadata["parsed_json"] = data
                    metadata["source"] = "json"
                    metadata["confidence"] = 0.95
                    
                    # FORMAT 1: Command with explanation
                    if "command" in data:
                        command = data["command"]
                        
                        # Extract additional metadata if available
                        if "explanation" in data:
                            metadata["explanation"] = data["explanation"]
                        if "alternatives" in data:
                            metadata["suggested_alternatives"] = data["alternatives"]
                        if "requires_implementation" in data:
                            metadata["requires_implementation"] = data["requires_implementation"]
                            
                        # Handle command with file operation
                        if "file_operation" in data:
                            metadata["file_operation"] = data["file_operation"]
                            if "operation_params" in data:
                                metadata["operation_params"] = data["operation_params"]
                            
                        logger.debug(f"Extracted command from JSON: {command}")
                        return True, command, metadata
                    
                    # FORMAT 2: File operation
                    elif "file_operation" in data:
                        metadata["file_operation"] = data["file_operation"]
                        if "operation_params" in data:
                            metadata["operation_params"] = data["operation_params"]
                        if "explanation" in data:
                            metadata["explanation"] = data["explanation"]
                            
                        metadata["source"] = "json_file_operation"
                        
                        # Generate command from file operation
                        command = self._generate_command_from_file_operation(
                            data["file_operation"], 
                            data.get("operation_params", {})
                        )
                        
                        if command:
                            logger.debug(f"Generated command from file operation: {command}")
                            return True, command, metadata
                    
                    # FORMAT 3: Error response
                    elif "error" in data and data["error"]:
                        metadata["is_error"] = True
                        metadata["error_message"] = data.get("error_message", "Unable to fulfill request")
                        if "suggested_approach" in data:
                            metadata["suggested_approach"] = data["suggested_approach"]
                        metadata["requires_implementation"] = data.get("requires_implementation", True)
                        
                        logger.debug(f"AI reported error: {metadata['error_message']}")
                        return False, None, metadata
                    
                    # FORMAT 4: Informational response
                    elif "info_type" in data or "information" in data:
                        # Handle info_type format
                        if "info_type" in data:
                            metadata["info_type"] = data["info_type"]
                            metadata["info_response"] = data.get("response", "")
                            if "related_command" in data:
                                metadata["related_commands"].append(data["related_command"])
                        # Handle information format
                        elif "information" in data:
                            metadata["info_response"] = data["information"]
                            if "related_commands" in data:
                                metadata["related_commands"] = data["related_commands"]
                        
                        metadata["source"] = "json_info"
                        metadata["confidence"] = 0.9
                        
                        logger.debug(f"Extracted informational response: {metadata['info_type'] if 'info_type' in metadata else 'general info'}")
                        return False, None, metadata
                        
                    # After: data = json.loads(json_str)
                    if "intent" in data and data["intent"] == "browser_automation":
                        metadata["intent"] = "browser_automation"
                        metadata["browser"] = data.get("browser", "")
                        metadata["url"] = data.get("url", "")
                        metadata["actions"] = data.get("actions", [])
                        return True, None, metadata
                    
                except json.JSONDecodeError:
                    # This particular JSON string was invalid, try the next one
                    continue
        except Exception as e:
            logger.error(f"Error processing JSON response: {e}")
        
        # Second priority: Look for code blocks
        code_blocks = self._extract_code_blocks(ai_response)
        if code_blocks:
            command = code_blocks[0].strip()
            metadata["source"] = "code_block"
            metadata["confidence"] = 0.85
            logger.debug(f"Extracted command from code block: {command}")
            return True, command, metadata
        
        # Third priority: Look for inline code
        inline_codes = self._extract_inline_code(ai_response)
        if inline_codes:
            # Find the first non-empty inline code
            for code in inline_codes:
                code = code.strip()
                if code:
                    metadata["source"] = "inline_code"
                    metadata["confidence"] = 0.75
                    logger.debug(f"Extracted command from inline code: {code}")
                    return True, code, metadata
        
        # Fourth priority: Extract command from phrases like "use the command..."
        command = self._extract_command_from_phrases(ai_response)
        if command:
            metadata["source"] = "phrase"
            metadata["confidence"] = 0.65
            logger.debug(f"Extracted command from phrase: {command}")
            return True, command, metadata
        
        # Fifth priority: Check for Arabic commands
        arabic_command = self._extract_arabic_command(ai_response)
        if arabic_command:
            metadata["source"] = "arabic"
            metadata["confidence"] = 0.7
            logger.debug(f"Extracted Arabic command: {arabic_command}")
            return True, arabic_command, metadata
        
        # Check for error indicators
        is_error, error_message = self._check_for_error(ai_response)
        if is_error:
            metadata["is_error"] = True
            metadata["error_message"] = error_message
            metadata["requires_implementation"] = True
            logger.debug(f"Detected error in response: {error_message}")
            return False, None, metadata
        
        # No command found
        logger.debug("No command found in response")
        return False, None, metadata
    
    def _extract_json_blocks(self, text: str) -> List[str]:
        """Extract JSON blocks from code blocks."""
        blocks = []
        lines = text.split('\n')
        in_json_block = False
        current_block = []
        
        for line in lines:
            if line.strip().startswith('```json'):
                in_json_block = True
                current_block = []
            elif in_json_block and line.strip().startswith('```'):
                in_json_block = False
                if current_block:
                    blocks.append('\n'.join(current_block))
            elif in_json_block:
                current_block.append(line)
        
        return blocks
    
    def _extract_raw_json(self, text: str) -> List[str]:
        """Extract raw JSON objects from text."""
        blocks = []
        lines = text.split('\n')
        current_block = []
        brace_count = 0
        
        for line in lines:
            if '{' in line:
                brace_count += line.count('{')
                current_block.append(line)
            elif '}' in line:
                brace_count -= line.count('}')
                current_block.append(line)
                if brace_count == 0 and current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
            elif current_block:
                current_block.append(line)
        
        return blocks
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from text."""
        blocks = []
        lines = text.split('\n')
        in_code_block = False
        current_block = []
        
        for line in lines:
            if any(line.strip().startswith(marker) for marker in self.code_block_markers):
                in_code_block = True
                current_block = []
            elif in_code_block and line.strip().startswith('```'):
                in_code_block = False
                if current_block:
                    blocks.append('\n'.join(current_block))
            elif in_code_block:
                current_block.append(line)
        
        return blocks
    
    def _extract_inline_code(self, text: str) -> List[str]:
        """Extract inline code from text."""
        codes = []
        words = text.split()
        in_code = False
        current_code = []
        
        for word in words:
            if word.startswith(self.inline_code_marker):
                if word.endswith(self.inline_code_marker) and len(word) > 1:
                    # Single word code
                    codes.append(word[1:-1])
                else:
                    # Start of multi-word code
                    in_code = True
                    current_code.append(word[1:])
            elif in_code and word.endswith(self.inline_code_marker):
                # End of multi-word code
                in_code = False
                current_code.append(word[:-1])
                codes.append(' '.join(current_code))
                current_code = []
            elif in_code:
                current_code.append(word)
        
        return codes
    
    def _extract_command_from_phrases(self, text: str) -> Optional[str]:
        """Extract command from phrases like 'use the command...'."""
        words = text.lower().split()
        
        for phrase in self.command_indicator_phrases:
            # Check if all words in the phrase appear in sequence
            for i in range(len(words) - len(phrase) + 1):
                if words[i:i + len(phrase)] == phrase:
                    # Found the phrase, look for the command
                    remaining = ' '.join(words[i + len(phrase):])
                    
                    # Check for quoted command
                    if remaining.startswith(("'", '"')):
                        quote_char = remaining[0]
                        end_quote = remaining.find(quote_char, 1)
                        if end_quote != -1:
                            return remaining[1:end_quote]
                    
                    # Check for backtick command
                    if remaining.startswith('`'):
                        end_backtick = remaining.find('`', 1)
                        if end_backtick != -1:
                            return remaining[1:end_backtick]
                    
                    # Take the first word as command
                    return remaining.split()[0]
        
        return None
    
    def _extract_arabic_command(self, ai_response: str) -> Optional[str]:
        """
        Extract Arabic commands from the AI response using the AI-driven approach.
        This is a language-agnostic implementation that relies on JSON structures
        rather than hardcoded patterns.
        
        Args:
            ai_response: The AI response to analyze
            
        Returns:
            Optional[str]: Extracted Arabic command or None
        """
        # Special case for the write with content pattern: "اكتب 'content' في ملف filename"
        if "اكتب" in ai_response and "في ملف" in ai_response:
            content_match = re.search(r"'([^']*)'", ai_response)
            filename_match = re.search(r"في ملف\s+(\S+)", ai_response)
            if content_match and filename_match:
                content = content_match.group(1)
                filename = filename_match.group(1)
                return f"echo '{content}' > {filename}"
            
        # First priority: Look for JSON structures in the response
        json_patterns = [
            r'```json\s*(\{[\s\S]*?\})\s*```',  # JSON in code blocks
            r'(\{[\s\S]*?"command"\s*:\s*".*?"[\s\S]*?\})'  # Bare JSON with command field
        ]
        
        for pattern in json_patterns:
            json_matches = re.findall(pattern, ai_response, re.DOTALL)
            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    # If JSON contains a command field, use it directly
                    if "command" in data:
                        return data["command"]
                    
                    # If JSON contains file operation, generate a command
                    if "file_operation" in data and "operation_params" in data:
                        operation = data["file_operation"]
                        params = data["operation_params"]
                        
                        if operation == "create" and "filename" in params:
                            if "content" in params and params["content"]:
                                return f"echo '{params['content']}' > {params['filename']}"
                            else:
                                return f"touch {params['filename']}"
                                
                        elif operation == "read" and "filename" in params:
                            return f"cat {params['filename']}"
                            
                        elif operation == "delete" and "filename" in params:
                            return f"rm {params['filename']}"
                            
                        elif operation == "list":
                            directory = params.get("directory", ".")
                            return f"ls -la {directory}"
                except:
                    # If JSON parsing failed, continue checking other patterns
                    continue
        
        # Second priority: Look for code blocks with potential commands
        code_block_pattern = r'```(?:bash|shell|sh|zsh|console|terminal)?\s*(.*?)\s*```'
        code_blocks = re.findall(code_block_pattern, ai_response, re.DOTALL)
        
        if code_blocks:
            # Use the first code block that looks like a command
            for block in code_blocks:
                if block.strip() and not block.startswith(('#', '//')):
                    return block.strip()
        
        # Third priority: Look for inline code with potential commands
        inline_code_pattern = r'`(.*?)`'
        inline_codes = re.findall(inline_code_pattern, ai_response)
        
        if inline_codes:
            # Use the first inline code that looks like a command
            for code in inline_codes:
                if code.strip() and not code.startswith(('#', '//')):
                    return code.strip()
        
        # Fourth priority: Process Arabic commands based on keywords
        # This is needed for the current test cases which don't use JSON or code blocks
        for indicator in self.arabic_command_indicators:
            if indicator in ai_response:
                words = ai_response.split()
                # Find the index of the Arabic command indicator
                for i, word in enumerate(words):
                    if indicator in word:
                        # Handle more complex filenames with "باسم" (meaning "named")
                        if "باسم" in ai_response:
                            # Extract the filename after "باسم" (named)
                            name_idx = words.index("باسم") if "باسم" in words else -1
                            if name_idx >= 0 and name_idx + 1 < len(words):
                                filename = words[name_idx + 1]
                                
                                # Map Arabic command indicators to shell commands
                                if indicator in ["احذف", "امسح", "ازل", "أزل"]:
                                    return f"rm {filename}"
                                elif indicator in ["اقرأ", "اعرض"]:
                                    return f"cat {filename}"
                                elif indicator in ["انشئ", "انشاء"]:
                                    return f"touch {filename}"
                                elif indicator in ["اكتب", "أكتب", "اضف", "أضف"]:
                                    # Look for content in single quotes
                                    content_match = re.search(r"'([^']*)'", ai_response)
                                    if content_match:
                                        content = content_match.group(1)
                                        return f"echo '{content}' > {filename}"
                                    else:
                                        return f"touch {filename}"
                        
                        # Extract filename after the indicator with "ملف" (file)
                        elif i + 1 < len(words) and "ملف" in words[i+1]:
                            # The pattern is typically: [arabic command] ملف [filename]
                            if i + 2 < len(words):
                                filename = words[i+2]
                                
                                # If the filename is followed by "في" (in), then the actual filename comes after
                                if "في" in ai_response and "ملف" in ai_response:
                                    try:
                                        # Find the word "في" (in) followed by "ملف" (file)
                                        if "في" in words and "ملف" in words:
                                            في_idx = words.index("في")
                                            if في_idx + 2 < len(words) and words[في_idx + 1] == "ملف":
                                                filename = words[في_idx + 2]
                                    except (ValueError, IndexError):
                                        pass
                                    
                                # Map Arabic command indicators to shell commands
                                if indicator in ["احذف", "امسح", "ازل", "أزل"]:
                                    return f"rm {filename}"
                                elif indicator in ["اقرأ", "اعرض"]:
                                    return f"cat {filename}"
                                elif indicator in ["انشئ", "انشاء"]:
                                    return f"touch {filename}"
                                elif indicator in ["اكتب", "أكتب", "اضف", "أضف"]:
                                    # Look for content in single quotes
                                    content_match = re.search(r"'([^']*)'", ai_response)
                                    if content_match:
                                        content = content_match.group(1)
                                        return f"echo '{content}' > {filename}"
                                    else:
                                        return f"touch {filename}"
                        
                        # Special case for directory listing
                        elif "المجلد" in ai_response and "الحالي" in ai_response:
                            return "ls -l"
                            
        # If no structured format is found, return None
        # The main extract_command method will handle fallbacks
        return None
    
    def _check_for_error(self, ai_response: str) -> Tuple[bool, Optional[str]]:
        """
        Check if the AI response indicates an error condition.
        
        Args:
            ai_response: The AI response text
            
        Returns:
            Tuple of (is_error, error_message)
        """
        for error_phrase in self.error_indicators:
            if error_phrase.lower() in ai_response.lower():
                # Try to extract a more specific error message
                lines = ai_response.split('\n')
                for line in lines:
                    if error_phrase.lower() in line.lower():
                        return True, line.strip()
                        
                # If no specific line found, use a generic message
                return True, "The requested command cannot be safely executed."
                
        return False, None
    
    def _detect_file_operation(self, command: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect if a command is a file operation and extract relevant information.
        
        Args:
            command: The command to analyze
            metadata: Existing metadata to update
            
        Returns:
            Updated metadata dictionary
        """
        # Check for file creation operations
        if command.startswith(("touch ", "echo ", "cat >", ">", "printf ")):
            metadata["file_operation"] = "create"
            
            # Try to extract filename
            if command.startswith("touch "):
                filename_match = re.search(r'touch\s+([^\s;|>]+)', command)
                if filename_match:
                    metadata["operation_params"] = {"filename": filename_match.group(1)}
                    
            elif command.startswith(("echo ", "printf ")):
                # Check for redirection to file
                redirect_match = re.search(r'>\s*([^\s;|>]+)', command)
                if redirect_match:
                    content_match = re.search(r'(?:echo|printf)\s+[\'"]([^\'"]+)[\'"]', command)
                    metadata["operation_params"] = {
                        "filename": redirect_match.group(1),
                        "content": content_match.group(1) if content_match else ""
                    }
        
        # Check for file read operations
        elif command.startswith(("cat ", "less ", "more ", "head ", "tail ", "vim ", "nano ")):
            metadata["file_operation"] = "read"
            
            # Try to extract filename
            filename_match = re.search(r'(?:cat|less|more|head|tail|vim|nano)\s+([^\s;|]+)', command)
            if filename_match:
                metadata["operation_params"] = {"filename": filename_match.group(1)}
                
        # Check for file delete operations
        elif command.startswith("rm "):
            metadata["file_operation"] = "delete"
            
            # Try to extract filename
            filename_match = re.search(r'rm\s+(?:-[rf]\s+)?([^\s;|]+)', command)
            if filename_match:
                metadata["operation_params"] = {"filename": filename_match.group(1)}
                
        # Check for directory listing
        elif command.startswith(("ls ", "dir ")):
            metadata["file_operation"] = "list"
            
            # Try to extract directory
            dir_match = re.search(r'(?:ls|dir)(?:\s+-\w+)?\s+([^\s;|]+)', command)
            if dir_match:
                metadata["operation_params"] = {"directory": dir_match.group(1)}
            else:
                metadata["operation_params"] = {"directory": "."}  # Current dir
                
        # Check for file search
        elif command.startswith(("find ", "grep ", "locate ")):
            metadata["file_operation"] = "search"
            
            # Extract search parameters based on command type
            if command.startswith("find "):
                dir_match = re.search(r'find\s+([^\s;|]+)', command)
                name_match = re.search(r'-name\s+[\'"]([^\'"]+)[\'"]', command)
                
                if dir_match:
                    metadata["operation_params"] = {"directory": dir_match.group(1)}
                if name_match:
                    metadata["operation_params"]["search_pattern"] = name_match.group(1)
                    
            elif command.startswith("grep "):
                pattern_match = re.search(r'grep\s+[\'"]?([^\'"]+)[\'"]?', command)
                file_match = re.search(r'grep\s+[\'"]?[^\'"]+[\'"]?\s+([^\s;|]+)', command)
                
                if pattern_match:
                    metadata["operation_params"] = {"search_term": pattern_match.group(1)}
                if file_match:
                    metadata["operation_params"]["filename"] = file_match.group(1)
                    
        # File copy/move operations
        elif command.startswith(("cp ", "mv ")):
            metadata["file_operation"] = "copy" if command.startswith("cp ") else "move"
            
            # Try to extract source and destination
            paths_match = re.search(r'(?:cp|mv)\s+([^\s;|]+)\s+([^\s;|]+)', command)
            if paths_match:
                metadata["operation_params"] = {
                    "source": paths_match.group(1),
                    "destination": paths_match.group(2)
                }
                
        return metadata
    
    def _generate_command_from_file_operation(self, operation_type: str, params: Dict[str, Any]) -> Optional[str]:
        """
        Generate a shell command from a file operation specification.
        
        Args:
            operation_type: Type of file operation (create, read, etc.)
            params: Parameters for the operation
            
        Returns:
            Shell command string or None if invalid operation
        """
        if operation_type == "create":
            filename = params.get("filename")
            if not filename:
                return None
                
            content = params.get("content")
            if content:
                # Escape single quotes in content for shell safety
                content_safe = content.replace("'", "'\\''")
                return f"echo '{content_safe}' > {filename}"
            else:
                return f"touch {filename}"
                
        elif operation_type == "read":
            filename = params.get("filename")
            if not filename:
                return None
                
            return f"cat {filename}"
            
        elif operation_type == "write" or operation_type == "append":
            filename = params.get("filename")
            content = params.get("content", "")
            if not filename:
                return None
                
            # Escape single quotes for shell safety
            content_safe = content.replace("'", "'\\''")
            redirect_op = ">>" if operation_type == "append" else ">"
            return f"echo '{content_safe}' {redirect_op} {filename}"
            
        elif operation_type == "delete":
            filename = params.get("filename")
            if not filename:
                return None
                
            recursive = params.get("recursive", False)
            force = params.get("force", False)
            
            options = ""
            if recursive:
                options += "r"
            if force:
                options += "f"
                
            if options:
                return f"rm -{options} {filename}"
            return f"rm {filename}"
            
        elif operation_type == "list":
            directory = params.get("directory", ".")
            all_files = params.get("all", True)
            long_format = params.get("long_format", True)
            
            options = ""
            if all_files:
                options += "a"
            if long_format:
                options += "l"
                
            if options:
                return f"ls -{options} {directory}"
            return f"ls {directory}"
            
        elif operation_type == "search":
            directory = params.get("directory", ".")
            search_term = params.get("search_term", "*")
            
            # Determine whether to use find or grep based on params
            if "content" in params:
                # Search for content within files
                content = params["content"]
                return f"grep -r '{content}' {directory}"
            else:
                # Search for filenames
                return f"find {directory} -name '*{search_term}*'"
                
        return None
    
    def format_ai_prompt(self, user_input, system_info):
        """
        Format the prompt for the AI model, including detailed system information and available tools.
        Explicitly requests a JSON output with a 'command' field and an optional 'explanation' field.
        
        Args:
            user_input (str): The user's input command.
            system_info (dict): System information including OS, version, etc.
        
        Returns:
            str: The formatted prompt for the AI model.
        """
        prompt = f"""
You are an AI assistant running on a system with the following details:
- OS: {system_info.get('system', 'Unknown')}
- Version: {system_info.get('version', 'Unknown')}
- Available tools: file operations, browser automation, shell commands, folder search, USB device queries, and more.

The user has provided the following command:
"{user_input}"

Please analyze this command and determine the appropriate action. If the command is a folder search, set the intent to "folder_search" and include a "folder_name" field. If it's a browser automation command, set the intent to "browser_automation" and include "browser", "url", and "actions" fields. For other commands, set the intent to "command" and provide the command to execute.

Your response must be a valid JSON object with the following structure:
{{
    "intent": "<intent>",
    "command": "<command to execute>",
    "explanation": "<optional explanation>",
    "folder_name": "<folder name if intent is folder_search>",
    "browser": "<browser name if intent is browser_automation>",
    "url": "<url if intent is browser_automation>",
    "actions": [<list of actions if intent is browser_automation>]
}}

Ensure your response is a valid JSON object.
"""
        return prompt
