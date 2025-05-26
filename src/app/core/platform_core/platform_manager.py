"""
Platform manager for Labeeb.

This module provides a central manager for platform-specific functionality,
coordinating between different platform handlers and ensuring proper isolation.
"""
import os
import sys
import platform
import logging
from typing import Dict, Any, Optional, List, Type
from .common.base_handler import BaseHandler
from .mac.input_handler import MacInputHandler
from .mac.audio_handler import MacAudioHandler
from .mac.display_handler import MacDisplayHandler
from .mac.usb_handler import MacUSBHandler
from .mac.shell_handler import MacShellHandler
from .mac.browser_handler import MacBrowserHandler
from .common.system_info import BaseSystemInfoGatherer
from .mac.system_info import MacSystemInfoGatherer
from .windows.system_info import WindowsSystemInfoGatherer
from .ubuntu.system_info import UbuntuSystemInfoGatherer
from .shell_handler import BaseShellHandler
from .browser_handler import BaseBrowserHandler
from .i18n import gettext as _

logger = logging.getLogger(__name__)

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
    
    _shell_handlers: Dict[str, Type[BaseShellHandler]] = {
        'Darwin': MacShellHandler,
        'Windows': None,  # TODO: Implement Windows shell handler
        'Linux': None,    # TODO: Implement Linux shell handler
    }
    
    _browser_handlers: Dict[str, Type[BaseBrowserHandler]] = {
        'Darwin': MacBrowserHandler,
        'Windows': None,  # TODO: Implement Windows browser handler
        'Linux': None,    # TODO: Implement Linux browser handler
    }
    
    def __init__(self):
        """Initialize the platform manager."""
        self.platform = sys.platform
        self.handlers = {}
        self._load_platform_handlers()
        self._config: Dict[str, Any] = {}
        self._initialized = False
    
    def _load_platform_handlers(self) -> None:
        """Load platform-specific handlers based on the current OS"""
        try:
            if self.platform == 'darwin':
                from .macos import calendar_controller
                self.handlers['calendar'] = calendar_controller.CalendarController()
            elif self.platform == 'win32':
                # Windows handlers will be loaded here
                pass
            elif self.platform.startswith('linux'):
                # Linux handlers will be loaded here
                pass
        except Exception as e:
            logger.error(f"Error loading platform handlers: {str(e)}")
            raise
    
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
        for handler in self.handlers.values():
            try:
                handler.cleanup()
            except Exception as e:
                print(f"Error cleaning up handler: {e}")
        
        self.handlers.clear()
        self._initialized = False
    
    def _load_config(self) -> None:
        """Load platform-specific configuration."""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__),
                self.platform,
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
            'usb': MacUSBHandler,
            'shell': self._shell_handlers.get(platform.system(), None),
            'browser': self._browser_handlers.get(platform.system(), None)
        }
        
        # Initialize each handler
        for handler_type, handler_class in handler_map.items():
            if handler_class is None:
                continue
                
            try:
                handler = handler_class(self._config.get(handler_type, {}))
                if handler.initialize():
                    self.handlers[handler_type] = handler
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
        return self.handlers.get(handler_type)
    
    def get_platform(self) -> str:
        """Get the current platform identifier.
        
        Returns:
            str: Platform identifier.
        """
        return self.platform
    
    def is_platform_supported(self) -> bool:
        """Check if the current platform is supported.
        
        Returns:
            bool: True if the platform is supported, False otherwise.
        """
        return self.platform != 'unknown'
    
    def get_config(self) -> Dict[str, Any]:
        """Get the platform configuration.
        
        Returns:
            Dict[str, Any]: Platform configuration.
        """
        return self._config.copy()
    
    def get_available_handlers(self) -> List[str]:
        """Get a list of available handler types.
        
        Returns:
            List[str]: List of available handler types.
        """
        return list(self.handlers.keys())
    
    def is_handler_available(self, handler_type: str) -> bool:
        """Check if a specific handler type is available.
        
        Args:
            handler_type: Type of handler to check.
            
        Returns:
            bool: True if the handler is available, False otherwise.
        """
        return handler_type in self.handlers
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get information about the current platform.
        
        Returns:
            Dict[str, Any]: Platform information.
        """
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'features': self._get_platform_features(),
            'paths': self._get_platform_paths()
        }
    
    def _get_platform_features(self) -> Dict[str, bool]:
        """Get platform-specific features.
        
        Returns:
            Dict[str, bool]: Dictionary of feature flags.
        """
        features = {
            'gui_support': False,
            'audio_support': False,
            'usb_support': False,
            'network_support': True,
            'file_system_support': True
        }
        
        # Update features based on available handlers
        if 'display' in self.handlers:
            features['gui_support'] = True
        if 'audio' in self.handlers:
            features['audio_support'] = True
        if 'usb' in self.handlers:
            features['usb_support'] = True
            
        return features
    
    def _get_platform_paths(self) -> Dict[str, str]:
        """Get platform-specific paths.
        
        Returns:
            Dict[str, str]: Dictionary of platform paths.
        """
        paths = {
            'home': os.path.expanduser('~'),
            'config': os.path.join(os.path.expanduser('~'), '.config', 'labeeb'),
            'data': os.path.join(os.path.expanduser('~'), '.local', 'share', 'labeeb'),
            'cache': os.path.join(os.path.expanduser('~'), '.cache', 'labeeb')
        }
        
        # Platform-specific path adjustments
        if self.platform == 'win32':
            paths['config'] = os.path.join(os.environ.get('APPDATA', ''), 'Labeeb')
            paths['data'] = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Labeeb')
            paths['cache'] = os.path.join(os.environ.get('TEMP', ''), 'Labeeb')
            
        return paths
    
    def get_handlers(self) -> Dict[str, Any]:
        """Get all platform handlers.
        
        Returns:
            Dict[str, Any]: Dictionary of all handlers.
        """
        return self.handlers.copy()
    
    @classmethod
    def get_system_info_gatherer(cls) -> BaseSystemInfoGatherer:
        """Get the appropriate system info gatherer for the current platform.
        
        Returns:
            BaseSystemInfoGatherer: System info gatherer instance.
        """
        system = platform.system()
        gatherer_class = cls._system_info_gatherers.get(system)
        if gatherer_class is None:
            raise RuntimeError(f"No system info gatherer available for {system}")
        return gatherer_class()
    
    @classmethod
    def get_system_info(cls, language: Optional[str] = None) -> Dict[str, Any]:
        """Get system information.
        
        Args:
            language: Optional language code for localized information.
            
        Returns:
            Dict[str, Any]: System information.
        """
        gatherer = cls.get_system_info_gatherer()
        return gatherer.gather_info(language)

def get_platform_system_info_gatherer() -> BaseSystemInfoGatherer:
    """Get the appropriate system info gatherer for the current platform.
    
    Returns:
        BaseSystemInfoGatherer: System info gatherer instance.
    """
    return PlatformManager.get_system_info_gatherer()

# Create a singleton instance
platform_manager = PlatformManager()
