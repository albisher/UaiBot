"""
File Operations Handler Module

Handles file operations using structured data from AI responses.
Supports creating, reading, writing, deleting, searching, and listing files.
"""

import os
import json
import logging
import shlex
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List, Union
from datetime import datetime
from uaibot.core.file_search import FileSearch

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
        
        # Command keywords for natural language processing
        self.command_keywords = {
            "create": ["create", "make", "new", "generate", "add"],
            "read": ["read", "show", "display", "get", "view", "open"],
            "write": ["write", "update", "modify", "change", "edit"],
            "delete": ["delete", "remove", "erase", "drop"],
            "search": ["find", "search", "look", "locate", "seek"],
            "list": ["list", "ls", "dir", "show", "display"]
        }
        
        # File operation indicators
        self.file_indicators = ["file", "document", "text", "content"]
        
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
        
        # Check required parameters
        if not filename:
            return "❌ No filename specified for deletion"
            
        # Handle relative paths
        filename = self._resolve_path(filename)
        
        try:
            # Check if file exists
            if not os.path.exists(filename):
                return f"❌ File not found: {filename}"
                
            if not os.path.isfile(filename):
                return f"❌ {filename} is not a file"
                
            # Delete the file
            os.remove(filename)
            return f"✅ Deleted file: {filename}"
            
        except Exception as e:
            return f"❌ Error deleting file: {str(e)}"
    
    def handle_search(self, params: Dict[str, Any]) -> str:
        """
        Handle file search operation.
        
        Args:
            params: Operation parameters
            
        Returns:
            Operation result message
        """
        # Get parameters
        pattern = params.get("pattern")
        directory = params.get("directory", ".")
        max_results = params.get("max_results", 10)
        
        # Check required parameters
        if not pattern:
            return "❌ No search pattern specified"
            
        # Handle relative paths
        directory = self._resolve_path(directory)
        
        try:
            # Search for files
            results = self.file_search.search_files(pattern, directory, max_results)
            
            if not results:
                return f"🔍 No files found matching '{pattern}' in {directory}"
                
            # Format results
            result_str = f"🔍 Found {len(results)} files matching '{pattern}' in {directory}:\n\n"
            for i, result in enumerate(results, 1):
                result_str += f"{i}. {result}\n"
                
            return result_str
            
        except Exception as e:
            return f"❌ Error searching files: {str(e)}"
    
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
        max_results = params.get("max_results", 50)
        
        # Handle relative paths
        directory = self._resolve_path(directory)
        
        try:
            # List files
            files = []
            for item in os.listdir(directory):
                if not show_hidden and item.startswith('.'):
                    continue
                    
                path = os.path.join(directory, item)
                size = os.path.getsize(path)
                is_dir = os.path.isdir(path)
                
                files.append({
                    'name': item,
                    'size': self._format_size(size),
                    'is_dir': is_dir
                })
                
            # Sort files (directories first, then alphabetically)
            files.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            
            # Format results
            result_str = f"📁 Contents of {directory}:\n\n"
            for i, file in enumerate(files[:max_results], 1):
                icon = "📁" if file['is_dir'] else "📄"
                result_str += f"{i}. {icon} {file['name']} ({file['size']})\n"
                
            if len(files) > max_results:
                result_str += f"\n... and {len(files) - max_results} more items"
                
            return result_str
            
        except Exception as e:
            return f"❌ Error listing files: {str(e)}"
    
    def _resolve_path(self, path: str) -> str:
        """
        Resolve a path, handling special directories and relative paths.
        
        Args:
            path: Path to resolve
            
        Returns:
            Resolved absolute path
        """
        # Handle special directories
        if path in self.default_dirs:
            return self.default_dirs[path]
            
        # Handle relative paths
        if not os.path.isabs(path):
            return os.path.abspath(path)
            
        return path
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def parse_operation_from_ai_metadata(self, metadata: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Parse file operation from AI response metadata.
        
        Args:
            metadata: AI response metadata
            
        Returns:
            Tuple of (operation_type, parameters)
        """
        if not isinstance(metadata, dict):
            return None, {}
            
        # Extract operation type
        operation_type = metadata.get("operation")
        if not operation_type or operation_type not in self.command_keywords:
            return None, {}
            
        # Extract parameters
        params = metadata.get("parameters", {})
        if not isinstance(params, dict):
            return None, {}
            
        return operation_type, params
    
    def extract_operation_from_request(self, request: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract file operation from natural language request.
        
        Args:
            request: Natural language request
            
        Returns:
            Tuple of (operation_type, parameters)
        """
        request_lower = request.lower()
        words = request_lower.split()
        
        # Find operation type
        operation_type = None
        for op, keywords in self.command_keywords.items():
            if any(keyword in words for keyword in keywords):
                operation_type = op
                break
                
        if not operation_type:
            return None, {}
            
        # Extract parameters based on operation type
        params = {}
        
        # Extract filename
        filename = None
        for indicator in self.file_indicators:
            if indicator in words:
                idx = words.index(indicator)
                if idx + 1 < len(words):
                    # Check for quoted filename
                    if '"' in request or "'" in request:
                        quote_start = request.find('"') if '"' in request else request.find("'")
                        quote_end = request.find('"', quote_start + 1) if '"' in request else request.find("'", quote_start + 1)
                        if quote_end != -1:
                            filename = request[quote_start + 1:quote_end]
                    else:
                        # Try to find filename after indicator
                        potential_filename = words[idx + 1]
                        if '.' in potential_filename:  # Basic file extension check
                            filename = potential_filename
                break
                
        if filename:
            params["filename"] = filename
            
        # Extract content for write operations
        if operation_type in ["create", "write"]:
            content = None
            if "with content" in request_lower or "containing" in request_lower:
                content_start = request_lower.find("with content") + len("with content")
                if content_start == -1:
                    content_start = request_lower.find("containing") + len("containing")
                if content_start != -1:
                    content = request[content_start:].strip()
                    if content.startswith('"') or content.startswith("'"):
                        content = content[1:]
                    if content.endswith('"') or content.endswith("'"):
                        content = content[:-1]
                    params["content"] = content
                    
        # Extract search pattern
        if operation_type == "search":
            pattern = None
            if "named" in request_lower or "containing" in request_lower:
                pattern_start = request_lower.find("named") + len("named")
                if pattern_start == -1:
                    pattern_start = request_lower.find("containing") + len("containing")
                if pattern_start != -1:
                    pattern = request[pattern_start:].strip()
                    if pattern.startswith('"') or pattern.startswith("'"):
                        pattern = pattern[1:]
                    if pattern.endswith('"') or pattern.endswith("'"):
                        pattern = pattern[:-1]
                    params["pattern"] = pattern
                    
        # Extract directory
        if "in" in words:
            dir_idx = words.index("in")
            if dir_idx + 1 < len(words):
                directory = words[dir_idx + 1]
                if directory in self.default_dirs:
                    params["directory"] = directory
                    
        # Extract max results
        if "limit" in words or "max" in words:
            limit_idx = words.index("limit") if "limit" in words else words.index("max")
            if limit_idx + 2 < len(words) and words[limit_idx + 1] == "results":
                try:
                    max_results = int(words[limit_idx + 2])
                    params["max_results"] = max_results
                except ValueError:
                    pass
                    
        return operation_type, params
