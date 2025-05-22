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
from app.utils import get_project_root, run_command
from app.core.platform_commands import PlatformCommands
from app.core.command_processor.command_registry import CommandRegistry
from app.core.command_processor.command_executor import CommandExecutor
from app.core.parallel_utils import ParallelTaskManager, run_in_parallel
from app.core.command_processor.ai_command_extractor import AICommandExtractor
from app.utils.ai_json_tools import build_ai_prompt

# Simplified version of the command processor focused on handling natural language commands properly
class CommandProcessor:
    """
    Processes user commands and determines the appropriate handler.
    Supports natural language command processing with platform-aware commands.
    """
    
    def __init__(self, ai_handler, shell_handler, quiet_mode=False, fast_mode=False):
        """Initialize CommandProcessor with AI and shell handlers."""
        self.ai_handler = ai_handler
        self.shell_handler = shell_handler
        self.quiet_mode = quiet_mode
        self.fast_mode = fast_mode  # Add fast_mode flag to control termination behavior
        
        # Pass fast_mode to AI handler if possible
        if hasattr(ai_handler, 'fast_mode'):
            ai_handler.fast_mode = fast_mode
        
        self.system_platform = platform.system().lower()
        
        # Initialize platform commands helper
        self.platform_commands = PlatformCommands()
        
        # Initialize command registry and executor
        self.command_registry = CommandRegistry()
        self.command_executor = CommandExecutor()
        
        # Initialize AI command extractor
        self.command_extractor = AICommandExtractor()
        
        # Load command patterns from JSON file (Keeping for backward compatibility)
        self.command_patterns = self._load_command_patterns()
        
        # User settings
        self.user_settings = self._load_user_settings()
        
        # Output formatting settings
        self.color_settings = {
            "thinking": "\033[38;5;244m",  # Gray color for thinking process
            "success": "\033[38;5;34m",    # Green color for success
            "error": "\033[38;5;196m",     # Red color for errors
            "important": "\033[1;38;5;33m", # Bold blue for important info
            "reset": "\033[0m"             # Reset to default color
        }
        
        # Initialize output state tracking to prevent duplication
        self._thinking_shown = False
        self._command_shown = False
        self._result_shown = False
        
        # Iteration state tracking
        self.iteration_state = {
            "active": False,
            "current_step": 0,
            "total_steps": 0,
            "step_results": [],
            "current_operation": None,
            "last_updated": None
        }
        
        # Ensure user home path is correctly set
        self._detect_user_home_path()
        
        # Fix the undefined 'thinking' variable
        self.thinking = False  # Add this at the top of the file with other global variables
        
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
                ],
                "system_info": [
                    r"(what\s+system|which\s+system|what\s+os|operating\s+system|platform|distro|distribution)",
                    r"(what\s+(computer|machine|device)\s+(is\s+this|am\s+i\s+using|i'm\s+on|i\s+am\s+on))",
                    r"(system\s+information|os\s+version|kernel\s+version)"
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
                ],
                "create_file": [
                    r"(create|make|new)\s+(a\s+)?(text\s+)?file",
                    r"(write|save)\s+(a\s+)?(text\s+)?file",
                    r"(create|make|new)\s+(a\s+)?document"
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
            },
            "iteration": {
                "continue": [
                    r"(continue(\s+to)?\s+iterate\??)",
                    r"(keep\s+going|proceed|continue|next\s+step)",
                    r"(should\s+(we|i)\s+continue|go\s+on|move\s+forward)"
                ],
                "stop": [
                    r"(stop\s+iteration|end\s+iteration|cancel\s+iteration)",
                    r"(stop|halt|cancel|abort|enough)",
                    r"(no\s+more|that's\s+enough|that\s+is\s+enough)"
                ],
                "status": [
                    r"(iteration\s+status|current\s+status|where\s+are\s+we)",
                    r"(progress|how\s+far|how\s+many\s+(more|left))",
                    r"(status\s+update|progress\s+report)"
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

    def _load_user_settings(self):
        """Load user-specific settings from JSON file."""
        settings_file = os.path.join(get_project_root(), 'config', 'user_settings.json')
        default_settings = {
            "username": "",
            "full_name": "",
            "preferred_name": "",
            "home_directory": "",
            "preferred_locations": {
                "desktop": "",
                "documents": "",
                "downloads": ""
            }
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default settings file if it doesn't exist
                os.makedirs(os.path.dirname(settings_file), exist_ok=True)
                with open(settings_file, 'w') as f:
                    json.dump(default_settings, f, indent=2)
                return default_settings
        except Exception as e:
            print(f"Error loading user settings: {e}")
            return default_settings
            
    def _save_user_settings(self):
        """Save user settings to JSON file."""
        settings_file = os.path.join(get_project_root(), 'config', 'user_settings.json')
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.user_settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving user settings: {e}")
            return False
            
    def _detect_user_home_path(self):
        """Detect and store the user's actual home path."""
        # Get actual username and home directory
        username = os.environ.get('USER') or os.environ.get('USERNAME')
        home_dir = os.path.expanduser('~')
        
        # If we haven't stored this information or it's changed, update and ask to save
        if not self.user_settings.get("username") or self.user_settings.get("username") != username:
            self.user_settings["username"] = username
            # Only prompt in interactive mode and not in fast mode
            if not getattr(self, 'mode', 'interactive') == 'interactive' or getattr(self, 'fast_mode', False):
                # In non-interactive or fast mode, just set and skip prompt
                pass
            else:
                print(f"\n📋 I detected your username is '{username}'. Would you like me to remember this? (y/n)")
                response = input("> ").strip().lower()
                if response.startswith('y'):
                    self._save_user_settings()
                    print("✅ Username saved in settings.")
        
        # Update home directory if needed
        if not self.user_settings.get("home_directory") or self.user_settings.get("home_directory") != home_dir:
            self.user_settings["home_directory"] = home_dir
            
        # Update standard locations if not set
        if not self.user_settings["preferred_locations"].get("desktop") or not os.path.exists(self.user_settings["preferred_locations"].get("desktop")):
            desktop_path = os.path.join(home_dir, "Desktop")
            if os.path.exists(desktop_path):
                self.user_settings["preferred_locations"]["desktop"] = desktop_path
                
        if not self.user_settings["preferred_locations"].get("documents") or not os.path.exists(self.user_settings["preferred_locations"].get("documents")):
            documents_path = os.path.join(home_dir, "Documents")
            if os.path.exists(documents_path):
                self.user_settings["preferred_locations"]["documents"] = documents_path
                
        if not self.user_settings["preferred_locations"].get("downloads") or not os.path.exists(self.user_settings["preferred_locations"].get("downloads")):
            downloads_path = os.path.join(home_dir, "Downloads")
            if os.path.exists(downloads_path):
                self.user_settings["preferred_locations"]["downloads"] = downloads_path

    def process_command(self, user_input):
        """Process user input using AI-driven approach."""
        # Reset output state for new command
        self._reset_output_state()
        
        if not user_input.strip():
            return "Please enter a command or question."
        
        # Format thinking process that will be folded
        thinking = self._format_thinking(
            f"🤖 Processing your request: '{user_input}'\n\n"
            f"I'm thinking about how to handle this request...\n"
            f"Instead of using pattern matching, I'll ask the AI to interpret this request...\n"
            f"Getting the AI to provide a structured response..."
        )
        
        # Always handle with AI for all requests
        return self._handle_with_ai(user_input, thinking)
    
    def _reset_output_state(self):
        """Reset output state tracking to prevent duplication."""
        self._thinking_shown = False
        self._command_shown = False
        self._result_shown = False
        
    def _handle_with_ai(self, user_input, thinking=""):
        """Process user input with AI to generate an executable command."""
        # If thinking wasn't provided, generate it
        if not thinking:
            thinking = self._format_thinking(
                f"🤖 Processing your request: '{user_input}'\n\n"
                f"I'm thinking about how to best handle this...\n"
                f"Using AI to interpret your request and generate an appropriate response..."
            )
        
        # Use the unified AI prompt template
        prompt_for_ai = build_ai_prompt(user_input)
        
        # Get response from AI with timeout handling in fast mode
        try:
            # In fast mode, we'll use a shorter internal timeout
            ai_response = self.ai_handler.process_command(prompt_for_ai)
        except Exception as e:
            if self.fast_mode:
                # In fast mode, provide a simple error and let the program continue to exit
                return f"{thinking}\n\nError: Failed to get AI response: {str(e)}"
            else:
                # In normal mode, re-raise the exception
                raise
        
        # Extract command from AI response using the command extractor
        success, command, metadata = self.command_extractor.extract_command(ai_response)

        # If command is a JSON block, extract the 'command' field
        import json as _json
        if isinstance(command, str) and command.strip().startswith('{'):
            try:
                command_json = _json.loads(command)
                if isinstance(command_json, dict) and 'command' in command_json:
                    command = command_json['command']
            except Exception:
                pass
        
        # Format the result with colors
        result = f"{thinking}\n\n"
        
        if success and command:
            # Format the command with duplicate prevention
            command_display = self._format_command(command)
            if command_display:
                result += command_display + "\n\n"
            
            # Execute the command using the shell handler
            execution_result = self.shell_handler.execute_command(command)
            
            # Format the execution result with duplicate prevention
            result_display = self._format_result(execution_result, command, metadata)
            if result_display:
                result += result_display
            
            return result
        elif metadata["is_error"]:
            # Format error response
            error_text = f"{self.color_settings['error']}❌ {metadata['error_message']}{self.color_settings['reset']}"
            result_display = self._format_result(error_text, "Error", metadata)
            if result_display:
                result += result_display
            return result
        else:
            # If no command could be extracted, return the AI's response directly
            return f"{thinking}\n\n{self.color_settings['important']}💬 I couldn't find a specific command for that, but here's some information:{self.color_settings['reset']}\n\n{ai_response}"
    
    def _format_thinking(self, thinking_text):
        """Format the thinking process as a folded/collapsible section."""
        # Check if thinking has already been shown to prevent duplication
        if hasattr(self, '_thinking_shown') and self._thinking_shown:
            return ""
            
        # Mark thinking as shown
        self._thinking_shown = True
        
        formatted = f"{self.color_settings['thinking']}🤔 Thinking...\n"
        # Add a folded section indicator
        formatted += "┌───────────────────────────────────────────────┐\n"
        # Add the thinking content with proper indentation
        for line in thinking_text.split("\n"):
            formatted += f"│ {line.ljust(45)} │\n"
        formatted += "└───────────────────────────────────────────────┘"
        formatted += f"{self.color_settings['reset']}"
        return formatted
        
    def _format_command(self, command_text):
        """Format the command with duplicate prevention."""
        # Check if command has already been shown to prevent duplication
        if hasattr(self, '_command_shown') and self._command_shown:
            return ""
            
        # Mark command as shown
        self._command_shown = True
        
        # Format the command with colors
        return f"{self.color_settings['important']}📌 I'll execute this command:{self.color_settings['reset']} {command_text}"
        
    def _format_result(self, execution_result, command, metadata=None):
        """Format the execution result with duplicate prevention."""
        # Check if result has already been shown to prevent duplication
        if hasattr(self, '_result_shown') and self._result_shown:
            return ""
            
        # Mark result as shown
        self._result_shown = True
        
        # Format the result based on execution outcome
        if execution_result:
            if "Error" in execution_result or "not found" in execution_result.lower():
                result = f"{self.color_settings['error']}❌ There was a problem:{self.color_settings['reset']}\n{execution_result}\n"
                # In fast mode, skip fallback response to avoid delaying exit
                if not self.fast_mode:
                    # Provide a helpful explanation when command fails
                    result += f"\n{self.color_settings['important']}💡 Let me try a different approach:{self.color_settings['reset']}\n"
                    # Use metadata if available to inform the fallback
                    if metadata and metadata.get("explanation"):
                        result += f"{metadata['explanation']}\n\n"
                    fallback_response = self.ai_handler.process_command(f"The command '{command}' failed with: {execution_result}. Please provide information or explanation directly.")
                    # Extract a string from the dict if needed
                    if isinstance(fallback_response, dict):
                        fallback_response_str = fallback_response.get("command") or str(fallback_response)
                    else:
                        fallback_response_str = str(fallback_response)
                    result += fallback_response_str
                else:
                    # In fast mode, just add a simple message
                    result += f"\n{self.color_settings['important']}💡 Fast mode: Skipping fallback explanation.{self.color_settings['reset']}\n"
            else:
                result = f"{self.color_settings['success']}✅ Result:{self.color_settings['reset']}\n{execution_result}\n"
                # Add explanation if available
                if metadata and metadata.get("explanation"):
                    result += f"\n{self.color_settings['important']}📝 {metadata['explanation']}{self.color_settings['reset']}\n"
        else:
            result = f"{self.color_settings['success']}✅ Command executed successfully with no output.{self.color_settings['reset']}\n"
            # Add explanation if available
            if metadata and metadata.get("explanation"):
                result += f"\n{self.color_settings['important']}📝 {metadata['explanation']}{self.color_settings['reset']}\n"
            
        return result
        
    def _get_detailed_system_specs(self):
        """Get detailed system hardware specifications using the AI handler."""
        try:
            # Format the output with thinking process folded
            thinking = self._format_thinking("Checking your system specifications...\n"
                       "This might take a moment while I gather information about your hardware.\n"
                       "Collecting CPU, RAM, disk, and other hardware details...")
            
            # Get the system information directly without relying on AI
            specs = self._collect_system_info()
            
            # Format the final output with colors
            result = f"{thinking}\n\n{self.color_settings['important']}💻 Machine Specifications:{self.color_settings['reset']}\n"
            
            if isinstance(specs, dict):
                # Format the dictionary output nicely
                for category, details in specs.items():
                    result += f"\n{self.color_settings['success']}✅ {category}:{self.color_settings['reset']}\n"
                    if isinstance(details, dict):
                        for key, value in details.items():
                            result += f"   • {key}: {value}\n"
                    else:
                        result += f"   • {details}\n"
            else:
                # If it's just a string, pass it through
                result += specs
                
            return result
        except Exception as e:
            return f"{self.color_settings['error']}❌ Error collecting system specifications: {str(e)}{self.color_settings['reset']}"

    def _collect_system_info(self):
        """Collect system information directly without relying on AI."""
        import platform
        import os
        import psutil
        import subprocess
        from datetime import datetime
        
        specs = {}
        
        # System Info
        specs["System Information"] = {
            "OS": f"{platform.system()} {platform.release()}",
            "Architecture": platform.machine(),
            "Version": platform.version(),
            "Hostname": platform.node()
        }
        
        # CPU Info
        try:
            specs["CPU Information"] = {
                "Processor": platform.processor(),
                "Physical cores": psutil.cpu_count(logical=False),
                "Total cores": psutil.cpu_count(logical=True),
                "Current CPU usage": f"{psutil.cpu_percent()}%"
            }
        except Exception as e:
            specs["CPU Information"] = f"Error collecting CPU info: {str(e)}"
        
        # Memory Info
        try:
            mem = psutil.virtual_memory()
            specs["Memory Information"] = {
                "Total Memory": f"{mem.total / (1024**3):.2f} GB",
                "Available Memory": f"{mem.available / (1024**3):.2f} GB",
                "Used Memory": f"{mem.used / (1024**3):.2f} GB",
                "Memory Percentage": f"{mem.percent}%"
            }
        except Exception as e:
            specs["Memory Information"] = f"Error collecting memory info: {str(e)}"
        
        # Disk Info
        try:
            disk_info = {}
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.mountpoint] = {
                        "Total Size": f"{partition_usage.total / (1024**3):.2f} GB",
                        "Used": f"{partition_usage.used / (1024**3):.2f} GB",
                        "Free": f"{partition_usage.free / (1024**3):.2f} GB",
                        "Usage": f"{partition_usage.percent}%",
                        "File System Type": partition.fstype
                    }
                except PermissionError:
                    disk_info[partition.mountpoint] = "Permission denied"
            specs["Disk Information"] = disk_info
        except Exception as e:
            specs["Disk Information"] = f"Error collecting disk info: {str(e)}"
        
        # Network Info
        try:
            network_info = {}
            net_io = psutil.net_io_counters()
            network_info["Bytes Sent"] = f"{net_io.bytes_sent / (1024**2):.2f} MB"
            network_info["Bytes Received"] = f"{net_io.bytes_recv / (1024**2):.2f} MB"
            
            specs["Network Information"] = network_info
        except Exception as e:
            specs["Network Information"] = f"Error collecting network info: {str(e)}"
        
        # Additional distribution info if Linux
        if platform.system().lower() == 'linux':
            try:
                if os.path.exists('/etc/os-release'):
                    with open('/etc/os-release', 'r') as f:
                        lines = f.readlines()
                        distro_info = {}
                        for line in lines:
                            if '=' in line:
                                key, value = line.strip().split('=', 1)
                                distro_info[key] = value.strip('"')
                        
                        if 'NAME' in distro_info:
                            specs["System Information"]["Distribution"] = distro_info['NAME']
                        if 'VERSION' in distro_info:
                            specs["System Information"]["Distribution Version"] = distro_info['VERSION']
            except Exception as e:
                specs["System Information"]["Distribution Info"] = f"Error: {str(e)}"
                
        return specs

    def _extract_command_from_ai_response(self, ai_response):
        """Extract just the command from an AI response text."""
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
        
    def _execute_file_write_command(self, user_input):
        """Execute file write or append operations."""
        query_lower = user_input.lower()
        
        # Format thinking process
        thinking = self._format_thinking(
            f"Processing file write/append request...\n"
            f"Analyzing to extract the filename, content, and write mode...\n"
            f"Checking if this is an append or overwrite operation..."
        )
        
        # Step 1: Extract the filename
        filename = None
        file_patterns = [
            r'(?:to|into|in)\s+(?:file|text file|document|)\s+([^\s,]+\.[a-zA-Z0-9]+)', 
            r'(?:to|into|in)\s+(?:file|text file|document|)\s+([^\s,]+)',
            r'(?:file|text file|document)\s+([^\s,]+\.[a-zA-Z0-9]+)',
            r'([^\s,]+\.[a-zA-Z0-9]+)'
        ]
        
        # Arabic file patterns
        arabic_file_patterns = [
            r'(?:في|الى|إلى)\s+(?:ملف|الملف)\s+([^\s,]+\.[a-zA-Z0-9]+)',
            r'(?:في|الى|إلى)\s+(?:ملف|الملف)\s+([^\s,]+)',
            r'(?:ملف|الملف)\s+([^\\s,]+\.[a-zA-Z0-9]+)'
        ]
        
        # Try to find the filename
        for pattern in file_patterns + arabic_file_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filename = match.group(1)
                break
                
        if not filename:
            # If no filename found, look for test_files folder mention
            if 'test_files' in query_lower:
                # Check if a word after "test_files/" could be a filename
                test_files_match = re.search(r'test_files/([^\s,]+)', query_lower)
                if test_files_match:
                    filename = f"test_files/{test_files_match.group(1)}"
                else:
                    filename = "test_files/notes.txt"  # Default
            else:
                filename = "note.txt"  # Default
        
        # Step 2: Extract the content to write
        content = None
        
        # Check for content between quotes
        quote_patterns = [
            r"['\"]([^'\"]+)['\"]",  # Content in quotes
            r"(?:line|text|content|string)\s+['\"]?([^'\"\.]+)['\"]?", # Content after keywords
            r"(?:write|add|append|put)\s+['\"]?([^'\"\.]+)['\"]?\s+(?:to|in|into)"  # Content before file
        ]
        
        # Arabic content patterns
        arabic_content_patterns = [
            r"['\"]([^'\"]+)['\"]",  # Content in quotes (same for any language)
            r"(?:السطر|النص|المحتوى)\s+['\"]?([^'\"\.]+)['\"]?", # Content after Arabic keywords
            r"(?:اكتب|أكتب|اضف|أضف)\s+['\"]?([^'\"\.]+)['\"]?\s+(?:في|الى|إلى)"  # Arabic content before file
        ]
        
        for pattern in quote_patterns + arabic_content_patterns:
            match = re.search(pattern, user_input)  # Use original input to preserve case
            if match:
                content = match.group(1).strip()
                break
                
        # If still no content found, try a simpler approach
        if not content:
            # Look for content between specific keywords and file mentions
            write_terms = ['write', 'add', 'put', 'append', 'اكتب', 'أكتب', 'اضف', 'أضف']
            file_terms = ['file', 'document', 'text file', 'ملف', 'نص', 'مستند']
            
            for write_term in write_terms:
                if write_term in query_lower:
                    parts = query_lower.split(write_term, 1)[1]
                    for file_term in file_terms:
                        if file_term in parts:
                            content_part = parts.split(file_term)[0].strip()
                            if content_part:
                                # Use the content until the file term
                                content = content_part
                                break
                if content:
                    break
        
        # If still no content, set a default
        if not content:
            content = "This is a new line of text."
            
        # Step 3: Determine append or overwrite mode
        append_mode = False
        append_keywords = ['append', 'add', 'اضف', 'أضف']
        
        if any(keyword in query_lower for keyword in append_keywords):
            append_mode = True
            
        # Step 4: Execute the command
        # Make sure the directory exists if needed
        if '/' in filename or '\\' in filename:
            directory = os.path.dirname(filename)
            if directory:
                # Create directory if it doesn't exist
                try:
                    if not os.path.exists(directory):
                        os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    return f"{thinking}\n\n{self.color_settings['error']}❌ Error creating directory {directory}: {str(e)}{self.color_settings['reset']}"
                    
        # Determine the command based on OS and mode
        if self.platform_commands.is_windows:
            if append_mode:
                command = f'echo {content} >> "{filename}"'
            else:
                command = f'echo {content} > "{filename}"'
        else:  # Linux/macOS
            if append_mode:
                command = f"echo '{content}' >> {shlex.quote(filename)}"
            else:
                command = f"echo '{content}' > {shlex.quote(filename)}"
        
        # Initialize result string with thinking
        result = ""
        if thinking:
            result += thinking + "\n\n"
        
        # Format the command with duplicate prevention
        command_text = f"{'Appending' if append_mode else 'Writing'} to file '{filename}' with content: \"{content}\"\nCommand: {command}"
        command_display = self._format_command(command_text)
        
        if command_display:
            result += command_display + "\n\n"
        
        # Execute the command
        execution_result = self.shell_handler.execute_command(command)
        
        # Format the result with duplicate prevention
        if not execution_result or "Error" not in execution_result:
            success_text = f"{self.color_settings['success']}✅ {'Added' if append_mode else 'Wrote'} content to file '{filename}':{self.color_settings['reset']}" + \
                          f"\n{self.color_settings['important']}📝 Content:{self.color_settings['reset']} \"{content}\""
            result_display = self._format_result(success_text, command)
            
            if result_display:
                result += result_display
        else:
            error_text = f"{self.color_settings['error']}❌ Error writing to file: {execution_result}{self.color_settings['reset']}"
            result_display = self._format_result(error_text, command)
            
            if result_display:
                result += result_display
        
        return result

    def _execute_file_delete_command(self, user_input):
        """Execute file deletion operations."""
        query_lower = user_input.lower()
        
        # Format thinking process
        thinking = self._format_thinking(
            f"Processing file deletion request...\n"
            f"Analyzing to extract the filename...\n"
            f"Checking for safety considerations..."
        )
        
        # Step 1: Extract the filename
        filename = None
        
        # Common patterns for file mentions in deletion commands
        file_patterns = [
            r'(?:delete|remove|trash|erase)\s+(?:the\s+)?(?:file|text file|document)?\s+([^\s,\.]+\.[a-zA-Z0-9]+)',
            r'(?:delete|remove|trash|erase)\s+(?:the\s+)?([^\s,\.]+\.[a-zA-Z0-9]+)',
            r'([^\s,\.]+\.[a-zA-Z0-9]+)\s+(?:file|text file|document)?\s+(?:delete|remove|trash|erase)'
        ]
        
        # Arabic file patterns for deletion
        arabic_file_patterns = [
            r'(?:احذف|امسح|ازل|أزل)\s+(?:ال|ملف|الملف)?\s+([^\s,\.]+\.[a-zA-Z0-9]+)',
            r'(?:احذف|امسح|ازل|أزل)\s+([^\س,\.]+\.[a-zA-Z0-9]+)'
        ]
        
        # Try to extract the filename
        for pattern in file_patterns + arabic_file_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filename = match.group(1)
                break
                
        # Special handling for test_files directory
        if not filename and 'test_files' in query_lower:
            # Look for patterns like "test_files/filename.txt"
            test_file_match = re.search(r'test_files/([^\s,\.]+\.[a-zA-Z0-9]+)', query_lower)
            if test_file_match:
                filename = f"test_files/{test_file_match.group(1)}"
            else:
                # Default to notes.txt in test_files if mentioned
                filename = "test_files/notes.txt"
        
        # Initialize result string with thinking
        result = ""
        if thinking:
            result += thinking + "\n\n"
        
        if not filename:
            # If no filename could be detected
            error_text = f"{self.color_settings['error']}❌ Unable to determine which file to delete from your request.{self.color_settings['reset']}\n" + \
                       f"Please specify a filename, for example: 'delete myfile.txt' or 'احذف ملف myfile.txt'"
            return result + error_text
        
        # Step 2: Check if file exists before deleting
        if not os.path.exists(filename):
            # Try to find the file in common locations
            found = False
            
            # Check in desktop, documents, downloads
            common_locations = []
            
            if self.user_settings["preferred_locations"].get("desktop"):
                common_locations.append(os.path.join(self.user_settings["preferred_locations"]["desktop"], filename))
            
            if self.user_settings["preferred_locations"].get("documents"):
                common_locations.append(os.path.join(self.user_settings["preferred_locations"]["documents"], filename))
                
            if self.user_settings["preferred_locations"].get("downloads"):
                common_locations.append(os.path.join(self.user_settings["preferred_locations"]["downloads"], filename))
            
            # Check if file exists in any of these locations
            for location in common_locations:
                if os.path.exists(location):
                    filename = location
                    found = True
                    break
            
            if not found:
                # If file not found anywhere
                error_text = f"{self.color_settings['error']}❌ File '{filename}' not found.{self.color_settings['reset']}\n" + \
                       f"Please check if the file exists and provide the correct path."
                return result + error_text
        
        # Step 3: Delete the file
        try:
            # Get confirmation from user (if not in quiet mode)
            if not self.quiet_mode:
                print(f"\nAre you sure you want to delete '{filename}'? (y/n)")
                confirmation = input("> ").lower().strip()
                if confirmation != 'y' and confirmation != 'yes':
                    cancel_text = f"{self.color_settings['important']}ℹ️ File deletion cancelled.{self.color_settings['reset']}"
                    return result + cancel_text
            
            # Determine the command based on OS
            if self.platform_commands.is_windows:
                command = f'del "{filename}"'
            else:  # Linux/macOS
                command = f"rm {shlex.quote(filename)}"
            
            # Format the command with duplicate prevention
            command_text = f"Deleting file: {command}"
            command_display = self._format_command(command_text)
            
            if command_display:
                result += command_display + "\n\n"
            
            # Execute the command
            execution_result = self.shell_handler.execute_command(command)
            
            # Check if the file was actually deleted
            file_exists = os.path.exists(filename)
            
            if not file_exists and (not execution_result or "Error" not in execution_result):
                success_text = f"{self.color_settings['success']}✅ Successfully deleted file '{filename}'.{self.color_settings['reset']}"
                result_display = self._format_result(success_text, command)
                if result_display:
                    result += result_display
                return result
            else:
                if execution_result:
                    error_text = f"{self.color_settings['error']}❌ Error deleting file: {execution_result}{self.color_settings['reset']}"
                    result_display = self._format_result(error_text, command)
                    if result_display:
                        result += result_display
                    return result
                else:
                    error_text = f"{self.color_settings['error']}❌ Failed to delete file '{filename}'. The file still exists.{self.color_settings['reset']}"
                    result_display = self._format_result(error_text, command)
                    if result_display:
                        result += result_display
                    return result
                
        except Exception as e:
            error_text = f"{self.color_settings['error']}❌ Error deleting file: {str(e)}{self.color_settings['reset']}"
            return result + error_text

    def process_request(self, request: str) -> Dict[str, Any]:
        """
        Process a user request and return the result.
        
        Args:
            request: The user request string
            
        Returns:
            Dictionary containing the processing result
        """
        # Check if we're in quiet mode
        if self._quiet_mode:
            # Don't show thinking message in quiet mode
            pass
        else:
            # Show thinking message if not already shown
            if not self._thinking_shown:
                print("Thinking...")
                self._thinking_shown = True
        
        # Get platform information for context
        platform_info = self._get_platform_info()
        
        # Format the AI prompt with the request and platform info
        ai_prompt = self._ai_command_extractor.format_ai_prompt(request, platform_info)
        
        # Get the AI response
        ai_response = self._ai_handler.process_command(ai_prompt)
        
        # Use parallel extraction for better performance
        success, command, metadata = self._ai_command_extractor.extract_command_parallel(ai_response)
        
        # Format the result with colors
        result = f"{thinking}\n\n"
        
        if success and command:
            # Format the command with duplicate prevention
            command_display = self._format_command(command)
            if command_display:
                result += command_display + "\n\n"
            
            # Execute the command using the shell handler
            execution_result = self.shell_handler.execute_command(command)
            
            # Format the execution result with duplicate prevention
            result_display = self._format_result(execution_result, command, metadata)
            if result_display:
                result += result_display
            
            return result
        elif metadata["is_error"]:
            # Format error response
            error_text = f"{self.color_settings['error']}❌ {metadata['error_message']}{self.color_settings['reset']}"
            result_display = self._format_result(error_text, "Error", metadata)
            if result_display:
                result += result_display
            return result
        else:
            # If no command could be extracted, return the AI's response directly
            return f"{thinking}\n\n{self.color_settings['important']}💬 I couldn't find a specific command for that, but here's some information:{self.color_settings['reset']}\n\n{ai_response}"
    
    def _format_thinking(self, thinking_text):
        """Format the thinking process as a folded/collapsible section."""
        # Check if thinking has already been shown to prevent duplication
        if hasattr(self, '_thinking_shown') and self._thinking_shown:
            return ""
            
        # Mark thinking as shown
        self._thinking_shown = True
        
        formatted = f"{self.color_settings['thinking']}🤔 Thinking...\n"
        # Add a folded section indicator
        formatted += "┌───────────────────────────────────────────────┐\n"
        # Add the thinking content with proper indentation
        for line in thinking_text.split("\n"):
            formatted += f"│ {line.ljust(45)} │\n"
        formatted += "└───────────────────────────────────────────────┘"
        formatted += f"{self.color_settings['reset']}"
        return formatted
        
    def _format_command(self, command_text):
        """Format the command with duplicate prevention."""
        # Check if command has already been shown to prevent duplication
        if hasattr(self, '_command_shown') and self._command_shown:
            return ""
            
        # Mark command as shown
        self._command_shown = True
        
        # Format the command with colors
        return f"{self.color_settings['important']}📌 I'll execute this command:{self.color_settings['reset']} {command_text}"
        
    def _format_result(self, execution_result, command, metadata=None):
        """Format the execution result with duplicate prevention."""
        # Check if result has already been shown to prevent duplication
        if hasattr(self, '_result_shown') and self._result_shown:
            return ""
            
        # Mark result as shown
        self._result_shown = True
        
        # Format the result based on execution outcome
        if execution_result:
            if "Error" in execution_result or "not found" in execution_result.lower():
                result = f"{self.color_settings['error']}❌ There was a problem:{self.color_settings['reset']}\n{execution_result}\n"
                # In fast mode, skip fallback response to avoid delaying exit
                if not self.fast_mode:
                    # Provide a helpful explanation when command fails
                    result += f"\n{self.color_settings['important']}💡 Let me try a different approach:{self.color_settings['reset']}\n"
                    # Use metadata if available to inform the fallback
                    if metadata and metadata.get("explanation"):
                        result += f"{metadata['explanation']}\n\n"
                    fallback_response = self.ai_handler.process_command(f"The command '{command}' failed with: {execution_result}. Please provide information or explanation directly.")
                    # Extract a string from the dict if needed
                    if isinstance(fallback_response, dict):
                        fallback_response_str = fallback_response.get("command") or str(fallback_response)
                    else:
                        fallback_response_str = str(fallback_response)
                    result += fallback_response_str
                else:
                    # In fast mode, just add a simple message
                    result += f"\n{self.color_settings['important']}💡 Fast mode: Skipping fallback explanation.{self.color_settings['reset']}\n"
            else:
                result = f"{self.color_settings['success']}✅ Result:{self.color_settings['reset']}\n{execution_result}\n"
                # Add explanation if available
                if metadata and metadata.get("explanation"):
                    result += f"\n{self.color_settings['important']}📝 {metadata['explanation']}{self.color_settings['reset']}\n"
        else:
            result = f"{self.color_settings['success']}✅ Command executed successfully with no output.{self.color_settings['reset']}\n"
            # Add explanation if available
            if metadata and metadata.get("explanation"):
                result += f"\n{self.color_settings['important']}📝 {metadata['explanation']}{self.color_settings['reset']}\n"
            
        return result
        
    def _get_detailed_system_specs(self):
        """Get detailed system hardware specifications using the AI handler."""
        try:
            # Format the output with thinking process folded
            thinking = self._format_thinking("Checking your system specifications...\n"
                       "This might take a moment while I gather information about your hardware.\n"
                       "Collecting CPU, RAM, disk, and other hardware details...")
            
            # Get the system information directly without relying on AI
            specs = self._collect_system_info()
            
            # Format the final output with colors
            result = f"{thinking}\n\n{self.color_settings['important']}💻 Machine Specifications:{self.color_settings['reset']}\n"
            
            if isinstance(specs, dict):
                # Format the dictionary output nicely
                for category, details in specs.items():
                    result += f"\n{self.color_settings['success']}✅ {category}:{self.color_settings['reset']}\n"
                    if isinstance(details, dict):
                        for key, value in details.items():
                            result += f"   • {key}: {value}\n"
                    else:
                        result += f"   • {details}\n"
            else:
                # If it's just a string, pass it through
                result += specs
                
            return result
        except Exception as e:
            return f"{self.color_settings['error']}❌ Error collecting system specifications: {str(e)}{self.color_settings['reset']}"

    def _collect_system_info(self):
        """Collect system information directly without relying on AI."""
        import platform
        import os
        import psutil
        import subprocess
        from datetime import datetime
        
        specs = {}
        
        # System Info
        specs["System Information"] = {
            "OS": f"{platform.system()} {platform.release()}",
            "Architecture": platform.machine(),
            "Version": platform.version(),
            "Hostname": platform.node()
        }
        
        # CPU Info
        try:
            specs["CPU Information"] = {
                "Processor": platform.processor(),
                "Physical cores": psutil.cpu_count(logical=False),
                "Total cores": psutil.cpu_count(logical=True),
                "Current CPU usage": f"{psutil.cpu_percent()}%"
            }
        except Exception as e:
            specs["CPU Information"] = f"Error collecting CPU info: {str(e)}"
        
        # Memory Info
        try:
            mem = psutil.virtual_memory()
            specs["Memory Information"] = {
                "Total Memory": f"{mem.total / (1024**3):.2f} GB",
                "Available Memory": f"{mem.available / (1024**3):.2f} GB",
                "Used Memory": f"{mem.used / (1024**3):.2f} GB",
                "Memory Percentage": f"{mem.percent}%"
            }
        except Exception as e:
            specs["Memory Information"] = f"Error collecting memory info: {str(e)}"
        
        # Disk Info
        try:
            disk_info = {}
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.mountpoint] = {
                        "Total Size": f"{partition_usage.total / (1024**3):.2f} GB",
                        "Used": f"{partition_usage.used / (1024**3):.2f} GB",
                        "Free": f"{partition_usage.free / (1024**3):.2f} GB",
                        "Usage": f"{partition_usage.percent}%",
                        "File System Type": partition.fstype
                    }
                except PermissionError:
                    disk_info[partition.mountpoint] = "Permission denied"
            specs["Disk Information"] = disk_info
        except Exception as e:
            specs["Disk Information"] = f"Error collecting disk info: {str(e)}"
        
        # Network Info
        try:
            network_info = {}
            net_io = psutil.net_io_counters()
            network_info["Bytes Sent"] = f"{net_io.bytes_sent / (1024**2):.2f} MB"
            network_info["Bytes Received"] = f"{net_io.bytes_recv / (1024**2):.2f} MB"
            
            specs["Network Information"] = network_info
        except Exception as e:
            specs["Network Information"] = f"Error collecting network info: {str(e)}"
        
        # Additional distribution info if Linux
        if platform.system().lower() == 'linux':
            try:
                if os.path.exists('/etc/os-release'):
                    with open('/etc/os-release', 'r') as f:
                        lines = f.readlines()
                        distro_info = {}
                        for line in lines:
                            if '=' in line:
                                key, value = line.strip().split('=', 1)
                                distro_info[key] = value.strip('"')
                        
                        if 'NAME' in distro_info:
                            specs["System Information"]["Distribution"] = distro_info['NAME']
                        if 'VERSION' in distro_info:
                            specs["System Information"]["Distribution Version"] = distro_info['VERSION']
            except Exception as e:
                specs["System Information"]["Distribution Info"] = f"Error: {str(e)}"
                
        return specs

    def _extract_command_from_ai_response(self, ai_response):
        """Extract just the command from an AI response text."""
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
        
    def _execute_file_write_command(self, user_input):
        """Execute file write or append operations."""
        query_lower = user_input.lower()
        
        # Format thinking process
        thinking = self._format_thinking(
            f"Processing file write/append request...\n"
            f"Analyzing to extract the filename, content, and write mode...\n"
            f"Checking if this is an append or overwrite operation..."
        )
        
        # Step 1: Extract the filename
        filename = None
        file_patterns = [
            r'(?:to|into|in)\s+(?:file|text file|document|)\s+([^\s,]+\.[a-zA-Z0-9]+)', 
            r'(?:to|into|in)\s+(?:file|text file|document|)\s+([^\s,]+)',
            r'(?:file|text file|document)\s+([^\s,]+\.[a-zA-Z0-9]+)',
            r'([^\s,]+\.[a-zA-Z0-9]+)'
        ]
        
        # Arabic file patterns
        arabic_file_patterns = [
            r'(?:في|الى|إلى)\s+(?:ملف|الملف)\s+([^\s,]+\.[a-zA-Z0-9]+)',
            r'(?:في|الى|إلى)\s+(?:ملف|الملف)\s+([^\s,]+)',
            r'(?:ملف|الملف)\s+([^\\s,]+\.[a-zA-Z0-9]+)'
        ]
        
        # Try to find the filename
        for pattern in file_patterns + arabic_file_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filename = match.group(1)
                break
                
        if not filename:
            # If no filename found, look for test_files folder mention
            if 'test_files' in query_lower:
                # Check if a word after "test_files/" could be a filename
                test_files_match = re.search(r'test_files/([^\s,]+)', query_lower)
                if test_files_match:
                    filename = f"test_files/{test_files_match.group(1)}"
                else:
                    filename = "test_files/notes.txt"  # Default
            else:
                filename = "note.txt"  # Default
        
        # Step 2: Extract the content to write
        content = None
        
        # Check for content between quotes
        quote_patterns = [
            r"['\"]([^'\"]+)['\"]",  # Content in quotes
            r"(?:line|text|content|string)\s+['\"]?([^'\"\.]+)['\"]?", # Content after keywords
            r"(?:write|add|append|put)\s+['\"]?([^'\"\.]+)['\"]?\s+(?:to|in|into)"  # Content before file
        ]
        
        # Arabic content patterns
        arabic_content_patterns = [
            r"['\"]([^'\"]+)['\"]",  # Content in quotes (same for any language)
            r"(?:السطر|النص|المحتوى)\s+['\"]?([^'\"\.]+)['\"]?", # Content after Arabic keywords
            r"(?:اكتب|أكتب|اضف|أضف)\s+['\"]?([^'\"\.]+)['\"]?\s+(?:في|الى|إلى)"  # Arabic content before file
        ]
        
        for pattern in quote_patterns + arabic_content_patterns:
            match = re.search(pattern, user_input)  # Use original input to preserve case
            if match:
                content = match.group(1).strip()
                break
                
        # If still no content found, try a simpler approach
        if not content:
            # Look for content between specific keywords and file mentions
            write_terms = ['write', 'add', 'put', 'append', 'اكتب', 'أكتب', 'اضف', 'أضف']
            file_terms = ['file', 'document', 'text file', 'ملف', 'نص', 'مستند']
            
            for write_term in write_terms:
                if write_term in query_lower:
                    parts = query_lower.split(write_term, 1)[1]
                    for file_term in file_terms:
                        if file_term in parts:
                            content_part = parts.split(file_term)[0].strip()
                            if content_part:
                                # Use the content until the file term
                                content = content_part
                                break
                if content:
                    break
        
        # If still no content, set a default
        if not content:
            content = "This is a new line of text."
            
        # Step 3: Determine append or overwrite mode
        append_mode = False
        append_keywords = ['append', 'add', 'اضف', 'أضف']
        
        if any(keyword in query_lower for keyword in append_keywords):
            append_mode = True
            
        # Step 4: Execute the command
        # Make sure the directory exists if needed
        if '/' in filename or '\\' in filename:
            directory = os.path.dirname(filename)
            if directory:
                # Create directory if it doesn't exist
                try:
                    if not os.path.exists(directory):
                        os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    return f"{thinking}\n\n{self.color_settings['error']}❌ Error creating directory {directory}: {str(e)}{self.color_settings['reset']}"
                    
        # Determine the command based on OS and mode
        if self.platform_commands.is_windows:
            if append_mode:
                command = f'echo {content} >> "{filename}"'
            else:
                command = f'echo {content} > "{filename}"'
        else:  # Linux/macOS
            if append_mode:
                command = f"echo '{content}' >> {shlex.quote(filename)}"
            else:
                command = f"echo '{content}' > {shlex.quote(filename)}"
        
        # Initialize result string with thinking
        result = ""
        if thinking:
            result += thinking + "\n\n"
        
        # Format the command with duplicate prevention
        command_text = f"{'Appending' if append_mode else 'Writing'} to file '{filename}' with content: \"{content}\"\nCommand: {command}"
        command_display = self._format_command(command_text)
        
        if command_display:
            result += command_display + "\n\n"
        
        # Execute the command
        execution_result = self.shell_handler.execute_command(command)
        
        # Format the result with duplicate prevention
        if not execution_result or "Error" not in execution_result:
            success_text = f"{self.color_settings['success']}✅ {'Added' if append_mode else 'Wrote'} content to file '{filename}':{self.color_settings['reset']}" + \
                          f"\n{self.color_settings['important']}📝 Content:{self.color_settings['reset']} \"{content}\""
            result_display = self._format_result(success_text, command)
            
            if result_display:
                result += result_display
        else:
            error_text = f"{self.color_settings['error']}❌ Error writing to file: {execution_result}{self.color_settings['reset']}"
            result_display = self._format_result(error_text, command)
            
            if result_display:
                result += result_display
        
        return result

    def _execute_file_delete_command(self, user_input):
        """Execute file deletion operations."""
        query_lower = user_input.lower()
        
        # Format thinking process
        thinking = self._format_thinking(
            f"Processing file deletion request...\n"
            f"Analyzing to extract the filename...\n"
            f"Checking for safety considerations..."
        )
        
        # Step 1: Extract the filename
        filename = None
        
        # Common patterns for file mentions in deletion commands
        file_patterns = [
            r'(?:delete|remove|trash|erase)\s+(?:the\s+)?(?:file|text file|document)?\s+([^\s,\.]+\.[a-zA-Z0-9]+)',
            r'(?:delete|remove|trash|erase)\s+(?:the\s+)?([^\s,\.]+\.[a-zA-Z0-9]+)',
            r'([^\s,\.]+\.[a-zA-Z0-9]+)\s+(?:file|text file|document)?\s+(?:delete|remove|trash|erase)'
        ]
        
        # Arabic file patterns for deletion
        arabic_file_patterns = [
            r'(?:احذف|امسح|ازل|أزل)\s+(?:ال|ملف|الملف)?\s+([^\s,\.]+\.[a-zA-Z0-9]+)',
            r'(?:احذف|امسح|ازل|أزل)\s+([^\س,\.]+\.[a-zA-Z0-9]+)'
        ]
        
        # Try to extract the filename
        for pattern in file_patterns + arabic_file_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filename = match.group(1)
                break
                
        # Special handling for test_files directory
        if not filename and 'test_files' in query_lower:
            # Look for patterns like "test_files/filename.txt"
            test_file_match = re.search(r'test_files/([^\s,\.]+\.[a-zA-Z0-9]+)', query_lower)
            if test_file_match:
                filename = f"test_files/{test_file_match.group(1)}"
            else:
                # Default to notes.txt in test_files if mentioned
                filename = "test_files/notes.txt"
        
        # Initialize result string with thinking
        result = ""
        if thinking:
            result += thinking + "\n\n"
        
        if not filename:
            # If no filename could be detected
            error_text = f"{self.color_settings['error']}❌ Unable to determine which file to delete from your request.{self.color_settings['reset']}\n" + \
                       f"Please specify a filename, for example: 'delete myfile.txt' or 'احذف ملف myfile.txt'"
            return result + error_text
        
        # Step 2: Check if file exists before deleting
        if not os.path.exists(filename):
            # Try to find the file in common locations
            found = False
            
            # Check in desktop, documents, downloads
            common_locations = []
            
            if self.user_settings["preferred_locations"].get("desktop"):
                common_locations.append(os.path.join(self.user_settings["preferred_locations"]["desktop"], filename))
            
            if self.user_settings["preferred_locations"].get("documents"):
                common_locations.append(os.path.join(self.user_settings["preferred_locations"]["documents"], filename))
                
            if self.user_settings["preferred_locations"].get("downloads"):
                common_locations.append(os.path.join(self.user_settings["preferred_locations"]["downloads"], filename))
            
            # Check if file exists in any of these locations
            for location in common_locations:
                if os.path.exists(location):
                    filename = location
                    found = True
                    break
            
            if not found:
                # If file not found anywhere
                error_text = f"{self.color_settings['error']}❌ File '{filename}' not found.{self.color_settings['reset']}\n" + \
                       f"Please check if the file exists and provide the correct path."
                return result + error_text
        
        # Step 3: Delete the file
        try:
            # Get confirmation from user (if not in quiet mode)
            if not self.quiet_mode:
                print(f"\nAre you sure you want to delete '{filename}'? (y/n)")
                confirmation = input("> ").lower().strip()
                if confirmation != 'y' and confirmation != 'yes':
                    cancel_text = f"{self.color_settings['important']}ℹ️ File deletion cancelled.{self.color_settings['reset']}"
                    return result + cancel_text
            
            # Determine the command based on OS
            if self.platform_commands.is_windows:
                command = f'del "{filename}"'
            else:  # Linux/macOS
                command = f"rm {shlex.quote(filename)}"
            
            # Format the command with duplicate prevention
            command_text = f"Deleting file: {command}"
            command_display = self._format_command(command_text)
            
            if command_display:
                result += command_display + "\n\n"
            
            # Execute the command
            execution_result = self.shell_handler.execute_command(command)
            
            # Check if the file was actually deleted
            file_exists = os.path.exists(filename)
            
            if not file_exists and (not execution_result or "Error" not in execution_result):
                success_text = f"{self.color_settings['success']}✅ Successfully deleted file '{filename}'.{self.color_settings['reset']}"
                result_display = self._format_result(success_text, command)
                if result_display:
                    result += result_display
                return result
            else:
                if execution_result:
                    error_text = f"{self.color_settings['error']}❌ Error deleting file: {execution_result}{self.color_settings['reset']}"
                    result_display = self._format_result(error_text, command)
                    if result_display:
                        result += result_display
                    return result
                else:
                    error_text = f"{self.color_settings['error']}❌ Failed to delete file '{filename}'. The file still exists.{self.color_settings['reset']}"
                    result_display = self._format_result(error_text, command)
                    if result_display:
                        result += result_display
                    return result
                
        except Exception as e:
            error_text = f"{self.color_settings['error']}❌ Error deleting file: {str(e)}{self.color_settings['reset']}"
            return result + error_text

    def process_request(self, request: str) -> Dict[str, Any]:
        """
        Process a user request and return the result.
        
        Args:
            request: The user request string
            
        Returns:
            Dictionary containing the processing result
        """
        # Use the AI-driven processor to handle the request
        result = self.ai_processor.process_request(request)
        
        # Extract the command and metadata
        command = result.get("command", "")
        metadata = result.get("metadata", {})
        success = result.get("success", False)
        
        # If the command was successfully extracted, execute it
        if success and command:
            # Execute the command using the shell handler
            execution_result = self.command_executor.execute_command(command)
            
            # Update the result with the execution result
            result["execution_result"] = execution_result
        
        return result
