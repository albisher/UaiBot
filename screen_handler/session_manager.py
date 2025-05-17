"""
Screen Session Handler Module
Provides functionality for detecting, interacting with, and managing screen sessions
"""
import re
import subprocess
import os
import tempfile

class ScreenSessionHandler:
    def __init__(self, quiet_mode=False):
        """
        Initialize the screen session handler
        
        Args:
            quiet_mode (bool): If True, reduces unnecessary terminal output
        """
        self.quiet_mode = quiet_mode
        
    def log(self, message):
        """Helper function to print messages when not in quiet mode"""
        if not self.quiet_mode:
            print(message)
    
    def check_screen_exists(self):
        """
        Check if there are any active screen sessions
        
        Returns:
            bool: True if at least one screen session is active, False otherwise
        """
        try:
            result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
            screen_output = result.stdout + result.stderr
            if "No Sockets found" not in screen_output:
                return True
            return False
        except Exception:
            return False
            
    def get_screen_sessions(self):
        """
        Get a list of active screen sessions
        
        Returns:
            list: List of screen session IDs
        """
        try:
            result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
            screen_output = result.stdout + result.stderr
            
            if "No Sockets found" in screen_output:
                return []
                
            # Extract all available screen sessions
            sessions = []
            sessions = re.findall(r'(\d+\.[^\s]+)', screen_output)
            
            # Group sessions into attached and detached
            attached_sessions = [s for s in sessions if "(Attached)" in screen_output.split(s)[1].split("\n")[0]]
            detached_sessions = [s for s in sessions if "(Detached)" in screen_output.split(s)[1].split("\n")[0]]
            
            return {"all": sessions, "attached": attached_sessions, "detached": detached_sessions}
        except Exception as e:
            self.log(f"Error getting screen sessions: {str(e)}")
            return []
            
    def send_to_screen(self, command, session_id=None, device_path=None):
        """
        Send a command to an active screen session
        
        Args:
            command (str): The command to send
            session_id (str): Specific session ID to target, if None will select best match
            device_path (str): Device path to look for in session names, for better matching
            
        Returns:
            str: Result message indicating success or failure
        """
        try:
            # First, get available sessions
            sessions = self.get_screen_sessions()
            
            if not sessions or not sessions.get("all"):
                return "No active screen sessions found.\n" + \
                       "To connect to a USB device first, use a command like:\n" + \
                       "  screen /dev/cu.usbmodem* 115200\n" + \
                       "After you've established a screen session, you can send commands to it."
            
            # Find the best session to use
            target_session = None
            
            # If specific session ID provided, use that
            if session_id and session_id in sessions.get("all", []):
                target_session = session_id
            
            # If device path provided, try to find a matching session
            elif device_path:
                device_name = os.path.basename(device_path)
                possible_matches = []
                for sess in sessions.get("all", []):
                    if device_name.lower() in sess.lower():
                        possible_matches.append(sess)
                
                if possible_matches:
                    target_session = possible_matches[0]
            
            # Otherwise use first attached session, or first session if none attached
            if not target_session:
                if sessions.get("attached"):
                    target_session = sessions["attached"][0]
                elif sessions.get("all"):
                    target_session = sessions["all"][0]
            
            if not target_session:
                return "Could not find a suitable screen session to use."
            
            # Special handling for interactive applications
            is_interactive = False
            interactive_commands = ['vi', 'vim', 'nano', 'less', 'more', 'top', 'man']
            command_base = command.split()[0] if ' ' in command else command
            
            if command_base in interactive_commands:
                is_interactive = True
                self.log(f"Warning: '{command_base}' is an interactive command. It may need additional input in the screen session.")
            
            # Now send the command to the session
            self.log(f"Found screen session: {target_session}")
            
            # Handle special characters in commands properly
            # Check for complex command patterns that might need special handling
            has_complex_syntax = False
            complex_operators = ['|', '>', '<', ';', '&&', '||', '*', '?', '`', '$(', '$', '{', '}', '[', ']']
            for op in complex_operators:
                if op in command:
                    has_complex_syntax = True
                    break
                    
            # Escape single quotes and backslashes in the command if present
            escaped_command = command.replace('\\', '\\\\').replace("'", "\\'")
            
            # For very complex commands, we might need special handling
            if has_complex_syntax:
                self.log("Complex command syntax detected, may require special handling")
                # For commands with redirection, pipes, etc., sometimes writing to a temp script
                # and executing that in the screen session works better
                if any(op in command for op in ['|', '>', '<']):
                    try:
                        # For particularly complex commands, create a temp script and run that                        
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                            f.write("#!/bin/bash\n")
                            f.write(f"{command}\n")
                            temp_script = f.name
                        
                        os.chmod(temp_script, 0o755)
                        self.log(f"Created temporary script: {temp_script}")
                        
                        # First send the command to run the script
                        escaped_command = f"sh {temp_script}"
                    except Exception as script_error:
                        self.log(f"Could not create temp script: {script_error}")
                        # Fall back to direct command
            
            # Try sending the command
            send_cmd = ['screen', '-S', target_session, '-X', 'stuff', f'{escaped_command}\n']
            cmd_result = subprocess.run(send_cmd, capture_output=True, text=True)
            
            # If successful, return success message
            if cmd_result.returncode == 0:
                result_msg = f"Command '{command}' sent to screen session {target_session}"
                if is_interactive:
                    result_msg += "\nNote: This is an interactive command. You may need to interact with it directly in the Terminal window."
                return result_msg
                
            # If failed, try some recovery options
            self.log(f"Command failed with error: {cmd_result.stderr}")
            
            # Try with -d -r first to reattach if needed
            self.log("First attempt failed, trying to reattach the session...")
            
            # Try to reattach the session first
            reattach_cmd = ['screen', '-d', '-r', target_session]
            try:
                subprocess.run(reattach_cmd, timeout=2)
            except subprocess.TimeoutExpired:
                # This is expected, as screen -d -r will not return immediately
                pass
            
            # Try sending the command again
            send_cmd = ['screen', '-S', target_session, '-X', 'stuff', f'{escaped_command}\n']
            cmd_result = subprocess.run(send_cmd, capture_output=True, text=True)
            
            if cmd_result.returncode == 0:
                result_msg = f"Command '{command}' sent to screen session {target_session} (after reattach)"
                if is_interactive:
                    result_msg += "\nNote: This is an interactive command. You may need to interact with it directly in the Terminal window."
                return result_msg
            
            # If still failed on macOS, try AppleScript approach
            import platform
            if platform.system().lower() == "darwin":
                self.log("Command sending still failed, trying AppleScript approach...")
                import os
                # Double escape for AppleScript
                apscript_escaped_cmd = escaped_command.replace('\\', '\\\\')
                script = f"""
                tell application "Terminal"
                    do script "screen -S {target_session} -X stuff '{apscript_escaped_cmd}\\n'" in window 1
                end tell
                """
                os.system(f'osascript -e \'{script}\'')
                result_msg = f"Command '{command}' sent to screen session {target_session} via AppleScript"
                if is_interactive:
                    result_msg += "\nNote: This is an interactive command. You may need to interact with it directly in the Terminal window."
                return result_msg
                
            return f"Failed to send command to screen: {cmd_result.stderr}"
            
        except Exception as e:
            return f"Error sending command to screen: {str(e)}"

# For backward compatibility
SessionManager = ScreenSessionHandler
