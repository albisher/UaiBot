"""
Folder search handling module for UaiBot.
Handles searching for files and folders.
"""
import re
import logging
from typing import Tuple, Optional

# Set up logging
logger = logging.getLogger(__name__)

class FolderSearchHandler:
    def __init__(self, shell_handler, quiet_mode: bool = False):
        """
        Initialize the FolderSearchHandler.
        
        Args:
            shell_handler: Shell handler instance for executing commands
            quiet_mode (bool): If True, reduces terminal output
        """
        self.shell_handler = shell_handler
        self.quiet_mode = quiet_mode
    
    def handle_folder_search(self, query: str) -> Tuple[bool, str]:
        """
        Handle folder search queries.
        
        Args:
            query (str): The search query
            
        Returns:
            tuple: (bool, str) - (True, result) if handled, (False, "") otherwise
        """
        query_lower = query.lower()
        
        # Special case for Apple Notes
        if "notes" in query_lower and ("folder" in query_lower or 
                                      "app" in query_lower or
                                      "show me" in query_lower or
                                      "where" in query_lower):
            return True, self.shell_handler.find_folders("Notes", location="~", include_cloud=True)
        
        # Check if this is a file/folder search request
        if "find" in query_lower or "search" in query_lower:
            # Extract search term if any
            search_terms = ["file", "folder", "directory"]
            for term in search_terms:
                if term in query_lower:
                    pattern = rf"(?:find|search)(?:\s+for)?\s+(?:a|the)?\s+{term}(?:s)?\s+(?:named|called)?\s+['\"]*([a-zA-Z0-9_\-\.\s]+)['\"\s]*"
                    match = re.search(pattern, query_lower)
                    if match:
                        search_name = match.group(1).strip()
                        if term in ["folder", "directory"]:
                            return True, self.shell_handler.find_folders(search_name)
                        else:
                            # Use find with both files and directories for generic file search
                            return True, self._try_direct_execution(f'find ~ -name "*{search_name}*" -type f 2>/dev/null | head -n 20')
        
        return False, ""
    
    def _try_direct_execution(self, command: str) -> str:
        """
        Try to execute a command directly.
        
        Args:
            command (str): The command to execute
            
        Returns:
            str: Command output or error message
        """
        try:
            return self.shell_handler.execute_command(command)
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return f"Error executing command: {str(e)}"
    
    def log(self, message: str) -> None:
        """Print a message if not in quiet mode"""
        if not self.quiet_mode:
            print(message) 