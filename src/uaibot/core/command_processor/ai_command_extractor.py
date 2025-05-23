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
        }

        # Check for empty response
        if not ai_response or not ai_response.strip():
            metadata["is_error"] = True
            metadata["error_message"] = "Empty AI response"
            return False, None, metadata

        # Check for error indicators
        is_error, error_message = self._check_for_error(ai_response)
        if is_error:
            metadata["is_error"] = True
            metadata["error_message"] = error_message
            return False, None, metadata

        # Try to extract JSON from code blocks or raw text
        json_blocks = self._extract_json_blocks(ai_response)
        if not json_blocks:
            json_blocks = self._extract_raw_json(ai_response)

        # Try to parse JSON blocks
        data = None
        for json_str in json_blocks:
            try:
                data = json.loads(json_str)
                break
            except json.JSONDecodeError:
                continue

        # If JSON parsing failed, try other extraction methods
        if not data:
            # Try to extract command from code blocks
            code_blocks = self._extract_code_blocks(ai_response)
            if code_blocks:
                command = code_blocks[0].strip()
                return True, {"command": command, "type": "shell"}, metadata

            # Try to extract command from phrases
            command = self._extract_command_from_phrases(ai_response)
            if command:
                return True, {"command": command, "type": "shell"}, metadata

            # Try to extract Arabic command
            command = self._extract_arabic_command(ai_response)
            if command:
                return True, {"command": command, "type": "shell"}, metadata

            metadata["is_error"] = True
            metadata["error_message"] = "No valid command found in AI response"
            return False, None, metadata

        # Process parsed JSON data
        metadata["parsed_json"] = data
        metadata["confidence"] = data.get("confidence", 0.95)
        metadata["language"] = data.get("language", "en")

        # Handle plan-based structure
        if "plan" in data and isinstance(data["plan"], list):
            metadata["plan"] = data["plan"]
            metadata["overall_confidence"] = data.get("overall_confidence")
            metadata["alternatives"] = data.get("alternatives", [])
            metadata["source"] = "plan_json"
            return True, data, metadata

        # Handle single command structure
        if "command" in data:
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

        metadata["is_error"] = True
        metadata["error_message"] = "No valid command structure found in JSON"
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
        in_block = False
        current_block = []
        
        for line in lines:
            if any(line.strip().startswith(marker) for marker in self.code_block_markers):
                in_block = True
                current_block = []
            elif in_block and line.strip().startswith('```'):
                in_block = False
                if current_block:
                    blocks.append('\n'.join(current_block))
            elif in_block:
                current_block.append(line)
        
        return blocks

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

    def _extract_arabic_command(self, text: str) -> Optional[str]:
        """Extract Arabic commands from text."""
        # Special case for the write with content pattern: "اكتب 'content' في ملف filename"
        if "اكتب" in text and "في ملف" in text:
            content_match = re.search(r"'([^']*)'", text)
            filename_match = re.search(r"في ملف\s+(\S+)", text)
            if content_match and filename_match:
                content = content_match.group(1)
                filename = filename_match.group(1)
                return f"echo '{content}' > {filename}"

        # Process Arabic commands based on keywords
        for indicator in self.arabic_command_indicators:
            if indicator in text:
                words = text.split()
                # Find the index of the Arabic command indicator
                for i, word in enumerate(words):
                    if indicator in word:
                        # Handle more complex filenames with "باسم" (meaning "named")
                        if "باسم" in text:
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
                                    content_match = re.search(r"'([^']*)'", text)
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
                                if "في" in text and "ملف" in text:
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
                                    content_match = re.search(r"'([^']*)'", text)
                                    if content_match:
                                        content = content_match.group(1)
                                        return f"echo '{content}' > {filename}"
                                    else:
                                        return f"touch {filename}"
                        
                        # Special case for directory listing
                        elif "المجلد" in text and "الحالي" in text:
                            return "ls -l"
        
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
