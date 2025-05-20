"""
AI Command Extractor Module

This module extracts executable commands from AI responses and 
handles various formats and response types to make command processing
more robust and flexible.
"""

import re
import json
import logging
from datetime import datetime
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
            # Look for code blocks containing JSON - this is the highest priority
            json_pattern = r'```json\s*(\{[\s\S]*?\})\s*```'
            json_matches = re.findall(json_pattern, ai_response, re.DOTALL)
            
            if not json_matches:
                # If no code block JSON, look for raw JSON objects
                raw_json_pattern = r'(\{[\s\S]*?\})'
                json_matches = re.findall(raw_json_pattern, ai_response, re.DOTALL)
            
            # Try each potential JSON match until we find a valid one
            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    metadata["parsed_json"] = data
                    metadata["source"] = "json"
                    metadata["confidence"] = 0.95
                    
                    # """
        Extract Arabic commands from the AI response using the AI-driven approach.
        This is a language-agnostic implementation that relies on JSON structures
        rather than hardcoded patterns.
        
        Args:
            ai_response: The AI response to analyze
            
        Returns:
            Optional[str]: Extracted Arabic command or None
        """
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
        
        # If no structured format is found, return None
        # The main extract_command method will handle fallbacks
        return None
        
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
        This implementation focuses on having the AI process all requests without relying
        on hardcoded patterns in the code.
        
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
        
        # Get current timestamp for context
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a comprehensive system prompt that encourages AI to handle all request types
        prompt = f"""You are UaiBot, an advanced AI terminal assistant that interprets user requests and converts them into executable actions without relying on pattern matching.

CURRENT TIME: {current_time}
USER REQUEST: {user_request}
SYSTEM INFO: {os_info}

CORE PRINCIPLES:
- DO NOT try to detect patterns in the request. Process each request based on its meaning.
- ALWAYS respond in one of the structured JSON formats below - this is critical.
- YOU are responsible for processing ALL requests directly - there is no fallback system.
- Understand and handle ALL user intentions regardless of wording or language used.
- Make no assumptions about what the system can or cannot handle - YOU handle everything.

INSTRUCTIONS:
1. Analyze the user's request and determine the appropriate action by understanding its semantic meaning.
2. ALWAYS format your response in one of the structured JSON formats below - this is absolutely required.
3. Process ALL requests, regardless of type, wording, or language - nothing gets passed to a secondary handler.
4. Support multiple languages including English and Arabic without translation.
5. Consider the user's operating system when suggesting commands.
6. Convert natural language requests like "show me files in the directory" to the appropriate command.
7. Convert file operation requests like "create a file named test.txt" to proper file operation structure.
8. For informational requests, provide both information and any related commands.
9. For all commands, ensure they are safe, well-formed, and appropriate for the user's operating system.
10. If you cannot safely fulfill a request, use the error format with a clear explanation.

RESPONSE FORMATS:

"""

FORMAT 5 (for handling file system operations):
```json
{{
  "filesystem_operation": true,
  "operation_type": "<view|find|list|browse>",
  "path": "<target path or pattern>",
  "recursive": <true|false>,
  "command": "<the shell command that will execute this operation>",
  "explanation": "<brief explanation of what will be shown>"
}}
```

FORMAT 6 (for multi-step operations):
```json
{{
  "multi_step": true,
  "steps": [
    {{
      "command": "<step 1 command>",
      "explanation": "<what this step does>"
    }},
    {{
      "command": "<step 2 command>",
      "explanation": "<what this step does>"
    }}
  ],
  "summary": "<brief summary of the full operation>"
}}
```

MULTILINGUAL SUPPORT:
- If the request is in a non-English language (e.g., Arabic), process it naturally without translation.
- Format the response using the same JSON structure, generating appropriate commands for the target OS.
- Handle various forms of the same request regardless of phrasing or language used.

SAFETY INSTRUCTIONS:
- Never generate commands that could harm the system.
- For potentially destructive operations, include appropriate warnings.
- For commands requiring elevated privileges, use FORMAT 3 with clear explanations.

IMPORTANT: YOU MUST HANDLE ALL REQUESTS DIRECTLY. Do not defer to another system or handler. Process the request and provide a properly formatted response regardless of the query type.

Now process the user's request and respond with the appropriate JSON format.
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
            if "desktop" في request_lower:
                result["directory"] = "~/Desktop"
            elif "documents" في request_lower:
                result["directory"] = "~/Documents"
            elif "downloads" في request_lower:
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

    def process_request_with_ai(self, ai_handler, user_request: str, platform_info: Dict[str, Any] = None) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Process a user request completely with AI, without relying on pattern matching.
        This is the main entry point for the new AI-driven approach.
        
        Args:
            ai_handler: The AI handler to use for processing
            user_request: The user's request
            platform_info: Information about the user's platform
        
        Returns:
            Tuple containing:
                - Success flag (boolean)
                - Extracted command or information (string or None)
                - Metadata about the processing (dictionary)
        """
        # Create a prompt that guides the AI to process all requests
        prompt = self.format_ai_prompt(user_request, platform_info)
        
        # Get the AI response
        try:
            ai_response = ai_handler.get_ai_response(prompt)
            logger.debug(f"AI Response: {ai_response}")
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return False, None, {
                "is_error": True, 
                "error_message": f"Failed to process with AI: {str(e)}",
                "source": "ai_error"
            }
        
        # Extract a command from the AI response
        success, command, metadata = self.extract_command(ai_response)
        
        # If we couldn't extract a command but we have an AI response, set the full response as metadata
        if not success and not metadata["is_error"]:
            metadata["full_ai_response"] = ai_response
        
        return success, command, metadata
