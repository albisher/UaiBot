"""
Agent-to-Agent (A2A) Protocol Implementation

This module provides the A2A protocol implementation for agent-to-agent communication,
ensuring standardized message passing and interaction between agents.
"""

from typing import Any, Dict, List, Optional, Union
from .base_protocol import BaseProtocol
import logging
import json
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class A2AProtocol(BaseProtocol):
    """A2A protocol implementation for agent-to-agent communication."""
    
    def __init__(self, name: str, description: str):
        """Initialize the A2A protocol.
        
        Args:
            name: The name of the A2A implementation
            description: A description of the A2A implementation's purpose
        """
        super().__init__(name, description)
        self._message_queue: List[Dict[str, Any]] = []
        self._message_history: List[Dict[str, Any]] = []
        self._connections: Dict[str, Any] = {}
        
    def initialize(self) -> bool:
        """Initialize the A2A protocol implementation.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self._message_queue = []
            self._message_history = []
            self._connections = {}
            self.add_capability('message_passing')
            self.add_capability('connection_management')
            self.add_capability('message_history')
            return True
        except Exception as e:
            logger.error(f"Failed to initialize A2A protocol: {str(e)}")
            return False
    
    def validate(self) -> bool:
        """Validate the A2A protocol implementation.
        
        Returns:
            bool: True if validation was successful, False otherwise
        """
        try:
            required_capabilities = ['message_passing', 'connection_management', 'message_history']
            return all(cap in self._capabilities for cap in required_capabilities)
        except Exception as e:
            logger.error(f"Failed to validate A2A protocol: {str(e)}")
            return False
    
    def send_message(self, target: str, message: Dict[str, Any]) -> bool:
        """Send a message to a target agent.
        
        Args:
            target: The target agent identifier
            message: The message to send
            
        Returns:
            bool: True if the message was sent successfully, False otherwise
        """
        try:
            if target not in self._connections:
                logger.warning(f"Target {target} not found in connections")
                return False
                
            message_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            message_data = {
                'id': message_id,
                'source': self.name,
                'target': target,
                'timestamp': timestamp,
                'content': message
            }
            
            self._message_queue.append(message_data)
            self._message_history.append(message_data)
            self.log(f"Message {message_id} sent to {target}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False
    
    def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive a message from the queue.
        
        Returns:
            Optional[Dict[str, Any]]: The received message, or None if the queue is empty
        """
        try:
            if not self._message_queue:
                return None
                
            message = self._message_queue.pop(0)
            self.log(f"Message {message['id']} received from {message['source']}")
            return message
        except Exception as e:
            logger.error(f"Failed to receive message: {str(e)}")
            return None
    
    def connect(self, agent_id: str, connection_info: Dict[str, Any]) -> bool:
        """Connect to another agent.
        
        Args:
            agent_id: The identifier of the agent to connect to
            connection_info: Information about the connection
            
        Returns:
            bool: True if the connection was successful, False otherwise
        """
        try:
            if agent_id in self._connections:
                logger.warning(f"Already connected to agent {agent_id}")
                return False
                
            self._connections[agent_id] = connection_info
            self.log(f"Connected to agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to agent: {str(e)}")
            return False
    
    def disconnect(self, agent_id: str) -> bool:
        """Disconnect from an agent.
        
        Args:
            agent_id: The identifier of the agent to disconnect from
            
        Returns:
            bool: True if the disconnection was successful, False otherwise
        """
        try:
            if agent_id not in self._connections:
                logger.warning(f"Not connected to agent {agent_id}")
                return False
                
            del self._connections[agent_id]
            self.log(f"Disconnected from agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect from agent: {str(e)}")
            return False
    
    def get_connections(self) -> Dict[str, Any]:
        """Get all active connections.
        
        Returns:
            Dict[str, Any]: The active connections
        """
        return self._connections.copy()
    
    def get_message_history(self) -> List[Dict[str, Any]]:
        """Get the message history.
        
        Returns:
            List[Dict[str, Any]]: The message history
        """
        return self._message_history.copy()
    
    def clear_message_history(self) -> None:
        """Clear the message history."""
        self._message_history = []
        self.log("Message history cleared")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the A2A protocol to a dictionary representation.
        
        Returns:
            Dict[str, Any]: The dictionary representation
        """
        data = super().to_dict()
        data.update({
            'message_queue': self._message_queue,
            'message_history': self._message_history,
            'connections': self._connections
        })
        return data
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load the A2A protocol from a dictionary representation.
        
        Args:
            data: The dictionary representation
        """
        super().from_dict(data)
        self._message_queue = data.get('message_queue', [])
        self._message_history = data.get('message_history', [])
        self._connections = data.get('connections', {}) 