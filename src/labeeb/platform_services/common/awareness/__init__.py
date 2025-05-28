"""
Awareness module initialization.

This module initializes the awareness handlers and registers them with the factory.
"""
from .base_awareness import BaseAwarenessHandler, AwarenessContext
from .awareness_factory import AwarenessHandlerFactory

# Import platform-specific handlers
try:
    from ...windows.awareness.windows_awareness import WindowsAwarenessHandler
    AwarenessHandlerFactory.register_handler('Windows', WindowsAwarenessHandler)
except ImportError:
    pass

try:
    from ...ubuntu.awareness.ubuntu_awareness import UbuntuAwarenessHandler
    AwarenessHandlerFactory.register_handler('Linux', UbuntuAwarenessHandler)
except ImportError:
    pass

try:
    from ...macos.awareness.macos_awareness import MacOSAwarenessHandler
    AwarenessHandlerFactory.register_handler('Darwin', MacOSAwarenessHandler)
except ImportError:
    pass

__all__ = [
    'BaseAwarenessHandler',
    'AwarenessContext',
    'AwarenessHandlerFactory'
] 