"""
AI-Driven Command Processor Module

This module implements an AI-driven approach to command processing
without relying on pattern matching. Instead, it guides the AI
to format responses in a structured way for direct execution.
"""
import json
import logging
import platform
import os
import re
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List, Union

from uaibot.core.command_processor.ai_response_cache import AIResponseCache
from uaibot.core.command_processor.error_handler import error_handler, ErrorCategory
from uaibot.core.command_processor.user_interaction_history import interaction_history

logger = logging.getLogger(__name__)

class AIDrivenProcessor:
    """
    Processes user requests without relying on hardcoded patterns.
    Structures the AI prompt to return commands in predictable formats.
    """
    
    def __init__(self, quiet_mode=False, use_cache=True, cache_size=100, cache_ttl=3600):
        """
        Initialize the AI-driven processor.
        
        Args:
            quiet_mode (bool): Whether to operate in quiet mode
            use_cache (bool): Whether to use response caching
            cache_size (int): Maximum number of items in the cache
            cache_ttl (int): Time-to-live for cache entries in seconds
        """
        self.quiet_mode = quiet_mode
        self.use_cache = use_cache
        self.response_cache = AIResponseCache(max_size=cache_size, ttl_seconds=cache_ttl) if use_cache else None
        
        # Enhanced examples dictionary with more comprehensive examples
        self.format_examples = {
            # Basic command examples
            "list_files": {
                "command": "ls -la",
                "explanation": "Lists all files in the current directory with details",
                "alternatives": ["ls", "find . -maxdepth 1"],
            },
            "advanced_search": {
                "command": "find /home/user -type f -name '*.txt' -size +1M -mtime -7",
                "explanation": "Finds text files larger than 1MB, modified in the last week",
                "alternatives": ["find /home/user -type f -name '*.txt' | xargs ls -lah"],
            },
            
            # File operation examples
            "create_file": {
                "file_operation": "create",
                "operation_params": {
                    "filename": "test.txt", 
                    "content": "Hello world"
                },
                "explanation": "Creates a new file named test.txt with content"
            },
            "read_file": {
                "file_operation": "read",
                "operation_params": {
                    "filename": "config.json"
                },
                "explanation": "Reads and displays the content of config.json"
            },
            "append_file": {
                "file_operation": "append",
                "operation_params": {
                    "filename": "log.txt",
                    "content": "New log entry added"
                },
                "explanation": "Appends a new line to log.txt without overwriting existing content"
            },
            "search_files": {
                "file_operation": "search",
                "operation_params": {
                    "search_term": "config",
                    "directory": "/etc"
                },
                "explanation": "Searches for files containing 'config' in their name in the /etc directory"
            },
            
            # Information responses
            "system_info": {
                "info_type": "system_info",
                "response": "The system is running Linux with 16GB RAM.",
                "related_command": "uname -a",
                "explanation": "Provides information about the operating system"
            },
            "concept_info": {
                "info_type": "concept_explanation",
                "response": "A firewall is a network security system that monitors and controls traffic.",
                "related_command": "sudo ufw status",
                "explanation": "Explains what a firewall is and shows a command to check the firewall status"
            },
            
            # Error responses
            "security_error": {
                "error": True,
                "error_message": "Cannot execute system-level commands that might compromise security",
                "suggested_approach": "Try using a more specific, safer command"
            },
            
            # Multilingual examples
            "arabic_example": {
                "file_operation": "create",
                "operation_params": {"filename": "مرحبا.txt"},
                "explanation": "Creates a new empty file with an Arabic name"
            },
            "spanish_example": {
                "command": "echo 'Hola mundo' > saludo.txt",
                "explanation": "Creates a file with 'Hello World' in Spanish",
                "alternatives": ["printf 'Hola mundo' > saludo.txt"]
            },
            
            # Platform-specific examples
            "macos_example": {
                "command": "sw_vers",
                "explanation": "Displays macOS version information",
                "platform": "macOS"
            },
            "linux_example": {
                "command": "lsb_release -a",
                "explanation": "Displays Linux distribution information",
                "alternatives": ["cat /etc/os-release"],
                "platform": "Linux"
            },
            
            # Multi-step operation example
            "complex_example": {
                "multi_step_operation": True,
                "steps": [
                    {
                        "command": "mkdir -p project/src",
                        "explanation": "Create project directory structure"
                    },
                    {
                        "file_operation": "create",
                        "operation_params": {
                            "filename": "project/src/main.py",
                            "content": "print('Hello, world!')"
                        },
                        "explanation": "Create main.py file"
                    }
                ],
                "explanation": "Sets up a simple Python project"
            }
        }
    
    def format_ai_prompt(self, user_request: str, platform_info: Dict[str, str] = None) -> str:
        """
        Format a comprehensive prompt that guides the AI to return structured responses.
        
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
            if platform_info.get('processor'):
                os_info += f"\nProcessor: {platform_info.get('processor')}"
        
        # Get current timestamp for context
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a comprehensive system prompt that encourages AI to handle all request types
        prompt = f"""
