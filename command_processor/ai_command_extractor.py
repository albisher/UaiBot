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
                                related_cmd = data["related_command"]
                                metadata["related_commands"] = [related_cmd] if isinstance(related_cmd, str) else related_cmd
                                
                            # If there's a related command, return it
                            if metadata["related_commands"]:
                                command = metadata["related_commands"][0]
                                if "explanation" in data:
                                    metadata["explanation"] = data["explanation"]
                                return True, command, metadata
                        
                        # Handle information format
                        if "information" in data and data["information"]:
                            metadata["info_response"] = data.get("content", "")
                            if "related_commands" in data:
                                metadata["related_commands"] = data["related_commands"]
                                
                            # If there's a related command, return it
                            if metadata["related_commands"] and len(metadata["related_commands"]) > 0:
                                command = metadata["related_commands"][0]
                                return True, command, metadata
                    
                    # FORMAT 5: Filesystem operation
                    elif "filesystem_operation" in data and data["filesystem_operation"]:
                        if "command" in data:
                            command = data["command"]
                            if "explanation" in data:
                                metadata["explanation"] = data["explanation"]
                            metadata["operation_type"] = data.get("operation_type", "unknown")
                            metadata["path"] = data.get("path", ".")
                            
                            return True, command, metadata
                    
                    # FORMAT 6: Multi-step operation (return the first command)
                    elif "steps" in data and isinstance(data["steps"], list) and len(data["steps"]) > 0:
                        first_step = data["steps"][0]
                        if isinstance(first_step, dict) and "command" in first_step:
                            command = first_step["command"]
                            metadata["multi_step"] = True
                            metadata["total_steps"] = len(data["steps"])
                            metadata["current_step"] = 1
                            metadata["all_steps"] = data["steps"]
                            if "explanation" in first_step:
                                metadata["explanation"] = first_step["explanation"]
                            
                            return True, command, metadata
                    
                except json.JSONDecodeError:
                    # This particular JSON string was invalid, try the next one
                    continue
        except Exception as e:
            logger.debug(f"Error processing JSON in AI response: {e}")
        
        # Second priority: Try to extract code blocks if JSON parsing failed
        try:
            # Look for code blocks (bash, shell, etc.)
            code_blocks = re.findall(r'```(?:bash|shell|sh|cmd|powershell)?\s*([^`]+)```', ai_response, re.DOTALL)
            if code_blocks:
                command = code_blocks[0].strip()
                metadata["source"] = "code_block"
                metadata["confidence"] = 0.8
                
                logger.debug(f"Extracted command from code block: {command}")
                return True, command, metadata
        except Exception as e:
            logger.debug(f"Error extracting code blocks: {e}")
        
        # Third priority: Try to extract inline code
        try:
            inline_codes = re.findall(r'`([^`]+)`', ai_response)
            if inline_codes:
                # Use the longest inline code as it's more likely to be a complete command
                command = max(inline_codes, key=len).strip()
                metadata["source"] = "inline_code"
                metadata["confidence"] = 0.7
                
                logger.debug(f"Extracted command from inline code: {command}")
                return True, command, metadata
        except Exception as e:
            logger.debug(f"Error extracting inline code: {e}")
        
        # Fallback: Check for Arabic commands
        try:
            arabic_command = self._extract_arabic_command(ai_response)
            if arabic_command:
                metadata["source"] = "arabic_command"
                metadata["confidence"] = 0.6
                
                logger.debug(f"Extracted Arabic command: {arabic_command}")
                return True, arabic_command, metadata
        except Exception as e:
            logger.debug(f"Error extracting Arabic command: {e}")
            
        # No command found - check if response indicates an error
        for error_text in self.error_indicators:
            if error_text.lower() in ai_response.lower():
                metadata["is_error"] = True
                error_match = re.search(r'(?:ERROR|error|Error):\s*(.*?)(?:\n|$)', ai_response)
                if error_match:
                    metadata["error_message"] = error_match.group(1).strip()
                else:
                    metadata["error_message"] = "Unable to fulfill request safely"
                
                logger.debug(f"Detected error in AI response: {metadata['error_message']}")
                return False, None, metadata
            
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
                        # File creation commands
                        if "انشاء" in line or "انشئ" in line or "جديد" in line:
                            # Create file command - extract the filename
                            match = re.search(r'(?:انشاء|انشئ|جديد)\s+(?:ملف|مجلد)?\s+(?:باسم|اسمه)?\s*([^\s,]+)', line)
                            if match:
                                return f"touch {match.group(1)}"
                            # Try alternative pattern
                            match = re.search(r'(?:انشاء|انشئ).*?(?:ملف|مجلد)\s+(?:جديد)?\s+(?:باسم|اسمه)?\s*([^\s,]+)', line)
                            if match:
                                return f"touch {match.group(1)}"
                                
                        # File deletion commands
                        elif "احذف" in line or "امسح" in line or "ازل" in line or "أزل" in line:
                            # Delete file command - extract the filename
                            match = re.search(r'(?:احذف|امسح|ازل|أزل)\s+(?:ال)?(?:ملف|مجلد)?\s+([^\s,]+)', line)
                            if match:
                                return f"rm {match.group(1)}"
                                
                        # File read commands
                        elif "اقرأ" in line or "اعرض" in line or "اظهر" in line:
                            # First check for "محتوى الملف" pattern
                            match = re.search(r'(?:اقرأ|اعرض|اظهر)\s+(?:محتوى|محتويات)\s+(?:ال)?ملف\s+([^\s,]+)', line)
                            if match:
                                return f"cat {match.group(1)}"
                            # Then check for simpler pattern
                            match = re.search(r'(?:اقرأ|اعرض|اظهر)\s+(?:ال)?ملف\s+([^\s,]+)', line)
                            if match:
                                return f"cat {match.group(1)}"
                                
                        # List files commands
                        elif "الملفات" in line or "اعرض جميع" in line:
                            # Check if a specific directory is mentioned
                            match = re.search(r'(?:في|في ال|في المجلد)\s+([^\s,]+)', line)
                            if match:
                                return f"ls -l {match.group(1)}"
                            else:
                                return "ls -l"
                                
                        # Write to file commands
                        elif "اكتب" in line or "أكتب" in line or "اضف" in line or "أضف" in line:
                            # Look for content in quotes
                            content_match = re.search(r'[\'"]([^\'"\n]+)[\'"]', line)
                            # Look for filename after "في" (in)
                            file_match = re.search(r'(?:في|الى|إلى)\s+(?:ال)?ملف\s+([^\s,]+)', line)
                            
                            if content_match and file_match:
                                content = content_match.group(1)
                                filename = file_match.group(1)
                                return f"echo '{content}' > {filename}"
                            elif file_match:
                                # If we found a file but no content
                                return f"touch {file_match.group(1)}"
        
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
  "requires_implementation": true,
  "suggested_approach": "<if applicable, suggest how the user might accomplish this>"
}}
```

FORMAT 4 (for informational/conversational queries):
```json
{{
  "info_type": "<system_info|general_question|help|definition>",
  "response": "<your detailed response>",
  "related_command": "<optional command related to the query>",
  "explanation": "<brief explanation of the response>"
}}
```

EXAMPLES:
1. "list files in directory" → {"command": "ls -la", "explanation": "Lists all files in the current directory with details", "alternatives": ["ls", "find . -maxdepth 1"], "requires_implementation": false}
2. "create a file named test.txt with content hello" → {"file_operation": "create", "operation_params": {"filename": "test.txt", "content": "hello"}, "explanation": "Creates a new file named test.txt with content 'hello'"}
3. "what's my ip address" → {"command": "ip addr show", "explanation": "Shows network interface information including IP addresses", "alternatives": ["ifconfig", "hostname -I"], "requires_implementation": false}
4. "انشاء ملف جديد باسم test_ar.txt" → {"file_operation": "create", "operation_params": {"filename": "test_ar.txt"}, "explanation": "Creates a new empty file named test_ar.txt"}
"""

FORMAT 4 (for information requests that don't require commands):
```json
{{
  "information": true,
  "content": "<the informational response>",
  "related_commands": ["<related command 1>", "<related command 2>"]
}}
```

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
