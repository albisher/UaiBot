from .system.macos_system import MacOSSystem
from .ui.macos_ui import MacOSUI
from .network.macos_network import MacOSNetwork
from .audio.macos_audio import MacOSAudio
from .fs.macos_fs import MacOSFileSystem
from ..platform_factory import PlatformFactory

# Register macOS implementations
PlatformFactory.register_system_impl('macos', MacOSSystem)
PlatformFactory.register_ui_impl('macos', MacOSUI)
PlatformFactory.register_network_impl('macos', MacOSNetwork)
PlatformFactory.register_audio_impl('macos', MacOSAudio)
PlatformFactory.register_fs_impl('macos', MacOSFileSystem) 