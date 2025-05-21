"""
File Operations Handler Module

Handles file operations using structured data from AI responses.
Supports creating, reading, writing, deleting, searching, and listing files.
"""

import os
import re
import json
import logging
import shlex
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List, Union
from datetime import datetime
from core.file_search import FileSearch

logger = logging.getLogger(__name__)

class FileOperationsHandler:
    """
    Handles file operations requested through natural language or JSON structure.
    """
    
    def __init__(self, shell_handler=None, quiet_mode=False):
        """
        Initialize the file operations handler.
        
        Args:
            shell_handler: Shell handler for executing commands
            quiet_mode: Whether to minimize console output
        """
        self.shell_handler = shell_handler
        self.quiet_mode = quiet_mode
        
        # Default directory paths - will be expanded as needed
        self.default_dirs = {
            "desktop": os.path.expanduser("~/Desktop"),
            "documents": os.path.expanduser("~/Documents"),
            "downloads": os.path.expanduser("~/Downloads"),
            "home": os.path.expanduser("~"),
            "temp": os.path.expanduser("/tmp"),
            "current": ".",
            "test_files": "test_files"
        }
        
        # Ensure test_files directory exists
        if not os.path.exists("test_files"):
            try:
                os.makedirs("test_files", exist_ok=True)
                logger.info("Created test_files directory")
            except Exception as e:
                logger.warning(f"Could not create test_files directory: {e}")
                
        self.file_search = FileSearch(quiet_mode=quiet_mode)
        
    def log(self, message, level="info"):
        """Log a message with specified level."""
        if not self.quiet_mode or level in ["warning", "error"]:
            if level == "warning":
                print(f"⚠️ {message}")
            elif level == "error":
                print(f"❌ {message}")
            else:
                print(f"📝 {message}")
                
        # Log to logger as well
        getattr(logger, level)(message)
    
    def handle_operation(self, operation_type: str, params: Dict[str, Any]) -> str:
        """
        Handle a file operation based on operation type and parameters.
        
        Args:
            operation_type: Type of file operation (create, read, write, delete, search, list)
            params: Parameters for the operation
            
        Returns:
            Operation result message
        """
        # Validate operation type
        if operation_type not in ["create", "read", "write", "delete", "search", "list"]:
            return f"❌ Unsupported file operation: {operation_type}"
            
        # Dispatch to the appropriate handler
        try:
            if operation_type == "create":
                return self.handle_create(params)
            elif operation_type == "read":
                return self.handle_read(params)
            elif operation_type == "write":
                return self.handle_write(params)
            elif operation_type == "delete":
                return self.handle_delete(params)
            elif operation_type == "search":
                return self.handle_search(params)
            elif operation_type == "list":
                return self.handle_list(params)
        except Exception as e:
            logger.error(f"Error in file operation {operation_type}: {e}")
            return f"❌ Error in file operation: {str(e)}"
    
    def handle_create(self, params: Dict[str, Any]) -> str:
        """
        Handle file creation operation.
        
        Args:
            params: Operation parameters
            
        Returns:
            Operation result message
        """
        # Get parameters
        filename = params.get("filename")
        content = params.get("content", "")
        add_date = params.get("add_date", False)
        
        # Check required parameters
        if not filename:
            return "❌ No filename specified for file creation"
            
        # Handle relative paths
        filename = self._resolve_path(filename)
        
        # Ensure directory exists
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                return f"❌ Error creating directory {directory}: {str(e)}"
                
        try:
            # Create the file
            if add_date:
                # Add date at the beginning of content
                date_str = datetime.now().strftime("%Y-%m-%d")
                with open(filename, 'w') as file:
                    file.write(f"{date_str}\n{content}")
            else:
                # Create with specified content
                with open(filename, 'w') as file:
                    file.write(content)
                    
            return f"✅ Created file: {filename}" + \
                   (f"\n📝 Content: {content}" if content else "")
        except Exception as e:
            return f"❌ Error creating file: {str(e)}"
    
    def handle_read(self, params: Dict[str, Any]) -> str:
        """
        Handle file reading operation.
        
        Args:
            params: Operation parameters
            
        Returns:
            Operation result message
        """
        # Get parameters
        filename = params.get("filename")
        max_lines = params.get("max_lines", 20)  # Default to 20 lines
        
        # Check required parameters
        if not filename:
            return "❌ No filename specified for reading"
            
        # Handle relative paths
        filename = self._resolve_path(filename)
        
        try:
            # Check if file exists
            if not os.path.exists(filename):
                return f"❌ File not found: {filename}"
                
            if not os.path.isfile(filename):
                return f"❌ {filename} is not a file"
                
            # Read the file
            with open(filename, 'r') as file:
                content = file.read()
                
            # Truncate if too long
            lines = content.split('\n')
            if len(lines) > max_lines:
                truncated_content = '\n'.join(lines[:max_lines])
                return f"📄 Content of {filename} (first {max_lines} lines):\n\n{truncated_content}\n\n[...File truncated, {len(lines)} lines total...]"
            else:
                return f"📄 Content of {filename}:\n\n{content}"
                
        except UnicodeDecodeError:
            # Handle binary files
            return f"❌ {filename} appears to be a binary file and cannot be displayed"
        except Exception as e:
            return f"❌ Error reading file: {str(e)}"
    
    def handle_write(self, params: Dict[str, Any]) -> str:
        """
        Handle file write or append operation.
        
        Args:
            params: Operation parameters
            
        Returns:
            Operation result message
        """
        # Get parameters
        filename = params.get("filename")
        content = params.get("content", "")
        append = params.get("append", False)
        add_date = params.get("add_date", False)
        
        # Check required parameters
        if not filename:
            return "❌ No filename specified for writing"
            
        # Handle relative paths
        filename = self._resolve_path(filename)
        
        # Ensure directory exists
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                return f"❌ Error creating directory {directory}: {str(e)}"
                
        try:
            # Prepare content
            if add_date:
                date_str = datetime.now().strftime("%Y-%m-%d")
                content = f"{date_str}\n{content}"
                
            # Write or append to the file
            mode = 'a' if append else 'w'
            with open(filename, mode) as file:
                file.write(content)
                
            action = "Appended to" if append else "Wrote to"
            return f"✅ {action} file: {filename}\n📝 Content: {content}"
            
        except Exception as e:
            return f"❌ Error writing to file: {str(e)}"
    
    def handle_delete(self, params: Dict[str, Any]) -> str:
        """
        Handle file deletion operation.
        
        Args:
            params: Operation parameters
            
        Returns:
            Operation result message
        """
        # Get parameters
        filename = params.get("filename")
        force = params.get("force", False)
        
        # Check required parameters
        if not filename:
            return "❌ No filename specified for deletion"
            
        # Handle relative paths
        filename = self._resolve_path(filename)
        
        try:
            # Check if file exists
            if not os.path.exists(filename):
                return f"❌ File not found: {filename}"
                
            # Check if it's a directory
            if os.path.isdir(filename) and not force:
                return f"❌ {filename} is a directory. Use force=True to delete directories."
                
            # Delete file or directory
            if os.path.isdir(filename):
                import shutil
                shutil.rmtree(filename)
                return f"✅ Deleted directory: {filename}"
            else:
                os.remove(filename)
                return f"✅ Deleted file: {filename}"
                
        except Exception as e:
            return f"❌ Error deleting file: {str(e)}"
    
    def handle_search(self, query: str) -> str:
        """
        Handle a file search query.
        
        This method processes the query to extract search parameters and
        uses the FileSearch class to perform the search.
        
        Args:
            query (str): The search query to process
            
        Returns:
            str: Formatted search results
        """
        try:
            # Extract search parameters from query
            file_pattern, location, max_results = self._parse_query(query)
            
            # Perform the search using FileSearch
            return self.file_search.find_files(file_pattern, location, max_results)
            
        except Exception as e:
            error_msg = f"Error processing file search: {str(e)}"
            if not self.quiet_mode:
                logger.error(error_msg)
            return error_msg
    
    def _parse_query(self, query: str) -> tuple[str, str, int]:
        """
        Parse a file search query to extract search parameters.
        
        Args:
            query (str): The search query to parse
            
        Returns:
            tuple[str, str, int]: Tuple containing (file_pattern, location, max_results)
        """
        # Default values
        file_pattern = ""
        location = "~"
        max_results = 20
        
        # Extract file pattern
        if "named" in query:
            parts = query.split("named", 1)
            if len(parts) > 1:
                file_pattern = parts[1].strip()
        elif "containing" in query:
            parts = query.split("containing", 1)
            if len(parts) > 1:
                file_pattern = parts[1].strip()
        else:
            # Try to extract file pattern from common patterns
            import re
            patterns = [
                r"find files? (?:named|containing|with) ['\"](.+?)['\"]",
                r"search for files? (?:named|containing|with) ['\"](.+?)['\"]",
                r"look for files? (?:named|containing|with) ['\"](.+?)['\"]"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    file_pattern = match.group(1)
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
        
        return file_pattern, location, max_results
    
    def handle_list(self, params: Dict[str, Any]) -> str:
        """
        Handle file listing operation.
        
        Args:
            params: Operation parameters
            
        Returns:
            Operation result message
        """
        # Get parameters
        directory = params.get("directory", ".")
        show_hidden = params.get("show_hidden", False)
        
        # Handle relative paths
        directory = self._resolve_path(directory)
        
        try:
            # Check if directory exists
            if not os.path.exists(directory):
                return f"❌ Directory not found: {directory}"
                
            if not os.path.isdir(directory):
                return f"❌ {directory} is not a directory"
                
            # Execute list command using shell handler if available
            if self.shell_handler:
                cmd = f"ls -la {shlex.quote(directory)}" if show_hidden else f"ls -l {shlex.quote(directory)}"
                result = self.shell_handler.execute_command(cmd)
                
                return f"📂 Contents of {directory}:\n{result}"
            else:
                # Fallback to Python's os.listdir
                files = os.listdir(directory)
                
                if not show_hidden:
                    # Filter out hidden files
                    files = [f for f in files if not f.startswith('.')]
                    
                if not files:
                    return f"Directory {directory} is empty."
                    
                # Format list with file types
                formatted_list = []
                for file in sorted(files):
                    file_path = os.path.join(directory, file)
                    if os.path.isdir(file_path):
                        formatted_list.append(f"📁 {file}/")
                    else:
                        # Get file size
                        size = os.path.getsize(file_path)
                        size_str = self._format_size(size)
                        formatted_list.append(f"📄 {file} ({size_str})")
                        
                return f"📂 Contents of {directory}:\n" + "\n".join(formatted_list)
                
        except Exception as e:
            return f"❌ Error listing directory: {str(e)}"
    
    def _resolve_path(self, path: str) -> str:
        """
        Resolve a path string, expanding special directories and user home.
        
        Args:
            path: Path string that may contain special directory references
            
        Returns:
            Resolved path
        """
        # Handle special directories
        if path.startswith(tuple(self.default_dirs.keys())):
            for key, dir_path in self.default_dirs.items():
                # Check for exact match or directory name followed by / or \
                if path == key or path.startswith(f"{key}/") or path.startswith(f"{key}\\"):
                    # Replace just the directory part
                    return path.replace(key, dir_path, 1)
        
        # Expand user home directory (~)
        return os.path.expanduser(path)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in a human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0 or unit == 'TB':
                break
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} {unit}"
    
    def parse_operation_from_ai_metadata(self, metadata: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract file operation information from AI response metadata.
        
        Args:
            metadata: Metadata dictionary from AI command extraction
            
        Returns:
            Tuple of (operation_type, operation_params) or (None, {}) if not a file operation
        """
        if not metadata.get("file_operation"):
            return None, {}
            
        operation_type = metadata["file_operation"]
        operation_params = metadata.get("operation_params", {})
        
        return operation_type, operation_params
    
    def extract_operation_from_request(self, request: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract file operation from natural language request.
        
        Args:
            request: User request string
            
        Returns:
            Tuple of (operation_type, operation_params) or (None, {}) if not a file operation
        """
        request_lower = request.lower()
        
        # Define operation mapping
        operations = {
            "create": ["create", "new", "make", "touch", "generate", "انشاء", "انشئ", "جديد"],
            "read": ["read", "show", "display", "cat", "view", "output", "اقرأ", "اعرض", "اظهر"],
            "write": ["write", "add", "append", "edit", "update", "اكتب", "أكتب", "اضف", "أضف"],
            "delete": ["delete", "remove", "erase", "destroy", "trash", "rm", "احذف", "امسح", "ازل", "أزل"],
            "search": ["search", "find", "locate", "where", "which", "ابحث", "جد", "أين", "اين", "وين"],
            "list": ["list", "ls", "dir", "enumerate", "اظهر", "اعرض", "قائمة"]
        }
        
        # Check for file operation indicators
        operation_type = None
        for op_type, keywords in operations.items():
            if any(keyword in request_lower for keyword in keywords):
                operation_type = op_type
                break
                
        if not operation_type:
            return None, {}
            
        # Extract operation parameters
        params = {}
        
        # Extract filename - look for quoted or extension-containing words
        filename_match = re.search(r'[\'"]([\w\.-]+\.[\w]+)[\'"]|(?:file|filename|document)\s+[\'"]?([\w\.-]+\.[\w]+)[\'"]?', request)
        if filename_match:
            filename = filename_match.group(1) or filename_match.group(2)
            params["filename"] = filename
        elif "test_files" in request_lower:
            # Default for test_files folder
            filename_match = re.search(r'test_files/([^\s,]+)', request_lower)
            if filename_match:
                params["filename"] = f"test_files/{filename_match.group(1)}"
            else:
                params["filename"] = "test_files/file.txt"
        
        # Extract content for write operations
        if operation_type == "write":
            content_match = re.search(r'[\'"]([^\'"\n]+)[\'"]|content\s+[\'"]?([^\'"\n.]+)[\'"]?', request)
            if content_match:
                content = content_match.group(1) or content_match.group(2)
                params["content"] = content
            
            # Check for append vs. overwrite
            params["append"] = any(word in request_lower for word in ["append", "add", "اضف", "أضف"])
        
        # Extract directory for list/search operations
        if operation_type in ["list", "search"]:
            if "desktop" in request_lower:
                params["directory"] = "desktop"
            elif "documents" in request_lower:
                params["directory"] = "documents"
            elif "downloads" in request_lower:
                params["directory"] = "downloads"
            elif "test_files" in request_lower:
                params["directory"] = "test_files"
            else:
                params["directory"] = "current"
        
        # Extract search term for search operations
        if operation_type == "search":
            search_match = re.search(r'(?:for|containing|with)\s+[\'"]?([^\'"\n.]+)[\'"]?', request_lower)
            if search_match:
                params["search_term"] = search_match.group(1)
        
        return operation_type, params
