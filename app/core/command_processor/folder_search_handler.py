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
from typing import Optional, Tuple
from app.core.file_search import FileSearch

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
    
    def _parse_query(self, query: str) -> Tuple[str, str, int]:
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
        
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        # Extract folder name using keyword-based approach
        folder_keywords = ["named", "containing", "with"]
        for keyword in folder_keywords:
            if keyword in query_lower:
                parts = query.split(keyword, 1)
                if len(parts) > 1:
                    # Extract text between quotes if present
                    text = parts[1].strip()
                    if text.startswith(("'", '"')) and text.endswith(("'", '"')):
                        folder_name = text[1:-1]
                    else:
                        # If no quotes, take the first word
                        folder_name = text.split()[0]
                    break
        
        # If no folder name found yet, try to extract from common patterns
        if not folder_name:
            search_verbs = ["find", "search for", "look for"]
            for verb in search_verbs:
                if verb in query_lower:
                    # Get the part after the verb
                    parts = query.split(verb, 1)
                    if len(parts) > 1:
                        # Look for text between quotes
                        text = parts[1].strip()
                        if text.startswith(("'", '"')) and text.endswith(("'", '"')):
                            folder_name = text[1:-1]
                            break
        
        # Extract location if specified
        if "in" in query_lower:
            parts = query.split("in", 1)
            if len(parts) > 1:
                location = parts[1].strip()
        
        # Extract max results if specified
        if "limit" in query_lower or "max" in query_lower:
            # Find the number after "limit" or "max"
            words = query_lower.split()
            for i, word in enumerate(words):
                if word in ["limit", "max"] and i + 1 < len(words):
                    try:
                        max_results = int(words[i + 1])
                        break
                    except ValueError:
                        continue
        
        return folder_name, location, max_results 