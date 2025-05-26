"""
Platform manager for UaiBot.

This module provides a central manager for platform-specific functionality,
coordinating between different platform handlers and ensuring proper isolation.
"""
import os
import sys
import platform
from typing import Dict, Any, Optional, List, Type
from .common.base_handler import BaseHandler
from .mac.input_handler import MacInputHandler
from .mac.audio_handler import MacAudioHandler
from .mac.display_handler import MacDisplayHandler
from .mac.usb_handler import MacUSBHandler
from .common.system_info import BaseSystemInfoGatherer
from .mac.system_info import MacSystemInfoGatherer
from .windows.system_info import WindowsSystemInfoGatherer
from .ubuntu.system_info import UbuntuSystemInfoGatherer
from .i18n import gettext as _

class PlatformManager:
    """Manager for platform-specific functionality."""
    
    # Supported platforms
    SUPPORTED_PLATFORMS = {
        'darwin': 'macos',
        'linux': 'ubuntu',
        'win32': 'windows'
    }
    
    _system_info_gatherers: Dict[str, Type[BaseSystemInfoGatherer]] = {
        'Darwin': MacSystemInfoGatherer,
        'Windows': WindowsSystemInfoGatherer,
        'Linux': UbuntuSystemInfoGatherer,
    }
    
    def __init__(self):
        """Initialize the platform manager."""
        self._platform = self._detect_platform()
        self._handlers: Dict[str, BaseHandler] = {}
        self._config: Dict[str, Any] = {}
        self._initialized = False
    
    def _detect_platform(self) -> str:
        """Detect the current platform.
        
        Returns:
            str: Platform identifier.
        """
        system = sys.platform
        platform_name = self.SUPPORTED_PLATFORMS.get(system, 'unknown')
        
        # Additional platform-specific detection
        if platform_name == 'ubuntu':
            # Check for Jetson
            try:
                with open('/proc/device-tree/model', 'r') as f:
                    model = f.read().lower()
                    if 'jetson' in model:
                        return 'jetson'
            except:
                pass
            
            # Check for specific Linux distribution
            try:
                import distro
                dist_name = distro.name().lower()
                if 'ubuntu' in dist_name:
                    return 'ubuntu'
                elif 'debian' in dist_name:
                    return 'debian'
                elif 'fedora' in dist_name:
                    return 'fedora'
                elif 'centos' in dist_name or 'rhel' in dist_name:
                    return 'rhel'
                elif 'arch' in dist_name:
                    return 'arch'
            except ImportError:
                pass
        
        return platform_name
    
    def initialize(self) -> bool:
        """Initialize the platform manager.
        
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        if self._initialized:
            return True
        
        try:
            # Load platform configuration
            self._load_config()
            
            # Initialize platform-specific handlers
            self._initialize_handlers()
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize PlatformManager: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up platform manager resources."""
        if not self._initialized:
            return
        
        # Clean up all handlers
        for handler in self._handlers.values():
            try:
                handler.cleanup()
            except Exception as e:
                print(f"Error cleaning up handler: {e}")
        
        self._handlers.clear()
        self._initialized = False
    
    def _load_config(self) -> None:
        """Load platform-specific configuration."""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__),
                self._platform,
                'config.json'
            )
            
            if os.path.exists(config_path):
                import json
                with open(config_path, 'r') as f:
                    self._config = json.load(f)
            else:
                print(f"Warning: No configuration file found at {config_path}")
                self._config = {}
                
        except Exception as e:
            print(f"Failed to load platform configuration: {e}")
            self._config = {}
    
    def _initialize_handlers(self) -> None:
        """Initialize platform-specific handlers."""
        # Map of handler types to their platform-specific implementations
        handler_map: Dict[str, Type[BaseHandler]] = {
            'input': MacInputHandler,
            'audio': MacAudioHandler,
            'display': MacDisplayHandler,
            'usb': MacUSBHandler
        }
        
        # Initialize each handler
        for handler_type, handler_class in handler_map.items():
            try:
                handler = handler_class(self._config.get(handler_type, {}))
                if handler.initialize():
                    self._handlers[handler_type] = handler
                else:
                    print(f"Warning: Failed to initialize {handler_type} handler")
            except Exception as e:
                print(f"Error initializing {handler_type} handler: {e}")
    
    def get_handler(self, handler_type: str) -> Optional[BaseHandler]:
        """Get a platform-specific handler.
        
        Args:
            handler_type: Type of handler to get (e.g., 'input', 'audio').
            
        Returns:
            Optional[BaseHandler]: The requested handler or None if not available.
        """
        return self._handlers.get(handler_type)
    
    def get_platform(self) -> str:
        """Get the current platform identifier.
        
        Returns:
            str: Platform identifier.
        """
        return self._platform
    
    def is_platform_supported(self) -> bool:
        """Check if the current platform is supported.
        
        Returns:
            bool: True if the platform is supported, False otherwise.
        """
        return self._platform != 'unknown'
    
    def get_config(self) -> Dict[str, Any]:
        """Get the platform configuration.
        
        Returns:
            Dict[str, Any]: Platform configuration.
        """
        return self._config.copy()
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update the platform configuration.
        
        Args:
            config: New configuration to apply.
            
        Returns:
            bool: True if configuration was updated successfully, False otherwise.
        """
        try:
            # Update configuration
            self._config.update(config)
            
            # Save configuration to file
            config_path = os.path.join(
                os.path.dirname(__file__),
                self._platform,
                'config.json'
            )
            
            import json
            with open(config_path, 'w') as f:
                json.dump(self._config, f, indent=4)
            
            # Reinitialize handlers with new configuration
            self.cleanup()
            return self.initialize()
            
        except Exception as e:
            print(f"Failed to update platform configuration: {e}")
            return False
    
    def get_available_handlers(self) -> List[str]:
        """Get list of available handlers.
        
        Returns:
            List[str]: List of available handler types.
        """
        return list(self._handlers.keys())
    
    def is_handler_available(self, handler_type: str) -> bool:
        """Check if a specific handler is available.
        
        Args:
            handler_type: Type of handler to check.
            
        Returns:
            bool: True if the handler is available, False otherwise.
        """
        handler = self.get_handler(handler_type)
        return handler is not None and handler.is_available()
    
    def get_platform_info(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed platform information.
        
        Args:
            language: Optional language code for localized labels
            
        Returns:
            Dict[str, Any]: Platform information.
        """
        info = {
            'name': self._platform,
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'handlers': self.get_available_handlers()
        }
        
        # Add platform-specific information
        if self._platform == 'macos':
            info['mac_version'] = platform.mac_ver()[0]
        elif self._platform == 'windows':
            info['windows_edition'] = platform.win32_edition() if hasattr(platform, 'win32_edition') else ""
        
        return info

    @classmethod
    def get_system_info_gatherer(cls) -> BaseSystemInfoGatherer:
        """Get the appropriate system info gatherer for the current platform.
        
        Returns:
            BaseSystemInfoGatherer: Platform-specific system info gatherer
            
        Raises:
            NotImplementedError: If platform is not supported
        """
        system = platform.system()
        gatherer_class = cls._system_info_gatherers.get(system)
        
        if gatherer_class is None:
            raise NotImplementedError(f"System info gatherer not implemented for platform: {system}")
        
        return gatherer_class()
    
    @classmethod
    def get_system_info(cls, language: Optional[str] = None) -> Dict[str, Any]:
        """Get system information for the current platform.
        
        Args:
            language: Optional language code for localized labels
            
        Returns:
            Dict[str, Any]: Dictionary containing system information
        """
        gatherer = cls.get_system_info_gatherer()
        return gatherer.get_system_info(language)

def get_platform_system_info_gatherer() -> BaseSystemInfoGatherer:
    """Get the appropriate system info gatherer for the current platform.
    
    Returns:
        BaseSystemInfoGatherer: Platform-specific system info gatherer
    """
    return PlatformManager.get_system_info_gatherer()

# Create singleton instance
platform_manager = PlatformManager()
