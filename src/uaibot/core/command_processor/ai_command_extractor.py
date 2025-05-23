"""
AI Command Extractor Module

This module extracts executable commands from AI responses and 
handles various formats and response types to make command processing
more robust and flexible.
"""

import json
import re
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List, Union

logger = logging.getLogger(__name__)

# Add imports for parallel processing at the top of the file
import concurrent.futures
from uaibot.core.parallel_utils import ParallelTaskManager, run_in_parallel

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
        
        # Arabic command indicators
        self.arabic_command_indicators = [
            "اكتب", "أكتب", "اضف", "أضف", "احذف", "امسح", 
            "ازل", "أزل", "انشاء", "انشئ", "اقرأ", "اعرض"
        ]
        
    def extract_command(self, ai_response: str) -> Tuple[bool, Optional[dict], Dict[str, Any]]:
        """
        Extract a plan-based command from AI response text with rich metadata.
        Prioritizes structured JSON formats as specified in the new prompt.
        
        Args:
            ai_response: The text response from the AI
            
        Returns:
            Tuple containing:
                - Success flag (boolean)
                - Extracted plan (dict or None)
                - Metadata about the extraction (dictionary)
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"Starting command extraction with response: {ai_response[:200]}...")

        metadata = {
            "source": None,
            "confidence": 0.0,
            "is_error": False,
            "error_message": None,
            "alternatives": [],
            "parsed_json": None,
            "plan": None,
            "overall_confidence": None,
            "language": None,
            "extraction_steps": []  # Track which extraction methods were attempted
        }

        # Check for empty response
        if not ai_response or not ai_response.strip():
            logger.warning("Empty AI response received")
            metadata["is_error"] = True
            metadata["error_message"] = "Empty AI response"
            return False, None, metadata

        # Check for error indicators
        is_error, error_message = self._check_for_error(ai_response)
        if is_error:
            logger.warning(f"Error detected in AI response: {error_message}")
            metadata["is_error"] = True
            metadata["error_message"] = error_message
            return False, None, metadata

        # Try to extract JSON from code blocks or raw text
        logger.debug("Attempting JSON extraction from code blocks")
        json_blocks = self._extract_json_blocks(ai_response)
        if not json_blocks:
            logger.debug("No JSON found in code blocks, trying raw text")
            json_blocks = self._extract_raw_json(ai_response)

        # Try to parse JSON blocks
        data = None
        for json_str in json_blocks:
            try:
                data = json.loads(json_str)
                logger.debug(f"Successfully parsed JSON: {json.dumps(data)[:200]}...")
                break
            except json.JSONDecodeError as e:
                logger.debug(f"JSON parsing failed: {str(e)}")
                continue

        # If JSON parsing failed, try other extraction methods
        if not data:
            logger.debug("JSON parsing failed, trying alternative extraction methods")
            metadata["extraction_steps"].append("json_failed")

            # Try to extract command from code blocks
            logger.debug("Attempting code block extraction")
            code_blocks = self._extract_code_blocks(ai_response)
            if code_blocks:
                logger.debug(f"Found code block: {code_blocks[0][:100]}...")
                command = code_blocks[0].strip()
                metadata["source"] = "code_block"
                metadata["extraction_steps"].append("code_block_success")
                return True, {"command": command, "type": "shell"}, metadata
            metadata["extraction_steps"].append("code_block_failed")

            # Try to extract command from phrases
            logger.debug("Attempting phrase extraction")
            command = self._extract_command_from_phrases(ai_response)
            if command:
                logger.debug(f"Found command in phrases: {command[:100]}...")
                metadata["source"] = "phrase"
                metadata["extraction_steps"].append("phrase_success")
                return True, {"command": command, "type": "shell"}, metadata
            metadata["extraction_steps"].append("phrase_failed")

            # Try to extract Arabic command
            logger.debug("Attempting Arabic command extraction")
            command = self._extract_arabic_command(ai_response)
            if command:
                logger.debug(f"Found Arabic command: {command[:100]}...")
                metadata["source"] = "arabic"
                metadata["extraction_steps"].append("arabic_success")
                return True, {"command": command, "type": "shell"}, metadata
            metadata["extraction_steps"].append("arabic_failed")

            logger.warning("All extraction methods failed")
            metadata["is_error"] = True
            metadata["error_message"] = "No valid command found in AI response"
            return False, None, metadata

        # Process parsed JSON data
        logger.debug("Processing parsed JSON data")
        metadata["parsed_json"] = data
        metadata["confidence"] = data.get("confidence", 0.95)
        metadata["language"] = data.get("language", "en")

        # Handle plan-based structure
        if "plan" in data and isinstance(data["plan"], list):
            logger.debug("Found plan-based structure")
            metadata["plan"] = data["plan"]
            metadata["overall_confidence"] = data.get("overall_confidence")
            metadata["alternatives"] = data.get("alternatives", [])
            metadata["source"] = "plan_json"
            return True, data, metadata

        # Handle single command structure
        if "command" in data:
            logger.debug("Found single command structure")
            metadata["source"] = "command_json"
            return True, {
                "plan": [{
                    "step": 1,
                    "description": data["command"],
                    "operation": data.get("type", "shell"),
                    "parameters": data.get("parameters", {}),
                    "confidence": data.get("confidence", 0.9),
                    "condition": None,
                    "on_success": [],
                    "on_failure": [],
                    "explanation": data.get("explanation", "")
                }]
            }, metadata

        # Handle multiple commands structure
        if "commands" in data and isinstance(data["commands"], list):
            logger.debug("Found multiple commands structure")
            metadata["source"] = "commands_json"
            return True, {
                "plan": [
                    {
                        "step": i + 1,
                        "description": cmd["command"],
                        "operation": cmd.get("type", "shell"),
                        "parameters": cmd.get("parameters", {}),
                        "confidence": cmd.get("confidence", 0.9),
                        "condition": None,
                        "on_success": [],
                        "on_failure": [],
                        "explanation": cmd.get("explanation", "")
                    }
                    for i, cmd in enumerate(data["commands"])
                ]
            }, metadata

        logger.warning("No valid command structure found in JSON")
        metadata["is_error"] = True
        metadata["error_message"] = "No valid command structure found in JSON"
        return False, None, metadata

    def _extract_json_blocks(self, text: str) -> List[str]:
        """Extract JSON blocks from text, handling various formats."""
        logger = logging.getLogger(__name__)
        json_blocks = []
        
        # Pattern for JSON in code blocks
        code_block_pattern = r'```(?:json)?\s*({[\s\S]*?})\s*```'
        code_blocks = re.findall(code_block_pattern, text, re.DOTALL)
        
        if code_blocks:
            logger.debug(f"Found {len(code_blocks)} JSON code blocks")
            json_blocks.extend(code_blocks)
        
        # Pattern for JSON in triple backticks without language specifier
        triple_backtick_pattern = r'```\s*({[\s\S]*?})\s*```'
        triple_blocks = re.findall(triple_backtick_pattern, text, re.DOTALL)
        
        if triple_blocks:
            logger.debug(f"Found {len(triple_blocks)} triple backtick blocks")
            json_blocks.extend(triple_blocks)
        
        # Pattern for JSON in single backticks
        single_backtick_pattern = r'`({[\s\S]*?})`'
        single_blocks = re.findall(single_backtick_pattern, text, re.DOTALL)
        
        if single_blocks:
            logger.debug(f"Found {len(single_blocks)} single backtick blocks")
            json_blocks.extend(single_blocks)
        
        # Validate each block is actually JSON
        valid_blocks = []
        for block in json_blocks:
            try:
                # Try to parse the JSON
                json.loads(block)
                valid_blocks.append(block)
            except json.JSONDecodeError:
                logger.debug(f"Invalid JSON block found: {block[:100]}...")
                continue
        
        return valid_blocks

    def _extract_raw_json(self, text: str) -> List[str]:
        """Extract raw JSON from text without code block markers."""
        logger = logging.getLogger(__name__)
        json_blocks = []
        
        # Pattern for raw JSON objects
        json_pattern = r'({[\s\S]*?})'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            logger.debug(f"Found {len(matches)} potential raw JSON blocks")
            
            # Validate each match is actually JSON
            for match in matches:
                try:
                    # Try to parse the JSON
                    json.loads(match)
                    json_blocks.append(match)
                except json.JSONDecodeError:
                    logger.debug(f"Invalid raw JSON found: {match[:100]}...")
                    continue
        
        return json_blocks

    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from text, handling various formats."""
        logger = logging.getLogger(__name__)
        code_blocks = []
        
        # Pattern for code blocks with language specifier
        code_block_pattern = r'```(?:bash|shell|zsh|sh|console|terminal)?\s*(.*?)\s*```'
        blocks = re.findall(code_block_pattern, text, re.DOTALL)
        
        if blocks:
            logger.debug(f"Found {len(blocks)} code blocks with language specifier")
            code_blocks.extend(blocks)
        
        # Pattern for code blocks without language specifier
        raw_block_pattern = r'```\s*(.*?)\s*```'
        raw_blocks = re.findall(raw_block_pattern, text, re.DOTALL)
        
        if raw_blocks:
            logger.debug(f"Found {len(raw_blocks)} raw code blocks")
            code_blocks.extend(raw_blocks)
        
        # Pattern for inline code
        inline_pattern = r'`(.*?)`'
        inline_blocks = re.findall(inline_pattern, text)
        
        if inline_blocks:
            logger.debug(f"Found {len(inline_blocks)} inline code blocks")
            code_blocks.extend(inline_blocks)
        
        # Clean and validate each block
        valid_blocks = []
        for block in code_blocks:
            # Clean the block
            cleaned = block.strip()
            if cleaned:
                # Skip if it looks like JSON
                if cleaned.startswith('{') and cleaned.endswith('}'):
                    try:
                        json.loads(cleaned)
                        logger.debug(f"Skipping JSON block: {cleaned[:100]}...")
                        continue
                    except json.JSONDecodeError:
                        pass
                valid_blocks.append(cleaned)
        
        return valid_blocks

    def _extract_command_from_phrases(self, text: str) -> Optional[str]:
        """Extract command from natural language phrases."""
        logger = logging.getLogger(__name__)
        
        # Common command indicators
        command_indicators = [
            r'run\s+(?:the\s+)?command:\s*(.*?)(?:\.|$)',
            r'execute\s+(?:the\s+)?command:\s*(.*?)(?:\.|$)',
            r'use\s+(?:the\s+)?command:\s*(.*?)(?:\.|$)',
            r'command\s+is:\s*(.*?)(?:\.|$)',
            r'run:\s*(.*?)(?:\.|$)',
            r'execute:\s*(.*?)(?:\.|$)',
            r'use:\s*(.*?)(?:\.|$)',
            r'command:\s*(.*?)(?:\.|$)'
        ]
        
        for pattern in command_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                command = matches[0].strip()
                logger.debug(f"Found command in phrase: {command[:100]}...")
                return command
        
        # Try to find lines that look like commands
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('#', '//', 'Note:', 'Here', 'Try')):
                # Check if line looks like a command
                if any(c in line for c in ['$', '>', 'sudo', 'git', 'npm', 'python', 'pip']):
                    logger.debug(f"Found command-like line: {line[:100]}...")
                    return line
        
        return None

    def _extract_arabic_command(self, text: str) -> Optional[str]:
        """Extract command from Arabic text."""
        logger = logging.getLogger(__name__)
        
        # Common Arabic command indicators
        arabic_indicators = [
            r'نفذ\s+(?:الامر|الاوامر):\s*(.*?)(?:\.|$)',
            r'استخدم\s+(?:الامر|الاوامر):\s*(.*?)(?:\.|$)',
            r'الامر\s+هو:\s*(.*?)(?:\.|$)',
            r'نفذ:\s*(.*?)(?:\.|$)',
            r'استخدم:\s*(.*?)(?:\.|$)',
            r'الامر:\s*(.*?)(?:\.|$)'
        ]
        
        for pattern in arabic_indicators:
            matches = re.findall(pattern, text)
            if matches:
                command = matches[0].strip()
                logger.debug(f"Found Arabic command: {command[:100]}...")
                return command
        
        return None

    def _check_for_error(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if the AI response indicates an error condition.
        
        Args:
            text: The AI response text
            
        Returns:
            Tuple of (is_error, error_message)
        """
        for error_phrase in self.error_indicators:
            if error_phrase.lower() in text.lower():
                # Try to extract a more specific error message
                lines = text.split('\n')
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
        prompt = (
            "You are an AI assistant running on a system with the following details:\n"
            f"- OS: {system_info.get('system', 'Unknown')}\n"
            f"- Version: {system_info.get('version', 'Unknown')}\n"
            "- Available tools: file operations, browser automation, shell commands, folder search, USB device queries, and more.\n\n"
            "The user has provided the following command:\n"
            f'"{user_input}"\n\n'
            "STRICT INSTRUCTIONS:\n"
            "- You MUST reply with a valid JSON object ONLY (no markdown, no triple backticks, no extra text).\n"
            "- The JSON must have a 'plan' key, which is a list of steps.\n"
            "- Each step must have:\n"
            "    - 'step': short step name\n"
            "    - 'description': short description\n"
            "    - 'operation': one of [\"system_command\", \"execute_command\", \"file_system_search\", \"file_operation\", \"info_query\", \"print_formatted_output\", \"sort\", \"regex_extraction\", \"prompt_user\", \"send_confirmation\", \"error\"] (never null, never a sentence)\n"
            "    - 'parameters': object (may be empty)\n"
            "    - 'confidence': float (0.0-1.0)\n"
            "    - 'conditions': null or string\n"
            "- Never use natural language in the 'operation' field. Only use the allowed values above.\n"
            "- Never use null for 'operation'.\n"
            "- Never use markdown or triple backticks.\n"
            "- If you are unsure, use 'error' as the operation and explain in 'description'.\n\n"
            "Canonical Example:\n"
            "{\n"
            "  \"plan\": [\n"
            "    {\n"
            "      \"step\": \"get_system_uptime\",\n"
            "      \"description\": \"Get how long the system has been running.\",\n"
            "      \"operation\": \"system_command\",\n"
            "      \"parameters\": {\"command\": \"uptime\"},\n"
            "      \"confidence\": 0.95,\n"
            "      \"conditions\": null\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Your response must match this schema exactly. Now process the user's request and reply with ONLY the JSON object."
        )
        return prompt
