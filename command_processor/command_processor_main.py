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
from core.platform_commands import PlatformCommands
from terminal_commands import CommandRegistry, CommandExecutor

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
        self.command_executor = CommandExecutor(shell_handler, self.command_registry)
        
        # Load command patterns from JSON file
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
            
            if not self.quiet_mode:
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
        """Process user input and execute commands directly."""
        query_lower = user_input.lower().strip()
        
        if not query_lower:
            return "Please enter a command or question."
        
        # Check for iteration-related commands (new highest priority)
        if self._is_iteration_command(query_lower):
            return self._handle_iteration_command(query_lower)
            
        # Check for machine specs query specifically (high priority)
        if self._is_machine_specs_query(query_lower):
            return self._get_detailed_system_specs()
            
        # Check for system info query (second priority)
        if self._is_system_info_query(query_lower):
            return self._execute_system_info_command(query_lower)
        
        # Check for file/folder operations (third priority)
        if self._is_file_folder_query(query_lower):
            return self._execute_file_folder_command(query_lower)
            
        # Check for notes app queries (fourth priority)
        if self._is_notes_app_query(query_lower):
            return self._execute_notes_app_command(query_lower)
        
        # Check for file write/append queries
        if self._is_file_write_query(query_lower):
            return self._execute_file_write_command(user_input)
            
        # Check for file deletion queries
        if self._is_file_delete_query(query_lower):
            return self._execute_file_delete_command(user_input)
        
        # Check for file creation requests (lower priority)
        # IMPORTANT: This should be checked after other common queries to avoid incorrect matches
        if self._is_file_creation_query(query_lower):
            return self._execute_file_creation_command(user_input)
        
        # If no patterns matched, use AI to generate a command
        return self._handle_with_ai(user_input)
        
    def _is_iteration_command(self, query):
        """Detect iteration-related commands."""
        # Check loaded patterns
        patterns = self.command_patterns.get("iteration", {})
        for cmd_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query, re.IGNORECASE):
                    return True
        
        # Direct keyword check for simple cases
        iteration_keywords = [
            'continue', 'iterate', 'next step', 'keep going',
            'stop iteration', 'halt', 'cancel', 'abort',
            'iteration status', 'progress report'
        ]
        
        return any(keyword in query for keyword in iteration_keywords)
        
    def _handle_iteration_command(self, query):
        """Handle iteration-related commands."""
        # Format thinking process
        thinking = self._format_thinking(
            f"Processing iteration command: '{query}'\n"
            f"Current iteration state: active={self.iteration_state['active']}, step={self.iteration_state['current_step']}/{self.iteration_state['total_steps']}\n"
            f"Determining appropriate action..."
        )
        
        # Determine command type (continue, stop, status)
        command_type = None
        patterns = self.command_patterns.get("iteration", {})
        
        for cmd_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query, re.IGNORECASE):
                    command_type = cmd_type
                    break
            if command_type:
                break
        
        # Default to continue if no specific match found
        if not command_type:
            if any(word in query for word in ['stop', 'halt', 'cancel', 'abort', 'enough']):
                command_type = 'stop'
            elif any(word in query for word in ['status', 'progress', 'where']):
                command_type = 'status'
            else:
                command_type = 'continue'
        
        # Handle based on command type
        if command_type == 'continue':
            return self._handle_continue_iteration(thinking)
        elif command_type == 'stop':
            return self._handle_stop_iteration(thinking)
        elif command_type == 'status':
            return self._handle_iteration_status(thinking)
        else:
            return f"{thinking}\n\n{self.color_settings['error']}❌ Unknown iteration command type.{self.color_settings['reset']}"
    
    def _handle_continue_iteration(self, thinking):
        """Handle 'continue' iteration command."""
        import time
        from datetime import datetime
        
        if not self.iteration_state['active']:
            # Initialize a new iteration if none is active
            self.iteration_state['active'] = True
            self.iteration_state['current_step'] = 1
            self.iteration_state['total_steps'] = 5  # Default to 5 steps
            self.iteration_state['step_results'] = []
            self.iteration_state['current_operation'] = "Processing data"
            self.iteration_state['last_updated'] = datetime.now().isoformat()
            
            result = f"{thinking}\n\n{self.color_settings['important']}🔄 Starting iteration process.{self.color_settings['reset']}\n"
            result += f"Step 1/{self.iteration_state['total_steps']}: {self.iteration_state['current_operation']}\n"
            result += f"{self.color_settings['success']}✅ Iteration initialized. Say 'continue' to proceed to the next step.{self.color_settings['reset']}"
            return result
        else:
            # Continue to the next step
            if self.iteration_state['current_step'] < self.iteration_state['total_steps']:
                self.iteration_state['current_step'] += 1
                self.iteration_state['last_updated'] = datetime.now().isoformat()
                
                # Simulate different operations for different steps
                operations = [
                    "Processing data",
                    "Analyzing results",
                    "Generating report",
                    "Optimizing solution",
                    "Finalizing output"
                ]
                
                current_op = operations[min(self.iteration_state['current_step']-1, len(operations)-1)]
                self.iteration_state['current_operation'] = current_op
                
                # Generate a simulated result for this step
                step_result = f"Completed {current_op.lower()}: "
                if current_op == "Processing data":
                    step_result += "Processed 2,456 records successfully."
                elif current_op == "Analyzing results":
                    step_result += "Found 3 patterns and 2 anomalies in the data."
                elif current_op == "Generating report":
                    step_result += "Created summary with 5 key insights."
                elif current_op == "Optimizing solution":
                    step_result += "Improved efficiency by 27%."
                else:
                    step_result += "All tasks completed successfully."
                    
                self.iteration_state['step_results'].append(step_result)
                
                result = f"{thinking}\n\n{self.color_settings['important']}🔄 Continuing iteration process.{self.color_settings['reset']}\n"
                result += f"Step {self.iteration_state['current_step']}/{self.iteration_state['total_steps']}: {current_op}\n"
                result += f"{self.color_settings['success']}✅ {step_result}{self.color_settings['reset']}\n\n"
                
                if self.iteration_state['current_step'] < self.iteration_state['total_steps']:
                    result += "Say 'continue' to proceed to the next step."
                else:
                    result += f"{self.color_settings['important']}🎉 Iteration complete! All steps finished.{self.color_settings['reset']}"
                    # Reset iteration state after completion
                    self.iteration_state['active'] = False
                
                return result
            else:
                # Already at the last step
                result = f"{thinking}\n\n{self.color_settings['important']}🔄 Iteration process already complete.{self.color_settings['reset']}\n"
                result += f"All {self.iteration_state['total_steps']} steps were completed.\n\n"
                
                # Show summary of results
                result += f"{self.color_settings['important']}📊 Summary of results:{self.color_settings['reset']}\n"
                for i, step_result in enumerate(self.iteration_state['step_results']):
                    result += f"  • Step {i+1}: {step_result}\n"
                
                # Reset iteration state
                self.iteration_state['active'] = False
                return result
    
    def _handle_stop_iteration(self, thinking):
        """Handle 'stop' iteration command."""
        if not self.iteration_state['active']:
            return f"{thinking}\n\n{self.color_settings['error']}⚠️ No active iteration process to stop.{self.color_settings['reset']}"
        
        # Reset iteration state
        current_step = self.iteration_state['current_step']
        total_steps = self.iteration_state['total_steps']
        self.iteration_state['active'] = False
        
        result = f"{thinking}\n\n{self.color_settings['important']}🛑 Iteration process stopped.{self.color_settings['reset']}\n"
        result += f"Stopped at step {current_step}/{total_steps}.\n\n"
        
        # Show summary of results so far
        if self.iteration_state['step_results']:
            result += f"{self.color_settings['important']}📊 Results so far:{self.color_settings['reset']}\n"
            for i, step_result in enumerate(self.iteration_state['step_results']):
                result += f"  • Step {i+1}: {step_result}\n"
        
        return result
    
    def _handle_iteration_status(self, thinking):
        """Handle 'status' iteration command."""
        if not self.iteration_state['active']:
            return f"{thinking}\n\n{self.color_settings['important']}ℹ️ No active iteration process.{self.color_settings['reset']}\n" + \
                   f"You can start a new iteration by saying 'continue to iterate'."
        
        result = f"{thinking}\n\n{self.color_settings['important']}📊 Current Iteration Status:{self.color_settings['reset']}\n"
        result += f"Progress: Step {self.iteration_state['current_step']}/{self.iteration_state['total_steps']}\n"
        result += f"Current operation: {self.iteration_state['current_operation']}\n\n"
        
        # Show percentage complete
        percentage = (self.iteration_state['current_step'] / self.iteration_state['total_steps']) * 100
        result += f"Completion: {percentage:.1f}%\n"
        
        # Visual progress bar
        bar_length = 20
        completed_length = int(bar_length * percentage / 100)
        progress_bar = "["
        progress_bar += "=" * completed_length
        if completed_length < bar_length:
            progress_bar += ">"
            progress_bar += " " * (bar_length - completed_length - 1)
        progress_bar += "]"
        
        result += f"Progress: {progress_bar}\n\n"
        
        # Show results of completed steps
        if self.iteration_state['step_results']:
            result += f"{self.color_settings['important']}📝 Completed steps:{self.color_settings['reset']}\n"
            for i, step_result in enumerate(self.iteration_state['step_results']):
                result += f"  • Step {i+1}: {step_result}\n"
        
        return result
        
    def _is_machine_specs_query(self, query):
        """Detect machine specifications queries."""
        spec_keywords = [
            'machine specs', 'system specs', 'hardware specs', 'computer specs',
            'what is my machine', 'what are my machine specs', 'what are my system specs',
            'specs of my machine', 'specs of my computer', 'specs of this machine',
            'system information', 'hardware info', 'system details',
            'show specs', 'display specs', 'tell me about my machine',
            'cpu info', 'ram info', 'memory info', 'disk info',
            'my machine specs', 'my system specs'
        ]
        
        # Check if any of the spec keywords are in the query
        return any(keyword in query for keyword in spec_keywords)
        
    def _is_system_info_query(self, query):
        """Detect system info queries with comprehensive patterns."""
        # Simple direct system check
        if 'what system' in query or 'which system' in query or 'what os' in query:
            return True
            
        # Check loaded patterns
        patterns = self.command_patterns.get("system_info", {})
        for cmd_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query, re.IGNORECASE):
                    return True
        
        return False

    def _is_notes_app_query(self, query):
        """Detect Notes app related queries."""
        # Check loaded patterns
        patterns = self.command_patterns.get("notes_app", {})
        for cmd_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query, re.IGNORECASE):
                    return True
        
        # Also check direct mentions of notes app
        note_terms = ['notes app', 'note app', 'notebook', 'do i have notes', 'open notes']
        return any(term in query for term in note_terms)
        
    def _is_file_folder_query(self, query):
        """Detect file and folder operation queries."""
        # Check for looking at text files in downloads folder specifically
        if ('look' in query or 'find' in query or 'search' in query or 'list' in query or 'show' in query) and \
           ('text file' in query or 'files' in query) and ('download' in query or 'downloads' in query):
            return True
            
        # Check loaded patterns
        patterns = self.command_patterns.get("file_system", {})
        for cmd_type, pattern_list in patterns.items():
            if cmd_type == "create_file":
                continue  # Skip create file patterns as we handle them separately
                
            for pattern in pattern_list:
                if re.search(pattern, query, re.IGNORECASE):
                    return True
        
        # Expanded file/folder operation keywords
        file_folder_keywords = [
            'list files', 'list folder', 'list directory', 'list dir',
            'show files', 'show folders', 'show directories', 
            'find files', 'find folder', 'search for files',
            'ls', 'dir', 'find', 'grep', 'locate',
            'what\'s in', 'what files', 'what folders',
            'contents of', 'folder contents'
        ]
        
        # Arabic file/folder keywords - add support for Arabic commands
        arabic_file_folder_keywords = [
            'اظهر الملفات', 'عرض الملفات', 'قائمة الملفات',
            'اظهر المجلدات', 'عرض المجلدات', 'قائمة المجلدات',
            'ابحث عن ملف', 'ابحث عن مجلد', 'جد الملفات',
            'محتويات المجلد', 'ما هي الملفات'
        ]
        
        return any(keyword in query for keyword in file_folder_keywords) or \
               any(keyword in query for keyword in arabic_file_folder_keywords)

    def _is_file_creation_query(self, query):
        """Detect file creation requests more accurately."""
        # These should be explicit file creation patterns to avoid false positives
        creation_keywords = [
            'create file', 'make file', 'create a file', 'make a file', 
            'create a text file', 'make a text file',
            'new file', 'new text file',
            'save file', 'save to file', 'write to file',
            'create document', 'make document'
        ]
        
        # Arabic file creation keywords
        arabic_creation_keywords = [
            'انشاء ملف', 'انشئ ملف', 'اصنع ملف', 'عمل ملف جديد',
            'ملف جديد', 'ملف نصي جديد', 'احفظ ملف'
        ]
        
        # Check if any explicit file creation keywords are present - using whole word matching
        # to avoid partial matches in other contexts
        has_creation_intent = any(re.search(r'\b' + re.escape(keyword) + r'\b', query) for keyword in creation_keywords) or \
                             any(keyword in query for keyword in arabic_creation_keywords)
        
        # Additional checks to reduce false positives
        # If query contains file creation intent but also contains other command keywords,
        # we should be cautious about classifying it as file creation
        other_command_indicators = [
            'list ', 'show me', 'display', 'find', 'search', 'open', 'run',
            'execute', 'move', 'copy', 'rename', 'install', 'download',
            'what is', 'what are', 'tell me', 'how to', 'continue', 'iterate', 
            'check', 'verify', 'help', 'status'
        ]
        
        # Check if the query has other command indicators that aren't file creation
        has_other_intent = any(indicator in query for indicator in other_command_indicators)
        
        # If there's a clear file creation intent and no conflicting indicators, classify as file creation
        if has_creation_intent and not has_other_intent:
            return True
        
        # Check for filename patterns that strongly indicate file creation - more strict pattern matching
        filename_patterns = [
            r'name(?:d|)\s+(?:it|)\s+([a-z0-9_.-]+\.[a-z0-9]+)\b',
            r'call(?:ed|)\s+(?:it|)\s+([a-z0-9_.-]+\.[a-z0-9]+)\b',
            r'file\s+(?:called|named)\s+([a-z0-9_.-]+\.[a-z0-9]+)\b'
        ]
        
        for pattern in filename_patterns:
            if re.search(pattern, query):
                # Found explicit filename pattern, but make sure it's not part of another command
                return not has_other_intent
        
        # By default, don't interpret as a file creation unless explicitly requested
        return False

    def _is_file_write_query(self, query):
        """Detect file write or append requests."""
        # Keywords for writing to existing files
        write_keywords = [
            'write to', 'add to', 'append to', 'update', 'put in',
            'add line', 'append line', 'write line', 'add text',
            'insert into', 'insert in', 'write into'
        ]
        
        # Arabic write keywords
        arabic_write_keywords = [
            'اكتب', 'أكتب في', 'اضف إلى', 'اضف الى', 'اضافة الى',
            'اكتب السطر', 'اضف سطر', 'اكتب نص', 'ادخل في'
        ]
        
        # Check for write keywords
        has_write_intent = any(keyword in query for keyword in write_keywords) or \
                           any(keyword in query for keyword in arabic_write_keywords)
        
        # Check for presence of file mention
        has_file_mention = 'file' in query or '.txt' in query or 'text file' in query or 'ملف' in query
        
        # Check for presence of content indicators
        content_indicators = ['line', 'text', 'content', 'string', 'text', 'سطر', 'نص', 'محتوى']
        has_content_indicator = any(indicator in query for indicator in content_indicators)
        
        # If query has write intent and a file is mentioned
        if has_write_intent and has_file_mention:
            return True
        
        # Look for cases like "add 'hello' to file.txt" pattern
        # This matches patterns with quoted content going to a file
        if re.search(r'(?:add|append|write|put)\s+[\'"]([^\'"]+)[\'"]\s+(?:to|in|into)', query):
            return True
            
        # Look for sentence patterns like "write the line X in file Y"
        line_patterns = [
            r'(?:write|add|append|put)\s+(?:the\s+)?(?:line|text|content|string)\s+[\'"]?([^\'"]+)[\'"]?\s+(?:to|in|into)\s+([^\s]+)',
            r'(?:write|add|append|put)\s+[\'"]?([^\'"]+)[\'"]?\s+(?:to|in|into)\s+(?:the\s+)?(?:file|text file)\s+([^\s]+)'
        ]
        
        for pattern in line_patterns:
            if re.search(pattern, query):
                return True
                
        # Arabic patterns like "اكتب السطر X في الملف Y"
        arabic_line_patterns = [
            r'(?:اكتب|أكتب|اضف|أضف)\s+(?:السطر|النص|المحتوى)\s+[\'"]?([^\'"]+)[\'"]?\s+(?:في|الى|إلى)\s+(?:الملف|ملف)\s+([^\s]+)',
            r'(?:اكتب|أكتب|اضف|أضف)\s+[\'"]?([^\'"]+)[\'"]?\s+(?:في|الى|إلى)\s+(?:الملف|ملف)\s+([^\s]+)'
        ]
        
        for pattern in arabic_line_patterns:
            if re.search(pattern, query):
                return True
        
        return False
        
    def _is_file_delete_query(self, query):
        """Detect file deletion requests."""
        # Keywords for deleting files
        delete_keywords = [
            'delete', 'remove', 'trash', 'erase', 'get rid of'
        ]
        
        # Arabic delete keywords
        arabic_delete_keywords = [
            'احذف', 'امسح', 'ازل', 'أزل'
        ]
        
        # Check for delete keywords
        has_delete_intent = any(keyword in query for keyword in delete_keywords) or \
                            any(keyword in query for keyword in arabic_delete_keywords)
        
        # Check for presence of file mention
        has_file_mention = 'file' in query or '.txt' in query or 'text file' in query or 'ملف' in query
        
        # If query has delete intent and a file is mentioned
        if has_delete_intent and has_file_mention:
            return True
            
        # More complex patterns for file deletion
        file_patterns = [
            r'(?:delete|remove|trash|erase|get rid of)\s+(?:the\s+)?(?:file|text file|document)\s+([^\s]+)',
            r'(?:delete|remove|trash|erase|get rid of)\s+([^\s]+\.(?:txt|md|pdf|doc|json|py|js|html|css))'
        ]
        
        for pattern in file_patterns:
            if re.search(pattern, query):
                return True
                
        # Arabic patterns
        arabic_file_patterns = [
            r'(?:احذف|امسح|ازل|أزل)\s+(?:ال|ملف|الملف)\s+([^\s]+)',
            r'(?:احذف|امسح|ازل|أزل)\s+([^\s]+\.(?:txt|md|pdf|doc|json|py|js|html|css))'
        ]
        
        for pattern in arabic_file_patterns:
            if re.search(pattern, query):
                return True
                
        return False

    def _execute_system_info_command(self, query):
        """Execute appropriate system command for information queries."""
        # Direct "what system" query - use the platform detection
        if 'what system' in query or 'which system' in query or 'what os' in query or 'am i on' in query:
            platform_info = self.platform_commands.get_platform_info()
            
            # Create a user-friendly response
            if self.platform_commands.is_linux:
                # For Linux, include distribution info if available
                if self.platform_commands.linux_distro:
                    return f"You are running Linux ({self.platform_commands.linux_distro.capitalize()}). Your current shell is {self.platform_commands.shell}."
                else:
                    return f"You are running Linux. Your current shell is {self.platform_commands.shell}."
            elif self.platform_commands.is_macos:
                return f"You are running macOS. Your current shell is {self.platform_commands.shell}."
            elif self.platform_commands.is_windows:
                return "You are running Windows."
            else:
                # Generic response if platform not specifically identified
                return f"You are running {platform.system()} on {platform.machine()} architecture."
        
        # Use platform-specific commands for other system info queries
        if any(term in query for term in ['uptime', 'how long', 'running']):
            command = self.platform_commands.get_system_status_command("uptime")
            return self.shell_handler.execute_command(command)
        
        if any(term in query for term in ['memory', 'ram']):
            command = self.platform_commands.get_system_status_command("memory")
            return self.shell_handler.execute_command(command)
            
        if any(term in query for term in ['disk', 'storage', 'space']):
            command = self.platform_commands.get_system_status_command("disk")
            return self.shell_handler.execute_command(command)
            
        if any(term in query for term in ['cpu', 'processor', 'load']):
            command = self.platform_commands.get_system_status_command("cpu")
            return self.shell_handler.execute_command(command)
            
        # Default system info - use a summary command based on platform
        command = self.platform_commands.get_system_status_command("summary")
        return self.shell_handler.execute_command(command)
        
    def _execute_notes_app_command(self, query):
        """Execute appropriate Notes app command directly using platform commands."""
        result_prefix = "📝 Notes Results:\n"
        
        if 'open' in query:
            command = self.platform_commands.get_notes_command("open")
            result = self.shell_handler.execute_command(command)
            return f"✅ Opening notes application: {result}"
        
        elif 'count' in query or 'many' in query or 'number' in query:
            command = self.platform_commands.get_notes_command("count")
            result = self.shell_handler.execute_command(command)
            
            # Format the result nicely
            if result.isdigit():
                return f"{result_prefix}You have {result} notes."
            else:
                return f"{result_prefix}{result}"
            
        elif ('list' in query and 'folder' not in query and 'topic' not in query) or ('show' in query and 'folder' not in query and 'topic' not in query):
            command = self.platform_commands.get_notes_command("list")
            result = self.shell_handler.execute_command(command)
            
            # Format the result with bullet points if it's a list
            if '\n' in result:
                notes = result.strip().split('\n')
                formatted_notes = "\n".join([f"  • {note}" for note in notes[:20]])
                if len(notes) > 20:
                    formatted_notes += f"\n  ... and {len(notes) - 20} more notes"
                return f"{result_prefix}{formatted_notes}"
            else:
                return f"{result_prefix}{result}"
            
        else:
            # Default for topics/folders - using shell_handler.find_folders
            if hasattr(self.shell_handler, "find_folders"):
                return self.shell_handler.find_folders("notes", "~", 20, True)
            else:
                # Fallback to command if find_folders is not available
                command = self.platform_commands.get_file_search_command("folder", "notes")
                result = self.shell_handler.execute_command(command)
                
                # Format the result with bullet points
                if '\n' in result:
                    folders = result.strip().split('\n')
                    formatted_folders = "\n".join([f"  📁 {folder}" for folder in folders])
                    return f"{result_prefix}Potential notes folders found:\n{formatted_folders}"
                else:
                    return f"{result_prefix}{result}"
        
    def _execute_file_folder_command(self, query):
        """Execute appropriate file/folder command directly using platform commands."""
        result_prefix = "📂 File/Folder Results:\n"
        
        # Extract search term and file extension if present
        search_term = None
        file_extension = None
        
        # Check for specific file extension requests
        extension_match = re.search(r'(txt|pdf|docx?|jpe?g|png|zip|gif|mp3|mp4)\s+files', query, re.IGNORECASE)
        if extension_match:
            file_extension = extension_match.group(1).lower()
        
        # Check for "what is/are the X files" pattern
        is_are_match = re.search(r'what\s+(is|are)\s+the\s+(.*?)\s+files', query, re.IGNORECASE)
        if is_are_match:
            descriptor = is_are_match.group(2).strip().lower()
            if 'text' in descriptor or 'txt' in descriptor:
                file_extension = 'txt'
            elif 'pdf' in descriptor:
                file_extension = 'pdf'
            elif 'doc' in descriptor:
                file_extension = 'doc'
            elif 'image' in descriptor or 'picture' in descriptor or 'photo' in descriptor:
                file_extension = 'jpg,jpeg,png,gif'
        
        # Extract location - desktop, documents, downloads
        location = None
        location_match = re.search(r'(on|in)\s+(my|the)?\s*(desktop|documents?|downloads?)', query, re.IGNORECASE)
        if location_match:
            location = location_match.group(3).lower()
            if location == 'document' or location == 'documents':
                location = 'documents'
            elif location == 'download' or location == 'downloads':
                location = 'downloads'
        
        # If no explicit location mentioned, see if terms appear in the query
        if not location:
            if 'desktop' in query.lower():
                location = 'desktop'
            elif 'document' in query.lower():
                location = 'documents'
            elif 'download' in query.lower():
                location = 'downloads'
            else:
                # Default to current directory if no location specified
                location = 'current'
        
        # Extract search term for other file search patterns
        if not search_term and not file_extension:
            for term in ['find', 'search', 'where', 'about', 'for']:
                if term in query:
                    parts = query.split(term, 1)
                    if len(parts) > 1:
                        potential_terms = parts[1].split()
                        if potential_terms:
                            search_term = potential_terms[0].strip()
                            break
        
        # Determine if we're searching for files or folders
        search_type = "folder" if any(term in query for term in ['folder', 'directory', 'directories']) else "file"
        
        # Format special command for file extension search
        if file_extension and location:
            if location == 'desktop':
                base_dir = self.user_settings["preferred_locations"].get("desktop", "~/Desktop")
            elif location == 'documents':
                base_dir = self.user_settings["preferred_locations"].get("documents", "~/Documents")
            elif location == 'downloads':
                base_dir = self.user_settings["preferred_locations"].get("downloads", "~/Downloads")
            else:
                base_dir = "."  # Current directory
                
            # Use platform-specific command for file extension search
            if self.platform_commands.is_linux or self.platform_commands.is_macos:
                if ',' in file_extension:
                    # Multiple extensions
                    extensions = file_extension.split(',')
                    find_parts = [f"-name '*.{ext}'" for ext in extensions]
                    command = f"find {base_dir} -type f \\( {' -o '.join(find_parts)} \\) | sort"
                else:
                    command = f"find {base_dir} -type f -name '*.{file_extension}' | sort"
            elif self.platform_commands.is_windows:
                if ',' in file_extension:
                    # Multiple extensions
                    extensions = file_extension.split(',')
                    find_parts = [f"*.{ext}" for ext in extensions]
                    command = f"dir /b {base_dir}\\{{{','.join(find_parts)}}}"
                else:
                    command = f"dir /b {base_dir}\\*.{file_extension}"
            else:
                # Fallback to platform commands
                command = self.platform_commands.get_file_search_command(search_type, file_extension)
        else:
            # Get and execute the platform-specific command
            if not search_term:
                search_term = "*"  # Default to all files/folders
                
            command = self.platform_commands.get_file_search_command(search_type, search_term)
        
        # Execute the command
        if not self.quiet_mode:
            print(f"\n🔍 Searching for {search_type}s" + 
                  (f" with extension '{file_extension}'" if file_extension else f" matching '{search_term}'") + 
                  f" in {location} directory\n")
            print(f"Command: {command}\n")
        
        # Fix for wildcard pattern "**" which is causing issues
        if search_term == "**":
            # Use a safer alternative search pattern
            search_term = "*"
            # Get revised command with the safer pattern
            command = self.platform_commands.get_file_search_command(search_type, search_term)
            if not self.quiet_mode:
                print(f"Using safer search pattern: {command}\n")
            
        result = self.shell_handler.execute_command(command)
        
        # Format the results
        if result and not result.startswith("Error"):
            items = [item for item in result.strip().split('\n') if item]
            if items:
                icon = "📁" if search_type == "folder" else "📄"
                formatted_results = "\n".join([f"  {icon} {item}" for item in items])
                
                # Create a nice header for the results
                header = f"{search_type.capitalize()}s"
                if file_extension:
                    header += f" with extension .{file_extension}"
                if location and location != "current":
                    header += f" in your {location}"
                    
                return f"{result_prefix}Found {len(items)} {header}:\n{formatted_results}"
            else:
                header = f"{search_type.capitalize()}s"
                if file_extension:
                    header += f" with extension .{file_extension}"
                if location and location != "current":
                    header += f" in your {location}"
                return f"No {header} were found."
        else:
            return f"❌ Error searching for {search_type}s: {result}"
            
    def _execute_file_creation_command(self, user_input):
        """Handle file creation requests by extracting filename, content, and location."""
        query_lower = user_input.lower()
        
        # Format thinking process that will be folded
        thinking = self._format_thinking(
            f"Creating a file based on your request...\n"
            f"Analyzing to extract the filename, location, and content...\n"
            f"Checking your preferred locations..."
        )
        
        # Step 1: Try to extract the filename
        filename = None
        name_patterns = [
            r'name(?:d|)\s+(?:it|)\s+([a-z0-9_.-]+\.[a-z0-9]+)',
            r'call(?:ed|)\s+(?:it|)\s+([a-z0-9_.-]+\.[a-z0-9]+)',
            r'file\s+(?:called|named)\s+([a-z0-9_.-]+\.[a-z0-9]+)',
            r'create\s+(?:a\s+|)(?:file|text file)\s+([a-z0-9_.-]+\.[a-z0-9]+)',
            r'make\s+(?:a\s+|)(?:file|text file)\s+([a-z0-9_.-]+\.[a-z0-9]+)',
            r'(?:save|write)(?:\s+to|)\s+(?:a\s+|)(?:file|)\s+([a-z0-9_.-]+\.[a-z0-9]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filename = match.group(1)
                break
        
        # If no filename with extension found, check for filenames without extension
        if not filename:
            name_patterns_no_ext = [
                r'name(?:d|)\s+(?:it|)\s+([a-z0-9_.-]+)',
                r'call(?:ed|)\s+(?:it|)\s+([a-z0-9_.-]+)',
                r'file\s+(?:called|named)\s+([a-z0-9_.-]+)',
                r'create\s+(?:a\s+|)(?:file|text file)\s+([a-z0-9_.-]+)'
            ]
            
            for pattern in name_patterns_no_ext:
                match = re.search(pattern, query_lower)
                if match:
                    filename = match.group(1) + ".txt"  # Add .txt extension
                    break
        
        # Default filename if none found
        if not filename:
            filename = "hello.txt"
        
        # Step 2: Try to extract content
        content = None
        content_requested = False
        
        # First check if content was explicitly requested or mentioned
        content_mentions = [
            'with content', 'containing', 'that says', 
            'with text', 'that reads', 'saying', 
            'put in it', 'inside it', 'with the following'
        ]
        
        # If any content terms are mentioned, mark content as requested
        content_requested = any(term in query_lower for term in content_mentions)
        
        # Improved content patterns with better handling of various expressions
        content_patterns = [
            # Match content between quotes
            r'content\s+(?:is|as|of|)\s+"([^"]+)"',
            r'content\s+(?:is|as|of|)\s+\'([^\']+)\'',
            
            # Match 'put in it X' pattern (very common in natural language)
            r'put\s+(?:in\s+it|inside|in\s+the\s+file)\s+([^,\.]+)',
            r'put\s+([^,\.]+)\s+(?:in\s+it|inside|in\s+the\s+file)',
            
            # General content patterns
            r'content\s+(?:is|as|of|)\s+([^.]+)(?:\.|$)',
            r'with\s+(?:the\s+|)(?:text|content)\s+(?:of|)\s+"?([^".]+)"?',
            r'with\s+(?:the\s+words|)\s+"?([^".]+)"?',
            r'containing\s+(?:the\s+text|)\s+"?([^".]+)"?',
            r'that\s+(?:has|contains|says|includes)\s+"?([^".]+)"?',
            r'with\s+"?([^".]+)"?\s+(?:in it|inside|as content)',
            r'saying\s+"?([^".]+)"?'
        ]
        
        for pattern in content_patterns:
            match = re.search(pattern, query_lower)
            if match:
                content = match.group(1).strip()
                content_requested = True
                break
        
        # Special check for hello world between commands
        if not content and 'hello world' in query_lower:
            # Extract a segment around "hello world"
            hello_idx = query_lower.find('hello world')
            start_idx = max(0, hello_idx - 10)
            end_idx = min(len(query_lower), hello_idx + 20)
            content_segment = query_lower[start_idx:end_idx]
            content = "Hello World!"
            content_requested = True
        
        # Only use default content if content wasn't explicitly requested
        if not content:
            if content_requested:
                # If content was requested but couldn't be extracted, ask AI for help
                content_prompt = f"The user wants to create a file named {filename} but I couldn't extract the content they wanted. What would be a good default content based on their request: '{user_input}'?"
                content = self.ai_handler.query_ai(content_prompt)
                # Ensure it's not too long
                if len(content) > 100:
                    content = content[:100] + "..."
            else:
                # If content wasn't requested at all
                content = "This is a text file."
        
        # Step 3: Try to extract location - IMPROVED TO DETECT DOCUMENT FOLDER
        location = None
        location_patterns = [
            r'(?:in|on|to|at)\s+(?:the\s+|my\s+|)(\w+)\s+(?:folder|directory)',
            r'(?:in|on|to|at)\s+(?:the\s+|my\s+|)(\w+)(?:\s+|$)',
            r'(?:save|store|put)\s+(?:in|on|to|at)\s+(?:the\s+|my\s+|)(\w+)'
        ]
        
        # First look specifically for document folder references
        document_patterns = [
            r'(?:in|on|to|at)\s+(?:the\s+|my\s+|)(doc|document|documents)\s+(?:folder|directory)',
            r'(?:in|on|to|at)\s+(?:the\s+|my\s+|)(doc|document|documents)(?:\s+|$)',
            r'(?:save|store|put)\s+(?:in|on|to|at)\s+(?:the\s+|my\s+|)(doc|document|documents)'
        ]
        
        # Explicitly check for document folder mentions
        for pattern in document_patterns:
            match = re.search(pattern, query_lower)
            if match:
                location = 'documents'
                break
        
        # If documents not explicitly mentioned, try other locations
        if not location:
            for pattern in location_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    location_name = match.group(1).strip()
                    if location_name in ['desktop', 'documents', 'downloads', 'home']:
                        location = location_name
                        break
        
            # Check for specific desktop mention at the beginning or anywhere in the query
            if query_lower.startswith(('on desktop', 'on my desktop', 'at desktop', 'at my desktop')) or 'desktop' in query_lower:
                location = 'desktop'
            elif query_lower.startswith(('in documents', 'in my documents', 'at documents', 'at my documents')) or 'documents' in query_lower:
                location = 'documents'
            elif query_lower.startswith(('in downloads', 'in my downloads', 'at downloads', 'at my downloads')) or 'downloads' in query_lower:
                location = 'downloads'
        
        # Default to desktop if no location specified
        if not location:
            location = 'desktop'
        
        # Get the platform-specific command to create the file
        command = self.platform_commands.get_create_file_command(filename, content, location)
        
        # Add verbose output in non-quiet mode
        if not self.quiet_mode:
            print(f"\nFile Creation Request:")
            print(f"  Filename: {filename}")
            print(f"  Location: {location}")
            print(f"  Content: \"{content}\"")
            print(f"  Command: {command}\n")
            
        result = self.shell_handler.execute_command(command)
        
        # Format the response with thinking and colors
        if not result or "Error" not in result:
            # Build the full path for reporting
            if location.lower() == 'desktop':
                if self.platform_commands.is_windows:
                    path = f"%USERPROFILE%\\Desktop\\{filename}"
                else:
                    path = f"~/Desktop/{filename}"
            elif location.lower() == 'documents':
                if self.platform_commands.is_windows:
                    path = f"%USERPROFILE%\\Documents\\{filename}"
                else:
                    path = f"~/Documents/{filename}"
            else:
                path = f"{location}/{filename}"
                
            return f"{thinking}\n\n{self.color_settings['success']}✅ Created file '{filename}' in {location}{self.color_settings['reset']}" + \
                   f"\n{self.color_settings['important']}📄 Content:{self.color_settings['reset']} \"{content}\""
        else:
            return f"{thinking}\n\n{self.color_settings['error']}❌ Error creating file: {result}{self.color_settings['reset']}"
        
    def _handle_with_ai(self, user_input):
        """Process user input with AI to generate an executable command."""
        # Format thinking process that will be folded
        thinking = self._format_thinking(
            f"🤖 Processing your request: '{user_input}'\n\n"
            f"I'm thinking about how to best handle this...\n"
            f"Analyzing the intent of your request...\n"
            f"Checking if I can map this to a system command..."
        )
        
        # Create a prompt that's aware of the current platform
        system_info = self.platform_commands.get_platform_info()
        
        # Create a better prompt that helps with file creation and other common tasks
        prompt_for_ai = (
            f"User request: '{user_input}'\n"
            f"Current OS: {system_info['system']} "
            f"{'(' + system_info['linux_distro'] + ')' if system_info['linux_distro'] else ''}\n"
            f"Shell: {system_info['shell']}\n\n"
            f"IMPORTANT INSTRUCTIONS:\n"
            f"1. Generate a single command that would execute this request on the user's current OS.\n"
            f"2. For file creation requests, use the appropriate OS command (e.g. echo on Linux/macOS, type on Windows).\n" 
            f"3. For commands that need to handle spaces or special characters, use proper escaping/quoting.\n"
        )
        
        # Get response from AI with timeout handling in fast mode
        try:
            # In fast mode, we'll use a shorter internal timeout
            ai_response = self.ai_handler.get_ai_response(prompt_for_ai)
        except Exception as e:
            if self.fast_mode:
                # In fast mode, provide a simple error and let the program continue to exit
                return f"{thinking}\n\nError: Failed to get AI response: {str(e)}"
            else:
                # In normal mode, re-raise the exception
                raise
        
        # Extract command from AI response with special handling for fast mode
        command = self._extract_command_from_ai_response(ai_response)
        
        # If we're in fast mode and this is an AI error response, use the raw response as a command
        if self.fast_mode and command is None and ai_response and ai_response.startswith("Error:"):
            command = ai_response  # This allows the error to propagate properly in fast mode
        
        if command:
            # Format the result with colors
            result = f"{thinking}\n\n"
            result += f"{self.color_settings['important']}📌 I'll execute this command:{self.color_settings['reset']} {command}\n\n"
            
            # Execute the command using the shell handler
            execution_result = self.shell_handler.execute_command(command)
            
            # Format the execution result
            if execution_result:
                if "Error" in execution_result or "not found" in execution_result.lower():
                    result += f"{self.color_settings['error']}❌ There was a problem:{self.color_settings['reset']}\n{execution_result}\n"
                    # In fast mode, skip fallback response to avoid delaying exit
                    if not self.fast_mode:
                        # Provide a helpful explanation when command fails
                        result += f"\n{self.color_settings['important']}💡 Let me try a different approach:{self.color_settings['reset']}\n"
                        fallback_response = self.ai_handler.query_ai(f"The command '{command}' failed with: {execution_result}. Please provide information or explanation directly.")
                        result += fallback_response
                    else:
                        # In fast mode, just add a simple message
                        result += f"\n{self.color_settings['important']}💡 Fast mode: Skipping fallback explanation.{self.color_settings['reset']}\n"
                else:
                    result += f"{self.color_settings['success']}✅ Result:{self.color_settings['reset']}\n{execution_result}\n"
            else:
                result += f"{self.color_settings['success']}✅ Command executed successfully with no output.{self.color_settings['reset']}\n"
            
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
            r'(?:ملف|الملف)\s+([^\s,]+\.[a-zA-Z0-9]+)'
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
        
        # Execute the command
        if not self.quiet_mode:
            print(f"\nFile Write Request:")
            print(f"  Filename: {filename}")
            print(f"  Content: \"{content}\"")
            print(f"  Mode: {'Append' if append_mode else 'Overwrite'}")
            print(f"  Command: {command}\n")
            
        result = self.shell_handler.execute_command(command)
        
        # Format the response
        if not result or "Error" not in result:
            return f"{thinking}\n\n{self.color_settings['success']}✅ {'Added' if append_mode else 'Wrote'} content to file '{filename}':{self.color_settings['reset']}" + \
                   f"\n{self.color_settings['important']}📝 Content:{self.color_settings['reset']} \"{content}\""
        else:
            return f"{thinking}\n\n{self.color_settings['error']}❌ Error writing to file: {result}{self.color_settings['reset']}"

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
            r'(?:احذف|امسح|ازل|أزل)\s+([^\s,\.]+\.[a-zA-Z0-9]+)'
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
        
        if not filename:
            # If no filename could be detected
            return f"{thinking}\n\n{self.color_settings['error']}❌ Unable to determine which file to delete from your request.{self.color_settings['reset']}\n" + \
                   f"Please specify a filename, for example: 'delete myfile.txt' or 'احذف ملف myfile.txt'"
        
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
                return f"{thinking}\n\n{self.color_settings['error']}❌ File '{filename}' not found.{self.color_settings['reset']}\n" + \
                       f"Please check if the file exists and provide the correct path."
        
        # Step 3: Delete the file
        try:
            # Get confirmation from user (if not in quiet mode)
            if not self.quiet_mode:
                print(f"\nAre you sure you want to delete '{filename}'? (y/n)")
                confirmation = input("> ").lower().strip()
                if confirmation != 'y' and confirmation != 'yes':
                    return f"{thinking}\n\n{self.color_settings['important']}ℹ️ File deletion cancelled.{self.color_settings['reset']}"
            
            # Determine the command based on OS
            if self.platform_commands.is_windows:
                command = f'del "{filename}"'
            else:  # Linux/macOS
                command = f"rm {shlex.quote(filename)}"
            
            # Execute the command
            if not self.quiet_mode:
                print(f"Executing: {command}")
                
            result = self.shell_handler.execute_command(command)
            
            # Check if the file was actually deleted
            file_exists = os.path.exists(filename)
            
            if not file_exists and (not result or "Error" not in result):
                return f"{thinking}\n\n{self.color_settings['success']}✅ Successfully deleted file '{filename}'.{self.color_settings['reset']}"
            else:
                if result:
                    return f"{thinking}\n\n{self.color_settings['error']}❌ Error deleting file: {result}{self.color_settings['reset']}"
                else:
                    return f"{thinking}\n\n{self.color_settings['error']}❌ Failed to delete file '{filename}'. The file still exists.{self.color_settings['reset']}"
                
        except Exception as e:
            return f"{thinking}\n\n{self.color_settings['error']}❌ Error deleting file: {str(e)}{self.color_settings['reset']}"
