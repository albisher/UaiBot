"""
Platform Interface

This module defines the interface that all platform-specific implementations must follow.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class PlatformInterface(ABC):
    """Base interface for platform-specific implementations."""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the platform implementation.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources used by the platform implementation."""
        pass
    
    @abstractmethod
    def get_platform_info(self) -> Dict[str, Any]:
        """Get information about the current platform.
        
        Returns:
            Dict[str, Any]: Dictionary containing platform information
        """
        pass
    
    @abstractmethod
    def is_platform_supported(self) -> bool:
        """Check if the current platform is supported.
        
        Returns:
            bool: True if the platform is supported, False otherwise
        """
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Get the name of the current platform.
        
        Returns:
            str: Platform name
        """
        pass 