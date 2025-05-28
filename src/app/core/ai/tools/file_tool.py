"""
File tool for Labeeb AI system.

This module provides functionality for file operations.
"""
import os
import logging
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool
from .tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class FileTool(BaseTool):
    """Tool for file operations."""
    
    def __init__(self):
        """Initialize the file tool."""
        super().__init__(name="file", description="Tool for file operations")
    
    def create_file(self, path: str, content: str) -> bool:
        """Create a file with the given content.
        
        Args:
            path: Path to the file
            content: Content to write to the file
            
        Returns:
            bool: True if file was created successfully
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Write content to file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Failed to create file {path}: {e}")
            return False
    
    def read_file(self, path: str) -> Optional[str]:
        """Read content from a file.
        
        Args:
            path: Path to the file
            
        Returns:
            Optional[str]: File content if successful, None otherwise
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {path}: {e}")
            return None
    
    def delete_file(self, path: str) -> bool:
        """Delete a file.
        
        Args:
            path: Path to the file
            
        Returns:
            bool: True if file was deleted successfully
        """
        try:
            os.remove(path)
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {path}: {e}")
            return False
    
    def list_files(self, directory: str) -> List[str]:
        """List files in a directory.
        
        Args:
            directory: Directory to list files from
            
        Returns:
            List[str]: List of file names
        """
        try:
            return os.listdir(directory)
        except Exception as e:
            logger.error(f"Failed to list files in {directory}: {e}")
            return []
    
    def file_exists(self, path: str) -> bool:
        """Check if a file exists.
        
        Args:
            path: Path to the file
            
        Returns:
            bool: True if file exists
        """
        return os.path.isfile(path)
    
    def directory_exists(self, path: str) -> bool:
        """Check if a directory exists.
        
        Args:
            path: Path to the directory
            
        Returns:
            bool: True if directory exists
        """
        return os.path.isdir(path)
    
    def create_directory(self, path: str) -> bool:
        """Create a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            bool: True if directory was created successfully
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return False
    
    def delete_directory(self, path: str) -> bool:
        """Delete a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            bool: True if directory was deleted successfully
        """
        try:
            os.rmdir(path)
            return True
        except Exception as e:
            logger.error(f"Failed to delete directory {path}: {e}")
            return False
    
    def get_file_size(self, path: str) -> Optional[int]:
        """Get file size in bytes.
        
        Args:
            path: Path to the file
            
        Returns:
            Optional[int]: File size in bytes if successful, None otherwise
        """
        try:
            return os.path.getsize(path)
        except Exception as e:
            logger.error(f"Failed to get file size for {path}: {e}")
            return None
    
    def get_file_extension(self, path: str) -> str:
        """Get file extension.
        
        Args:
            path: Path to the file
            
        Returns:
            str: File extension
        """
        return os.path.splitext(path)[1]
    
    def get_file_name(self, path: str) -> str:
        """Get file name without extension.
        
        Args:
            path: Path to the file
            
        Returns:
            str: File name without extension
        """
        return os.path.splitext(os.path.basename(path))[0]
    
    def get_file_path(self, path: str) -> str:
        """Get file path without file name.
        
        Args:
            path: Path to the file
            
        Returns:
            str: File path without file name
        """
        return os.path.dirname(path)
    
    def get_absolute_path(self, path: str) -> str:
        """Get absolute path.
        
        Args:
            path: Path to the file
            
        Returns:
            str: Absolute path
        """
        return os.path.abspath(path)
    
    def get_relative_path(self, path: str, start: str) -> str:
        """Get relative path.
        
        Args:
            path: Path to the file
            start: Start directory
            
        Returns:
            str: Relative path
        """
        return os.path.relpath(path, start)
    
    def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get file information.
        
        Args:
            path: Path to the file
            
        Returns:
            Dict[str, Any]: File information
        """
        try:
            stat = os.stat(path)
            return {
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'mode': stat.st_mode,
                'uid': stat.st_uid,
                'gid': stat.st_gid
            }
        except Exception as e:
            logger.error(f"Failed to get file info for {path}: {e}")
            return {}

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a file operation action asynchronously."""
        try:
            if action == "create_file":
                result = self.create_file(kwargs["path"], kwargs.get("content", ""))
                return {"success": result}
            elif action == "read_file":
                content = self.read_file(kwargs["path"])
                return {"content": content}
            elif action == "delete_file":
                result = self.delete_file(kwargs["path"])
                return {"success": result}
            elif action == "list_files":
                files = self.list_files(kwargs["directory"])
                return {"files": files}
            elif action == "file_exists":
                exists = self.file_exists(kwargs["path"])
                return {"exists": exists}
            elif action == "directory_exists":
                exists = self.directory_exists(kwargs["path"])
                return {"exists": exists}
            elif action == "create_directory":
                result = self.create_directory(kwargs["path"])
                return {"success": result}
            elif action == "delete_directory":
                result = self.delete_directory(kwargs["path"])
                return {"success": result}
            elif action == "get_file_size":
                size = self.get_file_size(kwargs["path"])
                return {"size": size}
            elif action == "get_file_extension":
                ext = self.get_file_extension(kwargs["path"])
                return {"extension": ext}
            elif action == "get_file_name":
                name = self.get_file_name(kwargs["path"])
                return {"name": name}
            elif action == "get_file_path":
                path = self.get_file_path(kwargs["path"])
                return {"path": path}
            elif action == "get_absolute_path":
                abs_path = self.get_absolute_path(kwargs["path"])
                return {"absolute_path": abs_path}
            elif action == "get_relative_path":
                rel_path = self.get_relative_path(kwargs["path"], kwargs["start"])
                return {"relative_path": rel_path}
            elif action == "get_file_info":
                info = self.get_file_info(kwargs["path"])
                return {"info": info}
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return self.handle_error(e)

    def get_available_actions(self) -> Dict[str, str]:
        """Get available actions for this tool.
        
        Returns:
            Dict[str, str]: Dictionary of action names and descriptions
        """
        return {
            "create_directory": "Create a new directory",
            "list_files": "List files in a directory",
            "create_file": "Create a new file",
            "read_file": "Read content from a file",
            "delete_file": "Delete a file",
            "delete_directory": "Delete a directory"
        }

    async def forward(self, **kwargs):
        action = kwargs.get('action')
        args = kwargs.copy()
        args.pop('action', None)
        return await self._execute_command(action, args)

    async def _execute_command(self, action: str, args: dict) -> dict:
        if action == "create_directory":
            path = args.get("path")
            if not path:
                return {"error": "No path provided"}
            success = self.create_directory(path)
            return {"success": success, "path": path}
        elif action == "list_files":
            directory = args.get("directory", ".")
            files = self.list_files(directory)
            return {"files": files, "directory": directory}
        elif action == "create_file":
            path = args.get("path")
            content = args.get("content", "")
            if not path:
                return {"error": "No path provided"}
            success = self.create_file(path, content)
            return {"success": success, "path": path}
        elif action == "read_file":
            path = args.get("path")
            if not path:
                return {"error": "No path provided"}
            content = self.read_file(path)
            return {"content": content, "path": path}
        elif action == "delete_file":
            path = args.get("path")
            if not path:
                return {"error": "No path provided"}
            success = self.delete_file(path)
            return {"success": success, "path": path}
        elif action == "delete_directory":
            path = args.get("path")
            if not path:
                return {"error": "No path provided"}
            success = self.delete_directory(path)
            return {"success": success, "path": path}
        else:
            return {"error": f"Unknown action: {action}"}