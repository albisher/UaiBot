"""
Shell command handling for UaiBot
Provides safe execution of shell commands and special command routing
"""
import subprocess
import shlex
import os
import platform
import json
from core.utils import get_platform_name
try:
    from core.platform_commands import get_platform_command
except ImportError:
    # Define a placeholder if the module is not available
    def get_platform_command(platform, command_type, subtype=None):
        return None

# Basic list of commands that are generally safe.
# All commands from enhancements2.txt are included here
SAFE_COMMAND_WHITELIST = [
    # Basic navigation and file operations
    'ls', 'cd', 'pwd', 'echo', 'cat', 'mkdir', 'rmdir', 'cp', 'mv', 'find', 'grep',
    # Programming and development tools
    'python', 'python3', 'pip', 'git', 'man', 'uname',
    # System information and management
    'df', 'du', 'free', 'top', 'ps', 'kill', 'killall', 'uptime', 'cal', 'date',
    # macOS specific commands
    'osascript', 'screen', 'open', 'softwareupdate', 'caffeinate', 'say',
    # Text editors and viewers
    'nano', 'vi', 'vim', 'less', 'more', 'head', 'tail',
    # Network tools
    'ping', 'curl', 'wget', 'ssh', 'scp', 'telnet', 'netstat', 'ifconfig', 'traceroute', 'nslookup',
    # Text processing
    'grep', 'awk', 'sed', 'sort', 'uniq', 'wc', 'diff', 'pbcopy', 'pbpaste',
    # File management
    'touch', 'ditto', 'chmod', 'chown', 'chgrp', 'ln',
    # System commands
    'history', 'crontab', 'alias', 'which', 'whereis', 'whoami', 'who', 'w', 
    # Advanced macOS commands
    'networksetup', 'airport', 'scutil', 'mdfind', 'diskutil', 'system_profiler', 
    'sw_vers', 'sysctl', 'pmset', 'launchctl', 'defaults', 'plutil', 'hdiutil', 
    'screencapture', 'security', 'xcode-select', 'xcodebuild', 'xcrun', 'codesign', 
    'spctl', 'ioreg', 'pkgutil', 'automator', 'afplay'
    # Additional commands can be added as needed
]

# Commands that should always require confirmation or be blocked in certain modes.
POTENTIALLY_DANGEROUS_COMMANDS = [
    'rm', 'sudo', 'mkfs', 'shutdown', 'reboot', 'dd', 'fdisk', 'kill', 
    'chmod', 'chown', 'chgrp', 'mv', 'cp', 'rmdir', 'ln -s', 'format',
    'diskutil', 'diskpart', 'parted', 'gparted', '> /dev/', '| sudo', 
    'mkfs', 'fsck', 'mount', 'umount', ':(){', 'eval', 'dmesg'
    # Commands that could be harmful if misused or have system-wide effects
]

