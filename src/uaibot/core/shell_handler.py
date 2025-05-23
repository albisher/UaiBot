"""
Shell command handling for UaiBot in a modular structure.
This version removes the send_to_screen_session method and uses the ScreenManager instead.
"""
import subprocess
import shlex
import os
import platform
import json
import enum
import re
from uaibot.utils import get_platform_name, run_command
from uaibot.core.device_manager.usb_detector import USBDetector
from uaibot.core.browser_handler import BrowserHandler
from uaibot.core.file_search import FileSearch

# Define CommandSafetyLevel enumeration to fix the import error
class CommandSafetyLevel(enum.Enum):
    """Safety levels for shell commands."""
    SAFE = "SAFE"
    NOT_IN_WHITELIST = "NOT_IN_WHITELIST" 
    POTENTIALLY_DANGEROUS = "POTENTIALLY_DANGEROUS"
    REQUIRES_SHELL_TRUE = "REQUIRES_SHELL_TRUE"
    EMPTY = "EMPTY"
    UNKNOWN = "UNKNOWN"
    JSON_PLAN = "JSON_PLAN"  # New type for JSON plans
    SEMI_DANGEROUS = "SEMI_DANGEROUS"  # New type for commands that need extra verification

# Basic list of commands that are generally safe.
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
]

# Commands that should always require confirmation or be blocked in certain modes.
POTENTIALLY_DANGEROUS_COMMANDS = [
    'rm', 'sudo', 'mkfs', 'shutdown', 'reboot', 'dd', 'fdisk', 'kill', 
    'chmod', 'chown', 'chgrp', 'mv', 'cp', 'rmdir', 'ln -s', 'format',
    'diskutil', 'diskpart', 'parted', 'gparted', '> /dev/', '| sudo', 
    'mkfs', 'fsck', 'mount', 'umount', ':(){', 'eval', 'dmesg'
]

