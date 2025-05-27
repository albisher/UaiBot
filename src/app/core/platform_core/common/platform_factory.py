import sys
from typing import Optional

from .platform_interface import PlatformInterface

class PlatformFactory:
    """Factory class for creating platform-specific implementations."""
    
    _instance: Optional[PlatformInterface] = None
    
    @classmethod
    def get_platform(cls) -> PlatformInterface:
        """Get the platform implementation for the current system."""
        if cls._instance is None:
            platform_name = sys.platform.lower()
            
            if platform_name == "darwin":
                from ..macos.macos_platform import MacOSPlatform
                cls._instance = MacOSPlatform()
            elif platform_name == "win32":
                from ..windows.platform import WindowsPlatform
                cls._instance = WindowsPlatform()
            elif platform_name.startswith("linux"):
                from ..linux.platform import LinuxPlatform
                cls._instance = LinuxPlatform()
            else:
                raise NotImplementedError(f"Platform {platform_name} is not supported")
        
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset the platform instance (useful for testing)."""
        cls._instance = None 