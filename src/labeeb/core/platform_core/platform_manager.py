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
from .mac.usb_handler import MacUSBHandler
from .common.system_info import BaseSystemInfoGatherer
from .shell_handler import BaseShellHandler
from .browser_handler import BaseBrowserHandler
from .i18n import gettext as _, is_rtl, get_current_language

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
        'Darwin': None,  # Will be lazily loaded
        'Windows': None,  # Will be lazily loaded
        'Linux': None,    # Will be lazily loaded
    }
    
    _shell_handlers: Dict[str, Type[BaseShellHandler]] = {
        'Darwin': None,  # Will be lazily loaded
        'Windows': None,  # TODO: Implement Windows shell handler
        'Linux': None,    # TODO: Implement Linux shell handler
    }
    
    _browser_handlers: Dict[str, Type[BaseBrowserHandler]] = {
        'Darwin': None,  # Will be lazily loaded
        'Windows': None,  # TODO: Implement Windows browser handler
        'Linux': None,    # TODO: Implement Linux browser handler
    }
    
    def __init__(self):
        """Initialize the platform manager."""
        self.platform = sys.platform
        self.platform_name = self.SUPPORTED_PLATFORMS.get(self.platform, 'unknown')
        self.handlers = {}
        self._load_platform_handlers()
        self._config: Dict[str, Any] = {}
        self._initialized = False
        
        # Initialize language and RTL support
        self.current_language = get_current_language()
        self.rtl_support = is_rtl(self.current_language)
        
        # Lazy load platform-specific modules
        if self.platform == 'darwin':
            from .mac.system_info import MacSystemInfoGatherer
            from .mac.shell_handler import MacShellHandler
            from .mac.browser_handler import MacBrowserHandler
            self._system_info_gatherers['Darwin'] = MacSystemInfoGatherer
            self._shell_handlers['Darwin'] = MacShellHandler
            self._browser_handlers['Darwin'] = MacBrowserHandler
        elif self.platform == 'win32':
            from .windows.system_info import WindowsSystemInfoGatherer
            self._system_info_gatherers['Windows'] = WindowsSystemInfoGatherer
        elif self.platform.startswith('linux'):
            from .ubuntu.system_info import UbuntuSystemInfoGatherer
            self._system_info_gatherers['Linux'] = UbuntuSystemInfoGatherer
    
    def _load_platform_handlers(self) -> None:
        """Load platform-specific handlers based on the current OS"""
        try:
            if self.platform == 'darwin':
                from .mac import calendar_controller
                self.handlers['calendar'] = calendar_controller.MacOSCalendarController()
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
            
            # Update RTL support based on current language
            self.current_language = get_current_language()
            self.rtl_support = is_rtl(self.current_language)
            
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
                self.platform_name,
                'config.json'
            )
            
            if os.path.exists(config_path):
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                print(f"Warning: No configuration file found at {config_path}")
                self._config = {}
                
        except Exception as e:
            print(f"Failed to load platform configuration: {e}")
            self._config = {}
    
    def _initialize_handlers(self) -> None:
        """Initialize platform-specific handlers."""
        # Import MacDisplayHandler here to avoid circular import
        from .mac.display_handler import MacDisplayHandler
        
        # Map of handler types to their platform-specific implementations
        handler_map: Dict[str, Type[BaseHandler]] = {
            'input': MacInputHandler,
            'audio': MacAudioHandler,
            'display': MacDisplayHandler,
            'usb': MacUSBHandler,
            'shell': self._shell_handlers.get(self.platform_name, None),
            'browser': self._browser_handlers.get(self.platform_name, None)
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
        return self.platform in self.SUPPORTED_PLATFORMS
    
    def get_config(self) -> Dict[str, Any]:
        """Get the platform configuration.
        
        Returns:
            Dict[str, Any]: Platform configuration.
        """
        return self._config.copy()
    
    def get_available_handlers(self) -> List[str]:
        """Get list of available handlers.
        
        Returns:
            List[str]: List of available handler types.
        """
        return list(self.handlers.keys())
    
    def is_handler_available(self, handler_type: str) -> bool:
        """Check if a handler is available.
        
        Args:
            handler_type: Type of handler to check.
            
        Returns:
            bool: True if the handler is available, False otherwise.
        """
        return handler_type in self.handlers
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform information.
        
        Returns:
            Dict[str, Any]: Platform information including features and paths.
        """
        return {
            'platform': self.platform,
            'platform_name': self.platform_name,
            'features': self._get_platform_features(),
            'paths': self._get_platform_paths(),
            'language': self.current_language,
            'rtl_support': self.rtl_support
        }
    
    def _get_platform_features(self) -> Dict[str, bool]:
        """Get platform-specific features.
        
        Returns:
            Dict[str, bool]: Dictionary of feature flags.
        """
        features = {
            'gui': True,
            'audio': True,
            'usb': True,
            'bluetooth': True,
            'network': True,
            'shell': True,
            'browser': True,
            'rtl': self.rtl_support
        }
        
        # Platform-specific feature adjustments
        if self.platform == 'darwin':
            features.update({
                'calendar': True,
                'notifications': True,
                'accessibility': True
            })
        elif self.platform == 'win32':
            features.update({
                'calendar': False,
                'notifications': True,
                'accessibility': True
            })
        elif self.platform.startswith('linux'):
            features.update({
                'calendar': False,
                'notifications': True,
                'accessibility': True
            })
            
        return features
    
    def _get_platform_paths(self) -> Dict[str, str]:
        """Get platform-specific paths.
        
        Returns:
            Dict[str, str]: Dictionary of platform paths.
        """
        paths = {}
        
        if self.platform == 'darwin':
            paths.update({
                'home': os.path.expanduser('~'),
                'config': os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Labeeb'),
                'cache': os.path.join(os.path.expanduser('~'), 'Library', 'Caches', 'Labeeb'),
                'logs': os.path.join(os.path.expanduser('~'), 'Library', 'Logs', 'Labeeb')
            })
        elif self.platform == 'win32':
            paths.update({
                'home': os.path.expanduser('~'),
                'config': os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Labeeb'),
                'cache': os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Labeeb'),
                'logs': os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Labeeb', 'Logs')
            })
        elif self.platform.startswith('linux'):
            paths.update({
                'home': os.path.expanduser('~'),
                'config': os.path.join(os.path.expanduser('~'), '.config', 'labeeb'),
                'cache': os.path.join(os.path.expanduser('~'), '.cache', 'labeeb'),
                'logs': os.path.join(os.path.expanduser('~'), '.local', 'share', 'labeeb', 'logs')
            })
            
        return paths
    
    def get_handlers(self) -> Dict[str, Any]:
        """Get all initialized handlers.
        
        Returns:
            Dict[str, Any]: Dictionary of initialized handlers.
        """
        return self.handlers.copy()
    
    @classmethod
    def get_system_info_gatherer(cls) -> BaseSystemInfoGatherer:
        """Get the appropriate system info gatherer for the current platform.
        
        Returns:
            BaseSystemInfoGatherer: System info gatherer instance.
        """
        platform_name = platform.system()
        gatherer_class = cls._system_info_gatherers.get(platform_name)
        
        if gatherer_class is None:
            raise NotImplementedError(f"No system info gatherer for {platform_name}")
            
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
        return gatherer.get_system_info(language)

def get_platform_system_info_gatherer() -> BaseSystemInfoGatherer:
    """Get the appropriate system info gatherer for the current platform.
    
    Returns:
        BaseSystemInfoGatherer: System info gatherer instance.
    """
    return PlatformManager.get_system_info_gatherer()

# Create a singleton instance
platform_manager = PlatformManager()
