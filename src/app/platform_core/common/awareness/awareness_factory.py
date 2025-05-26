"""
Factory for creating platform-specific awareness handlers.

This module provides a factory class for creating platform-specific awareness handlers,
following A2A (Agent-to-Agent), MCP (Multi-Context Protocol), and SmolAgents patterns.
"""
import platform
from typing import Dict, Any, Type
from .base_awareness import BaseAwarenessHandler

class AwarenessHandlerFactory:
    """Factory class for creating platform-specific awareness handlers."""
    
    _handlers: Dict[str, Type[BaseAwarenessHandler]] = {}
    
    @classmethod
    def register_handler(cls, platform_name: str, handler_class: Type[BaseAwarenessHandler]) -> None:
        """Register a platform-specific awareness handler.
        
        Args:
            platform_name: Name of the platform (e.g., 'Windows', 'Linux', 'Darwin').
            handler_class: Class implementing the platform-specific awareness handler.
        """
        cls._handlers[platform_name] = handler_class
    
    @classmethod
    def create_handler(cls, config: Dict[str, Any]) -> BaseAwarenessHandler:
        """Create a platform-specific awareness handler.
        
        Args:
            config: Configuration dictionary.
            
        Returns:
            BaseAwarenessHandler: Platform-specific awareness handler.
            
        Raises:
            ValueError: If no handler is registered for the current platform.
        """
        system = platform.system()
        handler_class = cls._handlers.get(system)
        
        if handler_class is None:
            raise ValueError(f"No awareness handler registered for platform: {system}")
        
        return handler_class(config)
    
    @classmethod
    def get_supported_platforms(cls) -> list[str]:
        """Get list of supported platforms.
        
        Returns:
            list[str]: List of supported platform names.
        """
        return list(cls._handlers.keys()) 