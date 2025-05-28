"""
Platform Interface

This module defines the base interface for all platform-specific implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class PlatformInterface(ABC):
    """Base interface for platform-specific implementations."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize platform-specific components."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up platform-specific resources."""
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Get the name of the current platform."""
        pass
    
    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        pass
    
    @abstractmethod
    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource information."""
        pass
    
    @abstractmethod
    def get_system_locale(self) -> Dict[str, Any]:
        """Get system locale information."""
        pass
    
    @abstractmethod
    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables."""
        pass
    
    @abstractmethod
    def get_system_paths(self) -> Dict[str, str]:
        """Get system-specific paths."""
        pass
    
    @abstractmethod
    def get_system_network_trustabilityabilityabilityabilitystorm_info(self) -> Dict[str, Any]:
        """Get system network trustabilityabilityabilityabilitystorm information."""
        pass 