CURRENT TIME: {current_time}
USER REQUEST: {user_request}
SYSTEM INFO: {os_info}

INSTRUCTIONS:
1. Analyze the user's request to determine the appropriate action WITHOUT relying on pattern detection.
2. Process ALL requests, regardless of type, wording, or language - don't defer to other handlers.
3. ALWAYS format your response in one of the structured JSON formats below.
4. Support multiple languages including English and Arabic.
5. Consider the user's operating system when suggesting commands.
6. For natural language requests like "show files in directory", convert them to appropriate commands.
7. For file operations like "create a file named test.txt", use the file_operation structure.
8. For informational requests, provide relevant information AND related commands.
9. Format all responses as valid JSON with proper escaping.
10. NEVER include markdown formatting or triple backticks in your response.
11. NEVER include explanatory text outside the JSON structure.
12. If you're unsure about a command, use the error format and explain why.

RESPONSE FORMATS:

FORMAT 1 (for executable shell commands):
{{
  "command": "<executable shell command>",
  "explanation": "<brief explanation of what the command does>",
  "alternatives": ["<alternative command 1>", "<alternative command 2>"],
  "confidence": 0.95,
  "type": "shell"
}}

FORMAT 2 (for file operations):
{{
  "file_operation": "<create|read|write|delete|search|list>",
  "operation_params": {{
    "filename": "<filename>",
    "content": "<content to write if applicable>",
    "directory": "<directory path if applicable>",
    "search_term": "<search term if applicable>"
  }},
  "explanation": "<brief explanation of the operation>",
  "confidence": 0.95,
  "type": "file"
}}

FORMAT 3 (for information/conversational queries):
{{
  "info_type": "<system_info|general_question|help|definition>",
  "response": "<your detailed response>",
  "related_command": "<optional command related to the query>",
  "explanation": "<brief explanation of the response>",
  "confidence": 0.95,
  "type": "info"
}}

FORMAT 4 (for requests that cannot be fulfilled):
{{
  "error": true,
  "error_message": "<explain why this cannot be executed>",
  "suggested_approach": "<if applicable, suggest how the user might accomplish this>",
  "confidence": 0.95,
  "type": "error"
}}

EXAMPLES:

1. English command: "list files in directory"
{{
  "command": "ls -la",
  "explanation": "Lists all files in the current directory with details",
  "alternatives": ["ls", "find . -maxdepth 1"],
  "confidence": 0.95,
  "type": "shell"
}}

2. Arabic command: "انشاء ملف جديد باسم test_ar.txt"
{{
  "file_operation": "create",
  "operation_params": {{
    "filename": "test_ar.txt"
  }},
  "explanation": "Creates a new empty file named test_ar.txt",
  "confidence": 0.95,
  "type": "file"
}}

3. Information request: "what is the current directory?"
{{
  "info_type": "system_info",
  "response": "The current directory is where you are currently working in the terminal.",
  "related_command": "pwd",
  "explanation": "Shows the current working directory path",
  "confidence": 0.95,
  "type": "info"
}}

4. Error case: "delete system files"
{{
  "error": true,
  "error_message": "Cannot delete system files as it may cause system instability",
  "suggested_approach": "Please specify which specific files you want to delete, and I'll help you do it safely",
  "confidence": 0.95,
  "type": "error"
}}

IMPORTANT GUIDELINES:
1. ONLY respond with the JSON format that best matches the request type
2. Generate properly escaped JSON with no markdown formatting outside the JSON
3. Don't include explanations outside the JSON structure
4. For ANY request, find the appropriate JSON format - don't say "I can't handle this"
5. Commands should be executable directly in a shell without modification
6. Always include the confidence and type fields in your response
7. If you're unsure about a command, use the error format
8. Never include markdown or triple backticks in your response

