"""
Base handler for platform-specific functionality.

This module provides a base class for all platform-specific handlers,
ensuring consistent interface and proper isolation.
"""
import os
import sys
import platform
from typing import Dict, Any, Optional, List, Type, TypeVar, Generic

T = TypeVar('T')

class BaseHandler(Generic[T]):
    """Base class for platform-specific handlers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the base handler.
        
        Args:
            config: Configuration for the handler.
        """
        self._config = config or {}
        self._initialized = False
        self._platform = None
        self._validate_platform()
    
    def initialize(self) -> bool:
        """Initialize the handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        if self._initialized:
            return True
        
        try:
            # Validate platform
            if not self._validate_platform():
                return False
            
            # Initialize handler
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize {self.__class__.__name__}: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up handler resources."""
        self._initialized = False
    
    def is_available(self) -> bool:
        """Check if the handler is available.
        
        Returns:
            bool: True if the handler is available, False otherwise.
        """
        return self._initialized
    
    def _validate_platform(self) -> bool:
        """Validate that the handler is running on the correct platform.
        
        Returns:
            bool: True if the platform is valid, False otherwise.
        """
        try:
            from ..platform_manager import platform_manager
            
            # Get current platform
            current_platform = platform_manager.get_platform()
            
            # Get handler platform from class name
            handler_platform = self.__class__.__name__.lower()
            if handler_platform.startswith('mac'):
                handler_platform = 'macos'
            elif handler_platform.startswith('ubuntu'):
                handler_platform = 'ubuntu'
            elif handler_platform.startswith('windows'):
                handler_platform = 'windows'
            elif handler_platform.startswith('jetson'):
                handler_platform = 'jetson'
            
            # Validate platform
            if current_platform != handler_platform:
                print(f"Warning: {self.__class__.__name__} is not supported on {current_platform}")
                return False
            
            self._platform = current_platform
            return True
            
        except Exception as e:
            print(f"Failed to validate platform: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get the handler configuration.
        
        Returns:
            Dict[str, Any]: Handler configuration.
        """
        return self._config.copy()
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update the handler configuration.
        
        Args:
            config: New configuration to apply.
            
        Returns:
            bool: True if configuration was updated successfully, False otherwise.
        """
        try:
            self._config.update(config)
            return True
        except Exception as e:
            print(f"Failed to update configuration: {e}")
            return False
    
    def get_platform_specific_path(self, path: str) -> str:
        """Get a platform-specific path.
        
        Args:
            path: Base path to make platform-specific.
            
        Returns:
            str: Platform-specific path.
        """
        try:
            # Get platform-specific path components
            if self._platform == 'macos':
                base_dir = os.path.expanduser('~/Library/Application Support/Labeeb')
            elif self._platform == 'ubuntu':
                base_dir = os.path.expanduser('~/.config/labeeb')
            elif self._platform == 'windows':
                base_dir = os.path.join(os.environ.get('APPDATA', ''), 'Labeeb')
            elif self._platform == 'jetson':
                base_dir = os.path.expanduser('~/.config/labeeb')
            else:
                base_dir = os.path.expanduser('~/.labeeb')
            
            # Create directory if it doesn't exist
            os.makedirs(base_dir, exist_ok=True)
            
            # Return full path
            return os.path.join(base_dir, path)
            
        except Exception as e:
            print(f"Failed to get platform-specific path: {e}")
            return path
    
    def get_feature_config(self, feature: str) -> Dict[str, Any]:
        """Get configuration for a specific feature.
        
        Args:
            feature: Name of the feature.
            
        Returns:
            Dict[str, Any]: Feature configuration.
        """
        return self._config.get(feature, {})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled.
        
        Args:
            feature: Name of the feature.
            
        Returns:
            bool: True if the feature is enabled, False otherwise.
        """
        feature_config = self.get_feature_config(feature)
        return feature_config.get('enabled', False)
    
    def get_handler_name(self) -> str:
        """Get the name of the handler.
        
        Returns:
            str: Handler name.
        """
        return self.__class__.__name__ 