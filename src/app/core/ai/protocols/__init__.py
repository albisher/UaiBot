"""
Protocol Registry

This module provides a registry for managing all protocols (A2A, MCP, and SmolAgents)
and ensuring their proper initialization and interaction.
"""

from typing import Dict, Optional, Type
from .base_protocol import BaseProtocol
from .a2a_protocol import A2AProtocol
from .mcp_protocol import MCPProtocol
from .smol_agent_protocol import SmolAgentProtocol
import logging

logger = logging.getLogger(__name__)

class ProtocolRegistry:
    """Registry for managing all protocols."""
    
    _instance = None
    _protocols: Dict[str, BaseProtocol] = {}
    
    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super(ProtocolRegistry, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the protocol registry."""
        if not self._protocols:
            self._initialize_protocols()
    
    def _initialize_protocols(self):
        """Initialize all protocols."""
        try:
            # Initialize A2A Protocol
            a2a = A2AProtocol(
                name="A2A Protocol",
                description="Agent-to-Agent communication protocol"
            )
            self.register_protocol("a2a", a2a)
            
            # Initialize MCP Protocol
            mcp = MCPProtocol(
                name="MCP Protocol",
                description="Model Context Protocol for managing model interactions"
            )
            self.register_protocol("mcp", mcp)
            
            # Initialize SmolAgents Protocol
            smol = SmolAgentProtocol(
                name="SmolAgents Protocol",
                description="Minimal agent interaction protocol"
            )
            self.register_protocol("smol", smol)
            
            logger.info("All protocols initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize protocols: {str(e)}")
            raise
    
    def register_protocol(self, name: str, protocol: BaseProtocol) -> bool:
        """Register a protocol.
        
        Args:
            name: The name of the protocol
            protocol: The protocol instance
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            if name in self._protocols:
                logger.warning(f"Protocol {name} already registered, overwriting")
            self._protocols[name] = protocol
            logger.info(f"Protocol {name} registered successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to register protocol {name}: {str(e)}")
            return False
    
    def get_protocol(self, name: str) -> Optional[BaseProtocol]:
        """Get a protocol by name.
        
        Args:
            name: The name of the protocol
            
        Returns:
            Optional[BaseProtocol]: The protocol instance, or None if not found
        """
        return self._protocols.get(name)
    
    def get_all_protocols(self) -> Dict[str, BaseProtocol]:
        """Get all registered protocols.
        
        Returns:
            Dict[str, BaseProtocol]: All registered protocols
        """
        return self._protocols.copy()
    
    def get_protocol_capabilities(self, name: str) -> Optional[Dict[str, bool]]:
        """Get the capabilities of a protocol.
        
        Args:
            name: The name of the protocol
            
        Returns:
            Optional[Dict[str, bool]]: The protocol capabilities, or None if not found
        """
        protocol = self.get_protocol(name)
        if protocol:
            return protocol.get_capabilities()
        return None
    
    def validate_protocol(self, name: str) -> bool:
        """Validate a protocol.
        
        Args:
            name: The name of the protocol
            
        Returns:
            bool: True if validation was successful, False otherwise
        """
        protocol = self.get_protocol(name)
        if protocol:
            return protocol.validate()
        return False
    
    def initialize_protocol(self, name: str) -> bool:
        """Initialize a protocol.
        
        Args:
            name: The name of the protocol
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        protocol = self.get_protocol(name)
        if protocol:
            return protocol.initialize()
        return False
    
    def get_protocol_state(self, name: str) -> Optional[Dict]:
        """Get the state of a protocol.
        
        Args:
            name: The name of the protocol
            
        Returns:
            Optional[Dict]: The protocol state, or None if not found
        """
        protocol = self.get_protocol(name)
        if protocol:
            return protocol.to_dict()
        return None
    
    def set_protocol_state(self, name: str, state: Dict) -> bool:
        """Set the state of a protocol.
        
        Args:
            name: The name of the protocol
            state: The state to set
            
        Returns:
            bool: True if the state was set successfully, False otherwise
        """
        protocol = self.get_protocol(name)
        if protocol:
            try:
                protocol.from_dict(state)
                return True
            except Exception as e:
                logger.error(f"Failed to set protocol state: {str(e)}")
        return False

# Create singleton instance
protocol_registry = ProtocolRegistry() 