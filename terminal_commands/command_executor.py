"""
Command executor for UaiBot terminal commands.
"""
import subprocess
import platform
from .output_processor import OutputProcessor
from core.utils import run_command

class CommandExecutor:
    """Executes terminal commands and processes their output."""
    
    def __init__(self, shell_handler, command_registry):
        self.shell_handler = shell_handler
        self.command_registry = command_registry
        self.output_processor = OutputProcessor()
    
    def execute_system_command(self, command_type, **params):
        """Execute a system command and return processed results."""
        try:
            # Get the platform-specific command
            command = self.command_registry.get_command(command_type, **params)
            
            # Execute the command using shell handler
            raw_output = self.shell_handler.execute_command(command, force_shell=True)
            
            # Process the output according to command type
            if command_type == "uptime":
                return self.output_processor.process_uptime(raw_output)
            elif command_type == "memory":
                return self.output_processor.process_memory(raw_output)
            elif command_type == "disk_space":
                return self.output_processor.process_disk_space(raw_output)
            elif command_type in ["notes_topics", "notes_folders"]:
                return self.output_processor.process_notes_topics(raw_output)
            elif command_type == "notes_count":
                return self.output_processor.process_notes_count(raw_output)
            elif command_type == "notes_list":
                return self.output_processor.process_notes_list(raw_output)
            elif command_type == "find_folders":
                return self.output_processor.process_folder_search(raw_output, params.get("search_term", ""))
            
            return raw_output
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    def execute_direct_command(self, command, **kwargs):
        """
        Execute a command directly using the run_command utility function.
        
        This provides a more flexible way to execute commands with various options
        like output capturing, async execution, etc.
        
        Args:
            command (str or list): The command to execute
            **kwargs: Additional parameters to pass to run_command:
                - capture_output (bool): Whether to capture stdout/stderr
                - text (bool): If True, decode output as text
                - shell (bool): If True, execute through shell
                - timeout (int): Maximum time to wait for completion
                - check (bool): If True, raise exception on non-zero exit
                - env (dict): Environment variables for subprocess
                - cwd (str): Directory to change to before executing
                - input (str): Input to pass to stdin
                - async_mode (bool): If True, return Popen object for async execution
                
        Returns:
            dict: Result containing returncode, stdout, stderr, and success flag
            or subprocess.Popen object if async_mode is True
        """
        try:
            # Process command to inject platform-specific adjustments if needed
            if isinstance(command, str) and command.startswith('${'):
                # This appears to be a command template, try to resolve it
                command_type = command.strip('${}')
                command = self.command_registry.get_command(command_type, **kwargs)
                
            # Forward to the run_command utility
            result = run_command(command, **kwargs)
            return result
        except Exception as e:
            return {
                'returncode': -1,
                'success': False,
                'stdout': None,
                'stderr': f"Error executing command: {str(e)}",
                'exception': e
            }
