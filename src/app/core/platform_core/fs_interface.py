import logging
import sys
from typing import Any, Dict, List, Optional

from .base_fs_handler import BaseFSHandler

class FSInterface:
    """Platform-agnostic file system interface."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the file system interface.
        
        Args:
            config: Optional configuration dictionary
        """
        self._config = config or {}
        self._handler = self._initialize_handler()
    
    def _initialize_handler(self) -> Optional[BaseFSHandler]:
        """Initialize the appropriate platform-specific handler.
        
        Returns:
            Optional[BaseFSHandler]: Initialized handler or None if initialization fails
        """
        try:
            if sys.platform == 'darwin':
                from .macos.fs_handler import MacOSFSHandler
                handler = MacOSFSHandler(self._config)
            elif sys.platform == 'win32':
                from .windows.fs_handler import WindowsFSHandler
                handler = WindowsFSHandler(self._config)
            elif sys.platform.startswith('linux'):
                from .linux.fs_handler import LinuxFSHandler
                handler = LinuxFSHandler(self._config)
            else:
                logging.error(f"Unsupported platform: {sys.platform}")
                return None
            
            if not handler.initialize():
                logging.error("Failed to initialize file system handler")
                return None
                
            return handler
            
        except Exception as e:
            logging.error(f"Error initializing file system handler: {e}")
            return None
    
    def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """List contents of a directory.
        
        Args:
            path: Directory path to list
            
        Returns:
            List[Dict[str, Any]]: List of file/directory information dictionaries
        """
        if not self._handler:
            return []
        return self._handler.list_directory(path)
    
    def create_directory(self, path: str) -> bool:
        """Create a new directory.
        
        Args:
            path: Directory path to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._handler:
            return False
        return self._handler.create_directory(path)
    
    def delete_path(self, path: str, recursive: bool = False) -> bool:
        """Delete a file or directory.
        
        Args:
            path: Path to delete
            recursive: Whether to delete directories recursively
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._handler:
            return False
        return self._handler.delete_path(path, recursive)
    
    def move_path(self, src: str, dst: str) -> bool:
        """Move a file or directory.
        
        Args:
            src: Source path
            dst: Destination path
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._handler:
            return False
        return self._handler.move_path(src, dst)
    
    def copy_path(self, src: str, dst: str) -> bool:
        """Copy a file or directory.
        
        Args:
            src: Source path
            dst: Destination path
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._handler:
            return False
        return self._handler.copy_path(src, dst)
    
    def get_path_info(self, path: str) -> Dict[str, Any]:
        """Get information about a path.
        
        Args:
            path: Path to get information for
            
        Returns:
            Dict[str, Any]: Dictionary containing path information
        """
        if not self._handler:
            return {'error': 'No file system handler available'}
        return self._handler.get_path_info(path)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current file system status.
        
        Returns:
            Dict[str, Any]: Dictionary containing file system status information
        """
        if not self._handler:
            return {'error': 'No file system handler available'}
        return self._handler.get_status()
    
    def cleanup(self) -> None:
        """Clean up file system resources."""
        if self._handler:
            self._handler.cleanup()
            self._handler = None 