Now process the user's request and respond with ONLY the appropriate JSON format:
"""
        return prompt
    
    def extract_command(self, ai_response: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Extract a structured command from the AI response.
        
        Args:
            ai_response: The AI's response text
            
        Returns:
            Tuple containing:
                - Success flag (boolean)
                - Extracted command (string or None)
                - Metadata about the response (dictionary)
        """
        # Initialize metadata
        metadata = {
            "source": "ai_driven_processor",
            "confidence": 0.0,
            "is_error": False,
            "error_message": None,
            "explanation": None,
            "file_operation": None,
            "operation_params": {},
            "info_type": None,
            "info_content": None,
        }
        
        # Try to extract JSON from the response
        json_pattern = r'```(?:json)?\s*({[\s\S]*?})\s*```|({[\s\S]*?})'
        json_match = re.search(json_pattern, ai_response)
        
        if not json_match:
            metadata["is_error"] = True
            metadata["error_message"] = "Failed to extract structured data from AI response"
            metadata["raw_response"] = ai_response
            return False, None, metadata
        
        # Get the JSON string and parse it
        json_str = json_match.group(1) or json_match.group(2)
        try:
            data = json.loads(json_str)
            metadata["parsed_json"] = data
            metadata["confidence"] = 0.9
            
            # Extract command from the parsed data
            if "command" in data:
                command = data["command"]
                if "explanation" in data:
                    metadata["explanation"] = data["explanation"]
                if "alternatives" in data:
                    metadata["alternatives"] = data["alternatives"]
                return True, command, metadata
            
            # Handle file operations
            elif "file_operation" in data:
                metadata["file_operation"] = data["file_operation"]
                if "operation_params" in data:
                    metadata["operation_params"] = data["operation_params"]
                if "explanation" in data:
                    metadata["explanation"] = data["explanation"]
                
                # Generate a command based on the file operation
                command = self._generate_command_from_file_operation(
                    data["file_operation"],
                    data.get("operation_params", {})
                )
                
                if command:
                    return True, command, metadata
                else:
                    metadata["is_error"] = True
                    metadata["error_message"] = f"Could not generate command for file operation: {data['file_operation']}"
                    return False, None, metadata
            
            # Handle informational responses
            elif "info_type" in data:
                metadata["info_type"] = data["info_type"]
                metadata["info_content"] = data.get("response", "")
                if "related_command" in data:
                    command = data["related_command"]
                    if "explanation" in data:
                        metadata["explanation"] = data["explanation"]
                    return True, command, metadata
                else:
                    # No command to execute, but not an error
                    metadata["is_error"] = False
                    metadata["explanation"] = data.get("explanation", "Information response")
                    return False, None, metadata
            
            # Handle explicit error responses
            elif "error" in data and data["error"]:
                metadata["is_error"] = True
                metadata["error_message"] = data.get("error_message", "Unknown error")
                if "suggested_approach" in data:
                    metadata["suggested_approach"] = data["suggested_approach"]
                return False, None, metadata
            
            # Fallback for unexpected data structure
            else:
                metadata["is_error"] = True
                metadata["error_message"] = "Unexpected data structure in AI response"
                metadata["raw_data"] = data
                return False, None, metadata
                
        except json.JSONDecodeError as e:
            metadata["is_error"] = True
            metadata["error_message"] = f"Failed to parse JSON from AI response: {str(e)}"
            metadata["raw_response"] = ai_response
            return False, None, metadata
    
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
            
        elif operation == "write":
            filename = params.get("filename")
            content = params.get("content", "")
            if not filename:
                return None
                
            # Escape any single quotes in the content
            content_escaped = content.replace("'", "'\\''")
            return f"echo '{content_escaped}' > {filename}"
            
        elif operation == "append":
            filename = params.get("filename")
            content = params.get("content", "")
            if not filename:
                return None
                
            # Escape any single quotes in the content
            content_escaped = content.replace("'", "'\\''")
            return f"echo '{content_escaped}' >> {filename}"
            
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
    
    def process_request(self, ai_handler, user_request: str, platform_info: Dict[str, Any] = None) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Process a user request using the AI-driven approach.
        
        Args:
            ai_handler: Handler for interacting with the AI model
            user_request: The user's input request
            platform_info: Information about the user's platform
            
        Returns:
            Tuple containing:
                - Success flag (boolean)
                - Command to execute (or None)
                - Metadata about the processing
        """
        # Attempt to retrieve from cache first
        cached_result = None
        if self.use_cache and self.response_cache:
            cached_key = f"{user_request}_{platform_info.get('system', '')}" if platform_info else user_request
            cached_result = self.response_cache.get(cached_key)
            
            if cached_result:
                logger.info(f"Cache hit for request: {user_request[:30]}...")
                return cached_result.get('success', False), cached_result.get('command'), cached_result.get('metadata', {})
        
        # Format the prompt to guide the AI's response
        prompt = self.format_ai_prompt(user_request, platform_info)
        
        try:
            # Get the AI response
            ai_response = ai_handler.get_ai_response(prompt)
            logger.debug(f"AI Response: {ai_response}")
            
            # Extract the command and metadata
            success, command, metadata = self.extract_command(ai_response)
            
            # If we have a direct error from the AI
            if metadata["is_error"]:
                return False, None, metadata
            
            # Add the full AI response to metadata if we didn't get a command
            if not success:
                metadata["full_ai_response"] = ai_response
            
            # Store successful results in cache for future use
            if success and self.use_cache and self.response_cache:
                cached_key = f"{user_request}_{platform_info.get('system', '')}" if platform_info else user_request
                cached_data = {
                    'success': success,
                    'command': command,
                    'metadata': metadata
                }
                self.response_cache.put(cached_key, cached_data)
                logger.debug(f"Cached response for request: {user_request[:30]}...")
            
            return success, command, metadata
            
        except Exception as e:
            logger.error(f"Error in AI-driven processing: {e}")
            metadata = {
                "source": "ai_driven_processor",
                "is_error": True,
                "error_message": f"Error occurred during processing: {str(e)}",
                "exception_type": str(type(e).__name__)
            }
            return False, None, metadata
            
    def clear_cache(self) -> None:
        """
        Clear the response cache.
        """
        if self.use_cache and self.response_cache:
            self.response_cache.clear()
            logger.info("AI response cache cleared")
            
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary containing cache statistics or empty dict if cache is disabled
        """
        if self.use_cache and self.response_cache:
            return self.response_cache.get_stats()
        return {"enabled": False}
        
    def _get_platform_info(self) -> Dict[str, Any]:
        """
        Get information about the current platform.
        
        Returns:
            Dictionary with platform details
        """
        system = platform.system()
        platform_info = {
            "system": system,
            "version": platform.version(),
            "processor": platform.processor()
        }
        
        # Add Linux distribution info if available
        if system == "Linux":
            try:
                import distro
                platform_info["linux_distro"] = distro.name(pretty=True)
            except ImportError:
                pass
                
        return platform_info

    def process_request_with_extractors(self, request: str, ai_handler, command_extractor) -> Dict[str, Any]:
        """
        Process a user request using provided extractors and handler.
        Used for advanced processing that requires direct access to extractors.
        
        Args:
            request: The user request string
            ai_handler: The AI handler to use for generating responses
            command_extractor: The command extractor to use
            
        Returns:
            Dictionary containing the processing result
        """
        # Get platform information for context
        platform_info = self._get_platform_info()
        
        # Generate a cache key based on the request and platform info
        if self.use_cache and self.response_cache:
            cached_key = f"{request}_{platform_info.get('system', '')}"
            cached_result = self.response_cache.get(cached_key)
            
            if cached_result:
                logger.debug(f"Cache hit for request: {request[:30]}...")
                return cached_result
        
        # Format the AI prompt with the request and platform info
        ai_prompt = self.format_ai_prompt(request, platform_info)
        
        # Get the AI response
        ai_response = ai_handler.get_ai_response(ai_prompt)
        
        # Extract the command and metadata
        success, command, metadata = self.extract_command(ai_response)
        
        # Prepare the result
        result = {
            "success": success,
            "command": command,
            "metadata": metadata,
            "ai_response": ai_response
        }
        
        # Cache the result for future use
        if self.use_cache and self.response_cache:
            cached_key = f"{request}_{platform_info.get('system', '')}"
            self.response_cache.put(cached_key, result)
        
        return result
