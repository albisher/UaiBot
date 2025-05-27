"""
File Tool Implementation

This module provides the FileTool for file system operations,
implementing A2A (Agent-to-Agent), MCP (Model Context Protocol), and SmolAgents patterns.
"""
import os
import shutil
import json
from pathlib import Path
from typing import Any, Dict, List, Union
from .base_tool import BaseTool
from . import ToolRegistry

@ToolRegistry.register
class FileTool(BaseTool):
    """Tool for file system operations."""
    
    def __init__(self):
        """Initialize the FileTool."""
        super().__init__(
            name="FileTool",
            description="Handles file system operations including reading, writing, and managing files"
        )
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a file system operation.
        
        Args:
            action (str): The action to execute
            **kwargs: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the operation
        """
        try:
            if not self.validate_input(action, **kwargs):
                return self.handle_error(ValueError("Invalid input"))
            
            if action == "read_file":
                return self._read_file(**kwargs)
            elif action == "write_file":
                return self._write_file(**kwargs)
            elif action == "list_directory":
                return self._list_directory(**kwargs)
            elif action == "create_directory":
                return self._create_directory(**kwargs)
            elif action == "delete_file":
                return self._delete_file(**kwargs)
            elif action == "move_file":
                return self._move_file(**kwargs)
            elif action == "copy_file":
                return self._copy_file(**kwargs)
            else:
                return self.handle_error(ValueError(f"Unknown action: {action}"))
                
        except Exception as e:
            return self.handle_error(e)
    
    def get_available_actions(self) -> Dict[str, str]:
        """
        Get available file system operations.
        
        Returns:
            Dict[str, str]: Available operations and their descriptions
        """
        return {
            "read_file": "Read contents of a file",
            "write_file": "Write contents to a file",
            "list_directory": "List contents of a directory",
            "create_directory": "Create a new directory",
            "delete_file": "Delete a file",
            "move_file": "Move a file to a new location",
            "copy_file": "Copy a file to a new location"
        }
    
    def _read_file(self, path: str, encoding: str = "utf-8", **kwargs) -> Dict[str, Any]:
        """Read contents of a file."""
        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
            return {
                "content": content,
                "size": os.path.getsize(path),
                "encoding": encoding
            }
        except FileNotFoundError:
            return self.handle_error(ValueError(f"File not found: {path}"))
        except Exception as e:
            return self.handle_error(e)
    
    def _write_file(self, path: str, content: str, encoding: str = "utf-8", **kwargs) -> Dict[str, Any]:
        """Write contents to a file."""
        try:
            with open(path, "w", encoding=encoding) as f:
                f.write(content)
            return {
                "path": path,
                "size": os.path.getsize(path),
                "encoding": encoding
            }
        except Exception as e:
            return self.handle_error(e)
    
    def _list_directory(self, path: str = ".", **kwargs) -> Dict[str, Any]:
        """List contents of a directory."""
        try:
            items = []
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                items.append({
                    "name": item,
                    "path": full_path,
                    "type": "directory" if os.path.isdir(full_path) else "file",
                    "size": os.path.getsize(full_path) if os.path.isfile(full_path) else None
                })
            return {"items": items}
        except Exception as e:
            return self.handle_error(e)
    
    def _create_directory(self, path: str, **kwargs) -> Dict[str, Any]:
        """Create a new directory."""
        try:
            os.makedirs(path, exist_ok=True)
            return {
                "path": path,
                "created": True
            }
        except Exception as e:
            return self.handle_error(e)
    
    def _delete_file(self, path: str, **kwargs) -> Dict[str, Any]:
        """Delete a file."""
        try:
            if os.path.isfile(path):
                os.remove(path)
                return {"deleted": True, "path": path}
            else:
                return self.handle_error(ValueError(f"Not a file: {path}"))
        except Exception as e:
            return self.handle_error(e)
    
    def _move_file(self, source: str, destination: str, **kwargs) -> Dict[str, Any]:
        """Move a file to a new location."""
        try:
            shutil.move(source, destination)
            return {
                "source": source,
                "destination": destination,
                "moved": True
            }
        except Exception as e:
            return self.handle_error(e)
    
    def _copy_file(self, source: str, destination: str, **kwargs) -> Dict[str, Any]:
        """Copy a file to a new location."""
        try:
            shutil.copy2(source, destination)
            return {
                "source": source,
                "destination": destination,
                "copied": True
            }
        except Exception as e:
            return self.handle_error(e)