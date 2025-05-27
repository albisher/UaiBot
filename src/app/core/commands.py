"""
Command handlers for Labeeb.
These functions process user commands and return formatted responses.
"""
import os
import re
import logging
from .file_utils import search_files, find_cv_files, expand_path

logger = logging.getLogger(__name__)

def handle_file_search(query, search_path=None, file_type=None):
    """
    Handle file search requests.
    
    Args:
        query (str): Search term
        search_path (str): Path to search in (default: home directory)
        file_type (str): Optional file type filter (e.g., "pdf")
        
    Returns:
        str: Formatted response
    """
    logger.info(f"Searching for files matching '{query}'")
    
    # Format file type pattern if provided
    name_pattern = None
    if file_type:
        if not file_type.startswith('.'):
            file_type = f".{file_type}"
        name_pattern = f"*{file_type}"
    
    # Search for files
    results, error = search_files(query, search_path, name_pattern=name_pattern)
    
    # Handle errors
    if error:
        logger.error(f"❌ Error searching for files: {error}")
        return f"❌ Error searching for files: {error}"
    
    # Format response
    if not results:
        return f"No files found matching '{query}'"
    
    # Build response
    path_desc = "current directory" if search_path in (None, ".", "./") else f"'{expand_path(search_path)}'"
    output = f"🔍 Found {len(results)} files matching '{query}' in {path_desc}:\n\n"
    
    for i, path in enumerate(results, 1):
        output += f"{i}. {path}\n"
    
    return output

def handle_cv_search(search_path=None):
    """
    Special handler for searching CV/resume files.
    
    Args:
        search_path (str): Path to search in (default: home directory)
        
    Returns:
        str: Formatted response
    """
    logger.info("Searching for CV/resume files")
    
    # Use specialized CV search function
    results, error = find_cv_files(search_path)
    
    # Handle errors
    if error:
        logger.error(f"❌ Error searching for CV files: {error}")
        return f"❌ Error searching for CV files: {error}"
    
    # Format response
    if not results:
        path_desc = "home directory" if not search_path else f"'{expand_path(search_path)}'"
        return f"No CV files found in {path_desc}"
    
    path_desc = "home directory" if not search_path else f"'{expand_path(search_path)}'"
    output = f"📄 Found {len(results)} CV/resume files in {path_desc}:\n\n"
    
    for i, path in enumerate(results, 1):
        output += f"{i}. {path}\n"
    
    return output
