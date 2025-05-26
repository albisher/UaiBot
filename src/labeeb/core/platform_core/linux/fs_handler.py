import logging
import os
import shutil
import pwd
import grp
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..base_fs_handler import BaseFSHandler

logger = logging.getLogger(__name__)

class LinuxFSHandler(BaseFSHandler):
    """Linux-specific file system handler implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Linux file system handler.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
    
    def initialize(self) -> bool:
        """Initialize the Linux file system handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Linux-specific initialization if needed
            self._initialized = True
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Linux file system handler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up file system resources."""
        self._initialized = False
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get file system capabilities.
        
        Returns:
            Dict[str, bool]: Dictionary of available file system capabilities
        """
        return {
            'case_sensitive': True,  # Linux is case-sensitive
            'symlinks': True,
            'hard_links': True,
            'extended_attributes': True,
            'access_control': True
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current file system status.
        
        Returns:
            Dict[str, Any]: Dictionary containing file system status information
        """
        try:
            if not self._initialized:
                return {'error': 'Handler not initialized'}
            
            # Get root directory info
            root_info = self.get_path_info('/')
            
            return {
                'initialized': self._initialized,
                'root_space': root_info.get('space', {}),
                'case_sensitive': self.get_capabilities()['case_sensitive'],
                'platform': 'Linux'
            }
        except Exception as e:
            logging.error(f"Error getting file system status: {e}")
            return {'error': str(e)}
    
    def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """List contents of a directory.
        
        Args:
            path: Directory path to list
            
        Returns:
            List[Dict[str, Any]]: List of file/directory information dictionaries
        """
        try:
            if not self._initialized:
                return []
            
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                items.append(self.get_path_info(item_path))
            
            return items
        except Exception as e:
            logging.error(f"Error listing directory {path}: {e}")
            return []
    
    def create_directory(self, path: str) -> bool:
        """Create a new directory.
        
        Args:
            path: Directory path to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._initialized:
                return False
            
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logging.error(f"Error creating directory {path}: {e}")
            return False
    
    def delete_path(self, path: str, recursive: bool = False) -> bool:
        """Delete a file or directory.
        
        Args:
            path: Path to delete
            recursive: Whether to delete directories recursively
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._initialized:
                return False
            
            if os.path.isdir(path):
                if recursive:
                    shutil.rmtree(path)
                else:
                    os.rmdir(path)
            else:
                os.remove(path)
            return True
        except Exception as e:
            logging.error(f"Error deleting path {path}: {e}")
            return False
    
    def move_path(self, src: str, dst: str) -> bool:
        """Move a file or directory.
        
        Args:
            src: Source path
            dst: Destination path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._initialized:
                return False
            
            shutil.move(src, dst)
            return True
        except Exception as e:
            logging.error(f"Error moving path {src} to {dst}: {e}")
            return False
    
    def copy_path(self, src: str, dst: str) -> bool:
        """Copy a file or directory.
        
        Args:
            src: Source path
            dst: Destination path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._initialized:
                return False
            
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            return True
        except Exception as e:
            logging.error(f"Error copying path {src} to {dst}: {e}")
            return False
    
    def get_path_info(self, path: str) -> Dict[str, Any]:
        """Get information about a path.
        
        Args:
            path: Path to get information for
            
        Returns:
            Dict[str, Any]: Dictionary containing path information
        """
        try:
            if not self._initialized:
                return {'error': 'Handler not initialized'}
            
            stat = os.stat(path)
            
            # Get Linux-specific user and group info
            try:
                owner = pwd.getpwuid(stat.st_uid).pw_name
            except KeyError:
                owner = str(stat.st_uid)
                
            try:
                group = grp.getgrgid(stat.st_gid).gr_name
            except KeyError:
                group = str(stat.st_gid)
            
            info = {
                'name': os.path.basename(path),
                'path': path,
                'type': 'directory' if os.path.isdir(path) else 'file',
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'permissions': oct(stat.st_mode)[-3:],
                'owner': owner,
                'group': group
            }
            
            # Add Linux-specific attributes
            if os.path.isdir(path):
                try:
                    total, used, free = shutil.disk_usage(path)
                    info['space'] = {
                        'total': total,
                        'used': used,
                        'free': free
                    }
                except Exception:
                    pass
            
            return info
        except Exception as e:
            logging.error(f"Error getting path info for {path}: {e}")
            return {'error': str(e)} 