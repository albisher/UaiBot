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
        default_patterns = {
            "system_info": {
                "uptime": [r"(how\s+long|since|uptime|duration|running\s+time|system\s+on\s+time|time\s+running)"],
                "memory": [r"(memory|ram|available\s+memory|free\s+memory|memory\s+usage)"],
                "disk_space": [r"(disk|space|storage|free\s+space|available\s+space|disk\s+usage)"]
            },
            "notes_app": {
                "topics": [r"(notes?\s+topics?|notes?\s+folders?|list\s+.*\s+notes|show\s+.*\s+notes|what\s+.*\s+notes|notes?\s+(topic|folder)\s+list|all\s+.*\s+notes)"],
                "count": [r"(how\s+many\s+notes|notes?\s+count|number\s+of\s+notes)"],
                "list": [r"(list\s+notes|show\s+notes|what\s+notes|my\s+notes|notes\s+list)"]
            },
            "file_system": {
                "find_folders": [r"(folders?|directories?|where\s+.*\s+folders?|show\s+.*\s+folders?|list\s+.*\s+folders?|find\s+.*\s+folders?)"]
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
        """Process user input with AI after direct command processing failed."""
        # Check if this looks like a direct command request that we can execute
        if self._looks_like_direct_command(user_input):
            direct_result = self._try_direct_execution(user_input)
            if direct_result:
                return direct_result
        
        # If not a direct command or execution failed, request AI response 
        # but with our instructions to execute commands directly
        ai_response = self.ai_handler.get_ai_response(user_input)
        
        # Check if the AI response is suggesting a command to run
        # If it is, we should try to extract and run that command
        suggested_command = self._extract_command_from_ai_response(ai_response)
        if suggested_command:
            # Tell the user we're executing the suggested command
            print(f"🤖 AI suggested command: `{suggested_command}`\nExecuting directly...")
            
            # Use our new run_command utility
            result = run_command(suggested_command, shell=True, capture_output=True, text=True)
            
            # Format the execution result
            if result['success']:
                output = result['stdout'].strip() if result['stdout'] else "Command executed successfully (no output)"
                execution_result = f"✅ Command executed: `{suggested_command}`\n\n```\n{output}\n```"
            else:
                error = result['stderr'].strip() if result['stderr'] else f"Command failed with return code {result['returncode']}"
                execution_result = f"❌ Command failed: `{suggested_command}`\n\n```\n{error}\n```"
            
            # Return both the AI's explanation and the execution result
            return f"{ai_response}\n\n---\n\n{execution_result}"
        
        # Check for notes-related commands that might not have been caught
        notes_keywords = ['notes', 'note', 'folder', 'folders', 'robotic world']
        if any(keyword in user_input.lower() for keyword in notes_keywords):
            if 'open' in user_input.lower():
                # Special handling for "open notes" type commands
                search_term = None
                if 'robotic world' in user_input.lower():
                    search_term = "Robotic World"
                elif 'about' in user_input.lower():
                    # Try to extract what the notes are about
                    about_match = re.search(r'about\s+(\w+(?:\s+\w+)*)', user_input.lower())
                    if about_match:
                        search_term = about_match.group(1).strip()
                
                # Execute the notes opening command
                if search_term:
                    escaped_term = search_term.replace(' ', '\\ ')
                    command = f"open -a Notes ~/Documents/{escaped_term}"
                else:
                    command = "open -a Notes"
                
                result = run_command(command, shell=True)
                if result['success']:
                    return f"✅ Opened Notes app{' for ' + search_term if search_term else ''}"
                else:
                    return f"❌ Failed to open Notes: {result['stderr']}\n\n{ai_response}"
        
        return ai_response
        
    def _extract_command_from_ai_response(self, ai_response):
        """Extract a command from an AI response that suggests running a command."""
        # Check for code blocks that might contain commands
        code_block_pattern = r'```(?:bash|shell|zsh|sh)?\s*(.*?)\s*```'
        code_blocks = re.findall(code_block_pattern, ai_response, re.DOTALL)
        
        if code_blocks:
            # Use the first code block as the command
            command = code_blocks[0].strip()
            
            # If the command has multiple lines, only use the first meaningful line
            command_lines = [line.strip() for line in command.split('\n') if line.strip() and not line.strip().startswith('#')]
            if command_lines:
                return command_lines[0]
        
        # Check for commands in backticks
        backtick_pattern = r'`(.*?)`'
        backticks = re.findall(backtick_pattern, ai_response)
        
        if backticks:
            # Check each backticked item to see if it looks like a command
            command_prefixes = ["ls", "cd", "find", "grep", "echo", "mkdir", "touch", "cat", "open", 
                                "python", "pip", "npm", "git", "ssh", "curl", "wget", "osascript",
                                "rm", "cp", "mv", "chmod"]
            
            for item in backticks:
                words = item.split()
                if words and words[0] in command_prefixes:
                    return item
        
        # Check for specific phrases indicating commands
        command_phrases = [
            "you can run:", "try running:", "execute:", "command:", 
            "you can use:", "run this command:", "try this:"
        ]
        
        for phrase in command_phrases:
            if phrase in ai_response.lower():
                # Get the text after the phrase until the end of the line
                match = re.search(f"{re.escape(phrase)}\\s*(.*?)(?:\\n|$)", ai_response.lower())
                if match:
                    return match.group(1).strip()
        
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
        """Try to execute the input as a direct command."""
        try:
            # Extract the actual command from natural language input
            command = self._extract_command(user_input)
            
            if not command:
                return None  # If we couldn't extract a command, let the AI handle it
                
            # Execute the command directly using our run_command utility
            result = run_command(command, shell=True, capture_output=True, text=True)
            
            if result['success']:
                output = result['stdout'].strip() if result['stdout'] else "Command executed successfully (no output)"
                return f"✅ Command executed: `{command}`\n\n```\n{output}\n```"
            else:
                error = result['stderr'].strip() if result['stderr'] else f"Command failed with return code {result['returncode']}"
                return f"❌ Command failed: `{command}`\n\n```\n{error}\n```"
        except Exception as e:
            return f"Error trying to execute command: {str(e)}"
            
    def _extract_command(self, user_input):
        """Extract the actual command from natural language input."""
        input_lower = user_input.lower().strip()
        
        # First, check for specific commands we want to execute directly
        # Notes app commands
        if any(term in input_lower for term in ['notes', 'note']):
            if 'show' in input_lower and 'folder' in input_lower:
                # Handle "show my Notes folders" type commands
                if platform.system() == 'Darwin':  # macOS
                    return """osascript -e 'tell application "Notes" to get name of every folder'"""
                else:
                    return 'find ~ -type d -name "*Notes*" -o -name "*notes*" | head -n 10'
            elif 'show' in input_lower or 'list' in input_lower:
                # Handle "show my Notes" type commands
                if platform.system() == 'Darwin':  # macOS
                    return """osascript -e 'tell application "Notes" to get name of every note'"""
                else:
                    return 'find ~ -name "*.txt" -o -name "*.md" | grep -i note | head -n 10'
            elif 'open' in input_lower:
                if 'robotic world' in input_lower:
                    return 'open -a Notes ~/Documents/Robotic\\ World'
                return 'open -a Notes'
                
        # Direct command prefixes to remove
        prefixes = [
            "run ", "execute ", "start ", "launch ", "can you run ", 
            "please run ", "could you run ", "would you run ",
            "can you execute ", "please execute ", "execute the command ",
            "run the command ", "run this: ", "execute this: "
        ]
        
        # Try to extract the command by removing prefixes
        command = user_input.strip()
        for prefix in prefixes:
            if input_lower.startswith(prefix):
                command = user_input[len(prefix):].strip()
                break
                
        # Special handling for specific command patterns
        if input_lower.startswith("open "):
            # Handle "open X" commands specially for macOS
            app_name = command[5:].strip()  # Remove "open "
            if " with " in app_name.lower():  # "open file with app"
                parts = app_name.split(" with ", 1)
                file_path = parts[0].strip()
                app = parts[1].strip()
                return f"open -a \"{app}\" \"{file_path}\""
            elif not app_name.startswith("/") and not app_name.startswith("~"):
                # Likely an app name, not a path
                return f"open -a \"{app_name}\""
            else:
                # Likely a file path
                return f"open \"{app_name}\""
                
        # Handle "find X" commands
        if input_lower.startswith("find ") and "find -" not in input_lower:
            search_term = command[5:].strip()  # Remove "find "
            # Extract the search term and location if specified
            if " in " in search_term.lower():
                term, location = search_term.split(" in ", 1)
                term = term.strip()
                location = location.strip()
                if location.lower() in ["home", "my home", "home directory", "my home directory"]:
                    location = "~"
                return f"find {location} -name \"*{term}*\" -not -path \"*/\\.*\" | head -n 10"
            else:
                return f"find ~ -name \"*{search_term}*\" -not -path \"*/\\.*\" | head -n 10"
                
        # Handle "show me X" or "list X" commands
        show_prefixes = ["show me ", "show the ", "show all ", "list ", "list the ", "list all "]
        for prefix in show_prefixes:
            if input_lower.startswith(prefix):
                item_type = command[len(prefix):].strip()
                if "file" in item_type.lower() or "folder" in item_type.lower() or "director" in item_type.lower():
                    # Extract location if specified
                    if " in " in item_type.lower():
                        what, where = item_type.split(" in ", 1)
                        return f"ls -la {where.strip()}"
                    else:
                        return "ls -la"
                        
        # If we've made it here, just return the command as is
        return command
        
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
