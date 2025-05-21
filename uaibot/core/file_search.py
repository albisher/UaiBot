"""
File search module for UaiBot.

This module provides centralized file and folder searching functionality,
combining the best features from various implementations across the codebase.
It supports both native Python-based searching and platform-specific optimizations.

Features:
- File and folder searching with pattern matching
- Platform-specific optimizations (macOS, Windows, Linux)
- Special handling for cloud storage and notes applications
- Configurable search depth and result limits
- Support for wildcards and file extensions
- Cross-platform compatibility

Example:
    >>> file_search = FileSearch(quiet_mode=False)
    >>> results = file_search.find_folders("Documents", location="~")
    >>> files = file_search.find_files("*.txt", location="~/Downloads")
"""
import os
import re
import fnmatch
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

class FileSearch:
    """
    A class to handle file and folder searching operations.
    
    This class provides a unified interface for searching files and folders,
    combining the best features from various implementations across the codebase.
    It supports both native Python-based searching and platform-specific optimizations.
    
    Attributes:
        quiet_mode (bool): If True, reduces terminal output
        fast_mode (bool): If True, uses faster but less thorough search methods
        system_platform (str): The current operating system platform
    """
    
    def __init__(self, quiet_mode: bool = False, fast_mode: bool = False) -> None:
        """
        Initialize the FileSearch class.
        
        Args:
            quiet_mode (bool): If True, reduces terminal output
            fast_mode (bool): If True, uses faster but less thorough search methods
        """
        self.quiet_mode = quiet_mode
        self.fast_mode = fast_mode
        self.system_platform = self._get_platform()
    
    def _get_platform(self) -> str:
        """
        Get the current operating system platform.
        
        Returns:
            str: Platform name ('darwin', 'windows', or 'linux')
        """
        import platform
        return platform.system().lower()
    
    def find_folders(self, folder_name: str, location: str = "~", max_results: int = 20, 
                    include_cloud: bool = True) -> str:
        """
        Find folders matching a given name pattern.
        
        This method combines the best features from various implementations:
        - Native Python-based searching for reliability
        - Platform-specific optimizations
        - Special handling for cloud storage and notes applications
        - Configurable search depth and result limits
        
        Args:
            folder_name (str): Name pattern to search for
            location (str): Root directory to start the search
            max_results (int): Maximum number of results to return
            include_cloud (bool): Whether to include cloud storage folders
            
        Returns:
            str: Formatted search results with emojis and clear organization
        """
        # Sanitize inputs
        folder_name = folder_name.replace('"', '\\"').replace("'", "\\'")
        location = os.path.expanduser(location)
        
        try:
            # Prepare results containers
            all_folders: List[str] = []
            cloud_folders: List[Dict[str, str]] = []
            
            # First check for platform-specific notes folders
            if include_cloud and folder_name.lower() in ["notes", "note", "notes app"]:
                self._get_notes_folders(cloud_folders)
            
            # Use Python's native file system functions for safer, more controlled folder search
            self._find_folders_natively(folder_name, location, max_results, all_folders)
            
            # Format the output with emojis
            if not all_folders and not cloud_folders:
                return f"I searched for '{folder_name}' folders but didn't find any matching folders in {location}."
            
            formatted_result = f"I found these folders matching '{folder_name}':\n\n"
            
            # First show cloud folders (if any)
            if cloud_folders:
                if self.system_platform == "darwin":
                    formatted_result += "🌥️  iCloud/macOS:\n\n"
                elif self.system_platform == "windows":
                    formatted_result += "📝  Note Applications:\n\n"
                else:
                    formatted_result += "📝  Notes:\n\n"
                
                # Show all folders with type and count
                for cf in cloud_folders:
                    formatted_result += f"  • {cf['name']}    {cf['items']}\n"
                
                formatted_result += "\n"
            
            # Then show filesystem folders
            if all_folders:
                formatted_result += "💻 Local Filesystem:\n\n"
                for folder in all_folders:
                    formatted_result += f"  • {folder}\n"
                
                if len(all_folders) >= max_results:
                    formatted_result += f"\n⚠️  Showing first {max_results} results. To see more, specify a narrower search."
            
            return formatted_result
            
        except Exception as e:
            error_msg = f"Error searching for folders: {str(e)}"
            if not self.quiet_mode:
                logger.error(error_msg)
            return error_msg
    
    def _get_notes_folders(self, cloud_folders: List[Dict[str, str]]) -> None:
        """
        Get platform-specific notes folders.
        
        This method handles special cases for notes applications on different platforms:
        - macOS: iCloud Notes and local Notes app
        - Windows: OneNote and Sticky Notes
        - Linux: GNOME Notes and other note-taking applications
        
        Args:
            cloud_folders (List[Dict[str, str]]): List to populate with found note folders
        """
        if self.system_platform == "darwin":
            # Try to find iCloud Notes folders
            icloud_path = os.path.expanduser("~/Library/Mobile Documents/com~apple~Notes")
            if os.path.exists(icloud_path):
                try:
                    # Count total notes in root
                    notes_count = 0
                    for root, dirs, files in os.walk(icloud_path):
                        if root == icloud_path:
                            for file in files:
                                if file.endswith('.icloud') or file.endswith('.notesdata'):
                                    notes_count += 1
                    
                    cloud_folders.append({
                        "name": "Notes",
                        "path": "iCloud/Notes",
                        "type": "iCloud",
                        "items": str(notes_count)
                    })
                    
                    # Check for actual iCloud folders
                    notes_dirs = os.path.join(icloud_path, "Notes")
                    if os.path.exists(notes_dirs):
                        try:
                            for item in os.listdir(notes_dirs):
                                subfolder_path = os.path.join(notes_dirs, item)
                                if os.path.isdir(subfolder_path):
                                    items_count = 0
                                    for root, dirs, files in os.walk(subfolder_path):
                                        items_count += len(files)
                                    
                                    cloud_folders.append({
                                        "name": item,
                                        "path": f"iCloud/Notes/{item}",
                                        "type": "iCloud",
                                        "items": str(items_count)
                                    })
                        except Exception as e:
                            if not self.quiet_mode:
                                logger.error(f"Error scanning Notes subfolders: {e}")
                except Exception as e:
                    if not self.quiet_mode:
                        logger.error(f"Error scanning iCloud Notes folders: {e}")
                    cloud_folders.append({
                        "name": "Notes",
                        "path": "iCloud/Notes",
                        "type": "iCloud",
                        "items": "Unknown"
                    })
            
            # Check for local Notes container
            local_notes = os.path.expanduser("~/Library/Containers/com.apple.Notes")
            if os.path.exists(local_notes):
                cloud_folders.append({
                    "name": "Notes App",
                    "path": "Notes App (Local)",
                    "type": "Local",
                    "items": "Notes App Data"
                })
        
        elif self.system_platform == "windows":
            # Try to identify common Windows Notes locations
            note_locations = [
                os.path.expanduser("~/Documents/OneNote Notebooks"),
                os.path.expanduser("~/OneDrive/Documents/OneNote Notebooks"),
                "C:/Program Files (x86)/Microsoft Office/Office16/ONENOTE.EXE",
                "C:/Program Files/Microsoft Office/Office16/ONENOTE.EXE",
                os.path.expanduser("~/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe")
            ]
            
            for note_path in note_locations:
                if os.path.exists(note_path):
                    if "OneNote" in note_path:
                        cloud_folders.append({
                            "name": "OneNote Notebooks",
                            "path": note_path,
                            "type": "Microsoft",
                            "items": "OneNote"
                        })
                    elif "StickyNotes" in note_path:
                        cloud_folders.append({
                            "name": "Sticky Notes",
                            "path": note_path,
                            "type": "Microsoft",
                            "items": "Sticky Notes"
                        })
                    elif "ONENOTE.EXE" in note_path:
                        cloud_folders.append({
                            "name": "OneNote Application",
                            "path": note_path,
                            "type": "Microsoft",
                            "items": "OneNote App"
                        })
        
        elif self.system_platform == "linux":
            # Check for GNOME Notes (Bijiben) and other note-taking apps
            note_locations = [
                os.path.expanduser("~/.local/share/bijiben"),
                "/usr/bin/bijiben",
                os.path.expanduser("~/.var/app/org.gnome.Notes"),
                os.path.expanduser("~/.config/joplin-desktop")
            ]
            
            for note_path in note_locations:
                if os.path.exists(note_path):
                    note_type = "Joplin" if "joplin" in note_path.lower() else "GNOME Notes"
                    cloud_folders.append({
                        "name": note_type,
                        "path": note_path,
                        "type": "Linux",
                        "items": "Notes App"
                    })
    
    def _find_folders_natively(self, folder_name: str, location: str, max_results: int, 
                              result_list: List[str]) -> None:
        """
        Find folders using Python's native file system functions.
        
        This method provides a safer, more reliable, and cross-platform way to search
        for folders compared to shell commands.
        
        Args:
            folder_name (str): Pattern to search for in folder names
            location (str): Root directory to search in
            max_results (int): Maximum number of results to return
            result_list (List[str]): List to populate with found folders
        """
        # Convert pattern to lowercase for case-insensitive matching
        folder_pattern = folder_name.lower()
        
        # Handle wildcard cases specially
        is_wildcard = folder_pattern in ["*", "**"]
        
        # Determine search depth based on mode and pattern
        max_depth = 2 if (is_wildcard or self.fast_mode) else 4
        
        # Keep track of results count
        count = 0
        
        # If searching in home, focus on common directories first
        if location == os.path.expanduser("~"):
            common_dirs = ['Documents', 'Downloads', 'Desktop', 'Pictures', 'Music', 'Videos']
            for common_dir in common_dirs:
                common_path = os.path.join(location, common_dir)
                if os.path.exists(common_path) and count < max_results:
                    self._search_directory(common_path, folder_pattern, max_depth, 1, 
                                         result_list, max_results, is_wildcard)
                    count = len(result_list)
        
        # If we need more results, perform general search
        if count < max_results:
            self._search_directory(location, folder_pattern, max_depth, 0, 
                                 result_list, max_results, is_wildcard)
    
    def _search_directory(self, root_dir: str, pattern: str, max_depth: int, 
                         current_depth: int, result_list: List[str], max_results: int, 
                         is_wildcard: bool = False) -> None:
        """
        Recursively search a directory for folders matching a pattern.
        
        Args:
            root_dir (str): Directory to search in
            pattern (str): Pattern to match folder names against
            max_depth (int): Maximum recursion depth
            current_depth (int): Current recursion depth
            result_list (List[str]): List to populate with results
            max_results (int): Maximum number of results
            is_wildcard (bool): Whether this is a wildcard search
        """
        # Stop if we have enough results or reached max depth
        if len(result_list) >= max_results or current_depth > max_depth:
            return
        
        try:
            # List all entries in the directory
            entries = os.listdir(root_dir)
            
            # Process all directories first (breadth-first approach)
            for entry in entries:
                # Skip hidden entries
                if entry.startswith('.'):
                    continue
                
                full_path = os.path.join(root_dir, entry)
                
                # Only process directories
                if os.path.isdir(full_path):
                    # For wildcard searches, add all directories
                    # For specific searches, check if pattern is in the name
                    if is_wildcard or pattern in entry.lower():
                        result_list.append(full_path)
                        if len(result_list) >= max_results:
                            return
            
            # Then recurse into subdirectories if we haven't reached max depth
            if current_depth < max_depth:
                for entry in entries:
                    if entry.startswith('.'):
                        continue
                    
                    full_path = os.path.join(root_dir, entry)
                    if os.path.isdir(full_path):
                        self._search_directory(full_path, pattern, max_depth,
                                             current_depth + 1, result_list,
                                             max_results, is_wildcard)
                        if len(result_list) >= max_results:
                            return
        except (PermissionError, FileNotFoundError) as e:
            # Skip directories we can't access
            pass
        except Exception as e:
            # Log unexpected errors but continue
            if not self.quiet_mode:
                logger.error(f"Error searching directory {root_dir}: {str(e)}")
    
    def find_files(self, file_pattern: str, location: str = "~", max_results: int = 20) -> str:
        """
        Find files matching a given pattern using Python's native file system functions.
        
        This method provides a safer, more reliable, and cross-platform way to search
        for files compared to shell commands.
        
        Args:
            file_pattern (str): Pattern to search for (e.g. "*.txt", "enha*.txt")
            location (str): Root directory to start the search
            max_results (int): Maximum number of results to return
            
        Returns:
            str: Formatted search results with emojis and clear organization
        """
        # Sanitize and expand user path
        location = os.path.expanduser(location)
        
        # Check if location exists
        if not os.path.exists(location):
            return f"Error: The specified location '{location}' does not exist."
        
        try:
            # Prepare results container
            matching_files: List[str] = []
            
            # Extract extension from pattern for better targeting
            is_extension_search = False
            target_extension = None
            
            # Check if this is a file extension search (*.ext pattern)
            if file_pattern.startswith('*.'):
                target_extension = file_pattern[2:].lower()
                is_extension_search = True
            
            # Create regex pattern from glob pattern
            if '*' in file_pattern or '?' in file_pattern:
                regex_pattern = fnmatch.translate(file_pattern)
                pattern_obj = re.compile(regex_pattern, re.IGNORECASE)
            else:
                # If no wildcards, do a simple substring search
                pattern_obj = None
            
            # Determine search depth based on mode
            max_depth = 3 if self.fast_mode else 5
            
            # First, search in common document locations
            common_paths = []
            home = os.path.expanduser('~')
            
            for common_dir in ['Documents', 'Downloads', 'Desktop']:
                path = os.path.join(home, common_dir)
                if os.path.exists(path):
                    common_paths.append(path)
            
            # If location is not home or a custom path, add it to common paths
            if location != home and location not in common_paths:
                common_paths.insert(0, location)
            
            # Search in all designated locations
            for path in common_paths:
                self._search_files_directory(path, file_pattern, pattern_obj,
                                           matching_files, max_results, 0, max_depth,
                                           target_extension=target_extension)
                # Stop if we've found enough files
                if len(matching_files) >= max_results:
                    break
            
            # If we haven't found enough results and location wasn't in common paths,
            # search the specified location (to be thorough)
            if len(matching_files) < max_results and location not in common_paths:
                self._search_files_directory(location, file_pattern, pattern_obj,
                                           matching_files, max_results, 0, max_depth,
                                           target_extension=target_extension)
            
            # Format the results
            if not matching_files:
                return f"No files matching '{file_pattern}' were found in {location}."
            
            formatted_result = f"I found these files matching '{file_pattern}':\n\n"
            formatted_result += "💻 Local Filesystem:\n\n"
            
            for file_path in matching_files:
                # Get file size in human-readable format
                try:
                    size = os.path.getsize(file_path)
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.1f} KB"
                    else:
                        size_str = f"{size/(1024*1024):.1f} MB"
                except:
                    size_str = "unknown size"
                
                # Add file info to results
                formatted_result += f"  • {file_path} ({size_str})\n"
            
            if len(matching_files) >= max_results:
                formatted_result += f"\n⚠️  Showing first {max_results} results. To see more, specify a narrower search."
            
            return formatted_result
            
        except Exception as e:
            error_msg = f"Error searching for files: {str(e)}"
            if not self.quiet_mode:
                logger.error(error_msg)
            return error_msg
    
    def _search_files_directory(self, directory: str, file_pattern: str, pattern_obj: Optional[re.Pattern],
                               result_list: List[str], max_results: int, current_depth: int,
                               max_depth: int, target_extension: Optional[str] = None) -> None:
        """
        Recursively search a directory for files matching a pattern.
        
        Args:
            directory (str): Directory to search in
            file_pattern (str): Pattern to match file names against
            pattern_obj (Optional[re.Pattern]): Compiled regex pattern for matching
            result_list (List[str]): List to populate with results
            max_results (int): Maximum number of results
            current_depth (int): Current recursion depth
            max_depth (int): Maximum recursion depth
            target_extension (Optional[str]): Target file extension for optimization
        """
        # Stop if we have enough results or reached max depth
        if len(result_list) >= max_results or current_depth > max_depth:
            return
        
        try:
            # List all entries in the directory
            entries = os.listdir(directory)
            
            # Process all files first
            for entry in entries:
                # Skip hidden files
                if entry.startswith('.'):
                    continue
                
                full_path = os.path.join(directory, entry)
                
                # Process regular files
                if os.path.isfile(full_path):
                    # Fast path: if target_extension is specified, check extension first
                    if target_extension:
                        _, ext = os.path.splitext(entry)
                        if ext.lower() != f'.{target_extension}' and ext.lower() != target_extension:
                            continue
                    
                    # Match against the pattern
                    if pattern_obj:
                        # Use regex pattern for wildcard matching
                        if pattern_obj.match(entry):
                            result_list.append(full_path)
                            if len(result_list) >= max_results:
                                return
                    else:
                        # Use simple substring matching
                        if file_pattern.lower() in entry.lower():
                            result_list.append(full_path)
                            if len(result_list) >= max_results:
                                return
            
            # Then recurse into subdirectories if we haven't reached max depth
            if current_depth < max_depth:
                for entry in entries:
                    if entry.startswith('.'):
                        continue
                    
                    full_path = os.path.join(directory, entry)
                    if os.path.isdir(full_path):
                        self._search_files_directory(full_path, file_pattern, pattern_obj,
                                                   result_list, max_results,
                                                   current_depth + 1, max_depth,
                                                   target_extension=target_extension)
                        if len(result_list) >= max_results:
                            return
        except (PermissionError, FileNotFoundError) as e:
            # Skip directories we can't access
            pass
        except Exception as e:
            # Log unexpected errors but continue
            if not self.quiet_mode:
                logger.error(f"Error searching directory {directory}: {str(e)}") 