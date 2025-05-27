"""
Screen session management module for Labeeb.
Handles sending commands to screen sessions and detecting active sessions.
"""
import subprocess
import re
import os
from src.app.core.platform_core.platform_utils import get_platform_name

class ScreenManager:
    def __init__(self, quiet_mode=False):
        """
        Initialize the ScreenManager.
        
        Args:
            quiet_mode (bool): If True, reduces terminal output
        """
        self.quiet_mode = quiet_mode
        self.system_platform = get_platform_name()
    
    def log(self, message):
        """Print a message if not in quiet mode"""
        if not self.quiet_mode:
            print(message)
    
    def list_sessions(self):
        """
        List all active screen sessions.
        
        Returns:
            dict: Screen sessions with their status (attached/detached)
        """
        try:
            result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
            screen_output = result.stdout + result.stderr
            
            if "No Sockets found" in screen_output:
                return {}
            
            sessions = {}
            session_matches = re.findall(r'(\d+\.[^\s]+)(?:\s+\(([^)]+)\))?', screen_output)
            
            for session_id, status in session_matches:
                sessions[session_id] = status if status else "Unknown"
                
            return sessions
        except Exception as e:
            self.log(f"Error listing screen sessions: {e}")
            return {}
    
    def send_command_to_session(self, command, session_id=None, device_path=None):
        """
        Send a command to a screen session.
        
        Args:
            command (str): Command to send
            session_id (str, optional): Specific session ID to send to
            device_path (str, optional): Device path to look for in session names
            
        Returns:
            str: Result message
        """
        try:
            # Get all available sessions
            sessions = self.list_sessions()
            if not sessions:
                return "No screen sessions available."
            
            # Choose which session to send to
            target_session = session_id
            
            # If no specific session provided, try to find the best match
            if not target_session:
                # First look for a session with the device name if provided
                if device_path:
                    device_name = os.path.basename(device_path)
                    for sess in sessions:
                        if device_name.lower() in sess.lower():
                            target_session = sess
                            break
                
                # If still no target, prefer attached sessions
                if not target_session:
                    attached_sessions = [s for s, status in sessions.items() if "Attached" in status]
                    if attached_sessions:
                        target_session = attached_sessions[0]
                    else:
                        # Take the last (most recent) session as fallback
                        target_session = list(sessions.keys())[-1]
            
            # Check if target session exists
            if target_session not in sessions:
                return f"Session {target_session} not found. Available sessions: {', '.join(sessions.keys())}"
            
            # Handle special characters in commands 
            escaped_command = command.replace('\\', '\\\\').replace("'", "\\'")
            
            # Send command to session
            self.log(f"Sending command to screen session {target_session}: {command}")
            send_cmd = ['screen', '-S', target_session, '-X', 'stuff', f'{escaped_command}\n']
            cmd_result = subprocess.run(send_cmd, capture_output=True, text=True)
            
            # If successful, return confirmation
            if cmd_result.returncode == 0:
                return f"Command '{command}' sent to screen session {target_session}"
            
            # If failed, try reattaching first
            self.log("First attempt failed, trying to reattach the session...")
            reattach_cmd = ['screen', '-d', '-r', target_session]
            try:
                subprocess.run(reattach_cmd, timeout=2)
            except subprocess.TimeoutExpired:
                # Expected behavior as screen -d -r will not return immediately
                pass
            
            # Try sending again
            send_cmd = ['screen', '-S', target_session, '-X', 'stuff', f'{escaped_command}\n']
            cmd_result = subprocess.run(send_cmd, capture_output=True, text=True)
            
            if cmd_result.returncode == 0:
                return f"Command '{command}' sent to screen session {target_session} (after reattach)"
            
            # Try AppleScript approach on macOS as last resort
            if self.system_platform == "darwin":
                self.log("Command sending still failed, trying AppleScript approach...")
                import os
                apscript_escaped_cmd = escaped_command.replace('\\', '\\\\')
                script = f"""
                tell application "Terminal"
                    do script "screen -S {target_session} -X stuff '{apscript_escaped_cmd}\\n'" in window 1
                end tell
                """
                os.system(f'osascript -e \'{script}\'')
                return f"Command '{command}' sent to screen session {target_session} via AppleScript"
            
            return f"Failed to send command to screen: {cmd_result.stderr}"
            
        except Exception as e:
            return f"Error sending command to screen: {str(e)}"
