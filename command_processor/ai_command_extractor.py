"""
AI Command Extractor Module

This module extracts executable commands from AI responses and 
handles various formats and response types to make command processing
more robust and flexible.
"""

import re
import json
import logging
from typing import Dict, Any, Tuple, Optional, List, Union

logger = logging.getLogger(__name__)

class AICommandExtractor:
    """
    Extracts structured command information from AI model responses.
    Supports multiple response formats and implements fallback strategies.
    """
    
    def __init__(self):
        """Initialize the AI command extractor."""
        # Define patterns for extracting commands
        self.code_block_pattern = r'```(?:bash|shell|sh|zsh|console|terminal)?\s*(.*?)\s*```'
        self.inline_code_pattern = r'`(.*?)`'
        self.command_indicator_phrases = [
            r'(?:you can )?(?:run|execute|try|use|enter)(?:the)?\s+(?:command|following|code)?\s*:?\s*[`"]?([\w\s\-\.\/\*\|\>\<\&\$\[\]\{\}\(\)]+)[`"]?',
            r'(?:use|with|try)(?:the)?\s+(?:command|following)?\s*[`"]?([\w\s\-\.\/\*\|\>\<\&\$\[\]\{\}\(\)]+)[`"]?'
        ]
        self.json_pattern = r'\{[\s\S]*?"command"\s*:\s*"(.+?)"[\s\S]*?\}'
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
        }
        
        # First, check if the AI indicates an error or limitation
        for error_text in self.error_indicators:
            if error_text.lower() in ai_response.lower():
                metadata["is_error"] = True
                error_match = re.search(r'(?:ERROR|error|Error):\s*(.*?)(?:\n|$)', ai_response)
                if error_match:
                    metadata["error_message"] = error_match.group(1).strip()
                else:
                    # Try to extract a sentence containing the error
                    sentences = re.split(r'[.!?]\s+', ai_response)
                    for sentence in sentences:
                        if any(indicator.lower() in sentence.lower() for indicator in self.error_indicators):
                            metadata["error_message"] = sentence.strip()
                            break
                    
                    if not metadata["error_message"]:
                        metadata["error_message"] = "Unable to fulfill request safely"
                
                metadata["requires_implementation"] = True
                return False, None, metadata
                
        # Check if response is in JSON format
        try:
            # Try to extract JSON structure from the response
            json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```|(\{[\s\S]*"command"[\s\S]*?\})', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1) or json_match.group(2)
                data = json.loads(json_str)
                metadata["parsed_json"] = data
                
                # If it has a command field, extract it
                if "command" in data:
                    command = data["command"]
                    metadata["source"] = "json"
                    metadata["confidence"] = 0.9
                    
                    # Extract file operation information if present
                    if "file_operation" in data:
                        metadata["file_operation"] = data["file_operation"]
                        if "operation_params" in data:
                            metadata["operation_params"] = data["operation_params"]
                    
                    # Check additional metadata in JSON
                    if "requires_implementation" in data:
                        metadata["requires_implementation"] = data["requires_implementation"]
                    if "alternatives" in data:
                        metadata["suggested_alternatives"] = data["alternatives"]
                    if "explanation" in data:
                        metadata["explanation"] = data["explanation"]
                    if "error" in data and data["error"]:
                        metadata["is_error"] = True
                        metadata["error_message"] = data.get("error_message", "Unknown error")
                        return False, None, metadata
                        
                    return True, command, metadata
                
                # If it's a file operation specification but no direct command
                elif "file_operation" in data:
                    metadata["file_operation"] = data["file_operation"]
                    metadata["operation_params"] = data.get("operation_params", {})
                    metadata["source"] = "json_file_operation"
                    metadata["confidence"] = 0.85
                    
                    # Generate command based on the file operation
                    command = self._generate_command_from_file_operation(
                        data["file_operation"], 
                        data.get("operation_params", {})
                    )
                    
                    if command:
                        return True, command, metadata
                    else:
                        metadata["is_error"] = True
                        metadata["error_message"] = "Unable to generate command from file operation specification"
                        metadata["requires_implementation"] = True
                        return False, None, metadata
        except json.JSONDecodeError:
            pass  # Not valid JSON, continue with other methods
        except Exception as e:
            logger.debug(f"Error parsing JSON: {e}")
        
        # Try to extract code blocks (highest confidence)
        code_blocks = re.findall(self.code_block_pattern, ai_response, re.DOTALL)
        if code_blocks:
            command = code_blocks[0].strip()
            metadata["source"] = "code_block"
            metadata["confidence"] = 0.9
            
            # Try to determine if this is a file operation
            metadata = self._detect_file_operation(command, metadata)
            
            return True, command, metadata
            
        # Try to extract inline code (second highest confidence)
        inline_codes = re.findall(self.inline_code_pattern, ai_response)
        if inline_codes:
            # Use the longest inline code as it's more likely to be a complete command
            command = max(inline_codes, key=len).strip()
            metadata["source"] = "inline_code"
            metadata["confidence"] = 0.7
            
            # Try to determine if this is a file operation
            metadata = self._detect_file_operation(command, metadata)
            
            return True, command, metadata
            
        # Try to extract commands based on indicator phrases
        for pattern in self.command_indicator_phrases:
            matches = re.search(pattern, ai_response, re.IGNORECASE)
            if matches:
                command = matches.group(1).strip()
                metadata["source"] = "indicator_phrase"
                metadata["confidence"] = 0.5
                
                # Try to determine if this is a file operation
                metadata = self._detect_file_operation(command, metadata)
                
                return True, command, metadata
                
        # Check for Arabic commands (added support for Arabic)
        arabic_command = self._extract_arabic_command(ai_response)
        if arabic_command:
            metadata["source"] = "arabic_command"
            metadata["confidence"] = 0.6
            
            # Try to determine if this is a file operation
            metadata = self._detect_file_operation(arabic_command, metadata)
            
            return True, arabic_command, metadata
                
        # Try to extract from lines that look like commands (lowest confidence)
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            # Look for lines that start with common command prefixes
            if re.match(r'^(find|grep|ls|cat|echo|mkdir|touch|rm|cp|mv|curl|wget|tar|ssh|python|node|npm)\s+', line):
                metadata["source"] = "line_pattern"
                metadata["confidence"] = 0.3
                
                # Try to determine if this is a file operation
                metadata = self._detect_file_operation(line, metadata)
                
                return True, line, metadata
        
        # No command found, but not explicitly an error
        # This might be a general explanation or information
        return False, None, metadata
    
    def _extract_arabic_command(self, ai_response: str) -> Optional[str]:
        """
        Extract Arabic commands from the AI response.
        
        Args:
            ai_response: The AI response to analyze
            
        Returns:
            Optional[str]: Extracted Arabic command or None
        """
        # Look for Arabic command indicators
        for indicator in self.arabic_command_indicators:
            if indicator in ai_response:
                # Find the line containing the Arabic command
                lines = ai_response.split('\n')
                for line in lines:
                    if indicator in line:
                        # Try to convert to an equivalent shell command
                        # This is a simplification - a complete implementation would map Arabic commands to shell commands
                        if "انشاء" in line or "انشئ" in line or "جديد" in line:
                            # Create file command
                            match = re.search(r'(?:انشاء|انشئ|جديد)\s+(?:ملف|مجلد)?\s+([^\s]+)', line)
                            if match:
                                return f"touch {match.group(1)}"
                        elif "احذف" in line or "امسح" في line or "ازل" في line:
                            # Delete file command
                            match = re.search(r'(?:احذف|امسح|ازل|أزل)\s+(?:ملف|مجلد)?\s+([^\s]+)', line)
                            if match:
                                return f"rm {match.group(1)}"
                        elif "اقرأ" في line or "اعرض" في line or "اظهر" في line:
                            # Read file command
                            match = re.search(r'(?:اقرأ|اعرض|اظهر)\s+(?:ملف|محتوى)?\s+([^\s]+)', line)
                            if match:
                                return f"cat {match.group(1)}"
                        elif "اكتب" في line or "أكتب" في line or "اضف" في line or "أضف" في line:
                            # Write to file command
                            match = re.search(r'(?:اكتب|أكتب|اضف|أضف)\s+[\'"]?([^\'"\n]+)[\'"]?\s+(?:في|الى|إلى)\s+([^\s]+)', line)
                            if match:
                                content = match.group(1)
                                filename = match.group(2)
                                return f"echo '{content}' > {filename}"
        
        return None
        
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
                    metadata["operation_params"]["filename"] = filename_match.group(1)
            
            elif command.startswith("echo "):
                # This could be writing to a file
                filename_match = re.search(r'>\s*([^\s;|]+)', command)
                if filename_match:
                    metadata["operation_params"]["filename"] = filename_match.group(1)
                    
                    # Extract content
                    content_match = re.search(r'echo\s+[\'"]?([^\'"\n]*)[\'"]?', command)
                    if content_match:
                        metadata["operation_params"]["content"] = content_match.group(1)
        
        # Check for file reading operations
        elif command.startswith(("cat ", "less ", "more ", "head ", "tail ")):
            metadata["file_operation"] = "read"
            
            # Try to extract filename
            filename_match = re.search(r'(?:cat|less|more|head|tail)\s+([^\s;|>]+)', command)
            if filename_match:
                metadata["operation_params"]["filename"] = filename_match.group(1)
        
        # Check for file deletion operations
        elif command.startswith(("rm ", "del ", "unlink ")):
            metadata["file_operation"] = "delete"
            
            # Try to extract filename
            filename_match = re.search(r'(?:rm|del|unlink)\s+([^\s;|>]+)', command)
            if filename_match:
                metadata["operation_params"]["filename"] = filename_match.group(1)
        
        # Check for file search operations
        elif command.startswith(("find ", "grep ", "locate ")):
            metadata["file_operation"] = "search"
            
            # Try to extract search term
            if command.startswith("find "):
                search_term_match = re.search(r'-name\s+[\'"]([^\'"]+)[\'"]', command)
                if search_term_match:
                    metadata["operation_params"]["search_term"] = search_term_match.group(1)
            elif command.startswith("grep "):
                search_term_match = re.search(r'grep\s+[\'"]?([^\'"\s]+)[\'"]?', command)
                if search_term_match:
                    metadata["operation_params"]["search_term"] = search_term_match.group(1)
        
        # Check for file listing operations
        elif command.startswith(("ls ", "dir ")):
            metadata["file_operation"] = "list"
            
            # Try to extract directory
            dir_match = re.search(r'(?:ls|dir)\s+([^\s;|>-]+)', command)
            if dir_match:
                metadata["operation_params"]["directory"] = dir_match.group(1)
            else:
                metadata["operation_params"]["directory"] = "current"
        
        return metadata
        
    def _generate_command_from_file_operation(self, operation: str, params: Dict[str, Any]) -> Optional[str]:
        """
        Generate a shell command from a file operation specification.
        
        Args:
            operation: The type of file operation
            params: Parameters for the operation
            
        Returns:
            Generated shell command or None if unable to generate
        """
        if operation == "create":
            filename = params.get("filename")
            if not filename:
                return None
                
            content = params.get("content")
            if content:
                # Escape any single quotes in the content
                content_escaped = content.replace("'", "'\\''")
                return f"echo '{content_escaped}' > {filename}"
            else:
                return f"touch {filename}"
                
        elif operation == "read":
            filename = params.get("filename")
            if not filename:
                return None
                
            return f"cat {filename}"
            
        elif operation == "delete":
            filename = params.get("filename")
            if not filename:
                return None
                
            if params.get("force", False):
                return f"rm -f {filename}"
            else:
                return f"rm {filename}"
                
        elif operation == "search":
            search_term = params.get("search_term")
            directory = params.get("directory", ".")
            
            if not search_term:
                return None
                
            return f"find {directory} -name '*{search_term}*'"
            
        elif operation == "list":
            directory = params.get("directory", ".")
            return f"ls -la {directory}"
            
        return None
        
    def format_ai_prompt(self, user_request: str, platform_info: Dict[str, str] = None) -> str:
        """
        Format a prompt for the AI that encourages structured command responses.
        
        Args:
            user_request: The original user request
            platform_info: Information about the user's platform
            
        Returns:
            Formatted prompt string
        """
        os_info = ""
        if platform_info:
            os_info = f"OS: {platform_info.get('system', 'Unknown')}"
            if platform_info.get('version'):
                os_info += f" {platform_info.get('version')}"
            if platform_info.get('linux_distro'):
                os_info += f" ({platform_info.get('linux_distro')})"
                
        # Enhanced prompt to support both JSON structures for commands and file operations
        prompt = f"""USER REQUEST: {user_request}
SYSTEM INFO: {os_info}

Generate a response in one of the following JSON formats:

FORMAT 1 (for executable shell commands):
```json
{{
  "command": "<executable shell command>",
  "explanation": "<brief explanation of what the command does>",
  "alternatives": ["<alternative command 1>", "<alternative command 2>"],
  "requires_implementation": false
}}
```

FORMAT 2 (for file operations):
```json
{{
  "file_operation": "<create|read|write|delete|search|list>",
  "operation_params": {{
    "filename": "<filename>",
    "content": "<content to write if applicable>",
    "directory": "<directory path if applicable>",
    "search_term": "<search term if applicable>"
  }},
  "explanation": "<brief explanation of the operation>"
}}
```

FORMAT 3 (for requests that cannot be fulfilled with a command):
```json
{{
  "error": true,
  "error_message": "<explain why this cannot be executed>",
  "requires_implementation": true
}}
```

Ensure the command is appropriate for the user's OS. If it cannot be safely executed as a single command, use FORMAT 3.
For file operations, prefer FORMAT 2 as it allows for better structured handling.

If the request appears to be in Arabic, respond with the equivalent command for the user's OS.
"""
        return prompt
        
    def extract_implementation_details(self, ai_response: str) -> Dict[str, Any]:
        """
        Extract detailed implementation requirements from an error response.
        
        Args:
            ai_response: The error response from the AI
            
        Returns:
            Dictionary with implementation details
        """
        details = {
            "requirements": [],
            "complexity": "unknown",
            "reason": "Unknown reason"
        }
        
        # Try to determine the complexity based on keywords
        complexity_indicators = {
            "high": ["complex", "complicated", "multiple steps", "advanced", "specialized"],
            "medium": ["several", "multiple commands", "workflow", "process"],
            "low": ["simple", "straightforward", "basic"]
        }
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in ai_response.lower() for indicator in indicators):
                details["complexity"] = level
                break
                
        # Try to extract the main reason for implementation
        reason_match = re.search(r'(?:because|as|since|reason)\s+(?:it|this|the request)?\s+(?:is|requires|needs|involves)\s+(.*?)(?:\.|\n|$)', 
                                ai_response, re.IGNORECASE)
        if reason_match:
            details["reason"] = reason_match.group(1).strip()
            
        # Try to extract potential requirements or steps
        req_matches = re.findall(r'(?:requires|needs|would need|should have|must have)\s+(.*?)(?:\.|\n|$)', 
                               ai_response, re.IGNORECASE)
        for match in req_matches:
            if match.strip() and len(match.strip().split()) > 2:  # Avoid very short matches
                details["requirements"].append(match.strip())
                
        return details
        
    def parse_file_operation_from_request(self, request: str) -> Dict[str, Any]:
        """
        Parse a natural language request to identify file operations.
        
        Args:
            request: The user request string
            
        Returns:
            Dictionary with file operation details or empty if not a file operation
        """
        request_lower = request.lower()
        result = {
            "is_file_operation": False,
            "operation_type": None,
            "filename": None,
            "content": None,
            "directory": None,
            "search_term": None,
        }
        
        # Define operation type patterns
        operations = {
            "create": ["create", "new", "make", "touch", "generate", "انشاء", "انشئ", "جديد"],
            "read": ["read", "show", "display", "cat", "view", "output", "اقرأ", "اعرض", "اظهر"],
            "write": ["write", "add", "append", "edit", "update", "اكتب", "أكتب", "اضف", "أضف"],
            "delete": ["delete", "remove", "erase", "destroy", "trash", "rm", "احذف", "امسح", "ازل", "أزل"],
            "search": ["search", "find", "locate", "where", "which", "ابحث", "جد", "أين", "اين", "وين"],
            "list": ["list", "ls", "dir", "enumerate", "اظهر", "اعرض", "قائمة"]
        }
        
        # Check for file operation terms
        for op_type, keywords in operations.items():
            if any(keyword in request_lower for keyword in keywords):
                result["is_file_operation"] = True
                result["operation_type"] = op_type
                break
                
        if not result["is_file_operation"]:
            return result
            
        # Try to extract filename
        # Look for quoted file names first
        filename_matches = re.findall(r'[\'"]([^\'"\n]+\.[\w]+)[\'"]', request)
        if filename_matches:
            result["filename"] = filename_matches[0]
        else:
            # Look for unquoted filenames with extensions
            filename_matches = re.findall(r'[\s\'"]([\w-]+\.[\w]+)[\s\'"]', request)
            if filename_matches:
                result["filename"] = filename_matches[0]
            else:
                # Look for "called/named <filename>" pattern
                name_match = re.search(r'(?:called|named)\s+[\'"]?([\w-]+\.?[\w]*)[\'"]?', request_lower)
                if name_match:
                    result["filename"] = name_match.group(1)
                    # Add .txt extension if none specified
                    if '.' not in result["filename"]:
                        result["filename"] += ".txt"
        
        # Try to extract content for write operations
        if result["operation_type"] == "write":
            # Look for quoted content
            content_match = re.search(r'[\'"]([^\'"\n]+)[\'"]', request)
            if content_match:
                result["content"] = content_match.group(1)
            else:
                # Look for content indicators
                content_patterns = [
                    r'(?:with|containing|that says)\s+[\'"]?([^\'"\n.]+)[\'"]?',
                    r'[\'"]?([^\'"\n.]+)[\'"]?\s+(?:to|into|in)\s+(?:the\s+)?file',
                    r'(?:write|add|append)\s+[\'"]?([^\'"\n.]+)[\'"]?',
                ]
                
                for pattern in content_patterns:
                    content_match = re.search(pattern, request_lower)
                    if content_match:
                        result["content"] = content_match.group(1)
                        break
        
        # Try to extract directory for list operations
        if result["operation_type"] == "list":
            dir_patterns = [
                r'(?:in|of|from)\s+(?:the\s+)?(?:directory|folder|dir)?\s+[\'"]?([^\'"\n]+)[\'"]?',
                r'(?:list|ls|dir)\s+[\'"]?([^\'"\n]+)[\'"]?',
            ]
            
            for pattern in dir_patterns:
                dir_match = re.search(pattern, request_lower)
                if dir_match:
                    result["directory"] = dir_match.group(1)
                    break
                    
            # Handle special folder names
            if "desktop" in request_lower:
                result["directory"] = "~/Desktop"
            elif "documents" in request_lower:
                result["directory"] = "~/Documents"
            elif "downloads" in request_lower:
                result["directory"] = "~/Downloads"
        
        # Try to extract search term
        if result["operation_type"] == "search":
            search_patterns = [
                r'(?:for|about|containing|with|related to)\s+[\'"]?([^\'"\n.]+)[\'"]?',
                r'(?:search|find|locate)\s+[\'"]?([^\'"\n]+)[\'"]?',
            ]
            
            for pattern in search_patterns:
                search_match = re.search(pattern, request_lower)
                if search_match:
                    result["search_term"] = search_match.group(1)
                    break
                    
        return result
