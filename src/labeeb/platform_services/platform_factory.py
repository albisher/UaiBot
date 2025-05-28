import platform
from typing import Dict, Type

from .common.system.system_interface import SystemInterface
from .common.ui.ui_interface import UIInterface
from .common.network.network_interface import NetworkInterface
from .common.audio.audio_interface import AudioInterface
from .common.fs.fs_interface import FileSystemInterface

class PlatformFactory:
    """Factory for creating platform-specific implementations."""
    
    _system_impl: Dict[str, Type[SystemInterface]] = {}
    _ui_impl: Dict[str, Type[UIInterface]] = {}
    _network_impl: Dict[str, Type[NetworkInterface]] = {}
    _audio_impl: Dict[str, Type[AudioInterface]] = {}
    _fs_impl: Dict[str, Type[FileSystemInterface]] = {}
    
    @classmethod
    def register_system_impl(cls, platform_name: str, implementation: Type[SystemInterface]) -> None:
        """Register a system implementation for a platform."""
        cls._system_impl[platform_name] = implementation
    
    @classmethod
    def register_ui_impl(cls, platform_name: str, implementation: Type[UIInterface]) -> None:
        """Register a UI implementation for a platform."""
        cls._ui_impl[platform_name] = implementation
    
    @classmethod
    def register_network_impl(cls, platform_name: str, implementation: Type[NetworkInterface]) -> None:
        """Register a network implementation for a platform."""
        cls._network_impl[platform_name] = implementation
    
    @classmethod
    def register_audio_impl(cls, platform_name: str, implementation: Type[AudioInterface]) -> None:
        """Register an audio implementation for a platform."""
        cls._audio_impl[platform_name] = implementation
    
    @classmethod
    def register_fs_impl(cls, platform_name: str, implementation: Type[FileSystemInterface]) -> None:
        """Register a filesystem implementation for a platform."""
        cls._fs_impl[platform_name] = implementation
    
    @classmethod
    def get_current_platform(cls) -> str:
        """Get the current platform name."""
        system = platform.system().lower()
        if system == 'darwin':
            return 'macos'
        elif system == 'windows':
            return 'windows'
        elif system == 'linux':
            return 'linux'
        else:
            raise NotImplementedError(f"Platform {system} is not supported")
    
    @classmethod
    def create_system(cls) -> SystemInterface:
        """Create a system implementation for the current platform."""
        platform_name = cls.get_current_platform()
        if platform_name not in cls._system_impl:
            raise NotImplementedError(f"No system implementation for {platform_name}")
        return cls._system_impl[platform_name]()
    
    @classmethod
    def create_ui(cls) -> UIInterface:
        """Create a UI implementation for the current platform."""
        platform_name = cls.get_current_platform()
        if platform_name not in cls._ui_impl:
            raise NotImplementedError(f"No UI implementation for {platform_name}")
        return cls._ui_impl[platform_name]()
    
    @classmethod
    def create_network(cls) -> NetworkInterface:
        """Create a network implementation for the current platform."""
        platform_name = cls.get_current_platform()
        if platform_name not in cls._network_impl:
            raise NotImplementedError(f"No network implementation for {platform_name}")
        return cls._network_impl[platform_name]()
    
    @classmethod
    def create_audio(cls) -> AudioInterface:
        """Create an audio implementation for the current platform."""
        platform_name = cls.get_current_platform()
        if platform_name not in cls._audio_impl:
            raise NotImplementedError(f"No audio implementation for {platform_name}")
        return cls._audio_impl[platform_name]()
    
    @classmethod
    def create_fs(cls) -> FileSystemInterface:
        """Create a filesystem implementation for the current platform."""
        platform_name = cls.get_current_platform()
        if platform_name not in cls._fs_impl:
            raise NotImplementedError(f"No filesystem implementation for {platform_name}")
        return cls._fs_impl[platform_name]() 