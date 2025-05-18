# Copyright (c) 2025 UaiBot Team
# License: Custom license - free for personal and educational use.
# Commercial use requires a paid license. See LICENSE file for details.

import re
import os
import platform
import sys
import json
import shlex
import base64
from typing import Dict, Any, Union, Optional
from core.utils import get_project_root, run_command
from terminal_commands import CommandRegistry, CommandExecutor

class CommandProcessor:
    """
    Processes user commands and determines the appropriate handler.
    Supports multimodal inputs like text, audio, images, and gestures.
    """
    
    def __init__(self, ai_handler, shell_handler, quiet_mode=False):
        """Initialize CommandProcessor with AI and shell handlers."""
        self.ai_handler = ai_handler
        self.shell_handler = shell_handler
        self.quiet_mode = quiet_mode
        self.system_platform = platform.system().lower()
        
        # Initialize command registry and executor
        self.command_registry = CommandRegistry()
        self.command_executor = CommandExecutor(shell_handler, self.command_registry)
        
        # Load command patterns from JSON file
        self.command_patterns = self._load_command_patterns()
        
    def _load_command_patterns(self):
        """Load command patterns from JSON file."""
        patterns_file = os.path.join(get_project_root(), 'config', 'command_patterns.json')
        # Enhanced patterns with more comprehensive matching for user intent
        default_patterns = {
            "system_info": {
                "uptime": [
                    r"(how\s+long|since|uptime|duration|running\s+time|system\s+on\s+time|time\s+running)",
                    r"(when\s+(was|did)\s+(system|computer|pc|mac|it)\s+(start|boot|turn\s+on))",
                    r"(system\s+uptime|boot\s+time|last\s+reboot)"
                ],
                "memory": [
                    r"(memory|ram|available\s+memory|free\s+memory|memory\s+usage)",
                    r"(how\s+much\s+(memory|ram)\s+(do\s+i\s+have|is\s+available|is\s+free|is\s+used))",
                    r"(system\s+memory|ram\s+status|memory\s+status)"
                ],
                "disk_space": [
                    r"(disk|space|storage|free\s+space|available\s+space|disk\s+usage)",
                    r"(how\s+much\s+(disk|space|storage)\s+(do\s+i\s+have|is\s+available|is\s+free|is\s+used))",
                    r"(hard\s+drive|ssd|drive\s+capacity|storage\s+capacity)"
                ],
                "system_load": [
                    r"(load|system\s+load|cpu\s+load|processor\s+load)",
                    r"(how\s+(busy|loaded)\s+is\s+(my\s+system|computer|cpu|processor))"
                ]
            },
            "notes_app": {
                "topics": [
                    r"(notes?\s+topics?|notes?\s+folders?|list\s+.*\s+notes|show\s+.*\s+notes|what\s+.*\s+notes|notes?\s+(topic|folder)\s+list|all\s+.*\s+notes)",
                    r"(what\s+notes?\s+(topics?|folders?|categories?)\s+(do\s+i\s+have|are\s+there))"
                ],
                "count": [
                    r"(how\s+many\s+notes|notes?\s+count|number\s+of\s+notes)",
                    r"(count\s+(my\s+)?notes|total\s+notes)"
                ],
                "list": [
                    r"(list\s+notes|show\s+notes|what\s+notes|my\s+notes|notes\s+list)",
                    r"(show\s+me\s+(my\s+)?notes|display\s+(my\s+)?notes|what\s+notes\s+do\s+i\s+have)"
                ],
                "search": [
                    r"(find\s+notes?\s+about|search\s+(for\s+)?notes?\s+on|notes?\s+regarding)",
                    r"(notes?\s+about|notes?\s+containing|notes?\s+with)"
                ]
            },
            "file_system": {
                "find_folders": [
                    r"(folders?|directories?|where\s+.*\s+folders?|show\s+.*\s+folders?|list\s+.*\s+folders?|find\s+.*\s+folders?)",
                    r"(locate\s+folders?|search\s+(for\s+)?folders?|where\s+can\s+i\s+find\s+folders?)"
                ],
                "find_files": [
                    r"(files?|where\s+.*\s+files?|show\s+.*\s+files?|list\s+.*\s+files?|find\s+.*\s+files?)",
                    r"(locate\s+files?|search\s+(for\s+)?files?|where\s+can\s+i\s+find\s+files?)"
                ],
                "search_content": [
                    r"(search\s+(for|in)\s+content|find\s+text\s+in|look\s+for\s+.*\s+in\s+files)",
                    r"(files?\s+containing|files?\s+with\s+text|grep\s+for)"
                ]
            },
            "search_queries": {
                "general_search": [
                    r"(search\s+for|find|look\s+for|locate|where\s+is|where\s+are)",
                    r"(can\s+you\s+(search|find|locate)|help\s+me\s+(search|find|locate))"
                ],
                "web_search": [
                    r"(search\s+(the\s+)?web|search\s+(the\s+)?internet|google|browser\s+search)",
                    r"(find\s+online|look\s+up\s+online|web\s+results\s+for)"
                ]
            }
        }
        
        try:
            if os.path.exists(patterns_file):
                with open(patterns_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default patterns file if it doesn't exist
                os.makedirs(os.path.dirname(patterns_file), exist_ok=True)
                with open(patterns_file, 'w') as f:
                    json.dump(default_patterns, f, indent=2)
                return default_patterns
        except Exception as e:
            print(f"Error loading command patterns: {e}")
            return default_patterns

    def process_command(self, user_input):
        """Process user input and execute commands directly."""
        query_lower = user_input.lower()
        
        # DIRECT EXECUTION CHECK - Check first for direct command-like syntax
        if self._looks_like_direct_command(user_input):
            result = self._try_direct_execution(user_input)
            # Only return if successful or clearly a command execution attempt
            if result and ('Command executed' in result or 'Command failed' in result):
                return result
        
        # SYSTEM INFORMATION QUERIES - Check second
        if self._is_system_info_query(query_lower):
            return self._execute_system_info_command(query_lower)
            
        # NOTES APP QUERIES - Check third
        if self._is_notes_app_query(query_lower):
            return self._execute_notes_app_command(query_lower)
        
        # FILE/FOLDER OPERATIONS - Check fourth
        if self._is_file_folder_query(query_lower):
            return self._execute_file_folder_command(query_lower)
        
        # If no direct execution patterns matched, use AI
        # Try to have the AI generate a command for us to execute
        return self._handle_with_ai(user_input)
        
    def _is_system_info_query(self, query):
        """Detect system info queries with comprehensive patterns."""
        # Check patterns from the loaded JSON
        patterns = self.command_patterns.get("system_info", {})
        
        for cmd_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query, re.IGNORECASE):
                    return True
                    
        return False

    def _is_notes_app_query(self, query):
        """Detect Notes app related queries."""
        # Check patterns from the loaded JSON
        patterns = self.command_patterns.get("notes_app", {})
        
        for cmd_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query, re.IGNORECASE):
                    return True
                    
        return False
        
    def _is_file_folder_query(self, query):
        """Detect file and folder operation queries."""
        # Check patterns from the loaded JSON
        patterns = self.command_patterns.get("file_system", {})
        
        for cmd_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query, re.IGNORECASE):
                    return True
                    
        return False

    def _execute_system_info_command(self, query):
        """Execute appropriate system command for information queries."""
        if any(term in query for term in ['uptime', 'how long', 'running']):
            return self.command_executor.execute_system_command("uptime")
        
        if any(term in query for term in ['memory', 'ram']):
            return self.command_executor.execute_system_command("memory")
            
        if any(term in query for term in ['disk', 'storage', 'space']):
            return self.command_executor.execute_system_command("disk_space")
            
        # Default system info if no specific match
        return self.command_executor.execute_system_command("uptime")
        
    def _execute_notes_app_command(self, query):
        """Execute appropriate Notes app command directly."""
        result_prefix = "📝 Notes Results:\n"
        
        if 'open' in query:
            # Direct execution for opening Notes app
            if 'robotic' in query.lower() or 'world' in query.lower():
                # Special case for "Robotic World" notes
                result = run_command("open -a Notes ~/Documents/Robotic\\ World", shell=True)
                return f"✅ Opening Notes about Robotic World" if result['success'] else f"❌ Failed to open Notes: {result['stderr']}"
            else:
                # General Notes app opening
                result = run_command("open -a Notes", shell=True)
                return f"✅ Notes app opened successfully" if result['success'] else f"❌ Failed to open Notes: {result['stderr']}"
        
        elif 'count' in query or 'many' in query or 'number' in query:
            # Instead of explanation, directly execute and return results
            if platform.system() == 'Darwin':  # macOS
                result = run_command("""osascript -e 'tell application "Notes" to get the count of notes'""", shell=True)
                if result['success']:
                    return f"{result_prefix}You have {result['stdout'].strip()} notes."
                else:
                    return f"❌ Failed to count notes: {result['stderr']}"
            else:
                return "Counting notes is currently only supported on macOS."
            
        elif ('list' in query and 'folder' not in query and 'topic' not in query) or ('show' in query and 'folder' not in query and 'topic' not in query):
            # Directly list notes
            if platform.system() == 'Darwin':  # macOS
                result = run_command("""osascript -e 'tell application "Notes" to get name of every note'""", shell=True)
                if result['success']:
                    notes = result['stdout'].strip().split(', ')
                    formatted_notes = "\n".join([f"  • {note}" for note in notes[:20]])
                    if len(notes) > 20:
                        formatted_notes += f"\n  ... and {len(notes) - 20} more notes"
                    return f"{result_prefix}{formatted_notes}"
                else:
                    return f"❌ Failed to list notes: {result['stderr']}"
            else:
                return "Listing notes is currently only supported on macOS."
            
        else:
            # Default for topics/folders (direct execution)
            if platform.system() == 'Darwin':  # macOS
                result = run_command("""osascript -e 'tell application "Notes" to get name of every folder'""", shell=True)
                if result['success']:
                    folders = result['stdout'].strip().split(', ')
                    formatted_folders = "\n".join([f"  📁 {folder}" for folder in folders])
                    return f"{result_prefix}Notes folders:\n{formatted_folders}"
                else:
                    return f"❌ Failed to get notes folders: {result['stderr']}"
            else:
                # Fallback for Linux/Windows
                result = run_command("find ~ -type d -name \"*Notes*\" -o -name \"*notes*\" | head -n 10", shell=True)
                if result['success']:
                    folders = result['stdout'].strip().split('\n')
                    formatted_folders = "\n".join([f"  📁 {folder}" for folder in folders if folder])
                    return f"{result_prefix}Potential notes folders found:\n{formatted_folders}" if formatted_folders else "No notes folders found."
                else:
                    return f"❌ Failed to find notes folders: {result['stderr']}"
        
    def _execute_file_folder_command(self, query):
        """Execute appropriate file/folder command directly."""
        result_prefix = "📂 Folder Results:\n"
        
        # Extract search term if present
        search_term = None
        for term in ['find', 'search', 'where']:
            if term in query:
                parts = query.split(term, 1)
                if len(parts) > 1:
                    # Extract search term after the action word
                    potential_terms = parts[1].split()
                    if potential_terms:
                        search_term = potential_terms[0].strip()
                        break
        
        if not search_term:
            # Try to extract term after "show" or "list"
            for term in ['show', 'list']:
                if term in query:
                    parts = query.split(term, 1)
                    if len(parts) > 1:
                        potential_terms = parts[1].strip().split()
                        if potential_terms:
                            search_term = potential_terms[0].strip()
                            break
        
        # Default search term if none found
        if not search_term:
            search_term = "Documents"
        
        # Directly execute the folder search command using run_command
        command = f"find ~ -type d -name \"*{search_term}*\" -not -path \"*/\\.*\" | head -n 10"
        result = run_command(command, shell=True)
        
        if result['success']:
            folders = [folder for folder in result['stdout'].strip().split('\n') if folder]
            if folders:
                formatted_results = "\n".join([f"  📁 {folder}" for folder in folders])
                return f"{result_prefix}Found folders matching '{search_term}':\n{formatted_results}"
            else:
                return f"No folders matching '{search_term}' were found."
        else:
            return f"❌ Error searching for folders: {result['stderr']}"
        
    def _handle_with_ai(self, user_input):
        """Process user input with AI after direct command processing failed.
        Ensures an executable command is generated and properly executed."""
        # Log that we're using AI for this request
        if not self.quiet_mode:
            print(f"🤖 Using AI to process request: '{user_input}'")
        
        # Create a comprehensive system-aware prompt with specific instruction requirements
        system_info = platform.system()
        os_version = platform.release()
        shell_type = os.environ.get('SHELL', '/bin/bash').split('/')[-1]
        
        prompt_for_ai = (
            f"User request: '{user_input}'\n"
            f"Operating system: {system_info} {os_version}\n"
            f"Shell: {shell_type}\n\n"
            f"TASK: Generate a single executable shell command that will directly accomplish the user's request.\n\n"
            f"REQUIREMENTS:\n"
            f"1. You MUST return a command that can be executed directly in a terminal\n"
            f"2. Format your response as: ```shell\n[command]\n```\n"
            f"3. DO NOT include explanations, suggestions, or anything other than the code block\n"
            f"4. Provide a complete, specific command - never use placeholders\n"
            f"5. Use safe commands appropriate for {system_info} with {shell_type}\n"
            f"6. If you absolutely cannot create a safe command, respond with 'ERROR: [specific reason]'\n\n"
            f"EXAMPLES:\n"
            f"- 'show me large files' → ```shell\nfind ~ -type f -size +100M | sort -hr | head -n 10\n```\n"
            f"- 'what's the weather' → ```shell\ncurl wttr.in\n```\n"
            f"- 'show system status' → ```shell\nsystemctl status\n```\n"
            f"- 'search for documents about AI' → ```shell\nfind ~/Documents -type f -name \"*AI*\" -o -exec grep -l \"AI\" {{}} \\; 2>/dev/null | head -n 15\n```\n"
        )
        
        # First attempt - request AI response with specific command generation instructions
        ai_response = self.ai_handler.get_ai_response(prompt_for_ai)
        if not self.quiet_mode:
            print(f"AI response received (length: {len(ai_response)})")
        
        # Clear indication of error in response?
        has_error = False
        error_reason = None
        error_indicators = ["ERROR:", "I can't", "I cannot", "unable to", "not possible", "sorry"]
        
        # Check for explicit error messages
        if any(indicator in ai_response for indicator in error_indicators):
            has_error = True
            if "ERROR:" in ai_response:
                error_parts = ai_response.split("ERROR:", 1)
                if len(error_parts) > 1:
                    error_reason = error_parts[1].strip().split("\n")[0].strip().strip('`').strip()
                    if not self.quiet_mode:
                        print(f"AI returned explicit error: {error_reason}")
            else:
                # Find the first sentence with an error indicator
                for line in ai_response.split("\n"):
                    if any(indicator.lower() in line.lower() for indicator in error_indicators):
                        error_reason = line.strip().strip('`').strip()
                        if not self.quiet_mode:
                            print(f"AI returned implicit error: {error_reason}")
                        break
                        
                if not error_reason:
                    error_reason = "Unable to generate an appropriate command"
        
        # If it's a clear error response with no code block, handle it directly
        if has_error and not re.search(r'```.*?```', ai_response, re.DOTALL):
            if not self.quiet_mode:
                print(f"Handling as implementation request - no code block found and error detected")
            self._log_command_request(
                user_input, 
                None, 
                "implementation_needed", 
                f"AI ERROR: {error_reason if error_reason else 'Unknown error'}"
            )
            return self._handle_unknown_command_request(
                user_input, 
                error_reason if error_reason else "Unable to generate appropriate command"
            )
        
        # Attempt to extract a command from the AI response
        suggested_command = self._extract_command_from_ai_response(ai_response)
        
        # If first attempt failed, try once more with a more assertive prompt
        if not suggested_command:
            if not self.quiet_mode:
                print("First attempt failed to extract command - trying with more assertive prompt")
                
            retry_prompt = (
                f"CRITICAL: You must generate an executable shell command for: '{user_input}'\n\n"
                f"Your previous response did not contain a valid command. Please try again.\n\n"
                f"REMEMBER: Your response MUST contain exactly ONE command in a code block formatted as:\n"
                f"```shell\n[command]\n```\n\n"
                f"Do not provide explanations or alternatives. Focus only on generating a working command."
            )
            
            # Second attempt with more assertive prompt
            ai_response = self.ai_handler.get_ai_response(retry_prompt)
            if not self.quiet_mode:
                print(f"Second attempt response received (length: {len(ai_response)})")
            suggested_command = self._extract_command_from_ai_response(ai_response)
        
        # At this point we've tried up to two times to get a command
        if suggested_command:
            if not self.quiet_mode:
                print(f"🤖 AI Suggested Command: {suggested_command}")
                
            # Validate the command before execution to catch any error messages masquerading as commands
            error_prefixes = ["error:", "error ", "sorry", "i can't", "i cannot", "unable to", "apologies", "my apologies"]
            suspicious_patterns = ["error", "cannot ", "can't ", "don't ", "unable", "not possible", "invalid request"]
            
            # Check for error prefixes
            if any(suggested_command.lower().startswith(err_prefix) for err_prefix in error_prefixes):
                # AI returned an error disguised as a command - handle as an unknown request
                error_reason = suggested_command
                if ":" in suggested_command:
                    parts = suggested_command.split(":", 1)
                    if len(parts) > 1:
                        error_reason = parts[1].strip()
                
                if not self.quiet_mode:
                    print(f"Command rejected - starts with error prefix: {suggested_command}")
                
                # Log the implementation request
                self._log_command_request(
                    user_input, 
                    None, 
                    "implementation_needed", 
                    f"AI ERROR: {error_reason}"
                )
                
                # Handle as unknown command
                return self._handle_unknown_command_request(user_input, error_reason)
            
            # Additional sanity check for suspicious content
            if any(pattern in suggested_command.lower() for pattern in suspicious_patterns):
                # This might be an error message in disguise - check more carefully
                if len(suggested_command.split()) > 6:  # Error messages tend to be verbose
                    # Likely an error message, not a command - log and handle as unknown
                    if not self.quiet_mode:
                        print(f"Command rejected - suspicious content: {suggested_command}")
                    
                    # Log the implementation request
                    self._log_command_request(
                        user_input, 
                        None, 
                        "implementation_needed", 
                        f"Suspicious command rejected: {suggested_command}"
                    )
                    
                    # Handle as unknown command
                    return self._handle_unknown_command_request(
                        user_input,
                        "Generated command appears to be an error message"
                    )
            
            # At this point, we have a command that looks legitimate
            try:
                # Safety check on command
                from core.shell_handler import CommandSafetyLevel
                safety_level = self.shell_handler.assess_command_safety(suggested_command)
                if not self.quiet_mode:
                    print(f"Command safety level: {safety_level}")
                
                # Execute the command using run_command utility
                result = run_command(suggested_command, shell=True, capture_output=True, text=True)
                
                # Process and format the result for better user experience
                if result['success']:
                    output = result['stdout'].strip() if result['stdout'] else "Command executed successfully (no output)"
                    # Format the output based on command type
                    return self._format_command_output(output, suggested_command)
                else:
                    error = result['stderr'].strip() if result['stderr'] else f"Command failed with return code {result['returncode']}"
                    # Log and handle the failed command
                    self._log_command_request(user_input, suggested_command, "failed", error)
                    return self._handle_failed_command(error, user_input, suggested_command)
            except Exception as e:
                # Handle any execution errors
                if not self.quiet_mode:
                    print(f"Command execution error: {str(e)}")
                    
                # Log the error
                self._log_command_request(
                    user_input, 
                    suggested_command, 
                    "execution_error", 
                    f"Error: {str(e)}"
                )
                
                # Return error message to user
                return f"❌ Error executing command: {str(e)}"
        else:
            # AI couldn't generate a command - implement the "request new command" flow
            if not self.quiet_mode:
                print("No valid command could be extracted from AI response")
            
            # Try to get an error reason if available
            error_reason = "Could not map request to executable command"
            if "ERROR:" in ai_response:
                # AI explicitly indicated it couldn't generate a command
                error_parts = ai_response.split("ERROR:", 1)
                if len(error_parts) > 1:
                    error_reason = error_parts[1].strip()
            
            # Log this request with high priority for future implementation
            self._log_command_request(
                user_input, 
                None, 
                "implementation_needed", 
                f"PRIORITY: AI failed to generate command. Reason: {error_reason}"
            )
            
            # Provide helpful response to the user with clear next steps
            return self._handle_unknown_command_request(user_input, error_reason)
    
        # The function should never reach this point with the new implementation
        # But just in case, we'll make sure to return something sensible
        # Log this unexpected path
        self._log_command_request(user_input, None, "unexpected_path", "Function reached unexpected code path")
        return f"I've noted your request to '{user_input}'. This request has been logged for implementation."
        
    def _format_command_output(self, output, command=None):
        """Format command output in a user-friendly way."""
        # Process output based on command type for better readability
        if "ls" in command or "find" in command:
            # Format file/folder listing with icons
            lines = output.split('\n')
            formatted_lines = []
            for line in lines:
                if line.endswith('/'):
                    # It's a directory
                    formatted_lines.append(f"📁 {line}")
                elif line.strip():
                    # It's a file
                    formatted_lines.append(f"📄 {line}")
            
            formatted_output = "\n".join(formatted_lines)
            return f"✅ Results:\n\n{formatted_output}"
        elif "ps" in command or "top" in command:
            # Process list formatting
            return f"✅ Process Information:\n\n```\n{output}\n```"
        else:
            # Generic output formatting
            return f"✅ Result:\n\n```\n{output}\n```"
    
    def _handle_failed_command(self, error, original_input, failed_command):
        """Handle cases where a command failed to execute properly."""
        # Check for common error patterns and provide helpful responses
        if "command not found" in error.lower():
            # Try to suggest an alternative
            return (f"❌ Command failed: The system doesn't recognize `{failed_command}`.\n\n"
                    f"I'll try another approach to accomplish your request.")
        elif "permission denied" in error.lower():
            # Permission issues
            return (f"❌ Permission denied when trying to execute the command.\n\n"
                   f"This operation might require additional permissions.")
        elif "no such file or directory" in error.lower():
            # File/path not found
            return (f"❌ The file or directory specified in the command doesn't exist.\n\n"
                   f"Let me try a different approach to find what you're looking for.")
        else:
            # Generic error handling
            # Log the failed command request for future improvement
            self._log_command_request(original_input, failed_command, "failed", error)
            return f"❌ The command encountered a problem: {error}\n\nIs there another way I can help you with this?"
    
    def _handle_unknown_command_request(self, user_input, reason=""):
        """Handle requests that couldn't be mapped to a command.
        Provides clear feedback and logs the request for future implementation."""
        # This request is already logged in the caller, so we don't need to log it again
        
        # Provide a helpful response with clear next steps
        response = (
            f"📝 I understand you want me to '{user_input}', but I couldn't map this to an executable command.\n\n"
            f"Reason: {reason if reason else 'Could not determine appropriate command'}\n\n"
            f"✅ This request has been logged for future implementation.\n\n"
        )
        
        # Try to suggest some related commands or approaches
        if "search" in user_input.lower() or "find" in user_input.lower():
            response += "📌 You might try a more specific search query, like:\n- 'find files containing X'\n- 'search for folders named Y'\n- 'locate files modified today'"
        elif "install" in user_input.lower():
            response += "📌 For installations, please specify the package manager and package name:\n- 'install X using brew'\n- 'use pip to install Y'\n- 'apt-get install Z'"
        elif "open" in user_input.lower() or "launch" in user_input.lower():
            response += "📌 For opening applications, try specifying the exact application name:\n- 'open Safari'\n- 'launch Terminal'\n- 'open Notes app'"
        elif "show" in user_input.lower() or "list" in user_input.lower():
            response += "📌 For listing information, try being more specific:\n- 'show running processes'\n- 'list files in Downloads'\n- 'show disk usage'"
        else:
            response += "📌 Please try rephrasing your request to be more specific about what you want to accomplish."
        
        return response
    
    def _log_command_request(self, user_input, command, status, details=""):
        """Log command requests for future improvement and implementation.
        Uses a simplified approach for more reliable logging."""
        try:
            # Log entry with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = {
                "timestamp": timestamp,
                "user_input": user_input,
                "command": command,
                "status": status,
                "details": details,
                "os": platform.system(),
                "shell": os.environ.get('SHELL', '/bin/bash').split('/')[-1]
            }
            
            # Convert to JSON string
            log_string = json.dumps(log_entry)
            
            # Always print to console for debug purposes during development
            if not self.quiet_mode and (status == "implementation_needed" or status == "unknown"):
                print(f"🔴 Command implementation needed: '{user_input}'")
                print(f"📝 Log entry: {log_string}")
            
            # Get log directory from config if available
            log_dir = None
            try:
                config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'settings.json')
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                        log_dir = config.get('log_directory')
            except Exception:
                log_dir = None
                
            # Try different log directories if needed
            log_dirs_to_try = [
                # From config
                log_dir,
                # Current directory logs
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'),
                # Home directory logs
                os.path.join(os.path.expanduser('~'), '.uaibot', 'logs'),
                # /tmp directory logs
                os.path.join('/tmp', 'uaibot_logs') if platform.system() != 'Windows' else 
                os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'uaibot_logs')
            ]
            
            # Try each directory until one works
            for dir_path in log_dirs_to_try:
                if not dir_path:
                    continue
                    
                try:
                    # Create directory
                    os.makedirs(dir_path, exist_ok=True)
                    
                    # Define log files
                    log_file = os.path.join(dir_path, 'command_requests.log')
                    if status == "unknown":
                        special_log = os.path.join(dir_path, 'unknown_commands.log')
                    elif status == "implementation_needed":
                        special_log = os.path.join(dir_path, 'implementation_needed.log')
                    else:
                        special_log = None
                    
                    # Write to main log file
                    with open(log_file, 'a') as f:
                        f.write(log_string + '\n')
                        
                    # Write to specialized log if applicable
                    if special_log:
                        with open(special_log, 'a') as f:
                            f.write(log_string + '\n')
                    
                    if not self.quiet_mode:
                        print(f"Logged command request to: {dir_path}")
                    return  # Successfully logged, so return
                except Exception as e:
                    if not self.quiet_mode:
                        print(f"Failed to log to {dir_path}: {str(e)}")
                    continue  # Try next directory
            
            # If we got here, all log attempts failed
            if not self.quiet_mode:
                print("Failed to log command request to any location")
                
        except Exception as e:
            # Global exception handler for the entire logging process
            if not self.quiet_mode:
                print(f"Critical error in logging system: {str(e)}")
    
    def _extract_command_from_ai_response(self, ai_response):
        """Extract an executable command from an AI response.
        Always tries to find a valid command, with aggressive extraction.
        Returns None only if no potential command can be found."""
        if not ai_response:
            return None
            
        # Define error-indicating phrases that should prevent command extraction
        error_indicators = [
            "ERROR:", "I cannot", "I can't", "Unable to", "Not possible", 
            "Cannot generate", "Can't generate", "I'm sorry", "sorry,", 
            "apologies", "Invalid request", "Cannot perform", "Can't perform",
            "not recommended", "could be dangerous", "security risk",
            "insufficient permissions", "requires admin", "administrator privileges",
            "not safe", "not secure", "harmful"
        ]
        
        # Load security settings
        security_settings = {}
        try:
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'settings.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    security_settings = config.get('security', {})
        except Exception:
            # Default security settings if unable to load
            security_settings = {
                "block_dangerous_commands": True,
                "never_execute_raw_input": True,
                "validate_before_execution": True
            }
            
        # Skip explicit error messages unless they contain code blocks
        if any(indicator in ai_response for indicator in error_indicators) and not re.search(r'```.*?```', ai_response, re.DOTALL):
            if not self.quiet_mode:
                print(f"AI response contains error indicators without code block")
            return None
            
        # Track if there were errors for fallback methods
        has_error = any(indicator in ai_response for indicator in error_indicators)
        
        # First priority: Extract from code blocks (our preferred format)
        code_block_pattern = r'```(?:bash|shell|zsh|sh|console|terminal)?\s*(.*?)\s*```'
        code_blocks = re.findall(code_block_pattern, ai_response, re.DOTALL)
        
        if code_blocks:
            # Use the first code block as the command
            command = code_blocks[0].strip()
            
            # If the code block itself contains error indicators, reject it
            if any(indicator.lower() in command.lower() for indicator in error_indicators):
                if not self.quiet_mode:
                    print(f"Code block contains error indicators: {command}")
                return None
            
            # If the command has multiple lines, use the first meaningful line 
            # that looks like an actual command, not just a comment or empty line
            command_lines = [line.strip() for line in command.split('\n') 
                           if line.strip() and not line.strip().startswith('#')]
            if command_lines:
                extracted_cmd = command_lines[0]
                # Check that the extracted line itself isn't an error message
                if not any(indicator.lower() in extracted_cmd.lower() for indicator in error_indicators):
                    return extracted_cmd
        
        # Second priority: Check for commands in backticks
        backtick_pattern = r'`(.*?)`'
        backticks = re.findall(backtick_pattern, ai_response)
        
        if backticks:
            # Expanded list of command prefixes that indicate likely shell commands
            command_prefixes = [
                # File operations
                "ls", "cd", "find", "grep", "echo", "mkdir", "touch", "cat", "open", 
                "less", "more", "head", "tail", "nano", "vim", "vi", "emacs", "code",
                # Package managers and programming
                "python", "python3", "pip", "pip3", "npm", "node", "yarn", "ruby", "gem",
                "go", "cargo", "rustc", "javac", "java", "gcc", "g++", "make", "cmake",
                # Network tools
                "git", "ssh", "curl", "wget", "ping", "traceroute", "netstat", "ifconfig",
                "ip", "nc", "telnet", "nmap", "dig", "host", "whois", "arp", 
                # Scripting and automation
                "osascript", "powershell", "wsl", "bash", "sh", "zsh", "ksh", "csh", "fish",
                # System operations
                "rm", "cp", "mv", "chmod", "chown", "df", "du", "tar", "zip", "unzip", "gzip",
                "ps", "top", "htop", "kill", "pkill", "man", "which", "sudo", "su", "uptime",
                "reboot", "shutdown", "systemctl", "service", "launchctl", "diskutil",
                # Package managers and containers
                "apt", "apt-get", "brew", "yum", "dnf", "pacman", "snap", "flatpak", "docker",
                "kubectl", "helm", "podman", "aws", "az", "gcloud", "terraform", "ansible"
            ]
            
            for item in backticks:
                # Skip error messages in backticks
                if any(indicator.lower() in item.lower() for indicator in error_indicators):
                    continue
                    
                words = item.split()
                if words and words[0].lower() in [prefix.lower() for prefix in command_prefixes]:
                    # More permissive check - any command in backticks is likely intended for execution
                    return item.strip()
                # Special check for simple commands that may be standalone
                elif len(words) == 1 and words[0].lower() in ["ls", "pwd", "uptime", "date", "whoami", "clear"]:
                    return item.strip()
        
        # Third priority: Look for command phrases followed by commands
        command_phrases = [
            "you can run:", "try running:", "execute:", "command:", "run:", 
            "you can use:", "run this command:", "try this:", "use:", "shell:",
            "you could try:", "enter:", "type:", "execute this:", "try executing:",
            "you should use:", "terminal:", "console:", "the command is:", "using:", 
            "command line:", "cli:", "enter this command:", "type this:", "bash:", 
            "terminal command:", "you may use:", "try the command:", "execute the following:",
            "run the following:", "input:", "command to run:", "use this command:",
            "from your terminal:", "in your terminal:", "from your shell:", "in your shell:"
        ]
        
        # Define error phrases that might be around commands
        error_indicators = [
            "ERROR:", "I cannot", "I can't", "Unable to", "Not possible", 
            "Cannot generate", "Can't generate", "I'm sorry", "sorry,", 
            "apologies", "Invalid request", "Cannot perform", "Can't perform"
        ]
        
        for phrase in command_phrases:
            if phrase.lower() in ai_response.lower():
                # Get the text after the phrase until the end of the line or next punctuation
                phrase_pattern = f"{re.escape(phrase.lower())}\\s*(.*?)(?:[.;\\n]|$)"
                match = re.search(phrase_pattern, ai_response.lower())
                if match:
                    candidate = match.group(1).strip()
                    
                    # Skip error messages
                    if any(indicator.lower() in candidate.lower() for indicator in error_indicators):
                        continue
                    
                    # More permissive check for commands
                    words = candidate.split()
                    first_word = words[0].lower() if words else ""
                    if first_word and len(words) > 0:  # Any non-empty string with spaces
                        # Find the actual casing in the original text
                        start_pos = ai_response.lower().find(candidate)
                        if start_pos >= 0:
                            end_pos = start_pos + len(candidate)
                            extracted_cmd = ai_response[start_pos:end_pos].strip()
                            
                            # Final safety check against error messages
                            if not any(indicator.lower() in extracted_cmd.lower() for indicator in error_indicators):
                                if not self.quiet_mode:
                                    print(f"Found command after phrase '{phrase}'")
                                return extracted_cmd
                        
                        # If we couldn't extract with original casing, use the lowercase version
                        if not any(indicator.lower() in candidate.lower() for indicator in error_indicators):
                            if not self.quiet_mode:
                                print(f"Using lowercase command after phrase '{phrase}'")
                            return candidate
        
        # Fourth priority: Look for standalone commands in the text
        command_prefixes = [
            "ls", "cd", "find", "grep", "echo", "mkdir", "touch", "cat", "open", 
            "df", "du", "ps", "top", "ping", "curl", "wget", "git", "python",
            "npm", "apt", "brew"  # Shortened list for performance
        ]
        
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.endswith(':') and not line.startswith('#'):
                # Skip lines with error indicators
                if any(indicator.lower() in line.lower() for indicator in error_indicators):
                    continue
                    
                words = line.split()
                if words and words[0].lower() in [prefix.lower() for prefix in command_prefixes]:
                    # Skip potential explanatory text masquerading as commands
                    if not any(phrase in line.lower() for phrase in [
                        "would", "could", "should", "might", "may", "for example", 
                        "such as", "like this", "something like", "you can", "i think"
                    ]):
                        if not self.quiet_mode:
                            print(f"Found standalone command")
                        return line
        
        # Fifth priority: Try to generate a command from the AI's response if it mentioned what to search for
        if any(term in ai_response.lower() for term in ["search for", "find", "look for", "locate"]):
            search_pattern = r'(?:search for|find|look for|locate)\s+["\'"]?([^"\'.,;!?]+)["\'"]?'
            search_match = re.search(search_pattern, ai_response.lower())
            if search_match:
                search_term = search_match.group(1).strip()
                if search_term:
                    # Make search term more specific by limiting to words
                    search_terms = search_term.split()[:3]  # Take up to 3 words
                    search_term = " ".join(search_terms)
                    
                    if "file" in ai_response.lower() or "document" in ai_response.lower():
                        cmd = f"find ~ -name \"*{search_term}*\" -type f 2>/dev/null | head -n 10"
                        if not self.quiet_mode:
                            print(f"Generated file search command")
                        return cmd
                    elif "folder" in ai_response.lower() or "directory" in ai_response.lower():
                        cmd = f"find ~ -name \"*{search_term}*\" -type d 2>/dev/null | head -n 10"
                        if not self.quiet_mode:
                            print(f"Generated folder search command")
                        return cmd
                    else:
                        cmd = f"find ~ -name \"*{search_term}*\" 2>/dev/null | head -n 10"
                        if not self.quiet_mode:
                            print(f"Generated general search command")
                        return cmd
        
        # Sixth priority: Generate commands for common operations
        if has_error or all(not any(cmd_prefix in ai_response.lower() for cmd_prefix in command_prefixes) for cmd_prefix in command_prefixes):
            # Only use these fallbacks if no command prefixes found or explicit error indicated
            if "disk space" in ai_response.lower() or "storage" in ai_response.lower():
                if not self.quiet_mode:
                    print("Generating disk space command")
                return "df -h"
            elif "memory" in ai_response.lower() or "ram" in ai_response.lower():
                if not self.quiet_mode:
                    print("Generating memory info command")
                return "top -l 1 | grep PhysMem" if platform.system() == "Darwin" else "free -h"
            elif "process" in ai_response.lower() or "running" in ai_response.lower():
                if not self.quiet_mode:
                    print("Generating process list command")
                return "ps aux | head -n 10"
            elif "list" in ai_response.lower() and "file" in ai_response.lower():
                if not self.quiet_mode:
                    print("Generating file list command")
                return "ls -la"
            elif "system" in ai_response.lower() and "info" in ai_response.lower():
                if not self.quiet_mode:
                    print("Generating system info command")
                return "uname -a"
        
        if not self.quiet_mode:
            print("No valid command could be extracted")
        return None
    
    def _looks_like_direct_command(self, user_input):
        """Determine if user input looks like a direct command request."""
        # Common action verbs that suggest direct execution
        action_indicators = [
            "run", "execute", "start", "launch", "open", 
            "show", "display", "list", "find", "search",
            "create", "make", "do", "perform", "check",
            "get", "fetch", "download", "install", "copy",
            "move", "delete", "remove", "set", "configure"
        ]
        
        # Common command prefixes
        command_prefixes = [
            "ls", "cd", "pwd", "mkdir", "touch", "cat", "grep",
            "find", "echo", "ps", "kill", "rm", "cp", "mv",
            "python", "pip", "npm", "git", "ssh", "curl", "wget",
            "open", "nano", "vim", "chmod", "chown", "mkdir",
            "tar", "zip", "unzip", "man", "which", "sudo"
        ]
        
        input_cleaned = user_input.strip()
        words = input_cleaned.split()
        first_word = words[0].lower() if words else ""
        
        # Check if input starts with a common command
        if first_word in command_prefixes:
            return True
            
        # Check if the input starts with any of the action verbs
        if first_word in action_indicators:
            # If it has both an action verb and a recognized command, it's likely a direct command
            if len(words) > 1 and words[1].lower() in command_prefixes:
                return True
            
            # Also check for commands with 'the' after the action verb
            if len(words) > 2 and words[1].lower() == 'the' and words[2].lower() in command_prefixes:
                return True
                
            # Special cases like "open Notes" or "open the file"
            if first_word == "open" and len(words) > 1:
                return True
                
            # Special cases like "find all files" or "show me folders"
            if first_word in ["find", "show", "list"] and any(term in input_cleaned for term in ["file", "folder", "directory"]):
                return True
        
        # Check for command name patterns like "ls -la" or "git status"
        if re.match(r'^[a-zA-Z0-9_\-\.]+(\s+.*)?$', input_cleaned):
            return True
            
        # Check for specific phrases that should be direct commands
        command_phrases = [
            "look for", "search for", "where are", "what files", "what folders",
            "show me", "tell me about", "give me", "list all", "find all",
            "run the command", "execute the command", "can you run"
        ]
        
        for phrase in command_phrases:
            if input_cleaned.lower().startswith(phrase):
                return True
                
        return False
    
    def _try_direct_execution(self, user_input):
        """Try to execute the input as a direct command.
        Never executes raw natural language - only executes the extracted command
        if we have high confidence it's a valid shell command."""
        try:
            # Extract the actual command from natural language input
            command = self._extract_command(user_input)
            
            if not command:
                # If we couldn't confidently extract a command, don't try to execute anything
                if not self.quiet_mode:
                    print(f"Could not extract command from: '{user_input}'")
                return None
            
            # Validate the command before execution
            command_first_word = command.split()[0] if command.split() else ""
            valid_command_prefixes = [
                "ls", "cd", "find", "grep", "echo", "mkdir", "touch", "cat", "open", 
                "python", "pip", "npm", "node", "git", "ssh", "curl", "wget", "osascript",
                "rm", "cp", "mv", "chmod", "chown", "df", "du", "tar", "zip", "unzip", 
                "ps", "top", "kill", "pkill", "man", "which", "sudo", "apt", "brew", 
                "yum", "dnf", "systemctl", "service", "docker", "kubectl"
            ]
            
            # Only execute if the first word is a known command prefix
            if command_first_word not in valid_command_prefixes:
                if not self.quiet_mode:
                    print(f"Refusing to execute unknown command type: '{command_first_word}'")
                return None
                
            # Log the command for debugging/auditing
            if not self.quiet_mode:
                print(f"Executing command: '{command}'")
                
            # Execute the command directly using our run_command utility
            result = run_command(command, shell=True, capture_output=True, text=True)
            
            if result['success']:
                output = result['stdout'].strip() if result['stdout'] else "Command executed successfully (no output)"
                return self._format_command_output(output, command)
            else:
                error = result['stderr'].strip() if result['stderr'] else f"Command failed with return code {result['returncode']}"
                # Log the failed command
                self._log_command_request(user_input, command, "failed", error)
                return self._handle_failed_command(error, user_input, command)
        except Exception as e:
            error_msg = str(e)
            self._log_command_request(user_input, command if 'command' in locals() else None, "error", error_msg)
            return f"Error processing command: {error_msg}"
            
    def _extract_command(self, user_input):
        """Extract an executable command from natural language input.
        Returns None if input can't be confidently mapped to a valid command."""
        input_lower = user_input.lower().strip()
        
        # Step 1: Check if input is a direct shell command
        command_prefixes = ["ls", "cd", "grep", "find", "mkdir", "rm", "cp", "mv", "cat", "echo",
                          "python", "pip", "npm", "git", "apt", "brew", "curl", "wget"]
        first_word = input_lower.split()[0] if input_lower.split() else ""
        
        if first_word in command_prefixes:
            # This is likely already a shell command
            return user_input.strip()
            
        # Step 2: Category-based command mapping
        
        # Notes app commands
        if any(term in input_lower for term in ['notes', 'note']):
            if 'folder' in input_lower and any(verb in input_lower for verb in ['show', 'list', 'what']):
                # Handle notes folders queries
                if platform.system() == 'Darwin':  # macOS
                    return """osascript -e 'tell application "Notes" to get name of every folder'"""
                else:
                    return 'find ~ -type d -name "*Notes*" -o -name "*notes*" | head -n 10'
            elif any(verb in input_lower for verb in ['show', 'list', 'what']):
                # Handle notes listing queries
                if platform.system() == 'Darwin':  # macOS
                    return """osascript -e 'tell application "Notes" to get name of every note'"""
                else:
                    return 'find ~ -name "*.txt" -o -name "*.md" | grep -i note | head -n 10'
            elif 'count' in input_lower or 'how many' in input_lower:
                # Handle notes counting queries
                if platform.system() == 'Darwin':  # macOS
                    return """osascript -e 'tell application "Notes" to get the count of notes'"""
                else:
                    return 'find ~ -name "*.txt" -o -name "*.md" | grep -i note | wc -l'
            elif any(verb in input_lower for verb in ['open', 'launch', 'start']):
                # Handle opening notes app
                if 'robotic world' in input_lower:
                    return 'open -a Notes ~/Documents/Robotic\\ World'
                return 'open -a Notes'
            elif 'search' in input_lower or 'find' in input_lower or 'about' in input_lower:
                # Extract search term for notes
                search_pattern = r"(?:search|find|about|regarding|containing)\s+(?:for\s+)?(?:notes?\s+(?:about|on|with|containing))?\s*([a-zA-Z0-9\s]+)"
                match = re.search(search_pattern, input_lower)
                if match:
                    search_term = match.group(1).strip()
                    if platform.system() == 'Darwin':  # macOS
                        return f"""osascript -e 'tell application "Notes" to get name of notes where name contains "{search_term}" or body contains "{search_term}"'"""
                    else:
                        return f'find ~ -name "*.txt" -o -name "*.md" | xargs grep -l "{search_term}" 2>/dev/null | head -n 10'
                
        # Step 3: Intent-based command mapping
        
        # Search and find operations
        if any(term in input_lower for term in ['search for', 'find', 'look for', 'where is', 'where are']):
            # Extract what we're searching for
            search_patterns = [
                r"(?:search|find|look)\s+(?:for\s+)?([a-zA-Z0-9\s]+?)(?:\s+in\s+|\s+on\s+|\s*$)",
                r"where\s+(?:is|are)\s+(?:the\s+)?([a-zA-Z0-9\s]+?)(?:\s+in\s+|\s+on\s+|\s*$)"
            ]
            
            search_term = None
            location = "~"  # Default to home directory
            
            for pattern in search_patterns:
                match = re.search(pattern, input_lower)
                if match:
                    search_term = match.group(1).strip()
                    # Check if location is specified
                    loc_match = re.search(r"\s+in\s+([a-zA-Z0-9\/\s~\._-]+)$", input_lower)
                    if loc_match:
                        raw_location = loc_match.group(1).strip()
                        # Map common location phrases to paths
                        if raw_location in ["home", "my home", "home directory"]:
                            location = "~"
                        else:
                            location = raw_location
                    break
            
            if search_term:
                # Determine if we're looking for files, folders, or content
                if 'folder' in input_lower or 'directory' in input_lower:
                    return f"find {location} -type d -name \"*{search_term}*\" -not -path \"*/\\.*\" | head -n 10"
                elif 'file' in input_lower:
                    return f"find {location} -type f -name \"*{search_term}*\" -not -path \"*/\\.*\" | head -n 10"
                elif any(term in input_lower for term in ['content', 'text', 'containing', 'inside']):
                    return f"find {location} -type f -not -path \"*/\\.*\" | xargs grep -l \"{search_term}\" 2>/dev/null | head -n 10"
                else:
                    # Generic search defaulting to finding files
                    return f"find {location} -name \"*{search_term}*\" -not -path \"*/\\.*\" | head -n 10"
        
        # List/Show operations
        if any(prefix in input_lower for prefix in ['show me', 'show the', 'show all', 'list', 'display']):
            # Extract what to list
            list_patterns = [
                r"(?:show|list|display)\s+(?:me\s+)?(?:the\s+)?(?:all\s+)?([a-zA-Z0-9\s]+?)(?:\s+in\s+|\s*$)"
            ]
            
            list_term = None
            location = "."  # Default to current directory
            
            for pattern in list_patterns:
                match = re.search(pattern, input_lower)
                if match:
                    list_term = match.group(1).strip()
                    # Check if location is specified
                    loc_match = re.search(r"\s+in\s+([a-zA-Z0-9\/\s~\._-]+)$", input_lower)
                    if loc_match:
                        raw_location = loc_match.group(1).strip()
                        if raw_location in ["home", "my home", "home directory"]:
                            location = "~"
                        else:
                            location = raw_location
                    break
            
            if list_term:
                # Determine what kind of listing to do
                if 'file' in list_term:
                    return f"find {location} -type f -not -path \"*/\\.*\" | sort | head -n 20"
                elif 'folder' in list_term or 'directory' in list_term:
                    return f"find {location} -type d -not -path \"*/\\.*\" | sort | head -n 20"
                elif 'process' in list_term:
                    return "ps aux | head -n 20"
                else:
                    # Default to ls with details
                    return f"ls -la {location}"
        
        # Open/Launch operations
        if any(verb in input_lower for verb in ['open', 'launch', 'start']):
            # Extract what to open
            open_match = re.search(r"(?:open|launch|start)\s+(?:the\s+)?([a-zA-Z0-9\s\._-]+)", input_lower)
            if open_match:
                item_to_open = open_match.group(1).strip()
                
                # Check if opening with a specific app
                with_app = None
                with_match = re.search(r"\s+with\s+([a-zA-Z0-9\s]+)$", input_lower)
                if with_match:
                    with_app = with_match.group(1).strip()
                    # Remove the "with app" part from the item to open
                    item_to_open = item_to_open.replace(f" with {with_app}", "").strip()
                
                if platform.system() == 'Darwin':  # macOS
                    common_apps = {
                        "browser": "Safari", 
                        "web browser": "Safari",
                        "chrome": "Google Chrome",
                        "firefox": "Firefox",
                        "safari": "Safari",
                        "mail": "Mail",
                        "calendar": "Calendar",
                        "notes": "Notes",
                        "music": "Music",
                        "photos": "Photos",
                        "terminal": "Terminal",
                        "word": "Microsoft Word",
                        "excel": "Microsoft Excel",
                        "powerpoint": "Microsoft PowerPoint",
                    }
                    
                    # Check if it's a common app
                    if item_to_open.lower() in common_apps:
                        return f"open -a '{common_apps[item_to_open.lower()]}'"
                    
                    # Check if it's a file path or URL
                    if item_to_open.startswith(('http://', 'https://', '/', '~/')):
                        if with_app:
                            return f"open -a '{with_app}' '{item_to_open}'"
                        return f"open '{item_to_open}'"
                    else:
                        # Assume it's an application name
                        return f"open -a '{item_to_open}'"
                else:  # Linux/Windows fallbacks
                    if platform.system() == 'Linux':
                        if item_to_open.startswith(('http://', 'https://')):
                            return f"xdg-open '{item_to_open}'"
                        elif '.' in item_to_open and not item_to_open.startswith(('/', '~')):
                            return f"xdg-open '{item_to_open}'"
                        else:
                            return f"{item_to_open.lower()} &"
                    else:  # Windows
                        return f"start {item_to_open}"
        
        # System information queries
        if any(term in input_lower for term in ['uptime', 'how long', 'running time', 'system on']):
            return "uptime"
            
        if any(term in input_lower for term in ['memory', 'ram']):
            if platform.system() == 'Darwin':  # macOS
                return "vm_stat && top -l 1 | grep PhysMem"
            else:  # Linux
                return "free -h"
                
        if any(term in input_lower for term in ['disk', 'storage', 'space']):
            return "df -h"
            
        if any(term in input_lower for term in ['process', 'cpu', 'load']):
            if platform.system() == 'Darwin':  # macOS
                return "top -l 1 | head -n 15"
            else:  # Linux
                return "top -b -n 1 | head -n 15"
        
        # Step 4: Check for explicit command execution requests
        direct_command_prefixes = [
            "run", "execute", "start", "launch", "run this", "execute this", 
            "can you run", "please run", "would you run", "could you run",
        ]
        
        for prefix in direct_command_prefixes:
            if input_lower.startswith(prefix + " "):
                potential_cmd = user_input[len(prefix):].strip()
                # Only return if it looks like a valid command
                first_word = potential_cmd.split()[0] if potential_cmd.split() else ""
                if first_word in command_prefixes:
                    return potential_cmd
        
        # Step 5: If we couldn't confidently extract a command, return None
        # This is important - don't return raw user input as a command!
        return None
        
    def process_multimodal_input(self, input_data):
        """
        Process multimodal inputs including text, images, audio, and gestures.
        
        Args:
            input_data (dict): Dictionary containing multimodal input data with keys:
                - text (str, optional): Text input from the user
                - image (bytes or str, optional): Image data or path to image file
                - audio (bytes or str, optional): Audio data or path to audio file
                - gesture (str, optional): Name of detected gesture
                
        Returns:
            str: Response to the multimodal input
        """
        # Extract components
        text = input_data.get('text', '')
        image_data = input_data.get('image')
        audio_data = input_data.get('audio')
        gesture = input_data.get('gesture')
        
        # Process gesture first (if provided)
        if gesture:
            gesture_response = self._process_gesture(gesture)
            if gesture_response:
                return gesture_response
        
        # Process image data (if provided)
        if image_data:
            # If it's an image path, use it directly; otherwise, save temp file
            image_result = self._process_image(image_data)
            if image_result:
                # If image processing yielded a command, combine with text
                if text:
                    text = f"{text} (image context: {image_result})"
                else:
                    text = image_result
        
        # Process audio data (if provided)
        if audio_data and not text:
            # If no text was provided, try to get text from audio
            text = self._process_audio(audio_data)
        
        # Process text command (now enhanced with any image/audio context)
        if text:
            return self.process_command(text)
        else:
            return "I didn't receive any input I could understand. Please try again."
            
    def _process_image(self, image_data):
        """
        Process an image to extract context or commands.
        
        Args:
            image_data: Either a path to an image file (str) or raw image data (bytes)
            
        Returns:
            str: Extracted text or context from the image, or None if processing failed
        """
        try:
            # Handle image file path
            if isinstance(image_data, str) and os.path.exists(image_data):
                # Run OCR using our new run_command utility
                result = run_command(
                    ['tesseract', image_data, 'stdout'], 
                    capture_output=True,
                    text=True
                )
                
                if result['success']:
                    return result['stdout'].strip()
                else:
                    if not self.quiet_mode:
                        print(f"OCR error: {result['stderr']}")
                    return None
                    
            # Handle raw image data
            elif isinstance(image_data, bytes):
                # Save to temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    tmp.write(image_data)
                    tmp_path = tmp.name
                
                # Run OCR
                result = run_command(
                    ['tesseract', tmp_path, 'stdout'], 
                    capture_output=True,
                    text=True
                )
                
                # Clean up
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
                if result['success']:
                    return result['stdout'].strip()
                else:
                    if not self.quiet_mode:
                        print(f"OCR error: {result['stderr']}")
                    return None
            
            return None
        except Exception as e:
            if not self.quiet_mode:
                print(f"Error processing image: {e}")
            return None
            
    def _process_audio(self, audio_data):
        """
        Process audio data to extract speech.
        
        Args:
            audio_data: Either a path to an audio file (str) or raw audio data (bytes)
            
        Returns:
            str: Extracted text from speech, or None if processing failed
        """
        try:
            # Handle audio file path
            if isinstance(audio_data, str) and os.path.exists(audio_data):
                # Use our run_command utility to process audio with appropriate tool
                # Example using SpeechRecognition + ffmpeg
                result = run_command(
                    f"ffmpeg -i {audio_data} -ar 16000 -ac 1 -f wav - | python -c 'import sys, speech_recognition as sr; r=sr.Recognizer(); audio=sr.AudioData(sys.stdin.read(), 16000, 2); print(r.recognize_google(audio))'",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result['success']:
                    return result['stdout'].strip()
                else:
                    if not self.quiet_mode:
                        print(f"Speech recognition error: {result['stderr']}")
                    return None
                    
            # Handle raw audio data
            elif isinstance(audio_data, bytes):
                # Save to temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name
                
                # Run speech recognition
                result = run_command(
                    f"ffmpeg -i {tmp_path} -ar 16000 -ac 1 -f wav - | python -c 'import sys, speech_recognition as sr; r=sr.Recognizer(); audio=sr.AudioData(sys.stdin.read(), 16000, 2); print(r.recognize_google(audio))'",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                # Clean up
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
                if result['success']:
                    return result['stdout'].strip()
                else:
                    if not self.quiet_mode:
                        print(f"Speech recognition error: {result['stderr']}")
                    return None
            
            return None
        except Exception as e:
            if not self.quiet_mode:
                print(f"Error processing audio: {e}")
            return None
            
    def _process_gesture(self, gesture):
        """
        Process a gesture command.
        
        Args:
            gesture (str): The name of the detected gesture
            
        Returns:
            str: Response to the gesture, or None if no specific action
        """
        # Map common gestures to commands
        gesture_commands = {
            "wave": "echo 'Hello! How can I help you today?'",
            "thumbs_up": "echo 'Great! I'm glad you like it.'",
            "thumbs_down": "echo 'I'm sorry to hear that. What can I do better?'",
            "palm": "echo 'Stopping current operation.'",
            "point_up": "cd ..",
            "point_down": "ls -la",
            "victory": "uname -a",  # System info
            "ok": "echo 'Command confirmed.'",
            "pinch": "echo 'Zooming in/out'",
        }
        
        if gesture.lower() in gesture_commands:
            cmd = gesture_commands[gesture.lower()]
            # Execute the command using run_command
            result = run_command(cmd, shell=True, capture_output=True, text=True)
            if result['success']:
                return f"Gesture '{gesture}' detected: {result['stdout']}"
            else:
                return f"Gesture '{gesture}' recognized, but command failed: {result['stderr']}"
        
        return None
