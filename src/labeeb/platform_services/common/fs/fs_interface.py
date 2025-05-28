from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
from pathlib import Path

class FileSystemInterface(ABC):
    """Interface for filesystem-related operations."""
    
    @abstractmethod
    def list_directory(self, path: Union[str, Path]) -> List[Dict[str, str]]:
        """List contents of a directory."""
        pass
    
    @abstractmethod
    def create_directory(self, path: Union[str, Path]) -> bool:
        """Create a new directory."""
        pass
    
    @abstractmethod
    def delete_directory(self, path: Union[str, Path], recursive: bool = False) -> bool:
        """Delete a directory."""
        pass
    
    @abstractmethod
    def create_file(self, path: Union[str, Path], content: Optional[str] = None) -> bool:
        """Create a new file."""
        pass
    
    @abstractmethod
    def read_file(self, path: Union[str, Path]) -> str:
        """Read contents of a file."""
        pass
    
    @abstractmethod
    def write_file(self, path: Union[str, Path], content: str) -> bool:
        """Write content to a file."""
        pass
    
    @abstractmethod
    def delete_file(self, path: Union[str, Path]) -> bool:
        """Delete a file."""
        pass
    
    @abstractmethod
    def get_file_info(self, path: Union[str, Path]) -> Dict[str, str]:
        """Get information about a file."""
        pass
    
    @abstractmethod
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Copy a file."""
        pass
    
    @abstractmethod
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Move a file."""
        pass
    
    @abstractmethod
    def get_disk_usage(self, path: Optional[Union[str, Path]] = None) -> Dict[str, float]:
        """Get disk usage information."""
        pass 