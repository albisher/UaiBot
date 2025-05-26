"""
DEPRECATED: File search logic has been moved to platform_core/platform_manager.py.
Use PlatformManager for all file search logic.
"""

# Deprecated stub for backward compatibility
from platform_core.platform_manager import PlatformManager

"""
File search module for Labeeb.

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
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

from .platform_core import get_platform_name, get_file_path

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
        self.system_platform = get_platform_name()
    
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
        location = get_file_path(os.path.expanduser(location))
        
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
            icloud_path = get_file_path(os.path.expanduser("~/Library/Mobile Documents/com~apple~Notes"))
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
                    notes_dirs = get_file_path(os.path.join(icloud_path, "Notes"))
                    if os.path.exists(notes_dirs):
                        try:
                            for item in os.listdir(notes_dirs):
                                subfolder_path = get_file_path(os.path.join(notes_dirs, item))
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
            local_notes = get_file_path(os.path.expanduser("~/Library/Containers/com.apple.Notes"))
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
                get_file_path(os.path.expanduser("~/Documents/OneNote Notebooks")),
                get_file_path(os.path.expanduser("~/OneDrive/Documents/OneNote Notebooks")),
                get_file_path("C:/Program Files (x86)/Microsoft Office/Office16/ONENOTE.EXE"),
                get_file_path("C:/Program Files/Microsoft Office/Office16/ONENOTE.EXE"),
                get_file_path(os.path.expanduser("~/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe"))
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
                            "items": "OneNote"
                        })
        
        elif self.system_platform == "linux":
            # Try to identify common Linux Notes locations
            note_locations = [
                get_file_path(os.path.expanduser("~/.local/share/gnome-boxes")),
                get_file_path(os.path.expanduser("~/.local/share/notes")),
                get_file_path(os.path.expanduser("~/Documents/Notes"))
            ]
            
            for note_path in note_locations:
                if os.path.exists(note_path):
                    cloud_folders.append({
                        "name": os.path.basename(note_path),
                        "path": note_path,
                        "type": "Local",
                        "items": "Notes"
                    })
    
    def _find_folders_natively(self, folder_name: str, location: str, max_results: int, 
                              result_list: List[str]) -> None:
        """
        Find folders using native Python file system functions.
        
        Args:
            folder_name (str): Name pattern to search for
            location (str): Root directory to start the search
            max_results (int): Maximum number of results to return
            result_list (List[str]): List to populate with found folders
        """
        # Determine if we're using wildcards
        is_wildcard = '*' in folder_name or '?' in folder_name
        
        # Set search depth based on mode
        max_depth = 3 if self.fast_mode else 5
        
        # Start the search
        self._search_directory(
            location,
            folder_name,
            max_depth,
            0,
            result_list,
            max_results,
            is_wildcard
        )
    
    def _search_directory(self, root_dir: str, pattern: str, max_depth: int, 
                         current_depth: int, result_list: List[str], max_results: int, 
                         is_wildcard: bool = False) -> None:
        """
        Recursively search a directory for matching folders.
        
        Args:
            root_dir (str): Directory to search
            pattern (str): Pattern to match
            max_depth (int): Maximum search depth
            current_depth (int): Current search depth
            result_list (List[str]): List to populate with found folders
            max_results (int): Maximum number of results to return
            is_wildcard (bool): Whether the pattern contains wildcards
        """
        if current_depth > max_depth or len(result_list) >= max_results:
            return
        
        try:
            # Get all items in the directory
            items = os.listdir(root_dir)
            
            # First check for exact matches
            if not is_wildcard:
                if pattern.lower() in [item.lower() for item in items]:
                    for item in items:
                        if item.lower() == pattern.lower() and os.path.isdir(os.path.join(root_dir, item)):
                            result_list.append(os.path.join(root_dir, item))
                            if len(result_list) >= max_results:
                                return
            
            # Then check for pattern matches
            for item in items:
                item_path = os.path.join(root_dir, item)
                if os.path.isdir(item_path):
                    # Check if the item matches the pattern
                    if is_wildcard:
                        if fnmatch.fnmatch(item.lower(), pattern.lower()):
                            result_list.append(item_path)
                            if len(result_list) >= max_results:
                                return
                    else:
                        if pattern.lower() in item.lower():
                            result_list.append(item_path)
                            if len(result_list) >= max_results:
                                return
                    
                    # Recursively search subdirectories
                    self._search_directory(
                        item_path,
                        pattern,
                        max_depth,
                        current_depth + 1,
                        result_list,
                        max_results,
                        is_wildcard
                    )
        
        except Exception as e:
            if not self.quiet_mode:
                logger.error(f"Error searching directory {root_dir}: {e}")
    
    def find_files(self, file_pattern: str, location: str = "~", max_results: int = 20) -> str:
        """
        Find files matching a given pattern.
        
        Args:
            file_pattern (str): Pattern to search for
            location (str): Root directory to start the search
            max_results (int): Maximum number of results to return
            
        Returns:
            str: Formatted search results with emojis and clear organization
        """
        # Sanitize inputs
        file_pattern = file_pattern.replace('"', '\\"').replace("'", "\\'")
        location = get_file_path(os.path.expanduser(location))
        
        try:
            # Prepare results container
            all_files: List[str] = []
            
            # Determine if we're using wildcards
            is_wildcard = '*' in file_pattern or '?' in file_pattern
            
            # Compile regex pattern if needed
            pattern_obj = None
            if is_wildcard:
                pattern_obj = re.compile(fnmatch.translate(file_pattern), re.IGNORECASE)
            
            # Get target extension if specified
            target_extension = None
            if '.' in file_pattern and not is_wildcard:
                target_extension = file_pattern.split('.')[-1].lower()
            
            # Set search depth based on mode
            max_depth = 3 if self.fast_mode else 5
            
            # Start the search
            self._search_files_directory(
                location,
                file_pattern,
                pattern_obj,
                all_files,
                max_results,
                0,
                max_depth,
                target_extension
            )
            
            # Format the output with emojis
            if not all_files:
                return f"I searched for '{file_pattern}' but didn't find any matching files in {location}."
            
            formatted_result = f"I found these files matching '{file_pattern}':\n\n"
            
            # Group files by extension
            files_by_extension: Dict[str, List[str]] = {}
            for file in all_files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in files_by_extension:
                    files_by_extension[ext] = []
                files_by_extension[ext].append(file)
            
            # Show files grouped by extension
            for ext, files in files_by_extension.items():
                if ext:
                    formatted_result += f"📄 {ext} files:\n\n"
                else:
                    formatted_result += "📄 Other files:\n\n"
                
                for file in files:
                    formatted_result += f"  • {file}\n"
                
                formatted_result += "\n"
            
            if len(all_files) >= max_results:
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
        Recursively search a directory for matching files.
        
        Args:
            directory (str): Directory to search
            file_pattern (str): Pattern to match
            pattern_obj (Optional[re.Pattern]): Compiled regex pattern
            result_list (List[str]): List to populate with found files
            max_results (int): Maximum number of results to return
            current_depth (int): Current search depth
            max_depth (int): Maximum search depth
            target_extension (Optional[str]): Target file extension
        """
        if current_depth > max_depth or len(result_list) >= max_results:
            return
        
        try:
            # Get all items in the directory
            items = os.listdir(directory)
            
            for item in items:
                item_path = os.path.join(directory, item)
                
                if os.path.isfile(item_path):
                    # Check if the file matches the pattern
                    if pattern_obj:
                        if pattern_obj.match(item):
                            result_list.append(item_path)
                            if len(result_list) >= max_results:
                                return
                    elif target_extension:
                        if item.lower().endswith(f".{target_extension}"):
                            result_list.append(item_path)
                            if len(result_list) >= max_results:
                                return
                    else:
                        if file_pattern.lower() in item.lower():
                            result_list.append(item_path)
                            if len(result_list) >= max_results:
                                return
                
                elif os.path.isdir(item_path):
                    # Recursively search subdirectories
                    self._search_files_directory(
                        item_path,
                        file_pattern,
                        pattern_obj,
                        result_list,
                        max_results,
                        current_depth + 1,
                        max_depth,
                        target_extension
                    )
        
        except Exception as e:
            if not self.quiet_mode:
                logger.error(f"Error searching directory {directory}: {e}") 