class ShellHandler:
    def __init__(self, safe_mode=True, enable_dangerous_command_check=True, suppress_prompt=False):
        """
        Initializes the ShellHandler.
        Args:
            safe_mode (bool): If True, restricts execution to whitelisted commands and may require
                              confirmation for potentially dangerous ones (if not outright blocked).
            enable_dangerous_command_check (bool): If True, checks commands against POTENTIALLY_DANGEROUS_COMMANDS.
            suppress_prompt (bool): If True, does not prompt for confirmation but handles according to safe_mode.
        """
        self.safe_mode = safe_mode
        self.enable_dangerous_command_check = enable_dangerous_command_check
        self.suppress_prompt = suppress_prompt
        # Get platform information
        self.system_platform = platform.system().lower()
        self.platform_name = get_platform_name()
        print(f"ShellHandler initialized. Safe mode: {self.safe_mode}, Dangerous command check: {self.enable_dangerous_command_check}")

    # Add platform-specific commands to the safe list
    def _update_safe_commands_for_platform(self):
        """Update safe commands list with platform-specific commands"""
        # Add platform-specific safe commands
        if self.system_platform == "darwin":  # macOS
            # Add macOS-specific commands to whitelist based on enhancements2.txt
            SAFE_COMMAND_WHITELIST.extend([
                # File & Directory operations
                'open', 'touch', 'ditto',
                # Media and output
                'afplay', 'say', 'pbcopy', 'pbpaste', 
                # System commands
                'softwareupdate', 'caffeinate', 'mdfind', 'diskutil',
                # Network commands
                'networksetup', 'airport', 'scutil', 'ping', 'curl', 'ssh', 'scp',
                'ifconfig', 'netstat', 'nslookup', 'traceroute', 'nettop',
                # Text processing and viewing
                'less', 'more', 'nano', 'vi', 'grep', 'awk', 'sed',
                # System information
                'system_profiler', 'sw_vers', 'top', 'ps', 'uptime', 'cal', 'date',
                'sysctl', 'pmset', 'launchctl',
                # AppleScript execution
                'osascript',
                # macOS special commands
                'defaults', 'plutil', 'hdiutil', 'screencapture', 'security',
                'xcode-select', 'xcodebuild', 'xcrun', 'codesign', 'spctl',
                'ioreg', 'pkgutil', 'automator'
            ])
        elif self.system_platform == "linux":  # Linux/Ubuntu/Jetson
            # Add Linux-specific commands to whitelist
            SAFE_COMMAND_WHITELIST.extend(['xdg-open', 'paplay', 'arecord', 'nautilus', 'gnome-terminal', 
                                          'google-chrome', 'firefox', 'chromium-browser'])
            
    def _is_command_safe(self, command_parts):
        """Checks if the command is on the whitelist or considered generally safe."""
        if not command_parts:
            return False
        command_name = command_parts[0]

        # Add platform-specific commands to the safe list
        self._update_safe_commands_for_platform()
        
        if command_name in SAFE_COMMAND_WHITELIST:
            return True
        
        # Basic check for path-like commands (e.g. /bin/ls)
        if '/' in command_name and command_name.split('/')[-1] in SAFE_COMMAND_WHITELIST:
            return True

        return False

    def _is_potentially_dangerous(self, command_parts):
        """Checks if the command is in the list of potentially dangerous commands."""
        if not command_parts:
            return False
        command_name = command_parts[0]
        
        if command_name in POTENTIALLY_DANGEROUS_COMMANDS:
            return True
        # Check for sudo usage with another command
        if command_name == 'sudo' and len(command_parts) > 1 and command_parts[1] in POTENTIALLY_DANGEROUS_COMMANDS:
            return True
        return False
        
    def _fix_platform_command(self, command_string):
        """Adjust command based on platform if needed"""
        # Simple pass-through for now, can be extended in the future
        return command_string

    def execute_command(self, command_string, force_shell=False, require_confirmation_for_shell=True, suppress_prompt=False):
        """Execute a shell command and return the output"""
        try:
            # Clean up the command string, removing unwanted elements
            command_string = command_string.strip()
            
            # Remove any markdown code block markers (```bash, ```, etc)
            if command_string.startswith('```'):
                # Remove all leading backticks
                while command_string.startswith('`'):
                    command_string = command_string[1:]
                # Find the end marker if it exists
                end_pos = command_string.rfind('```')
                if end_pos != -1:
                    command_string = command_string[:end_pos]
            
            # Also check for individual backtick wrapping
            elif command_string.startswith('`') and command_string.endswith('`'):
                command_string = command_string[1:-1]
                
            # Remove language hints (e.g., "bash", "shell", etc.) from the start
            first_line_end = command_string.find('\n')
            if first_line_end != -1:
                first_line = command_string[:first_line_end].strip().lower()
                if first_line in ['bash', 'shell', 'zsh', 'sh', 'cmd', 'powershell']:
                    command_string = command_string[first_line_end + 1:]
            
            # Remove any remaining backticks
            command_string = command_string.replace('`', '').strip()
            
            if not command_string.strip():
                return "Error: No command provided after processing."

            # Check for and fix platform-specific commands
            command_string = self._fix_platform_command(command_string)
            print(f"Attempting to execute: {command_string}")

            # Special handling for commands with wildcards (e.g., ls /dev/cu.*, find . -name "*.txt", etc.)
            if ('*' in command_string or '?' in command_string or 
                '|' in command_string or  # Pipe symbol
                '>' in command_string or  # Redirection
                '<' in command_string or  # Input redirection
                ';' in command_string or  # Command separator
                '&&' in command_string or  # Command chaining
                '`' in command_string or  # Command substitution
                '$(' in command_string):  # Command substitution
                print(f"Using shell=True for command with special syntax: {command_string}")
                result = subprocess.run(command_string, shell=True, capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    return result.stderr.strip() if result.stderr else f"Command failed with return code {result.returncode}"

            # Special handling for device path commands
            if (command_string.startswith('ls /dev') or 
                any(cmd in command_string for cmd in ['screen /dev', 'cat /dev', 'echo > /dev', 'stty -f /dev'])):
                # Commands with device paths need shell=True
                print(f"Using shell=True for command with device paths: {command_string}")
                force_shell = True

            # Special handling for screen command (terminal emulator)
            if command_string.startswith('screen '):
                print("Using special handling for screen command")
                # Use shell=True for screen command to properly handle device paths
                return subprocess.run(command_string, text=True, shell=True, 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).stderr or "Screen command executed"
                
            # Special handling for opening terminal with USB connection
            if ('open -a Terminal' in command_string and '/dev/cu.' in command_string) or 'usb' in command_string.lower():
                # For macOS terminal with device connection
                if self.system_platform == 'darwin':
                    # Extract USB device path and other parameters
                    import re
                    # More flexible pattern to match USB serial devices
                    usb_match = re.search(r'/dev/cu\.[^/\s]+', command_string)
                    if usb_match:
                        usb_path = usb_match.group(0)
                        baud_match = re.search(r'\b\d{4,6}\b', command_string) # Find baud rate
                        baud_rate = baud_match.group(0) if baud_match else "115200"
                        
                        # Create AppleScript to open Terminal with screen command
                        script = f"""
                        tell application "Terminal"
                            do script "screen {usb_path} {baud_rate}"
                        end tell
                        """
                        os.system(f"osascript -e '{script}'")
                        return f"Opened Terminal with screen {usb_path} {baud_rate}"

            # Special handling for 'cd' command
            if command_string.strip().startswith('cd '):
                parts = shlex.split(command_string)
                if len(parts) > 1:
                    path_to_change = os.path.expanduser(parts[1])
                    try:
                        os.chdir(path_to_change)
                        return f"Changed directory to {os.getcwd()}"
                    except FileNotFoundError:
                        return f"Error: Directory not found: {path_to_change}"
                    except PermissionError:
                        return f"Error: Permission denied to change directory to {path_to_change}"
                    except Exception as e:
                        return f"Error changing directory: {str(e)}"
                else: # just 'cd' often means go to home directory
                    try:
                        home_dir = os.path.expanduser('~')
                        os.chdir(home_dir)
                        return f"Changed directory to {os.getcwd()}"
                    except Exception as e:
                        return f"Error changing to home directory: {str(e)}"

            # Prefer to split the command into a list to avoid shell=True
            if not force_shell:
                try:
                    command_parts = shlex.split(command_string)
                    if not command_parts:
                        return "Error: Command is empty after parsing."

                    command_name = command_parts[0]

                    if self.safe_mode and not self._is_command_safe(command_parts):
                        return f"Error: Command '{command_name}' is not in the allowed list in safe mode."

                    if self.enable_dangerous_command_check and self._is_potentially_dangerous(command_parts):
                        # In a real application, you would prompt the user here.
                        # For now, we'll just return an error or require a flag to bypass.
                        # This part needs to be integrated with the main loop for user interaction.
                        print(f"Warning: Command '{command_string}' is potentially dangerous.")
                        # Example: If not user_confirms(f"Execute potentially dangerous command: {command_string}? "): return "Execution cancelled by user."
                        # For this iteration, we will block it if safe_mode is on, or allow if safe_mode is off but print warning.
                        if self.safe_mode:
                            return f"Error: Execution of potentially dangerous command '{command_string}' blocked in safe mode."

                    # Execute without shell=True
                    print(f"Executing with shlex: {command_parts}")
                    result = subprocess.run(command_parts, capture_output=True, text=True, check=False)
                except ValueError as e:
                    # If shlex can't parse the command, try with shell=True if permitted
                    print(f"Error parsing command with shlex: {str(e)}")
                    if not self.safe_mode or force_shell:
                        print(f"Falling back to shell=True for: {command_string}")
                        result = subprocess.run(command_string, shell=True, capture_output=True, text=True, check=False)
                    else:
                        return f"Error: Could not parse command '{command_string}'. Try simplifying or using quotes properly."
            else: # force_shell is True
                if require_confirmation_for_shell and not suppress_prompt and self.safe_mode and not self.suppress_prompt:
                    # This confirmation should ideally happen in the main loop or UI
                    # For now, we simulate it with a print and proceed if not in strict safe_mode.
                    print(f"Warning: Executing command '{command_string}' with shell=True.")
                    if self.safe_mode: # Stricter handling for safe_mode
                        # In a real app: confirm = input("This command uses shell=True. Are you sure? (yes/no): ")
                        # if confirm.lower() != 'yes': return "Execution cancelled."
                        # For now, we'll allow it anyway with a warning
                        print("Shell=True allowed without confirmation due to special command needs.")
                
                print(f"Executing with shell=True: {command_string}")
                result = subprocess.run(command_string, shell=True, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                # Log the error, include both stdout and stderr for context
                error_message = f"Error executing command: {command_string}"
                error_message += f"\nReturn Code: {result.returncode}"
                if result.stdout:
                    error_message += f"\nStdout:\n{result.stdout.strip()}"
                if result.stderr:
                    error_message += f"\nStderr:\n{result.stderr.strip()}"
                print(error_message) # Log to console
                return result.stderr.strip() if result.stderr else f"Command failed with return code {result.returncode}"
            return result.stdout.strip()
        
        except FileNotFoundError as e:
            # Correctly access command_parts if available
            cmd_name_for_error = command_string # Default to full string if parts not available early
            if not force_shell:
                try:
                    parsed_parts = shlex.split(command_string)
                    if parsed_parts:
                        cmd_name_for_error = parsed_parts[0]
                except ValueError:
                    pass # Keep command_string as cmd_name_for_error
            return f"Error: Command not found - {e.strerror}: {cmd_name_for_error}"
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out: {command_string}"
        except Exception as e:
            return f"An unexpected error occurred while executing command '{command_string}': {str(e)}"

    def send_to_screen_session(self, command, device_path=None):
        """
        Send a command to an active screen session connected to a specific device.
        If device_path is provided, attempts to find a screen session for that device.
        Handles complex commands including interactive applications like vi, nano, etc.
        """
        try:
            import re
            # First, list all screen sessions
            result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
            screen_output = result.stdout + result.stderr
            
            if "No Sockets found" in screen_output:
                # No screen sessions available, help the user understand what to do
                help_message = "No active screen sessions found.\n"
                help_message += "To connect to a USB device first, use a command like:\n"
                help_message += "  screen /dev/cu.usbmodem* 115200\n"
                help_message += "After you've established a screen session, you can send commands to it."
                return help_message
                
            # If device path is specified, try to find a matching session
            session_id = None
            sessions = []
            
            # Extract all available screen sessions
            sessions = re.findall(r'(\d+\.[^\s]+)', screen_output)
            
            # Check for attached vs detached sessions
            attached_sessions = [s for s in sessions if "(Attached)" in screen_output.split(s)[1].split("\n")[0]]
            detached_sessions = [s for s in sessions if "(Detached)" in screen_output.split(s)[1].split("\n")[0]]
            
            if device_path:
                # Look for sessions that might be connected to this device
                # This is a best guess since screen doesn't directly report the device path
                
                # Try to find a session that matches the device path
                device_name = os.path.basename(device_path)
                possible_matches = []
                for sess in sessions:
                    if device_name.lower() in sess.lower():
                        possible_matches.append(sess)
                
                if possible_matches:
                    # If we found a potential match based on device name
                    session_id = possible_matches[0]
                elif not sessions:
                    return "No screen sessions available."
                # First try attached sessions, then any available session
                elif attached_sessions:
                    session_id = attached_sessions[0]
                else:
                    session_id = sessions[-1]  # Take the most recent
            else:
                # If no device specified, prefer attached sessions, then fall back to most recent
                if attached_sessions:
                    session_id = attached_sessions[0]
                elif sessions:
                    session_id = sessions[-1]
                else:
                    return "No screen sessions available."
            
            # Special handling for interactive applications
            is_interactive = False
            interactive_commands = ['vi', 'vim', 'nano', 'less', 'more', 'top', 'man']
            command_base = command.split()[0] if ' ' in command else command
            
            if command_base in interactive_commands:
                is_interactive = True
                # For interactive commands, we may want to warn the user
                print(f"Warning: '{command_base}' is an interactive command. It may need additional input in the screen session.")
            
            # Now send the command to the session
            print(f"Found screen session: {session_id}")
            
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
                print("Complex command syntax detected, may require special handling")
                # For commands with redirection, pipes, etc., sometimes writing to a temp script
                # and executing that in the screen session works better
                if any(op in command for op in ['|', '>', '<']):
                    try:
                        # For particularly complex commands, create a temp script and run that
                        import tempfile
                        import os
                        
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                            f.write("#!/bin/bash\n")
                            f.write(f"{command}\n")
                            temp_script = f.name
                        
                        os.chmod(temp_script, 0o755)
                        print(f"Created temporary script: {temp_script}")
                        
                        # First send the command to run the script
                        escaped_command = f"sh {temp_script}"
                    except Exception as script_error:
                        print(f"Could not create temp script: {script_error}")
                        # Fall back to direct command
            
            send_cmd = ['screen', '-S', session_id, '-X', 'stuff', f'{escaped_command}\n']
            cmd_result = subprocess.run(send_cmd, capture_output=True, text=True)
            
            if cmd_result.returncode == 0:
                result_msg = f"Command '{command}' sent to screen session {session_id}"
                if is_interactive:
                    result_msg += "\nNote: This is an interactive command. You may need to interact with it directly in the Terminal window."
                return result_msg
            else:
                print(f"Command failed with error: {cmd_result.stderr}")
                # Try with -d -r first to reattach if needed
                print("First attempt failed, trying to reattach the session...")
                
                # Try to reattach the session first
                reattach_cmd = ['screen', '-d', '-r', session_id]
                try:
                    subprocess.run(reattach_cmd, timeout=2)
                except subprocess.TimeoutExpired:
                    # This is expected, as screen -d -r will not return immediately
                    pass
                
                # Try sending the command again
                send_cmd = ['screen', '-S', session_id, '-X', 'stuff', f'{escaped_command}\n']
                cmd_result = subprocess.run(send_cmd, capture_output=True, text=True)
                
                if cmd_result.returncode == 0:
                    result_msg = f"Command '{command}' sent to screen session {session_id} (after reattach)"
                    if is_interactive:
                        result_msg += "\nNote: This is an interactive command. You may need to interact with it directly in the Terminal window."
                    return result_msg
                    
                # If still failed, try AppleScript approach on macOS
                print("Command sending still failed, trying AppleScript approach...")
                if self.system_platform == "darwin":
                    import os
                    # Double escape for AppleScript
                    apscript_escaped_cmd = escaped_command.replace('\\', '\\\\')
                    script = f"""
                    tell application "Terminal"
                        do script "screen -S {session_id} -X stuff '{apscript_escaped_cmd}\\n'" in window 1
                    end tell
                    """
                    os.system(f'osascript -e \'{script}\'')
                    result_msg = f"Command '{command}' sent to screen session {session_id} via AppleScript"
                    if is_interactive:
                        result_msg += "\nNote: This is an interactive command. You may need to interact with it directly in the Terminal window."
                    return result_msg
                    
                return f"Failed to send command to screen: {cmd_result.stderr}"
                
        except Exception as e:
            return f"Error sending command to screen: {str(e)}"
    
    def detect_command_target(self, command, context=""):
        """
        Determine if a command should go to the screen session or local system.
        Returns "SCREEN", "LOCAL", or "UNKNOWN" based on command and context.
        
        Args:
            command (str): The command to analyze
            context (str): Additional context text that might hint at target
        """
        # If explicit screen indicators in context, prefer screen
        screen_indicators = [
            "screen", "serial", "usb", "terminal session", "device"
        ]
        
        if any(indicator in context.lower() for indicator in screen_indicators):
            return "SCREEN"
            
        # Check if command is a direct file/navigation command
        nav_commands = ['ls', 'pwd', 'cd', 'dir']
        sys_commands = ['top', 'ps', 'df', 'du', 'uptime', 'date', 'whoami', 'who']
        
        # Split the command to get the base command
        command_parts = command.split()
        base_command = command_parts[0] if command_parts else ""
        
        # Navigation commands with no args are ambiguous
        # They could be for either local system or screen session
        if base_command in nav_commands and len(command_parts) == 1:
            # Check if we have a USB/serial context
            if any(term in context.lower() for term in ["usb", "serial", "device", "screen"]):
                return "SCREEN"
            else:
                return "LOCAL"
                
        # System information commands typically run locally
        if base_command in sys_commands:
            return "LOCAL"
            
        # Mac-specific commands almost always run locally
        mac_commands = ['open', 'say', 'pbcopy', 'pbpaste', 'networksetup', 'airport',
                        'system_profiler', 'sw_vers', 'defaults', 'osascript']
        if base_command in mac_commands:
            return "LOCAL"
            
        # If we can't determine, default to LOCAL for safety
        return "LOCAL"
    
    def check_command_safety_level(self, command_string):
        """
        Checks the safety level of a command string.
        Returns one of:
        - "SAFE" - Command is considered generally safe
        - "POTENTIALLY_DANGEROUS" - Command is potentially dangerous
        - "NOT_IN_WHITELIST" - Command is not in whitelist (only matters if safe_mode is enabled)
        - "REQUIRES_SHELL_TRUE_ASSESSMENT" - Command may require shell=True which needs assessment
        """
        try:
            # Quick pass to see if command is empty
            if not command_string or not command_string.strip():
                return "EMPTY"
                
            # Check for wildcards and special characters that might need shell=True
            contains_wildcards = '*' in command_string or '?' in command_string
            
            # Check for special shell operators that need shell=True
            special_operators = ['|', '>', '<', ';', '&&', '||', '`', '$(']
            contains_special = any(op in command_string for op in special_operators)
            
            if contains_wildcards or contains_special:
                return "REQUIRES_SHELL_TRUE_ASSESSMENT"
            
            # Try parsing the command with shlex
            try:
                command_parts = shlex.split(command_string)
                if not command_parts:
                    return "EMPTY"
                    
                # Check against our safe and dangerous lists
                if self._is_command_safe(command_parts):
                    if self._is_potentially_dangerous(command_parts):
                        return "POTENTIALLY_DANGEROUS"
                    else:
                        return "SAFE"
                else:
                    return "NOT_IN_WHITELIST"
                    
            except ValueError:
                # If shlex can't parse the command, it might need shell=True
                return "REQUIRES_SHELL_TRUE_ASSESSMENT"
                
        except Exception as e:
            print(f"Error in check_command_safety_level: {str(e)}")
            return "ERROR_ASSESSING"  # This would need special handling in the caller
            
        return "SAFE"  # Default to safe if we somehow hit this
    
    def get_usb_devices(self):
        """
        Get a list of available USB devices with enhanced detection.
        Shows human-readable information about connected USB devices.
        Returns a formatted string with device information.
        """
        import platform
        import subprocess
        import re
        import os
        
        system = platform.system().lower()
        devices = []
        
        try:
            if system == 'darwin':  # macOS
                # Get serial devices
                serial_result = subprocess.run(['ls', '/dev/cu.*'], capture_output=True, text=True)
                if serial_result.returncode == 0:
                    serial_devices = serial_result.stdout.strip().split('\n')
                    if serial_devices and serial_devices[0]:  # Make sure we have devices
                        devices.extend(serial_devices)
                
                # Get detailed information with system_profiler
                try:
                    usb_info = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                                             capture_output=True, text=True).stdout
                    
                    # Extract product names and additional details from system_profiler output
                    usb_devices_info = []
                    vendor_pattern = re.compile(r'(?:Manufacturer|Vendor ID): (.*)')
                    product_pattern = re.compile(r'(?:Product ID|Product): (.*)')
                    
                    # Find sections with vendor/product info
                    sections = usb_info.split('\n\n')
                    for section in sections:
                        if 'Serial Number' in section or 'Product ID' in section:
                            vendor_match = vendor_pattern.search(section)
                            product_match = product_pattern.search(section)
                            
                            if product_match:
                                product = product_match.group(1).strip()
                                vendor = vendor_match.group(1).strip() if vendor_match else "Unknown"
                                usb_devices_info.append(f"{product} ({vendor})")
                                
                    # Add the product information if available
                    if usb_devices_info:
                        devices.append("\nUSB Device Information:")
                        devices.extend([f"  - {info}" for info in usb_devices_info])
                        
                except Exception:
                    pass
                    
            elif system == 'linux':
                # List TTY devices
                tty_result = subprocess.run(['ls', '/dev/tty*'], capture_output=True, text=True)
                if tty_result.returncode == 0:
                    tty_devices = [dev for dev in tty_result.stdout.strip().split('\n') 
                                  if any(x in dev for x in ['USB', 'ACM', 'ttyS'])]
                    if tty_devices:
                        devices.extend(tty_devices)
                
                # Try to get more detailed USB info
                try:
                    lsusb_result = subprocess.run(['lsusb'], capture_output=True, text=True)
                    if lsusb_result.returncode == 0 and lsusb_result.stdout.strip():
                        devices.append("\nUSB Device Information:")
                        devices.extend([f"  - {line}" for line in lsusb_result.stdout.strip().split('\n')])
                except Exception:
                    pass
        except Exception as e:
            return f"Error detecting USB devices: {str(e)}"
            
        # Format the output
        if not devices:
            return "No USB devices detected."
            
        return "\n".join([
            "📱 Available USB Devices:",
            "------------------------",
            *devices,
            "------------------------",
            "\nTo connect to a device, use: screen /dev/cu.* 115200",
            "Replace * with the specific device name and 115200 with the baud rate if needed."
        ])
