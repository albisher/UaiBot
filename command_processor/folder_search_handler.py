"""
Folder search handler module for UaiBot.

This module provides a handler for folder search queries, using the FileSearch
class to perform efficient and reliable folder searches.

Features:
- Folder search query processing
- Integration with FileSearch for reliable searching
- Support for cloud storage and notes applications
- Configurable search parameters

Example:
    >>> handler = FolderSearchHandler(quiet_mode=False)
    >>> result = handler.handle_folder_search("find folders named Documents")
"""
import logging
from typing import Optional
from core.file_search import FileSearch

# Set up logging
logger = logging.getLogger(__name__)

class FolderSearchHandler:
    """
    A class to handle folder search queries.
    
    This class processes folder search queries and uses the FileSearch class
    to perform efficient and reliable folder searches.
    
    Attributes:
        quiet_mode (bool): If True, reduces terminal output
        file_search (FileSearch): Instance of FileSearch for folder operations
    """
    
    def __init__(self, quiet_mode: bool = False) -> None:
        """
        Initialize the FolderSearchHandler class.
        
        Args:
            quiet_mode (bool): If True, reduces terminal output
        """
        self.quiet_mode = quiet_mode
        self.file_search = FileSearch(quiet_mode=quiet_mode)
    
    def handle_folder_search(self, query: str) -> str:
        """
        Handle a folder search query.
        
        This method processes the query to extract search parameters and
        uses the FileSearch class to perform the search.
        
        Args:
            query (str): The search query to process
            
        Returns:
            str: Formatted search results
        """
        try:
            # Extract search parameters from query
            folder_name, location, max_results = self._parse_query(query)
            
            # Perform the search using FileSearch
            return self.file_search.find_folders(folder_name, location, max_results)
            
        except Exception as e:
            error_msg = f"Error processing folder search: {str(e)}"
            if not self.quiet_mode:
                logger.error(error_msg)
            return error_msg
    
    def _parse_query(self, query: str) -> tuple[str, str, int]:
        """
        Parse a folder search query to extract search parameters.
        
        Args:
            query (str): The search query to parse
            
        Returns:
            tuple[str, str, int]: Tuple containing (folder_name, location, max_results)
        """
        # Default values
        folder_name = ""
        location = "~"
        max_results = 20
        
        # Extract folder name
        if "named" in query:
            parts = query.split("named", 1)
            if len(parts) > 1:
                folder_name = parts[1].strip()
        elif "containing" in query:
            parts = query.split("containing", 1)
            if len(parts) > 1:
                folder_name = parts[1].strip()
        else:
            # Try to extract folder name from common patterns
            import re
            patterns = [
                r"find folders? (?:named|containing|with) ['\"](.+?)['\"]",
                r"search for folders? (?:named|containing|with) ['\"](.+?)['\"]",
                r"look for folders? (?:named|containing|with) ['\"](.+?)['\"]"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    folder_name = match.group(1)
                    break
        
        # Extract location if specified
        if "in" in query:
            parts = query.split("in", 1)
            if len(parts) > 1:
                location = parts[1].strip()
        
        # Extract max results if specified
        if "limit" in query or "max" in query:
            import re
            match = re.search(r"(?:limit|max)(?:\s+results?)?\s+(\d+)", query, re.IGNORECASE)
            if match:
                max_results = int(match.group(1))
        
        return folder_name, location, max_results 