class ShellHandler:
    def __init__(self, safe_mode=True, enable_dangerous_command_check=True, suppress_prompt=False, quiet_mode=False, fast_mode=False):
        """
        Initializes the ShellHandler.
        Args:
            safe_mode (bool): If True, restricts execution to whitelisted commands.
            enable_dangerous_command_check (bool): If True, checks commands against POTENTIALLY_DANGEROUS_COMMANDS.
            suppress_prompt (bool): If True, does not prompt for confirmation.
            quiet_mode (bool): If True, reduces unnecessary terminal output.
            fast_mode (bool): If True, doesn't wait for feedback on errors, exits immediately.
        """
        # If fast_mode is enabled, override safe_mode and dangerous command check
        if fast_mode:
            safe_mode = False
            enable_dangerous_command_check = False
        self.safe_mode = safe_mode
        self.enable_dangerous_command_check = enable_dangerous_command_check
        self.suppress_prompt = suppress_prompt
        self.quiet_mode = quiet_mode
        self.fast_mode = fast_mode
        self.system_platform = platform.system().lower()
        self.platform_name = get_platform_name()
        
        # Will be assigned externally
        self.screen_manager = None
        
        # Create a USB device detector
        self.usb_detector = USBDetector(quiet_mode=quiet_mode)
        
        # Create a browser handler
        self.browser_handler = BrowserHandler(shell_handler=self)
        
        # Use log method instead of direct print
        self._log_debug(f"ShellHandler initialized. Safe mode: {self.safe_mode}, Dangerous command check: {self.enable_dangerous_command_check}, Fast mode: {self.fast_mode}")
        
        # Create a FileSearch instance
        self.file_search = FileSearch(quiet_mode=quiet_mode)
    
    def _log(self, message):
        """Print a message if not in quiet mode"""
        if not self.quiet_mode:
            # Check if we're running in main.py context where a log function might be available
            import sys
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, 'log'):
                # Use the main module's log function
                main_module.log(message, debug_only=False)
            else:
                # Fall back to print but only in non-quiet mode
                print(message)

    def _log_debug(self, message):
        """Log debug messages if not in quiet mode"""
        if not self.quiet_mode:
            # Check if we're running in main.py context
            import sys
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, 'log'):
                # Use the main module's log function with debug flag
                main_module.log(message, debug_only=True)
            # For debug messages, we don't print directly even if log function is not available
            # This change ensures debug messages like initialization don't appear unless logged by main
    
    def log(self, message):
        """Print a message if not in quiet mode"""
        if not self.quiet_mode:
            print(message)
    
    # Update safe commands for the current platform
    def _update_safe_commands_for_platform(self):
        """Update safe commands list with platform-specific commands"""
        # Platform-specific commands are already included in the whitelist
        pass
    
    def is_command_safe(self, command):
        """
        Public method to check if a command is safe.
        Forwards to the internal _is_command_safe method after splitting the command.
        
        Args:
            command (str): The command string to check
            
        Returns:
            bool: True if the command is considered safe, False otherwise
        """
        try:
            command_parts = shlex.split(command)
            return self._is_command_safe(command_parts)
        except ValueError:
            # If shlex cannot split (e.g. unmatched quotes), consider unsafe
            return False
        
    def _is_command_safe(self, command_parts):
        """Checks if the command is on the whitelist."""
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
    
    def assess_command_safety(self, command_string):
        """
        Enhanced command safety assessment that handles JSON plans and provides detailed risk analysis.
        Returns:
            tuple: (CommandSafetyLevel, dict) - Safety level and additional assessment info
        """
        assessment_info = {
            "confidence": 1.0,
            "risk_level": "low",
            "requires_admin": False,
            "potential_impact": [],
            "recommendation": ""
        }

        if not command_string.strip():
            return CommandSafetyLevel.EMPTY, assessment_info

        # Check if it's a JSON plan
        if command_string.strip().startswith('{') or command_string.strip().startswith('```json'):
            try:
                # Clean up the command string if it's a markdown code block
                if command_string.strip().startswith('```'):
                    command_string = command_string.strip('`').lstrip('json').strip()
                
                # Parse the JSON
                plan_data = json.loads(command_string)
                
                # If it's a plan, assess each step
                if isinstance(plan_data, dict) and 'plan' in plan_data:
                    assessment_info["confidence"] = plan_data.get('confidence', 0.5)
                    assessment_info["recommendation"] = "Process as structured plan"
                    return CommandSafetyLevel.JSON_PLAN, assessment_info
            except json.JSONDecodeError:
                pass  # Not valid JSON, continue with normal assessment

        try:
            command_parts = shlex.split(command_string)
            if not command_parts:
                return CommandSafetyLevel.EMPTY, assessment_info
        except ValueError:
            return CommandSafetyLevel.REQUIRES_SHELL_TRUE, assessment_info

        # Check for dangerous commands
        if self.enable_dangerous_command_check:
            if self._is_potentially_dangerous(command_parts):
                assessment_info.update({
                    "risk_level": "high",
                    "requires_admin": True,
                    "potential_impact": ["System modification", "Data loss", "Security risk"],
                    "recommendation": "Requires admin confirmation"
                })
                return CommandSafetyLevel.POTENTIALLY_DANGEROUS, assessment_info

        # Check for semi-dangerous commands
        semi_dangerous_patterns = [
            (r'rm\s+.*\*', "Deleting multiple files"),
            (r'chmod\s+.*777', "Setting wide permissions"),
            (r'chown\s+.*root', "Changing ownership to root"),
            (r'mv\s+.*\/', "Moving files to system directories"),
            (r'cp\s+.*\/', "Copying files to system directories")
        ]

        for pattern, impact in semi_dangerous_patterns:
            if re.search(pattern, command_string):
                assessment_info.update({
                    "risk_level": "medium",
                    "requires_admin": False,
                    "potential_impact": [impact],
                    "recommendation": "Verify command intent"
                })
                return CommandSafetyLevel.SEMI_DANGEROUS, assessment_info

        # Check whitelist in safe mode
        if self.safe_mode and not self._is_command_safe(command_parts):
            assessment_info.update({
                "risk_level": "medium",
                "recommendation": "Command not in whitelist"
            })
            return CommandSafetyLevel.NOT_IN_WHITELIST, assessment_info

        # Check for shell operators
        shell_operators = ['|', '>', '<', '>>', '<<', '&&', '||', ';']
        if any(operator in command_string for operator in shell_operators):
            assessment_info.update({
                "risk_level": "low",
                "recommendation": "Use shell=True for execution"
            })
            return CommandSafetyLevel.REQUIRES_SHELL_TRUE, assessment_info

        return CommandSafetyLevel.SAFE, assessment_info

    def execute_command(self, command, force_shell=False, timeout=None):
        """Execute a shell command with enhanced safety checks."""
        # Use a shorter timeout in fast mode
        if self.fast_mode and timeout is None:
            timeout = 5

        # Assess command safety
        safety_level, assessment = self.assess_command_safety(command)
        
        # Handle JSON plans
        if safety_level == CommandSafetyLevel.JSON_PLAN:
            try:
                # Clean up the command string if it's a markdown code block
                if command.strip().startswith('```'):
                    command = command.strip('`').lstrip('json').strip()
                
                # Parse the JSON plan
                plan_data = json.loads(command)
                
                # Process the plan
                if isinstance(plan_data, dict) and 'plan' in plan_data:
                    results = []
                    for step in plan_data['plan']:
                        operation = step.get('operation')
                        parameters = step.get('parameters', {})
                        
                        # Execute the step
                        if operation == 'shell' and 'command' in parameters:
                            step_result = self.execute_command(parameters['command'])
                            results.append(f"Step '{step.get('description', '')}': {step_result}")
                        else:
                            results.append(f"Step '{step.get('description', '')}': Operation '{operation}' not supported")
                    
                    return "\n".join(results)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON plan format"

        # Handle dangerous commands
        if safety_level == CommandSafetyLevel.POTENTIALLY_DANGEROUS:
            if not self.suppress_prompt:
                print(f"\n⚠️ Warning: This command is potentially dangerous:")
                print(f"Command: {command}")
                print(f"Risk Level: {assessment['risk_level']}")
                print(f"Potential Impact: {', '.join(assessment['potential_impact'])}")
                if assessment['requires_admin']:
                    print("\nThis command requires admin privileges.")
                    admin_pass = input("Enter admin password to continue (or press Enter to cancel): ")
                    if not admin_pass:
                        return "Command execution cancelled by user."
                else:
                    confirm = input("\nAre you sure you want to proceed? (y/N): ")
                    if confirm.lower() != 'y':
                        return "Command execution cancelled by user."

        # Handle semi-dangerous commands
        if safety_level == CommandSafetyLevel.SEMI_DANGEROUS:
            if not self.suppress_prompt:
                print(f"\n⚠️ Note: This command may have significant effects:")
                print(f"Command: {command}")
                print(f"Potential Impact: {', '.join(assessment['potential_impact'])}")
                confirm = input("\nDo you want to proceed? (y/N): ")
                if confirm.lower() != 'y':
                    return "Command execution cancelled by user."

        # Execute the command
        try:
            if not force_shell and "|" not in command and ">" not in command and "<" not in command and "*" not in command:
                args = shlex.split(command)
                process = subprocess.run(
                    args,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False
                )
            else:
                process = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False
                )

            if process.returncode != 0:
                if process.stderr:
                    return process.stderr
                return f"Command failed with return code {process.returncode}"
            return process.stdout

        except FileNotFoundError:
            return f"Command not found: {command}"
        except PermissionError:
            return f"Permission denied when running: {command}"
        except subprocess.TimeoutExpired:
            if self.fast_mode:
                return f"Command timed out after {timeout} seconds. Fast mode enabled, not retrying."
            return f"Command timed out after {timeout} seconds: {command}"
        except Exception as e:
            return f"Error executing command: {command}\n{str(e)}"
    
    def detect_command_target(self, command, context=""):
        """
        Determine if a command should go to the screen session or local system.
        
        Args:
            command (str): The command to analyze
            context (str): Additional context text that might hint at target
            
        Returns:
            str: "SCREEN", "LOCAL", or "UNKNOWN"
        """
        # If explicit screen indicators in context, prefer screen
        screen_indicators = [
            "screen", "serial", "usb", "terminal session", "device", 
            "remote", "remote system", "remote machine", "other os", 
            "other machine", "screened", "over usb", "over the usb", 
            "connected device", "through screen"
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
    
    def assess_command_safety(self, command_string):
        """
        Assesses the safety level of a command string.
        Returns:
            CommandSafetyLevel: The safety level enum value
        """
        if not command_string.strip():
            return CommandSafetyLevel.EMPTY

        try:
            command_parts = shlex.split(command_string)
            if not command_parts:
                return CommandSafetyLevel.EMPTY
        except ValueError:
            # If shlex cannot split (e.g. unmatched quotes)
            # Consider it potentially requiring shell=True
            return CommandSafetyLevel.REQUIRES_SHELL_TRUE

        if self.enable_dangerous_command_check and self._is_potentially_dangerous(command_parts):
            return CommandSafetyLevel.POTENTIALLY_DANGEROUS
        
        if self.safe_mode and not self._is_command_safe(command_parts):
            return CommandSafetyLevel.NOT_IN_WHITELIST
            
        # Check for shell operators which indicate a complex command
        shell_operators = ['|', '>', '<', '>>', '<<', '&&', '||', ';']
        if any(operator in command_string for operator in shell_operators):
            return CommandSafetyLevel.REQUIRES_SHELL_TRUE
            
        return CommandSafetyLevel.SAFE
        
    # Alias the older method to use the new one for backwards compatibility
    def check_command_safety_level(self, command_string):
        """
        Legacy method that returns the string representation of the safety level.
        Returns:
            str: 'SAFE', 'NOT_IN_WHITELIST', 'POTENTIALLY_DANGEROUS', 'REQUIRES_SHELL_TRUE_ASSESSMENT', or 'EMPTY'.
        """
        safety_level = self.assess_command_safety(command_string)
        
        # Map the enum value to the old string format
        if safety_level == CommandSafetyLevel.REQUIRES_SHELL_TRUE:
            return 'REQUIRES_SHELL_TRUE_ASSESSMENT'  # Match the old naming
        
        return safety_level.value

    def get_usb_devices(self):
        """
        Get a list of available USB devices.
        
        Returns:
            str: Formatted string with device information
        """
        return self.usb_detector.get_usb_devices()
        
    def get_browser_content(self, browser_name=None):
        """
        Get content from browser tabs (titles and URLs).
        
        Args:
            browser_name (str, optional): Specific browser to target
                                         ("chrome", "firefox", "safari", "edge")
        
        Returns:
            str: Formatted browser content or error message
        """
        return self.browser_handler.get_browser_content(browser_name)
    
    def find_folders(self, folder_name, location="~", max_results=20, include_cloud=True):
        """
        Find folders matching a given name pattern.
        
        Args:
            folder_name (str): Name pattern to search for
            location (str): Root directory to start the search
            max_results (int): Maximum number of results to return
            include_cloud (bool): Whether to include cloud storage folders
            
        Returns:
            str: Formatted search results
        """
        return self.file_search.find_folders(folder_name, location, max_results)
    
    def find_files(self, file_pattern, location="~", max_results=20):
        """
        Find files matching a given pattern.
        
        This method uses the FileSearch class to find files, providing a safer
        and more reliable way to search compared to shell commands.
        
        Args:
            file_pattern (str): Pattern to search for (e.g. "*.txt")
            location (str): Root directory to start the search
            max_results (int): Maximum number of results to return
            
        Returns:
            str: Formatted search results
        """
        return self.file_search.find_files(file_pattern, location, max_results)
    
    def get_current_directory(self):
        """Get the current working directory in a user-friendly format."""
        try:
            # Get the current directory
            if self.system_platform == 'windows':
                command = 'cd'
            else:
                command = 'pwd'
                
            cwd = self.execute_command(command).strip()
            home_path = os.path.expanduser('~')
            
            # Format the path to show ~ for home directory
            if cwd.startswith(home_path):
                cwd = cwd.replace(home_path, '~', 1)
                
            return f"📁 Current directory: {cwd}"
        except Exception as e:
            return f"❌ Error getting current directory: {str(e)}"
        
    def handle_directory_query(self, query):
        """Handle various forms of directory-related queries."""
        query_lower = query.lower()
        
        # Handle different types of directory queries
        if any(term in query_lower for term in ['where am i', 'current directory', 'pwd', 'active folder', 'current folder']):
            return self.get_current_directory()
            
        # List files in current directory
        elif any(term in query_lower for term in ['show files', 'list files', 'what files', 'files in current']):
            command = 'ls -la' if self.system_platform != 'windows' else 'dir'
            result = self.execute_command(command)
            return f"📋 Files in current directory:\n{result}"
            
        # General directory operations
        else:
            return self.get_current_directory()
