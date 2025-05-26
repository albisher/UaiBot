"""
Agent-to-Agent (A2A) Protocol Implementation.

This module implements the A2A protocol for agent collaboration, following the
SmolAgents pattern for minimal, efficient agent communication.

The A2A protocol enables:
- Direct agent-to-agent communication
- Message passing between agents
- Tool sharing and discovery
- State synchronization
- Error handling and recovery

Message Types:
- REQUEST: Initial request from sender
- RESPONSE: Response to a request
- ERROR: Error message
- TOOL_REQUEST: Request to use a tool
- TOOL_RESPONSE: Response from tool execution
- STATE_UPDATE: Agent state update
- HEARTBEAT: Keep-alive message

Protocol Flow:
1. Sender creates a message with type and content
2. Message is sent to receiver
3. Receiver processes message and generates response
4. Response is sent back to sender
5. Sender processes response

Error Handling:
- Timeout handling for unresponsive agents
- Retry logic for failed messages
- Error propagation between agents
- State recovery mechanisms
"""

from typing import Any, Dict, List, Optional, Protocol, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
from enum import Enum
import asyncio
from .smol_agent import SmolAgent, AgentState, AgentResult

class MessageType(Enum):
    """Types of A2A messages."""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    TOOL_REQUEST = "tool_request"
    TOOL_RESPONSE = "tool_response"
    STATE_UPDATE = "state_update"
    HEARTBEAT = "heartbeat"

@dataclass
class Message:
    """A2A message structure."""
    type: MessageType
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    message_id: str = field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "type": self.type.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(
            type=MessageType(data["type"]),
            sender=data["sender"],
            receiver=data["receiver"],
            content=data["content"],
            timestamp=data["timestamp"],
            message_id=data["message_id"],
            correlation_id=data.get("correlation_id"),
            metadata=data.get("metadata", {})
        )

class A2AProtocol:
    """
    A2A protocol implementation for agent communication.
    
    This class handles:
    - Message routing between agents
    - Tool discovery and sharing
    - State synchronization
    - Error handling and recovery
    """
    
    def __init__(self):
        """Initialize A2A protocol."""
        self.logger = logging.getLogger("A2AProtocol")
        self._message_handlers: Dict[MessageType, List[callable]] = {
            msg_type: [] for msg_type in MessageType
        }
        self._pending_messages: Dict[str, asyncio.Future] = {}
        self._message_timeout = 30.0  # seconds
        self._retry_count = 3
        self._retry_delay = 1.0  # seconds
    
    def register_handler(self, message_type: MessageType, handler: callable):
        """Register a message handler."""
        self._message_handlers[message_type].append(handler)
    
    def register_tool(self, tool: Any):
        """Register a tool for sharing with other agents."""
        # Tool registration logic here
        pass
    
    async def send_message(self, message: Message) -> Message:
        """
        Send a message and wait for response.
        
        Args:
            message: The message to send
            
        Returns:
            Message: The response message
            
        Raises:
            TimeoutError: If no response received within timeout
            A2AError: If message handling fails
        """
        try:
            # Create future for response
            future = asyncio.Future()
            self._pending_messages[message.message_id] = future
            
            # Send message
            await self._route_message(message)
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(future, timeout=self._message_timeout)
                return response
            except asyncio.TimeoutError:
                raise TimeoutError(f"No response received for message {message.message_id}")
            finally:
                self._pending_messages.pop(message.message_id, None)
                
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            raise A2AError(f"Failed to send message: {str(e)}")
    
    async def handle_message(self, message: Message) -> Message:
        """
        Handle an incoming message.
        
        Args:
            message: The message to handle
            
        Returns:
            Message: The response message
        """
        try:
            # Get handlers for message type
            handlers = self._message_handlers[message.type]
            
            # Execute handlers
            for handler in handlers:
                try:
                    response = await handler(message)
                    if response:
                        return response
                except Exception as e:
                    self.logger.error(f"Handler error: {str(e)}")
            
            # If no handler responded, create error response
            return Message(
                type=MessageType.ERROR,
                sender=message.receiver,
                receiver=message.sender,
                content={"error": "No handler found for message type"},
                correlation_id=message.message_id
            )
            
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            return Message(
                type=MessageType.ERROR,
                sender=message.receiver,
                receiver=message.sender,
                content={"error": str(e)},
                correlation_id=message.message_id
            )
    
    async def _route_message(self, message: Message):
        """Route message to appropriate handler."""
        # Message routing logic here
        pass
    
    async def _retry_message(self, message: Message, attempt: int = 0) -> Message:
        """Retry sending a message with exponential backoff."""
        try:
            return await self.send_message(message)
        except (TimeoutError, A2AError) as e:
            if attempt < self._retry_count:
                await asyncio.sleep(self._retry_delay * (2 ** attempt))
                return await self._retry_message(message, attempt + 1)
            raise e

class A2AError(Exception):
    """Base class for A2A protocol errors."""
    pass

class MessageTimeoutError(A2AError):
    """Raised when a message times out."""
    pass

class MessageHandlerError(A2AError):
    """Raised when a message handler fails."""
    pass 