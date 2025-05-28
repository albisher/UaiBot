import os
import shutil
import stat
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from ...common.fs.fs_interface import FileSystemInterface

class MacOSFileSystem(FileSystemInterface):
    """macOS implementation of filesystem operations."""
    
    def list_directory(self, path: Union[str, Path]) -> List[Dict[str, str]]:
        """List contents of a directory."""
        path = Path(path)
        if not path.exists() or not path.is_dir():
            return []
        
        items = []
        for item in path.iterdir():
            try:
                stat_info = item.stat()
                item_info = {
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': str(stat_info.st_size),
                    'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    'permissions': oct(stat_info.st_mode)[-3:]
                }
                items.append(item_info)
            except (PermissionError, OSError):
                continue
        return items
    
    def create_directory(self, path: Union[str, Path]) -> bool:
        """Create a new directory."""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except (PermissionError, OSError):
            return False
    
    def delete_directory(self, path: Union[str, Path], recursive: bool = False) -> bool:
        """Delete a directory."""
        try:
            if recursive:
                shutil.rmtree(path)
            else:
                os.rmdir(path)
            return True
        except (PermissionError, OSError):
            return False
    
    def create_file(self, path: Union[str, Path], content: Optional[str] = None) -> bool:
        """Create a new file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                if content:
                    f.write(content)
            return True
        except (PermissionError, OSError):
            return False
    
    def read_file(self, path: Union[str, Path]) -> str:
        """Read contents of a file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except (PermissionError, OSError, UnicodeDecodeError):
            return ''
    
    def write_file(self, path: Union[str, Path], content: str) -> bool:
        """Write content to a file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except (PermissionError, OSError):
            return False
    
    def delete_file(self, path: Union[str, Path]) -> bool:
        """Delete a file."""
        try:
            os.remove(path)
            return True
        except (PermissionError, OSError):
            return False
    
    def get_file_info(self, path: Union[str, Path]) -> Dict[str, str]:
        """Get information about a file."""
        try:
            stat_info = Path(path).stat()
            return {
                'name': Path(path).name,
                'type': 'directory' if Path(path).is_dir() else 'file',
                'size': str(stat_info.st_size),
                'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'permissions': oct(stat_info.st_mode)[-3:],
                'owner': str(stat_info.st_uid),
                'group': str(stat_info.st_gid)
            }
        except (PermissionError, OSError):
            return {}
    
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Copy a file."""
        try:
            shutil.copy2(source, destination)
            return True
        except (PermissionError, OSError):
            return False
    
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Move a file."""
        try:
            shutil.move(source, destination)
            return True
        except (PermissionError, OSError):
            return False
    
    def get_disk_usage(self, path: Optional[Union[str, Path]] = None) -> Dict[str, float]:
        """Get disk usage information."""
        try:
            if path:
                path = Path(path)
                while not path.exists():
                    path = path.parent
                usage = shutil.disk_usage(path)
            else:
                usage = shutil.disk_usage('/')
            
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': (usage.used / usage.total) * 100
            }
        except (PermissionError, OSError):
            return {
                'total': 0.0,
                'used': 0.0,
                'free': 0.0,
                'percent': 0.0
            } 