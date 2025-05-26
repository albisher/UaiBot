"""
Base awareness handler for Labeeb.

This module provides the base class for platform-specific awareness handlers,
following A2A (Agent-to-Agent), MCP (Multi-Context Protocol), and SmolAgents patterns.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from ..base_handler import BaseHandler

@dataclass
class AwarenessContext:
    """Context information for awareness handlers."""
    system_info: Dict[str, Any]
    user_info: Dict[str, Any]
    environment_info: Dict[str, Any]
    agent_state: Dict[str, Any]

class BaseAwarenessHandler(BaseHandler, ABC):
    """Base class for platform-specific awareness handlers."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the awareness handler.
        
        Args:
            config: Configuration dictionary.
        """
        super().__init__(config)
        self._context: Optional[AwarenessContext] = None
        self._observers: List[Any] = []
    
    @abstractmethod
    def get_system_awareness(self) -> Dict[str, Any]:
        """Get system awareness information.
        
        Returns:
            Dict[str, Any]: System awareness information.
        """
        pass
    
    @abstractmethod
    def get_user_awareness(self) -> Dict[str, Any]:
        """Get user awareness information.
        
        Returns:
            Dict[str, Any]: User awareness information.
        """
        pass
    
    @abstractmethod
    def get_environment_awareness(self) -> Dict[str, Any]:
        """Get environment awareness information.
        
        Returns:
            Dict[str, Any]: Environment awareness information.
        """
        pass
    
    def update_context(self, context: AwarenessContext) -> None:
        """Update the awareness context.
        
        Args:
            context: New awareness context.
        """
        self._context = context
        self._notify_observers()
    
    def get_context(self) -> Optional[AwarenessContext]:
        """Get the current awareness context.
        
        Returns:
            Optional[AwarenessContext]: Current awareness context.
        """
        return self._context
    
    def add_observer(self, observer: Any) -> None:
        """Add an observer to be notified of context changes.
        
        Args:
            observer: Observer object with an update method.
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: Any) -> None:
        """Remove an observer.
        
        Args:
            observer: Observer to remove.
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self) -> None:
        """Notify all observers of context changes."""
        for observer in self._observers:
            try:
                observer.update(self._context)
            except Exception as e:
                self.logger.error(f"Error notifying observer: {e}")
    
    def get_awareness_info(self) -> Dict[str, Any]:
        """Get complete awareness information.
        
        Returns:
            Dict[str, Any]: Complete awareness information.
        """
        return {
            'system': self.get_system_awareness(),
            'user': self.get_user_awareness(),
            'environment': self.get_environment_awareness(),
        } 