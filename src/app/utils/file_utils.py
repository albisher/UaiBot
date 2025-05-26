"""
File utility functions for Labeeb.
Provides file search capabilities with proper path expansion and cross-platform compatibility.
"""
import os
import subprocess
import logging
import shlex
import platform
import glob
from pathlib import Path
import fnmatch  # Make sure fnmatch is properly imported

logger = logging.getLogger(__name__)

class FileUtils:
    @staticmethod
    def expand_path(path_str):
        """
        Expand user home directory and environment variables in a path string.
        
        Args:
            path_str (str): Path string potentially containing ~ or environment variables
            
        Returns:
            str: Expanded path
        """
        if not path_str:
            return os.path.expanduser("~")
            
        # First expand user directory (~ or ~user)
        expanded = os.path.expanduser(path_str)
        # Then expand any environment variables
        expanded = os.path.expandvars(expanded)
        return expanded

    @staticmethod
    def search_files(search_term, search_path=None, name_pattern=None, file_type=None, limit=15):
        """
        Search for files matching criteria using Python's os module.
        This is more reliable and cross-platform than using the find command.
        
        Args:
            search_term (str): Term to search for in filenames
            search_path (str): Base path to search in (default: home directory)
            name_pattern (str): Filename pattern to match (e.g., "*.pdf")
            file_type (str): Type of file to search for
            limit (int): Maximum number of results to return
            
        Returns:
            tuple: (list of matching files, error message or None)
        """
        # Expand path to handle ~ and environment variables
        if not search_path:
            search_path = "~"
        
        expanded_path = FileUtils.expand_path(search_path)
        
        if not os.path.exists(expanded_path):
            return [], f"Search path does not exist: {expanded_path}"
        
        # Create search pattern    
        if not search_term and not name_pattern and not file_type:
            return [], "No search criteria provided"
        
        # Prepare search results
        results = []
        seen_files = set()  # Track seen files to prevent duplicates
        
        try:
            # Walk through directory structure
            for root, dirs, files in os.walk(expanded_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for filename in files:
                    # Skip hidden files
                    if filename.startswith('.'):
                        continue
                        
                    # Check if file matches search criteria
                    file_path = os.path.join(root, filename)
                    
                    # Skip if we've already processed this file
                    if file_path in seen_files:
                        continue
                    seen_files.add(file_path)
                    
                    match = True
                    
                    # Apply name pattern filter if specified
                    if name_pattern:
                        if not fnmatch.fnmatch(filename, name_pattern):
                            match = False
                    
                    # Apply file type filter if specified
                    if file_type and match:
                        ext = os.path.splitext(filename)[1].lower()
                        if not ext.endswith(file_type.lower()):
                            match = False
                    
                    # Apply search term filter if specified - make this more robust
                    if search_term and match:
                        # If search_term has wildcards, use fnmatch pattern matching
                        if '*' in search_term or '?' in search_term:
                            if not fnmatch.fnmatch(filename.lower(), search_term.lower()):
                                match = False
                        # Otherwise use simple substring search
                        elif search_term.lower() not in filename.lower():
                            match = False
                    
                    if match:
                        results.append(file_path)
                        
                    # Check limit
                    if limit and len(results) >= limit:
                        return results[:limit], None
            
            return results, None
            
        except Exception as e:
            logger.error(f"Error during file search: {str(e)}")
            return [], str(e)

    @staticmethod
    def find_cv_files(search_path=None):
        """
        Specialized function to find CV or resume files.
        
        Args:
            search_path (str): Path to search in (default: home directory)
            
        Returns:
            tuple: (list of matching files, error message or None)
        """
        # Common CV-related terms
        cv_terms = ["cv", "resume", "curriculum", "vitae"]
        # Common document formats for CVs
        cv_extensions = [".pdf", ".doc", ".docx", ".txt", ".rtf"]
        
        results = []
        seen_files = set()  # Track seen files to prevent duplicates
        
        # Search for each combination of term and extension
        for term in cv_terms:
            for ext in cv_extensions:
                files, _ = FileUtils.search_files(term, search_path, f"*{ext}")
                for file in files:
                    if file not in seen_files:
                        seen_files.add(file)
                        results.append(file)
        
        return results, None

# For backward compatibility, expose the functions directly
expand_path = FileUtils.expand_path
search_files = FileUtils.search_files
find_cv_files = FileUtils.find_cv_files
