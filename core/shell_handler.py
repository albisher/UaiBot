# core/shell_handler.py
import subprocess
import shlex
import os # Added import

# Basic list of commands that are generally safe. This should be expanded.
# For a more robust solution, consider external configuration or more sophisticated checks.
SAFE_COMMAND_WHITELIST = [
    'ls', 'cd', 'pwd', 'echo', 'cat', 'mkdir', 'rmdir', 'cp', 'mv', 'find', 'grep',
    'python', 'python3', 'pip', 'git', 'man', 'uname', 'df', 'du', 'free', 'top', 'ps'
    # Add other commands considered safe for general use
]

# Commands that should always require confirmation or be blocked in certain modes.
POTENTIALLY_DANGEROUS_COMMANDS = [
    'rm', 'sudo', 'mkfs', 'shutdown', 'reboot', 'dd', 'fdisk', 'kill'
    # Add other commands that could be harmful if misused
]

class ShellHandler:
    def __init__(self, safe_mode=True, enable_dangerous_command_check=True):
        """
        Initializes the ShellHandler.
        Args:
            safe_mode (bool): If True, restricts execution to whitelisted commands and may require
                              confirmation for potentially dangerous ones (if not outright blocked).
            enable_dangerous_command_check (bool): If True, checks commands against POTENTIALLY_DANGEROUS_COMMANDS.
        """
        self.safe_mode = safe_mode
        self.enable_dangerous_command_check = enable_dangerous_command_check
        print(f"ShellHandler initialized. Safe mode: {self.safe_mode}, Dangerous command check: {self.enable_dangerous_command_check}")

    def _is_command_safe(self, command_parts):
        """Checks if the command is on the whitelist or considered generally safe."""
        if not command_parts:
            return False
        command_name = command_parts[0]

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

    def execute_command(self, command_string, force_shell=False, require_confirmation_for_shell=True):
        """
        Executes the given shell command string.
        Args:
            command_string (str): The command to execute.
            force_shell (bool): If True, forces the use of shell=True. Use with extreme caution.
            require_confirmation_for_shell (bool): If True and force_shell is True, asks for user confirmation.
        Returns:
            str: The stdout of the command, or an error message.
        """
        if not command_string.strip():
            return "Error: No command provided."

        print(f"Attempting to execute: {command_string}")

        try:
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
            else: # force_shell is True
                if require_confirmation_for_shell:
                    # This confirmation should ideally happen in the main loop or UI
                    # For now, we simulate it with a print and proceed if not in strict safe_mode.
                    print(f"Warning: Executing command '{command_string}' with shell=True.")
                    if self.safe_mode: # Stricter handling for safe_mode
                        # In a real app: confirm = input("This command uses shell=True. Are you sure? (yes/no): ")
                        # if confirm.lower() != 'yes': return "Execution cancelled."
                        return "Error: shell=True execution requires explicit override when safe_mode is active and no direct confirmation mechanism is implemented here."
                
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

    def check_command_safety_level(self, command_string):
        """
        Checks the safety level of a command string.
        Returns:
            str: 'SAFE', 'NOT_IN_WHITELIST', 'POTENTIALLY_DANGEROUS', or 'EMPTY'.
        """
        if not command_string.strip():
            return 'EMPTY'

        try:
            command_parts = shlex.split(command_string)
            if not command_parts:
                return 'EMPTY'
        except ValueError:
            # If shlex cannot split (e.g. unmatched quotes), consider it risky or handle as per policy
            # For now, let's treat it as potentially problematic, though not strictly 'dangerous' by list.
            # Depending on policy, this could be 'UNPARSABLE' or another category.
            # For simplicity here, if it's not parsable by shlex, it won't pass _is_command_safe if safe_mode is on.
            # And it's unlikely to match _is_potentially_dangerous in its raw string form.
            # Let's assume it will be handled by the execution part if it's complex.
            # A more robust way would be to have the AI return structured commands.
            # For now, if shlex fails, we can't reliably check its parts against whitelist/blacklist.
            # We'll assume it's not explicitly whitelisted if parsing fails.
            if self.safe_mode:
                 return 'NOT_IN_WHITELIST' # Or a new category like 'UNPARSABLE_REQUIRES_SHELL_TRUE'
            # If not in safe mode, it might be allowed via shell=True later, but it's not on a specific list.
            return 'REQUIRES_SHELL_TRUE_ASSESSMENT' # Indicates it might need shell=True

        if self.enable_dangerous_command_check and self._is_potentially_dangerous(command_parts):
            return 'POTENTIALLY_DANGEROUS'
        
        if self.safe_mode and not self._is_command_safe(command_parts):
            return 'NOT_IN_WHITELIST'
            
        return 'SAFE'

# Example usage (for testing - remove or comment out for production):
# if __name__ == '__main__':
#     # Test in safe mode (default)
#     safe_handler = ShellHandler(safe_mode=True)
#     print("--- Safe Mode Tests ---")
#     print(f"LS Output: {safe_handler.execute_command('ls -la')}")
#     print(f"Echo Output: {safe_handler.execute_command('echo Hello World')}")
#     print(f"Dangerous RM Output: {safe_handler.execute_command('rm -rf /')}") # Should be blocked or warned
#     print(f"Sudo Command Output: {safe_handler.execute_command('sudo apt update')}") # Should be blocked or warned
#     print(f"Unknown Command: {safe_handler.execute_command('someunknowncommand')}")
#     print(f"Shell True (blocked in safe): {safe_handler.execute_command('echo $HOME', force_shell=True)}") 

#     # Test in less safe mode (but still with dangerous command checks)
#     less_safe_handler = ShellHandler(safe_mode=False, enable_dangerous_command_check=True)
#     print("\n--- Less Safe Mode (Dangerous Command Check Enabled) ---")
#     print(f"LS Output: {less_safe_handler.execute_command('ls -la')}")
#     print(f"Dangerous RM (Warning, not blocked if safe_mode=False): {less_safe_handler.execute_command('rm -rf /tmp/testfile')}") # Should warn
#     print(f"Sudo Command (Warning): {less_safe_handler.execute_command('sudo echo test')}")
#     print(f"Shell True (Confirmation would be needed): {less_safe_handler.execute_command('echo $HOME', force_shell=True)}")

#     # Test with dangerous command checks disabled (NOT RECOMMENDED for AI interaction)
#     unsafe_handler = ShellHandler(safe_mode=False, enable_dangerous_command_check=False)
#     print("\n--- Unsafe Mode (Dangerous Command Check Disabled) ---")
#     # This would execute if the command was valid and permissions allowed, without specific blocking here.
#     # print(f"Dangerous RM (No check): {unsafe_handler.execute_command('echo Simulating rm -rf /')}") 
#     print(f"Shell True (No check): {unsafe_handler.execute_command('echo $HOME', force_shell=True)}")
